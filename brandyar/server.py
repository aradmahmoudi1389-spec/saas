import argparse
import base64
import datetime
import getpass
import hashlib
import hmac
import json
import logging
import os
import re
import secrets
import sqlite3
import struct
import time
import ssl
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from ipaddress import ip_address
from pathlib import Path
from urllib.parse import urlsplit
from zoneinfo import ZoneInfo

import brand_analysis
import supabase_store
import admin_workspace

ASSESSMENT_COOKIE_KEY = secrets.token_bytes(32)
ASSESSMENT_LEAD_ROLES = {'owner', 'support'}
CONSULTATION_TIMEZONE = os.environ.get('BRANDYAR_TIMEZONE', 'Asia/Tehran')
CONSULTATION_ADMIN_ROLES = {'owner', 'support'}

ROOT = Path(__file__).resolve().parent
DB = Path(os.environ.get('BRANDYAR_DB', str(ROOT / '.data' / 'brandyar.sqlite3')))
ROLES = {'owner', 'product', 'support', 'finance', 'viewer'} | set(admin_workspace.PERMISSIONS)
SECTIONS = {
    'owner': ('summary', 'users', 'tickets', 'plans', 'invoices', 'discounts', 'changes', 'features', 'funnel', 'churn', 'ai', 'integrations', 'sessions', 'audit'),
    'product': ('summary', 'users', 'changes', 'features', 'funnel', 'churn', 'ai', 'integrations'),
    'support': ('summary', 'users', 'tickets', 'funnel', 'churn', 'integrations'),
    'finance': ('summary', 'users', 'plans', 'invoices', 'discounts'),
    'viewer': ('summary', 'users', 'plans', 'invoices', 'discounts', 'changes', 'features', 'tickets', 'funnel', 'churn', 'ai', 'integrations', 'audit'),
}


def connect():
    DB.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(DB, timeout=10)
    os.chmod(DB, 0o600)
    db.row_factory = sqlite3.Row
    db.execute('PRAGMA foreign_keys=ON')
    db.executescript('''
        CREATE TABLE IF NOT EXISTS staff (id INTEGER PRIMARY KEY, email TEXT NOT NULL UNIQUE, name TEXT NOT NULL, role TEXT NOT NULL, salt BLOB NOT NULL, password_hash BLOB NOT NULL, totp_secret TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS sessions (token_hash TEXT PRIMARY KEY, staff_id INTEGER NOT NULL REFERENCES staff(id), csrf TEXT NOT NULL, verified INTEGER NOT NULL, created INTEGER NOT NULL, last_seen INTEGER NOT NULL, expires INTEGER NOT NULL);
        CREATE TABLE IF NOT EXISTS attempts (source TEXT NOT NULL, account TEXT NOT NULL, at INTEGER NOT NULL);
        CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT NOT NULL, email TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'فعال', plan TEXT NOT NULL DEFAULT 'رایگان', created INTEGER NOT NULL);
        CREATE TABLE IF NOT EXISTS tickets (id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL REFERENCES users(id), subject TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'باز', created INTEGER NOT NULL);
        CREATE TABLE IF NOT EXISTS audit (id INTEGER PRIMARY KEY, staff_id INTEGER REFERENCES staff(id), action TEXT NOT NULL, result TEXT NOT NULL, at INTEGER NOT NULL);
        CREATE TABLE IF NOT EXISTS consultation_slots (id INTEGER PRIMARY KEY, starts_at INTEGER NOT NULL, duration_minutes INTEGER NOT NULL, status TEXT NOT NULL, capacity INTEGER NOT NULL DEFAULT 1, created_at INTEGER NOT NULL);
        CREATE TABLE IF NOT EXISTS consultation_requests (id INTEGER PRIMARY KEY, session_hash TEXT NOT NULL, name TEXT NOT NULL, phone TEXT NOT NULL, slot_id INTEGER REFERENCES consultation_slots(id), notes TEXT NOT NULL, status TEXT NOT NULL, created_at INTEGER NOT NULL, updated_at INTEGER NOT NULL);
        CREATE UNIQUE INDEX IF NOT EXISTS consultation_active_session ON consultation_requests(session_hash) WHERE status IN ('pending','confirmed');
        CREATE UNIQUE INDEX IF NOT EXISTS consultation_active_phone ON consultation_requests(phone) WHERE status IN ('pending','confirmed');
        CREATE UNIQUE INDEX IF NOT EXISTS consultation_active_slot ON consultation_requests(slot_id) WHERE status IN ('pending','confirmed');
        CREATE TABLE IF NOT EXISTS assessment_leads (session_hash TEXT PRIMARY KEY, phone TEXT NOT NULL, consent_version TEXT NOT NULL, created_at INTEGER NOT NULL);
        CREATE TABLE IF NOT EXISTS assessment_sessions (token_hash TEXT PRIMARY KEY, expires INTEGER NOT NULL);
        CREATE INDEX IF NOT EXISTS assessment_sessions_expiry ON assessment_sessions(expires);
        CREATE TABLE IF NOT EXISTS consultation_attempts (session_hash TEXT NOT NULL, at INTEGER NOT NULL);
        CREATE INDEX IF NOT EXISTS consultation_attempts_lookup ON consultation_attempts(session_hash,at);
        CREATE INDEX IF NOT EXISTS consultation_slots_lookup ON consultation_slots(status,starts_at);
        CREATE INDEX IF NOT EXISTS attempts_lookup ON attempts(source,account,at);
        CREATE INDEX IF NOT EXISTS consultation_requests_lookup ON consultation_requests(status,created_at);
    ''')
    if any(row['name'] == 'slot_id' and row['notnull'] for row in db.execute('PRAGMA table_info(consultation_requests)')):
        with db:
            db.execute('BEGIN IMMEDIATE')
            if any(row['name'] == 'slot_id' and row['notnull'] for row in db.execute('PRAGMA table_info(consultation_requests)')):
                db.execute('CREATE TABLE consultation_requests_nullable (id INTEGER PRIMARY KEY, session_hash TEXT NOT NULL, name TEXT NOT NULL, phone TEXT NOT NULL, slot_id INTEGER REFERENCES consultation_slots(id), notes TEXT NOT NULL, status TEXT NOT NULL, created_at INTEGER NOT NULL, updated_at INTEGER NOT NULL)')
                db.execute('INSERT INTO consultation_requests_nullable SELECT * FROM consultation_requests')
                db.execute('DROP TABLE consultation_requests')
                db.execute('ALTER TABLE consultation_requests_nullable RENAME TO consultation_requests')
                db.execute("CREATE UNIQUE INDEX consultation_active_session ON consultation_requests(session_hash) WHERE status IN ('pending','confirmed')")
                db.execute("CREATE UNIQUE INDEX consultation_active_phone ON consultation_requests(phone) WHERE status IN ('pending','confirmed')")
                db.execute("CREATE UNIQUE INDEX consultation_active_slot ON consultation_requests(slot_id) WHERE status IN ('pending','confirmed')")
                db.execute('CREATE INDEX consultation_requests_lookup ON consultation_requests(status,created_at)')
    admin_workspace.initialize(db)
    return db


