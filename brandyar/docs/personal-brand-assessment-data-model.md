# مدل داده و برنامهٔ migration

migration شمارهٔ ۲ در انتشار `49fcb80` اجرا شده است: `pb_question_rules` وزن و فعال‌بودن گویه را بدون تغییر شکل جدول قدیمی نگه می‌دارد و `pb_analysis_runs` اجرای تحلیل را ثبت می‌کند. قالب فعال `pb-test-24-v2` است؛ قالب‌ها و گزارش‌های قبلی حفظ شده‌اند. جزئیات بررسی زنده در [گزارش تحویل](personal-brand-assessment-release.md) آمده است.

## پایگاه و مالکیت

تمام جداول ماژول در SQLite فعلی برنامه، با پیشوند `pb_` هستند. ارزیابی‌های قدیمی Supabase مهاجرت یا کپی نمی‌شوند. `owner_hash` یک شناسهٔ مستعار نشست است، نه ایمیل یا حساب احراز‌شدهٔ عمومی. شناسه‌های موجودیت‌ها UUID هستند؛ شناسهٔ سؤال درون نسخهٔ تست پایدار است. زمان‌ها Unix UTC هستند و نمایش فارسی در مرورگر انجام می‌شود.

| موجودیت منطقی | جدول واقعی | تضمین اصلی |
|---|---|---|
| assessment_templates | pb_templates | شناسهٔ ثابت قالب |
| assessment_template_versions | pb_template_versions | شمارهٔ یکتا، draft/published/inactive، بدنهٔ منتشرشده immutable |
| assessment_questions | pb_questions | کلید مرکب سؤال و نسخه |
| assessment_question_options | pb_question_options | FK مرکب، مقدار ۱ تا ۵ |
| scoring_model_versions | pb_scoring_models | وزن و روش تحلیل snapshot، مدل منتشرشده immutable |
| هویت نشست | pb_sessions | hash مالک، CSRF و انقضا |
| assessments | pb_assessments | FK نسخه‌ها، revision، ترتیب ثابت تصادفی، مرحله، شروع/پایان و آرشیو نرم |
| assessment_answers | pb_answers | یک پاسخ در هر مرحله، raw/normalized، زمان و آخرین ذخیره |
| زمان گویه | pb_question_metrics | زمان تمرکز، FK ارزیابی، سقف یک روز |
| assessment_evidence | pb_evidence | شواهد اختیاری وابسته به ارزیابی |
| assessment_reports | pb_reports | یک ظرف گزارش برای هر ارزیابی |
| assessment_report_versions | pb_report_versions | نسخهٔ مستقل، input snapshot، دلیل و زمان؛ UPDATE ممنوع |
| assessment_scores | pb_scores | نمرهٔ شش بُعد برای نسخه، دامنهٔ ۰ تا ۱۰۰ |
| assessment_recommendations | pb_recommendations | ارجاع به بُعد و گویه‌های مبنا |
| رضایت | pb_consents | نوع، متن/سیاست نسخه‌دار، هدف، scope، اعطا و لغو |
| OAuth state | pb_oauth_states | hash یک‌بارمصرف، مالک، consent و انقضای ده‌دقیقه‌ای |
| instagram_connections | pb_instagram_connections | حساب حرفه‌ای، توکن رمزنگاری‌شده، scope، انقضا، وضعیت و آخرین sync |
| instagram_sync_jobs | pb_instagram_sync_jobs | running/success/failed و خطای خلاصهٔ امن |
| instagram_profile_snapshots | pb_instagram_profiles | پروفایل مجاز و زمان |
| instagram_media_snapshots | pb_instagram_media | فراداده و کپشن رسانهٔ همان حساب |
| instagram_content_analysis | pb_instagram_analysis | مشاهدهٔ متنی نسخه‌دار، نه تحلیل چهره |
| رخداد محصول | pb_events | نسخه/مرحله/وضعیت، dedupe_key یکتا |
| assessment_audit_logs | pb_audit | append-only، بدون پاسخ خام یا secret |
| data_deletion_requests | pb_deletion_requests | شناسهٔ پیگیری، نوع، وضعیت و تکمیل |
| سیاست نگهداری | pb_privacy_settings | ۱ تا ۳۶۵ روز؛ پیش‌فرض ۳۰ |
| بازخورد خبره | pb_expert_feedback | نسخهٔ تست، مدیر ثبت‌کننده و متن |
| محدودسازی درخواست | pb_request_limits | hash منبع، نوع عملیات و زمان؛ پنجرهٔ حداکثر ۱۵ دقیقه |
| قواعد نسخه‌دار گویه | pb_question_rules | وزن مثبت و فعال‌بودن؛ FK مرکب به گویه و نسخه |
| analysis_runs | pb_analysis_runs | نسخهٔ موتور، وضعیت و خطای امن؛ حداکثر یک اجرای running برای هر ارزیابی |
| migration | pb_schema_migrations | نسخهٔ ساختار |

