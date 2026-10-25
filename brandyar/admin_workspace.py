import csv
import datetime
import hashlib
import hmac
import io
import json
import re
import sqlite3
import time
import uuid
import zlib
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

import brand_analysis
import supabase_store

MODULES = ('overview', 'customers', 'crm', 'assessments', 'tests', 'prompts', 'plans', 'content', 'team', 'reports', 'audit', 'settings')
PERMISSIONS = {
    'owner': set(MODULES) | {'write', 'publish', 'export', 'private', 'roles', 'archive'},
    'admin': set(MODULES) - {'team', 'settings'} | {'write', 'publish', 'export', 'private', 'archive'},
    'crm_manager': {'overview', 'customers', 'crm', 'reports', 'write', 'private', 'export'},
    'content_manager': {'tests', 'plans', 'content', 'write'},
    'analyst': {'overview', 'assessments', 'reports'},
}
TITLES = dict(zip(MODULES, ('نمای کلی', 'مشتری‌ها', 'لیدها و CRM', 'ارزیابی‌ها', 'تست‌ها و سؤال‌ها', 'پرامپت‌های هوش مصنوعی', 'پلن‌ها و قیمت‌گذاری', 'محتوای سایت', 'اعضای تیم', 'گزارش‌ها', 'گزارش حسابرسی', 'تنظیمات')))
STAGES = ('لید جدید', 'ارزیابی را شروع کرده', 'ارزیابی را کامل کرده', 'گزارش را دیده', 'نیازمند پیگیری', 'مشتری فعال', 'غیرفعال', 'عدم تمایل')
VARIABLES = {'assessment.answers', 'test.title', 'test.instructions', 'locale', 'current_date'}


class Invalid(Exception):
    pass


def initialize(db):
    if db.execute("SELECT 1 FROM sqlite_master WHERE name='admin_schema_migrations'").fetchone():
        return
    script = Path(__file__).with_name('admin_migration_001.sql').read_text()
    try:
        db.executescript('BEGIN IMMEDIATE;\n' + script)
        for position, title in enumerate(STAGES):
            db.execute('INSERT OR IGNORE INTO admin_crm_stages VALUES(?,?,?)', (str(uuid.uuid5(uuid.NAMESPACE_URL, 'nesharo-stage:' + title)), title, position))
        db.commit()
    except Exception:
        db.rollback()
        raise


def allowed(role, permission):
    return permission in PERMISSIONS.get(role, set())


def identifier(value):
    if not supabase_store.is_id(value):
        raise Invalid('شناسه معتبر نیست.')
    return value


def text(value, maximum=200, required=True):
    if not isinstance(value, str) or len(value) > maximum or (required and not value.strip()):
        raise Invalid('متن واردشده معتبر نیست.')
    return value.strip()


def masked(value):
    return value[:4] + '•••' + value[-2:] if isinstance(value, str) and len(value) >= 8 else '—'


def audit(db, staff, action, entity, identity='', before=None, after=None):
    db.execute('INSERT INTO admin_audit_logs VALUES(?,?,?,?,?,?,?,?,?,?)', (str(uuid.uuid4()), staff['staff_id'], staff['role'], action, entity, identity, json.dumps(before or {}, ensure_ascii=False), json.dumps(after or {}, ensure_ascii=False), int(time.time()), str(uuid.uuid4())))


def event(db, assessment_id, name, prompt_version=None):
    db.execute('INSERT INTO admin_events VALUES(?,?,?,?,?,?)', (str(uuid.uuid4()), assessment_id, name, 'legacy-v1', prompt_version, int(time.time())))


def active_prompt(db):
    row = db.execute("SELECT v.id,v.body FROM admin_documents d JOIN admin_versions v ON v.id=d.active_version WHERE d.kind='prompts' AND d.slug='brand-assessment'").fetchone()
    return (row['id'], json.loads(row['body'])) if row else (None, None)


def render_prompt(body, answers):
    values = {'assessment.answers': json.dumps(answers, ensure_ascii=False), 'test.title': 'ارزیابی برند شخصی', 'test.instructions': 'تحلیل بر پایهٔ گزینه‌های انتخاب‌شده', 'locale': 'fa-IR', 'current_date': datetime.date.today().isoformat()}
    def replace(match):
        key = match.group(1).strip()
        if key not in values:
            raise Invalid('متغیر پرامپت در فهرست مجاز نیست: ' + key)
        return values[key]
    return re.sub(r'\{\{([^{}]+)\}\}', replace, body['instruction_prompt'])


