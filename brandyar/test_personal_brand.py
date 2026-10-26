import copy
import json
import sqlite3
import tempfile
import threading
import unittest
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from urllib.parse import parse_qs, urlencode, urlsplit

import personal_brand as pb
import personal_brand_instagram as ig
import personal_brand_model as model
import server


def responses(value=3):
    body = model.template()
    return {
        1: {**{k: 'متن آزمایشی' if required else '' for k, _, required in body['base']}, 'goal': body['goals'][0]},
        2: {k: 'پاسخ آزمایشی' if required else '' for k, _, required in body['identity']},
        3: {q['id']: value for q in body['items']},
        4: {},
        5: {'choice': 'skip'},
    }


class ModelTests(unittest.TestCase):
    def test_score_extremes_and_stages(self):
        for value, total, stage in [(1, 0, 'کشف'), (2, 25, 'تعریف'), (3, 50, 'تثبیت'), (4, 75, 'تمایز'), (5, 100, 'مرجعیت')]:
            with self.subTest(value=value):
                report = model.score(responses(value), model.template(), model.model())
                self.assertEqual(report['total'], total)
                self.assertEqual(report['stage'], stage)
                self.assertEqual(len(report['dimensions']), 6)
                self.assertEqual(len(report['immediate']), 3)
                self.assertEqual(report['confidence'], 'خوداظهاری')

    def test_weights_and_evidence_do_not_inflate_scores(self):
        answers = responses(1)
        for key in answers[3]:
            if key.startswith('identity_'):
                answers[3][key] = 5
        scoring = model.model()
        scoring['dimensions'] = {key: .1 for key in scoring['dimensions']}
        scoring['dimensions']['identity'] = .5
        report = model.score(answers, model.template(), scoring)
        self.assertEqual(report['total'], 50)
        answers[4]['proof'] = 'شرح نمونه‌کار؛ نه تأیید مستقل'
        enriched = model.score(answers, model.template(), scoring)
        self.assertEqual(enriched['total'], 50)
        self.assertEqual(enriched['confidence'], 'خوداظهاری به‌همراه شواهد')

    def test_invalid_answers(self):
        for answers in [{}, {'unknown': 3}, {**responses()[3], 'identity_1': True}, {**responses()[3], 'identity_1': 6}]:
            with self.subTest(answers=list(answers)), self.assertRaises(ValueError):
                model.validate_step(3, answers, model.template())
        for value in ['a' * 1201, '\x00']:
            with self.assertRaises(ValueError):
                model.clean(value)
        for link in ['http://example.test', 'javascript:alert(1)', 'https://user:pass@example.test']:
            with self.assertRaises(ValueError):
                model.validate_step(4, {'portfolio_url': link}, model.template())
        self.assertEqual(model.validate_step(5, {'choice': 'connected', 'introduction': 'ignored'}, model.template())['introduction'], '')

    def test_version_validation(self):
        body = json.loads(pb.dumps(model.template()))
        model.validate_template(body)
        body['items'][0]['title'] = 'سؤال اصلاح‌شده'
        model.validate_template(body)
        body['items'][0]['dimension'] = 'growth'
        with self.assertRaises(ValueError):
            model.validate_template(body)
        for weight in [True, -1, float('nan'), float('inf')]:
            scoring = model.model()
            scoring['dimensions']['identity'] = weight
            with self.assertRaises(ValueError):
                model.validate_model(scoring)


