import json
import sqlite3
import unittest
from unittest.mock import patch

import personal_brand as pb
import personal_brand_report as reports
import server
import test_brandyar_architecture as harness


class FullReportTests(unittest.TestCase):
    setUp = harness.ArchitectureTests.setUp
    close = harness.ArchitectureTests.close
    call = harness.ArchitectureTests.call
    session = harness.ArchitectureTests.session

    def completed(self):
        csrf, cookie = self.session(completed=True)
        identity = self.call(cookie=cookie)[1]['data']['assessments'][0]['id']
        return csrf, cookie, identity

    def post(self, csrf, cookie, identity, action, **data):
        return self.call('POST', '/api/personal-brand', {'csrf': csrf, 'id': identity, 'action': action, **data}, cookie)

    def test_phone_gate_cache_evidence_and_initial_result_preserved(self):
        csrf, cookie, identity = self.completed()
        initial = self.call(path='/api/personal-brand?id=' + identity, cookie=cookie)[1]['data']
        self.assertFalse(initial['report_flow']['phoneRegistered'])
        self.assertEqual(self.post(csrf, cookie, identity, 'full_report')[0], 403)
        self.assertEqual(self.call(path='/api/personal-brand?action=full_report&id=' + identity, cookie=cookie)[0], 403)
        for invalid in ('invalid', '0912', '+00989121234567', '0912+1234567'):
            self.assertEqual(self.post(csrf, cookie, identity, 'unlock_report', phone=invalid, consent=True)[0], 422)
        self.assertEqual(self.post('wrong', cookie, identity, 'unlock_report', phone='09121234567', consent=True)[0], 403)
        self.assertEqual(self.post(csrf, cookie, identity, 'unlock_report', phone='۰۹۱۲–۱۲۳ ۴۵۶۷', consent=True)[0], 200)
        status, data, _ = self.post(csrf, cookie, identity, 'full_report')
        self.assertEqual(status, 200)
        full = data['data']['report']
        self.assertEqual(full['summary'], initial['reports'][0]['body']['summary'])
        self.assertEqual([d['score'] for d in full['dimensions']], [d['score'] for d in initial['reports'][0]['body']['dimensions']])
        self.assertEqual(len(full['priorities']), 3)
        self.assertTrue(all(len(d['evidence']) == 3 for d in full['dimensions']))
        self.assertNotIn('09121234567', json.dumps(full))
        with patch.object(reports, 'build', side_effect=AssertionError('Report must be cached')):
            self.assertEqual(self.post(csrf, cookie, identity, 'full_report')[1]['data']['report'], full)
            self.assertEqual(self.call(path='/api/personal-brand?action=full_report&id=' + identity, cookie=cookie)[1]['data']['report'], full)
        again = self.call(path='/api/personal-brand?id=' + identity, cookie=cookie)[1]['data']
        self.assertEqual(again['reports'], initial['reports'])
        self.assertEqual(again['answers'], initial['answers'])
        self.assertTrue(again['report_flow']['phoneRegistered'])
        self.assertFalse(data['data']['offer']['hasAccess'])
        self.assertIsNone(data['data']['offer']['discount'])
        self.assertFalse(data['data']['offer']['checkoutAvailable'])
        self.assertEqual(self.call(path='/api/brandyar', cookie=cookie)[1]['data']['access']['status'], 'none')
        with server.connect() as db:
            self.assertEqual(db.execute('SELECT phone FROM pb_leads WHERE assessment_id=?', (identity,)).fetchone()[0], '09121234567')
            self.assertEqual(db.execute('SELECT count(*) FROM pb_full_reports').fetchone()[0], 1)
            events = db.execute('SELECT context_json FROM pb_events').fetchall()
            self.assertTrue(all('09121234567' not in row[0] for row in events))

    def test_owner_isolation_saved_phone_and_active_product(self):
        csrf, cookie, identity = self.completed()
        other_csrf, other_cookie, other_id = self.completed()
        self.assertEqual(self.call('POST', '/api/account', {'csrf': csrf, 'action': 'account_save', 'account': {'name': 'کاربر', 'phone': '+98 912 123 4567'}}, cookie)[0], 200)
        metadata = self.call(path='/api/personal-brand?id=' + identity, cookie=cookie)[1]['data']['report_flow']
        self.assertEqual(metadata['savedPhoneMasked'], '0912•••••67')
        self.assertNotIn('09121234567', json.dumps(metadata))
        self.assertEqual(self.post(csrf, cookie, identity, 'unlock_report', use_saved_phone=True, consent=True)[0], 200)
        self.assertEqual(self.post(other_csrf, other_cookie, identity, 'full_report')[0], 404)
        self.assertEqual(self.post(other_csrf, other_cookie, other_id, 'unlock_report', phone='09121234567', consent=True)[0], 200)
        self.assertEqual(self.post(other_csrf, other_cookie, identity, 'unlock_report', phone='09121234567', consent=True)[0], 404)
        self.assertEqual(self.call('POST', '/api/brandyar', {'csrf': csrf, 'action': 'trial_grant', 'planId': 'starter'}, cookie)[0], 200)
        offer = self.post(csrf, cookie, identity, 'full_report')[1]['data']['offer']
        self.assertTrue(offer['hasAccess'])
        self.assertEqual(offer['href'], '/brandyar/dashboard')
        other_report = self.post(other_csrf, other_cookie, other_id, 'full_report')[1]['data']['report']
        own_report = self.post(csrf, cookie, identity, 'full_report')[1]['data']['report']
        self.assertNotEqual(other_report['sourceVersion'], own_report['sourceVersion'])

    def test_failed_registration_and_generation_preserve_answers(self):
        csrf, cookie, identity = self.completed()
        before = self.call(path='/api/personal-brand?id=' + identity, cookie=cookie)[1]['data']
        with patch.object(pb, 'normalize_phone', side_effect=sqlite3.OperationalError('fixture')):
            self.assertEqual(self.post(csrf, cookie, identity, 'unlock_report', phone='09121234567', consent=True)[0], 503)
        self.assertEqual(self.post(csrf, cookie, identity, 'full_report')[0], 403)
        self.post(csrf, cookie, identity, 'unlock_report', phone='09121234567', consent=True)
        with patch.object(reports, 'build', side_effect=ValueError('fixture')):
            self.assertEqual(self.post(csrf, cookie, identity, 'full_report')[0], 422)
        after = self.call(path='/api/personal-brand?id=' + identity, cookie=cookie)[1]['data']
        self.assertEqual(after['answers'], before['answers'])
        self.assertEqual(after['reports'], before['reports'])
        self.assertEqual(self.post(csrf, cookie, identity, 'full_report')[0], 200)
        with server.connect() as db:
            pb.initialize(db)
            self.assertEqual(db.execute('SELECT count(*) FROM pb_schema_migrations WHERE version=5').fetchone()[0], 1)


if __name__ == '__main__':
    unittest.main()
