CREATE TABLE IF NOT EXISTS pb_full_reports (
    source_version TEXT PRIMARY KEY REFERENCES pb_report_versions(id) ON DELETE CASCADE,
    owner_hash TEXT NOT NULL,
    body TEXT NOT NULL,
    created_at INTEGER NOT NULL
);
INSERT INTO pb_schema_migrations(version,created_at) VALUES(5,strftime('%s','now'));
