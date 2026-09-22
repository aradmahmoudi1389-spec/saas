import { useState } from "react"

type Phase = "30" | "60" | "90"

const roadmap: Record<Phase, {
  week: string
  tasks: {
    title: string
    desc: string
    priority: "high" | "medium" | "low"
    done: boolean
  }[]
}[]> = {
  "30": [
    {
      week: "هفته ۱–۲",
      tasks: [
        {
          title: "بازنویسی بیو پیج",
          desc: "با فرمت اختصاصی Nesharo — جایگاه + مخاطب + نتیجه",
          priority: "high",
          done: true,
        },
        {
          title: "تعریف Core Message",
          desc: "یک جمله که هر محتوا باید به آن برگردد",
          priority: "high",
          done: true,
        },
        {
          title: "Brand Kit طراحی",
          desc: "رنگ، فونت، و تمپلیت پست اختصاصی",
          priority: "high",
          done: false,
        },
      ],
    },
    {
      week: "هفته ۳–۴",
      tasks: [
        {
          title: "تقویم محتوای ۴ هفته‌ای",
          desc: "۴ پست آموزشی + ۲ پست Social Proof در هفته",
          priority: "high",
          done: false,
        },
        {
          title: "بهبود CTA در پست‌ها",
          desc: "هر پست یک CTA مشخص داشته باشد",
          priority: "medium",
          done: false,
        },
        {
          title: "اولین Case Study",
          desc: "نتیجه یک دانش‌آموز واقعی را به محتوا تبدیل کنید",
          priority: "medium",
          done: false,
        },
      ],
    },
  ],
  "60": [
    {
      week: "هفته ۵–۶",
      tasks: [
        {
          title: "راه‌اندازی Lead Magnet",
          desc: "یک فایل رایگان (PDF یا ویدیو) برای جمع‌آوری ایمیل",
          priority: "high",
          done: false,
        },
        {
          title: "افزایش ریلز به ۵۰٪",
          desc: "نسبت ریلز به پست تصویری را تغییر دهید",
          priority: "medium",
          done: false,
        },
      ],
    },
    {
      week: "هفته ۷–۸",
      tasks: [
        {
          title: "همکاری با ۲ کانتنت کریتور هم‌نیچ",
          desc: "Collab Post یا لایو مشترک",
          priority: "high",
          done: false,
        },
        {
          title: "اولین وبینار رایگان",
          desc: "موضوع: رایج‌ترین اشتباه مخاطبانتان",
          priority: "medium",
          done: false,
        },
      ],
    },
  ],
  "90": [
    {
      week: "هفته ۹–۱۰",
      tasks: [
        {
          title: "راه‌اندازی اولین محصول پولی",
          desc: "ورک‌شاپ یا دوره کوتاه ۴–۶ ساعته",
          priority: "high",
          done: false,
        },
        {
          title: "سیستم Affiliate با ۳ مدرس",
          desc: "تعریف کمیسیون و اشتراک‌گذاری مخاطب",
          priority: "medium",
          done: false,
        },
      ],
    },
    {
      week: "هفته ۱۱–۱۲",
      tasks: [
        {
          title: "بررسی KPI ها و تحلیل مجدد",
          desc: "Brand Score باید به ۸۵+ رسیده باشد",
          priority: "high",
          done: false,
        },
        {
          title: "برنامه‌ریزی فاز بعدی",
          desc: "توسعه به یوتیوب یا لینکدین",
          priority: "low",
          done: false,
        },
      ],
    },
  ],
}

const priorityConfig = {
  high: {
    label: "فوری",
    color: "#f87171",
    bg: "rgba(239,68,68,0.1)",
    border: "rgba(239,68,68,0.2)",
  },
  medium: {
    label: "مهم",
    color: "#fb923c",
    bg: "rgba(251,146,60,0.1)",
    border: "rgba(251,146,60,0.2)",
  },
  low: {
    label: "عادی",
    color: "#60a5fa",
    bg: "rgba(96,165,250,0.1)",
    border: "rgba(96,165,250,0.2)",
  },
}

