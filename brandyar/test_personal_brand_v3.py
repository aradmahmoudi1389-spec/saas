import copy
import json
import sqlite3
import unittest

import personal_brand as pb
import personal_brand_model as model
from test_personal_brand import HTTPFlowTests as BaseHTTP, responses_v3


class VersionThreeTests(unittest.TestCase):
    def test_expert_review_rubric_is_validated_and_audited(self):
        with sqlite3.connect(':memory:') as db:
            db.row_factory = sqlite3.Row
            db.execute('PRAGMA foreign_keys=ON')
            db.execute('CREATE TABLE staff(id INTEGER PRIMARY KEY)')
            db.execute('INSERT INTO staff VALUES(1)')
            pb.initialize(db)
            review = {'action': 'feedback', 'id': 'pb-test-15-v3', 'question_id': 'behavior_1',
                      'rubric': dict.fromkeys(('fit', 'clarity', 'nonjudgment', 'unambiguous', 'distinct'), 3),
                      'reason': 'بازبینی تخصصی', 'confirmed': True}
            pb.admin_mutate(db, {'role': 'owner', 'staff_id': 1}, review)
            saved = json.loads(db.execute('SELECT body FROM pb_expert_feedback').fetchone()[0])
            self.assertEqual(saved['rubric'], review['rubric'])
            self.assertEqual(db.execute("SELECT count(*) FROM pb_audit WHERE action='feedback'").fetchone()[0], 1)
            with self.assertRaises(ValueError):
                pb.admin_mutate(db, {'role': 'owner', 'staff_id': 1}, {**review, 'rubric': {'fit': 8}})
            with self.assertRaises(PermissionError):
                pb.admin_mutate(db, {'role': 'analyst', 'staff_id': 1}, review)

    def test_internal_question_catalog_covers_every_question(self):
        from personal_brand_question_catalog import catalog
        body = catalog()
        self.assertEqual(len(body['questions']), 31)
        self.assertEqual(len({q['id'] for q in body['questions']}), 31)
        self.assertEqual(sum(q['scored'] for q in body['questions']), 15)
        self.assertTrue(all(q['construct'] and q['rationale'] and q['dimension'] for q in body['questions']))

    def test_exact_question_text_and_structure(self):
        body = model.template_v3()
        self.assertEqual(len(body['sections']), 5)
        self.assertEqual(len(body['behavior']), 15)
        self.assertEqual([q['title'] for q in body['behavior']], model.V3_BEHAVIOR)
        self.assertEqual([len(body[k]) for k in ('base', 'image', 'evidence', 'online')], [5, 5, 3, 3])
        model.validate_template(body)
        for step, answer in responses_v3().items():
            model.validate_step(step, answer, body)

    def test_real_scores_and_stage_boundaries(self):
        for value, score in ((1, 0), (2, 25), (3, 50), (4, 75), (5, 100)):
            report = model.score(responses_v3(value), model.template_v3(), model.model_v3())
            self.assertEqual(report['total'], score)
            self.assertEqual(len(report['dimensions']), 5)
            self.assertEqual(report['stage'], model.V3_STAGES[value - 1])
        answers = responses_v3(5)
        for q in model.template_v3()['behavior']:
            if q['dimension'] == 'evidence':
                answers[3][q['id']] = 1
        report = model.score(answers, model.template_v3(), model.model_v3())
        self.assertEqual(report['bottleneck'], 'اعتماد و شواهد')
        self.assertIn('تجربهٔ کوچک', report['starter_action'])

    def test_iranian_phone_formats(self):
        for phone in ('۰۹۱۲۱۲۳۴۵۶۷', '٠٩١٢١٢٣٤٥٦٧', '+98 912 123 4567', '00989121234567', '0912-123-4567'):
            self.assertEqual(pb.normalize_phone(phone), '09121234567')
        for phone in ('123', 'abc09121234567', '098765432101', '', None, '۰۹۱۲۱۲۳۴۵۶۷x'):
            with self.assertRaises(ValueError):
                pb.normalize_phone(phone)

    def test_choice_validation_and_partial_answers(self):
        body = model.template_v3()
        answers = responses_v3()
        with self.assertRaises(ValueError):
            model.validate_step(1, {**answers[1], 'audience': body['base'][2][2][:3]}, body)
        with self.assertRaises(ValueError):
            model.validate_step(1, {**answers[1], 'field': 'موضوع دیگری دارم'}, body)
        proofs = body['evidence'][0][2][:5]
        self.assertEqual(model.validate_step(4, {**answers[4], 'proof': proofs}, body)['proof'], proofs)
        with self.assertRaises(ValueError):
            model.validate_step(4, {**answers[4], 'proof': ['هنوز چیز مشخصی ندارم', proofs[0]]}, body)
        self.assertEqual(model.validate_partial_v3(1, {'field': answers[1]['field'], 'audience': []}, body)['audience'], [])
        for value in ({'behavior_1': True}, {'behavior_1': 6}, {'unknown': 2}):
            with self.assertRaises(ValueError):
                model.validate_partial_v3(3, value, body)

    def test_template_cannot_change_question_dimension(self):
        body = copy.deepcopy(model.template_v3())
        body['behavior'][0]['dimension'] = 'evidence'
        with self.assertRaises(ValueError):
            model.validate_template(body)


