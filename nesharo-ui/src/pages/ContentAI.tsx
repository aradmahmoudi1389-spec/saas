import { useState } from 'react';

const contentIdeas = [
  {
    type: 'کاروسل',
    hook: '۵ اشتباهی که مدرس‌های طراحی مرتکب می‌شوند (و تو هم داری مرتکب می‌شی)',
    cta: 'ذخیره کن تا یادت نره',
    tags: ['آموزشی', 'High Engagement'],
    reach: 'بالا',
    effort: 'متوسط',
  },
  {
    type: 'ریلز',
    hook: 'قبل vs بعد طراحی این لوگو — ۱۵ ثانیه تحول',
    cta: 'نظرت چیه؟ کامنت بده',
    tags: ['بصری', 'Viral Potential'],
    reach: 'خیلی بالا',
    effort: 'کم',
  },
  {
    type: 'پست تصویری',
    hook: 'این ۳ رنگ را هرگز کنار هم نگذار — راهنمای تئوری رنگ',
    cta: 'ذخیره کن + به یه طراح دیگه نشون بده',
    tags: ['آموزشی', 'Saveable'],
    reach: 'بالا',
    effort: 'کم',
  },
  {
    type: 'استوری',
    hook: 'امروز چند پروژه طراحی رو رد کردم — چرا؟',
    cta: 'در استوری بعدی جواب می‌دم',
    tags: ['پشت‌صحنه', 'Personal'],
    reach: 'متوسط',
    effort: 'خیلی کم',
  },
  {
    type: 'کاروسل',
    hook: 'کامل‌ترین راهنمای Typography برای طراحان مبتدی',
    cta: 'ذخیره کن — همیشه بهش نیاز داری',
    tags: ['آموزشی', 'Lead Magnet'],
    reach: 'خیلی بالا',
    effort: 'زیاد',
  },
];

const calendar = [
  { day: 'دوشنبه', type: 'کاروسل', title: '۵ اشتباه مدرس‌های طراحی', status: 'done' },
  { day: 'سه‌شنبه', type: '—', title: '—', status: 'rest' },
  { day: 'چهارشنبه', type: 'ریلز', title: 'قبل vs بعد لوگو', status: 'scheduled' },
  { day: 'پنجشنبه', type: 'استوری', title: 'پشت‌صحنه پروژه', status: 'scheduled' },
  { day: 'جمعه', type: '—', title: '—', status: 'rest' },
  { day: 'شنبه', type: 'کاروسل', title: 'تئوری رنگ کامل', status: 'idea' },
  { day: 'یک‌شنبه', type: 'پست', title: 'سه رنگ ممنوعه', status: 'idea' },
];

const statusConfig = {
  done: { label: 'منتشر شد', color: '#4ade80', bg: 'rgba(74,222,128,0.1)' },
  scheduled: { label: 'برنامه‌ریزی', color: '#a78bfa', bg: 'rgba(167,139,250,0.1)' },
  idea: { label: 'ایده', color: '#fb923c', bg: 'rgba(251,146,60,0.1)' },
  rest: { label: 'استراحت', color: 'var(--muted-foreground)', bg: 'var(--secondary)' },
};

