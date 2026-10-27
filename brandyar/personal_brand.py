import hashlib
import json
import secrets
import sqlite3
import time
import uuid
from http.cookies import SimpleCookie
from pathlib import Path
from urllib.parse import parse_qs, urlencode, urlsplit

import admin_workspace
import personal_brand_model as model


def now():
    return int(time.time())


def uid():
    return str(uuid.uuid4())


def digest(value):
    return hashlib.sha256(value.encode()).hexdigest()


def dumps(value):
    return json.dumps(value, ensure_ascii=False, separators=(',', ':'))


def initialize(db):
    exists = db.execute("SELECT 1 FROM sqlite_master WHERE name='pb_schema_migrations'").fetchone()
    if exists and db.execute('SELECT 1 FROM pb_schema_migrations WHERE version=4').fetchone() and db.execute("SELECT 1 FROM pb_template_versions WHERE id='pb-test-month-v4'").fetchone() and db.execute("SELECT 1 FROM pb_scoring_models WHERE id='pb-score-month-v4'").fetchone():
        return
    try:
        if not exists:
            db.executescript('BEGIN IMMEDIATE;\n' + Path(__file__).with_name('personal_brand_migration_001.sql').read_text())
            db.execute('INSERT INTO pb_templates VALUES(?,?,?)', ('personal-brand', model.TITLE, now()))
            db.commit()
        db.execute('BEGIN IMMEDIATE')
        if not db.execute('SELECT 1 FROM pb_schema_migrations WHERE version=2').fetchone():
            for statement in Path(__file__).with_name(
                'personal_brand_migration_002.sql').read_text().split(';'):
                if statement.strip():
                    db.execute(statement)
            version = max(2, db.execute('SELECT coalesce(max(version),0)+1 FROM pb_template_versions').fetchone()[0])
            db.execute("UPDATE pb_template_versions SET status='inactive' WHERE status='published'")
            body = model.template()
            db.execute('INSERT INTO pb_template_versions VALUES(?,?,?,?,?,?,NULL)', ('pb-test-24-v2', 'personal-brand', version, 'published', dumps(body), now()))
            save_questions(db, 'pb-test-24-v2', body)
            scoring_version = max(2, db.execute('SELECT coalesce(max(version),0)+1 FROM pb_scoring_models').fetchone()[0])
            db.execute("UPDATE pb_scoring_models SET status='inactive' WHERE status='published'")
            db.execute('INSERT INTO pb_scoring_models VALUES(?,?,?,?,?,NULL)', ('pb-score-rules-v2', scoring_version, 'published', dumps(model.model()), now()))
        if not db.execute('SELECT 1 FROM pb_schema_migrations WHERE version=3').fetchone():
            for statement in Path(__file__).with_name(
                'personal_brand_migration_003.sql').read_text().split(';'):
                if statement.strip():
                    db.execute(statement)
        if not db.execute("SELECT 1 FROM pb_template_versions WHERE id='pb-test-15-v3'").fetchone():
            version = max(3, db.execute('SELECT coalesce(max(version),0)+1 FROM pb_template_versions').fetchone()[0])
            db.execute("UPDATE pb_template_versions SET status='inactive' WHERE status='published'")
            body = model.template_v3()
            db.execute('INSERT INTO pb_template_versions VALUES(?,?,?,?,?,?,NULL)', ('pb-test-15-v3', 'personal-brand', version, 'published', dumps(body), now()))
            save_questions(db, 'pb-test-15-v3', body)
        if not db.execute("SELECT 1 FROM pb_scoring_models WHERE id='pb-score-rules-v3'").fetchone():
            scoring_version = max(3, db.execute('SELECT coalesce(max(version),0)+1 FROM pb_scoring_models').fetchone()[0])
            db.execute("UPDATE pb_scoring_models SET status='inactive' WHERE status='published'")
            db.execute('INSERT INTO pb_scoring_models VALUES(?,?,?,?,?,NULL)', ('pb-score-rules-v3', scoring_version, 'published', dumps(model.model_v3()), now()))
        if not db.execute('SELECT 1 FROM pb_schema_migrations WHERE version=4').fetchone():
            import personal_brand_v4 as monthly
            for statement in Path(__file__).with_name('personal_brand_migration_004.sql').read_text().split(';'):
                if statement.strip():
                    db.execute(statement)
            version = db.execute('SELECT coalesce(max(version),0)+1 FROM pb_template_versions').fetchone()[0]
            scoring_version = db.execute('SELECT coalesce(max(version),0)+1 FROM pb_scoring_models').fetchone()[0]
            db.execute("UPDATE pb_template_versions SET status='inactive' WHERE status='published'")
            db.execute("UPDATE pb_scoring_models SET status='inactive' WHERE status='published'")
            body = monthly.template()
            db.execute('INSERT INTO pb_template_versions VALUES(?,?,?,?,?,?,NULL)', (monthly.TEMPLATE_ID, 'personal-brand', version, 'published', dumps(body), now()))
            save_questions(db, monthly.TEMPLATE_ID, body)
            db.execute('INSERT INTO pb_scoring_models VALUES(?,?,?,?,?,NULL)', (monthly.MODEL_ID, scoring_version, 'published', dumps(monthly.model()), now()))
        db.commit()
    except Exception:
        db.rollback()
        raise


def save_questions(db, version, body):
    questions = body.get('items') or body.get('behavior') or []
    for i, q in enumerate(questions):
        db.execute('INSERT INTO pb_questions VALUES(?,?,?,?,?)', (q['id'], version, q['dimension'], q['title'], q.get('order', i)))
        db.execute('INSERT INTO pb_question_rules VALUES(?,?,?,?)', (q['id'], version, q.get('weight', 1), int(q.get('active', True))))
        db.executemany('INSERT INTO pb_question_options VALUES(?,?,?,?)', [(q['id'], version, n + 1, title) for n, title in enumerate(body['likert'])])