class StorageTests(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(':memory:')
        self.db.row_factory = sqlite3.Row
        self.db.execute('PRAGMA foreign_keys=ON')
        self.db.execute('CREATE TABLE staff(id INTEGER PRIMARY KEY)')
        self.db.execute('INSERT INTO staff VALUES(1)')
        pb.initialize(self.db)
        self.owner = 'test-owner'
        self.db.execute('INSERT INTO pb_sessions VALUES(?,?,?,?)', (self.owner, 'test-csrf', pb.now(), pb.now() + 86400))
        self.db.commit()
        self.staff = {'role': 'owner', 'staff_id': 1}
        self.addCleanup(self.db.close)

    def complete(self, values=None):
        identity = pb.mutate(self.db, self.owner, {'action': 'start'})['id']
        for step, answers in (values or responses()).items():
            pb.mutate(self.db, self.owner, {'action': 'save', 'id': identity, 'step': step, 'revision': step - 1, 'answers': answers, 'elapsed_ms': 1500})
        result = pb.mutate(self.db, self.owner, {'action': 'report', 'id': identity})['report']
        self.db.commit()
        return identity, result

    def test_idempotent_migration_and_report(self):
        pb.initialize(self.db)
        self.assertEqual(self.db.execute('SELECT count(*) FROM pb_questions').fetchone()[0], 18)
        identity, report = self.complete()
        again = pb.mutate(self.db, self.owner, {'action': 'report', 'id': identity})['report']
        self.assertEqual(again, report)
        self.assertEqual(self.db.execute('SELECT count(*) FROM pb_report_versions').fetchone()[0], 1)
        self.assertEqual(self.db.execute('PRAGMA foreign_key_check').fetchall(), [])

    def test_ownership_and_optimistic_revision(self):
        identity = pb.mutate(self.db, self.owner, {'action': 'start'})['id']
        with self.assertRaises(LookupError):
            pb.owned(self.db, identity, 'other-owner')
        with self.assertRaises(ValueError):
            pb.mutate(self.db, self.owner, {'action': 'save', 'id': identity, 'step': 1, 'revision': 9, 'answers': responses()[1]})
        with self.assertRaises(ValueError):
            pb.mutate(self.db, self.owner, {'action': 'report', 'id': identity})

    def test_report_immutable_and_reanalysis_uses_new_model(self):
        identity, first = self.complete()
        body = model.model()
        body['dimensions'] = {key: .1 for key in body['dimensions']}
        body['dimensions']['identity'] = .5
        pb.admin_mutate(self.db, self.staff, {'action': 'model_draft', 'body': body, 'confirmed': True, 'reason': 'آزمایش وزن تازه'})
        selected = self.db.execute('SELECT id FROM pb_scoring_models WHERE version=2').fetchone()[0]
        pb.admin_mutate(self.db, self.staff, {'action': 'model_publish', 'id': selected, 'confirmed': True, 'reason': 'انتشار آزمایشی'})
        pb.admin_mutate(self.db, self.staff, {'action': 'regenerate', 'id': identity, 'scoring_version': selected, 'confirmed': True, 'reason': 'مقایسهٔ مدل‌ها'})
        data = pb.assessment_data(self.db, pb.owned(self.db, identity, self.owner))
        self.assertEqual(len(data['reports']), 2)
        self.assertEqual(data['reports'][1]['body'], first)
        self.assertEqual(data['reports'][0]['scoring_version'], selected)
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute("UPDATE pb_report_versions SET body='{}'")
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute("UPDATE pb_template_versions SET body='{}' WHERE id='pb-test-1'")

    def test_admin_permissions_and_audit(self):
        identity, _ = self.complete()
        analyst = {'role': 'analyst', 'staff_id': 1}
        data = pb.admin_read(self.db, analyst, {})
        self.assertFalse(data['permissions']['private'])
        self.assertEqual(data['connections'], [])
        with self.assertRaises(PermissionError):
            pb.admin_read(self.db, analyst, {'id': [identity]})
        with self.assertRaises(PermissionError):
            pb.admin_mutate(self.db, analyst, {'action': 'privacy', 'reason': 'test', 'confirmed': True, 'retention_days': 10})
        with self.assertRaises(ValueError):
            pb.admin_mutate(self.db, self.staff, {'action': 'archive', 'id': identity, 'reason': 'test'})
        self.assertGreater(self.db.execute('SELECT count(*) FROM pb_audit').fetchone()[0], 0)
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute('DELETE FROM pb_audit')

    def test_deletion_and_disconnect(self):
        identity, _ = self.complete()
        pb.mutate(self.db, self.owner, {'action': 'delete_instagram'})
        self.assertEqual(self.db.execute('SELECT count(*) FROM pb_report_versions').fetchone()[0], 1)
        pb.mutate(self.db, self.owner, {'action': 'disconnect'})
        result = pb.mutate(self.db, self.owner, {'action': 'delete_assessment', 'id': identity})
        self.assertEqual(result['status'], 'completed')
        for table in ('pb_assessments', 'pb_answers', 'pb_scores', 'pb_reports', 'pb_report_versions', 'pb_evidence', 'pb_recommendations'):
            self.assertEqual(self.db.execute('SELECT count(*) FROM ' + table).fetchone()[0], 0)

    def test_event_idempotency(self):
        for _ in range(2):
            pb.event(self.db, self.owner, None, 'test', 'same')
        self.assertEqual(self.db.execute("SELECT count(*) FROM pb_events WHERE event='test'").fetchone()[0], 1)

    def test_start_rate_limit(self):
        for _ in range(10):
            pb.mutate(self.db, self.owner, {'action': 'start'})
        with self.assertRaises(ValueError):
            pb.mutate(self.db, self.owner, {'action': 'start'})

    def test_filters_export_and_question_times(self):
        identity, _ = self.complete()
        data = pb.admin_read(self.db, self.staff, {'state': ['completed'], 'maturity': ['تثبیت'], 'confidence': ['خوداظهاری'], 'connected': ['no']})
        self.assertEqual(data['total'], 1)
        self.assertEqual(pb.admin_read(self.db, self.staff, {'maturity': ['مرجعیت']})['total'], 0)
        exported = pb.admin_read(self.db, self.staff, {'action': ['validation_export']})
        self.assertEqual(exported['responses'], [responses()[3]])
        self.assertNotIn(identity, pb.dumps(exported))
        self.assertNotIn(self.owner, pb.dumps(exported))
        self.assertEqual(pb.mutate(self.db, self.owner, {'action': 'export_report', 'id': identity})['report']['total'], 50)
        analyst = {'role': 'analyst', 'staff_id': 1}
        with self.assertRaises(PermissionError):
            pb.admin_read(self.db, analyst, {'action': ['validation_export']})
        draft = pb.mutate(self.db, self.owner, {'action': 'start'})['id']
        pb.mutate(self.db, self.owner, {'action': 'save', 'id': draft, 'revision': 0, 'step': 3, 'answers': responses()[3], 'question_times': {'identity_1': 1500}})
        self.assertEqual(self.db.execute('SELECT elapsed_ms FROM pb_question_metrics').fetchone()[0], 1500)

    def test_rollback_guard(self):
        import personal_brand_maintenance as maintenance
        self.db.commit()
        maintenance.rollback(self.db)
        self.assertFalse(self.db.execute("SELECT 1 FROM sqlite_master WHERE name='pb_assessments'").fetchone())
        pb.initialize(self.db)
        self.db.execute('INSERT INTO pb_sessions VALUES(?,?,?,?)', (self.owner, 'test-csrf', pb.now(), pb.now()+86400))
        self.complete()
        with self.assertRaises(ValueError):
            maintenance.rollback(self.db)

    def test_retention_and_expiry(self):
        self.db.execute('INSERT INTO pb_instagram_connections VALUES(?,?,?,?,?,?,?,?,?,?,?,?)', ('c', self.owner, '123', 'test', b'cipher', 'basic', pb.now(), pb.now()-1, 'connected', None, None, pb.now()))
        self.db.execute('INSERT INTO pb_instagram_profiles VALUES(?,?,?,?)', ('p', 'c', '{}', pb.now()-31*86400))
        pb.maintenance(self.db)
        row = self.db.execute('SELECT * FROM pb_instagram_connections').fetchone()
        self.assertEqual(row['status'], 'expired')
        self.assertIsNone(row['token_cipher'])
        self.assertEqual(self.db.execute('SELECT count(*) FROM pb_instagram_profiles').fetchone()[0], 0)


class OAuthTests(StorageTests):
    def setUp(self):
        super().setUp()
        from cryptography.fernet import Fernet
        self.environment = patch.dict(ig.os.environ, {'PB_TOKEN_ENCRYPTION_KEY': Fernet.generate_key().decode(), 'META_INSTAGRAM_APP_ID': 'test-id', 'META_INSTAGRAM_APP_SECRET': 'test-only', 'META_INSTAGRAM_REDIRECT_URI': 'https://example.test/api/personal-brand/instagram/callback', 'META_GRAPH_VERSION': 'v25.0'})
        self.environment.start()
        self.addCleanup(self.environment.stop)
        self.handler = SimpleNamespace(headers={}, path='', respond=lambda *a, **kw: setattr(self, 'response', (a, kw)))
        self.principal = patch.object(pb, 'session', return_value={'owner_hash': self.owner})
        self.principal.start()
        self.addCleanup(self.principal.stop)

    def grant(self, **extra):
        url = ig.begin(self.db, self.owner, {'consent': True})['authorization_url']
        state = parse_qs(urlsplit(url).query)['state'][0]
        self.handler.path = '/api/personal-brand/instagram/callback?' + urlencode({'state': state, 'code': 'test-code', **extra})
        return state

    def callback(self):
        ig.callback(self.handler, lambda: self.db)
        return self.response[1]['headers']['Location']

    def connect_instagram(self):
        self.grant()
        with patch.object(ig, 'request', return_value={'access_token': 'test-only-provider-value', 'user_id': '123', 'expires_in': 3600}), patch.object(ig, 'graph', return_value={'user_id': '123', 'username': 'test-account', 'account_type': 'BUSINESS'}):
            self.assertIn('connected', self.callback())
        return pb.active_connection(self.db, self.owner)

    def test_oauth_state_replay_and_no_public_secret(self):
        row = self.connect_instagram()
        self.assertNotEqual(row['token_cipher'], b'test-only-provider-value')
        self.assertNotIn('token', pb.dumps(pb.public_connection(row)))
        self.assertIn('failed', self.callback())

    def test_wrong_state_expired_and_cancelled(self):
        self.grant()
        self.handler.path = '/api/personal-brand/instagram/callback?state=wrong&code=test'
        with patch.object(ig, 'request') as exchange:
            self.assertIn('failed', self.callback())
            exchange.assert_not_called()
        self.grant(error='access_denied')
        self.assertIn('cancelled', self.callback())
        self.grant()
        self.db.execute('UPDATE pb_oauth_states SET expires=0')
        self.db.commit()
        self.assertIn('failed', self.callback())

    def test_personal_account_and_identity_mismatch_rejected(self):
        for profile in [{'user_id': '123', 'username': 'test', 'account_type': 'PERSONAL'}, {'user_id': '456', 'username': 'test', 'account_type': 'BUSINESS'}]:
            self.grant()
            with patch.object(ig, 'request', return_value={'access_token': 'test-only', 'user_id': '123'}), patch.object(ig, 'graph', return_value=profile):
                self.assertIn('failed', self.callback())
        self.assertIsNone(pb.active_connection(self.db, self.owner))

    def test_sync_failure_preserves_snapshot_disconnect_deletion(self):
        row = self.connect_instagram()
        def graph(path, fields, token, limit=None):
            if path == 'me/media':
                return {'data': [{'id': 'm1', 'caption': 'ذخیره کنید #آموزش', 'media_type': 'IMAGE', 'timestamp': '2026-10-26T00:00:00+0000'}]}
            return {'user_id': '123', 'username': 'test-account', 'account_type': 'BUSINESS', 'biography': 'معرفی واقعی نمونهٔ تست', 'name': 'تست', 'website': '', 'unexpected_provider_field': 'must-not-be-published'}
        with patch.object(ig, 'graph', side_effect=graph):
            result = ig.sync(self.db, self.owner)
        self.assertEqual(result['observations']['sample_size'], 1)
        self.assertEqual(result['observations']['possible_cta_count'], 1)
        self.db.execute('UPDATE pb_instagram_sync_jobs SET created_at=0')
        self.db.commit()
        with patch.object(ig, 'graph', side_effect=ig.Unavailable), self.assertRaises(ig.Unavailable):
            ig.sync(self.db, self.owner)
        self.assertEqual(self.db.execute('SELECT count(*) FROM pb_instagram_profiles').fetchone()[0], 1)
        values = responses()
        values[5] = {'choice': 'connected'}
        identity, report = self.complete(values)
        self.assertIsNotNone(report['instagram'])
        self.assertNotIn('must-not-be-published', pb.dumps(report))
        self.assertNotIn('user_id', report['instagram']['profile'])
        pb.mutate(self.db, self.owner, {'action': 'disconnect'})
        self.assertIsNone(self.db.execute('SELECT token_cipher FROM pb_instagram_connections WHERE id=?', (row['id'],)).fetchone()[0])
        pb.mutate(self.db, self.owner, {'action': 'delete_instagram'})
        self.assertEqual(self.db.execute('SELECT count(*) FROM pb_instagram_profiles').fetchone()[0], 0)
        self.assertEqual(self.db.execute('SELECT count(*) FROM pb_report_versions').fetchone()[0], 0)
        with self.assertRaises(ValueError):
            pb.mutate(self.db, self.owner, {'action': 'report', 'id': identity})

    def test_disabled_and_malformed_configuration(self):
        with patch.dict(ig.os.environ, {'META_INSTAGRAM_REDIRECT_URI': 'https://['}):
            self.assertFalse(ig.configured())
        with patch.dict(ig.os.environ, {'META_INSTAGRAM_APP_ID': ''}):
            self.assertFalse(ig.configured())
            with self.assertRaises(ig.Unavailable):
                ig.begin(self.db, self.owner, {'consent': True})
        with self.assertRaises(ValueError):
            ig.begin(self.db, self.owner, {'consent': False})

    def test_wrong_owner_and_revoked_consent(self):
        self.grant()
        with patch.object(pb, 'session', return_value={'owner_hash': 'other-owner'}), patch.object(ig, 'request') as exchange:
            self.assertIn('failed', self.callback())
            exchange.assert_not_called()
        self.grant()
        def exchange(*args, **kwargs):
            pb.mutate(self.db, self.owner, {'action': 'disconnect'})
            self.db.commit()
            return {'access_token': 'test-only', 'user_id': '123'}
        with patch.object(ig, 'request', side_effect=exchange), patch.object(ig, 'graph', return_value={'user_id': '123', 'username': 'test', 'account_type': 'BUSINESS'}):
            self.assertIn('failed', self.callback())
        self.assertIsNone(pb.active_connection(self.db, self.owner))

    def test_expired_connection_does_not_call_provider(self):
        self.connect_instagram()
        self.db.execute('UPDATE pb_instagram_connections SET expires_at=0')
        self.db.commit()
        with patch.object(ig, 'graph') as graph, self.assertRaises(ig.Unavailable):
            ig.sync(self.db, self.owner)
        graph.assert_not_called()


class HTTPFlowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=Path(__file__).parent)
        self.addCleanup(self.temp.cleanup)
        setting = patch.object(server, 'DB', Path(self.temp.name) / 'test.sqlite')
        setting.start()
        self.addCleanup(setting.stop)
        with server.connect():
            pass
        self.http = ThreadingHTTPServer(('127.0.0.1', 0), server.Handler)
        self.thread = threading.Thread(target=self.http.serve_forever)
        self.thread.start()
        self.addCleanup(self.close)

    def close(self):
        self.http.shutdown()
        self.thread.join(timeout=5)
        self.http.server_close()

    def call(self, method='GET', path='/api/personal-brand?action=bootstrap', data=None, cookie='', origin='https://example.test'):
        client = HTTPConnection('127.0.0.1', self.http.server_port, timeout=10)
        headers = {'Host': 'example.test', 'X-Forwarded-Proto': 'https', 'Origin': origin, 'Content-Type': 'application/json', 'Cookie': cookie}
        client.request(method, path, body=pb.dumps(data).encode() if data is not None else None, headers=headers)
        response = client.getresponse()
        raw = response.read()
        content = json.loads(raw) if 'application/json' in response.getheader('Content-Type', '') else raw
        result = response.status, content, response.getheader('Set-Cookie', '').split(';')[0]
        client.close()
        return result

    def test_public_session_network_throttle(self):
        for _ in range(30):
            self.assertEqual(self.call()[0], 200)
        self.assertEqual(self.call()[0], 429)

    def test_admin_http_permissions(self):
        test_cookie = '0' * 64
        with server.connect() as db:
            db.execute("INSERT INTO staff VALUES(1,'test@example.test','عضو تست','analyst',X'00',X'00','test')")
            db.execute('INSERT INTO sessions VALUES(?,?,?,?,?,?,?)', (pb.digest(test_cookie), 1, 'test-csrf', 1, pb.now(), pb.now(), pb.now()+3600))
        cookie = 'brandysid=' + test_cookie
        self.assertEqual(self.call(path='/api/admin/personal-brand', cookie=cookie)[0], 200)
        self.assertEqual(self.call('POST', '/api/admin/personal-brand', {'csrf': 'test-csrf', 'action': 'privacy', 'confirmed': True, 'reason': 'test', 'retention_days': 5}, cookie)[0], 403)
        with server.connect() as db:
            db.execute("UPDATE staff SET role='owner' WHERE id=1")
        self.assertEqual(self.call('POST', '/api/admin/personal-brand', {'csrf': 'test-csrf', 'action': 'privacy', 'confirmed': True, 'reason': 'تغییر تست', 'retention_days': 5}, cookie)[0], 200)

    def test_complete_api_flow_csrf_idor_and_admin_denial(self):
        status, payload, cookie = self.call()
        self.assertEqual(status, 200)
        csrf = payload['data']['csrf']
        self.assertFalse(payload['data']['assessments'])
        def post(**body):
            return self.call('POST', '/api/personal-brand', {'csrf': csrf, **body}, cookie)[0:2]
        self.assertEqual(self.call('POST', '/api/personal-brand', {'csrf': csrf, 'action': 'start'}, cookie, 'https://other.test')[0], 403)
        self.assertEqual(self.call('POST', '/api/personal-brand', {'csrf': 'wrong', 'action': 'start'}, cookie)[0], 403)
        status, data = post(action='start')
        self.assertEqual(status, 200)
        identity = data['data']['id']
        for step, answers in responses().items():
            status, _ = post(action='save', id=identity, step=step, revision=step-1, answers=answers, elapsed_ms=1000)
            self.assertEqual(status, 200)
        status, report = post(action='report', id=identity)
        self.assertEqual(status, 200)
        self.assertEqual(report['data']['report']['total'], 50)
        _, _, other_cookie = self.call()
        self.assertEqual(self.call(path='/api/personal-brand?id='+identity, cookie=other_cookie)[0], 404)
        self.assertEqual(self.call(path='/api/admin/personal-brand')[0], 401)
        self.assertEqual(self.call(path='/personal-brand')[0], 200)
        self.assertEqual(post(action='delete_assessment', id=identity)[0], 200)
        self.assertEqual(self.call(path='/api/personal-brand?id='+identity, cookie=cookie)[0], 404)


class StatisticsTests(unittest.TestCase):
    def test_descriptive_statistics_and_degenerate_data(self):
        import personal_brand_validation as validation
        items = model.template()['items']
        self.assertEqual(validation.summarize([], items)['sample_size'], 0)
        rows = [responses(value)[3] for value in range(1, 6)]
        result = validation.summarize(rows, items)
        self.assertTrue(all(row['alpha'] == 1 for row in result['internal_consistency']))
        self.assertTrue(all(row['value'] == 1 for row in result['correlations']))
        constant = validation.summarize([responses()[3] for _ in range(5)], items)
        self.assertTrue(all(row['alpha'] is None for row in constant['internal_consistency']))
        self.assertTrue(all(row['value'] is None for row in constant['correlations']))


if __name__ == '__main__':
    unittest.main()
