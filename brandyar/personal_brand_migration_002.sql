ALTER TABLE pb_questions ADD COLUMN weight REAL NOT NULL DEFAULT 1 CHECK(weight>0);
ALTER TABLE pb_questions ADD COLUMN active INTEGER NOT NULL DEFAULT 1 CHECK(active IN (0,1));
CREATE TABLE pb_analysis_runs(id TEXT PRIMARY KEY, assessment_id TEXT NOT NULL REFERENCES pb_assessments(id) ON DELETE CASCADE, engine_version TEXT NOT NULL, status TEXT NOT NULL CHECK(status IN ('running','success','failed')), error_code TEXT, created_at INTEGER NOT NULL, completed_at INTEGER);
CREATE UNIQUE INDEX pb_analysis_running ON pb_analysis_runs(assessment_id) WHERE status='running';
INSERT INTO pb_schema_migrations VALUES(2,strftime('%s','now'));
