"""Identity records and the profile access point for the private Brandyar panel.

The signed-in owner is the existing assessment session cookie (`__Host-pb`), which is
the only per-person identifier this project has. It is provisional: it is scoped to the
browser, and it must be replaced by a real account layer when one exists.
"""
import json

import personal_brand as pb

PLANS = {
    'starter': {'name': 'شروع روشن'},
    'growth': {'name': 'مسیر رشد'},
}
REQUIRED = (
    'professionalRole', 'industry', 'targetDescription', 'problems',
    'valueProposition', 'professionalGoals',
)
LISTS = (
    'skills', 'services', 'differentiators', 'professionalGoals',
    'personalValues', 'preferredTopics', 'excludedTopics', 'needs', 'problems',
)
TEXTS = (
    'professionalRole', 'industry', 'experience', 'valueProposition',
    'desiredPerception', 'targetDescription', 'primaryGroup',
)
SECTIONS = {
    'work': ('professionalRole', 'industry'),
    'audience': ('targetDescription', 'problems'),
    'value': ('valueProposition',),
    'direction': ('professionalGoals',),
}
# Every stored field belongs to exactly one part, so un-approving after an edit stays scoped.
PART_FIELDS = {
    'work': ('professionalRole', 'industry', 'experience', 'skills', 'services'),
    'audience': ('targetDescription', 'primaryGroup', 'needs', 'problems'),
    'value': ('valueProposition', 'differentiators'),
    'direction': ('professionalGoals', 'desiredPerception', 'personalValues', 'preferredTopics',
                  'excludedTopics'),
}
MAX_TEXT = 2000
MAX_ITEMS = 20
MAX_ITEM = 160


def initialize(db):
    db.commit()
    db.executescript('''
        CREATE TABLE IF NOT EXISTS pb_identity_records (
            owner_hash TEXT PRIMARY KEY,
            body TEXT NOT NULL,
            status TEXT NOT NULL,
            completion INTEGER NOT NULL,
            created_at INTEGER NOT NULL,
            updated_at INTEGER NOT NULL,
            approved_at INTEGER
        );
        CREATE TABLE IF NOT EXISTS pb_identity_versions (
            id TEXT PRIMARY KEY,
            owner_hash TEXT NOT NULL,
            version INTEGER NOT NULL,
            action TEXT NOT NULL,
            body TEXT NOT NULL,
            created_at INTEGER NOT NULL
        );
        CREATE INDEX IF NOT EXISTS pb_identity_versions_owner ON pb_identity_versions(owner_hash, version);
        CREATE TABLE IF NOT EXISTS pb_identity_access (
            owner_hash TEXT PRIMARY KEY,
            plan_id TEXT NOT NULL,
            status TEXT NOT NULL,
            simulation INTEGER NOT NULL,
            updated_at INTEGER NOT NULL
        );
        CREATE TABLE IF NOT EXISTS pb_ai_outputs (
            id TEXT PRIMARY KEY,
            owner_hash TEXT NOT NULL,
            operation TEXT NOT NULL,
            status TEXT NOT NULL,
            input_json TEXT NOT NULL,
            output_json TEXT NOT NULL,
            created_at INTEGER NOT NULL,
            updated_at INTEGER NOT NULL
        );
        CREATE INDEX IF NOT EXISTS pb_ai_outputs_owner ON pb_ai_outputs(owner_hash, updated_at);
        CREATE TABLE IF NOT EXISTS pb_ai_feedback (
            id TEXT PRIMARY KEY,
            owner_hash TEXT NOT NULL,
            output_id TEXT NOT NULL,
            rating TEXT NOT NULL,
            note TEXT NOT NULL,
            created_at INTEGER NOT NULL
        );
        CREATE TABLE IF NOT EXISTS pb_brand_voice (
            owner_hash TEXT PRIMARY KEY,
            status TEXT NOT NULL,
            body TEXT NOT NULL,
            updated_at INTEGER NOT NULL
        );
        CREATE TABLE IF NOT EXISTS pb_content_pillars (
            owner_hash TEXT PRIMARY KEY,
            status TEXT NOT NULL,
            body TEXT NOT NULL,
            updated_at INTEGER NOT NULL
        );
        CREATE TABLE IF NOT EXISTS pb_content_items (
            id TEXT PRIMARY KEY,
            owner_hash TEXT NOT NULL,
            title TEXT NOT NULL,
            body TEXT NOT NULL,
            metadata TEXT NOT NULL,
            source TEXT NOT NULL,
            status TEXT NOT NULL,
            archived INTEGER NOT NULL DEFAULT 0,
            created_at INTEGER NOT NULL,
            updated_at INTEGER NOT NULL
        );
        CREATE INDEX IF NOT EXISTS pb_content_items_owner ON pb_content_items(owner_hash, updated_at);
    ''')
    db.commit()


