import { useState } from 'react';

const scoreCategories = [
  { label: 'Positioning', score: 65, weight: '20%', color: '#7c3aed' },
  { label: 'Messaging', score: 78, weight: '20%', color: '#4f46e5' },
  { label: 'Visual Identity', score: 70, weight: '15%', color: '#7c3aed' },
  { label: 'Authority', score: 82, weight: '20%', color: '#4f46e5' },
  { label: 'Consistency', score: 60, weight: '25%', color: '#7c3aed' },
];

const overallScore = 72;

const insights = [
  { type: 'warning', icon: '⚠️', text: 'لحن محتوای شما در ۳۰ روز اخیر ۴۲٪ تغییر کرده — ثبات پیام برند آسیب دیده است.' },
  { type: 'tip', icon: '💡', text: 'پست‌های کاروسل شما ۳.۲× بیشتر از ریلز تعامل دارند. تمرکز روی کاروسل توصیه می‌شود.' },
  { type: 'success', icon: '✅', text: 'نرخ تعامل هفته گذشته ۱۸٪ افزایش یافت. هوک‌های سوالی عملکرد بهتری داشتند.' },
  { type: 'warning', icon: '⚠️', text: 'بیوی پیج شما جایگاه مشخصی برای مخاطب ایجاد نمی‌کند — بهبود فوری توصیه می‌شود.' },
];

const weeklyData = [
  { day: 'شن', reach: 1200, engagement: 340 },
  { day: 'یک', reach: 1800, engagement: 510 },
  { day: 'دو', reach: 1500, engagement: 420 },
  { day: 'سه', reach: 2100, engagement: 680 },
  { day: 'چه', reach: 1900, engagement: 590 },
  { day: 'پن', reach: 2400, engagement: 780 },
  { day: 'جم', reach: 2200, engagement: 720 },
];

const maxReach = Math.max(...weeklyData.map(d => d.reach));