def save_response_records(db, row, body, answers):
    if body.get('schema') != 4:
        return
    ids = [question[0] for section in ('base', 'image') for question in body[section]]
    ids += json.loads(row['question_order'])
    ids += [question[0] for section in ('evidence', 'online') for question in body[section]]
    for key in body['other']:
        if key in answers and key + '_other' not in answers:
            db.execute('DELETE FROM pb_response_records WHERE assessment_id=? AND question_id=?', (row['id'], key + '_other'))
    for key, value in answers.items():
        display_key = key.removesuffix('_other')
        if display_key not in ids:
            continue
        db.execute('INSERT INTO pb_response_records VALUES(?,?,?,?,?,?) ON CONFLICT(assessment_id,question_id) DO UPDATE SET value_json=excluded.value_json,recorded_at=excluded.recorded_at WHERE pb_response_records.value_json<>excluded.value_json',
                   (row['id'], key, row['template_version'], dumps(value), now(), ids.index(display_key)))


def audit(db, actor, action, entity='', context=None):
    db.execute('INSERT INTO pb_audit VALUES(?,?,?,?,?,?)', (uid(), actor, action, entity, dumps(context or {}), now()))


def event(db, owner, assessment, name, key, stage=None, status='success'):
    version = assessment['template_version'] if assessment else None
    identity = assessment['id'] if assessment else None
    db.execute('INSERT OR IGNORE INTO pb_events VALUES(?,?,?,?,?,?,?,?,?,?)', (uid(), owner, identity, name, version, stage, '{}', status, digest(owner + ':' + key), now()))


def session(handler, db):
    cookie = SimpleCookie()
    try:
        cookie.load(handler.headers.get('Cookie', ''))
    except Exception:
        return None
    value = cookie.get('__Host-pb')
    if not value or len(value.value) != 64:
        return None
    return db.execute('SELECT * FROM pb_sessions WHERE owner_hash=? AND expires>?', (digest(value.value), now())).fetchone()


def owned(db, identity, owner):
    row = db.execute('SELECT * FROM pb_assessments WHERE id=? AND owner_hash=? AND archived_at IS NULL', (identity, owner)).fetchone()
    if not row:
        raise LookupError('ارزیابی پیدا نشد یا متعلق به این نشست نیست.')
    return row


def active_connection(db, owner):
    return db.execute("SELECT * FROM pb_instagram_connections WHERE owner_hash=? AND status='connected'", (owner,)).fetchone()


def latest_connection(db, owner):
    return db.execute("SELECT * FROM pb_instagram_connections WHERE owner_hash=? ORDER BY CASE status WHEN 'connected' THEN 0 ELSE 1 END,granted_at DESC,rowid DESC LIMIT 1", (owner,)).fetchone()


def public_connection(row):
    if not row:
        return None
    return {k: row[k] for k in ('id', 'username', 'status', 'expires_at', 'synced_at', 'error_code')}


def instagram_context(db, owner):
    row = active_connection(db, owner)
    if not row or row['expires_at'] <= now():
        return None
    analysis = db.execute('SELECT body,created_at FROM pb_instagram_analysis WHERE connection_id=? ORDER BY created_at DESC,rowid DESC LIMIT 1', (row['id'],)).fetchone()
    profile = db.execute('SELECT body FROM pb_instagram_profiles WHERE connection_id=? ORDER BY created_at DESC,rowid DESC LIMIT 1', (row['id'],)).fetchone()
    return {'connection_id': row['id'], 'profile': json.loads(profile['body']), 'observations': json.loads(analysis['body']), 'synced_at': analysis['created_at'], 'verified_source': 'official_instagram_api'} if analysis and profile else None


def lead_registered(db, owner, assessment_id):
    return db.execute('SELECT 1 FROM pb_leads WHERE owner_hash=? AND assessment_id=?', (owner, assessment_id)).fetchone() is not None


def report_available(db, owner, identity):
    row = owned(db, identity, owner)
    template = db.execute('SELECT body FROM pb_template_versions WHERE id=?', (row['template_version'],)).fetchone()
    return json.loads(template['body']).get('schema') == 4 or lead_registered(db, owner, identity)


def normalize_phone(value):
    if not isinstance(value, str):
        raise ValueError('شمارهٔ موبایل را وارد کنید.')
    digits = value.translate(str.maketrans('۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩', '01234567890123456789'))
    if any(c not in '0123456789+ -()' for c in digits):
        raise ValueError('یک شمارهٔ موبایل معتبر ایران وارد کن.')
    digits = ''.join(c for c in digits if c in '0123456789')
    if digits.startswith('0098'):
        digits = '0' + digits[4:]
    elif digits.startswith('98'):
        digits = '0' + digits[2:]
    if len(digits) != 11 or not digits.startswith('09'):
        raise ValueError('یک شمارهٔ موبایل معتبر ایران وارد کنید.')
    return digits


def report_preview(report):
    return {key: report[key] for key in ('title', 'total', 'stage', 'confidence', 'summary', 'top_opportunity', 'preview_opportunities', 'version', 'created_at', 'template_version', 'scoring_version') if key in report}


def assessment_data(db, row, full=True):
    template = json.loads(db.execute('SELECT body FROM pb_template_versions WHERE id=?', (row['template_version'],)).fetchone()[0])
    answers = {str(v['step']): json.loads(v['raw_json']) for v in db.execute('SELECT * FROM pb_answers WHERE assessment_id=?', (row['id'],))}
    for draft in db.execute('SELECT step,body FROM pb_answer_drafts WHERE assessment_id=?', (row['id'],)):
        answers[str(draft['step'])] = json.loads(draft['body'])
    reports = [dict(v) for v in db.execute('SELECT v.id,v.version,v.body,v.created_at,v.scoring_version,v.reason FROM pb_report_versions v JOIN pb_reports r ON r.id=v.report_id WHERE r.assessment_id=? ORDER BY v.version DESC', (row['id'],))]
    for report in reports:
        report['body'] = json.loads(report['body'])
        if not full:
            report['body'] = report_preview(report['body'])
    return {'assessment': {k: row[k] for k in ('id', 'state', 'stage', 'revision', 'created_at', 'updated_at', 'template_version', 'scoring_version')}, 'template': template, 'order': json.loads(row['question_order']), 'answers': answers, 'reports': reports, 'report_unlocked': full}