def empty_body():
    return {
        'id': 'brand-identity', 'status': 'not_started', 'completionPercentage': 0,
        'professionalRole': '', 'industry': '', 'experience': '', 'skills': [], 'services': [],
        'targetAudience': {'description': '', 'primaryGroup': '', 'needs': [], 'problems': []},
        'valueProposition': '', 'differentiators': [], 'professionalGoals': [],
        'personalValues': [], 'preferredTopics': [], 'excludedTopics': [], 'desiredPerception': '',
        'testInsight': {'exists': False, 'summary': '', 'isApprovedForBrandUse': False, 'isResolved': False,
                        'source': ''},
        'approvedSections': [], 'draftSections': [],
        'createdAt': None, 'updatedAt': None, 'approvedAt': None,
    }


def _text(value):
    return value.strip()[:MAX_TEXT] if isinstance(value, str) else ''


def _items(value):
    if not isinstance(value, list):
        raise ValueError('فهرست این بخش معتبر نیست.')
    seen, result = set(), []
    for entry in value:
        if not isinstance(entry, str):
            raise ValueError('هر مورد فهرست باید متن باشد.')
        item = ' '.join(entry.split())[:MAX_ITEM]
        if item and item not in seen:
            seen.add(item)
            result.append(item)
    return result[:MAX_ITEMS]


def normalize(incoming, current, insight):
    body = empty_body()
    for key, value in empty_body().items():
        if key in ('id', 'status', 'completionPercentage', 'approvedSections', 'draftSections',
                   'testInsight') or key == 'targetAudience':
            continue
        previous = current.get(key)
        if isinstance(value, list):
            body[key] = list(previous) if isinstance(previous, list) else []
        else:
            body[key] = previous if isinstance(previous, str) else ''
    target = empty_body()['targetAudience']
    previous_target = current.get('targetAudience') or {}
    body['targetAudience'] = {
        'description': previous_target.get('description') if isinstance(previous_target.get('description'), str) else '',
        'primaryGroup': previous_target.get('primaryGroup') if isinstance(previous_target.get('primaryGroup'), str) else '',
        'needs': list(previous_target.get('needs') or []),
        'problems': list(previous_target.get('problems') or []),
    }
    if not isinstance(incoming, dict):
        raise ValueError('اطلاعات ارسال‌شده معتبر نیست.')
    audience = incoming.get('targetAudience')
    if audience is not None:
        if not isinstance(audience, dict):
            raise ValueError('اطلاعات مخاطب معتبر نیست.')
        incoming = dict(incoming)
        for key in ('description', 'primaryGroup', 'needs', 'problems'):
            if key in audience:
                incoming['targetDescription' if key == 'description' else key] = audience[key]
    for key in TEXTS:
        if key in incoming:
            if not isinstance(incoming[key], str):
                raise ValueError('مقدار این بخش باید متن باشد.')
            value = _text(incoming[key])
            if key == 'targetDescription':
                body['targetAudience']['description'] = value
            elif key == 'primaryGroup':
                body['targetAudience']['primaryGroup'] = value
            else:
                body[key] = value
    for key in LISTS:
        if key in incoming:
            value = _items(incoming[key])
            if key in ('needs', 'problems'):
                body['targetAudience'][key] = value
            else:
                body[key] = value
    body['testInsight'] = insight
    return body


