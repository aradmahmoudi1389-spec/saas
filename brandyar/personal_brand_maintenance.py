import argparse
import sqlite3
from pathlib import Path

import personal_brand as pb


def rollback(db):
    protected = ('pb_assessments', 'pb_consents', 'pb_instagram_connections', 'pb_audit', 'pb_deletion_requests', 'pb_expert_feedback')
    if any(db.execute('SELECT count(*) FROM ' + table).fetchone()[0] for table in protected):
        raise ValueError('بازگشت ساختار با دادهٔ واقعی مجاز نیست؛ کد را بازگردانید و جداول افزایشی را حفظ کنید.')
    db.execute('BEGIN IMMEDIATE')
    tables = ['pb_question_metrics', 'pb_question_options', 'pb_questions', 'pb_scores', 'pb_recommendations', 'pb_report_versions', 'pb_reports', 'pb_evidence', 'pb_answers', 'pb_assessments', 'pb_instagram_analysis', 'pb_instagram_media', 'pb_instagram_profiles', 'pb_instagram_sync_jobs', 'pb_instagram_connections', 'pb_oauth_states', 'pb_consents', 'pb_expert_feedback', 'pb_events', 'pb_audit', 'pb_deletion_requests', 'pb_sessions', 'pb_scoring_models', 'pb_template_versions', 'pb_templates', 'pb_privacy_settings', 'pb_request_limits', 'pb_schema_migrations']
    for table in tables:
        db.execute('DROP TABLE ' + table)
    db.commit()


def main():
    parser = argparse.ArgumentParser(description='پاک‌سازی یا بازگشت امن ماژول ارزیابی')
    parser.add_argument('action', choices=['cleanup', 'rollback'])
    parser.add_argument('--database', type=Path, required=True)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    db = sqlite3.connect('file:' + str(args.database.resolve()) + '?mode=rw', uri=True)
    db.row_factory = sqlite3.Row
    db.execute('PRAGMA foreign_keys=ON')
    try:
        if not args.apply:
            print('بررسی فقط‌خواندنی؛ برای اجرای سیاست از --apply استفاده کنید.')
            print('Retention days:', db.execute('SELECT retention_days FROM pb_privacy_settings WHERE id=1').fetchone()[0])
        elif args.action == 'cleanup':
            pb.maintenance(db)
            print('پاک‌سازی مطابق سیاست اجرا شد.')
        else:
            rollback(db)
            print('ساختار خالی ماژول بازگردانی شد.')
    finally:
        db.close()


if __name__ == '__main__':
    main()