def create_report(db, row, reason, scoring_version=None):
    answers = {v['step']: json.loads(v['normalized_json']) for v in db.execute('SELECT * FROM pb_answers WHERE assessment_id=?', (row['id'],))}
    if set(answers) != {1, 2, 3, 4, 5}:
        raise ValueError('همهٔ مراحل را تکمیل کنید.')
    template = json.loads(db.execute('SELECT body FROM pb_template_versions WHERE id=?', (row['template_version'],)).fetchone()[0])
    scoring_version = scoring_version or row['scoring_version']
    selected = db.execute("SELECT body FROM pb_scoring_models WHERE id=? AND status<>'draft'", (scoring_version,)).fetchone()
    if not selected:
        raise ValueError('نسخهٔ منتشرشدهٔ مدل موجود نیست.')
    scoring = json.loads(selected[0])
    connection = instagram_context(db, row['owner_hash']) if template.get('schema') != 4 else None
    choice = answers[5].get('choice', 'skip')
    if choice == 'connected' and not connection:
        raise ValueError('همگام‌سازی معتبر موجود نیست؛ دوباره همگام‌سازی یا ادامه بدون اتصال را انتخاب کنید.')
    if choice == 'skip':
        connection = None
    for step, answer in answers.items():
        model.validate_step(step, answer, template)
    run_id = uid()
    db.execute('INSERT INTO pb_analysis_runs VALUES(?,?,?,?,?,?,?)', (run_id, row['id'], scoring['analysis_version'], 'running', None, now(), None))
    report = model.score(answers, template, scoring, connection)
    parent = db.execute('SELECT id FROM pb_reports WHERE assessment_id=?', (row['id'],)).fetchone()
    parent_id = parent['id'] if parent else uid()
    if not parent:
        db.execute('INSERT INTO pb_reports VALUES(?,?,?)', (parent_id, row['id'], now()))
    version = db.execute('SELECT coalesce(max(version),0)+1 FROM pb_report_versions WHERE report_id=?', (parent_id,)).fetchone()[0]
    identity = uid()
    report.update({'version': version, 'created_at': now(), 'template_version': row['template_version'], 'scoring_version': scoring_version})
    event(db, row['owner_hash'], row, 'report_started', 'report-start:' + identity)
    db.execute('INSERT INTO pb_report_versions VALUES(?,?,?,?,?,?,?,?)', (identity, parent_id, version, scoring_version, dumps(report), dumps({'answers': answers, 'template': template, 'model': scoring, 'instagram': connection}), reason, now()))
    for dimension in report['dimensions']:
        db.execute('INSERT INTO pb_scores VALUES(?,?,?)', (identity, dimension['key'], dimension['score']))
    for recommendation in report['immediate'] + report['thirty_days']:
        db.execute('INSERT INTO pb_recommendations VALUES(?,?,?,?,?)', (uid(), identity, recommendation['dimension'], dumps(recommendation), now()))
    db.execute("UPDATE pb_assessments SET state='completed',completed_at=?,updated_at=? WHERE id=?", (now(), now(), row['id']))
    event(db, row['owner_hash'], row, 'report_ready', 'report-ready:' + identity)
    db.execute("UPDATE pb_analysis_runs SET status='success',completed_at=? WHERE id=?", (now(), run_id))
    event(db, row['owner_hash'], row, 'assessment_completed', 'completed:' + identity)
    audit(db, row['owner_hash'], 'report_generated', row['id'], {'version': version})
    return report


def erase_instagram(db, owner):
    rows = db.execute('SELECT id FROM pb_instagram_connections WHERE owner_hash=?', (owner,)).fetchall()
    db.execute('DELETE FROM pb_instagram_connections WHERE owner_hash=?', (owner,))
    db.execute('DELETE FROM pb_oauth_states WHERE owner_hash=?', (owner,))
    db.execute('UPDATE pb_consents SET revoked_at=? WHERE owner_hash=? AND revoked_at IS NULL', (now(), owner))
    # Derived snapshots must be erased together with their source data.
    db.execute("DELETE FROM pb_report_versions WHERE report_id IN (SELECT r.id FROM pb_reports r JOIN pb_assessments a ON a.id=r.assessment_id WHERE a.owner_hash=?) AND json_extract(body,'$.instagram') IS NOT NULL", (owner,))
    return len(rows)


def maintenance(db):
    days = db.execute('SELECT retention_days FROM pb_privacy_settings WHERE id=1').fetchone()[0]
    cutoff = now() - days * 86400
    db.execute('DELETE FROM pb_oauth_states WHERE expires<=?', (now(),))
    db.execute("UPDATE pb_instagram_connections SET status='expired',token_cipher=NULL,updated_at=? WHERE status='connected' AND expires_at<=?", (now(), now()))
    for table in ('pb_instagram_profiles', 'pb_instagram_media', 'pb_instagram_analysis'):
        db.execute('DELETE FROM ' + table + ' WHERE created_at<?', (cutoff,))
    db.execute("DELETE FROM pb_report_versions WHERE json_extract(body,'$.instagram.synced_at')<?", (cutoff,))
    db.execute('DELETE FROM pb_instagram_connections WHERE owner_hash IN (SELECT owner_hash FROM pb_sessions WHERE expires<=?)', (now(),))
    db.commit()