def missing(body):
    result = []
    for key in REQUIRED:
        value = body['targetAudience']['description'] if key == 'targetDescription' else (
            body['targetAudience']['problems'] if key == 'problems' else body[key])
        if not (len(value) if isinstance(value, list) else value):
            result.append(key)
    return result


def completion(body):
    values = [body['professionalRole'], body['industry'], body['experience'], body['skills'],
              body['services'], body['targetAudience']['description'], body['targetAudience']['primaryGroup'],
              body['targetAudience']['needs'], body['targetAudience']['problems'], body['valueProposition'],
              body['differentiators'], body['professionalGoals'], body['desiredPerception'],
              body['personalValues'], body['preferredTopics'], body['excludedTopics']]
    return round(sum(1 for value in values if (len(value) if isinstance(value, list) else value)) * 100 / len(values))


def completed_sections(body):
    done = []
    for name, fields in SECTIONS.items():
        values = []
        for key in fields:
            values.append(body['targetAudience']['description'] if key == 'targetDescription' else (
                body['targetAudience']['problems'] if key == 'problems' else body[key]))
        if all(len(value) if isinstance(value, list) else value for value in values):
            done.append(name)
    return done


def changed_fields(current, body):
    keys = set(body) - {'status', 'completionPercentage', 'draftSections', 'approvedSections',
                        'updatedAt', 'approvedAt', 'createdAt', 'id'}
    keys |= {'targetAudience'}
    return {key for key in keys if current.get(key) != body.get(key)}


def status_for(body, current_status, changed):
    if current_status in ('approved', 'needs_revision'):
        return 'needs_revision' if changed else current_status
    if missing(body):
        return 'in_progress' if completed_sections(body) or completion(body) else 'not_started'
    return 'ready_for_review'


def stale_sections(body):
    """Parts that are already approved, so a reported edit to them must un-approve them."""
    approved = body.get('approvedSections') or []
    return [name for name in PART_FIELDS if name in approved]


def validate_sections(value):
    if value is None:
        return None
    if not isinstance(value, list) or not value:
        raise ValueError('بخش‌های ویرایش‌شده معتبر نیستند.')
    if any(not isinstance(name, str) or name not in PART_FIELDS for name in value):
        raise ValueError('بخش ویرایش‌شده شناخته نشد.')
    return list(dict.fromkeys(value))


def insight_for(db, owner):
    row = db.execute(
        "SELECT r.body FROM pb_report_versions r JOIN pb_reports p ON p.id=r.report_id"
        " JOIN pb_assessments a ON a.id=p.assessment_id"
        " WHERE a.owner_hash=? AND a.state='completed' AND a.archived_at IS NULL"
        " ORDER BY r.created_at DESC LIMIT 1", (owner,)).fetchone()
    if not row:
        return {'exists': False, 'summary': '', 'isApprovedForBrandUse': False, 'source': ''}
    try:
        report = json.loads(row[0])
    except ValueError:
        return {'exists': False, 'summary': '', 'isApprovedForBrandUse': False, 'source': ''}
    summary = report.get('summary') if isinstance(report.get('summary'), str) else ''
    return {'exists': bool(summary), 'summary': summary[:1000], 'isApprovedForBrandUse': False,
            'source': 'assessment'}


def load(db, owner):
    row = db.execute('SELECT * FROM pb_identity_records WHERE owner_hash=?', (owner,)).fetchone()
    insight = insight_for(db, owner)
    if not row:
        body = empty_body()
        body['status'] = 'not_started'
        return body
    body = json.loads(row['body'])
    stored = body.get('testInsight') or {}
    body['testInsight'] = {**insight, 'isApprovedForBrandUse': stored.get('isApprovedForBrandUse') is True,
                           'isResolved': stored.get('isResolved') is True,
                           'source': stored.get('source') or insight['source']}
    return body


def version_count(db, owner):
    return db.execute('SELECT coalesce(max(version),0) FROM pb_identity_versions WHERE owner_hash=?',
                      (owner,)).fetchone()[0]


