CREATE TABLE IF NOT EXISTS pb_leads(
    assessment_id TEXT PRIMARY KEY REFERENCES pb_assessments(id) ON DELETE CASCADE,
    owner_hash TEXT NOT NULL REFERENCES pb_sessions(owner_hash),
    phone TEXT NOT NULL,
    consent_version TEXT NOT NULL,
    created_at INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS pb_leads_phone ON pb_leads(phone);
CREATE TABLE IF NOT EXISTS pb_answer_drafts(
    assessment_id TEXT NOT NULL REFERENCES pb_assessments(id) ON DELETE CASCADE,
    step INTEGER NOT NULL CHECK(step BETWEEN 1 AND 5),
    body TEXT NOT NULL,
    updated_at INTEGER NOT NULL,
    PRIMARY KEY(assessment_id,step)
);
CREATE TABLE IF NOT EXISTS pb_question_feedback(
    assessment_id TEXT NOT NULL REFERENCES pb_assessments(id) ON DELETE CASCADE,
    question_id TEXT NOT NULL,
    clarity INTEGER NOT NULL CHECK(clarity BETWEEN 1 AND 3),
    updated_at INTEGER NOT NULL,
    PRIMARY KEY(assessment_id,question_id)
);
INSERT OR IGNORE INTO pb_schema_migrations VALUES(3,strftime('%s','now'));
