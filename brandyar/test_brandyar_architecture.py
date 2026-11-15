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
            self.assertNotEqual(self.post(csrf, cookie, action=action)[0], 403)
        self.assertEqual(self.post('wrong', cookie, action='account_save', account={})[0], 403)
        data = self.call(path='/api/brandyar', cookie=cookie)[1]['data']
        self.assertIn('identity', data)
        self.assertIn('workspace', data)

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
        after_logout = self.call(path='/api/brandyar', cookie=cookie)
        self.assertTrue(after_logout[1]['data']['signedIn'])
        self.assertEqual(after_logout[1]['data']['account']['name'], '')
        self.assertIn('__Host-pb=', after_logout[2])
        self.assertEqual(self.post(csrf, cookie, action='account_save', account={})[0], 403)

    def test_plan_settings_and_publication(self):
        csrf, cookie = self.session(completed=True)
        self.assertEqual(self.post(csrf, cookie, action='plan_select', planId='invalid')[0], 422)
        self.assertEqual(self.post(csrf, cookie, action='plan_select', planId='starter')[0], 200)
        data = self.call(path='/api/brandyar', cookie=cookie)[1]['data']
        self.assertEqual(data['access']['planId'], 'starter')
        self.assertEqual(data['access']['status'], 'none')
        self.assertFalse(data['trialUsed'])
        self.assertEqual(self.post(csrf, cookie, action='settings_save', settings={})[0], 200)
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
        self.assertEqual(self.post(csrf, cookie, action='publication_save', itemId='item', status='ready')[0], 200)
        self.assertIn('workspace', self.call(path='/api/brandyar', cookie=cookie)[1]['data'])
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

    def test_identity_phase_one_flow(self):
        csrf, cookie = self.session()
        # 1. Empty start: nothing is invented and approval is refused.
        data = self.call(path='/api/brandyar', cookie=cookie)[1]['data']['identity']
        self.assertEqual(data['status'], 'not_started')
        self.assertEqual(data['completionPercentage'], 0)
        self.assertEqual(data['achievements'], [])
        self.assertEqual(data['targetAudience']['obstacles'], [])
        self.assertEqual(self.post(csrf, cookie, action='identity_approve')[0], 422)
        # 2. Draft save with the new phase-one fields.
        draft = {'professionalRole': 'مشاور برند', 'industry': 'آموزش', 'achievements': ['کارگاه ۲۰ نفره'],
                 'audienceWants': ['رشد پایدار'], 'expectedResults': ['فروش روشن'], 'obstacles': ['بودجه'],
                 'workMethod': 'جلسهٔ هفتگی', 'supportingEvidence': ['نمونهٔ پروژه'], 'limitations': ['تبلیغات'],
                 'futurePath': 'کارگاه آنلاین'}
        self.assertEqual(self.post(csrf, cookie, action='identity_save', identity=draft)[0], 200)
        saved = self.call(path='/api/brandyar', cookie=cookie)[1]['data']['identity']
        self.assertEqual(saved['achievements'], ['کارگاه ۲۰ نفره'])
        self.assertEqual(saved['targetAudience']['expectedResults'], ['فروش روشن'])
        self.assertEqual(saved['workMethod'], 'جلسهٔ هفتگی')
        self.assertEqual(saved['futurePath'], 'کارگاه آنلاین')
        # 3. Reload keeps the draft (the same session reads it back).
        self.assertEqual(self.call(path='/api/brandyar', cookie=cookie)[1]['data']['identity']['professionalRole'], 'مشاور برند')
        # 4. Incomplete answers stay incomplete and cannot be approved.
        self.assertEqual(self.post(csrf, cookie, action='identity_approve')[0], 422)
        # 5. Field states: a hypothesis is stored but never auto-confirmed.
        self.assertEqual(self.post(csrf, cookie, action='identity_save', identity={**draft, 'fieldStates': {'workMethod': 'hypothesis', 'limitations': 'unknown'}})[0], 200)
        states = self.call(path='/api/brandyar', cookie=cookie)[1]['data']['identity']['fieldStates']
        self.assertEqual(states['workMethod'], 'hypothesis')
        self.assertEqual(states['limitations'], 'unknown')
        self.assertEqual(self.post(csrf, cookie, action='identity_save', identity={**draft, 'fieldStates': {'workMethod': 'bogus'}})[0], 200)
        self.assertEqual(self.call(path='/api/brandyar', cookie=cookie)[1]['data']['identity']['fieldStates']['workMethod'], 'hypothesis')
        # 6. Complete the required fields, then approve explicitly.
        full = {**draft, 'targetDescription': 'مدیران کوچک', 'problems': ['زمان'], 'valueProposition': 'مسیر روشن',
                'professionalGoals': ['آموزش']}
        self.assertEqual(self.post(csrf, cookie, action='identity_save', identity=full, insightApproval=False)[0], 200)
        self.assertEqual(self.post(csrf, cookie, action='identity_approve')[0], 200)
        approved = self.call(path='/api/brandyar', cookie=cookie)[1]['data']['identity']
        self.assertEqual(approved['status'], 'approved')
        self.assertTrue(approved['approvedAt'])
        # 7. Changing an approved part marks it for review without deleting data.
        self.assertEqual(self.post(csrf, cookie, action='identity_save', identity={**full, 'professionalRole': 'مدرس'}, sections=['work'])[0], 200)
        revised = self.call(path='/api/brandyar', cookie=cookie)[1]['data']['identity']
        self.assertEqual(revised['status'], 'needs_revision')
        self.assertEqual(revised['professionalRole'], 'مدرس')
        self.assertEqual(revised['achievements'], ['کارگاه ۲۰ نفره'])

    def test_identity_ai_operations_and_errors(self):
        csrf, cookie = self.session()
        identity = {'professionalRole': 'مشاور', 'industry': 'آموزش', 'targetDescription': 'مدیران',
                    'problems': ['زمان'], 'valueProposition': 'مسیر روشن', 'professionalGoals': ['آموزش']}
        self.assertEqual(self.post(csrf, cookie, action='identity_save', identity=identity, insightApproval=False)[0], 200)
        outputs = {
            'identity_discovery': {'summary': 'پاسخ‌ها روشن است', 'nextQuestion': 'چه نمونه‌ای داری؟', 'confirmedFacts': ['نقش']},
            'identity_analysis': {'summary': 'تحلیل', 'strengths': ['وضوح'], 'contradictions': ['زمان و بودجه'], 'recommendations': ['نمونه اضافه کن']},
            'identity_questions': {'followUpQuestions': [{'question': 'نمونه؟', 'why': 'اثبات', 'priority': 1}], 'enoughInformation': False},
            'identity_synthesis': {'professionalIdentity': 'مشاور آموزشی', 'valueProposition': 'مسیر روشن', 'confidence': 'medium', 'hypotheses': ['مخاطب مدیر است']},
            'identity_consistency_check': {'consistent': False, 'contradictions': ['زمان'], 'summary': 'یک تناقض'},
        }
        with patch.object(server.brandyar_ai, 'generate', side_effect=lambda operation, *args: dict(outputs[operation])):
            for operation in outputs:
                status, response, _ = self.post(csrf, cookie, action='ai_generate', operation=operation, inputs={})
                self.assertEqual(status, 200, operation)
                self.assertEqual(response['data']['ai']['operation'], operation)
            # 8. Rejecting a proposal keeps it out of the identity.
            _, response, _ = self.post(csrf, cookie, action='ai_generate', operation='identity_synthesis', inputs={})
            proposal = response['data']['ai']['id']
            self.assertEqual(self.post(csrf, cookie, action='ai_output_action', outputId=proposal, outputAction='reject')[0], 200)
            self.assertEqual(self.call(path='/api/brandyar', cookie=cookie)[1]['data']['identity']['professionalRole'], 'مشاور')
            # 9. Editing a proposal is allowed and does not touch the identity.
            _, response, _ = self.post(csrf, cookie, action='ai_generate', operation='identity_synthesis', inputs={})
            proposal = response['data']['ai']['id']
            self.assertEqual(self.post(csrf, cookie, action='ai_output_action', outputId=proposal, outputAction='edit', edited={'positioningStatement': 'نسخهٔ ویرایش‌شده'})[0], 200)
            self.assertEqual(self.call(path='/api/brandyar', cookie=cookie)[1]['data']['identity']['positioningStatement'], '')
        # 10. AI service failure becomes a readable error, not a crash.
        with patch.object(server.brandyar_ai, 'generate', side_effect=server.brandyar_ai.AIResponseError('x')):
            status, response, _ = self.post(csrf, cookie, action='ai_generate', operation='identity_analysis', inputs={})
            self.assertEqual(status, 503)
            self.assertIn('error', response)
        with patch.object(server.brandyar_ai, 'generate', side_effect=server.brandyar_ai.AIUnavailable()):
            self.assertEqual(self.post(csrf, cookie, action='ai_generate', operation='identity_analysis', inputs={})[0], 503)
        # 11. Storage failure keeps the previous identity intact.
        with patch.object(product, 'save', side_effect=sqlite3.OperationalError('fixture failure')):
            self.assertEqual(self.post(csrf, cookie, action='identity_save', identity={**identity, 'professionalRole': 'تازه'})[0], 503)
        self.assertEqual(self.call(path='/api/brandyar', cookie=cookie)[1]['data']['identity']['professionalRole'], 'مشاور')
        # 12. Unknown operations are refused.
        self.assertEqual(self.post(csrf, cookie, action='ai_generate', operation='identity_unknown', inputs={})[0], 422)

    def test_identity_legacy_data_is_preserved(self):
        csrf, cookie = self.session()
        legacy = {'professionalRole': 'قدیمی', 'industry': 'آموزش', 'skills': ['تدریس'], 'targetDescription': 'دانشجو',
                  'problems': ['تمرکز'], 'valueProposition': 'یادگیری', 'professionalGoals': ['رشد']}
        self.assertEqual(self.post(csrf, cookie, action='identity_save', identity=legacy, insightApproval=False)[0], 200)
        self.assertEqual(self.post(csrf, cookie, action='identity_save', identity={'achievements': ['نمونه']})[0], 200)
        saved = self.call(path='/api/brandyar', cookie=cookie)[1]['data']['identity']
        self.assertEqual(saved['professionalRole'], 'قدیمی')
        self.assertEqual(saved['skills'], ['تدریس'])
        self.assertEqual(saved['achievements'], ['نمونه'])
        self.assertEqual(saved['targetAudience']['problems'], ['تمرکز'])
        self.assertEqual(saved['targetAudience']['obstacles'], [])


    def test_ai_readers_get_plain_content(self):
        status, robots, _ = self.call(path='/robots.txt')
        self.assertEqual(status, 200)
        self.assertIn(b'Sitemap: https://nesharo.ir/sitemap.xml', robots)
        self.assertIn(b'User-agent: GPTBot', robots)
        self.assertIn(b'User-agent: ClaudeBot', robots)
        self.assertNotIn(b'Disallow: /brandyar', robots)
        status, sitemap, _ = self.call(path='/sitemap.xml')
        self.assertEqual(status, 200)
        self.assertIn(b'https://nesharo.ir/brandyar/dashboard', sitemap)
        for route in ('/brandyar.md', '/llms.txt', '/brandyar/dashboard.md'):
            status, body, _ = self.call(path=route)
            self.assertEqual(status, 200)
            text = body.decode()
            self.assertIn('برندی‌یار', text)
            self.assertIn('https://nesharo.ir/brandyar/start', text)
            self.assertNotIn('<script', text)
        status, page, _ = self.call(path='/brandyar/dashboard')
        self.assertEqual(status, 200)
        self.assertIn('برندی‌یار', page.decode())
        self.assertIn('index,follow', page.decode())


if __name__ == '__main__':
    unittest.main()