def save(db, owner, incoming, insight_approval, edited_sections=None):
    current = load(db, owner)
    insight = insight_for(db, owner)
    ins = current.get('testInsight') or {}
    # isResolved records that the person decided either way, so "ignored" is never mistaken for "never asked".
    insight['isApprovedForBrandUse'] = ins.get('isApprovedForBrandUse') is True
    insight['isResolved'] = ins.get('isResolved') is True
    if insight['isApprovedForBrandUse']:
        insight['source'] = 'user_approved'
    if insight_approval is True:
        if not insight['exists']:
            raise ValueError('بینشی از تست برای تأیید پیدا نشد.')
        insight['isApprovedForBrandUse'] = True
        insight['isResolved'] = True
        insight['source'] = 'user_approved'
    elif insight_approval is False:
        insight['isApprovedForBrandUse'] = False
        insight['isResolved'] = True
        insight['source'] = 'assessment'
    body = normalize(incoming, current, insight)
    previous_status = current.get('status')
    now = pb.now()
    body['createdAt'] = current.get('createdAt') or now
    body['updatedAt'] = now
    body['completionPercentage'] = completion(body)
    body['draftSections'] = completed_sections(body)
    body['approvedAt'] = current.get('approvedAt')
    approved = [entry for entry in (current.get('approvedSections') or []) if entry in PART_FIELDS]
    # Only the parts the client says it edited lose approval; a stale list cannot silently revert the whole identity.
    stale = [name for name in (edited_sections or []) if name in stale_sections(current)]
    approved = [entry for entry in approved if entry not in stale]
    body['approvedSections'] = approved
    if previous_status in ('approved', 'needs_revision'):
        body['status'] = 'needs_revision' if stale or missing(body) or not approved else previous_status
    else:
        body['status'] = status_for(body, previous_status, changed_fields(current, body) - {'testInsight'})
    row = db.execute('SELECT * FROM pb_identity_records WHERE owner_hash=?', (owner,)).fetchone()
    if row:
        db.execute('UPDATE pb_identity_records SET body=?,status=?,completion=?,updated_at=? WHERE owner_hash=?',
                   (pb.dumps(body), body['status'], body['completionPercentage'], now, owner))
    else:
        db.execute('INSERT INTO pb_identity_records VALUES(?,?,?,?,?,?,?)',
                   (owner, pb.dumps(body), body['status'], body['completionPercentage'], now, now, None))
    db.execute('INSERT INTO pb_identity_versions VALUES(?,?,?,?,?,?)',
               (pb.uid(), owner, version_count(db, owner) + 1, 'draft', pb.dumps(body), now))
    pb.audit(db, owner, 'identity_draft', '')
    db.commit()
    return body


def approve(db, owner, approved_at=None):
    current = load(db, owner)
    if not current.get('createdAt'):
        raise ValueError('هنوز اطلاعاتی برای تأیید ثبت نشده است.')
    if missing(current):
        raise ValueError('برای تأیید، اطلاعات ضروری را کامل کن.')
    pending = current.get('testInsight') or {}
    if pending.get('exists') and not pending.get('isResolved'):
        raise ValueError('بینش تست هنوز تعیین تکلیف نشده است؛ آن را تأیید کن یا نادیده بگیر و بعد هویت را تأیید کن.')
    accepted = approved_at if isinstance(approved_at, int) and abs(pb.now() - approved_at) <= 120 else None
    insight = current.get('testInsight') or {}
    body = dict(current)
    body['status'] = 'approved'
    body['approvedAt'] = accepted or pb.now()
    body['updatedAt'] = pb.now()
    body['approvedSections'] = completed_sections(body)
    body['testInsight'] = {**insight, 'isApprovedForBrandUse': insight.get('isApprovedForBrandUse') is True,
                           'isResolved': insight.get('isResolved') is True,
                           'source': insight.get('source') or 'assessment'}
    db.execute('UPDATE pb_identity_records SET body=?,status=?,completion=?,updated_at=?,approved_at=? WHERE owner_hash=?',
               (pb.dumps(body), 'approved', body['completionPercentage'], body['updatedAt'], body['approvedAt'], owner))
    db.execute('INSERT INTO pb_identity_versions VALUES(?,?,?,?,?,?)',
               (pb.uid(), owner, version_count(db, owner) + 1, 'approved', pb.dumps(body), body['updatedAt']))
    pb.audit(db, owner, 'identity_approved', '')
    db.commit()
    return body