def validate_document(kind, body):
    if not isinstance(body, dict):
        raise Invalid('ساختار نسخه باید یک شیء JSON باشد.')
    if kind == 'prompts':
        if set(body) != {'system_prompt', 'instruction_prompt', 'output_schema', 'sample_output'}:
            raise Invalid('فیلدهای پرامپت کامل نیستند.')
        text(body['system_prompt'], 16000)
        text(body['instruction_prompt'], 6000)
        render_prompt(body, {})
        if body['output_schema'] != brand_analysis.REPORT_SHAPE:
            raise Invalid('این موتور فقط schema فعلی گزارش را پشتیبانی می‌کند.')
        try:
            brand_analysis.validate_report(body['sample_output'])
        except (ValueError, KeyError, TypeError):
            raise Invalid('نمونه خروجی با schema گزارش سازگار نیست.') from None
    elif kind == 'tests':
        if set(body) != {'description', 'questions'} or not isinstance(body['questions'], list) or not 1 <= len(body['questions']) <= 100:
            raise Invalid('توضیح و فهرست سؤال‌ها الزامی است.')
        text(body['description'], 1000, False)
        keys = set()
        for q in body['questions']:
            if not isinstance(q, dict):
                raise Invalid('ساختار سؤال معتبر نیست.')
            key = text(q.get('id'), 64)
            if not re.fullmatch(r'[a-z][a-z0-9_]*', key) or key in keys:
                raise Invalid('کلید سؤال باید پایدار و یکتا باشد.')
            keys.add(key)
            text(q.get('title'), 600)
            if q.get('type', 'single') not in {'single', 'multi', 'text', 'textarea', 'number', 'scale'}:
                raise Invalid('نوع سؤال پشتیبانی نمی‌شود.')
            options = q.get('options', [])
            if not isinstance(options, list) or len(options) > 30:
                raise Invalid('گزینه‌های سؤال معتبر نیستند.')
            for option in options:
                text(option, 300)
    elif kind == 'plans':
        if set(body) != {'description', 'features', 'cta_path', 'active'} or not isinstance(body['features'], list) or len(body['features']) > 30 or type(body['active']) is not bool:
            raise Invalid('فیلدهای کاتالوگ پلن معتبر نیستند؛ پرداخت متصل نیست.')
        text(body['description'], 1000, False)
        for feature in body['features']:
            text(feature, 200)
        if body['cta_path'] not in {'#/assessment', '#/consultation', '#/app', '#/plans'}:
            raise Invalid('مسیر اقدام باید از مسیرهای واقعی سایت باشد.')
    elif kind == 'content':
        if set(body) != {'text', 'placement', 'cta_path'}:
            raise Invalid('ساختار محتوا معتبر نیست.')
        text(body['text'], 6000)
        text(body['placement'], 100)
        if body['cta_path'] not in {'', '#/assessment', '#/app', '#/plans'}:
            raise Invalid('مسیر اقدام معتبر نیست.')


def remote(store, table, query):
    if not store:
        raise Invalid('اتصال Supabase هنوز تنظیم نشده است.')
    return store.request(table, query=query, prefer='return=minimal')


def range_query(params):
    days = params.get('days', ['30'])[0]
    if days == 'custom':
        try:
            start = datetime.datetime.strptime(params.get('from', [''])[0], '%Y-%m-%d').replace(tzinfo=datetime.timezone.utc)
            end = datetime.datetime.strptime(params.get('to', [''])[0], '%Y-%m-%d').replace(tzinfo=datetime.timezone.utc) + datetime.timedelta(days=1)
        except ValueError:
            raise Invalid('بازهٔ تاریخ معتبر نیست.') from None
        if not 0 < (end-start).days <= 366:
            raise Invalid('بازه باید حداکثر یک سال باشد.')
    else:
        if days not in {'1', '7', '30'}:
            raise Invalid('بازهٔ تاریخ معتبر نیست.')
        end = datetime.datetime.now(datetime.timezone.utc)
        start = end - datetime.timedelta(days=int(days))
    return '&created_at=gte.' + supabase_store.filter_value(start.isoformat()) + '&created_at=lt.' + supabase_store.filter_value(end.isoformat()), int(start.timestamp()), int(end.timestamp()) + (0 if days == 'custom' else 1)


