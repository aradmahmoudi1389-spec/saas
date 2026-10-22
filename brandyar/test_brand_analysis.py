import json
import sqlite3
import tempfile
import threading
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