def mutate(db, owner, data):
    action = data.get('action')
    if action == 'start':
        draft = db.execute("SELECT id FROM pb_assessments WHERE owner_hash=? AND state='draft' AND archived_at IS NULL ORDER BY updated_at DESC LIMIT 1", (owner,)).fetchone()
        if draft:
            return {'id': draft['id'], 'resumed': True}
        completed = db.execute("SELECT id FROM pb_assessments WHERE owner_hash=? AND state='completed' AND archived_at IS NULL ORDER BY completed_at DESC LIMIT 1", (owner,)).fetchone()
        if completed and data.get('confirmed') is not True:
            return {'id': completed['id']}
        recent = db.execute('SELECT count(*) FROM pb_assessments WHERE owner_hash=? AND created_at>?', (owner, now() - 3600)).fetchone()[0]
        if recent >= 10:
            raise ValueError('در یک ساعت حداکثر ده ارزیابی تازه می‌توانید بسازید.')
        version = db.execute("SELECT * FROM pb_template_versions WHERE status='published' ORDER BY version DESC LIMIT 1").fetchone()
        scoring = db.execute("SELECT * FROM pb_scoring_models WHERE status='published' ORDER BY version DESC LIMIT 1").fetchone()
        if not version or not scoring:
            raise ValueError('نسخهٔ فعال ارزیابی موجود نیست.')
        body = json.loads(version['body'])
        questions = body.get('items') or body.get('behavior') or []
        order = [q['id'] for q in sorted(questions, key=lambda q: q.get('order', 0)) if q.get('active', True)]
        if body.get('schema') == 4:
            from personal_brand_v4 import question_order
            order = question_order(body)
        identity = uid()
        db.execute('INSERT INTO pb_assessments VALUES(?,?,?,?,?,?,?,?,?,?,?,?)', (identity, owner, version['id'], scoring['id'], dumps(order), 'draft', 0, 0, now(), now(), None, None))
        row = owned(db, identity, owner)
        event(db, owner, row, 'assessment_started', 'start:' + identity)
        return {'id': identity}
    if action == 'delete_instagram':
        request = uid()
        db.execute('INSERT INTO pb_deletion_requests VALUES(?,?,?,?,?,NULL)', (request, owner, 'instagram', 'processing', now()))
        event(db, owner, None, 'data_deletion_requested', 'delete:' + request)
        erase_instagram(db, owner)
        db.execute("UPDATE pb_deletion_requests SET status='completed',completed_at=? WHERE id=?", (now(), request))
        audit(db, owner, 'instagram_deleted', request)
        return {'request_id': request, 'status': 'completed'}
    if action == 'disconnect':
        db.execute("UPDATE pb_instagram_connections SET status='disconnected',token_cipher=NULL,updated_at=? WHERE owner_hash=?", (now(), owner))
        db.execute('UPDATE pb_consents SET revoked_at=? WHERE owner_hash=? AND revoked_at IS NULL', (now(), owner))
        db.execute('DELETE FROM pb_oauth_states WHERE owner_hash=?', (owner,))
        event(db, owner, None, 'disconnected', 'disconnect:' + uid())
        audit(db, owner, 'instagram_disconnected')
        return {'ok': True}
    row = owned(db, data.get('id'), owner)
    if action == 'unlock_report':
        if data.get('consent') is not True:
            raise ValueError('برای مشاهدهٔ گزارش کامل، رضایت خود را تأیید کنید.')
        if row['state'] != 'completed':
            raise ValueError('ابتدا ارزیابی را کامل کن.')
        phone = normalize_phone(data.get('phone'))
        db.execute('INSERT INTO pb_leads VALUES(?,?,?,?,?) ON CONFLICT(assessment_id) DO UPDATE SET phone=excluded.phone,consent_version=excluded.consent_version,created_at=excluded.created_at', (row['id'], owner, phone, 'report-access-v1', now()))
        event(db, owner, row, 'lead_registered', 'lead:' + row['id'])
        audit(db, owner, 'report_unlocked', row['id'])
        return {'ok': True}
    if action == 'restart':
        if row['state'] != 'completed' or data.get('confirmed') is not True:
            raise ValueError('شروع دوباره فقط پس از تکمیل و تأیید تو انجام می‌شود.')
        return mutate(db, owner, {'action': 'start', 'confirmed': True})
    if action == 'question_feedback':
        body = json.loads(db.execute('SELECT body FROM pb_template_versions WHERE id=?', (row['template_version'],)).fetchone()[0])
        ids = {q['id'] for q in body.get('behavior', body.get('items', []))}
        if data.get('question_id') not in ids or type(data.get('clarity')) is not int or data['clarity'] not in (1, 2, 3):
            raise ValueError('بازخورد معتبر نیست.')
        db.execute('INSERT INTO pb_question_feedback VALUES(?,?,?,?) ON CONFLICT(assessment_id,question_id) DO UPDATE SET clarity=excluded.clarity,updated_at=excluded.updated_at', (row['id'], data['question_id'], data['clarity'], now()))
        return {'ok': True}
    if action == 'draft':
        if row['state'] != 'draft' or data.get('revision') != row['revision']:
            raise ValueError('صفحه را دوباره باز کن تا ادامه بدهی.')
        step = data.get('step')
        if type(step) is not int or not 1 <= step <= 5:
            raise ValueError('مرحله معتبر نیست.')
        body = json.loads(db.execute('SELECT body FROM pb_template_versions WHERE id=?', (row['template_version'],)).fetchone()[0])
        answers = model.validate_partial(step, data.get('answers'), body)
        save_response_records(db, row, body, answers)
        db.execute('INSERT INTO pb_answer_drafts VALUES(?,?,?,?) ON CONFLICT(assessment_id,step) DO UPDATE SET body=excluded.body,updated_at=excluded.updated_at', (row['id'], step, dumps(answers), now()))
        return {'ok': True}
    if action == 'edit':
        db.execute("UPDATE pb_assessments SET state='draft',stage=0,revision=revision+1,updated_at=? WHERE id=?", (now(), row['id']))
        audit(db, owner, 'assessment_edit_started', row['id'])
        return {'ok': True}
    if action == 'save':
        if row['state'] != 'draft' or data.get('revision') != row['revision']:
            raise ValueError('نسخهٔ فرم تغییر کرده یا تکمیل شده است؛ اطلاعات را دوباره دریافت کنید.')
        step = data.get('step')
        if type(step) is not int or not 1 <= step <= 5:
            raise ValueError('مرحله معتبر نیست.')
        body = json.loads(db.execute('SELECT body FROM pb_template_versions WHERE id=?', (row['template_version'],)).fetchone()[0])
        normalized = model.validate_step(step, data.get('answers'), body)
        save_response_records(db, row, body, normalized)
        elapsed = data.get('elapsed_ms', 0)
        if type(elapsed) is not int or not 0 <= elapsed <= 86400000:
            raise ValueError('زمان پاسخ معتبر نیست.')
        db.execute('INSERT INTO pb_answers VALUES(?,?,?,?,?,?,?) ON CONFLICT(assessment_id,step) DO UPDATE SET raw_json=excluded.raw_json,normalized_json=excluded.normalized_json,elapsed_ms=excluded.elapsed_ms,updated_at=excluded.updated_at', (row['id'], step, dumps(data['answers']), dumps(normalized), elapsed, now(), now()))
        db.execute('DELETE FROM pb_answer_drafts WHERE assessment_id=? AND step=?', (row['id'], step))
        if step == 3:
            timings = data.get('question_times', {})
            if not isinstance(timings, dict) or set(timings) - set(normalized) or any(type(v) is not int or not 0 <= v <= 86400000 for v in timings.values()):
                raise ValueError('زمان گویه‌ها معتبر نیست.')
            db.executemany('INSERT INTO pb_question_metrics VALUES(?,?,?,?) ON CONFLICT(assessment_id,question_id) DO UPDATE SET elapsed_ms=excluded.elapsed_ms,updated_at=excluded.updated_at', [(row['id'], key, value, now()) for key, value in timings.items()])
        if step == 4:
            db.execute('DELETE FROM pb_evidence WHERE assessment_id=?', (row['id'],))
            db.execute('INSERT INTO pb_evidence VALUES(?,?,?,?)', (uid(), row['id'], dumps(normalized), now()))
        db.execute('UPDATE pb_assessments SET stage=max(stage,?),revision=revision+1,updated_at=? WHERE id=?', (step, now(), row['id']))
        event(db, owner, row, 'step_completed', f'step:{row["id"]}:{step}', step)
        if step == 5 and 'choice' in normalized:
            event(db, owner, row, 'instagram_skipped' if normalized['choice'] == 'skip' else 'instagram_selected', 'choice:' + row['id'])
        return {'revision': row['revision'] + 1}
    if action == 'report':
        if row['state'] == 'completed':
            reports = assessment_data(db, row, full=True)['reports']
            if not reports:
                raise ValueError('گزارش بر اساس سیاست حذف داده پاک شده است؛ ارزیابی تازه بسازید.')
            return {'report': reports[0]['body']}
        return {'report': create_report(db, row, 'تولید اولیه')}
    if action == 'offer_view':
        event(db, owner, row, 'instagram_offer_viewed', 'offer:' + row['id'], 5)
        return {'ok': True}
    if action == 'export_report':
        reports = assessment_data(db, row, full=True)['reports']
        if not reports:
            raise LookupError('گزارشی برای دریافت موجود نیست.')
        audit(db, owner, 'report_exported', row['id'], {'version': reports[0]['version']})
        return {'report': reports[0]['body']}
    if action == 'view_report':
        event(db, owner, row, 'report_viewed', 'view:' + row['id'])
        return {'ok': True}
    if action == 'abandon':
        event(db, owner, row, 'assessment_abandoned', 'abandon:' + row['id'])
        return {'ok': True}
    if action == 'delete_assessment':
        request = uid()
        db.execute('INSERT INTO pb_deletion_requests VALUES(?,?,?,?,?,?)', (request, owner, 'assessment', 'completed', now(), now()))
        event(db, owner, row, 'data_deletion_requested', 'delete:' + request)
        db.execute('DELETE FROM pb_assessments WHERE id=?', (row['id'],))
        audit(db, owner, 'assessment_deleted', request)
        return {'request_id': request, 'status': 'completed'}
    raise ValueError('عملیات پشتیبانی نمی‌شود.')