def get_data(db, staff, store, section, params):
    if not allowed(staff['role'], section):
        return 403, {'error': 'برای این بخش دسترسی ندارید.'}
    identity = params.get('id', [''])[0]
    if section in {'customers', 'crm', 'assessments'}:
        table = 'assessments' if section == 'assessments' else 'leads'
        if identity:
            identifier(identity)
            fields = 'id,lead_id,answers,insight,full_report,current_step,created_at,completed_at' if table == 'assessments' else 'id,mobile,consent_follow_up,status,created_at,updated_at'
            rows = remote(store, table, 'id=eq.' + identity + '&select=' + fields)
            if not rows:
                return 404, {'error': 'رکورد پیدا نشد.'}
            row = rows[0]
            if table == 'assessments':
                try:
                    row['full_report'] = supabase_store.unpack_report(row.get('full_report'))
                except (ValueError, TypeError, zlib.error):
                    row['full_report'] = None
                row['snapshot'] = dict(db.execute('SELECT * FROM admin_assessment_snapshots WHERE assessment_id=?', (identity,)).fetchone() or {})
                row['results'] = [dict(v) for v in db.execute('SELECT id,prompt_version,report_json,created_at,context_json FROM admin_assessment_results WHERE assessment_id=? ORDER BY created_at DESC LIMIT 50', (identity,))]
            else:
                if not allowed(staff['role'], 'private'):
                    return 403, {'error': 'مجوز مشاهدهٔ کامل مشتری ندارید.'}
                row['crm'] = dict(db.execute('SELECT * FROM admin_crm_records WHERE lead_id=?', (identity,)).fetchone() or {})
                row['notes'] = [dict(v) for v in db.execute('SELECT n.id,n.body,n.created_at,s.name AS author FROM admin_crm_notes n JOIN staff s ON s.id=n.created_by WHERE lead_id=? ORDER BY created_at DESC LIMIT 100', (identity,))]
                row['tasks'] = [dict(v) for v in db.execute('SELECT id,title,due_at,done,owner_id FROM admin_crm_tasks WHERE lead_id=? ORDER BY due_at LIMIT 100', (identity,))]
                row['assessments'] = remote(store, 'assessments', 'lead_id=eq.' + identity + '&select=id,current_step,created_at&order=created_at.desc&limit=100')
            audit(db, staff, 'view_full', table, identity)
            db.commit()
            return 200, {'record': row}
        try:
            page = int(params.get('page', ['0'])[0])
        except ValueError:
            raise Invalid('شمارهٔ صفحه معتبر نیست.') from None
        if not 0 <= page <= 10000:
            raise Invalid('شمارهٔ صفحه معتبر نیست.')
        query, _, _ = range_query(params)
        fields = 'id,lead_id,current_step,created_at,completed_at' if table == 'assessments' else 'id,mobile,status,created_at,updated_at'
        rows = remote(store, table, 'select=' + fields + query + '&order=created_at.desc&limit=50&offset=' + str(page * 50))
        archives = {v['entity_id'] for v in db.execute('SELECT entity_id FROM admin_archives WHERE entity_type=?', (table,))}
        for row in rows:
            row['archived'] = row['id'] in archives
            if table == 'leads':
                row['mobile'] = masked(row.get('mobile'))
                row['crm'] = dict(db.execute('SELECT r.stage_id,r.owner_id,r.tags,s.title AS stage FROM admin_crm_records r LEFT JOIN admin_crm_stages s ON s.id=r.stage_id WHERE r.lead_id=?', (row['id'],)).fetchone() or {})
        return 200, {'rows': rows, 'page': page, 'has_more': len(rows) == 50, 'source': 'Supabase'}
    if section in {'tests', 'prompts', 'plans', 'content'}:
        documents = []
        for row in db.execute('SELECT * FROM admin_documents WHERE kind=? ORDER BY created_at DESC', (section,)):
            item = dict(row)
            item['versions'] = [dict(v) for v in db.execute('SELECT v.*,s.name AS author FROM admin_versions v JOIN staff s ON s.id=v.created_by WHERE document_id=? ORDER BY version DESC', (row['id'],))]
            documents.append(item)
        result = {'documents': documents}
        if section == 'prompts':
            result.update({'variables': sorted(VARIABLES), 'schema': brand_analysis.REPORT_SHAPE, 'current_system': brand_analysis.SYSTEM_INSTRUCTION, 'runs': [dict(v) for v in db.execute('SELECT id,version_id,created_at,status,output_json FROM admin_prompt_runs ORDER BY created_at DESC LIMIT 30')]})
        if section == 'tests':
            result['current_questions'] = brand_analysis.QUESTIONS
            result['notice'] = 'موتور فعلی فقط تست برند شخصی ثابت را اجرا می‌کند. تست جدید و ساختار سؤال متفاوت تا اتصال موتور پویا فقط پیش‌نویس است.'
        if section in {'plans', 'content'}:
            result['notice'] = 'کاتالوگ آماده‌سازی است؛ سایت هنوز این داده را مصرف نمی‌کند و انتشار فعال نیست. پرداخت یا اشتراک متصل نیست.'
        return 200, result
    if section == 'team':
        return 200, {'rows': [dict(v) for v in db.execute('SELECT id,name,email,role FROM staff ORDER BY id')], 'roles': sorted(PERMISSIONS), 'notice': 'احراز هویت موجود: رمز و TOTP؛ اتصال به Supabase Auth هنوز انجام نشده است.'}
    if section == 'settings':
        return 200, {'stages': [dict(v) for v in db.execute('SELECT * FROM admin_crm_stages ORDER BY position')], 'permissions': {k: sorted(v) for k, v in PERMISSIONS.items()}, 'connections': {'supabase': bool(store), 'ai': brand_analysis.configured(), 'payment': False, 'messaging': False, 'supabase_auth': False}}
    if section == 'audit':
        _, start, end = range_query(params)
        rows = [dict(v) for v in db.execute('SELECT a.*,s.name AS actor FROM admin_audit_logs a JOIN staff s ON s.id=a.actor_id WHERE a.created_at>=? AND a.created_at<? ORDER BY a.created_at DESC LIMIT 500', (start, end))]
        search = text(params.get('q', [''])[0], 100, False)
        return 200, {'rows': [v for v in rows if not search or search in ' '.join(str(v[k]) for k in ('actor', 'action', 'entity_type', 'entity_id'))], 'limit': 500}
    if section in {'overview', 'reports'}:
        query, start, end = range_query(params)
        counts = {}
        if store:
            if allowed(staff['role'], 'customers'):
                counts['leads'] = store.count('leads', query)
            if allowed(staff['role'], 'assessments'):
                counts['assessments'] = store.count('assessments', query)
                counts['completed'] = store.count('assessments', query + '&current_step=in.(completed,preview_shown,report_unlocked)')
        counts['overdue'] = db.execute('SELECT count(*) FROM admin_crm_tasks WHERE done=0 AND due_at<?', (int(time.time()),)).fetchone()[0] if allowed(staff['role'], 'crm') else None
        events = {v['event']: v['total'] for v in db.execute('SELECT event,count(*) AS total FROM admin_events WHERE created_at>=? AND created_at<? GROUP BY event', (start, end))}
        tasks = [dict(v) for v in db.execute('SELECT id,title,due_at,lead_id FROM admin_crm_tasks WHERE done=0 ORDER BY due_at LIMIT 10')] if allowed(staff['role'], 'crm') else []
        return 200, {'counts': counts, 'events': events, 'tasks': tasks, 'notice': 'قیف بازدید گزارش، ثبت‌نام حساب و خرید هنوز ردیابی نمی‌شود. رویدادهای تحلیل از زمان نصب این نسخه ثبت می‌شوند؛ دادهٔ گذشته بازسازی نشده است.'}
    return 404, {'error': 'بخش پیدا نشد.'}


