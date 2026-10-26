# مدل دادهٔ پنل مدیریت نشارو

## منابع موجود

- Supabase `leads`: لیدها، وضعیت و موبایل.
- Supabase `assessments`: ارزیابی، پاسخ‌ها، وضعیت، insight و گزارش فشرده.
- SQLite `staff` و `sessions`: مدیر، نقش، password hash، TOTP و نشست.
- SQLite جدول‌های مشاوره، تحلیل و rate limit موجود قبلی.

## جدول‌های migration 001

- `admin_schema_migrations`: نسخهٔ migration.
- `admin_audit_logs`: audit append-only با before/after خلاصه‌شده.
- `admin_crm_stages`, `admin_crm_records`, `admin_crm_notes`, `admin_crm_tasks`: metadata CRM با lead UUID به‌عنوان شناسهٔ خارجی.
- `admin_archives`: آرشیو نرم leads و assessments.
- `admin_documents`, `admin_versions`: اسناد و نسخه‌های draft/published/archived.
- `admin_prompt_runs`: آزمایش ایزولهٔ پرامپت.
- `admin_assessment_snapshots`: سؤال و پاسخ زمان ارزیابی.
- `admin_assessment_results`: نتیجهٔ مستقل با prompt version و context.
- `admin_events`: رویدادهای تحلیل، ذخیره و ثبت لید.
- `admin_privacy_requests`: درخواست pending برای anonymize/delete/unsubscribe؛ اجرای خودکار ندارد.

## ارتباط‌ها

`leads.id` به metadata CRM و archive محلی وصل می‌شود. `assessments.id` به snapshot، result و event وصل می‌شود و در صورت وجود `lead_id` به lead مرتبط است. نسخهٔ سند به نویسندهٔ staff و اجرای Prompt Lab به نسخهٔ پرامپت وصل می‌شود.

## حفظ تاریخچه

snapshot نخستین ارزیابی با `INSERT OR IGNORE` حفظ می‌شود. هر اجرای جدید نتیجهٔ تازه می‌سازد و نتیجهٔ قبلی را overwrite نمی‌کند. نسخهٔ منتشرشدهٔ پرامپت immutable است.

## داده‌های عمداً موجود نیستند

در schema قابل اتکا سفارش، subscription، account profile کامل، پیام‌رسانی، موتور تست پویا و کاتالوگ عمومی پلن وجود ندارد؛ این موارد در پنل جعل یا از روی lead حدس زده نمی‌شوند.