export default function ContentAI() {
  const [captionInput, setCaptionInput] = useState('امروز یه لوگو طراحی کردم که خیلی خوشم اومد. می‌خوام باهاتون share کنم.');
  const [improved, setImproved] = useState(false);
  const [activeTab, setActiveTab] = useState<'ideas' | 'calendar' | 'caption'>('ideas');

  const improvedCaption = `🎨 وقتی یه لوگو بالاخره "کلیک" می‌کنه — اون حس بی‌نظیره.

امروز بعد از ۳ بار ریست کامل، این طرح رو تموم کردم. اشتباهی که داشتم مرتکب می‌شدم؟ داشتم برای خودم طراحی می‌کردم، نه برای مخاطب برند.

۳ چیزی که هر لوگو خوب باید داشته باشه:
▸ در سیاه‌وسفید هم جذاب باشه
▸ در ۱۶×۱۶ پیکسل هم خوانا بمونه
▸ داستان برند رو بدون کلمه بگه

کدوم طرح رو بیشتر می‌پسندی؟ 👇

#طراحی_لوگو #گرافیک_دیزاین #برندینگ`;

  return (
    <div className="p-6 md:p-8 max-w-6xl mx-auto">
      <div className="mb-8">
        <h1 className="text-2xl font-display font-bold mb-1" style={{ color: 'var(--foreground)' }}>
          AI Content Strategist
        </h1>
        <p className="text-sm" style={{ color: 'var(--muted-foreground)' }}>
          ایده‌ها و تقویم محتوای اختصاصی برند شما
        </p>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 mb-8 p-1 rounded-xl w-fit" style={{ background: 'var(--secondary)' }}>
        {([
          { id: 'ideas', label: '💡 ایده‌های محتوا' },
          { id: 'calendar', label: '📅 تقویم هفتگی' },
          { id: 'caption', label: '✍️ بهبود کپشن' },
        ] as const).map(tab => (
          <button
            key={tab.id}
            className="px-5 py-2.5 rounded-lg text-sm font-medium transition-all"
            style={
              activeTab === tab.id
                ? { background: 'var(--card)', color: 'var(--foreground)', boxShadow: '0 1px 4px rgba(0,0,0,0.3)' }
                : { color: 'var(--muted-foreground)' }
            }
            onClick={() => setActiveTab(tab.id)}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Content Ideas */}
      {activeTab === 'ideas' && (
        <div>
          <div className="flex items-center justify-between mb-5">
            <p className="text-sm" style={{ color: 'var(--muted-foreground)' }}>
              ۵ ایده اختصاصی براساس تحلیل برند شما
            </p>
            <button
              className="px-4 py-2 rounded-lg text-sm font-medium text-white transition-all"
              style={{ background: 'var(--primary)' }}
              onMouseEnter={e => (e.currentTarget.style.background = '#6d28d9')}
              onMouseLeave={e => (e.currentTarget.style.background = 'var(--primary)')}
            >
              ۵ ایده جدید ↻
            </button>
          </div>
          <div className="grid gap-4">
            {contentIdeas.map((idea, i) => (
              <div
                key={i}
                className="rounded-2xl p-5 card-hover"
                style={{ background: 'var(--card)', border: '1px solid var(--border)' }}
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-3 flex-wrap">
                      <span className="tag badge-violet">{idea.type}</span>
                      {idea.tags.map(t => (
                        <span key={t} className="tag" style={{ background: 'var(--secondary)', color: 'var(--secondary-foreground)', border: '1px solid var(--border)' }}>
                          {t}
                        </span>
                      ))}
                    </div>
                    <div className="font-medium mb-2 leading-snug" style={{ color: 'var(--foreground)' }}>
                      🎣 {idea.hook}
                    </div>
                    <div className="text-sm" style={{ color: 'var(--muted-foreground)' }}>
                      CTA: {idea.cta}
                    </div>
                  </div>
                  <div className="flex flex-col gap-2 text-center text-xs flex-shrink-0">
                    <div>
                      <div style={{ color: 'var(--muted-foreground)' }}>ریچ</div>
                      <div className="font-medium" style={{ color: idea.reach === 'خیلی بالا' ? '#4ade80' : idea.reach === 'بالا' ? '#a78bfa' : 'var(--foreground)' }}>
                        {idea.reach}
                      </div>
                    </div>
                    <div>
                      <div style={{ color: 'var(--muted-foreground)' }}>زمان</div>
                      <div className="font-medium" style={{ color: 'var(--foreground)' }}>{idea.effort}</div>
                    </div>
                  </div>
                </div>
                <div className="flex gap-2 mt-4">
                  <button
                    className="flex-1 py-2 rounded-lg text-xs font-medium transition-all"
                    style={{ background: 'var(--secondary)', color: 'var(--secondary-foreground)', border: '1px solid var(--border)' }}
                    onMouseEnter={e => (e.currentTarget.style.borderColor = 'rgba(124,58,237,0.3)')}
                    onMouseLeave={e => (e.currentTarget.style.borderColor = 'var(--border)')}
                  >
                    به تقویم اضافه کن
                  </button>
                  <button
                    className="flex-1 py-2 rounded-lg text-xs font-medium transition-all"
                    style={{ background: 'rgba(124,58,237,0.1)', color: '#a78bfa', border: '1px solid rgba(124,58,237,0.2)' }}
                  >
                    کپشن بنویس ✍️
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Calendar */}
      {activeTab === 'calendar' && (
        <div>
          <div className="mb-5">
            <div className="flex items-center justify-between mb-1">
              <h2 className="font-semibold" style={{ color: 'var(--foreground)' }}>هفته جاری</h2>
              <span className="text-sm" style={{ color: 'var(--muted-foreground)' }}>۱۸–۲۴ شهریور ۱۴۰۳</span>
            </div>
          </div>
          <div className="grid gap-3">
            {calendar.map((item, i) => {
              const sc = statusConfig[item.status as keyof typeof statusConfig];
              return (
                <div
                  key={i}
                  className="rounded-xl p-4 flex items-center gap-4"
                  style={{ background: 'var(--card)', border: '1px solid var(--border)', opacity: item.status === 'rest' ? 0.5 : 1 }}
                >
                  <div className="w-20 text-right flex-shrink-0">
                    <div className="text-sm font-medium" style={{ color: 'var(--foreground)' }}>{item.day}</div>
                  </div>
                  <div
                    className="flex-1 flex items-center gap-3"
                    style={{ opacity: item.status === 'rest' ? 0.4 : 1 }}
                  >
                    {item.status !== 'rest' && (
                      <span className="tag badge-violet text-xs">{item.type}</span>
                    )}
                    <span className="text-sm" style={{ color: item.status === 'rest' ? 'var(--muted-foreground)' : 'var(--foreground)' }}>
                      {item.title}
                    </span>
                  </div>
                  <span
                    className="tag text-xs flex-shrink-0"
                    style={{ background: sc.bg, color: sc.color, border: `1px solid ${sc.color}20` }}
                  >
                    {sc.label}
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Caption improver */}
      {activeTab === 'caption' && (
        <div className="grid md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium mb-3" style={{ color: 'var(--foreground)' }}>
              کپشن اولیه شما
            </label>
            <textarea
              className="w-full rounded-xl p-4 text-sm leading-relaxed resize-none transition-all"
              style={{
                background: 'var(--card)',
                border: '1px solid var(--border)',
                color: 'var(--foreground)',
                height: 220,
                outline: 'none',
              }}
              value={captionInput}
              onChange={e => {
                setCaptionInput(e.target.value);
                setImproved(false);
              }}
              onFocus={e => (e.currentTarget.style.borderColor = 'rgba(124,58,237,0.4)')}
              onBlur={e => (e.currentTarget.style.borderColor = 'var(--border)')}
            />
            <button
              className="mt-3 w-full py-3 rounded-xl font-semibold text-sm text-white transition-all"
              style={{ background: 'linear-gradient(135deg, #7c3aed, #4f46e5)' }}
              onClick={() => setImproved(true)}
              onMouseEnter={e => (e.currentTarget.style.opacity = '0.9')}
              onMouseLeave={e => (e.currentTarget.style.opacity = '1')}
            >
              ✨ بهبود با AI
            </button>
          </div>

          <div>
            <label className="block text-sm font-medium mb-3" style={{ color: 'var(--foreground)' }}>
              نسخه بهبودیافته
              {improved && <span className="tag badge-violet mr-2 text-xs">آماده</span>}
            </label>
            <div
              className="rounded-xl p-4 text-sm leading-relaxed transition-all"
              style={{
                background: improved ? 'rgba(124,58,237,0.06)' : 'var(--card)',
                border: `1px solid ${improved ? 'rgba(124,58,237,0.25)' : 'var(--border)'}`,
                height: 220,
                overflow: 'auto',
                color: improved ? 'var(--foreground)' : 'var(--muted-foreground)',
                whiteSpace: 'pre-line',
              }}
            >
              {improved ? improvedCaption : 'کپشن خود را بنویسید و دکمه بهبود را بزنید...'}
            </div>
            {improved && (
              <div className="flex gap-2 mt-3">
                <button
                  className="flex-1 py-2.5 rounded-xl text-sm font-medium transition-all"
                  style={{ background: 'var(--secondary)', color: 'var(--foreground)', border: '1px solid var(--border)' }}
                >
                  کپی کن
                </button>
                <button
                  className="flex-1 py-2.5 rounded-xl text-sm font-medium text-white transition-all"
                  style={{ background: 'rgba(124,58,237,0.4)', border: '1px solid rgba(124,58,237,0.4)' }}
                >
                  نسخه دیگری بنویس
                </button>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