FK و cascade حذف فرزندان ارزیابی/اتصال فعال‌اند. حذف حریم خصوصی استثنای موجه immutable بودن گزارش است: UPDATE ممنوع است، DELETE و cascade برای حذف دادهٔ مشتق‌شده مجازند. حذف دادهٔ Instagram فقط نسخه‌هایی را حذف می‌کند که snapshot پیج دارند؛ گزارش‌های صرفاً پرسش‌نامه‌ای حفظ می‌شوند. پس از حذف کامل نسخه‌های گزارش، API خطای امن می‌دهد و کاربر می‌تواند ارزیابی تازه بسازد.

## برنامهٔ استقرار امن

۱. روی سرور ثبت‌شده، نسخهٔ پشتیبان سازگار SQLite و آزمون بازیابی تهیه شود؛ فایل DB، WAL و تنظیمات محرمانه عمومی نشوند.
۲. وابستگی `requirements-personal-brand.txt` در محیط Python سرویس نصب شود.
۳. کد و migration هم‌نسخه منتقل شوند. `server.connect()`، migration شمارهٔ ۱ را در تراکنش و فقط در نبود جدول نشانگر اجرا می‌کند. تمام جداول جدیدند؛ هیچ جدول قدیمی rename/drop نمی‌شود.
۴. پیش از فعال‌کردن مسیر عمومی، `PRAGMA foreign_key_check`، ورود مدیر، مسیر قدیمی و ارزیابی بدون اتصال بررسی شوند.
۵. پاک‌سازی زمان‌بندی‌شده روی سرور تنظیم شود؛ اجرای خودکار هنگام درخواست به‌تنهایی تضمین اجرای دقیق در زمان بی‌ترافیکی نیست.

migration شمارهٔ ۱ همراه نسخهٔ `0ccb400` در تاریخ ۲۰۲۶-۱۰-۲۶ روی DB تولید اجرا شد و جداول زمان گویه و rate-limit را نیز شامل می‌شود. هر تغییر ساختاری بعدی باید migration افزایشی جدید داشته باشد؛ صرف تغییر فایل شمارهٔ ۱ روی DB موجود اعمال نمی‌شود.

## بازگشت

بازگشت کد قدیمی با باقی‌گذاشتن جداول افزایشی، گزینهٔ امن برای DB دارای داده است. برای DB خالی ماژول، ابزار زیر ابتدا فقط بررسی می‌کند:

```sh
python3 personal_brand_maintenance.py rollback --database <database-path>
```

افزودن `--apply` بازگشت واقعی را درخواست می‌کند. ابزار در صورت وجود ارزیابی، رضایت، اتصال، audit، حذف یا بازخورد، بازگشت ساختار را رد می‌کند. این ابزار برای پاک‌کردن اجباری دادهٔ واقعی نیست. بازگشت خالی و جلوگیری از بازگشت DB دارای داده در تست‌ها پوشش داده شده‌اند.

## وضعیت اجرای این تحویل

migration و seed ابتدا روی SQLite موقت/حافظه‌ای آزمایش و سپس با تأیید کاربر روی DB تولید اجرا شدند. پیش از اجرا، نسخهٔ پشتیبان با API استاندارد SQLite و دسترسی محدود تهیه شد. `quick_check` و `foreign_key_check` موفق بودند و شمار رکوردهای جدول‌های قدیمی پیش و پس از اجرا یکسان ماند. seed فقط قالب ۱۸گویه‌ای و مدل واقعی اولیه است؛ هیچ کاربر، پیج یا نتیجهٔ ساختگی در محیط محصول ایجاد نشد. Supabase تغییر نکرد. ۳۵ تست ماژول در staging سرور و بررسی‌های HTTPS پس از انتشار موفق بودند؛ زمان‌بندی cleanup و آزمون بازیابی کامل هنوز انجام نشده‌اند.
