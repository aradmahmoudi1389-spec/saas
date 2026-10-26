# معماری پنل مدیریت نشارو

## اصول

- معماری موجود Python استاتیک حفظ شده و پنل جدید در کنار پنل مشاورهٔ قبلی قرار گرفته است.
- Supabase منبع leads و assessments است؛ SQLite منبع احراز هویت مدیر و metadata مدیریتی است.
- هیچ کلید سرویس یا credential در مرورگر قرار نمی‌گیرد.
- مسیرهای مدیریتی با نشست verified، HTTPS، CSRF و مجوز سمت سرور محافظت می‌شوند.
- عملیات حذف مشتری و ارزیابی از پنل به archive یا privacy request تبدیل شده است.

## اجزا

- `server.py`: route، نشست، MFA، اتصال DB و اتصال workspace.
- `admin_workspace.py`: ماتریس مجوز، خواندن، mutation، audit، CRM، نسخه‌ها و Prompt Lab.
- `admin-workspace.html/css/js`: رابط فارسی RTL بدون framework و با حالت loading، empty و error.
- `supabase_store.py`: PostgREST سروری، count دقیق و ذخیرهٔ ارزیابی.
- `brand_analysis.py`: تولید گزارش و استفاده از پرامپت فعال.

## قرارداد مسیرها

- GET `/admin/login`: فرم ورود.
- GET `/admin` و `/admin/<module>`: workspace محافظت‌شده.
- GET `/api/admin/workspace?section=bootstrap|overview|customers|crm|assessments|tests|prompts|plans|content|team|reports|audit|settings`.
- POST `/api/admin/workspace`: mutationهای CRM، draft، انتشار/rollback پرامپت، export، privacy request، Prompt Lab و regenerate.
- `/admin/consultations` و APIهای مشاورهٔ قبلی مستقل باقی مانده‌اند.

## تصمیم‌های آگاهانه

تست پویا، کاتالوگ پلن/محتوا، خرید، سفارش، پیام‌رسانی و Supabase Auth در معماری موجود consumer یا منبع قابل اتکا ندارند؛ به‌جای اتصال ساختگی، draft یا وضعیت آماده‌سازی نمایش داده می‌شود. migration عضویت Supabase فقط آمادهٔ بازبینی است و فعال نشده است.
