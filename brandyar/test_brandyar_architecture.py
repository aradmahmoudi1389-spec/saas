import base64
import sqlite3
import unittest
from unittest.mock import patch

import brandyar_profile as product
import personal_brand as pb
import server
from test_personal_brand import HTTPFlowTests as HTTPHarness, responses_v4


class ArchitectureTests(unittest.TestCase):
    setUp = HTTPHarness.setUp
    close = HTTPHarness.close
    call = HTTPHarness.call

    def session(self, completed=False):
        _, payload, cookie = self.call()
        csrf = payload['data']['csrf']
        if completed:
            _, data, _ = self.call('POST', '/api/personal-brand', {'csrf': csrf, 'action': 'start'}, cookie)
            assessment = data['data']['id']
            for step, answers in responses_v4().items():
                status, _, _ = self.call('POST', '/api/personal-brand', {'csrf': csrf, 'action': 'save', 'id': assessment, 'step': step, 'revision': step - 1, 'answers': answers}, cookie)
                self.assertEqual(status, 200)
            self.assertEqual(self.call('POST', '/api/personal-brand', {'csrf': csrf, 'action': 'report', 'id': assessment}, cookie)[0], 200)
        return csrf, cookie

    def post(self, csrf, cookie, **body):
        return self.call('POST', '/api/brandyar', {'csrf': csrf, **body}, cookie)

    def test_independent_documents_and_access(self):
        for route in ('/account', '/brandyar/dashboard', '/brandyar/roadmap', '/brandyar/pillars'):
            self.assertEqual(self.call(path=route)[0], 200)
        self.assertEqual(self.call(path='/brandyar/profile')[0], 303)
        account = self.call(path='/account')[1].decode()
        self.assertIn('account-mode', account)
        self.assertNotIn('main-nav', account)
        csrf, cookie = self.session()
        for action in ('identity_save', 'identity_approve', 'trial_grant', 'plan_select', 'settings_save', 'publication_save', 'ai_generate'):
            self.assertEqual(self.post(csrf, cookie, action=action)[0], 403)
        self.assertEqual(self.post('wrong', cookie, action='account_save', account={})[0], 403)
        data = self.call(path='/api/brandyar', cookie=cookie)[1]['data']
        self.assertNotIn('identity', data)
        self.assertNotIn('workspace', data)

    def test_failed_write_does_not_report_success(self):
        csrf, cookie = self.session()
        with patch.object(product, 'save_account', side_effect=sqlite3.OperationalError('fixture failure')):
            status, response, _ = self.post(csrf, cookie, action='account_save', account={'name': 'ثبت نشده'})
        self.assertEqual(status, 503)
        self.assertIn('error', response)
        self.assertNotIn('data', response)
        self.assertEqual(self.call(path='/api/brandyar', cookie=cookie)[1]['data']['account']['name'], '')
        self.assertEqual(self.post(csrf, cookie, action='account_save', account={'name': 'ثبت شده'})[0], 200)

    def test_account_persistence_isolation_and_logout(self):
        csrf, cookie = self.session()
        avatar = 'data:image/png;base64,' + base64.b64encode(b'\x89PNG\r\n\x1a\nfixture').decode()
        account = {'name': 'کاربر تست', 'email': 'user@example.test', 'phone': '09120000000', 'avatar': avatar}
        self.assertEqual(self.post(csrf, cookie, action='account_save', account=account)[0], 200)
        self.assertEqual(self.call(path='/api/brandyar', cookie=cookie)[1]['data']['account'], account)
        _, other = self.session()
        self.assertEqual(self.call(path='/api/brandyar', cookie=other)[1]['data']['account']['name'], '')
        for invalid in ({'name': []}, {'email': 'not-email'}, {'avatar': 'data:image/svg+xml;base64,AAAA'}):
            self.assertEqual(self.post(csrf, cookie, action='account_save', account=invalid)[0], 422)
        self.assertEqual(self.call(path='/api/brandyar', cookie=cookie)[1]['data']['account'], account)
        self.assertEqual(self.post(csrf, cookie, action='account_logout')[0], 200)
        self.assertFalse(self.call(path='/api/brandyar', cookie=cookie)[1]['data']['signedIn'])
        self.assertEqual(self.post(csrf, cookie, action='account_save', account={})[0], 401)

    def test_plan_settings_and_publication(self):
        csrf, cookie = self.session(completed=True)
        self.assertEqual(self.post(csrf, cookie, action='plan_select', planId='invalid')[0], 422)
        self.assertEqual(self.post(csrf, cookie, action='plan_select', planId='starter')[0], 200)
        data = self.call(path='/api/brandyar', cookie=cookie)[1]['data']
        self.assertEqual(data['access']['planId'], 'starter')
        self.assertEqual(data['access']['status'], 'none')
        self.assertFalse(data['trialUsed'])
        self.assertEqual(self.post(csrf, cookie, action='settings_save', settings={})[0], 403)
        self.assertEqual(self.post(csrf, cookie, action='trial_grant', planId='starter')[0], 200)
        preferences = {'tone': 'روشن', 'format': 'کپشن', 'length': 'کوتاه'}
        self.assertEqual(self.post(csrf, cookie, action='settings_save', settings=preferences)[0], 200)
        with server.connect() as db:
            owner = db.execute('SELECT owner_hash FROM pb_sessions').fetchone()[0]
            self.assertEqual(product.product_settings(db, owner)['selectedPlan'], 'starter')
            db.execute('INSERT INTO pb_content_items VALUES(?,?,?,?,?,?,?,?,?,?)', ('item', owner, 'عنوان', 'متن', '{}', 'user', 'draft', 0, pb.now(), pb.now()))
            db.commit()
        for status, date in [('scheduled', ''), ('scheduled', 'invalid'), ('unknown', '')]:
            self.assertEqual(self.post(csrf, cookie, action='publication_save', itemId='item', status=status, publishAt=date)[0], 422)
        status, response, _ = self.post(csrf, cookie, action='publication_save', itemId='item', status='scheduled', publishAt='2026-12-01T10:00:00Z')
        self.assertEqual(status, 200)
        self.assertEqual(response['data']['workspace']['library'][0]['status'], 'scheduled')
        self.assertEqual(self.post(csrf, cookie, action='publication_save', itemId='missing', status='ready')[0], 422)
        with server.connect() as db:
            with self.assertRaises(ValueError):
                product.save_publication(db, 'another-owner', 'item', '', 'ready')
        self.assertEqual(self.post(csrf, cookie, action='access_revoke')[0], 200)
        self.assertEqual(self.post(csrf, cookie, action='publication_save', itemId='item', status='ready')[0], 403)
        self.assertNotIn('workspace', self.call(path='/api/brandyar', cookie=cookie)[1]['data'])
        status, response, _ = self.post(csrf, cookie, action='plan_select', planId='growth')
        self.assertEqual(status, 200)
        self.assertEqual(response['data']['access']['planId'], 'growth')
        self.assertEqual(response['data']['access']['status'], 'expired')

    def test_artifact_freshness_propagates_without_deleting(self):
        with server.connect() as db:
            owner = 'fixture-owner'
            version = product.version_count(db, owner)
            voice = {'definition': 'صدا', '_identityVersion': version}
            product._store_approved(db, 'pb_brand_voice', owner, voice)
            voice_artifact = {'body': voice}
            pillars = {'pillars': [], '_identityVersion': version, '_voiceRevision': product.source_revision(voice_artifact)}
            product._store_approved(db, 'pb_content_pillars', owner, pillars)
            metadata = {'_identityVersion': version, '_voiceRevision': product.source_revision(voice_artifact), '_pillarsRevision': product.source_revision({'body': pillars})}
            db.execute('INSERT INTO pb_content_items VALUES(?,?,?,?,?,?,?,?,?,?)', ('content', owner, 'title', 'body', pb.dumps(metadata), 'ai', 'draft', 0, pb.now(), pb.now()))
            db.commit()
            self.assertFalse(product.workspace_snapshot(db, owner)['library'][0]['needsRevision'])
            product._store_approved(db, 'pb_brand_voice', owner, {**voice, 'definition': 'صدای تازه'})
            db.commit()
            snapshot = product.workspace_snapshot(db, owner)
            self.assertEqual(snapshot['contentPillars']['status'], 'needs_revision')
            self.assertTrue(snapshot['library'][0]['needsRevision'])
            self.assertEqual(snapshot['library'][0]['body'], 'body')
            with self.assertRaises(ValueError):
                product.save_publication(db, owner, 'content', '', 'ready')
            proposal = product.ai_save_output(db, owner, 'content_draft', {}, {'body': 'متن', '_identityVersion': version})
            with self.assertRaises(ValueError):
                product.ai_action(db, owner, proposal['id'], 'edit', {'_identityVersion': 99})
            with self.assertRaises(ValueError):
                product.ai_action(db, owner, proposal['id'], 'accept')


    def test_ai_approval_flow_and_stale_proposal(self):
        csrf, cookie = self.session(completed=True)
        self.assertEqual(self.post(csrf, cookie, action='trial_grant', planId='starter')[0], 200)
        identity = {'professionalRole': 'مشاور', 'industry': 'آموزش', 'professionalGoals': ['آموزش'], 'targetDescription': 'مدیران', 'needs': ['یادگیری'], 'problems': ['زمان'], 'valueProposition': 'یادگیری روشن', 'differentiators': ['تجربه']}
        self.assertEqual(self.post(csrf, cookie, action='identity_save', identity=identity, insightApproval=False)[0], 200)
        self.assertEqual(self.post(csrf, cookie, action='identity_approve')[0], 200)
        outputs = {'brand_voice': {'definition': 'روشن', 'coreTraits': ['دقیق']}, 'content_pillars': {'pillars': [{'name': 'آموزش'}]}, 'content_draft': {'title': 'عنوان', 'body': 'متن واقعی آزمون'}}
        with patch.object(server.brandyar_ai, 'generate', side_effect=lambda operation, *args: dict(outputs[operation])):
            self.assertEqual(self.post(csrf, cookie, action='ai_generate', operation='content_draft')[0], 422)
            pending = None
            for operation in ('brand_voice', 'content_pillars', 'content_draft'):
                status, response, _ = self.post(csrf, cookie, action='ai_generate', operation=operation, inputs={})
                self.assertEqual(status, 200)
                proposal = response['data']['ai']
                self.assertIn('_identityVersion', proposal['output'])
                self.assertEqual(self.post(csrf, cookie, action='ai_output_action', outputId=proposal['id'], outputAction='accept')[0], 200)
                self.assertEqual(self.post(csrf, cookie, action='ai_output_action', outputId=proposal['id'], outputAction='accept')[0], 422)
                if operation == 'content_draft':
                    _, response, _ = self.post(csrf, cookie, action='ai_generate', operation=operation, inputs={})
                    pending = response['data']['ai']['id']
        snapshot = self.call(path='/api/brandyar', cookie=cookie)[1]['data']['workspace']
        self.assertEqual(snapshot['brandVoice']['status'], 'approved')
        self.assertEqual(snapshot['contentPillars']['status'], 'approved')
        self.assertEqual(len(snapshot['library']), 1)
        self.assertFalse(snapshot['library'][0]['needsRevision'])
        self.assertTrue(any(output['id'] == pending for output in snapshot['recentOutputs']))
        self.assertEqual(self.post(csrf, cookie, action='identity_save', identity={**identity, 'professionalRole': 'مدرس'}, sections=['work'])[0], 200)
        snapshot = self.call(path='/api/brandyar', cookie=cookie)[1]['data']['workspace']
        self.assertEqual(snapshot['brandVoice']['status'], 'needs_revision')
        self.assertEqual(snapshot['contentPillars']['status'], 'needs_revision')
        self.assertTrue(snapshot['library'][0]['needsRevision'])
        self.assertEqual(self.post(csrf, cookie, action='ai_output_action', outputId=pending, outputAction='accept')[0], 422)
        self.assertEqual(len(snapshot['library']), 1)


if __name__ == '__main__':
    unittest.main()