def mutate(db, staff, store, data):
    role = staff['role']
    action = text(data.get('action'), 40)
    section = text(data.get('section'), 40)
    if section not in MODULES or not allowed(role, section) or not allowed(role, 'write'):
        return 403, {'error': 'مجوز این عملیات را ندارید.'}
    if action in {'archive', 'publish', 'rollback', 'role', 'privacy', 'export', 'lab'} and data.get('confirmed') is not True:
        raise Invalid('تأیید نهایی عملیات الزامی است.')
    now = int(time.time())
    recent = db.execute('SELECT count(*) FROM admin_audit_logs WHERE actor_id=? AND created_at>?', (staff['staff_id'], now - 60)).fetchone()[0]
    if recent >= 30:
        return 429, {'error': 'تعداد عملیات زیاد است؛ یک دقیقه دیگر تلاش کنید.'}
    identity = data.get('id', '')
    if action == 'role' and section == 'team':
        if not allowed(role, 'roles') or type(data.get('staff_id')) is not int or data.get('role') not in PERMISSIONS:
            return 403, {'error': 'مجوز تغییر نقش ندارید.'}
        target = db.execute('SELECT id,role FROM staff WHERE id=?', (data['staff_id'],)).fetchone()
        if not target or target['role'] == 'owner' or target['id'] == staff['staff_id'] or data['role'] == 'owner':
            raise Invalid('نقش مالک و نقش خودتان از این مسیر قابل تغییر نیست.')
        db.execute('UPDATE staff SET role=? WHERE id=?', (data['role'], target['id']))
        db.execute('DELETE FROM sessions WHERE staff_id=?', (target['id'],))
        audit(db, staff, 'role_change', 'staff', str(target['id']), {'role': target['role']}, {'role': data['role']})
    elif action == 'stage' and section == 'settings':
        title = text(data.get('title'), 100)
        identity = str(uuid.uuid4())
        db.execute('INSERT INTO admin_crm_stages VALUES(?,?,?)', (identity, title, db.execute('SELECT count(*) FROM admin_crm_stages').fetchone()[0]))
        audit(db, staff, 'stage_create', 'crm_stage', identity, after={'title': title})
    elif action in {'crm', 'note', 'task', 'task_done', 'archive', 'privacy', 'export'} and section in {'customers', 'crm', 'assessments'}:
        table = 'assessments' if section == 'assessments' else 'leads'
        if action == 'export':
            if not allowed(role, 'export') or table != 'leads':
                return 403, {'error': 'مجوز خروجی گرفتن ندارید.'}
            rows = remote(store, table, 'select=id,status,created_at&order=created_at.desc&limit=500')
            stream = io.StringIO()
            writer = csv.writer(stream)
            writer.writerow(['id', 'status', 'created_at'])
            for row in rows:
                values = [str(row.get(k, '')) for k in ('id', 'status', 'created_at')]
                writer.writerow(["'" + value if value.lstrip().startswith(('=', '+', '-', '@', '\t', '\r', '\n')) else value for value in values])
            audit(db, staff, 'export', table, after={'count': len(rows), 'contains_contact': False})
            db.commit()
            return 200, {'csv': stream.getvalue(), 'count': len(rows)}
        identifier(identity)
        if not remote(store, table, 'id=eq.' + identity + '&select=id'):
            return 404, {'error': 'رکورد پیدا نشد.'}
        if action == 'archive':
            if not allowed(role, 'archive'):
                return 403, {'error': 'مجوز آرشیو ندارید.'}
            db.execute('INSERT OR IGNORE INTO admin_archives VALUES(?,?,?,?)', (table, identity, now, staff['staff_id']))
        elif action == 'privacy':
            if role != 'owner' or table != 'leads' or data.get('kind') not in {'delete', 'anonymize', 'unsubscribe'}:
                return 403, {'error': 'مجوز این درخواست را ندارید.'}
            db.execute('INSERT INTO admin_privacy_requests(id,lead_id,kind,created_at,created_by) VALUES(?,?,?,?,?)', (str(uuid.uuid4()), identity, data['kind'], now, staff['staff_id']))
        elif table != 'leads':
            raise Invalid('این عملیات فقط برای مشتری مجاز است.')
        elif action == 'crm':
            stage = identifier(data.get('stage_id'))
            if not db.execute('SELECT 1 FROM admin_crm_stages WHERE id=?', (stage,)).fetchone():
                raise Invalid('مرحلهٔ CRM وجود ندارد.')
            tags = data.get('tags', [])
            if not isinstance(tags, list) or len(tags) > 20:
                raise Invalid('برچسب‌ها معتبر نیستند.')
            tags = [text(v, 40) for v in tags]
            owner = data.get('owner_id')
            if owner is not None and (type(owner) is not int or not db.execute('SELECT 1 FROM staff WHERE id=?', (owner,)).fetchone()):
                raise Invalid('مسئول پیگیری معتبر نیست.')
            db.execute('INSERT INTO admin_crm_records(lead_id,stage_id,owner_id,tags,updated_at,updated_by) VALUES(?,?,?,?,?,?) ON CONFLICT(lead_id) DO UPDATE SET stage_id=excluded.stage_id,owner_id=excluded.owner_id,tags=excluded.tags,updated_at=excluded.updated_at,updated_by=excluded.updated_by', (identity, stage, owner, json.dumps(tags, ensure_ascii=False), now, staff['staff_id']))
        elif action == 'note':
            db.execute('INSERT INTO admin_crm_notes VALUES(?,?,?,?,?)', (str(uuid.uuid4()), identity, text(data.get('body'), 3000), now, staff['staff_id']))
        elif action == 'task':
            due = data.get('due_at')
            owner = data.get('owner_id')
            if type(due) is not int or not now - 86400 <= due <= now + 366 * 86400:
                raise Invalid('موعد وظیفه معتبر نیست.')
            if owner is not None and (type(owner) is not int or not db.execute('SELECT 1 FROM staff WHERE id=?', (owner,)).fetchone()):
                raise Invalid('مسئول وظیفه معتبر نیست.')
            db.execute('INSERT INTO admin_crm_tasks VALUES(?,?,?,?,?,0,?,?,?)', (str(uuid.uuid4()), identity, text(data.get('title'), 200), owner, due, now, now, staff['staff_id']))
        elif action == 'task_done':
            task = identifier(data.get('task_id'))
            if not db.execute('SELECT 1 FROM admin_crm_tasks WHERE id=? AND lead_id=?', (task, identity)).fetchone():
                raise Invalid('وظیفه پیدا نشد.')
            db.execute('UPDATE admin_crm_tasks SET done=1,updated_at=? WHERE id=? AND lead_id=?', (now, task, identity))
        audit(db, staff, action, table, identity)
    elif section in {'tests', 'prompts', 'plans', 'content'} and action in {'draft', 'publish', 'rollback'}:
        if action == 'draft':
            slug = text(data.get('slug'), 80)
            title = text(data.get('title'), 200)
            if not re.fullmatch(r'[a-z][a-z0-9-]*', slug):
                raise Invalid('نامک باید با حروف لاتین و خط تیره باشد.')
            body = data.get('body')
            validate_document(section, body)
            doc = db.execute('SELECT * FROM admin_documents WHERE kind=? AND slug=?', (section, slug)).fetchone()
            doc_id = doc['id'] if doc else str(uuid.uuid4())
            if not doc:
                db.execute('INSERT INTO admin_documents VALUES(?,?,?,?,NULL,?,?)', (doc_id, section, slug, title, now, staff['staff_id']))
            version = db.execute('SELECT coalesce(max(version),0)+1 FROM admin_versions WHERE document_id=?', (doc_id,)).fetchone()[0]
            identity = str(uuid.uuid4())
            db.execute('INSERT INTO admin_versions VALUES(?,?,?,?,?,?,?,?,NULL,NULL)', (identity, doc_id, version, json.dumps(body, ensure_ascii=False), 'draft', text(data.get('change_note', ''), 500, False), now, staff['staff_id']))
            audit(db, staff, 'draft_create', section, identity, after={'version': version})
        else:
            if not allowed(role, 'publish'):
                return 403, {'error': 'مجوز انتشار ندارید.'}
            if section != 'prompts':
                raise Invalid('موتور سایت هنوز انتشار این کاتالوگ را مصرف نمی‌کند؛ نسخه در پیش‌نویس باقی می‌ماند.')
            row = db.execute('SELECT v.*,d.slug,d.kind,d.active_version FROM admin_versions v JOIN admin_documents d ON d.id=v.document_id WHERE v.id=?', (identifier(identity),)).fetchone()
            if not row or row['kind'] != section or row['slug'] != 'brand-assessment':
                raise Invalid('پرامپت باید به تست فعلی با نامک brand-assessment متصل باشد.')
            if action == 'publish' and row['status'] != 'draft':
                raise Invalid('فقط پیش‌نویس قابل انتشار است.')
            if action == 'rollback' and row['status'] != 'published':
                raise Invalid('فقط نسخهٔ قبلاً منتشرشده قابل بازگردانی است.')
            validate_document(section, json.loads(row['body']))
            if action == 'publish':
                if not db.execute("SELECT 1 FROM admin_prompt_runs WHERE version_id=? AND status='success'", (identity,)).fetchone():
                    raise Invalid('پیش از انتشار یک اجرای موفق Prompt Lab لازم است.')
                db.execute("UPDATE admin_versions SET status='published',published_at=?,published_by=? WHERE id=?", (now, staff['staff_id'], identity))
            db.execute('UPDATE admin_documents SET active_version=? WHERE id=?', (identity, row['document_id']))
            audit(db, staff, action, section, identity, {'active_version': row['active_version']}, {'active_version': identity})
    else:
        raise Invalid('عملیات پشتیبانی نمی‌شود.')
    db.commit()
    return 200, {'ok': True, 'id': identity}


