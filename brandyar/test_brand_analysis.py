import json
import sqlite3
import tempfile
import threading
import time
import unittest
from concurrent.futures import ThreadPoolExecutor
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError, URLError

import brand_analysis as analysis
import server


def sample_answers(service=False):
    answers = {}
    for question in analysis.QUESTIONS:
        key = question['id']
        if (service and key == 'q12a') or (not service and key in ('q12', 'q13', 'q14')):
            continue
        if question.get('type') in ('text', 'textarea'):
            answers[key] = 'اطلاعات خصوصی آزمایشی'
        elif question.get('type') == 'multi':
            answers[key] = [question['options'][0]]
        else:
            answers[key] = question['options'][0]
    answers['q11'] = ['کلاس یا دورهٔ آموزشی' if service else 'آموزش رایگان در پیج']
    answers['q2extra'] = 'متن آزاد خصوصی آزمایشی'
    return {'answers': answers, 'consent': True}


def sample_report():
    return {
        'summary': 'بر اساس پاسخ‌ها، مسیر معرفی تخصص نیازمند شفاف‌سازی است.',
        **{key: {'status': 'نیازمند بررسی بیشتر', 'insight': 'از روی گزینه‌های انتخابی نمی‌توان دربارهٔ کیفیت واقعی قضاوت کرد.'} for key in ('positioning', 'content', 'trust')},
        'strengths': ['آمادگی برای مرور مسیر محتوا'],
        'growth_opportunities': ['روشن‌ترکردن پیام معرفی'],
        'priority_actions': [{'title': 'نوشتن پیام معرفی', 'description': 'یک جمله دربارهٔ مخاطب آموزش خود بنویس.', 'why_it_matters': 'شروع مسیر را روشن‌تر می‌کند.'} for _ in range(3)],
        'this_week_action': {'title': 'مرور یک تجربه', 'description': 'یک تجربهٔ آموزشی کوتاه یادداشت کن.'},
        'questions_to_refine': ['موضوع دقیق آموزش شما چیست؟'],
        'disclaimer': analysis.DISCLAIMER,
    }


class SchemaTests(unittest.TestCase):
    def test_both_branches_and_data_minimization(self):
        for service in (True, False):
            data = analysis.validate_answers(sample_answers(service))
            self.assertNotIn('خصوصی', json.dumps(data, ensure_ascii=False))
            self.assertTrue(set(data).isdisjoint({'q1', 'q3', 'q6', 'q2extra'}))
            self.assertEqual('q12' in data, service)
            self.assertEqual('q12a' in data, not service)

    def test_invalid_input(self):
        invalid = []
        for key, value in [('q1', ''), ('q4', 'گزینهٔ نامعتبر'), ('q10', ['الف']), ('q6', 'x' * 501), ('q5', [analysis.QUESTIONS[4]['none'], analysis.QUESTIONS[4]['options'][0]]), ('q11', [1])]:
            body = sample_answers()
            body['answers'][key] = value
            invalid.append(body)
        body = sample_answers(); body['consent'] = False; invalid.append(body)
        body = sample_answers(); body['answers']['email'] = 'not-sent'; invalid.append(body)
        body = sample_answers(); body['answers']['q12'] = 'دایرکت'; invalid.append(body)
        for body in invalid:
            with self.subTest(body=body), self.assertRaises(ValueError):
                analysis.validate_answers(body)

    def test_report_schema(self):
        self.assertEqual(analysis.validate_report(sample_report())['disclaimer'], analysis.DISCLAIMER)
        changes = [('summary', '<script>سلام</script>'), ('summary', 'امتیاز شما ۹۰ است'), ('summary', 'نود درصد رشد'), ('summary', 'https://example.test'), ('priority_actions', []), ('strengths', ['']), ('questions_to_refine', ['x' * 301]), ('summary', 1)]
        for key, value in changes:
            report = sample_report(); report[key] = value
            with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                analysis.validate_report(report)
        report = sample_report(); del report['trust']
        with self.assertRaises(ValueError): analysis.validate_report(report)
        with self.assertRaises(ValueError): analysis.parse_json('{"a":1,"a":2}')
        with self.assertRaises(ValueError): analysis.parse_json('{"a":NaN}')

    def test_missing_configuration(self):
        with patch.dict('os.environ', {'BRANDYAR_METIS_API_KEY': ''}):
            with self.assertRaises(analysis.AnalysisError) as caught:
                analysis.generate_report({})
        self.assertEqual(caught.exception.status, 503)

    def test_provider_payment_failure(self):
        with patch.dict('os.environ', {'BRANDYAR_METIS_API_KEY': 'unit-test-only'}), patch.object(analysis, 'build_opener') as opener:
            for code in (402, 401, 500):
                opener.return_value.open.side_effect = HTTPError(analysis.ENDPOINT, code, 'private provider details', {}, None)
                with self.subTest(code=code), self.assertRaises(analysis.AnalysisError) as caught:
                    analysis.generate_report({})
                self.assertEqual(caught.exception.status, 503 if code == 402 else 502)
                self.assertNotIn('private', caught.exception.message)
                if code == 402:
                    self.assertIn('اعتبار یا پرداخت', caught.exception.message)

    def test_provider_contract_and_failures(self):
        envelope = {'choices': [{'finish_reason': 'stop', 'message': {'content': json.dumps(sample_report())}}]}
        with patch.dict('os.environ', {'BRANDYAR_METIS_API_KEY': 'unit-test-only'}), patch.object(analysis, 'build_opener') as opener:
            response = opener.return_value.open.return_value.__enter__.return_value
            response.read.return_value = json.dumps(envelope).encode()
            result = analysis.generate_report({'q4': {'answer': 'گزینهٔ عمومی'}})
            self.assertEqual(len(result['priority_actions']), 3)
            request = opener.return_value.open.call_args.args[0]
            self.assertEqual(request.full_url, analysis.ENDPOINT)
            payload = json.loads(request.data)
            self.assertEqual(payload['model'], 'grok-4-fast')
            self.assertEqual(payload['messages'][0]['role'], 'system')
            self.assertEqual(payload['messages'][1]['role'], 'user')
            response.read.return_value = b'{"choices": []}'
            with self.assertRaises(analysis.AnalysisError): analysis.generate_report({})
            envelope['choices'][0]['finish_reason'] = 'length'
            response.read.return_value = json.dumps(envelope).encode()
            with self.assertRaises(analysis.AnalysisError): analysis.generate_report({})
            opener.return_value.open.side_effect = URLError('private provider details')
            with self.assertRaises(analysis.AnalysisError) as caught: analysis.generate_report({})
            self.assertNotIn('private', caught.exception.message)


class StorageTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(dir=Path(__file__).parent)
        self.path = str(Path(self.directory.name) / 'test.sqlite')
        self.answers = analysis.validate_answers(sample_answers())
        with self.database() as db: analysis.initialize(db)

    def tearDown(self):
        self.directory.cleanup()

    def database(self):
        db = sqlite3.connect(self.path, timeout=10)
        db.row_factory = sqlite3.Row
        return db

    def test_cache_and_session_isolation(self):
        with self.database() as db, patch.object(analysis, 'generate_report', return_value=sample_report()) as generate, patch.object(analysis.time, 'time', return_value=10000) as clock:
            analysis.analyze(db, 'session-one', 'source', self.answers)
            analysis.analyze(db, 'session-one', 'source', self.answers)
            self.assertEqual(generate.call_count, 1)
            self.assertEqual(db.execute('SELECT count(*) FROM assessment_attempts').fetchone()[0], 1)
            clock.return_value += 10
            analysis.analyze(db, 'session-two', 'source', self.answers)
            self.assertEqual(generate.call_count, 2)
            self.assertNotIn('خصوصی', str(db.execute('SELECT report FROM assessment_jobs').fetchall()))

    def test_failed_attempts_do_not_consume_quota(self):
        with self.database() as db, patch.object(analysis, 'generate_report', side_effect=analysis.AnalysisError()) as generate, patch.object(analysis.time, 'time', return_value=10000) as clock:
            for _ in range(5):
                with self.assertRaises(analysis.AnalysisError) as caught:
                    analysis.analyze(db, 'session', 'source', self.answers)
                self.assertEqual(caught.exception.status, 502)
                clock.return_value += 10
            self.assertEqual(db.execute('SELECT count(*) FROM assessment_jobs').fetchone()[0], 0)
            self.assertEqual(db.execute("SELECT count(*) FROM assessment_attempts WHERE state='failed'").fetchone()[0], 5)
            generate.side_effect = None
            generate.return_value = sample_report()
            self.assertEqual(analysis.analyze(db, 'session', 'source', self.answers), sample_report())

    def test_short_cooldown_and_source_isolation(self):
        with self.database() as db, patch.object(analysis, 'generate_report', side_effect=analysis.AnalysisError()) as generate, patch.object(analysis.time, 'time', return_value=10000) as clock:
            with self.assertRaises(analysis.AnalysisError):
                analysis.analyze(db, 'session', 'source', self.answers)
            clock.return_value += 9
            with self.assertRaises(analysis.AnalysisError) as caught:
                analysis.analyze(db, 'new-session', 'source', self.answers)
            self.assertEqual(caught.exception.status, 429)
            self.assertIn('1 ثانیه', caught.exception.message)
            self.assertEqual(generate.call_count, 1)
            with self.assertRaises(analysis.AnalysisError) as caught:
                analysis.analyze(db, 'other-session', 'other-source', self.answers)
            self.assertEqual(caught.exception.status, 502)
            clock.return_value += 1
            with self.assertRaises(analysis.AnalysisError) as caught:
                analysis.analyze(db, 'session', 'source', self.answers)
            self.assertEqual(caught.exception.status, 502)

    def test_successful_hourly_quota_and_expiry(self):
        with self.database() as db, patch.object(analysis, 'generate_report', return_value=sample_report()) as generate, patch.object(analysis.time, 'time', return_value=10000) as clock:
            for index in range(3):
                analysis.analyze(db, f'session-{index}', 'source', self.answers)
                clock.return_value += 10
            with self.assertRaises(analysis.AnalysisError) as caught:
                analysis.analyze(db, 'fourth-session', 'source', self.answers)
            self.assertEqual(caught.exception.status, 429)
            self.assertIn('۳ تحلیل موفق', caught.exception.message)
            self.assertEqual(generate.call_count, 3)
            analysis.analyze(db, 'session-0', 'source', self.answers)
            self.assertEqual(generate.call_count, 3)
            clock.return_value = 13600
            analysis.analyze(db, 'fourth-session', 'source', self.answers)
            self.assertEqual(generate.call_count, 4)

    def test_legacy_failures_do_not_block_retry(self):
        with self.database() as db, patch.object(analysis, 'generate_report', return_value=sample_report()):
            db.execute('CREATE TABLE assessment_usage (source_hash TEXT NOT NULL, at INTEGER NOT NULL)')
            source_hash = analysis.hashlib.sha256(b'source').hexdigest()
            db.executemany('INSERT INTO assessment_usage VALUES(?,?)', [(source_hash, int(analysis.time.time()))] * 3)
            db.commit()
            self.assertEqual(analysis.analyze(db, 'session', 'source', self.answers), sample_report())

    def test_stale_reservations_are_released(self):
        with self.database() as db, patch.object(analysis, 'generate_report', return_value=sample_report()), patch.object(analysis.time, 'time', return_value=10000):
            source_hash = analysis.hashlib.sha256(b'source').hexdigest()
            db.executemany("INSERT INTO assessment_attempts(source_hash,at,state) VALUES(?,?,'processing')", [(source_hash, 9900)] * 3)
            db.commit()
            self.assertEqual(analysis.analyze(db, 'session', 'source', self.answers), sample_report())
            self.assertEqual(db.execute("SELECT count(*) FROM assessment_attempts WHERE state='failed'").fetchone()[0], 3)

    def test_processing_reservations_enforce_limits(self):
        with self.database() as db, patch.object(analysis, 'generate_report') as generate, patch.object(analysis.time, 'time', return_value=10000):
            source_hash = analysis.hashlib.sha256(b'source').hexdigest()
            db.executemany("INSERT INTO assessment_attempts(source_hash,at,state) VALUES(?,?,'processing')", [(source_hash, 9980)] * 3)
            db.commit()
            with self.assertRaises(analysis.AnalysisError) as caught:
                analysis.analyze(db, 'session', 'source', self.answers)
            self.assertEqual(caught.exception.status, 429)
            generate.assert_not_called()

    def test_global_success_quota_and_failure_exclusion(self):
        with self.database() as db, patch.object(analysis, 'generate_report', return_value=sample_report()) as generate, patch.object(analysis.time, 'time', return_value=10000):
            db.executemany("INSERT INTO assessment_attempts(source_hash,at,state) VALUES(?,?,'failed')", [('other', 9980)] * 100)
            db.executemany("INSERT INTO assessment_attempts(source_hash,at,state) VALUES(?,?,'ready')", [('other', 9980)] * 99)
            db.commit()
            analysis.analyze(db, 'session', 'source', self.answers)
            with self.assertRaises(analysis.AnalysisError) as caught:
                analysis.analyze(db, 'another-session', 'another-source', self.answers)
            self.assertEqual(caught.exception.status, 429)
            self.assertEqual(generate.call_count, 1)

    def test_concurrent_duplicate(self):
        entered, finish = threading.Event(), threading.Event()
        def generate(_):
            entered.set()
            self.assertTrue(finish.wait(5))
            return sample_report()
        def first():
            with self.database() as db:
                return analysis.analyze(db, 'session', 'source', self.answers)
        with patch.object(analysis, 'generate_report', side_effect=generate) as generate_mock, ThreadPoolExecutor(max_workers=1) as executor:
            task = executor.submit(first)
            self.assertTrue(entered.wait(5))
            try:
                with self.database() as db, self.assertRaises(analysis.AnalysisError) as caught:
                    analysis.analyze(db, 'session', 'source', self.answers)
                self.assertEqual(caught.exception.status, 409)
            finally:
                finish.set()
            self.assertEqual(len(task.result()['priority_actions']), 3)
            self.assertEqual(generate_mock.call_count, 1)