def admin_read(db, staff, query):
    if not admin_workspace.allowed(staff['role'], 'assessments'):
        raise PermissionError('به ارزیابی‌ها دسترسی ندارید.')
    if query.get('action', [''])[0] == 'validation_export':
        if not admin_workspace.allowed(staff['role'], 'export'):
            raise PermissionError('اجازهٔ خروجی گرفتن ندارید.')
        version = query.get('template_version', [None])[0]
        if not version:
            version = db.execute("SELECT id FROM pb_template_versions WHERE status='published' ORDER BY version DESC LIMIT 1").fetchone()[0]
        rows = [json.loads(r[0]) for r in db.execute('SELECT a.normalized_json FROM pb_answers a JOIN pb_assessments s ON s.id=a.assessment_id WHERE a.step=3 AND s.template_version=? ORDER BY s.id LIMIT 5000', (version,))]
        audit(db, 'staff:' + str(staff['staff_id']), 'anonymous_validation_export', version, {'rows': len(rows)})
        return {'template_version': version, 'responses': rows, 'excluded': ['شناسه، زمان، متن آزاد، لینک، دادهٔ پیج و اطلاعات نشست']}
    identity = query.get('id', [''])[0]
    if identity:
        if not admin_workspace.allowed(staff['role'], 'private'):
            raise PermissionError('مشاهدهٔ پاسخ و گزارش شخصی برای نقش شما مجاز نیست.')
        row = db.execute('SELECT * FROM pb_assessments WHERE id=?', (identity,)).fetchone()
        if not row:
            raise LookupError('ارزیابی پیدا نشد.')
        audit(db, 'staff:' + str(staff['staff_id']), 'view_assessment', identity)
        detail = assessment_data(db, row, full=True)
        detail['analysis_runs'] = [dict(r) for r in db.execute('SELECT id,engine_version,status,error_code,created_at,completed_at FROM pb_analysis_runs WHERE assessment_id=? ORDER BY created_at DESC', (identity,))]
        detail['connection'] = public_connection(latest_connection(db, row['owner_hash']))
        detail['instagram'] = instagram_context(db, row['owner_hash'])
        detail['audit'] = [dict(r) for r in db.execute('SELECT action,created_at FROM pb_audit WHERE entity_id=? ORDER BY created_at DESC LIMIT 100', (identity,))]
        lead = db.execute('SELECT phone,consent_version,created_at FROM pb_leads WHERE assessment_id=?', (identity,)).fetchone()
        detail['lead'] = dict(lead) if lead else None
        return detail
    filters, params = [], []
    for key, expression in {'state': 's.state', 'maturity': "json_extract(v.body,'$.stage')", 'confidence': "json_extract(v.body,'$.confidence')"}.items():
        value = query.get(key, [''])[0]
        if value:
            filters.append(expression + '=?')
            params.append(model.clean(value, 100))
    search = query.get('search', [''])[0]
    if search:
        safe_search = model.clean(search, 100)
        if admin_workspace.allowed(staff['role'], 'private'):
            filters.append('(s.id LIKE ? OR l.phone LIKE ?)')
            params.extend(['%' + safe_search + '%', '%' + safe_search + '%'])
        else:
            filters.append('s.id LIKE ?')
            params.append('%' + safe_search + '%')
    connected = query.get('connected', [''])[0]
    if connected in {'yes', 'no'}:
        filters.append("json_extract(v.body,'$.instagram') IS " + ('NOT NULL' if connected == 'yes' else 'NULL'))
    offset = int(query.get('offset', ['0'])[0])
    if not 0 <= offset <= 1000000:
        raise ValueError('صفحه معتبر نیست.')
    sql = " FROM pb_assessments s LEFT JOIN pb_leads l ON l.assessment_id=s.id LEFT JOIN pb_reports r ON r.assessment_id=s.id LEFT JOIN pb_report_versions v ON v.id=(SELECT id FROM pb_report_versions WHERE report_id=r.id ORDER BY version DESC LIMIT 1)"
    where = ' WHERE ' + ' AND '.join(filters) if filters else ''
    total = db.execute('SELECT count(*)' + sql + where, params).fetchone()[0]
    rows = [dict(r) for r in db.execute("SELECT s.id,s.state,s.stage,s.template_version,s.scoring_version,s.created_at,s.completed_at,s.archived_at,CASE WHEN l.assessment_id IS NULL THEN 'not_registered' ELSE 'registered' END AS lead_status,(SELECT status FROM pb_analysis_runs WHERE assessment_id=s.id ORDER BY created_at DESC,rowid DESC LIMIT 1) AS analysis_status,(SELECT status FROM pb_instagram_connections WHERE owner_hash=s.owner_hash ORDER BY granted_at DESC,rowid DESC LIMIT 1) AS instagram_status,json_extract(v.body,'$.stage') AS maturity,json_extract(v.body,'$.confidence') AS confidence" + sql + where + ' ORDER BY s.created_at DESC,s.id LIMIT 100 OFFSET ?', [*params, offset])]
    templates = [dict(r) for r in db.execute('SELECT * FROM pb_template_versions ORDER BY version DESC')]
    models = [dict(r) for r in db.execute('SELECT * FROM pb_scoring_models ORDER BY version DESC')]
    for r in templates + models:
        r['body'] = json.loads(r['body'])
    private = admin_workspace.allowed(staff['role'], 'private')
    connections = [public_connection(r) for r in db.execute('SELECT * FROM pb_instagram_connections ORDER BY granted_at DESC LIMIT 100')] if private else []
    jobs = [dict(r) for r in db.execute('SELECT id,connection_id,status,error_code,created_at,completed_at FROM pb_instagram_sync_jobs ORDER BY created_at DESC LIMIT 100')]
    metrics = [dict(r) for r in db.execute('SELECT step,count(*) AS completed,avg(elapsed_ms) AS elapsed_ms FROM pb_answers GROUP BY step')]
    events = [dict(r) for r in db.execute('SELECT event,count(*) AS count FROM pb_events GROUP BY event')]
    question_metrics = [dict(r) for r in db.execute('SELECT question_id,count(*) AS measured,avg(elapsed_ms) AS elapsed_ms FROM pb_question_metrics GROUP BY question_id')]
    import personal_brand_validation
    validation = []
    for template in templates:
        samples = [json.loads(r[0]) for r in db.execute('SELECT a.normalized_json FROM pb_answers a JOIN pb_assessments s ON s.id=a.assessment_id WHERE a.step=3 AND s.template_version=? LIMIT 5000', (template['id'],))]
        validation.append({'template_version': template['id'], **personal_brand_validation.summarize(samples, template['body'].get('items', template['body'].get('behavior', [])))})
    question_feedback = [dict(r) for r in db.execute('SELECT s.template_version,f.question_id,count(*) AS responses,avg(f.clarity) AS clarity FROM pb_question_feedback f JOIN pb_assessments s ON s.id=f.assessment_id GROUP BY s.template_version,f.question_id')]
    return {'question_feedback': question_feedback, 'total': total, 'offset': offset, 'question_metrics': question_metrics, 'validation': validation, 'permissions': {'private': private, 'manage': admin_workspace.allowed(staff['role'], 'publish'), 'export': admin_workspace.allowed(staff['role'], 'export')}, 'assessments': rows, 'templates': templates, 'models': models, 'connections': connections, 'sync_jobs': jobs, 'metrics': metrics, 'events': events, 'retention_days': db.execute('SELECT retention_days FROM pb_privacy_settings WHERE id=1').fetchone()[0], 'feedback': [dict(r) for r in db.execute('SELECT template_version,body,created_at FROM pb_expert_feedback ORDER BY created_at DESC LIMIT 100')]}