def dispatch(handler, db, staff, write=False):
    if not staff or not handler.assessment_https():
        return handler.json(401, {'error': 'ورود امن و تأیید دومرحله‌ای لازم است.'})
    if staff['role'] not in PERMISSIONS:
        return handler.json(403, {'error': 'نقش شما به پنل مدیریت دسترسی ندارد.'})
    try:
        if write:
            if not handler.safe_origin():
                return handler.json(403, {'error': 'مبدأ درخواست معتبر نیست.'})
            data = handler.request_data(65536, brand_analysis.parse_json)
            if not hmac.compare_digest(str(data.get('csrf', '')), staff['csrf']):
                return handler.json(403, {'error': 'نشست فرم معتبر نیست؛ صفحه را تازه کنید.'})
            if data.get('action') == 'lab':
                return lab(handler, db, staff, data)
            if data.get('action') == 'regenerate':
                return regenerate(handler, db, staff, data)
            status, result = mutate(db, staff, handler.supabase(), data)
        else:
            params = parse_qs(urlsplit(handler.path).query)
            section = params.get('section', ['bootstrap'])[0]
            if section == 'bootstrap':
                result = {'principal': {'name': staff['name'], 'role': staff['role']}, 'csrf': staff['csrf'], 'modules': {k: TITLES[k] for k in MODULES if allowed(staff['role'], k)}, 'permissions': sorted(PERMISSIONS.get(staff['role'], set())), 'stages': [dict(v) for v in db.execute('SELECT * FROM admin_crm_stages ORDER BY position')], 'assignees': [dict(v) for v in db.execute('SELECT id,name FROM staff')] if allowed(staff['role'], 'crm') else []}
                status = 200
            else:
                status, result = get_data(db, staff, handler.supabase(), section, params)
        return handler.json(status, result)
    except Invalid as error:
        db.rollback()
        return handler.json(422, {'error': str(error)})
    except supabase_store.SupabaseUnavailable:
        db.rollback()
        return handler.json(503, {'error': 'دریافت یا ثبت در Supabase انجام نشد؛ دوباره تلاش کنید.'})
    except (sqlite3.Error, ValueError, TypeError, KeyError, RecursionError):
        db.rollback()
        return handler.json(422, {'error': 'ساختار داده یا وضعیت ذخیره‌سازی معتبر نیست.'})


