CREATE TABLE IF NOT EXISTS pb_response_records(
    assessment_id TEXT NOT NULL REFERENCES pb_assessments(id) ON DELETE CASCADE,
    question_id TEXT NOT NULL,
    template_version TEXT NOT NULL REFERENCES pb_template_versions(id),
    value_json TEXT NOT NULL,
    recorded_at INTEGER NOT NULL,
    display_order INTEGER NOT NULL,
    PRIMARY KEY(assessment_id,question_id)
);
INSERT OR IGNORE INTO pb_schema_migrations VALUES(4,strftime('%s','now'));