function ScoreRing({ score }: { score: number }) {
  const radius = 64;
  const circumference = 2 * Math.PI * radius;
  const dashOffset = circumference - (score / 100) * circumference;

  return (
    <div className="relative flex items-center justify-center" style={{ width: 160, height: 160 }}>
      <svg width="160" height="160" style={{ transform: 'rotate(-90deg)' }}>
        <circle
          cx="80"
          cy="80"
          r={radius}
          fill="none"
          stroke="var(--secondary)"
          strokeWidth="10"
        />
        <circle
          cx="80"
          cy="80"
          r={radius}
          fill="none"
          stroke="url(#scoreGradient)"
          strokeWidth="10"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={dashOffset}
          style={{ transition: 'stroke-dashoffset 1.2s cubic-bezier(0.4,0,0.2,1)' }}
        />
        <defs>
          <linearGradient id="scoreGradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#a78bfa" />
            <stop offset="100%" stopColor="#4f46e5" />
          </linearGradient>
        </defs>
      </svg>
      <div className="absolute text-center">
        <div className="font-mono font-bold text-4xl gradient-text" style={{ lineHeight: 1 }}>{score}</div>
        <div className="text-xs mt-1" style={{ color: 'var(--muted-foreground)' }}>از ۱۰۰</div>
      </div>
    </div>
  );
}

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState<'week' | 'month'>('week');

  return (
    <div className="p-6 md:p-8 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-1">
          <div
            className="w-10 h-10 rounded-xl flex items-center justify-center font-bold text-white font-display"
            style={{ background: 'linear-gradient(135deg, #7c3aed, #4f46e5)' }}
          >
            آ
          </div>
          <div>
            <h1 className="text-xl font-semibold" style={{ color: 'var(--foreground)' }}>
              سلام آرمین 👋
            </h1>
            <p className="text-sm" style={{ color: 'var(--muted-foreground)' }}>
              @armin.design · آخرین تحلیل: ۲ ساعت پیش
            </p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Score Card */}
        <div
          className="rounded-2xl p-6 flex flex-col items-center"
          style={{ background: 'var(--card)', border: '1px solid var(--border)' }}
        >
          <div className="text-sm font-medium mb-4 w-full" style={{ color: 'var(--muted-foreground)' }}>
            Brand Score
          </div>
          <ScoreRing score={overallScore} />
          <div className="w-full mt-6 space-y-3">
            {scoreCategories.map((cat) => (
              <div key={cat.label}>
                <div className="flex justify-between text-xs mb-1">
                  <span style={{ color: 'var(--secondary-foreground)' }}>{cat.label}</span>
                  <span className="font-mono" style={{ color: 'var(--foreground)' }}>{cat.score}</span>
                </div>
                <div
                  className="h-1.5 rounded-full"
                  style={{ background: 'var(--secondary)' }}
                >
                  <div
                    className="h-1.5 rounded-full progress-bar"
                    style={{ width: `${cat.score}%`, background: `linear-gradient(90deg, ${cat.color}, #4f46e5)` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Stats + Chart */}
        <div className="lg:col-span-2 flex flex-col gap-6">
          {/* Quick stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[
              { label: 'فالوور', value: '۴۲,۱۸۰', change: '+۳.۲٪', up: true },
              { label: 'نرخ تعامل', value: '۴.۸٪', change: '+۱.۱٪', up: true },
              { label: 'میانگین ریچ', value: '۱,۹۴۰', change: '-۰.۵٪', up: false },
              { label: 'پست این هفته', value: '۵', change: 'هدف: ۶', up: null },
            ].map((stat) => (
              <div
                key={stat.label}
                className="rounded-xl p-4"
                style={{ background: 'var(--card)', border: '1px solid var(--border)' }}
              >
                <div className="text-xs mb-1" style={{ color: 'var(--muted-foreground)' }}>{stat.label}</div>
                <div className="font-mono font-bold text-xl" style={{ color: 'var(--foreground)' }}>{stat.value}</div>
                <div
                  className="text-xs mt-1 font-medium"
                  style={{
                    color: stat.up === true ? '#4ade80' : stat.up === false ? '#f87171' : 'var(--muted-foreground)',
                  }}
                >
                  {stat.change}
                </div>
              </div>
            ))}
          </div>

          {/* Chart */}
          <div
            className="rounded-2xl p-6 flex-1"
            style={{ background: 'var(--card)', border: '1px solid var(--border)' }}
          >
            <div className="flex items-center justify-between mb-6">
              <div className="text-sm font-medium" style={{ color: 'var(--foreground)' }}>عملکرد هفتگی</div>
              <div className="flex gap-2">
                {(['week', 'month'] as const).map(tab => (
                  <button
                    key={tab}
                    className="px-3 py-1 rounded-lg text-xs font-medium transition-all"
                    style={
                      activeTab === tab
                        ? { background: 'rgba(124,58,237,0.15)', color: '#a78bfa', border: '1px solid rgba(124,58,237,0.3)' }
                        : { color: 'var(--muted-foreground)', border: '1px solid transparent' }
                    }
                    onClick={() => setActiveTab(tab)}
                  >
                    {tab === 'week' ? 'هفته' : 'ماه'}
                  </button>
                ))}
              </div>
            </div>
            {/* Bar chart */}
            <div className="flex items-end gap-2 h-32">
              {weeklyData.map((d, i) => (
                <div key={i} className="flex-1 flex flex-col items-center gap-1">
                  <div className="w-full flex flex-col gap-0.5 items-center" style={{ height: 112 }}>
                    <div className="flex-1 w-full flex items-end gap-0.5">
                      <div
                        className="flex-1 rounded-t-md transition-all"
                        style={{
                          height: `${(d.reach / maxReach) * 100}%`,
                          background: 'rgba(124,58,237,0.3)',
                        }}
                      />
                      <div
                        className="flex-1 rounded-t-md transition-all"
                        style={{
                          height: `${(d.engagement / maxReach) * 100}%`,
                          background: 'linear-gradient(to top, #7c3aed, #a78bfa)',
                        }}
                      />
                    </div>
                  </div>
                  <div className="text-xs" style={{ color: 'var(--muted-foreground)' }}>{d.day}</div>
                </div>
              ))}
            </div>
            <div className="flex gap-4 mt-4">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-sm" style={{ background: 'rgba(124,58,237,0.3)' }} />
                <span className="text-xs" style={{ color: 'var(--muted-foreground)' }}>ریچ</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-sm" style={{ background: '#7c3aed' }} />
                <span className="text-xs" style={{ color: 'var(--muted-foreground)' }}>تعامل</span>
              </div>
            </div>
          </div>
        </div>

        {/* Insights */}
        <div
          className="lg:col-span-3 rounded-2xl p-6"
          style={{ background: 'var(--card)', border: '1px solid var(--border)' }}
        >
          <div className="flex items-center justify-between mb-5">
            <div className="text-sm font-medium" style={{ color: 'var(--foreground)' }}>
              بینش‌های هوش مصنوعی
            </div>
            <span className="tag badge-violet">۴ بینش جدید</span>
          </div>
          <div className="grid md:grid-cols-2 gap-3">
            {insights.map((ins, i) => (
              <div
                key={i}
                className="flex gap-3 p-4 rounded-xl"
                style={{
                  background: 'var(--secondary)',
                  border: `1px solid ${ins.type === 'success' ? 'rgba(74,222,128,0.15)' : ins.type === 'warning' ? 'rgba(251,146,60,0.15)' : 'var(--border)'}`,
                }}
              >
                <span className="text-lg flex-shrink-0">{ins.icon}</span>
                <p className="text-sm leading-relaxed" style={{ color: 'var(--secondary-foreground)' }}>
                  {ins.text}
                </p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