def regenerate(handler, db, staff, data):
    if data.get('section') != 'assessments' or not allowed(staff['role'], 'publish') or not allowed(staff['role'], 'assessments') or data.get('confirmed') is not True:
        return handler.json(403, {'error': 'بازتولید نیازمند مجوز و تأیید نهایی است.'})
    identity = identifier(data.get('id'))
    if db.execute("SELECT 1 FROM admin_audit_logs WHERE actor_id=? AND action='regenerate' AND created_at>?", (staff['staff_id'], int(time.time()) - 30)).fetchone():
        return handler.json(429, {'error': 'بین بازتولیدها ۳۰ ثانیه فاصله لازم است.'})
    rows = remote(handler.supabase(), 'assessments', 'id=eq.' + identity + '&select=id,answers')
    if not rows or not isinstance(rows[0].get('answers'), dict) or not rows[0]['answers']:
        raise Invalid('پاسخ کافی برای بازتولید وجود ندارد.')
    answers = rows[0]['answers']
    for key, value in answers.items():
        if not re.fullmatch(r'q[0-9]+a?', key) or not isinstance(value, dict) or set(value) != {'question', 'answer'}:
            raise Invalid('قالب تاریخی پاسخ‌ها با موتور فعلی سازگار نیست.')
    prompt_id, body = active_prompt(db)
    audit(db, staff, 'regenerate', 'assessments', identity, after={'prompt_version': prompt_id})
    db.commit()
    try:
        report = brand_analysis.generate_report(answers, prompt_body=body) if body else brand_analysis.generate_report(answers)
        result_id = str(uuid.uuid4())
        db.execute('INSERT INTO admin_assessment_results VALUES(?,?,?,?,?,?)', (result_id, identity, prompt_id, json.dumps(report, ensure_ascii=False), int(time.time()), json.dumps({'answers': answers, 'test_version': 'legacy-v1'}, ensure_ascii=False)))
        audit(db, staff, 'regenerate_success', 'assessment_results', result_id)
        db.commit()
        return handler.json(200, {'ok': True, 'id': result_id})
    except brand_analysis.AnalysisError:
        audit(db, staff, 'regenerate_failed', 'assessments', identity)
        db.commit()
        return handler.json(503, {'error': 'بازتولید موفق نبود؛ خروجی قبلی حفظ شده است.'})