def admin_mutate(db, staff, data):
    if not admin_workspace.allowed(staff['role'], 'publish') or not admin_workspace.allowed(staff['role'], 'assessments'):
        raise PermissionError('این تغییر فقط برای مالک یا مدیر مجاز است.')
    if data.get('confirmed') is not True:
        raise ValueError('تأیید نهایی عملیات الزامی است.')
    action = data.get('action')
    reason = model.clean(data.get('reason', ''), 500, True)
    actor = 'staff:' + str(staff['staff_id'])
    if action in {'template_draft', 'model_draft'}:
        is_template = action == 'template_draft'
        body = data.get('body')
        (model.validate_template if is_template else model.validate_model)(body)
        table = 'pb_template_versions' if is_template else 'pb_scoring_models'
        version = db.execute('SELECT coalesce(max(version),0)+1 FROM ' + table).fetchone()[0]
        identity = uid()
        if is_template:
            db.execute('INSERT INTO pb_template_versions VALUES(?,?,?,?,?,?,?)', (identity, 'personal-brand', version, 'draft', dumps(body), now(), staff['staff_id']))
            save_questions(db, identity, body)
        else:
            db.execute('INSERT INTO pb_scoring_models VALUES(?,?,?,?,?,?)', (identity, version, 'draft', dumps(body), now(), staff['staff_id']))
    elif action in {'template_publish', 'model_publish', 'template_inactive', 'model_inactive'}:
        table = 'pb_template_versions' if action.startswith('template') else 'pb_scoring_models'
        identity = data.get('id')
        if not db.execute('SELECT 1 FROM ' + table + ' WHERE id=?', (identity,)).fetchone():
            raise LookupError('نسخه پیدا نشد.')
        if action.endswith('publish'):
            db.execute("UPDATE " + table + " SET status='inactive' WHERE status='published'")
        db.execute('UPDATE ' + table + ' SET status=? WHERE id=?', ('published' if action.endswith('publish') else 'inactive', identity))
    elif action in {'archive', 'regenerate'}:
        identity = data.get('id')
        row = db.execute('SELECT * FROM pb_assessments WHERE id=?', (identity,)).fetchone()
        if not row:
            raise LookupError('ارزیابی پیدا نشد.')
        if action == 'archive':
            db.execute('UPDATE pb_assessments SET archived_at=? WHERE id=?', (now(), identity))
        else:
            event(db, row['owner_hash'], row, 'report_update_requested', 'update:' + uid())
            create_report(db, row, reason, data.get('scoring_version'))
    elif action == 'erase_assessment':
        identity = data.get('id')
        row = db.execute('SELECT * FROM pb_assessments WHERE id=?', (identity,)).fetchone()
        if not row or not admin_workspace.allowed(staff['role'], 'private'):
            raise PermissionError('دسترسی به حذف این ارزیابی ندارید.')
        mutate(db, row['owner_hash'], {'action': 'delete_assessment', 'id': identity})
    elif action == 'disconnect_connection':
        identity = data.get('id')
        connection = db.execute('SELECT * FROM pb_instagram_connections WHERE id=?', (identity,)).fetchone()
        if not connection:
            raise LookupError('اتصال پیدا نشد.')
        mutate(db, connection['owner_hash'], {'action': 'disconnect'})
    elif action == 'privacy':
        days = data.get('retention_days')
        if type(days) is not int or not 1 <= days <= 365:
            raise ValueError('مدت نگهداری باید بین یک تا ۳۶۵ روز باشد.')
        db.execute('UPDATE pb_privacy_settings SET retention_days=?,updated_at=? WHERE id=1', (days, now()))
        identity = 'privacy'
    elif action == 'feedback':
        identity = data.get('id')
        template = db.execute('SELECT body FROM pb_template_versions WHERE id=?', (identity,)).fetchone()
        if not template:
            raise LookupError('نسخه پیدا نشد.')
        rubric = data.get('rubric')
        body = reason
        if rubric is not None:
            questions = json.loads(template['body'])
            keys = {'fit', 'clarity', 'nonjudgment', 'unambiguous', 'distinct'}
            if (not isinstance(rubric, dict) or set(rubric) != keys
                    or any(type(value) is not int or not 1 <= value <= 3 for value in rubric.values())
                    or data.get('question_id') not in {q['id'] for q in questions.get('items', questions.get('behavior', []))}):
                raise ValueError('معیارهای بازبینی سؤال کامل نیست.')
            body = dumps({'question_id': data['question_id'], 'rubric': rubric, 'reason': reason})
        db.execute('INSERT INTO pb_expert_feedback VALUES(?,?,?,?,?)', (uid(), identity, staff['staff_id'], body, now()))
    else:
        raise ValueError('عملیات مدیریتی معتبر نیست.')
    audit(db, actor, action, identity, {'reason': reason})
    return {'ok': True}


