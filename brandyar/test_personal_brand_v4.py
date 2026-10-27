import copy
import json
import sqlite3
import unittest

import personal_brand as pb
import personal_brand_model as model
import personal_brand_v4 as monthly
from test_personal_brand import HTTPFlowTests as BaseHTTP, responses_v4


class VersionFourTests(unittest.TestCase):
    def test_exact_question_text_and_structure(self):
        body = monthly.template()
        self.assertEqual(body['schema'], 4)
        self.assertEqual(len(body['sections']), 5)
        self.assertEqual(len(body['behavior']), 15)
        self.assertEqual([q['id'] for q in body['behavior']], [q[0] for q in monthly.BEHAVIOR])
        self.assertEqual([len(body[k]) for k in ('base', 'image', 'evidence', 'online')], [5, 5, 3, 3])
        monthly.validate_template(body)
        for step, answer in responses_v4().items():
            monthly.validate(step, answer, body)

    def test_real_scores_and_stage_boundaries(self):
        for value, score, stage in ((1, 0, 'شروع مسیر'), (2, 25, 'در حال شکل‌گرفتن'), (3, 50, 'قابل‌تشخیص'), (4, 75, 'روبه‌رشد'), (5, 100, 'جاافتاده و قابل‌اعتماد')):
            report = monthly.score(responses_v4(value), monthly.template(), monthly.model())
            self.assertEqual(report['total'], score)
            self.assertEqual(len(report['dimensions']), 5)
            self.assertEqual(report['stage'], stage)

    def test_lowest_dimension_drives_personalized_action(self):
        answers = responses_v4(5)
        for question in monthly.BEHAVIOR:
            if question[1] == 'evidence':
                answers[3][question[0]] = 1
        report = monthly.score(answers, monthly.template(), monthly.model())
        self.assertEqual(report['bottleneck'], 'شواهد و تجربه')
        self.assertIn('تجربهٔ کوچک', report['starter_action'])

    def test_order_is_shuffled_without_changing_ids(self):
        body = monthly.template()
        orders = [monthly.question_order(body) for _ in range(8)]
        self.assertTrue(all(set(order) == {q['id'] for q in body['behavior']} for order in orders))
        self.assertTrue(any(order != orders[0] for order in orders[1:]))

    def test_partial_and_other_choice_validation(self):
        body = monthly.template()
        self.assertEqual(monthly.validate(1, {'field': 'موضوع دیگری دارم', 'audience': []}, body, partial=True)['field'], 'موضوع دیگری دارم')
        with self.assertRaises(ValueError):
            monthly.validate(1, {**responses_v4()[1], 'audience': ['مشتریان و خریداران احتمالی'] * 3}, body)
        with self.assertRaises(ValueError):
            monthly.validate(4, {'available_proof': ['هنوز چیز مشخصی ندارم', 'نمونه‌کار'], 'proud_work': '', 'evidence_need': monthly.EVIDENCE[2][2][0]}, body)
        self.assertEqual(monthly.validate(5, responses_v4()[5], body)['profile_clarity'], monthly.ONLINE[2][2][0])

    def test_model_cannot_change_or_add_scoring(self):
        with self.assertRaises(ValueError):
            monthly.validate_model({**monthly.model(), 'dimensions': {**monthly.model()['dimensions'], 'clarity': .3}})
        with self.assertRaises(ValueError):
            monthly.validate_template({**monthly.template(), 'version': 'other'})

    def test_every_behavior_has_month_and_same_scale(self):
        body = monthly.template()
        self.assertTrue(all('در یک ماه اخیر' in q['title'] for q in body['behavior']))
        self.assertEqual(len(body['likert']), 5)
        self.assertEqual([sum(q['dimension'] == key for q in body['behavior']) for key, _ in monthly.DIMENSIONS], [3] * 5)

    def test_context_changes_text_but_not_scores(self):
        original = responses_v4()
        changed = copy.deepcopy(original)
        changed[1]['field'] = 'فناوری و برنامه‌نویسی'
        changed[1]['primary_goal'] = 'پیدا کردن شغل یا فرصت کاری بهتر'
        changed[4]['available_proof'] = ['هنوز چیز مشخصی ندارم']
        changed[5]['primary_channel'] = 'فعلاً حضور فعالی ندارم'
        changed[5]['profile_clarity'] = 'مطمئن نیستم'
        a, b = [monthly.score(x, monthly.template(), monthly.model()) for x in (original, changed)]
        self.assertEqual(a['total'], b['total'])
        self.assertEqual(a['dimensions'], b['dimensions'])
        self.assertNotEqual(a['starter_action'], b['starter_action'])
        self.assertNotEqual(a['challenge_question'], b['challenge_question'])
        self.assertTrue(b['needs_profile_review'])

    def test_all_reachable_totals_and_stage_boundaries(self):
        for increments in range(61):
            answers = responses_v4(1)
            left = increments
            for key in answers[3]:
                amount = min(4, left)
                answers[3][key] += amount
                left -= amount
            report = monthly.score(answers, monthly.template(), monthly.model())
            total = int(increments * 100 / 60 + .5)
            self.assertEqual(report['total'], total)
            self.assertEqual(report['stage'], monthly.STAGES[sum(total > x for x in (20, 40, 60, 80))])

    def test_missing_and_invalid_behavior_never_become_zero(self):
        for invalid in (None, True, 0, 6, '3'):
            answers = responses_v4()
            answers[3]['clarity_1'] = invalid
            with self.assertRaises(ValueError):
                monthly.score(answers, monthly.template(), monthly.model())
        answers = responses_v4()
        del answers[3]['clarity_1']
        with self.assertRaises(ValueError):
            monthly.score(answers, monthly.template(), monthly.model())

    def test_high_low_dimensions_drive_result(self):
        for low, _ in monthly.DIMENSIONS:
            for high, _ in monthly.DIMENSIONS:
                if low == high:
                    continue
                answers = responses_v4(3)
                for key, dimension, _ in monthly.BEHAVIOR:
                    answers[3][key] = 1 if dimension == low else 5 if dimension == high else 3
                report = monthly.score(answers, monthly.template(), monthly.model())
                self.assertEqual(report['growth_dimension'], low)
                self.assertEqual(report['strength_dimension'], high)

    def test_all_other_texts_are_optional(self):
        body = monthly.template()
        answers = responses_v4()
        for step, section in ((1, 'base'), (2, 'image'), (4, 'evidence'), (5, 'online')):
            for key, _, _ in body[section]:
                if key in monthly.OTHER:
                    answers[step][key] = [monthly.OTHER[key]] if key in {'audience', 'available_proof'} else monthly.OTHER[key]
            monthly.validate(step, answers[step], body)
        self.assertIn('starter_action', monthly.score(answers, body, monthly.model()))

    def test_legacy_v3_remains_available_for_old_data(self):
        self.assertEqual(model.template_v3()['schema'], 3)
        self.assertEqual(model.model_v3()['schema'], 3)