def lab(handler, db, staff, data):
    if not allowed(staff['role'], 'prompts') or not allowed(staff['role'], 'publish') or data.get('confirmed') is not True:
        return handler.json(403, {'error': 'آزمایش پرامپت نیازمند مجوز و تأیید هزینه است.'})
    version_id = identifier(data.get('id'))
    row = db.execute("SELECT v.* FROM admin_versions v JOIN admin_documents d ON d.id=v.document_id WHERE v.id=? AND d.kind='prompts'", (version_id,)).fetchone()
    if not row:
        raise Invalid('نسخهٔ پرامپت پیدا نشد.')
    if db.execute('SELECT 1 FROM admin_prompt_runs WHERE actor_id=? AND created_at>?', (staff['staff_id'], int(time.time()) - 30)).fetchone():
        return handler.json(429, {'error': 'بین اجرای آزمایش‌ها ۳۰ ثانیه فاصله لازم است.'})
    body = json.loads(row['body'])
    validate_document('prompts', body)
    answers = {q['id']: {'question': q['title'], 'answer': (['آموزش رایگان در پیج'] if q['id'] == 'q11' else [q['options'][0]] if q.get('type') == 'multi' else q['options'][0])} for q in brand_analysis.QUESTIONS if q.get('options') and q['id'] not in {'q12', 'q13', 'q14'}}
    rendered = render_prompt(body, answers)
    identity = str(uuid.uuid4())
    db.execute('INSERT INTO admin_prompt_runs VALUES(?,?,?,?,?,?,?)', (identity, version_id, int(time.time()), staff['staff_id'], rendered, None, 'running'))
    audit(db, staff, 'prompt_lab', 'prompts', version_id)
    db.commit()
    try:
        report = brand_analysis.generate_report(answers, prompt_body=body)
        db.execute('UPDATE admin_prompt_runs SET status=?,output_json=? WHERE id=?', ('success', json.dumps(report, ensure_ascii=False), identity))
        db.commit()
        return handler.json(200, {'input': rendered, 'output': report, 'valid': True, 'run_id': identity})
    except brand_analysis.AnalysisError:
        db.execute("UPDATE admin_prompt_runs SET status='failed' WHERE id=?", (identity,))
        db.commit()
        return handler.json(503, {'error': 'تولید آزمایشی موفق نبود؛ نتیجهٔ هیچ کاربری تغییر نکرد.'})
