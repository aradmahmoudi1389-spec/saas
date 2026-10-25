import copy
import hashlib
import json
import sqlite3
import tempfile
import threading
import time
import unittest
import uuid
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer
from pathlib import Path
from unittest.mock import MagicMock, patch

import admin_workspace as admin
import brand_analysis
import server
import supabase_store
from test_brand_analysis import sample_answers, sample_report


class WorkspaceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=Path(__file__).parent)
        self.addCleanup(self.temp.cleanup)
        self.db_patch = patch.object(server, 'DB', Path(self.temp.name) / 'admin.sqlite')
        self.db_patch.start()
        self.addCleanup(self.db_patch.stop)
        self.db = server.connect()
        self.addCleanup(self.db.close)
        self.db.execute("INSERT INTO staff VALUES(1,'owner@example.test','مدیر آزمایش','owner',X'00',X'00','test')")
        self.db.execute("INSERT INTO staff VALUES(2,'member@example.test','عضو آزمایش','analyst',X'00',X'00','test')")
        self.db.commit()
        self.staff = {'staff_id': 1, 'role': 'owner', 'csrf': 'test-csrf', 'name': 'مدیر آزمایش'}
        self.store = MagicMock()
        self.identity = str(uuid.uuid4())
        self.store.request.return_value = [{'id': self.identity}]

    def mutation(self, **data):
        return admin.mutate(self.db, self.staff, self.store, data)

    def prompt_body(self):
        return {'system_prompt': 'تحلیل محترمانه و دقیق', 'instruction_prompt': '{{assessment.answers}}', 'output_schema': copy.deepcopy(brand_analysis.REPORT_SHAPE), 'sample_output': sample_report()}

    def draft(self, **changes):
        return self.mutation(section='prompts', action='draft', slug='brand-assessment', title='پرامپت آزمایش', body=self.prompt_body(), **changes)[1]['id']

    def test_migration_is_idempotent_and_default_stages_real_config(self):
        admin.initialize(self.db)
        self.assertEqual(self.db.execute('SELECT count(*) FROM admin_crm_stages').fetchone()[0], 8)
        self.assertEqual(self.db.execute('SELECT count(*) FROM admin_documents').fetchone()[0], 0)
        self.assertEqual(self.db.execute('SELECT version FROM admin_schema_migrations').fetchone()[0], 1)

    def test_permission_matrix(self):
        for role, section, expected in [('owner','settings',True),('admin','team',False),('crm_manager','prompts',False),('content_manager','customers',False),('analyst','assessments',True),('support','customers',False)]:
            with self.subTest(role=role,section=section):
                self.assertEqual(admin.allowed(role,section),expected)
        self.staff['role']='analyst'
        status,_=self.mutation(section='assessments',action='archive',id=self.identity,confirmed=True)
        self.assertEqual(status,403)
        self.store.request.assert_not_called()

    def test_mask_list_and_audit_detail(self):
        self.store.request.return_value=[{'id':self.identity,'mobile':'09000000000','status':'new','created_at':'2026-10-25T00:00:00Z'}]
        status,data=admin.get_data(self.db,self.staff,self.store,'customers',{})
        self.assertEqual(status,200)
        self.assertNotIn('09000000000',json.dumps(data))
        self.store.request.return_value=[{'id':self.identity,'mobile':'09000000000','status':'new'}]
        status,data=admin.get_data(self.db,self.staff,self.store,'customers',{'id':[self.identity]})
        self.assertEqual(status,200)
        self.assertEqual(data['record']['mobile'],'09000000000')
        row=self.db.execute('SELECT * FROM admin_audit_logs').fetchone()
        self.assertEqual(row['action'],'view_full')
        self.assertNotIn('09000000000',json.dumps(dict(row)))

    def test_archive_never_deletes_remote_or_answers(self):
        with self.assertRaises(admin.Invalid):
            self.mutation(section='customers',action='archive',id=self.identity)
        status,_=self.mutation(section='customers',action='archive',id=self.identity,confirmed=True)
        self.assertEqual(status,200)
        self.assertEqual(self.db.execute('SELECT count(*) FROM admin_archives').fetchone()[0],1)
        self.assertTrue(all(len(call.args)<2 or call.args[1]!='DELETE' for call in self.store.request.call_args_list))
        self.assertEqual(self.db.execute('SELECT action FROM admin_audit_logs').fetchone()[0],'archive')

    def test_notes_tasks_separate_and_no_mass_assignment(self):
        stage=self.db.execute('SELECT id FROM admin_crm_stages LIMIT 1').fetchone()[0]
        self.mutation(section='crm',action='crm',id=self.identity,stage_id=stage,tags=['پیگیری'],owner_id=2)
        self.mutation(section='crm',action='note',id=self.identity,body='یادداشت غیرشخصی آزمایشی')
        self.mutation(section='crm',action='task',id=self.identity,title='پیگیری',owner_id=2,due_at=int(time.time())+3600)
        self.assertEqual(self.db.execute('SELECT count(*) FROM admin_crm_notes').fetchone()[0],1)
        self.assertEqual(self.db.execute('SELECT count(*) FROM admin_crm_tasks').fetchone()[0],1)
        self.assertEqual(self.db.execute('SELECT owner_id FROM admin_crm_records').fetchone()[0],2)
        self.assertTrue(all(v.args[0]=='leads' for v in self.store.request.call_args_list))
        with self.assertRaises(admin.Invalid):
            self.mutation(section='crm',action='task_done',id=str(uuid.uuid4()),task_id=str(uuid.uuid4()))

    def test_prompt_variables_never_execute(self):
        body=self.prompt_body()
        for value in ('{{__import__(os)}}','{{user.first_name}}','{{assessment.secret}}'):
            body['instruction_prompt']=value
            with self.subTest(value=value),self.assertRaises(admin.Invalid):
                admin.validate_document('prompts',body)
        self.assertIn('fa-IR',admin.render_prompt({'instruction_prompt':'{{locale}} {{assessment.answers}}'},{'q4':'گزینهٔ اول'}))

    def test_prompt_publish_requires_lab_and_rollback_retains_history(self):
        first=self.draft()
        with self.assertRaises(admin.Invalid):
            self.mutation(section='prompts',action='publish',id=first,confirmed=True)
        self.db.execute('INSERT INTO admin_prompt_runs VALUES(?,?,?,?,?,?,?)',(str(uuid.uuid4()),first,int(time.time()),1,'{}','{}','success'))
        self.mutation(section='prompts',action='publish',id=first,confirmed=True)
        second=self.draft(change_note='نسخهٔ دوم')
        self.db.execute('INSERT INTO admin_prompt_runs VALUES(?,?,?,?,?,?,?)',(str(uuid.uuid4()),second,int(time.time()),1,'{}','{}','success'))
        self.mutation(section='prompts',action='publish',id=second,confirmed=True)
        self.mutation(section='prompts',action='rollback',id=first,confirmed=True)
        self.assertEqual(admin.active_prompt(self.db)[0],first)
        self.assertEqual(self.db.execute('SELECT count(*) FROM admin_versions').fetchone()[0],2)
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute('UPDATE admin_versions SET body=? WHERE id=?',('{}',first))
        self.db.rollback()

    def test_content_manager_cannot_publish_prompts(self):
        first=self.draft()
        self.staff['role']='content_manager'
        self.assertEqual(self.mutation(section='prompts',action='publish',id=first,confirmed=True)[0],403)

    def test_unconnected_catalog_cannot_publish(self):
        status,data=self.mutation(section='content',action='draft',slug='faq',title='راهنما',body={'text':'راهنمای سایت','placement':'faq','cta_path':''})
        self.assertEqual(status,200)
        with self.assertRaises(admin.Invalid):
            self.mutation(section='content',action='publish',id=data['id'],confirmed=True)

    def test_team_owner_protected_and_sessions_revoked(self):
        with self.assertRaises(admin.Invalid):
            self.mutation(section='team',action='role',staff_id=1,role='analyst',confirmed=True)
        status,_=self.mutation(section='team',action='role',staff_id=2,role='crm_manager',confirmed=True)
        self.assertEqual(status,200)
        self.assertEqual(self.db.execute('SELECT role FROM staff WHERE id=2').fetchone()[0],'crm_manager')
        self.assertEqual(self.db.execute('SELECT action FROM admin_audit_logs').fetchone()[0],'role_change')

    def test_audit_is_append_only(self):
        admin.audit(self.db,self.staff,'view_full','leads',self.identity)
        self.db.commit()
        for query in ('DELETE FROM admin_audit_logs','UPDATE admin_audit_logs SET action=\'other\''):
            with self.assertRaises(sqlite3.IntegrityError):
                self.db.execute(query)
            self.db.rollback()

    def test_export_has_no_contact_and_is_audited(self):
        self.store.request.return_value=[{'id':self.identity,'status':'new','created_at':'2026-10-25'}]
        status,data=self.mutation(section='customers',action='export',confirmed=True)
        self.assertEqual(status,200)
        self.assertNotIn('mobile',data['csv'])
        self.assertEqual(self.db.execute('SELECT action FROM admin_audit_logs').fetchone()[0],'export')

    def test_privacy_is_request_not_destructive_action(self):
        status,_=self.mutation(section='customers',action='privacy',id=self.identity,kind='anonymize',confirmed=True)
        self.assertEqual(status,200)
        self.assertEqual(self.db.execute('SELECT status FROM admin_privacy_requests').fetchone()[0],'pending')

    def test_snapshot_never_uses_current_questions_for_history(self):
        self.store.request.return_value=[{'id':self.identity,'answers':{'old':'answer'},'full_report':supabase_store.pack_report(sample_report())}]
        status,data=admin.get_data(self.db,self.staff,self.store,'assessments',{'id':[self.identity]})
        self.assertEqual(status,200)
        self.assertEqual(data['record']['snapshot'],{})
        self.assertEqual(data['record']['full_report'],sample_report())

    def test_rollback_refuses_to_drop_live_audit(self):
        admin.audit(self.db,self.staff,'test','test')
        self.db.commit()
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.executescript(Path(__file__).with_name('admin_migration_001_down.sql').read_text())
        self.db.rollback()
        self.assertEqual(self.db.execute('SELECT count(*) FROM admin_audit_logs').fetchone()[0],1)

    def test_migration_rollback_on_empty_workspace(self):
        self.db.execute("UPDATE staff SET role='viewer' WHERE id=2")
        self.db.commit()
        self.db.executescript(Path(__file__).with_name('admin_migration_001_down.sql').read_text())
        self.assertFalse(self.db.execute("SELECT 1 FROM sqlite_master WHERE name='admin_documents'").fetchone())
        admin.initialize(self.db)
        self.assertEqual(self.db.execute('SELECT count(*) FROM admin_crm_stages').fetchone()[0],8)

    def test_invalid_identifiers_rejected_without_remote_call(self):
        for value in ('id=eq.any','../../etc','a',None):
            with self.subTest(value=value),self.assertRaises(admin.Invalid):
                self.mutation(section='customers',action='note',id=value,body='test')
        self.store.request.assert_not_called()

    def test_event_tracking_and_counts(self):
        admin.event(self.db,self.identity,'analysis_started')
        admin.event(self.db,self.identity,'analysis_ready')
        self.db.commit()
        self.store.count.return_value=4
        status,data=admin.get_data(self.db,self.staff,self.store,'overview',{})
        self.assertEqual(status,200)
        self.assertEqual(data['events']['analysis_ready'],1)
        self.assertEqual(data['counts']['leads'],4)

    def test_prompt_lab_isolated_and_audited(self):
        identity=self.draft()
        handler=MagicMock()
        with patch.object(brand_analysis,'generate_report',return_value=sample_report()):
            admin.lab(handler,self.db,self.staff,{'id':identity,'confirmed':True})
        self.assertEqual(handler.json.call_args.args[0],200)
        self.assertTrue(handler.json.call_args.args[1]['valid'])
        self.assertEqual(self.db.execute('SELECT status FROM admin_prompt_runs').fetchone()[0],'success')
        self.assertEqual(self.db.execute('SELECT count(*) FROM admin_assessment_results').fetchone()[0],0)

    def test_count_requires_exact_content_range(self):
        with patch.dict('os.environ', {'SUPABASE_URL': 'https://database.example.test', 'SUPABASE_SERVICE_ROLE_KEY': 'test-only'}):
            store = supabase_store.SupabaseStore()
        response = MagicMock()
        response.read.return_value = b'[]'
        response.headers = {'Content-Range': '*/42'}
        with patch.object(supabase_store, 'urlopen') as opener:
            opener.return_value.__enter__.return_value = response
            self.assertEqual(store.count('leads'), 42)
            response.headers = {'Content-Range': '*/*'}
            with self.assertRaises(supabase_store.SupabaseUnavailable):
                store.count('leads')

    def test_regeneration_appends_history_without_remote_write(self):
        handler = MagicMock()
        handler.supabase.return_value = self.store
        answers = {'q4': {'question': 'پرسش آزمایش', 'answer': 'گزینهٔ اول'}}
        self.store.request.return_value = [{'id': self.identity, 'answers': answers}]
        with patch.object(brand_analysis, 'generate_report', return_value=sample_report()):
            admin.regenerate(handler, self.db, self.staff, {'section': 'assessments', 'id': self.identity, 'confirmed': True})
        self.assertEqual(handler.json.call_args.args[0], 200)
        row = self.db.execute('SELECT * FROM admin_assessment_results').fetchone()
        self.assertEqual(row['assessment_id'], self.identity)
        self.assertEqual(json.loads(row['context_json'])['answers'], answers)
        self.assertTrue(all(len(call.args) < 2 for call in self.store.request.call_args_list))
        admin.regenerate(handler, self.db, self.staff, {'section': 'assessments', 'id': self.identity, 'confirmed': True})
        self.assertEqual(handler.json.call_args.args[0], 429)
        self.assertEqual(self.db.execute('SELECT count(*) FROM admin_assessment_results').fetchone()[0], 1)

    def test_regeneration_failure_preserves_history(self):
        handler = MagicMock()
        handler.supabase.return_value = self.store
        self.store.request.return_value = [{'id': self.identity, 'answers': {'q4': {'question': 'پرسش', 'answer': 'گزینه'}}}]
        with patch.object(brand_analysis, 'generate_report', side_effect=brand_analysis.AnalysisError('آزمایش')):
            admin.regenerate(handler, self.db, self.staff, {'section': 'assessments', 'id': self.identity, 'confirmed': True})
        self.assertEqual(handler.json.call_args.args[0], 503)
        self.assertEqual(self.db.execute('SELECT count(*) FROM admin_assessment_results').fetchone()[0], 0)
        self.assertTrue(self.db.execute("SELECT 1 FROM admin_audit_logs WHERE action='regenerate_failed'").fetchone())

    def test_csv_formula_is_neutralized(self):
        self.store.request.return_value = [{'id': self.identity, 'status': '=1+1', 'created_at': '2026-10-25'}]
        status, result = self.mutation(section='customers', action='export', confirmed=True)
        self.assertEqual(status, 200)
        self.assertIn("'=1+1", result['csv'])

    def test_corrupt_compressed_report_has_safe_detail(self):
        import base64
        self.store.request.return_value = [{'id': self.identity, 'full_report': {'encoding': 'zlib-base64-v1', 'data': base64.b64encode(b'not-zlib').decode()}}]
        status, result = admin.get_data(self.db, self.staff, self.store, 'assessments', {'id': [self.identity]})
        self.assertEqual(status, 200)
        self.assertIsNone(result['record']['full_report'])

    def test_published_prompt_reaches_real_generation_payload(self):
        response=MagicMock()
        response.read.return_value=json.dumps({'choices':[{'finish_reason':'stop','message':{'content':json.dumps(sample_report())}}]}).encode()
        opener=MagicMock()
        opener.open.return_value.__enter__.return_value=response
        with patch.dict('os.environ',{'BRANDYAR_METIS_API_KEY':'test-only'}),patch.object(brand_analysis,'build_opener',return_value=opener):
            brand_analysis.generate_report({'q4':'گزینهٔ اول'},prompt_body=self.prompt_body())
        payload=json.loads(opener.open.call_args.args[0].data)
        self.assertIn('تحلیل محترمانه',payload['messages'][0]['content'])
        self.assertIn('q4',payload['messages'][1]['content'])