class VersionThreeHTTPTests(BaseHTTP):
    def test_autosave_resume_lead_gate_and_restart(self):
        with __import__('server').connect() as db:
            db.execute("UPDATE pb_template_versions SET status='inactive' WHERE status='published'")
            db.execute("UPDATE pb_scoring_models SET status='inactive' WHERE status='published'")
            db.execute("UPDATE pb_template_versions SET status='published' WHERE id='pb-test-15-v3'")
            db.execute("UPDATE pb_scoring_models SET status='published' WHERE id='pb-score-rules-v3'")
        status, bootstrap, cookie = self.call()
        self.assertEqual(status, 200)
        csrf = bootstrap['data']['csrf']
        def post(**body):
            return self.call('POST', '/api/personal-brand', {'csrf': csrf, **body}, cookie)[:2]
        identity = post(action='start')[1]['data']['id']
        self.assertEqual(post(action='start')[1]['data']['id'], identity)
        self.assertEqual(post(action='restart', id=identity)[0], 422)
        self.assertEqual(post(action='edit', id=identity)[0], 403)
        partial = {'field': 'موضوع دیگری دارم', 'field_other': '<img src=x onerror=alert(1)>', 'audience': []}
        self.assertEqual(post(action='draft', id=identity, revision=0, step=1, answers=partial)[0], 200)
        loaded = self.call(path='/api/personal-brand?id=' + identity, cookie=cookie)[1]['data']
        self.assertEqual(loaded['answers']['1'], partial)
        self.assertEqual(loaded['assessment']['stage'], 0)
        self.assertEqual(loaded['template']['schema'], 3)
        self.assertEqual(post(action='unlock_report', id=identity, phone='09121234567', consent=True)[0], 422)
        for step, answer in responses_v3(4).items():
            self.assertEqual(post(action='save', id=identity, revision=step-1, step=step, answers=answer)[0], 200)
        status, payload = post(action='report', id=identity)
        self.assertEqual(status, 200)
        report = payload['data']['report']
        self.assertEqual(report['total'], 75)
        self.assertNotIn('dimensions', report)
        self.assertNotIn('starter_action', report)
        self.assertEqual(len(report['preview_opportunities']), 2)
        self.assertEqual(post(action='export_report', id=identity)[0], 403)
        self.assertEqual(post(action='unlock_report', id=identity, phone='wrong', consent=True)[0], 422)
        self.assertEqual(post(action='unlock_report', id=identity, phone='09121234567', consent=False)[0], 422)
        self.assertEqual(post(action='unlock_report', id=identity, phone='+989121234567', consent=True)[0], 200)
        loaded = self.call(path='/api/personal-brand?id=' + identity, cookie=cookie)[1]['data']
        self.assertTrue(loaded['report_unlocked'])
        self.assertEqual(len(loaded['reports'][0]['body']['dimensions']), 5)
        self.assertNotIn('phone', json.dumps(loaded))
        self.assertEqual(post(action='start')[1]['data']['id'], identity)
        self.assertEqual(post(action='restart', id=identity)[0], 422)
        next_id = post(action='restart', id=identity, confirmed=True)[1]['data']['id']
        self.assertNotEqual(next_id, identity)
        self.assertEqual(post(action='start')[1]['data']['id'], next_id)
        for step, answer in responses_v3().items():
            self.assertEqual(post(action='save', id=next_id, revision=step-1, step=step, answers=answer)[0], 200)
        self.assertEqual(post(action='report', id=next_id)[0], 200)
        self.assertEqual(post(action='unlock_report', id=next_id, phone='09121234567', consent=True)[0], 200)
        self.assertEqual(post(action='question_feedback', id=next_id, question_id='behavior_1', clarity=1)[0], 200)
        self.assertEqual(post(action='question_feedback', id=next_id, question_id='unknown', clarity=1)[0], 422)
        with __import__('server').connect() as db:
            self.assertEqual(db.execute('PRAGMA foreign_key_check').fetchall(), [])
            self.assertEqual(db.execute('SELECT count(*) FROM pb_leads').fetchone()[0], 2)
        self.assertEqual(post(action='delete_assessment', id=next_id)[0], 200)
        with __import__('server').connect() as db:
            self.assertEqual(db.execute('SELECT count(*) FROM pb_leads').fetchone()[0], 1)
            self.assertEqual(db.execute('SELECT count(*) FROM pb_question_feedback').fetchone()[0], 0)


if __name__ == '__main__':
    unittest.main()