class VersionFourHTTPTests(BaseHTTP):
    def test_autosave_resume_lead_gate_and_restart(self):
        status, bootstrap, cookie = self.call()
        self.assertEqual(status, 200)
        csrf = bootstrap['data']['csrf']
        def post(**body):
            return self.call('POST', '/api/personal-brand', {'csrf': csrf, **body}, cookie)[:2]
        identity = post(action='start')[1]['data']['id']
        self.assertEqual(post(action='start')[1]['data']['id'], identity)
        partial = {'field': 'موضوع دیگری دارم', 'field_other': '<img src=x onerror=alert(1)>', 'audience': []}
        self.assertEqual(post(action='draft', id=identity, revision=0, step=1, answers=partial)[0], 200)
        loaded = self.call(path='/api/personal-brand?id=' + identity, cookie=cookie)[1]['data']
        self.assertEqual(loaded['answers']['1'], partial)
        self.assertEqual(loaded['template']['schema'], 4)
        order = loaded['order']
        self.assertEqual(self.call(path='/api/personal-brand?id=' + identity, cookie=cookie)[1]['data']['order'], order)
        with __import__('server').connect() as db:
            record = db.execute('SELECT * FROM pb_response_records WHERE assessment_id=? AND question_id=?', (identity, 'field_other')).fetchone()
            self.assertEqual(record['template_version'], monthly.TEMPLATE_ID)
            self.assertGreater(record['recorded_at'], 0)
            self.assertEqual(record['display_order'], 0)
        for step, answer in responses_v4(4).items():
            self.assertEqual(post(action='save', id=identity, revision=step-1, step=step, answers=answer)[0], 200)
        report = post(action='report', id=identity)[1]['data']['report']
        self.assertEqual(report['total'], 75)
        self.assertEqual(len(report['dimensions']), 5)
        self.assertIn('starter_action', report)
        self.assertEqual(post(action='export_report', id=identity)[0], 200)
        loaded = self.call(path='/api/personal-brand?id=' + identity, cookie=cookie)[1]['data']
        self.assertTrue(loaded['report_unlocked'])
        self.assertEqual(len(loaded['reports'][0]['body']['dimensions']), 5)
        self.assertNotIn('phone', json.dumps(loaded))
        with __import__('server').connect() as db:
            self.assertEqual(db.execute('SELECT count(*) FROM pb_leads WHERE assessment_id=?', (identity,)).fetchone()[0], 0)
            records = db.execute('SELECT * FROM pb_response_records WHERE assessment_id=?', (identity,)).fetchall()
            self.assertEqual(len(records), 31)
            for record in records:
                self.assertEqual(record['template_version'], monthly.TEMPLATE_ID)
                if record['question_id'] in order:
                    self.assertEqual(record['display_order'], 10 + order.index(record['question_id']))
        self.assertEqual(post(action='restart', id=identity)[0], 422)
        next_id = post(action='restart', id=identity, confirmed=True)[1]['data']['id']
        self.assertNotEqual(next_id, identity)
        self.assertEqual(post(action='start')[1]['data']['id'], next_id)
        self.assertEqual(post(action='delete_assessment', id=next_id)[0], 200)
        self.assertEqual(post(action='delete_assessment', id=identity)[0], 200)


if __name__ == '__main__':
    unittest.main()
