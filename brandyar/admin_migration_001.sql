CREATE TABLE IF NOT EXISTS admin_schema_migrations (version INTEGER PRIMARY KEY, applied_at INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS admin_audit_logs (
 id TEXT PRIMARY KEY, actor_id INTEGER NOT NULL REFERENCES staff(id), actor_role TEXT NOT NULL,
 action TEXT NOT NULL, entity_type TEXT NOT NULL, entity_id TEXT NOT NULL,
 before_summary TEXT NOT NULL DEFAULT '{}', after_summary TEXT NOT NULL DEFAULT '{}',
 created_at INTEGER NOT NULL, request_id TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS admin_audit_created ON admin_audit_logs(created_at DESC);
CREATE TRIGGER IF NOT EXISTS admin_audit_no_update BEFORE UPDATE ON admin_audit_logs BEGIN SELECT RAISE(ABORT, 'append only'); END;
CREATE TRIGGER IF NOT EXISTS admin_audit_no_delete BEFORE DELETE ON admin_audit_logs BEGIN SELECT RAISE(ABORT, 'append only'); END;
CREATE TABLE IF NOT EXISTS admin_crm_stages (id TEXT PRIMARY KEY, title TEXT NOT NULL UNIQUE, position INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS admin_crm_records (
 lead_id TEXT PRIMARY KEY, stage_id TEXT REFERENCES admin_crm_stages(id), owner_id INTEGER REFERENCES staff(id),
 tags TEXT NOT NULL DEFAULT '[]', archived_at INTEGER, updated_at INTEGER NOT NULL, updated_by INTEGER NOT NULL REFERENCES staff(id)
);
CREATE TABLE IF NOT EXISTS admin_crm_notes (
 id TEXT PRIMARY KEY, lead_id TEXT NOT NULL, body TEXT NOT NULL, created_at INTEGER NOT NULL, created_by INTEGER NOT NULL REFERENCES staff(id)
);
CREATE INDEX IF NOT EXISTS admin_notes_lead ON admin_crm_notes(lead_id,created_at);
CREATE TABLE IF NOT EXISTS admin_crm_tasks (
 id TEXT PRIMARY KEY, lead_id TEXT NOT NULL, title TEXT NOT NULL, owner_id INTEGER REFERENCES staff(id),
 due_at INTEGER NOT NULL, done INTEGER NOT NULL DEFAULT 0 CHECK(done IN (0,1)),
 created_at INTEGER NOT NULL, updated_at INTEGER NOT NULL, created_by INTEGER NOT NULL REFERENCES staff(id)
);
CREATE INDEX IF NOT EXISTS admin_tasks_due ON admin_crm_tasks(done,due_at);
CREATE TABLE IF NOT EXISTS admin_archives (
 entity_type TEXT NOT NULL CHECK(entity_type IN ('leads','assessments')), entity_id TEXT NOT NULL,
 archived_at INTEGER NOT NULL, actor_id INTEGER NOT NULL REFERENCES staff(id), PRIMARY KEY(entity_type,entity_id)
);
CREATE TABLE IF NOT EXISTS admin_documents (
 id TEXT PRIMARY KEY, kind TEXT NOT NULL CHECK(kind IN ('tests','prompts','plans','content')),
 slug TEXT NOT NULL, title TEXT NOT NULL, active_version TEXT, created_at INTEGER NOT NULL,
 created_by INTEGER NOT NULL REFERENCES staff(id), UNIQUE(kind,slug)
);
CREATE TABLE IF NOT EXISTS admin_versions (
 id TEXT PRIMARY KEY, document_id TEXT NOT NULL REFERENCES admin_documents(id), version INTEGER NOT NULL CHECK(version>0),
 body TEXT NOT NULL, status TEXT NOT NULL CHECK(status IN ('draft','published','archived')),
 change_note TEXT NOT NULL, created_at INTEGER NOT NULL, created_by INTEGER NOT NULL REFERENCES staff(id),
 published_at INTEGER, published_by INTEGER REFERENCES staff(id), UNIQUE(document_id,version)
);
CREATE TRIGGER IF NOT EXISTS admin_version_immutable BEFORE UPDATE OF body ON admin_versions
 WHEN OLD.status<>'draft' BEGIN SELECT RAISE(ABORT, 'immutable published version'); END;
CREATE TABLE IF NOT EXISTS admin_prompt_runs (
 id TEXT PRIMARY KEY, version_id TEXT NOT NULL REFERENCES admin_versions(id), created_at INTEGER NOT NULL,
 actor_id INTEGER NOT NULL REFERENCES staff(id), input_json TEXT NOT NULL, output_json TEXT, status TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS admin_assessment_snapshots (
 assessment_id TEXT PRIMARY KEY, questions_json TEXT NOT NULL, answers_json TEXT NOT NULL, prompt_version TEXT, created_at INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS admin_assessment_results (
 id TEXT PRIMARY KEY, assessment_id TEXT NOT NULL, prompt_version TEXT, report_json TEXT NOT NULL, created_at INTEGER NOT NULL,
 context_json TEXT NOT NULL DEFAULT '{}'
);
CREATE INDEX IF NOT EXISTS admin_results_assessment ON admin_assessment_results(assessment_id,created_at);
CREATE TABLE IF NOT EXISTS admin_events (
 id TEXT PRIMARY KEY, assessment_id TEXT, event TEXT NOT NULL CHECK(event IN ('analysis_started','analysis_ready','analysis_failed','assessment_stored','lead_registered')),
 test_version TEXT NOT NULL, prompt_version TEXT, created_at INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS admin_events_created ON admin_events(created_at,event);
CREATE TABLE IF NOT EXISTS admin_privacy_requests (
 id TEXT PRIMARY KEY, lead_id TEXT NOT NULL, kind TEXT NOT NULL CHECK(kind IN ('anonymize','delete','unsubscribe')),
 status TEXT NOT NULL DEFAULT 'pending', created_at INTEGER NOT NULL, created_by INTEGER NOT NULL REFERENCES staff(id)
);
INSERT OR IGNORE INTO admin_schema_migrations(version,applied_at) VALUES(1,strftime('%s','now'));
