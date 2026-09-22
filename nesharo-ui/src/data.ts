export type Brand = {
  id: string
  name: string
  handle: string
  industry: string
  audience: string
  tone: string
  score: number
}

export type RoadmapTask = {
  id: string
  title: string
  description: string
  status: 'todo' | 'progress' | 'done'
  priority: 'high' | 'medium' | 'low'
  due: string
  category: string
  progress: number
  subtasks: string[]
}

export const brands: Brand[] = [
  { id: 'design', name: 'برند آرمین', handle: '@armin.design', industry: 'آموزش طراحی', audience: 'طراحان تازه‌کار', tone: 'آموزشی و صمیمی', score: 72 },
  { id: 'academy', name: 'آکادمی رشد', handle: '@roshd.academy', industry: 'کوچینگ کسب‌وکار', audience: 'کارآفرینان جوان', tone: 'مطمئن و انگیزشی', score: 64 },
]

export const tasks: RoadmapTask[] = [
  { id: 'bio', title: 'بازنویسی بیو پیج', description: 'جایگاه، مخاطب و نتیجه‌ای که ایجاد می‌کنید را در یک جمله شفاف کنید.', status: 'done', priority: 'high', due: '۱۴۰۳/۰۶/۲۰', category: 'برند', progress: 100, subtasks: ['تعریف وعده اصلی', 'نوشتن سه نسخه', 'انتخاب نسخه نهایی'] },
  { id: 'kit', title: 'ساخت Brand Kit', description: 'رنگ، فونت و تمپلیت ثابت برای فید طراحی کنید.', status: 'progress', priority: 'high', due: '۱۴۰۳/۰۶/۲۶', category: 'هویت بصری', progress: 55, subtasks: ['انتخاب پالت رنگ', 'تعریف تایپوگرافی', 'ساخت دو تمپلیت'] },
  { id: 'calendar', title: 'تقویم محتوای ۴ هفته‌ای', description: 'ترکیبی از آموزش، تجربه و Social Proof برای ماه آینده.', status: 'todo', priority: 'high', due: '۱۴۰۳/۰۷/۰۲', category: 'محتوا', progress: 0, subtasks: ['انتخاب چهار ستون محتوا', 'تعیین روز انتشار', 'تولید بریف‌ها'] },
  { id: 'case', title: 'اولین Case Study', description: 'نتیجه یک دانش‌آموز واقعی را به داستانی قابل انتشار تبدیل کنید.', status: 'todo', priority: 'medium', due: '۱۴۰۳/۰۷/۰۸', category: 'اعتبار', progress: 0, subtasks: ['مصاحبه با دانش‌آموز', 'جمع‌آوری داده', 'نوشتن داستان'] },
  { id: 'magnet', title: 'راه‌اندازی Lead Magnet', description: 'یک فایل رایگان برای تبدیل مخاطب به سرنخ بسازید.', status: 'progress', priority: 'medium', due: '۱۴۰۳/۰۷/۱۵', category: 'تبدیل', progress: 30, subtasks: ['انتخاب موضوع', 'ساخت فایل', 'اتصال فرم دریافت'] },
]

export const auditCategories = [
  { id: 'positioning', label: 'جایگاه‌سازی', english: 'Positioning', score: 65, status: 'نیاز به بهبود', explanation: 'تخصص شما دیده می‌شود، اما وعده متمایزتان در نگاه اول روشن نیست.', evidence: '۶۰٪ مخاطبان در نظرسنجی تفاوت شما با مدرس‌های دیگر را نمی‌دانستند.', recommendation: 'بیو را با فرمت «به چه کسی چه نتیجه‌ای می‌دهم» بازنویسی کنید.', impact: 'زیاد', effort: 'کم' },
  { id: 'messaging', label: 'پیام‌رسانی', english: 'Messaging', score: 78, status: 'خوب', explanation: 'هوک‌ها مناسب‌اند اما CTA در بیشتر پست‌ها غایب است.', evidence: '۷۲٪ پست‌های ۳۰ روز گذشته CTA قابل اقدام نداشتند.', recommendation: 'برای هر پست فقط یک اقدام مشخص تعریف کنید.', impact: 'متوسط', effort: 'کم' },
  { id: 'visual', label: 'هویت بصری', english: 'Visual Identity', score: 70, status: 'متوسط', explanation: 'پالت رنگی نسبتاً ثابت است، اما تایپوگرافی یکدست نیست.', evidence: '۴ فونت متفاوت در ۳۰ روز اخیر استفاده شده است.', recommendation: 'یک کیت برند با دو فونت و سه رنگ اصلی بسازید.', impact: 'متوسط', effort: 'متوسط' },
  { id: 'authority', label: 'اقتدار', english: 'Authority', score: 82, status: 'خوب', explanation: 'آموزش‌ها باکیفیت‌اند و مخاطب شما را متخصص می‌داند.', evidence: 'ذخیره محتوای آموزشی ۲.۱ برابر میانگین نیچ است.', recommendation: 'ماهانه دو Case Study از نتایج مخاطبان منتشر کنید.', impact: 'زیاد', effort: 'متوسط' },
  { id: 'consistency', label: 'ثبات', english: 'Consistency', score: 60, status: 'ضعیف', explanation: 'فاصله‌های انتشار باعث شده رشد برند ناپایدار باشد.', evidence: 'سه فاصلهٔ بیشتر از هفت روز در ۴۵ روز اخیر ثبت شده است.', recommendation: 'حداقل چهار محتوای قابل انتشار در هفته را برنامه‌ریزی کنید.', impact: 'زیاد', effort: 'زیاد' },
]

export const contentIdeas = [
  { id: 'idea-1', type: 'کاروسل', hook: '۵ اشتباهی که مدرس‌های طراحی مرتکب می‌شوند', cta: 'ذخیره کن تا یادت نره', reach: 'بالا', effort: 'متوسط' },
  { id: 'idea-2', type: 'ریلز', hook: 'قبل و بعد طراحی این لوگو در ۱۵ ثانیه', cta: 'نظرت چیه؟ کامنت بده', reach: 'خیلی بالا', effort: 'کم' },
  { id: 'idea-3', type: 'پست آموزشی', hook: 'این ۳ رنگ را هرگز کنار هم نگذار', cta: 'به یک طراح دیگر بفرست', reach: 'بالا', effort: 'کم' },
]

export const chartData = [42, 48, 45, 53, 58, 62, 72]