def password_hash(password, salt):
    return hashlib.scrypt(password.encode(), salt=salt, n=2**14, r=8, p=1, dklen=32, maxmem=32 * 1024 * 1024)


def valid_totp(secret, code, now):
    try:
        key = base64.b32decode(secret.upper().replace(' ', ''), casefold=True)
        if not (len(code) == 6 and code.isascii() and code.isdigit() and len(key) >= 20):
            return False
    except (ValueError, base64.binascii.Error):
        return False
    for tick in (now // 30 - 1, now // 30, now // 30 + 1):
        digest = hmac.new(key, struct.pack('>Q', tick), hashlib.sha1).digest()
        offset = digest[-1] & 15
        value = (struct.unpack('>I', digest[offset:offset + 4])[0] & 0x7fffffff) % 1000000
        if hmac.compare_digest(f'{value:06d}', code):
            return True
    return False


def add_staff(email, name, role):
    if role not in ROLES or not email.strip() or not name.strip():
        raise ValueError('Invalid staff details')
    password = getpass.getpass('Password: ')
    confirmation = getpass.getpass('Confirm password: ')
    otp_secret = getpass.getpass('Existing authenticator Base32 secret: ').replace(' ', '').upper()
    if len(password) < 12 or password != confirmation or not _valid_secret(otp_secret):
        raise ValueError('Password confirmation or authenticator secret is invalid')
    salt = secrets.token_bytes(32)
    with connect() as db:
        db.execute('INSERT INTO staff(email,name,role,salt,password_hash,totp_secret) VALUES(?,?,?,?,?,?)',
                   (email.strip().lower(), name.strip(), role, salt, password_hash(password, salt), otp_secret))
    print('Staff account created.')


def _valid_secret(value):
    try:
        return len(base64.b32decode(value, casefold=True)) >= 20
    except (ValueError, base64.binascii.Error):
        return False


class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def respond(self, status, body=b'', content_type='application/json', headers=None):
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Referrer-Policy', 'no-referrer')
        policy = "default-src 'none'; style-src 'self'; font-src 'self'; script-src 'self'; connect-src 'self'; base-uri 'none'; frame-ancestors 'none'; form-action 'self'"
        if self.path in ('/', '/index.html'):
            policy = "default-src 'none'; style-src 'self' 'unsafe-inline'; font-src 'self'; script-src 'unsafe-inline'; connect-src 'self'; img-src 'self' data:; base-uri 'none'; frame-ancestors 'none'; form-action 'self'"
        self.send_header('Content-Security-Policy', policy)
        for key, value in (headers or {}).items():
            self.send_header(key, value)
        self.end_headers()
        self.wfile.write(body)

    def json(self, status, payload, headers=None):
        self.respond(status, json.dumps(payload, ensure_ascii=False).encode(), headers=headers)

    def request_data(self, maximum=4096, parser=None):
        length = int(self.headers.get('Content-Length', '0'))
        if length < 1 or length > maximum or self.headers.get('Content-Type', '').split(';')[0] != 'application/json':
            raise ValueError('Invalid request')
        data = (parser or json.loads)(self.rfile.read(length))
        if not isinstance(data, dict):
            raise ValueError('Invalid request')
        return data

    def session(self, db, require_mfa=True):
        cookie = next((part.strip()[len('brandysid='):] for part in self.headers.get('Cookie', '').split(';') if part.strip().startswith('brandysid=')), '')
        if not cookie or len(cookie) != 64:
            return None
        record = db.execute('SELECT sessions.*, staff.role,staff.name FROM sessions JOIN staff ON staff.id=sessions.staff_id WHERE token_hash=?', (hashlib.sha256(cookie.encode()).hexdigest(),)).fetchone()
        now = int(time.time())
        if not record or now > record['expires'] or now - record['last_seen'] > 1800 or (require_mfa and not record['verified']):
            return None
        db.execute('UPDATE sessions SET last_seen=? WHERE token_hash=?', (now, record['token_hash']))
        db.commit()
        return record

    def cookie(self, token, max_age=28800):
        return f'brandysid={token}; HttpOnly; Secure; SameSite=Strict; Path=/; Max-Age={max_age}'

    def safe_origin(self):
        expected = ('https://' if self.headers.get('X-Forwarded-Proto') == 'https' else 'http://') + self.headers.get('Host', '')
        origin = self.headers.get('Origin', '')
        if origin:
            return origin == expected
        referer = self.headers.get('Referer', '')
        parsed = urlsplit(referer)
        if parsed.scheme + '://' + parsed.netloc == expected and parsed.path.startswith('/'):
            return True
        return self.headers.get('Sec-Fetch-Site', '') == 'same-origin'

    def throttle(self, db, source, account):
        now = int(time.time())
        db.execute('DELETE FROM attempts WHERE at<?', (now - 900,))
        blocked = db.execute('SELECT count(*) FROM attempts WHERE at>? AND (source=? OR account=?)', (now - 900, source, account)).fetchone()[0] >= 8
        db.execute('INSERT INTO attempts(source,account,at) VALUES(?,?,?)', (source, account, now))
        db.commit()
        return blocked

    def assessment_https(self):
        return isinstance(self.connection, ssl.SSLSocket) or (self.client_address[0] in ('127.0.0.1', '::1') and self.headers.get('X-Forwarded-Proto') == 'https')

    def supabase(self):
        store = supabase_store.SupabaseStore()
        return store if store.enabled else None

    def supabase_grace(self, session_hash):
        # Right after analysis the Supabase copy may be briefly unavailable; the signed report cookie still backs readiness.
        grace = self.headers.get('X-Nesharo-Supabase-Grace', '')
        if not (self.assessment_https() and grace.isascii() and grace.isdigit() and 0 < len(grace) <= 3 and int(grace) <= 180):
            return False
        try:
            with connect() as db:
                return db.execute("SELECT 1 FROM assessment_jobs WHERE session_hash=? AND state='ready' AND created>?", (session_hash, int(time.time()) - int(grace))).fetchone() is not None
        except sqlite3.Error:
            return False

    def source_tag(self, value):
        return value if isinstance(value, str) and 0 < len(value) <= 96 and re.fullmatch(r'[A-Za-z0-9_\-./#?=&%:]+\Z', value) else None

    def assessment_record(self):
        if not self.assessment_https() or not self.safe_origin():
            return self.json(403, {'error': 'این درخواست به اتصال امن و معتبر نیاز دارد.'})
        if not self.assessment_session():
            return self.json(401, {'error': 'نشست ارزیابی معتبر نیست. دوباره تلاش کن.'})
        try:
            data = self.request_data(16384, brand_analysis.parse_json)
            report = brand_analysis.validate_report(brand_analysis.parse_json(json.dumps(data.get('insight'), ensure_ascii=False)))
            answers = brand_analysis.validate_answers({'answers': data.get('answers'), 'consent': True})
        except (ValueError, TypeError, UnicodeError, RecursionError):
            return self.json(422, {'error': 'پاسخ‌ها یا بینش ارزیابی معتبر نیستند.'})
        store = self.supabase()
        if not store:
            return self.json(503, {'error': 'ذخیره‌سازی سرور هنوز فعال نشده است. لطفاً بعداً دوباره تلاش کن.'})
        try:
            assessment_id = store.save_assessment(self.assessment_session(), answers, report)
            try:
                with connect() as db:
                    admin_workspace.event(db, assessment_id, 'assessment_stored')
            except sqlite3.Error:
                logging.getLogger(__name__).warning('event_tracking_failure event=assessment_stored')
            return self.json(200, {'assessment_id': assessment_id})
        except supabase_store.SupabaseUnavailable:
            logging.getLogger(__name__).warning('database_failure table=assessments')
            return self.json(503, {'error': 'ذخیرهٔ ارزیابی انجام نشد. لطفاً دوباره تلاش کن.'})

    def lead_record(self):
        if not self.assessment_https() or not self.safe_origin():
            return self.json(403, {'error': 'این درخواست به اتصال امن و معتبر نیاز دارد.'})
        if not self.assessment_session():
            return self.json(401, {'error': 'نشست ارزیابی معتبر نیست. دوباره تلاش کن.'})
        try:
            data = self.request_data(1024, brand_analysis.parse_json)
            if set(data) != {'assessment_id', 'mobile', 'consent_follow_up', 'source_page', 'source_campaign'} or data['consent_follow_up'] is not True:
                raise ValueError()
            store = self.supabase()
            if not store or data['assessment_id'] != store.session_id(self.assessment_session()):
                raise ValueError()
            mobile = self.consultation_phone(data['mobile'])
            source_page, source_campaign = self.source_tag(data['source_page']), self.source_tag(data['source_campaign'])
        except (ValueError, TypeError, UnicodeError, RecursionError):
            return self.json(422, {'error': 'اطلاعات فرم کامل یا معتبر نیست.'})
        try:
            lead_id = store.save_lead(data['assessment_id'], mobile, True, source_page, source_campaign)
            return self.json(200, {'lead_id': lead_id, 'report_unlocked': True})
        except supabase_store.SupabaseUnavailable:
            logging.getLogger(__name__).warning('database_failure table=leads')
            return self.json(503, {'error': 'ثبت لید انجام نشد. لطفاً دوباره تلاش کن.'})

    def assessment_source(self):
        peer = self.client_address[0]
        if peer in ('127.0.0.1', '::1'):
            try:
                return str(ip_address(self.headers.get('X-Forwarded-For', '')))
            except ValueError:
                pass
        return peer

    def assessment_session(self):
        cookie = next((v.strip().split('=', 1)[1] for v in self.headers.get('Cookie', '').split(';') if v.strip().startswith('brandyassessment=')), '')
        value = self.headers.get('X-Nesharo-Assessment-Session', '') or cookie
        if len(value) > 150:
            return None
        if re.fullmatch(r'[0-9a-f]{64}', value):
            try:
                with connect() as db:
                    now = int(time.time())
                    valid = db.execute('SELECT 1 FROM assessment_sessions WHERE token_hash=? AND expires>?', (hashlib.sha256(value.encode()).hexdigest(), now)).fetchone() is not None
                return value if valid else None
            except sqlite3.Error:
                return None
        parts = value.split('.')
        if len(parts) != 3 or not parts[0].isascii() or not parts[0].isdigit() or len(parts[0]) > 10 or len(parts[1]) != 64 or len(parts[2]) != 64:
            return None
        if not 0 <= int(time.time()) - int(parts[0]) < 3600:
            return None
        signature = hmac.new(ASSESSMENT_COOKIE_KEY, '.'.join(parts[:2]).encode(), hashlib.sha256).hexdigest()
        return value if hmac.compare_digest(signature, parts[2]) else None

    def consultation_session_hash(self):
        value = self.assessment_session()
        return hashlib.sha256(value.encode()).hexdigest() if value else None

    def supabase_assessment(self):
        cookie = self.assessment_session()
        store = self.supabase()
        if not cookie or not store:
            return None
        return {'cookie': cookie, 'store': store, 'id': store.session_id(cookie)}

    def supabase_report_ready(self, record):
        try:
            rows = record['store'].request('assessments', 'GET', 'id=eq.' + supabase_store.filter_value(record['id']) + '&select=id,lead_id,current_step,full_report', prefer='return=minimal')
        except supabase_store.SupabaseUnavailable:
            return bool(self.supabase_grace(hashlib.sha256(record['cookie'].encode()).hexdigest())), None, False
        if not rows or not isinstance(rows[0].get('full_report'), dict):
            return False, None, False
        try:
            report = supabase_store.unpack_report(rows[0]['full_report'])
            brand_analysis.validate_report(report)
        except (ValueError, TypeError, KeyError):
            return False, None, False
        lead_id = rows[0].get('lead_id')
        return True, (lead_id if isinstance(lead_id, str) and len(lead_id) <= 64 else None), lead_id is not None

    def consultation_slot(self, row):
        return {'id': row['id'], 'startsAt': row['starts_at'], 'durationMinutes': row['duration_minutes'], 'timeZone': CONSULTATION_TIMEZONE}

    def consultation_slots(self, db):
        now = int(time.time())
        rows = db.execute("SELECT id,starts_at,duration_minutes FROM consultation_slots WHERE status='open' AND starts_at>? ORDER BY starts_at LIMIT 100", (now,)).fetchall()
        return [self.consultation_slot(row) for row in rows]

    def consultation_status(self, db, session_hash):
        row = db.execute("SELECT consultation_requests.status,consultation_requests.created_at,consultation_slots.starts_at,consultation_slots.duration_minutes FROM consultation_requests LEFT JOIN consultation_slots ON consultation_slots.id=consultation_requests.slot_id WHERE session_hash=? AND consultation_requests.status IN ('pending','confirmed','cancelled','completed') ORDER BY consultation_requests.id DESC LIMIT 1", (session_hash,)).fetchone()
        if not row:
            return None
        labels = {'pending': 'در انتظار تأیید', 'confirmed': 'زمان تأیید شد', 'cancelled': 'لغو شد', 'completed': 'انجام شد'}
        label = 'در انتظار تماس برای هماهنگی زمان' if row['status'] == 'pending' and row['starts_at'] is None else labels[row['status']]
        return {'status': label, 'state': row['status'], 'startsAt': row['starts_at'], 'timeZone': CONSULTATION_TIMEZONE}

    def consultation_phone(self, value):
        if not isinstance(value, str) or len(value) > 32:
            raise ValueError('شمارهٔ موبایل را کامل وارد کن.')
        digits = value.strip().replace(' ', '').replace('-', '')
        translation = str.maketrans('۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩', '01234567890123456789')
        digits = digits.translate(translation)
        if digits.startswith('+98'): digits = '0' + digits[3:]
        elif digits.startswith('98'): digits = '0' + digits[2:]
        if not re.fullmatch(r'09[0-9]{9}', digits):
            raise ValueError('شمارهٔ موبایل را کامل وارد کن.')
        return digits

    def cached_assessment_report(self, session_hash):
        try:
            with connect() as db:
                rows = db.execute("SELECT report FROM assessment_jobs WHERE session_hash=? AND state='ready' AND created>? ORDER BY created DESC", (session_hash, int(time.time()) - 3600)).fetchall()
        except sqlite3.Error:
            return None
        for row in rows:
            try:
                return brand_analysis.validate_report(brand_analysis.parse_json(row['report']))
            except (ValueError, TypeError, KeyError):
                continue
        return None

    def consultation_ready(self, db, session_hash):
        if not session_hash or not db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='assessment_jobs'").fetchone():
            return False
        rows = db.execute("SELECT report FROM assessment_jobs WHERE session_hash=? AND state='ready' AND created>?", (session_hash, int(time.time()) - 3600)).fetchall()
        for row in rows:
            try:
                brand_analysis.validate_report(brand_analysis.parse_json(row['report']))
                return True
            except (ValueError, TypeError, KeyError):
                continue
        return False

    def assessment_lead(self, write=False):
        if not self.assessment_https() or (write and not self.safe_origin()):
            return self.json(403, {'error': 'این درخواست به اتصال امن و معتبر نیاز دارد.'})
        session_hash = self.consultation_session_hash()
        if not session_hash:
            return self.json(401, {'error': 'نشست ارزیابی منقضی شده است؛ ارزیابی را دوباره مرور کن.'})
        record = self.supabase_assessment()
        if record:
            try:
                ready, lead_id, registered = self.supabase_report_ready(record)
            except (ValueError, TypeError):
                ready, lead_id, registered = False, None, False
            if not ready:
                report = self.cached_assessment_report(session_hash) if write else None
                if not report:
                    return self.json(403, {'error': 'ابتدا ارزیابی را کامل کن تا گزارش آماده شود.'})
                try:
                    with connect() as db:
                        snapshot = db.execute('SELECT answers_json FROM admin_assessment_snapshots WHERE assessment_id=?', (record['id'],)).fetchone()
                    answers = json.loads(snapshot['answers_json']) if snapshot else {}
                    record['store'].save_assessment(record['cookie'], answers, report)
                    ready = True
                except supabase_store.SupabaseUnavailable:
                    logging.getLogger(__name__).warning('database_failure table=assessments')
                    return self.json(503, {'error': 'ذخیرهٔ ارزیابی انجام نشد. لطفاً دوباره تلاش کن.'})
            if write:
                try:
                    data = self.request_data(512, brand_analysis.parse_json)
                    if set(data) != {'phone', 'consent'} or data['consent'] is not True:
                        raise ValueError()
                    phone = self.consultation_phone(data['phone'])
                except (ValueError, TypeError, UnicodeError, RecursionError):
                    return self.json(422, {'error': 'شماره موبایل را به‌درستی وارد کن.'})
                try:
                    lead_id = record['store'].save_lead(record['id'], phone, True, 'assessment-report', None) if not lead_id else record['store'].link_lead(record['id'], lead_id)
                except supabase_store.SupabaseUnavailable:
                    logging.getLogger(__name__).warning('database_failure table=leads')
                    return self.json(503, {'error': 'ثبت لید انجام نشد. لطفاً دوباره تلاش کن.'})
                try:
                    with connect() as db:
                        admin_workspace.event(db, record['id'], 'lead_registered')
                except sqlite3.Error:
                    logging.getLogger(__name__).warning('event_tracking_failure event=lead_registered')
                return self.json(200, {'registered': True, 'lead_id': lead_id, 'report_unlocked': True})
            return self.json(200, {'registered': registered})
        try:
            with connect() as db:
                if not self.consultation_ready(db, session_hash):
                    return self.json(403, {'error': 'ابتدا ارزیابی را کامل کن تا گزارش آماده شود.'})
                if write:
                    try:
                        data = self.request_data(512, brand_analysis.parse_json)
                        if set(data) != {'phone', 'consent'} or data['consent'] is not True:
                            raise ValueError()
                        phone = self.consultation_phone(data['phone'])
                    except (ValueError, TypeError, UnicodeError, RecursionError):
                        return self.json(422, {'error': 'شماره موبایل را به‌درستی وارد کن.'})
                    external = self.supabase()
                    if external:
                        try:
                            external.save_lead(external.session_id(self.assessment_session()), phone, True, 'assessment-report', None)
                        except supabase_store.SupabaseUnavailable:
                            logging.getLogger(__name__).warning('database_failure table=leads')
                            return self.json(503, {'error': 'ثبت لید انجام نشد. لطفاً دوباره تلاش کن.'})
                    else:
                        db.execute('INSERT INTO assessment_leads(session_hash,phone,consent_version,created_at) VALUES(?,?,?,?) ON CONFLICT(session_hash) DO NOTHING', (session_hash, phone, 'report-access-v1', int(time.time())))
                        db.commit()
                external = self.supabase()
                if external:
                    try:
                        registered = external.assessment_has_lead(external.session_id(self.assessment_session()))
                    except supabase_store.SupabaseUnavailable:
                        logging.getLogger(__name__).warning('database_failure table=assessments')
                        return self.json(503, {'error': 'دریافت وضعیت ثبت انجام نشد. لطفاً دوباره تلاش کن.'})
                else:
                    registered = db.execute('SELECT 1 FROM assessment_leads WHERE session_hash=?', (session_hash,)).fetchone() is not None
            return self.json(200, {'registered': registered})
        except (sqlite3.Error, OSError):
            return self.json(503, {'error': 'دریافت تأیید ثبت ممکن نشد. لطفاً دوباره تلاش کن.'})

    def consultation_dispatch(self, write=False):
        try:
            return self.consultation_request() if write else self.consultation_public()
        except (sqlite3.Error, OSError):
            return self.json(503, {'error': 'ذخیره‌سازی موقتاً در دسترس نیست. درخواست ثبت نشد؛ لطفاً دوباره تلاش کن.' if write else 'دریافت اطلاعات موقتاً ممکن نیست. لطفاً دوباره تلاش کن.'})

    def consultation_public(self):
        if not self.assessment_https():
            return self.json(503, {'error': 'اتصال امن سایت در دسترس نیست.'})
        session_hash = self.consultation_session_hash()
        if not session_hash:
            return self.json(401, {'error': 'گزارش معتبر این نشست پیدا نشد.'})
        with connect() as db:
            if not self.consultation_ready(db, session_hash):
                return self.json(403, {'error': 'این بخش پس از آماده‌شدن گزارش در دسترس است.'})
            return self.json(200, {'slots': self.consultation_slots(db), 'request': self.consultation_status(db, session_hash), 'timeZoneLabel': 'تهران' if CONSULTATION_TIMEZONE == 'Asia/Tehran' else CONSULTATION_TIMEZONE})

    def consultation_request(self):
        if not self.assessment_https() or not self.safe_origin():
            return self.json(403, {'error': 'این درخواست مجاز نیست.'})
        session_hash = self.consultation_session_hash()
        if not session_hash:
            return self.json(401, {'error': 'گزارش معتبر این نشست پیدا نشد.'})
        with connect() as db:
            if not self.consultation_ready(db, session_hash):
                return self.json(403, {'error': 'این بخش پس از آماده‌شدن گزارش در دسترس است.'})
            db.execute('BEGIN IMMEDIATE')
            now = int(time.time())
            db.execute('DELETE FROM consultation_attempts WHERE at<?', (now - 900,))
            if db.execute('SELECT count(*) FROM consultation_attempts WHERE session_hash=? AND at>?', (session_hash, now - 900)).fetchone()[0] >= 5:
                db.rollback()
                return self.json(429, {'error': 'تعداد تلاش‌ها زیاد است. لطفاً کمی بعد دوباره تلاش کن.'})
            db.execute('INSERT INTO consultation_attempts VALUES(?,?)', (session_hash, now))
            db.commit()
        try:
            data = self.request_data(4096, brand_analysis.parse_json)
            if set(data) != {'name', 'phone', 'slotId', 'notes'} or not isinstance(data['name'], str) or not isinstance(data['notes'], str) or (data['slotId'] is not None and type(data['slotId']) is not int):
                raise ValueError('اطلاعات فرم کامل یا معتبر نیست.')
            name, notes = data['name'].strip(), data['notes'].strip()
            phone, slot_id = self.consultation_phone(data['phone']), data['slotId']
            if len(name) > 120:
                raise ValueError('نام باید حداکثر ۱۲۰ نویسه باشد.')
            if len(data['notes']) > 200:
                raise ValueError('توضیح باید حداکثر ۲۰۰ نویسه باشد.')
        except (ValueError, TypeError, UnicodeError, RecursionError) as error:
            message = str(error)
            allowed = {'شمارهٔ موبایل را کامل وارد کن.', 'نام باید حداکثر ۱۲۰ نویسه باشد.', 'توضیح باید حداکثر ۲۰۰ نویسه باشد.'}
            return self.json(422, {'error': message if message in allowed else 'اطلاعات فرم کامل یا معتبر نیست.'})
        with connect() as db:
            db.execute('BEGIN IMMEDIATE')
            try:
                if not self.consultation_ready(db, session_hash):
                    return self.json(403, {'error': 'این بخش پس از آماده‌شدن گزارش در دسترس است.'})
                active = db.execute("SELECT 1 FROM consultation_requests WHERE session_hash=? AND status IN ('pending','confirmed')", (session_hash,)).fetchone()
                if active:
                    return self.json(409, {'error': 'یک درخواست فعال برای این نشست وجود دارد.'})
                if slot_id is not None:
                    slot = db.execute("SELECT * FROM consultation_slots WHERE id=? AND status='open' AND starts_at>?", (slot_id, int(time.time()))).fetchone()
                    if not slot:
                        return self.json(409, {'error': 'این زمان دیگر در دسترس نیست. زمان دیگری را انتخاب کن.'})
                    occupied = db.execute("SELECT count(*) FROM consultation_requests WHERE slot_id=? AND status IN ('pending','confirmed')", (slot_id,)).fetchone()[0]
                    if occupied >= slot['capacity']:
                        return self.json(409, {'error': 'این زمان دیگر در دسترس نیست. زمان دیگری را انتخاب کن.'})
                now = int(time.time())
                db.execute("INSERT INTO consultation_requests(session_hash,name,phone,slot_id,notes,status,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?)", (session_hash, name, phone, slot_id, notes, 'pending', now, now))
                db.execute("UPDATE consultation_slots SET status='requested' WHERE id=? AND status='open'", (slot_id,))
                state = self.consultation_status(db, session_hash)
                db.commit()
            except sqlite3.IntegrityError:
                db.rollback()
                return self.json(409, {'error': 'درخواست مشابهی در حال بررسی است. اگر لازم است، بعداً دوباره تلاش کن.'})
            except Exception:
                db.rollback()
                raise
        message = 'شماره‌ات ثبت شد. برای هماهنگی زمان جلسهٔ مشاوره با تو تماس می‌گیریم.' if slot_id is None else 'درخواستت ثبت شد. بعد از تأیید زمان، برای هماهنگی با تو تماس می‌گیریم.'
        return self.json(201, {'message': message, 'request': state})

    def admin_consultation(self, db, staff):
        if staff['role'] not in CONSULTATION_ADMIN_ROLES or not self.assessment_https():
            return self.json(403, {'error': 'این بخش برای نقش شما مجاز نیست یا اتصال امن برقرار نیست.'})
        if self.path == '/api/admin/consultations':
            rows = db.execute("SELECT r.id,r.name,r.phone,r.notes,r.status,r.created_at,s.starts_at,s.duration_minutes FROM consultation_requests r LEFT JOIN consultation_slots s ON s.id=r.slot_id ORDER BY r.id DESC LIMIT 200").fetchall()
            return self.json(200, {'requests': [dict(row) for row in rows]})
        if self.path == '/api/admin/consultation-slots':
            return self.json(200, {'slots': [dict(row) for row in db.execute('SELECT id,starts_at,duration_minutes,status,capacity FROM consultation_slots ORDER BY starts_at DESC LIMIT 200')], 'timeZone': CONSULTATION_TIMEZONE})
        return self.json(404, {'error': 'Not found'})

    def admin_privacy_allowed(self, staff):
        if not staff or staff['role'] not in ASSESSMENT_LEAD_ROLES or not self.assessment_https():
            return False
        return True

    def admin_assessments(self, staff):
        store = self.supabase()
        if not self.admin_privacy_allowed(staff) or not store:
            return self.json(403, {'error': 'این بخش برای نقش شما مجاز نیست یا اتصال امن برقرار نیست.'})
        try:
            rows = store.request('assessments', 'GET', 'select=id,lead_id,current_step,created_at,completed_at&order=created_at.desc&limit=100', prefer='return=minimal')
            return self.json(200, {'assessments': rows})
        except supabase_store.SupabaseUnavailable:
            logging.getLogger(__name__).warning('database_failure table=assessments')
            return self.json(503, {'error': 'دریافت فهرست ارزیابی‌ها ممکن نشد.'})

    def admin_leads(self, staff):
        store = self.supabase()
        if not self.admin_privacy_allowed(staff) or not store:
            return self.json(403, {'error': 'این بخش برای نقش شما مجاز نیست یا اتصال امن برقرار نیست.'})
        try:
            rows = store.request('leads', 'GET', 'select=id,mobile,consent_follow_up,source_page,source_campaign,status,created_at&order=created_at.desc&limit=200', prefer='return=minimal')
            for row in rows:
                row['mobile'] = admin_workspace.masked(row.get('mobile'))
            return self.json(200, {'leads': rows})
        except supabase_store.SupabaseUnavailable:
            logging.getLogger(__name__).warning('database_failure table=leads')
            return self.json(503, {'error': 'دریافت فهرست لیدها ممکن نشد.'})

    def audit_consultation(self, db, staff, action, result):
        db.execute('INSERT INTO audit(staff_id,action,result,at) VALUES(?,?,?,?)', (staff['staff_id'], action, result, int(time.time())))

    def new_assessment_session(self):
        value = secrets.token_hex(32)
        now = int(time.time())
        with connect() as db:
            db.execute('DELETE FROM assessment_sessions WHERE expires<=?', (now,))
            db.execute('INSERT INTO assessment_sessions(token_hash,expires) VALUES(?,?)', (hashlib.sha256(value.encode()).hexdigest(), now + 3600))
        return value, f'brandyassessment={value}; HttpOnly; Secure; SameSite=Strict; Path=/api/; Max-Age=3600'

    def assessment_status(self):
        if not self.assessment_https():
            return self.json(200, {'ready': False, 'error': 'ارسال تحلیل تا فعال‌شدن اتصال امن سایت در دسترس نیست. پاسخ‌های شما حفظ می‌شوند.'})
        if not brand_analysis.configured():
            return self.json(200, {'ready': False, 'error': 'تحلیل هوشمند هنوز فعال نشده است. پاسخ‌های شما حفظ می‌شوند.'})
        headers = {}
        if not self.assessment_session():
            _, headers['Set-Cookie'] = self.new_assessment_session()
        return self.json(200, {'ready': True}, headers)

    def assessment_analyze(self):
        if not self.assessment_https():
            return self.json(503, {'error': 'برای ارسال پاسخ‌ها، اتصال امن سایت باید فعال باشد.'})
        if not self.safe_origin():
            return self.json(403, {'error': 'این درخواست مجاز نیست.'})
        if not brand_analysis.configured():
            return self.json(503, {'error': 'تحلیل هوشمند هنوز فعال نشده است. پاسخ‌های شما حفظ شده‌اند.'})
        session = self.assessment_session()
        headers = {}
        if not session:
            session, headers['Set-Cookie'] = self.new_assessment_session()
        try:
            answers = brand_analysis.validate_answers(self.request_data(16384, brand_analysis.parse_json))
        except (ValueError, UnicodeError, RecursionError):
            return self.json(422, {'error': 'پاسخ‌های ارزیابی کامل یا معتبر نیستند. لطفاً آن‌ها را بررسی کن.'}, headers)
        try:
            with connect() as db:
                prompt_id, prompt_body = admin_workspace.active_prompt(db)
                assessment_id = supabase_store.SupabaseStore.session_id(session)
                admin_workspace.event(db, assessment_id, 'analysis_started', prompt_id)
                db.commit()
                try:
                    report = brand_analysis.analyze(db, session, self.assessment_source(), answers, prompt_body=prompt_body) if prompt_body else brand_analysis.analyze(db, session, self.assessment_source(), answers)
                except brand_analysis.AnalysisError:
                    admin_workspace.event(db, assessment_id, 'analysis_failed', prompt_id)
                    db.commit()
                    raise
                db.execute('INSERT OR IGNORE INTO admin_assessment_snapshots VALUES(?,?,?,?,?)', (assessment_id, json.dumps(brand_analysis.QUESTIONS, ensure_ascii=False), json.dumps(answers, ensure_ascii=False), prompt_id, int(time.time())))
                db.execute('INSERT INTO admin_assessment_results VALUES(?,?,?,?,?,?)', (str(admin_workspace.uuid.uuid4()), assessment_id, prompt_id, json.dumps(report, ensure_ascii=False), int(time.time()), json.dumps({'answers': answers, 'questions': brand_analysis.QUESTIONS, 'test_version': 'legacy-v1'}, ensure_ascii=False)))
                admin_workspace.event(db, assessment_id, 'analysis_ready', prompt_id)
            return self.json(200, {'report': report, 'session_id': session}, headers)
        except brand_analysis.AnalysisError as error:
            return self.json(error.status, {'error': error.message}, headers)
        except (sqlite3.Error, ValueError, TypeError):
            return self.json(503, {'error': brand_analysis.ERROR}, headers)

    def do_GET(self):
        path = urlsplit(self.path).path
        if path == '/api/assessment/status':
            return self.assessment_status()
        if path == '/api/assessment/lead':
            return self.assessment_lead()
        if path == '/api/assessment/consultation':
            return self.consultation_dispatch()
        if path == '/api/admin/workspace':
            with connect() as db:
                return admin_workspace.dispatch(self, db, self.session(db))
        if path in {'/admin/login', '/admin/workspace.js', '/admin/workspace.css'} or path == '/admin' or path.startswith('/admin/'):
            with connect() as db:
                staff = self.session(db)
                if path == '/admin/login':
                    file = ROOT / 'admin-login.html'
                elif path in {'/admin/workspace.js', '/admin/workspace.css'}:
                    file = ROOT / ('admin-workspace.js' if path.endswith('.js') else 'admin-workspace.css')
                elif not staff:
                    return self.respond(303, content_type='text/html; charset=utf-8', headers={'Location': '/admin/login'})
                elif path == '/admin/consultations':
                    file = ROOT / 'admin.html'
                elif path == '/admin' or path[7:] in admin_workspace.MODULES:
                    if staff['role'] not in admin_workspace.PERMISSIONS or (path != '/admin' and not admin_workspace.allowed(staff['role'], path[7:])):
                        return self.json(403, {'error': 'مجوز این بخش را ندارید.'})
                    file = ROOT / 'admin-workspace.html'
                else:
                    return self.json(404, {'error': 'صفحه پیدا نشد.'})
                return self.respond(200, file.read_bytes(), {'.html': 'text/html; charset=utf-8', '.js': 'text/javascript; charset=utf-8', '.css': 'text/css; charset=utf-8'}[file.suffix])
        public = {'/', '/index.html', '/styles.css', '/typography.css', '/app.js', '/logo.jpg'}
        is_font = path.startswith('/fonts/') and path.endswith('.woff2') and '..' not in path
        with connect() as db:
            staff = self.session(db) if path.startswith('/api/admin/') or path in ('/admin', '/admin-panel.js', '/admin-panel.css', '/admin-client.js') else None
            if path.startswith('/api/admin/'):
                if not staff:
                    return self.json(401, {'error': 'Unauthorized'})
                if path == '/api/admin/me':
                    return self.json(200, {'principal': {'role': staff['role'], 'displayName': staff['name']}, 'csrf': staff['csrf']})
                if path == '/api/admin/consultations' or path == '/api/admin/consultation-slots':
                    return self.admin_consultation(db, staff)
                if path == '/api/admin/assessments':
                    return self.admin_assessments(staff)
                if path == '/api/admin/leads':
                    return self.admin_leads(staff)
                if path == '/api/admin/data':
                    permitted = SECTIONS.get(staff['role'], ())
                    data = {key: [] for key in permitted if key != 'summary'}
                    if 'users' in permitted:
                        rows = db.execute('SELECT id,name,email,status,plan FROM users ORDER BY id DESC LIMIT 50').fetchall()
                        data['users'] = [{'id': str(v['id']), 'name': v['name'], 'email': v['email'] if staff['role'] in ('owner','support') else '—', 'status': v['status'], 'plan': v['plan']} for v in rows]
                    if 'tickets' in permitted:
                        rows = db.execute('SELECT tickets.id,subject,tickets.status,users.name AS user FROM tickets JOIN users ON users.id=tickets.user_id ORDER BY tickets.id DESC LIMIT 50').fetchall()
                        data['tickets'] = [{'id': str(v['id']), 'subject': v['subject'] if staff['role'] in ('owner','support') else '—', 'state': v['status'], 'user': v['user']} for v in rows]
                    if 'audit' in permitted:
                        data['audit'] = [dict(row) for row in db.execute('SELECT at,action,result FROM audit ORDER BY id DESC LIMIT 50')]
                    data['summary'] = {'total': db.execute('SELECT count(*) FROM users').fetchone()[0], 'openTickets': db.execute("SELECT count(*) FROM tickets WHERE status='باز'").fetchone()[0] if 'tickets' in permitted else '—'}
                    return self.json(200, data)
                return self.json(404, {'error': 'Not found'})
            if path in public or is_font:
                file = ROOT / ('index.html' if path in ('/', '/index.html') else path[1:])
            elif staff and path in ('/admin', '/admin-panel.js', '/admin-panel.css', '/admin-client.js'):
                file = ROOT / ('admin.html' if path == '/admin' else path[1:])
            else:
                return self.json(404, {'error': 'Not found'})
            types = {'.html': 'text/html; charset=utf-8', '.js': 'text/javascript; charset=utf-8', '.css': 'text/css; charset=utf-8', '.woff2': 'font/woff2', '.jpg': 'image/jpeg'}
            self.respond(200, file.read_bytes(), types[file.suffix])

    def do_POST(self):
        path = urlsplit(self.path).path
        if path == '/api/assessment/analyze':
            return self.assessment_analyze()
        if path == '/api/assessment/lead':
            return self.assessment_lead(write=True)
        if path == '/api/assessments':
            return self.assessment_record()
        if path == '/api/leads':
            return self.lead_record()
        if path == '/api/assessment/consultation':
            return self.consultation_dispatch(write=True)
        if path == '/api/admin/workspace':
            with connect() as db:
                return admin_workspace.dispatch(self, db, self.session(db), write=True)
        if not self.safe_origin():
            return self.json(403, {'error': 'Forbidden'})
        try:
            data = self.request_data()
        except (ValueError, json.JSONDecodeError):
            return self.json(422, {'error': 'Invalid input'})
        with connect() as db:
            source = self.client_address[0]
            if path in ('/api/admin/assessments', '/api/admin/leads'):
                staff = self.session(db)
                if not self.admin_privacy_allowed(staff) or not hmac.compare_digest(str(data.get('csrf', '')), staff['csrf']):
                    return self.json(403, {'error': 'این درخواست مجاز نیست.'})
                store, target_id = self.supabase(), data.get('id')
                if not store or not isinstance(target_id, str) or not supabase_store.is_id(target_id):
                    return self.json(422, {'error': 'شناسهٔ درخواستی معتبر نیست.'})
                if data.get('confirmed') is not True or not admin_workspace.allowed(staff['role'], 'archive'):
                    return self.json(403, {'error': 'آرشیو نیازمند مجوز و تأیید نهایی است؛ از پنل جدید استفاده کنید.'})
                section = 'assessments' if path.endswith('assessments') else 'customers'
                try:
                    status, result = admin_workspace.mutate(db, staff, store, {'action': 'archive', 'section': section, 'id': target_id, 'confirmed': True})
                    return self.json(status, result)
                except (admin_workspace.Invalid, supabase_store.SupabaseUnavailable):
                    db.rollback()
                    return self.json(503, {'error': 'آرشیو انجام نشد؛ دوباره تلاش کنید.'})
            if path.startswith('/api/admin/consultation'):
                staff = self.session(db)
                if not self.assessment_https() or not staff or staff['role'] not in CONSULTATION_ADMIN_ROLES or not hmac.compare_digest(str(data.get('csrf', '')), staff['csrf']):
                    return self.json(403, {'error': 'این درخواست مجاز نیست.'})
                try:
                    if path == '/api/admin/consultation-slots':
                        date, clock = str(data.get('date', '')).strip(), str(data.get('time', '')).strip()
                        duration = data.get('durationMinutes')
                        if not re.fullmatch(r'[0-9]{4}-[0-9]{2}-[0-9]{2}', date) or not re.fullmatch(r'[0-9]{2}:[0-9]{2}', clock) or type(duration) is not int or not 15 <= duration <= 240: raise ValueError
                        local = datetime.datetime.strptime(f'{date} {clock}', '%Y-%m-%d %H:%M').replace(tzinfo=ZoneInfo(CONSULTATION_TIMEZONE))
                        starts_at = int(local.timestamp())
                        if starts_at <= int(time.time()): raise ValueError
                        db.execute('BEGIN IMMEDIATE')
                        overlap = db.execute("SELECT 1 FROM consultation_slots WHERE status<>'cancelled' AND starts_at<? AND starts_at+duration_minutes*60>? LIMIT 1", (starts_at + duration * 60, starts_at)).fetchone()
                        if overlap: raise ValueError
                        db.execute('INSERT INTO consultation_slots(starts_at,duration_minutes,status,capacity,created_at) VALUES(?,?,?,?,?)', (starts_at,duration,'open',1,int(time.time())))
                        self.audit_consultation(db, staff, f'consultation_slot_create:{db.execute("SELECT last_insert_rowid()").fetchone()[0]}', 'success')
                        db.commit()
                        return self.json(201, {'status': 'created'})
                    if path == '/api/admin/consultation-slot-status':
                        slot_id, status = int(data.get('slotId')), str(data.get('status'))
                        if type(data.get('slotId')) is not int or status not in {'open', 'blocked', 'cancelled'}: raise ValueError
                        db.execute('BEGIN IMMEDIATE')
                        slot = db.execute('SELECT * FROM consultation_slots WHERE id=?', (slot_id,)).fetchone()
                        transitions = {'open': {'blocked','cancelled'}, 'blocked': {'open','cancelled'}, 'cancelled': {'open'}}
                        if not slot or slot['starts_at'] <= int(time.time()) or status not in transitions.get(slot['status'], set()): raise ValueError
                        if status == 'open':
                            overlaps = db.execute("SELECT 1 FROM consultation_slots WHERE id<>? AND status<>'cancelled' AND starts_at<? AND starts_at+duration_minutes*60>? LIMIT 1", (slot_id, slot['starts_at'] + slot['duration_minutes'] * 60, slot['starts_at'])).fetchone()
                            if overlaps: raise ValueError
                        db.execute('UPDATE consultation_slots SET status=? WHERE id=?', (status, slot_id))
                        self.audit_consultation(db, staff, f'consultation_slot_status:{slot_id}', status)
                        db.commit()
                        return self.json(200, {'status': 'updated'})
                    if path == '/api/admin/consultation-status':
                        request_id, status = int(data.get('requestId')), str(data.get('status'))
                        if type(data.get('requestId')) is not int or status not in {'confirmed', 'cancelled', 'completed'}: raise ValueError
                        db.execute('BEGIN IMMEDIATE')
                        request = db.execute('SELECT * FROM consultation_requests WHERE id=?', (request_id,)).fetchone()
                        if not request:
                            db.rollback()
                            return self.json(404, {'error': 'درخواست پیدا نشد.'})
                        transitions = {'pending': {'confirmed','cancelled'}, 'confirmed': {'cancelled','completed'}, 'cancelled': set(), 'completed': set()}
                        if status not in transitions[request['status']]: raise ValueError
                        slot = db.execute('SELECT * FROM consultation_slots WHERE id=?', (request['slot_id'],)).fetchone()
                        if status == 'confirmed':
                            expected_status = 'requested'
                            if request['slot_id'] is None:
                                if type(data.get('slotId')) is not int: raise ValueError
                                slot = db.execute('SELECT * FROM consultation_slots WHERE id=?', (data['slotId'],)).fetchone()
                                expected_status = 'open'
                            if not slot or slot['starts_at'] <= int(time.time()) or slot['status'] != expected_status: raise ValueError
                            overlaps = db.execute("SELECT 1 FROM consultation_requests r JOIN consultation_slots s ON s.id=r.slot_id WHERE r.status='confirmed' AND r.id<>? AND s.starts_at<? AND s.starts_at+s.duration_minutes*60>? LIMIT 1", (request_id, slot['starts_at'] + slot['duration_minutes'] * 60, slot['starts_at'])).fetchone()
                            if overlaps: raise ValueError
                            db.execute('UPDATE consultation_requests SET slot_id=? WHERE id=?', (slot['id'], request_id))
                            db.execute("UPDATE consultation_slots SET status='confirmed' WHERE id=?", (slot['id'],))
                        elif status == 'cancelled':
                            db.execute("UPDATE consultation_slots SET status='cancelled' WHERE id=?", (request['slot_id'],))
                        elif slot['starts_at'] + slot['duration_minutes'] * 60 > int(time.time()):
                            raise ValueError
                        db.execute('UPDATE consultation_requests SET status=?,updated_at=? WHERE id=?', (status, int(time.time()), request_id))
                        self.audit_consultation(db, staff, f'consultation_status:{request_id}', status)
                        db.commit()
                        return self.json(200, {'status': 'updated'})
                except (ValueError, TypeError, sqlite3.Error):
                    db.rollback()
                    return self.json(422, {'error': 'تغییر درخواستی معتبر نیست یا با وضعیت فعلی سازگار نیست.'})
                return self.json(404, {'error': 'Not found'})
            if path == '/api/auth/login':
                email = str(data.get('email', '')).strip().lower()[:254]
                password = str(data.get('password', ''))
                if self.throttle(db, source, email) or not email or len(password) > 1024:
                    return self.json(429, {'error': 'Try later'})
                staff = db.execute('SELECT * FROM staff WHERE email=?', (email,)).fetchone()
                salt = staff['salt'] if staff else b'0' * 32
                check = password_hash(password, salt)
                if not staff or not hmac.compare_digest(check, staff['password_hash']):
                    return self.json(401, {'error': 'Invalid credentials'})
                token = secrets.token_hex(32)
                now = int(time.time())
                db.execute('DELETE FROM sessions WHERE staff_id=? OR expires<?', (staff['id'], now))
                db.execute('INSERT INTO sessions VALUES(?,?,?,?,?,?,?)', (hashlib.sha256(token.encode()).hexdigest(), staff['id'], secrets.token_hex(32), 0, now, now, now + 300))
                db.commit()
                return self.json(200, {'mfaRequired': True}, {'Set-Cookie': self.cookie(token, 300)})
            if path == '/api/auth/mfa/verify':
                staff = self.session(db, require_mfa=False)
                code = str(data.get('code', ''))
                if not staff or staff['verified'] or self.throttle(db, source, f'mfa:{staff["staff_id"]}'):
                    return self.json(401, {'error': 'Verification failed'})
                secret = db.execute('SELECT totp_secret FROM staff WHERE id=?', (staff['staff_id'],)).fetchone()[0]
                if not valid_totp(secret, code, int(time.time())):
                    return self.json(401, {'error': 'Verification failed'})
                token = secrets.token_hex(32)
                now = int(time.time())
                db.execute('DELETE FROM sessions WHERE token_hash=?', (staff['token_hash'],))
                db.execute('INSERT INTO sessions VALUES(?,?,?,?,?,?,?)', (hashlib.sha256(token.encode()).hexdigest(), staff['staff_id'], secrets.token_hex(32), 1, now, now, now + 28800))
                db.execute('INSERT INTO audit(staff_id,action,result,at) VALUES(?,?,?,?)', (staff['staff_id'], 'login', 'success', now))
                admin_workspace.audit(db, staff, 'login', 'staff', str(staff['staff_id']))
                db.commit()
                return self.json(200, {'authenticated': True}, {'Set-Cookie': self.cookie(token)})
            if path == '/api/admin/logout':
                staff = self.session(db)
                if not staff:
                    return self.json(401, {'error': 'Unauthorized'})
                if not hmac.compare_digest(str(data.get('csrf', '')), staff['csrf']):
                    return self.json(403, {'error': 'Forbidden'})
                db.execute('DELETE FROM sessions WHERE token_hash=?', (staff['token_hash'],))
                admin_workspace.audit(db, staff, 'logout', 'staff', str(staff['staff_id']))
                db.commit()
                return self.json(200, {'status': 'success'}, {'Set-Cookie': self.cookie('', 0)})
            return self.json(404, {'error': 'Not found'})


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest='command', required=True)
    run = sub.add_parser('serve')
    run.add_argument('--port', type=int, default=8000)
    create = sub.add_parser('add-staff')
    create.add_argument('email')
    create.add_argument('name')
    create.add_argument('role', choices=sorted(ROLES))
    args = parser.parse_args()
    if args.command == 'add-staff':
        add_staff(args.email, args.name, args.role)
    else:
        print('Serving on loopback; terminate with Ctrl-C')
        ThreadingHTTPServer((os.environ.get('BRANDYAR_HOST', '127.0.0.1'), args.port), Handler).serve_forever()
