import { useState } from "react"

const sections = [
  {
    id: "positioning",
    title: "Positioning · جایگاه‌سازی",
    score: 65,
    status: "warning",
    summary:
      "پیج شما هنوز در ذهن مخاطب جایگاه مشخصی ندارد. تخصص شما در طراحی واضح است، اما «چرا باید شما را انتخاب کنم» در محتوا وجود ندارد.",
    issues: [
      "بیو پیج جایگاه اختصاصی ندارد — «مدرس طراحی» کافی نیست.",
      "هیچ پیام اصلی (Core Message) در محتوا تکرار نمی‌شود.",
      "۶۰٪ مخاطبان شما نمی‌دانند چه تفاوتی با سایر مدرس‌های طراحی دارید.",
    ],
    fixes: [
      "بیو را با فرمت «من به [نیچ] کمک می‌کنم تا [نتیجه]» بازنویسی کنید.",
      "یک جمله موقعیت‌ساز (Positioning Statement) برای محتوا تعریف کنید.",
      "هر هفته ۲ پست به «چرا متفاوتم» اختصاص دهید.",
    ],
  },
  {
    id: "messaging",
    title: "Messaging · پیام‌رسانی",
    score: 78,
    status: "good",
    summary:
      "پیام‌رسانی شما نسبتاً قوی است. هوک‌های کپشن خوب نوشته شده‌اند، اما CTA در اکثر پست‌ها غایب یا ضعیف است.",
    issues: [
      "۷۲٪ پست‌ها CTA واضح ندارند.",
      "لحن محتوا بین «آموزشی» و «انگیزشی» در نوسان است.",
    ],
    fixes: [
      "هر پست باید یک CTA مشخص داشته باشد (ذخیره، کامنت، DM، لینک بیو).",
      "لحن اصلی برند را تعریف و مکتوب کنید.",
    ],
  },
  {
    id: "visual",
    title: "Visual Identity · هویت بصری",
    score: 70,
    status: "ok",
    summary:
      "پالت رنگی نسبتاً ثابت است اما تایپوگرافی پست‌ها یکدست نیست. فید شما در یک نگاه قابل تشخیص نیست.",
    issues: [
      "۴ فونت مختلف در ۳۰ روز اخیر استفاده شده.",
      "نسبت محتوای ویدیویی به تصویری ۲۰:۸۰ است — ریچ پایین‌تر از حد بهینه.",
    ],
    fixes: [
      "یک Brand Kit (رنگ، فونت، لوگو) در Canva یا Figma تعریف کنید.",
      "نسبت ریلز را به ۵۰٪ برسانید.",
    ],
  },
  {
    id: "authority",
    title: "Authority · اقتدار",
    score: 82,
    status: "good",
    summary:
      "محتوای آموزشی شما کیفیت بالایی دارد و مخاطبان را در حوزه تخصصی باور می‌کنند. این قوی‌ترین جنبه برند شماست.",
    issues: ["Social Proof (نتایج دانش‌آموزان) در محتوا کم است."],
    fixes: ["هر ماه ۲ پست Case Study از نتایج دانش‌آموزان منتشر کنید."],
  },
  {
    id: "consistency",
    title: "Consistency · ثبات",
    score: 60,
    status: "bad",
    summary:
      "ثبات پایین‌ترین امتیاز شماست. در ۴۵ روز گذشته سه بار فاصله بیش از ۷ روز بدون انتشار داشته‌اید.",
    issues: [
      "در ۴۵ روز اخیر ۳ gap بیش از ۷ روز.",
      "فرکانس انتشار از ۶ پست/هفته به ۲ پست/هفته رسیده.",
      "هیچ تقویم محتوایی مدون وجود ندارد.",
    ],
    fixes: [
      "حداقل ۴ پست در هفته را به عنوان کف تعهد تعریف کنید.",
      "از تقویم محتوای AI Coach برای برنامه‌ریزی ۴ هفته آینده استفاده کنید.",
      "محتوای Batch تولید کنید — ۱ روز تولید برای ۲ هفته محتوا.",
    ],
  },
]

const statusConfig = {
  good: {
    label: "خوب",
    color: "#4ade80",
    bg: "rgba(74,222,128,0.08)",
    border: "rgba(74,222,128,0.2)",
  },
  ok: {
    label: "متوسط",
    color: "#fb923c",
    bg: "rgba(251,146,60,0.08)",
    border: "rgba(251,146,60,0.2)",
  },
  warning: {
    label: "نیاز به بهبود",
    color: "#fb923c",
    bg: "rgba(251,146,60,0.08)",
    border: "rgba(251,146,60,0.2)",
  },
  bad: {
    label: "ضعیف",
    color: "#f87171",
    bg: "rgba(239,68,68,0.08)",
    border: "rgba(239,68,68,0.2)",
  },
}

