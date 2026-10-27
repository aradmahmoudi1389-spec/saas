CREATE TABLE pb_question_rules(question_id TEXT NOT NULL, template_version TEXT NOT NULL, weight REAL NOT NULL CHECK(weight>0), active INTEGER NOT NULL CHECK(active IN (0,1)), PRIMARY KEY(question_id,template_version), FOREIGN KEY(question_id,template_version) REFERENCES pb_questions(id,template_version));
INSERT INTO pb_question_rules SELECT id,template_version,1,1 FROM pb_questions;
CREATE TABLE pb_analysis_runs(id TEXT PRIMARY KEY, assessment_id TEXT NOT NULL REFERENCES pb_assessments(id) ON DELETE CASCADE, engine_version TEXT NOT NULL, status TEXT NOT NULL CHECK(status IN ('running','success','failed')), error_code TEXT, created_at INTEGER NOT NULL, completed_at INTEGER);
CREATE UNIQUE INDEX pb_analysis_running ON pb_analysis_runs(assessment_id) WHERE status='running';
INSERT INTO pb_schema_migrations VALUES(2,strftime('%s','now'));
