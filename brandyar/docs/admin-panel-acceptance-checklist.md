# چک‌لیست پذیرش پنل مدیریت نشارو

## تحویل‌شده و تست‌شده

- [x] مسیر `/admin` و `/admin/login` محافظت شده است.
- [x] نقش‌های workspace و deny-by-default سمت سرور اعمال شده‌اند.
- [x] CSRF، MFA، نشست امن و کنترل مبدأ بررسی می‌شوند.
- [x] فهرست lead و assessment از Supabase خوانده می‌شود.
- [x] موبایل در فهرست ماسک و جزئیات با مجوز نمایش داده می‌شود.
- [x] archive جایگزین حذف فیزیکی شده است.
- [x] CRM stage، tag، owner، note و task واقعی ذخیره می‌شوند.
- [x] audit append-only و خروجی محدود بدون تماس کامل وجود دارد.
- [x] snapshot، نتیجهٔ نسخه‌دار و Prompt Lab وجود دارد.
- [x] انتشار و rollback پرامپت به اجرای موفق Lab وابسته است.
- [x] رویدادهای واقعی تحلیل، ذخیره و ثبت لید ثبت می‌شوند.
- [x] حالت‌های خالی، خطا، بارگذاری، RTL و responsive contract تست شده‌اند.
- [x] حذف فیزیکی از API قدیمی مسدود شده است.

## تست‌های اجراشده

```bash
python3 -m unittest discover -s brandyar -p 'test_*.py' -q
node brandyar/test_assessment.cjs
node brandyar/test_admin_workspace.cjs
node --check brandyar/admin-workspace.js
node --check brandyar/app.js
```

آخرین اجرای ثبت‌شده: ۱۰۰ تست Python موفق و هر دو تست Node موفق. تست browser visual، RLS زنده و provider واقعی انجام نشده‌اند.

## عمداً خارج از معیار تکمیل

- [ ] Supabase Auth و RLS membership اجرا نشده است.
- [ ] منبع واقعی سفارش، پرداخت، اشتراک و پلن عمومی در معماری موجود پیدا نشده است.
- [ ] تست پویا و انتشار سؤال جدید به consumer عمومی وصل نیست.
- [ ] funnel تجاری و backfill تاریخی معتبر در دسترس نیست.
- [ ] privacy request فقط ثبت می‌شود و اجرای خودکار ندارد.
- [ ] جست‌وجوی سراسری، فیلترهای پیشرفته و ویرایش/reorder مرحله CRM کامل نیست.
- [ ] Prompt Lab ارزیابی واقعی و مقایسهٔ خودکار نسخه‌ها ندارد.

## آزمون دستی

۱. `/admin/login` را باز کنید، با مدیر verified وارد شوید و نقش را بررسی کنید.
۲. Overview را در بازهٔ خالی و بازهٔ دارای داده ببینید؛ عدد ساختگی نباید وجود داشته باشد.
۳. Customers را باز کنید؛ موبایل در فهرست باید ماسک باشد و جزئیات audit شود.
۴. یک CRM stage، note و task ثبت کنید و بازخوانی صفحه را بررسی کنید.
۵. یک assessment را باز کنید؛ snapshot، پاسخ، گزارش و تاریخچهٔ result جدا باشند.
۶. یک draft prompt بسازید، Lab را با fixture اجرا کنید، سپس با تأیید منتشر و rollback کنید.
۷. به‌عنوان analyst عملیات نوشتن و بخش‌های ممنوع را امتحان کنید؛ باید رد شوند.
۸. آرشیو و export را اجرا کنید؛ حذف remote نباید رخ دهد و audit باید ثبت شود.
۹. `/admin/consultations` و حالت خطای سرویس را جدا بررسی کنید.