class WorkspaceHTTPTests(WorkspaceTests):
    @classmethod
    def setUpClass(cls):
        cls.http=ThreadingHTTPServer(('127.0.0.1',0),server.Handler)
        cls.thread=threading.Thread(target=cls.http.serve_forever)
        cls.thread.start()
        cls.port=cls.http.server_address[1]

    @classmethod
    def tearDownClass(cls):
        cls.http.shutdown();cls.http.server_close();cls.thread.join()

    def request(self,path,method='GET',body=None,cookie=None):
        headers={'X-Forwarded-Proto':'https','Origin':f'https://127.0.0.1:{self.port}','Content-Type':'application/json'}
        if cookie: headers['Cookie']=cookie
        connection=HTTPConnection('127.0.0.1',self.port,timeout=5)
        connection.request(method,path,json.dumps(body) if body is not None else None,headers)
        response=connection.getresponse()
        raw=response.read()
        result=response.status,raw,dict(response.getheaders())
        connection.close()
        return result

    def cookie(self,role='owner',verified=1):
        token=uuid.uuid4().hex+uuid.uuid4().hex
        now=int(time.time())
        self.db.execute('UPDATE staff SET role=? WHERE id=1',(role,))
        self.db.execute('INSERT INTO sessions VALUES(?,?,?,?,?,?,?)',(hashlib.sha256(token.encode()).hexdigest(),1,'test-csrf',verified,now,now,now+3600))
        self.db.commit()
        return 'brandysid='+token

    def test_all_pages_and_api_guarded(self):
        for module in admin.MODULES:
            self.assertEqual(self.request('/admin/'+module)[0],303)
        self.assertEqual(self.request('/api/admin/workspace?section=customers')[0],401)
        self.assertEqual(self.request('/admin/login')[0],200)
        self.assertEqual(self.request('/admin/tests',cookie=self.cookie('analyst'))[0],403)
        self.assertEqual(self.request('/admin/assessments',cookie=self.cookie('analyst'))[0],200)

    def test_csrf_mfa_and_role_cannot_be_bypassed(self):
        body={'section':'customers','action':'archive','id':self.identity,'confirmed':True}
        self.assertEqual(self.request('/api/admin/workspace','POST',body,self.cookie())[0],403)
        body['csrf']='test-csrf'
        self.assertEqual(self.request('/api/admin/workspace','POST',body,self.cookie('analyst'))[0],403)
        self.assertEqual(self.request('/api/admin/workspace','POST',body,self.cookie('owner',0))[0],401)

    def test_bootstrap_contains_no_staff_secrets(self):
        status,raw,_=self.request('/api/admin/workspace?section=bootstrap',cookie=self.cookie())
        self.assertEqual(status,200)
        for name in (b'password_hash',b'totp_secret',b'SERVICE_ROLE',b'token_hash'):
            self.assertNotIn(name,raw)

    def test_legacy_role_cannot_enter_workspace(self):
        cookie = self.cookie('support')
        self.assertEqual(self.request('/admin', cookie=cookie)[0], 403)
        self.assertEqual(self.request('/api/admin/workspace', cookie=cookie)[0], 403)

    def test_legacy_delete_route_cannot_delete(self):
        with patch.object(server.Handler,'supabase',return_value=self.store):
            status,_,_=self.request('/api/admin/leads','POST',{'id':self.identity,'csrf':'test-csrf'},self.cookie())
        self.assertEqual(status,403)
        self.store.request.assert_not_called()


if __name__=='__main__':
    unittest.main()
