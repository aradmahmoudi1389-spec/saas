BEGIN;
CREATE TEMP TABLE admin_rollback_guard (allowed INTEGER CHECK(allowed=1));
INSERT INTO admin_rollback_guard VALUES(CASE WHEN
 (SELECT count(*) FROM admin_audit_logs)=0 AND
 (SELECT count(*) FROM admin_crm_records)=0 AND
 (SELECT count(*) FROM admin_crm_notes)=0 AND
 (SELECT count(*) FROM admin_crm_tasks)=0 AND
 (SELECT count(*) FROM admin_archives)=0 AND
 (SELECT count(*) FROM admin_documents)=0 AND
 (SELECT count(*) FROM admin_versions)=0 AND
 (SELECT count(*) FROM admin_prompt_runs)=0 AND
 (SELECT count(*) FROM admin_crm_stages)=8 AND
 (SELECT count(*) FROM admin_audit_logs WHERE action='stage_create')=0 AND
 (SELECT count(*) FROM admin_events)=0 AND
 (SELECT count(*) FROM admin_assessment_snapshots)=0 AND
 (SELECT count(*) FROM admin_assessment_results)=0 AND
 (SELECT count(*) FROM admin_privacy_requests)=0 AND
 (SELECT count(*) FROM staff WHERE role IN ('admin','crm_manager','content_manager','analyst'))=0
 THEN 1 ELSE 0 END);
DROP TABLE admin_privacy_requests;
DROP TABLE admin_events;
DROP TABLE admin_assessment_results;
DROP TABLE admin_assessment_snapshots;
DROP TABLE admin_prompt_runs;
DROP TABLE admin_versions;
DROP TABLE admin_documents;
DROP TABLE admin_archives;
DROP TABLE admin_crm_tasks;
DROP TABLE admin_crm_notes;
DROP TABLE admin_crm_records;
DROP TABLE admin_crm_stages;
DROP TABLE admin_audit_logs;
DROP TABLE admin_schema_migrations;
DROP TABLE admin_rollback_guard;
COMMIT;
