# مجوزهای پنل مدیریت نشارو

## نقش‌ها

| نقش | دسترسی اصلی |
|---|---|
| owner | همهٔ بخش‌ها، انتشار، export، دادهٔ خصوصی، آرشیو، نقش‌ها و تنظیمات |
| admin | عملیات اصلی به‌جز تیم و تنظیمات |
| crm_manager | مشتری، CRM، گزارش و دادهٔ خصوصی محدود |
| content_manager | draft تست، پرامپت، پلن و محتوا؛ انتشار catalog فعال نیست |
| analyst | مشاهدهٔ overview، ارزیابی و گزارش |

## قواعد

- deny by default؛ هر route، section، رکورد و mutation در سمت سرور بررسی می‌شود.
- مخفی‌کردن دکمه معیار امنیت نیست.
- تغییر نقش فقط برای owner است؛ تغییر owner، خود یا ارتقای owner از این مسیر ممکن نیست.
- مشاهدهٔ کامل مشتری به `private` نیاز دارد و در audit ثبت می‌شود.
- export به `export` و تأیید نهایی نیاز دارد؛ CSV شامل تماس کامل نیست.
- انتشار و rollback پرامپت به `publish` و تأیید نهایی نیاز دارد؛ تغییر قیمت یا انتشار catalog تا اتصال واقعی بسته است.
- archive، privacy request، regenerate و Prompt Lab تأیید نهایی و audit دارند.
- نشست مدیر رمز، hash، TOTP secret یا service key را به API یا رابط برنمی‌گرداند.

## وضعیت RLS

احراز هویت فعال فعلی SQLite staff/TOTP است. فایل `supabase_admin_membership_001.sql` RLS و membership پیشنهادی را تعریف می‌کند اما اجرا نشده؛ بنابراین فعال‌شدن Supabase Auth یا تست RLS زنده ادعا نمی‌شود.