export default function BrandAudit() {
  const [active, setActive] = useState(sections[0].id)
  const activeSection = sections.find((s) => s.id === active)!
  const cfg = statusConfig[(activeSection.status as keyof typeof statusConfig)]

  return (
    <div className="p-6 md:p-8 max-w-7xl mx-auto">
      <div className="mb-8">
        <h1
          className="text-2xl font-display font-bold mb-1"
          style={{ color: "var(--foreground)" }}
        >
          Brand Audit
        </h1>
        <p className="text-sm" style={{ color: "var(--muted-foreground)" }}>
          تحلیل کامل پیج @armin.design · ۲ ساعت پیش
        </p>
      </div>

      {/* Score summary row */}
      <div className="grid grid-cols-5 gap-3 mb-8">
        {sections.map((s) => {
          const c = statusConfig[(s.status as keyof typeof statusConfig)]
          return (
            <button
              key={s.id}
              className="rounded-xl p-4 text-right transition-all cursor-pointer"
              style={{
                background: active === s.id ? c.bg : "var(--card)",
                border: `1px solid ${
                  active === s.id ? c.border : "var(--border)"
                }`,
              }}
              onClick={() => setActive(s.id)}
            >
              <div
                className="font-mono font-bold text-2xl mb-1"
                style={{ color: c.color }}
              >
                {s.score}
              </div>
              <div
                className="text-xs leading-tight"
                style={{ color: "var(--muted-foreground)" }}
              >
                {s.title.split(" · ")[1]}
              </div>
            </button>
          )
        })}
      </div>

      {/* Detail panel */}
      <div className="grid md:grid-cols-5 gap-6">
        {/* Section list */}
        <div className="md:col-span-2 flex flex-col gap-2">
          {sections.map((s) => {
            const c = statusConfig[(s.status as keyof typeof statusConfig)]
            return (
              <button
                key={s.id}
                className="flex items-center justify-between p-4 rounded-xl text-right transition-all cursor-pointer w-full"
                style={{
                  background:
                    active === s.id ? "var(--secondary)" : "var(--card)",
                  border: `1px solid ${
                    active === s.id ? "rgba(124,58,237,0.3)" : "var(--border)"
                  }`,
                }}
                onClick={() => setActive(s.id)}
              >
                <div className="text-right">
                  <div
                    className="text-sm font-medium"
                    style={{ color: "var(--foreground)" }}
                  >
                    {s.title.split(" · ")[1]}
                  </div>
                  <div
                    className="text-xs mt-0.5"
                    style={{ color: "var(--muted-foreground)" }}
                  >
                    {s.title.split(" · ")[0]}
                  </div>
                </div>
                <div className="text-left flex flex-col items-end gap-1">
                  <span
                    className="font-mono font-bold text-lg"
                    style={{ color: c.color }}
                  >
                    {s.score}
                  </span>
                  <span className="text-xs" style={{ color: c.color }}>
                    {c.label}
                  </span>
                </div>
              </button>
            )
          })}
        </div>

        {/* Detail */}
        <div className="md:col-span-3 flex flex-col gap-4">
          <div
            className="rounded-2xl p-6"
            style={{
              background: "var(--card)",
              border: "1px solid var(--border)",
            }}
          >
            <div className="flex items-center justify-between mb-4">
              <h2
                className="font-display text-lg font-bold"
                style={{ color: "var(--foreground)" }}
              >
                {activeSection.title}
              </h2>
              <span
                className="tag"
                style={{
                  background: cfg.bg,
                  color: cfg.color,
                  border: `1px solid ${cfg.border}`,
                }}
              >
                {activeSection.score}/100 · {cfg.label}
              </span>
            </div>

            {/* Score bar */}
            <div className="mb-5">
              <div
                className="h-2 rounded-full mb-1"
                style={{ background: "var(--secondary)" }}
              >
                <div
                  className="h-2 rounded-full transition-all duration-700"
                  style={{
                    width: `${activeSection.score}%`,
                    background: `linear-gradient(90deg, ${cfg.color}, ${
                      activeSection.score > 75 ? "#4ade80" : cfg.color
                    })`,
                  }}
                />
              </div>
            </div>

            <p
              className="text-sm leading-relaxed mb-5"
              style={{ color: "var(--secondary-foreground)" }}
            >
              {activeSection.summary}
            </p>

            {/* Issues */}
            <div className="mb-4">
              <div
                className="text-xs font-semibold mb-2 uppercase tracking-wide"
                style={{ color: "var(--muted-foreground)" }}
              >
                مشکلات شناسایی‌شده
              </div>
              <div className="flex flex-col gap-2">
                {activeSection.issues.map((issue, i) => (
                  <div
                    key={i}
                    className="flex gap-3 p-3 rounded-lg text-sm"
                    style={{
                      background: "rgba(239,68,68,0.06)",
                      border: "1px solid rgba(239,68,68,0.12)",
                    }}
                  >
                    <span style={{ color: "#f87171" }}>✗</span>
                    <span style={{ color: "var(--secondary-foreground)" }}>
                      {issue}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            {/* Fixes */}
            <div>
              <div
                className="text-xs font-semibold mb-2 uppercase tracking-wide"
                style={{ color: "var(--muted-foreground)" }}
              >
                اقدامات پیشنهادی
              </div>
              <div className="flex flex-col gap-2">
                {activeSection.fixes.map((fix, i) => (
                  <div
                    key={i}
                    className="flex gap-3 p-3 rounded-lg text-sm"
                    style={{
                      background: "rgba(74,222,128,0.05)",
                      border: "1px solid rgba(74,222,128,0.12)",
                    }}
                  >
                    <span style={{ color: "#4ade80" }}>→</span>
                    <span style={{ color: "var(--secondary-foreground)" }}>
                      {fix}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <button
            className="w-full py-3 rounded-xl font-semibold text-sm text-white transition-all"
            style={{ background: "linear-gradient(135deg, #7c3aed, #4f46e5)" }}
            onMouseEnter={(e) => (e.currentTarget.style.opacity = "0.9")}
            onMouseLeave={(e) => (e.currentTarget.style.opacity = "1")}
          >
            دریافت نقشه راه برای بهبود این شاخص ←
          </button>
        </div>
      </div>
    </div>
  )
}