class ConsultationTests(unittest.TestCase):
    path = '/api/assessment/consultation'

    @classmethod
    def setUpClass(cls):
        cls.http = ThreadingHTTPServer(('127.0.0.1', 0), server.Handler)
        cls.thread = threading.Thread(target=cls.http.serve_forever)
        cls.thread.start()
        cls.port = cls.http.server_address[1]

    @classmethod
    def tearDownClass(cls):
        cls.http.shutdown(); cls.http.server_close(); cls.thread.join()

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(dir=Path(__file__).parent)
        self.addCleanup(self.directory.cleanup)
        self.addCleanup(patch.stopall)
        patch.object(server, 'DB', Path(self.directory.name) / 'consultation.sqlite').start()
        patch.object(analysis, 'configured', return_value=True).start()
        self.provider = patch.object(analysis, 'generate_report').start()
        self.headers = {'Content-Type':'application/json', 'X-Forwarded-Proto':'https', 'Origin':f'https://127.0.0.1:{self.port}'}
        with server.connect() as db:
            analysis.initialize(db)

    def call(self, method, path, body=None, cookie='', headers=None):
        connection = HTTPConnection('127.0.0.1', self.port, timeout=10)
        request_headers = {**self.headers, 'Cookie':cookie, **(headers or {})}
        connection.request(method, path, json.dumps(body) if body is not None else None, request_headers)
        response = connection.getresponse()
        raw = response.read()
        payload = json.loads(raw) if response.getheader('Content-Type', '').startswith('application/json') else raw.decode()
        result = response.status, payload, dict(response.getheaders())
        connection.close()
        return result

    def assessment(self, ready=True, report=None):
        status, _, headers = self.call('GET', '/api/assessment/status')
        self.assertEqual(status, 200)
        cookie = headers['Set-Cookie'].split(';')[0]
        self.assertIn('Path=/api/assessment/', headers['Set-Cookie'])
        if ready:
            session_hash = analysis.hashlib.sha256(cookie.split('=', 1)[1].encode()).hexdigest()
            with server.connect() as db:
                db.execute('INSERT INTO assessment_jobs VALUES(?,?,?,?,?)', (session_hash, 'test', 'ready', int(time.time()), json.dumps(sample_report() if report is None else report)))
        return cookie

    def staff(self, role='owner', verified=True):
        token = server.secrets.token_hex(32)
        csrf = 'test-csrf'
        with server.connect() as db:
            now = int(time.time())
            staff_id = db.execute('INSERT INTO staff(email,name,role,salt,password_hash,totp_secret) VALUES(?,?,?,?,?,?)', (f'{token}@example.test','مدیر آزمایشی',role,b'test',b'test','test')).lastrowid
            db.execute('INSERT INTO sessions VALUES(?,?,?,?,?,?,?)', (analysis.hashlib.sha256(token.encode()).hexdigest(), staff_id, csrf, int(verified), now, now, now+3600))
        return f'brandysid={token}', csrf

    def slot(self, starts=None, status='open'):
        with server.connect() as db:
            return db.execute('INSERT INTO consultation_slots(starts_at,duration_minutes,status,capacity,created_at) VALUES(?,?,?,?,?)', (starts or int(time.time())+86400,60,status,1,int(time.time()))).lastrowid

    def body(self, slot, phone='۰۹۱۲-۱۲۳-۴۵۶۷', **changes):
        return {'name':'', 'phone':phone, 'slotId':slot, 'notes':'', **changes}

    def test_iranian_phone_normalization(self):
        handler = object.__new__(server.Handler)
        for value in ('۰۹۱۲-۱۲۳-۴۵۶۷', '+989121234567', '989121234567', '٠٩١٢١٢٣٤٥٦٧'):
            self.assertEqual(handler.consultation_phone(value), '09121234567')
        for value in ('', '0912', '0912123456a', '02112345678', '+98912123456', '0'*40, None, 9121234567, '09𝟙𝟚𝟙𝟚𝟛𝟜𝟝𝟞𝟟'):
            with self.subTest(value=value), self.assertRaises(ValueError):
                handler.consultation_phone(value)

    def test_gate_session_report_origin_and_https(self):
        self.assertEqual(self.call('GET', self.path)[0], 401)
        no_report = self.assessment(ready=False)
        self.assertEqual(self.call('GET', self.path, cookie=no_report)[0], 403)
        self.assertEqual(self.call('POST', self.path, self.body(1), no_report)[0], 403)
        malformed = self.assessment(report={'summary':'ناقص'})
        self.assertEqual(self.call('GET', self.path, cookie=malformed)[0], 403)
        cookie = self.assessment()
        self.assertEqual(self.call('POST', self.path, self.body(1), cookie, {'Origin':'https://untrusted.test'})[0], 403)
        self.assertEqual(self.call('POST', self.path, self.body(1), cookie, {'X-Forwarded-Proto':'http'})[0], 403)
        self.assertEqual(self.call('GET', self.path, cookie=cookie, headers={'X-Forwarded-Proto':'http'})[0], 503)
        self.assertEqual(self.call('GET', self.path, cookie=cookie+'tampered')[0], 401)
        self.provider.assert_not_called()

    def test_slots_empty_future_open_and_private(self):
        cookie = self.assessment()
        self.assertEqual(self.call('GET', self.path, cookie=cookie)[1]['slots'], [])
        open_slot = self.slot()
        self.slot(starts=int(time.time())-1)
        for state in ('requested','confirmed','blocked','cancelled'):
            self.slot(status=state)
        status, data, headers = self.call('GET', self.path, cookie=cookie)
        self.assertEqual(status, 200)
        self.assertEqual([row['id'] for row in data['slots']], [open_slot])
        self.assertEqual(set(data['slots'][0]), {'id','startsAt','durationMinutes','timeZone'})
        self.assertEqual(data['slots'][0]['timeZone'], 'Asia/Tehran')
        self.assertEqual(headers['Cache-Control'], 'no-store')
        self.assertNotIn('phone', json.dumps(data))

    def test_request_pending_isolated_and_duplicate_phone(self):
        cookie, other = self.assessment(), self.assessment()
        slot = self.slot()
        status, data, _ = self.call('POST', self.path, self.body(slot), cookie)
        self.assertEqual(status, 201)
        self.assertEqual(data['request']['state'], 'pending')
        self.assertIn('بعد از تأیید', data['message'])
        self.assertNotIn('phone', json.dumps(data))
        own = self.call('GET', self.path, cookie=cookie)[1]
        foreign = self.call('GET', self.path, cookie=other)[1]
        self.assertEqual(own['request']['state'], 'pending')
        self.assertIsNone(foreign['request'])
        self.assertEqual(foreign['slots'], [])
        second = self.slot(starts=int(time.time())+172800)
        self.assertEqual(self.call('POST', self.path, self.body(second), cookie)[0], 409)
        status, data, _ = self.call('POST', self.path, self.body(second), other)
        self.assertEqual(status, 409)
        self.assertNotIn('phone', json.dumps(data))
        with server.connect() as db:
            self.assertEqual(db.execute('SELECT count(*) FROM consultation_requests').fetchone()[0], 1)
            self.assertEqual(db.execute('SELECT phone FROM consultation_requests').fetchone()[0], '09121234567')
            self.assertEqual(db.execute('SELECT status FROM consultation_slots WHERE id=?', (second,)).fetchone()[0], 'open')
        self.provider.assert_not_called()

    def test_validation_and_session_rate_limit(self):
        slot = self.slot()
        invalid = [self.body(slot, phone=value) for value in ('','0912','0912123456a','02112345678')]
        invalid += [self.body(slot, notes='الف'*70), self.body(slot, name='ن'*121), self.body(True), self.body(str(slot)), self.body(slot, name={}), self.body(slot, phone=None)]
        for body in invalid:
            cookie = self.assessment()
            self.assertEqual(self.call('POST', self.path, body, cookie)[0], 422)
        cookie = self.assessment()
        for _ in range(5):
            self.assertEqual(self.call('POST', self.path, self.body(slot, phone=''), cookie)[0], 422)
        self.assertEqual(self.call('POST', self.path, self.body(slot), cookie)[0], 429)
        with server.connect() as db:
            self.assertEqual(db.execute('SELECT count(*) FROM consultation_requests').fetchone()[0], 0)

    def test_past_blocked_and_unknown_slots_rejected(self):
        cookie = self.assessment()
        for slot in (self.slot(starts=int(time.time())-1), self.slot(status='blocked'), 999):
            self.assertEqual(self.call('POST', self.path, self.body(slot), cookie)[0], 409)

    def test_parallel_booking_and_confirmation(self):
        cookies = [self.assessment(), self.assessment()]
        slot = self.slot()
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(lambda index: self.call('POST', self.path, self.body(slot, phone=f'0912123456{index}'), cookies[index])[0], range(2)))
        self.assertEqual(sorted(results), [201,409])
        admin, csrf = self.staff()
        with server.connect() as db:
            request_id = db.execute('SELECT id FROM consultation_requests').fetchone()[0]
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(lambda _: self.call('POST','/api/admin/consultation-status',{'requestId':request_id,'status':'confirmed','csrf':csrf},admin)[0], range(2)))
        self.assertEqual(sorted(results), [200,422])
        with server.connect() as db:
            self.assertEqual(db.execute("SELECT count(*) FROM consultation_requests WHERE status='confirmed'").fetchone()[0], 1)
        self.assertEqual(self.call('GET', self.path, cookie=cookies[0])[1]['slots'], [])

    def test_admin_roles_mfa_csrf_and_private_number(self):
        cookie = self.assessment()
        self.call('POST', self.path, self.body(self.slot()), cookie)
        for role in ('viewer','finance','product'):
            admin, csrf = self.staff(role)
            status, data, _ = self.call('GET','/api/admin/consultations',cookie=admin)
            self.assertEqual(status,403)
            self.assertNotIn('09121234567',json.dumps(data))
            self.assertEqual(self.call('POST','/api/admin/consultation-status',{'requestId':1,'status':'confirmed','csrf':csrf},admin)[0],403)
        unverified, _ = self.staff(verified=False)
        self.assertEqual(self.call('GET','/api/admin/consultations',cookie=unverified)[0],401)
        self.assertEqual(self.call('GET','/admin',cookie=unverified)[0],404)
        for role in ('owner','support'):
            admin, csrf = self.staff(role)
            status, data, _ = self.call('GET','/api/admin/consultations',cookie=admin)
            self.assertEqual(status,200)
            self.assertEqual(data['requests'][0]['phone'],'09121234567')
            self.assertEqual(self.call('GET','/admin',cookie=admin)[0],200)
            self.assertEqual(self.call('POST','/api/admin/consultation-status',{'requestId':1,'status':'confirmed','csrf':'wrong'},admin)[0],403)
        self.assertEqual(self.call('GET','/api/admin/consultations')[0],401)

    def test_admin_slot_timezone_overlap_block_cancel_and_reopen(self):
        admin, csrf = self.staff()
        local = server.datetime.datetime.now(server.ZoneInfo(server.CONSULTATION_TIMEZONE)) + server.datetime.timedelta(days=2)
        day = local.strftime('%Y-%m-%d')
        payload = {'date':day,'time':'10:00','durationMinutes':60,'csrf':csrf}
        self.assertEqual(self.call('POST','/api/admin/consultation-slots',payload,admin)[0],201)
        self.assertEqual(self.call('POST','/api/admin/consultation-slots',{**payload,'time':'10:30'},admin)[0],422)
        expected = int(server.datetime.datetime.strptime(day+' 10:00','%Y-%m-%d %H:%M').replace(tzinfo=server.ZoneInfo(server.CONSULTATION_TIMEZONE)).timestamp())
        with server.connect() as db:
            row = db.execute('SELECT * FROM consultation_slots').fetchone()
            self.assertEqual(row['starts_at'],expected)
            slot = row['id']
        for state in ('blocked','open','cancelled','open'):
            self.assertEqual(self.call('POST','/api/admin/consultation-slot-status',{'slotId':slot,'status':state,'csrf':csrf},admin)[0],200)
        self.assertEqual(self.call('POST','/api/admin/consultation-slot-status',{'slotId':999,'status':'open','csrf':csrf},admin)[0],422)
        self.assertEqual(self.call('POST','/api/admin/consultation-slots',{**payload,'date':'2020-01-01'},admin)[0],422)
        with server.connect() as db:
            self.assertEqual(db.execute('SELECT count(*) FROM audit').fetchone()[0],5)

    def test_request_state_machine_and_private_audit(self):
        cookie = self.assessment()
        slot = self.slot()
        self.call('POST',self.path,self.body(slot),cookie)
        admin, csrf = self.staff()
        body = {'requestId':1,'status':'confirmed','csrf':csrf}
        self.assertEqual(self.call('POST','/api/admin/consultation-status',{**body,'status':'completed'},admin)[0],422)
        self.assertEqual(self.call('POST','/api/admin/consultation-status',body,admin)[0],200)
        self.assertEqual(self.call('GET',self.path,cookie=cookie)[1]['request']['state'],'confirmed')
        self.assertEqual(self.call('POST','/api/admin/consultation-status',{**body,'status':'completed'},admin)[0],422)
        self.assertEqual(self.call('POST','/api/admin/consultation-status',{**body,'status':'cancelled'},admin)[0],200)
        self.assertEqual(self.call('GET',self.path,cookie=cookie)[1]['request']['state'],'cancelled')
        self.assertEqual(self.call('POST','/api/admin/consultation-status',body,admin)[0],422)
        with server.connect() as db:
            audit = [dict(row) for row in db.execute('SELECT action,result FROM audit')]
            self.assertEqual(len(audit),2)
            self.assertNotIn('09121234567',json.dumps(audit))
            self.assertEqual(db.execute('SELECT count(*) FROM consultation_requests').fetchone()[0],1)

    def test_overlapping_legacy_slots_cannot_both_be_confirmed(self):
        first, second = self.slot(), self.slot()
        cookies = [self.assessment(), self.assessment()]
        for index, slot in enumerate((first,second)):
            self.assertEqual(self.call('POST',self.path,self.body(slot,phone=f'0912123456{index}'),cookies[index])[0],201)
        admin, csrf = self.staff()
        with ThreadPoolExecutor(max_workers=2) as pool:
            statuses = list(pool.map(lambda request_id:self.call('POST','/api/admin/consultation-status',{'requestId':request_id,'status':'confirmed','csrf':csrf},admin)[0],(1,2)))
        self.assertEqual(sorted(statuses),[200,422])

    def test_completed_only_after_session_end(self):
        cookie = self.assessment()
        slot = self.slot()
        self.assertEqual(self.call('POST', self.path, self.body(slot), cookie)[0], 201)
        admin, csrf = self.staff()
        payload = {'requestId': 1, 'status': 'confirmed', 'csrf': csrf}
        self.assertEqual(self.call('POST', '/api/admin/consultation-status', payload, admin)[0], 200)
        with server.connect() as db:
            db.execute('UPDATE consultation_slots SET starts_at=? WHERE id=?', (int(time.time()) - 7200, slot))
        payload['status'] = 'completed'
        self.assertEqual(self.call('POST', '/api/admin/consultation-status', payload, admin)[0], 200)
        self.assertEqual(self.call('GET', self.path, cookie=cookie)[1]['request']['state'], 'completed')
        self.assertEqual(self.call('POST', '/api/admin/consultation-status', payload, admin)[0], 422)

    def test_failed_write_rolls_back_request_and_slot(self):
        cookie = self.assessment()
        slot = self.slot()
        with server.connect() as db:
            db.execute("CREATE TRIGGER reject_slot_update BEFORE UPDATE ON consultation_slots BEGIN SELECT RAISE(ABORT, 'private storage detail'); END")
        status, data, _ = self.call('POST', self.path, self.body(slot), cookie)
        self.assertNotIn(status, (200, 201))
        self.assertNotIn('private', json.dumps(data))
        with server.connect() as db:
            self.assertEqual(db.execute('SELECT count(*) FROM consultation_requests').fetchone()[0], 0)
            self.assertEqual(db.execute('SELECT status FROM consultation_slots WHERE id=?', (slot,)).fetchone()[0], 'open')

    def test_callback_without_available_slots_and_admin_scheduling(self):
        cookie = self.assessment()
        status, data, _ = self.call('POST', self.path, self.body(None), cookie)
        self.assertEqual(status, 201)
        self.assertIsNone(data['request']['startsAt'])
        self.assertEqual(data['request']['state'], 'pending')
        self.assertIn('هماهنگی', data['request']['status'])
        self.assertNotIn('09121234567', json.dumps(data))
        self.assertEqual(self.call('GET', self.path, cookie=cookie)[1]['request'], data['request'])
        self.assertEqual(self.call('POST', self.path, self.body(None), cookie)[0], 409)
        other = self.assessment()
        self.assertEqual(self.call('POST', self.path, self.body(None), other)[0], 409)
        self.assertIsNone(self.call('GET', self.path, cookie=other)[1]['request'])
        admin, csrf = self.staff()
        item = self.call('GET', '/api/admin/consultations', cookie=admin)[1]['requests'][0]
        self.assertEqual(item['phone'], '09121234567')
        self.assertIsNone(item['starts_at'])
        payload = {'requestId': item['id'], 'status': 'confirmed', 'csrf': csrf}
        self.assertEqual(self.call('POST', '/api/admin/consultation-status', payload, admin)[0], 422)
        blocked = self.slot(status='blocked')
        self.assertEqual(self.call('POST', '/api/admin/consultation-status', {**payload, 'slotId': blocked}, admin)[0], 422)
        slot = self.slot()
        self.assertEqual(self.call('POST', '/api/admin/consultation-status', {**payload, 'slotId': slot}, admin)[0], 200)
        confirmed = self.call('GET', self.path, cookie=cookie)[1]['request']
        self.assertEqual(confirmed['state'], 'confirmed')
        self.assertIsNotNone(confirmed['startsAt'])
        self.provider.assert_not_called()

    def test_callback_cancellation_without_slot(self):
        cookie = self.assessment()
        self.assertEqual(self.call('POST', self.path, self.body(None), cookie)[0], 201)
        admin, csrf = self.staff()
        self.assertEqual(self.call('POST', '/api/admin/consultation-status', {'requestId': 1, 'status': 'cancelled', 'csrf': csrf}, admin)[0], 200)
        self.assertEqual(self.call('GET', self.path, cookie=cookie)[1]['request']['state'], 'cancelled')
        self.assertEqual(self.call('POST', self.path, self.body(None), cookie)[0], 201)

    def test_parallel_callbacks_cannot_take_same_slot(self):
        cookies = [self.assessment(), self.assessment()]
        for index, cookie in enumerate(cookies):
            self.assertEqual(self.call('POST', self.path, self.body(None, phone=f'0912123456{index}'), cookie)[0], 201)
        admin, csrf = self.staff()
        slot = self.slot()
        with ThreadPoolExecutor(max_workers=2) as pool:
            statuses = list(pool.map(lambda request_id: self.call('POST', '/api/admin/consultation-status', {'requestId': request_id, 'status': 'confirmed', 'slotId': slot, 'csrf': csrf}, admin)[0], (1, 2)))
        self.assertEqual(sorted(statuses), [200, 422])
        with server.connect() as db:
            self.assertEqual(db.execute("SELECT count(*) FROM consultation_requests WHERE status='confirmed'").fetchone()[0], 1)
            self.assertEqual(db.execute("SELECT count(*) FROM consultation_requests WHERE status='pending' AND slot_id IS NULL").fetchone()[0], 1)

    def test_nullable_slot_migration_preserves_existing_booking(self):
        cookie = self.assessment()
        slot = self.slot()
        self.assertEqual(self.call('POST', self.path, self.body(slot), cookie)[0], 201)
        with server.connect() as db:
            db.execute('CREATE TABLE consultation_requests_old (id INTEGER PRIMARY KEY, session_hash TEXT NOT NULL, name TEXT NOT NULL, phone TEXT NOT NULL, slot_id INTEGER NOT NULL REFERENCES consultation_slots(id), notes TEXT NOT NULL, status TEXT NOT NULL, created_at INTEGER NOT NULL, updated_at INTEGER NOT NULL)')
            db.execute('INSERT INTO consultation_requests_old SELECT * FROM consultation_requests')
            db.execute('DROP TABLE consultation_requests')
            db.execute('ALTER TABLE consultation_requests_old RENAME TO consultation_requests')
        with server.connect() as db:
            row = db.execute('SELECT * FROM consultation_requests').fetchone()
            self.assertEqual(row['slot_id'], slot)
            self.assertEqual(row['phone'], '09121234567')
            self.assertFalse(next(row['notnull'] for row in db.execute('PRAGMA table_info(consultation_requests)') if row['name'] == 'slot_id'))
            with self.assertRaises(sqlite3.IntegrityError):
                db.execute('INSERT INTO consultation_requests SELECT id+1,session_hash,name,phone,slot_id,notes,status,created_at,updated_at FROM consultation_requests')
        other = self.assessment()
        self.assertEqual(self.call('POST', self.path, self.body(None, phone='09121234568'), other)[0], 201)

    def test_storage_failure_never_returns_success(self):
        cookie = self.assessment()
        with patch.object(server,'connect',side_effect=sqlite3.OperationalError('private details')):
            status, data, _ = self.call('POST',self.path,self.body(1),cookie)
        self.assertEqual(status,503)
        self.assertNotIn('private',json.dumps(data))
        self.assertNotIn('message',data)


class EndpointTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.http = ThreadingHTTPServer(('127.0.0.1', 0), server.Handler)
        cls.thread = threading.Thread(target=cls.http.serve_forever)
        cls.thread.start()
        cls.port = cls.http.server_address[1]

    @classmethod
    def tearDownClass(cls):
        cls.http.shutdown(); cls.http.server_close(); cls.thread.join()

    def request(self, method, path, body=None, headers=None):
        connection = HTTPConnection('127.0.0.1', self.port, timeout=5)
        connection.request(method, path, body=body, headers=headers or {})
        response = connection.getresponse()
        result = (response.status, json.loads(response.read()), dict(response.getheaders()))
        connection.close()
        return result

    def test_proxy_source_trust(self):
        handler = object.__new__(server.Handler)
        for peer, forwarded, expected in [
            ('127.0.0.1', '192.0.2.10', '192.0.2.10'),
            ('::1', '2001:db8::1', '2001:db8::1'),
            ('192.0.2.20', '192.0.2.10', '192.0.2.20'),
            ('127.0.0.1', '192.0.2.10, 192.0.2.20', '127.0.0.1'),
        ]:
            handler.client_address = (peer, 12345)
            handler.headers = {'X-Forwarded-For': forwarded}
            self.assertEqual(handler.assessment_source(), expected)

    def test_transport_config_origin_and_session(self):
        status, data, _ = self.request('GET', '/api/assessment/status')
        self.assertEqual(status, 200); self.assertFalse(data['ready'])
        status, _, _ = self.request('POST', '/api/assessment/analyze', '{}')
        self.assertEqual(status, 503)
        headers = {'X-Forwarded-Proto': 'https', 'Origin': f'https://127.0.0.1:{self.port}', 'Content-Type': 'application/json'}
        with patch.dict('os.environ', {'BRANDYAR_METIS_API_KEY': ''}):
            status, data, _ = self.request('POST', '/api/assessment/analyze', '{}', headers)
            self.assertEqual(status, 503); self.assertEqual(set(data), {'error'})
        with patch.object(analysis, 'configured', return_value=True):
            status, data, result_headers = self.request('GET', '/api/assessment/status', headers=headers)
            self.assertTrue(data['ready'])
            cookie = result_headers['Set-Cookie']
            self.assertIn('HttpOnly; Secure; SameSite=Strict', cookie)
            status, _, _ = self.request('POST', '/api/assessment/analyze', '{}', headers)
            self.assertEqual(status, 401)
            headers['Cookie'] = cookie.split(';')[0]
            with patch.object(analysis, 'analyze', return_value=sample_report()), patch.object(server, 'connect') as connect:
                connect.return_value.__enter__.return_value = object()
                status, data, _ = self.request('POST', '/api/assessment/analyze', json.dumps(sample_answers()), headers)
                self.assertEqual(status, 200); self.assertEqual(len(data['report']['priority_actions']), 3)
            status, _, _ = self.request('POST', '/api/assessment/analyze', '{"answers":{}}', headers)
            self.assertEqual(status, 422)
            headers['Origin'] = 'https://untrusted.test'
            status, _, _ = self.request('POST', '/api/assessment/analyze', '{}', headers)
            self.assertEqual(status, 403)


if __name__ == '__main__':
    unittest.main()