export default function Roadmap() {
  const [phase, setPhase] = useState<Phase>("30")
  const [done, setDone] = useState<Set<string>>(
    new Set(["هفته ۱–۲-بازنویسی بیو پیج", "هفته ۱–۲-تعریف Core Message"]),
  )

  const toggleDone = (key: string) => {
    setDone((prev) => {
      const next = new Set(prev)
      next.has(key) ? next.delete(key) : next.add(key)
      return next
    })
  }

  const totalTasks = roadmap[phase].flatMap((w) => w.tasks).length
  const doneTasks = roadmap[phase]
    .flatMap((w) => w.tasks)
    .filter((t, i, arr) => {
      const key = `${roadmap[phase].find((w) => w.tasks.includes(t))?.week}-${t.title}`
      return done.has(key)
    }).length

  return (
    <div className="p-6 md:p-8 max-w-5xl mx-auto">
      <div className="mb-8">
        <h1
          className="text-2xl font-display font-bold mb-1"
          style={{ color: "var(--foreground)" }}
        >
          Growth Roadmap
        </h1>
        <p className="text-sm" style={{ color: "var(--muted-foreground)" }}>
          نقشه راه شخصی‌سازی‌شده برای @armin.design
        </p>
      </div>

      {/* Phase tabs */}
      <div className="flex gap-3 mb-8">
        {(["30", "60", "90"] as Phase[]).map((p) => (
          <button
            key={p}
            className="px-6 py-3 rounded-xl font-medium text-sm transition-all"
            style={
              phase === p
                ? {
                    background: "rgba(124,58,237,0.15)",
                    color: "#a78bfa",
                    border: "1px solid rgba(124,58,237,0.3)",
                  }
                : {
                    background: "var(--card)",
                    color: "var(--muted-foreground)",
                    border: "1px solid var(--border)",
                  }
            }
            onClick={() => setPhase(p)}
          >
            {p} روز
          </button>
        ))}
      </div>

      {/* Progress */}
      <div
        className="rounded-2xl p-5 mb-6"
        style={{ background: "var(--card)", border: "1px solid var(--border)" }}
      >
        <div className="flex justify-between items-center mb-3">
          <span
            className="text-sm font-medium"
            style={{ color: "var(--foreground)" }}
          >
            پیشرفت فاز {phase} روزه
          </span>
          <span
            className="font-mono text-sm"
            style={{ color: "var(--muted-foreground)" }}
          >
            {doneTasks}/{totalTasks} وظیفه
          </span>
        </div>
        <div
          className="h-2 rounded-full"
          style={{ background: "var(--secondary)" }}
        >
          <div
            className="h-2 rounded-full transition-all duration-700"
            style={{
              width: `${totalTasks > 0 ? (doneTasks / totalTasks) * 100 : 0}%`,
              background: "linear-gradient(90deg, #7c3aed, #4f46e5)",
            }}
          />
        </div>
      </div>

      {/* Tasks */}
      <div className="space-y-6">
        {roadmap[phase].map((week) => (
          <div key={week.week}>
            <div className="flex items-center gap-3 mb-3">
              <div
                className="h-px flex-1"
                style={{ background: "var(--border)" }}
              />
              <span
                className="text-xs font-semibold px-3 py-1 rounded-full"
                style={{
                  background: "var(--secondary)",
                  color: "var(--muted-foreground)",
                }}
              >
                {week.week}
              </span>
              <div
                className="h-px flex-1"
                style={{ background: "var(--border)" }}
              />
            </div>
            <div className="space-y-3">
              {week.tasks.map((task) => {
                const key = `${week.week}-${task.title}`
                const isDone = done.has(key)
                const pc = priorityConfig[task.priority]
                return (
                  <div
                    key={key}
                    className="rounded-xl p-4 flex items-start gap-4 transition-all cursor-pointer"
                    style={{
                      background: isDone
                        ? "rgba(74,222,128,0.04)"
                        : "var(--card)",
                      border: `1px solid ${
                        isDone ? "rgba(74,222,128,0.15)" : "var(--border)"
                      }`,
                    }}
                    onClick={() => toggleDone(key)}
                  >
                    <div
                      className="w-5 h-5 rounded-md flex-shrink-0 flex items-center justify-center mt-0.5 transition-all"
                      style={{
                        background: isDone ? "#4ade80" : "var(--secondary)",
                        border: `1px solid ${
                          isDone ? "#4ade80" : "var(--border)"
                        }`,
                      }}
                    >
                      {isDone && (
                        <span
                          style={{
                            color: "#000",
                            fontSize: 11,
                            fontWeight: 700,
                          }}
                        >
                          ✓
                        </span>
                      )}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 flex-wrap mb-1">
                        <span
                          className="text-sm font-medium"
                          style={{
                            color: isDone
                              ? "var(--muted-foreground)"
                              : "var(--foreground)",
                            textDecoration: isDone ? "line-through" : "none",
                          }}
                        >
                          {task.title}
                        </span>
                        <span
                          className="tag text-xs"
                          style={{
                            background: pc.bg,
                            color: pc.color,
                            border: `1px solid ${pc.border}`,
                          }}
                        >
                          {pc.label}
                        </span>
                      </div>
                      <p
                        className="text-xs"
                        style={{ color: "var(--muted-foreground)" }}
                      >
                        {task.desc}
                      </p>
                    </div>
                  </div>
                )
              })}
            </div>
          </div>
        ))}
      </div>

      {/* AI Coach prompt */}
      <div
        className="mt-8 rounded-2xl p-6"
        style={{
          background: "rgba(124,58,237,0.08)",
          border: "1px solid rgba(124,58,237,0.2)",
        }}
      >
        <div className="flex items-start gap-4">
          <div
            className="w-10 h-10 rounded-xl flex-shrink-0 flex items-center justify-center text-white font-bold"
            style={{ background: "linear-gradient(135deg, #7c3aed, #4f46e5)" }}
          >
            AI
          </div>
          <div>
            <div
              className="text-sm font-medium mb-1"
              style={{ color: "#c4b5fd" }}
            >
              AI Coach می‌گوید:
            </div>
            <p
              className="text-sm leading-relaxed"
              style={{ color: "var(--secondary-foreground)" }}
            >
              اولویت اول این هفته: بیو پیج. این تغییر کمتر از ۳۰ دقیقه زمان
              می‌برد اما بیشترین تأثیر را روی نرخ تبدیل بازدیدکننده به فالوور
              دارد. می‌خواهید الان آن را با هم بنویسیم؟
            </p>
            <button
              className="mt-3 px-4 py-2 rounded-lg text-sm font-medium text-white transition-all"
              style={{
                background: "rgba(124,58,237,0.4)",
                border: "1px solid rgba(124,58,237,0.4)",
              }}
              onMouseEnter={(e) =>
                (e.currentTarget.style.background = "rgba(124,58,237,0.6)")
              }
              onMouseLeave={(e) =>
                (e.currentTarget.style.background = "rgba(124,58,237,0.4)")
              }
            >
              بله، بنویسیم ←
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
