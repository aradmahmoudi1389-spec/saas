# راه‌اندازی پنل مدیریت نشارو

## پیش‌نیاز

- Python 3 روی سرور.
- اتصال Supabase با `SUPABASE_URL` و `SUPABASE_SERVICE_ROLE_KEY` در محیط سرویس.
- کلید سرویس تحلیل در `BRANDYAR_METIS_API_KEY` در صورت فعال‌بودن تحلیل.
- مسیر SQLite در `BRANDYAR_DB`؛ اگر تنظیم نشده باشد از مسیر دادهٔ پیش‌فرض پروژه استفاده می‌شود.
- HTTPS و تنظیم proxy برای ارسال `X-Forwarded-Proto` و host صحیح.

مقدار هیچ secret را در این راهنما، frontend یا log قرار ندهید.

## ورود نخستین مدیر

ایجاد مدیر از مسیر سرور انجام می‌شود و رمز و کلید TOTP به‌صورت interactive خوانده می‌شوند:

```bash
cd /srv/brandyar
python3 server.py add-staff EMAIL "نام مدیر" owner
```

در prompt، رمز را دو بار و کلید Base32 مربوط به حساب Time-based در برنامهٔ Authenticator وارد کنید. کد شش‌رقمی بعداً هنگام ورود تولید می‌شود. کلید Base32 را در چت، screenshot یا log قرار ندهید.

سپس به `/admin` بروید، رمز را وارد کنید و کد شش‌رقمی را از Authenticator بزنید. اگر رمز یا کلید گم شد، از reset تعاملی روی سرور استفاده کنید؛ MFA را از کد حذف نکنید.

## migration محلی

`server.py` هنگام اتصال، `admin_migration_001.sql` را به‌صورت تراکنشی و idempotent اجرا می‌کند. قبل از استقرار روی SQLite موجود backup بگیرید. migration جدول‌های مدیریتی را اضافه می‌کند و جدول‌های leads/assessments در Supabase را حذف یا rewrite نمی‌کند.

برای rollback فقط وقتی اجرا کنید که دادهٔ مدیریتی، audit، نسخه و نقش مدیریتی جدید وجود نداشته باشد:

```bash
sqlite3 "$BRANDYAR_DB" < admin_migration_001_down.sql
```

فایل rollback در صورت وجود تاریخچه یا داده عمداً متوقف می‌شود.

## migration اختیاری Supabase

`supabase_admin_membership_001.sql` آمادهٔ بازبینی است اما بخشی از راه‌اندازی فعلی نیست. اجرای آن نیازمند بررسی وضعیت موجود `leads`، `assessments`، RLS و grants و داشتن برنامهٔ rollback است. احراز هویت فعلی SQLite staff/TOTP است، نه Supabase Auth.

## نقش‌ها

- `owner`: همهٔ بخش‌ها، تغییر نقش، انتشار، export و عملیات حساس.
- `admin`: مدیریت عملیاتی به‌جز تیم و تنظیمات.
- `crm_manager`: مشتری، CRM و گزارش‌های مرتبط.
- `content_manager`: draftهای تست، پلن و محتوا؛ انتشار catalog تا اتصال consumer عمومی بسته است.
- `analyst`: مشاهدهٔ ارزیابی و گزارش.

مجوز در سمت سرور کنترل می‌شود؛ حذف فیزیکی مشتری و ارزیابی از پنل مجاز نیست و فقط archive/privacy request ثبت می‌شود.

## بررسی پس از استقرار

```bash
python3 -m unittest discover -s brandyar -p 'test_*.py' -q
node brandyar/test_assessment.cjs
node brandyar/test_admin_workspace.cjs
node --check brandyar/admin-workspace.js
```

انتظار می‌رود `/admin/login` عمومی و `/admin` بدون نشست به ورود هدایت شود. API workspace بدون نشست باید پاسخ unauthorized بدهد. تست‌های فعلی با دادهٔ ساختگی محصول انجام نمی‌شوند؛ fixture Prompt Lab غیرشخصی است.

## محدودیت‌های فعلی

- Supabase Auth و migration membership فعال نشده‌اند.
- تست پویا، انتشار پلن/محتوا، پرداخت، خرید و پیام‌رسانی به consumer واقعی متصل نیستند.
- دادهٔ تاریخی فقط از منابع قابل اثبات استفاده می‌کند و نرخ قیف تخمینی تولید نمی‌شود.
- privacy request ثبت می‌شود اما اجرای حذف/ناشناس‌سازی خودکار فعال نیست.