def throttle(db, handler, action, maximum, seconds=60):
    import ipaddress
    peer = handler.client_address[0]
    source = handler.headers.get('X-Real-IP', peer) if peer in {'127.0.0.1', '::1'} else peer
    try:
        source = str(ipaddress.ip_address(source))
    except ValueError:
        source = peer
    source_hash = digest('pb-rate:' + source)
    db.execute('BEGIN IMMEDIATE')
    db.execute('DELETE FROM pb_request_limits WHERE created_at<?', (now() - 900,))
    count = db.execute('SELECT count(*) FROM pb_request_limits WHERE source_hash=? AND action=? AND created_at>?', (source_hash, action, now() - seconds)).fetchone()[0]
    if count < maximum:
        db.execute('INSERT INTO pb_request_limits VALUES(?,?,?)', (source_hash, action, now()))
    db.commit()
    return count >= maximum


def dispatch(handler, connect, admin=False, write=False):
    import personal_brand_instagram as instagram
    trace = uid()
    headers = {}
    owner, data = None, {}
    try:
        if not handler.assessment_https():
            raise PermissionError('برای این عملیات اتصال HTTPS لازم است.')
        with connect() as db:
            maintenance(db)
            if write and throttle(db, handler, 'write', 120):
                return handler.json(429, {'error': 'تعداد درخواست زیاد است؛ یک دقیقه دیگر تلاش کنید.'})
            if admin:
                staff = handler.session(db)
                if not staff:
                    return handler.json(401, {'error': 'ابتدا وارد پنل مدیریت شوید.'})
                if write:
                    data = handler.request_data(65536)
                    if not handler.safe_origin() or not secrets.compare_digest(str(data.get('csrf', '')), staff['csrf']):
                        raise PermissionError('نشست فرم یا مبدأ درخواست معتبر نیست.')
                    db.execute('BEGIN IMMEDIATE')
                    result = admin_mutate(db, staff, data)
                else:
                    result = admin_read(db, staff, parse_qs(urlsplit(handler.path).query))
                    result['csrf'] = staff['csrf']
            else:
                principal = session(handler, db)
                query = parse_qs(urlsplit(handler.path).query)
                if not principal and not write and query.get('action', [''])[0] == 'bootstrap':
                    if throttle(db, handler, 'new_session', 30, 900):
                        return handler.json(429, {'error': 'ساخت نشست تازه موقتاً محدود شده است؛ بعداً دوباره تلاش کنید.'})
                    token = secrets.token_hex(32)
                    owner = digest(token)
                    db.execute('INSERT INTO pb_sessions VALUES(?,?,?,?)', (owner, secrets.token_hex(32), now(), now() + 30 * 86400))
                    headers['Set-Cookie'] = '__Host-pb=' + token + '; Secure; HttpOnly; SameSite=Lax; Path=/; Max-Age=2592000'
                    principal = db.execute('SELECT * FROM pb_sessions WHERE owner_hash=?', (owner,)).fetchone()
                if not principal:
                    return handler.json(401, {'error': 'نشست ارزیابی پایان یافته است؛ صفحه را دوباره باز کنید.'})
                owner = principal['owner_hash']
                if write:
                    data = handler.request_data(65536)
                    if not handler.safe_origin() or not secrets.compare_digest(str(data.get('csrf', '')), principal['csrf']):
                        raise PermissionError('نشست فرم یا مبدأ درخواست معتبر نیست.')
                    recent = db.execute('SELECT count(*) FROM pb_audit WHERE actor=? AND created_at>?', (owner, now() - 60)).fetchone()[0]
                    if recent >= 60:
                        return handler.json(429, {'error': 'تعداد درخواست زیاد است؛ یک دقیقه دیگر تلاش کنید.'})
                    if data.get('action') in {'oauth', 'sync'}:
                        db.commit()
                        result = instagram.begin(db, owner, data) if data['action'] == 'oauth' else instagram.sync(db, owner)
                    else:
                        db.execute('BEGIN IMMEDIATE')
                        if data.get('action') == 'edit':
                            raise PermissionError('برای شروع دوباره، در صفحهٔ نتیجه تأیید کن.')
                        if data.get('action') == 'export_report' and not report_available(db, owner, data.get('id')):
                            raise PermissionError('برای دریافت گزارش، ابتدا آن را با شمارهٔ موبایل باز کنید.')
                        result = mutate(db, owner, data)
                        if data.get('action') == 'report' and not report_available(db, owner, data.get('id')):
                            result['report'] = report_preview(result['report'])
                    audit(db, owner, 'request:' + str(data.get('action', '')), '')
                elif query.get('action', [''])[0] == 'bootstrap':
                    result = {'csrf': principal['csrf'], 'instagram_available': instagram.configured(), 'connection': public_connection(latest_connection(db, owner)), 'assessments': [dict(r) for r in db.execute('SELECT id,state,stage,created_at FROM pb_assessments WHERE owner_hash=? AND archived_at IS NULL ORDER BY created_at DESC', (owner,))]}
                else:
                    row = owned(db, query.get('id', [''])[0], owner)
                    result = assessment_data(db, row, full=admin or report_available(db, owner, row['id']))
            db.commit()
        return handler.json(200, {'ok': True, 'data': result, 'request_id': trace}, headers)
    except PermissionError as error:
        return handler.json(403, {'error': str(error), 'request_id': trace})
    except LookupError as error:
        return handler.json(404, {'error': str(error), 'request_id': trace})
    except (ValueError, TypeError, KeyError, RecursionError):
        if owner and data.get('action') == 'report':
            try:
                with connect() as failed_db:
                    row = owned(failed_db, data.get('id'), owner)
                    event(failed_db, owner, row, 'report_failed', trace, status='failed')
                    failed_db.execute('INSERT INTO pb_analysis_runs VALUES(?,?,?,?,?,?,?)', (trace, row['id'], 'structured-rules-v2', 'failed', 'invalid_or_incomplete_answers', now(), now()))
                    failed_db.commit()
            except (sqlite3.Error, LookupError):
                pass
        if data.get('action') == 'unlock_report':
            message = 'برای دیدن گزارش، رضایتت را تأیید کن.' if data.get('consent') is not True else 'یک شمارهٔ موبایل معتبر ایران وارد کن.'
            return handler.json(422, {'error': message, 'request_id': trace})
        return handler.json(422, {'error': 'یکی از پاسخ‌ها کامل نیست یا این مرحله نیاز به بررسی دارد؛ پاسخ‌هایت را بررسی کن و دوباره ادامه بده.', 'request_id': trace})
    except sqlite3.Error:
        return handler.json(503, {'error': 'ذخیره‌سازی موقتاً در دسترس نیست؛ دوباره تلاش کنید.', 'request_id': trace})
    except instagram.Unavailable:
        return handler.json(503, {'error': 'اتصال یا همگام‌سازی اینستاگرام انجام نشد؛ می‌توانید دوباره تلاش کنید یا بدون اتصال ادامه دهید.', 'request_id': trace})