def access(db, owner):
    row = db.execute('SELECT * FROM pb_identity_access WHERE owner_hash=?', (owner,)).fetchone()
    if not row:
        return {'status': 'none', 'planId': '', 'planName': '', 'simulation': True}
    plan = PLANS.get(row['plan_id'])
    if not plan:
        return {'status': row['status'], 'planId': '', 'planName': '', 'simulation': bool(row['simulation'])}
    return {'status': row['status'], 'planId': row['plan_id'], 'planName': plan['name'],
            'simulation': bool(row['simulation'])}


def grant_trial(db, owner, plan_id):
    if plan_id not in PLANS:
        raise ValueError('پلن انتخاب‌شده معتبر نیست.')
    now = pb.now()
    db.execute('INSERT INTO pb_identity_access VALUES(?,?,?,?,?) ON CONFLICT(owner_hash) DO UPDATE SET'
               ' plan_id=excluded.plan_id,status=excluded.status,simulation=excluded.simulation,updated_at=excluded.updated_at',
               (owner, plan_id, 'trial', 1, now))
    pb.audit(db, owner, 'brandyar_trial_access', plan_id)
    db.commit()
    return access(db, owner)


def revoke(db, owner):
    now = pb.now()
    db.execute("UPDATE pb_identity_access SET status='expired',updated_at=? WHERE owner_hash=?", (now, owner))
    pb.audit(db, owner, 'brandyar_access_revoked', '')
    db.commit()
    return access(db, owner)


def trial_used(db, owner):
    return db.execute("SELECT 1 FROM pb_identity_access WHERE owner_hash=?", (owner,)).fetchone() is not None


def test_completed(db, owner):
    return insight_for(db, owner)['exists']


def snapshot(db, owner):
    """Everything the panel and the site profile need, from the same source as the panel gate."""
    return {'identity': load(db, owner), 'access': access(db, owner),
            'testCompleted': test_completed(db, owner), 'trialUsed': trial_used(db, owner)}




def ai_save_output(db, owner, operation, inputs, output):
    if not isinstance(operation, str) or not operation:
        raise ValueError('عملیات هوش مصنوعی معتبر نیست.')
    now = pb.now()
    output_id = pb.uid()
    db.execute('INSERT INTO pb_ai_outputs VALUES(?,?,?,?,?,?,?,?)',
               (output_id, owner, operation, 'proposed', pb.dumps(inputs or {}), pb.dumps(output), now, now))
    db.commit()
    return {'id': output_id, 'operation': operation, 'status': 'proposed', 'inputs': inputs or {}, 'output': output, 'createdAt': now}


def _ai_output(db, owner, output_id):
    row = db.execute('SELECT * FROM pb_ai_outputs WHERE id=? AND owner_hash=?', (output_id, owner)).fetchone()
    if not row:
        raise ValueError('خروجی پیدا نشد یا متعلق به این نشست نیست.')
    return row


def _store_approved(db, table, owner, body):
    now = pb.now()
    db.execute(f'INSERT INTO {table} VALUES(?,?,?,?) ON CONFLICT(owner_hash) DO UPDATE SET status=excluded.status,body=excluded.body,updated_at=excluded.updated_at',
               (owner, 'approved', pb.dumps(body), now))


def ai_action(db, owner, output_id, action, edited=None):
    if action not in {'accept', 'reject', 'edit', 'save'}:
        raise ValueError('اقدام خروجی معتبر نیست.')
    row = _ai_output(db, owner, output_id)
    output = json.loads(row['output_json'])
    if action == 'edit':
        if not isinstance(edited, dict):
            raise ValueError('ویرایش خروجی معتبر نیست.')
        output.update(edited)
        status = 'editing'
    elif action == 'reject':
        status = 'rejected'
    else:
        status = 'accepted'
        if row['operation'] == 'brand_voice':
            _store_approved(db, 'pb_brand_voice', owner, output)
        elif row['operation'] == 'content_pillars':
            _store_approved(db, 'pb_content_pillars', owner, output)
        elif row['operation'] == 'content_draft':
            now = pb.now()
            title = str(output.get('title') or 'پیش‌نویس بدون عنوان')[:200]
            body = str(output.get('body') or '')[:12000]
            metadata = {'goal': output.get('goal', ''), 'format': output.get('format', ''), 'pillar': output.get('pillar', '')}
            db.execute('INSERT INTO pb_content_items VALUES(?,?,?,?,?,?,?,?,?,?)',
                       (pb.uid(), owner, title, body, pb.dumps(metadata), 'ai', 'draft', 0, now, now))
    now = pb.now()
    db.execute('UPDATE pb_ai_outputs SET status=?,output_json=?,updated_at=? WHERE id=? AND owner_hash=?',
               (status, pb.dumps(output), now, output_id, owner))
    db.commit()
    return {'id': output_id, 'operation': row['operation'], 'status': status,
            'inputs': json.loads(row['input_json'] or '{}'), 'output': output}


def ai_feedback(db, owner, output_id, rating, note=''):
    if rating not in {'useful', 'needs_revision', 'not_aligned'}:
        raise ValueError('بازخورد خروجی معتبر نیست.')
    _ai_output(db, owner, output_id)
    db.execute('INSERT INTO pb_ai_feedback VALUES(?,?,?,?,?,?)',
               (pb.uid(), owner, output_id, rating, str(note or '')[:500], pb.now()))
    db.commit()


def ai_library(db, owner):
    rows = db.execute('SELECT * FROM pb_content_items WHERE owner_hash=? AND archived=0 ORDER BY updated_at DESC LIMIT 50', (owner,)).fetchall()
    return [{'id': row['id'], 'title': row['title'], 'body': row['body'], 'metadata': json.loads(row['metadata']),
             'source': row['source'], 'status': row['status'], 'createdAt': row['created_at'], 'updatedAt': row['updated_at']} for row in rows]


def ai_library_action(db, owner, item_id, action, title=None, body=None):
    if action not in {'archive', 'delete', 'edit', 'copy'}:
        raise ValueError('اقدام کتابخانه معتبر نیست.')
    row = db.execute('SELECT * FROM pb_content_items WHERE id=? AND owner_hash=? AND archived=0', (item_id, owner)).fetchone()
    if not row:
        raise ValueError('محتوا پیدا نشد یا متعلق به این نشست نیست.')
    if action == 'archive':
        db.execute('UPDATE pb_content_items SET archived=1,updated_at=? WHERE id=? AND owner_hash=?', (pb.now(), item_id, owner))
    elif action == 'delete':
        db.execute('DELETE FROM pb_content_items WHERE id=? AND owner_hash=?', (item_id, owner))
    elif action == 'edit':
        if not isinstance(title, str) or not isinstance(body, str):
            raise ValueError('ویرایش محتوا معتبر نیست.')
        db.execute('UPDATE pb_content_items SET title=?,body=?,status=?,updated_at=? WHERE id=? AND owner_hash=?',
                   (title.strip()[:200], body.strip()[:12000], 'draft', pb.now(), item_id, owner))
    db.commit()
    return ai_library(db, owner)


def workspace_snapshot(db, owner):
    voice = db.execute('SELECT status,body,updated_at FROM pb_brand_voice WHERE owner_hash=?', (owner,)).fetchone()
    pillars = db.execute('SELECT status,body,updated_at FROM pb_content_pillars WHERE owner_hash=?', (owner,)).fetchone()
    return {
        'brandVoice': {'status': voice['status'], 'body': json.loads(voice['body']), 'updatedAt': voice['updated_at']} if voice else None,
        'contentPillars': {'status': pillars['status'], 'body': json.loads(pillars['body']), 'updatedAt': pillars['updated_at']} if pillars else None,
        'library': ai_library(db, owner),
    }
