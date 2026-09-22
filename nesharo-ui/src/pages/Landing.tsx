interface LandingProps {
  onEnterApp: () => void
}

const features = [
  {
    icon: "🔍",
    title: "Brand Audit",
    desc: "تحلیل کامل پیج، بیو، هویت بصری، لحن، محتوا، تعامل و جایگاه برند شما.",
  },
  {
    icon: "📊",
    title: "Brand Score",
    desc: "امتیاز ۰ تا ۱۰۰ در پنج شاخص اختصاصی همراه با تحلیل علت هر امتیاز.",
  },
  {
    icon: "🗺️",
    title: "Growth Roadmap",
    desc: "نقشه راه ۳۰، ۶۰ و ۹۰ روزه متناسب با وضعیت دقیق همان پیج شما.",
  },
  {
    icon: "✍️",
    title: "AI Content Strategist",
    desc: "تقویم محتوا، بازنویسی کپشن، هوک و CTA اختصاصی برند شما.",
  },
]

const competitors = [
  { name: "ChatGPT", content: true, audit: false, roadmap: false },
  { name: "ابزار آنالیتیکس", content: false, audit: "محدود", roadmap: false },
  {
    name: "مشاور انسانی",
    content: true,
    audit: true,
    roadmap: true,
    expensive: true,
  },
  {
    name: "Nesharo",
    content: true,
    audit: true,
    roadmap: true,
    highlight: true,
  },
]

const plans = [
  {
    name: "رایگان",
    price: "۰",
    period: "",
    features: ["تحلیل اولیه پیج", "Brand Score", "۵ ایده محتوا", "گزارش محدود"],
    cta: "شروع رایگان",
    variant: "outline",
  },
  {
    name: "Pro",
    price: "۷۹,۹۰۰",
    period: "/ ماه",
    features: [
      "تحلیل نامحدود پیج",
      "نقشه راه کامل ۳۰/۶۰/۹۰ روزه",
      "تقویم محتوای هوشمند",
      "AI Coach اختصاصی",
      "گزارش هفتگی پیشرفت",
    ],
    cta: "شروع ۷ روز رایگان",
    variant: "primary",
    badge: "محبوب‌ترین",
  },
  {
    name: "Team",
    price: "سفارشی",
    period: "",
    features: [
      "مناسب آژانس‌ها",
      "مدیریت چند پیج",
      "اعضای تیم نامحدود",
      "گزارش مشترک و API",
    ],
    cta: "تماس با ما",
    variant: "outline",
  },
]

const metrics = [
  { label: "کاربر فعال", value: "۱۲,۴۰۰+" },
  { label: "تحلیل انجام شده", value: "۸۴,۰۰۰+" },
  { label: "میانگین رشد فالوور", value: "۳۴٪" },
  { label: "رضایت کاربران", value: "۹۶٪" },
]

const testimonials = [
  {
    name: "آرمین حسینی",
    role: "مدرس طراحی گرافیک · ۴۲K فالوور",
    text: "قبل از Nesharo واقعاً نمی‌دونستم چرا رشدم متوقف شده. بعد از اولین تحلیل، ۳ تا نقطه کور واضح توی محتوام پیدا شد.",
    score: 84,
    avatar: "آ",
  },
  {
    name: "نیلوفر رضایی",
    role: "کوچ کسب‌وکار · ۱۸K فالوور",
    text: "نقشه راه ۹۰ روزه‌ام رو کامل اجرا کردم. تعاملم ۶۸٪ بالا رفت و اولین دوره آموزشیم رو فروختم.",
    score: 91,
    avatar: "ن",
  },
  {
    name: "کامران نوری",
    role: "مدرس زبان · ۶۷K فالوور",
    text: "به عنوان یه مدرس زبان که نه وقت داره نه دونش بازاریابی، این ابزار مثل داشتن یه تیم برندینگ اختصاصیه.",
    score: 78,
    avatar: "ک",
  },
]

export default function Landing({ onEnterApp }: LandingProps) {
  return (
    <div className="min-h-screen" style={{ background: "var(--background)" }}>
      {/* Nav */}
      <nav
        className="fixed top-0 right-0 left-0 z-50 flex items-center justify-between px-8 py-4"
        style={{
          background: "rgba(7,7,15,0.85)",
          backdropFilter: "blur(20px)",
          borderBottom: "1px solid var(--border)",
        }}
      >
        <div className="flex items-center gap-2">
          <div
            className="w-8 h-8 rounded-lg flex items-center justify-center text-white font-bold text-sm"
            style={{ background: "linear-gradient(135deg, #7c3aed, #4f46e5)" }}
          >
            B
          </div>
          <span
            className="font-display font-semibold text-lg"
            style={{ color: "var(--foreground)" }}
          >
            Nesharo
          </span>
        </div>
        <div className="flex items-center gap-3">
          <button
            className="text-sm px-4 py-2 rounded-lg transition-colors"
            style={{ color: "var(--secondary-foreground)" }}
            onMouseEnter={(e) =>
              (e.currentTarget.style.color = "var(--foreground)")
            }
            onMouseLeave={(e) =>
              (e.currentTarget.style.color = "var(--secondary-foreground)")
            }
          >
            قیمت‌گذاری
          </button>
          <button
            className="text-sm px-4 py-2 rounded-lg transition-all font-medium"
            style={{ background: "var(--primary)", color: "#fff" }}
            onClick={onEnterApp}
            onMouseEnter={(e) => (e.currentTarget.style.background = "#6d28d9")}
            onMouseLeave={(e) =>
              (e.currentTarget.style.background = "var(--primary)")
            }
          >
            ورود به پلتفرم →
          </button>
        </div>
      </nav>

      {/* Hero */}
      <section className="relative pt-36 pb-24 px-6 text-center hero-gradient overflow-hidden">
        <div className="noise-overlay absolute inset-0" />
        <div className="relative max-w-4xl mx-auto">
          <span className="badge-violet tag mb-6 inline-flex">
            🤖 هوش مصنوعی تخصصی پرسونال برند
          </span>
          <h1
            className="font-display text-5xl md:text-7xl leading-tight mb-6"
            style={{ fontWeight: 700, lineHeight: 1.15 }}
          >
            <span style={{ color: "var(--foreground)" }}>برند شما را</span>
            <br />
            <span className="gradient-text">تحلیل، امتیازدهی</span>
            <br />
            <span style={{ color: "var(--foreground)" }}>و رشد می‌دهیم</span>
          </h1>
          <p
            className="text-lg md:text-xl mb-10 max-w-2xl mx-auto leading-relaxed"
            style={{ color: "var(--secondary-foreground)" }}
          >
            اولین پلتفرم هوش مصنوعی که به جای تولید محتوا، پرسونال برند شما را
            تحلیل، امتیازدهی و رشد می‌دهد. مخصوص مدرس‌ها و تولیدکنندگان محتوای
            آموزشی اینستاگرام.
          </p>
          <div className="flex items-center justify-center gap-4 flex-wrap">
            <button
              className="px-8 py-4 rounded-xl font-semibold text-white transition-all text-base"
              style={{
                background: "linear-gradient(135deg, #7c3aed, #4f46e5)",
                boxShadow: "0 0 40px rgba(124,58,237,0.35)",
              }}
              onClick={onEnterApp}
              onMouseEnter={(e) =>
                (e.currentTarget.style.transform = "translateY(-2px)")
              }
              onMouseLeave={(e) =>
                (e.currentTarget.style.transform = "translateY(0)")
              }
            >
              تحلیل رایگان پیج من ←
            </button>
            <button
              className="px-8 py-4 rounded-xl font-medium text-base transition-all"
              style={{
                border: "1px solid var(--border)",
                color: "var(--secondary-foreground)",
              }}
              onMouseEnter={(e) =>
                (e.currentTarget.style.borderColor = "rgba(124,58,237,0.4)")
              }
              onMouseLeave={(e) =>
                (e.currentTarget.style.borderColor = "var(--border)")
              }
            >
              نمونه گزارش را ببین
            </button>
          </div>
        </div>

        {/* Metrics strip */}
        <div
          className="relative max-w-3xl mx-auto mt-20 rounded-2xl p-6 grid grid-cols-2 md:grid-cols-4 gap-6"
          style={{
            background: "var(--card)",
            border: "1px solid var(--border)",
          }}
        >
          {metrics.map((m) => (
            <div key={m.label} className="text-center">
              <div className="font-display text-2xl font-bold gradient-text">
                {m.value}
              </div>
              <div
                className="text-sm mt-1"
                style={{ color: "var(--muted-foreground)" }}
              >
                {m.label}
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Features */}
      <section className="py-24 px-6">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-16">
            <h2
              className="font-display text-4xl font-bold mb-4"
              style={{ color: "var(--foreground)" }}
            >
              چهار سیستم هوشمند، یک پلتفرم
            </h2>
            <p style={{ color: "var(--muted-foreground)" }}>
              از تشخیص تا اجرا — هر مرحله رشد برند شما پوشش داده شده است.
            </p>
          </div>
          <div className="grid md:grid-cols-2 gap-6">
            {features.map((f, i) => (
              <div
                key={i}
                className="rounded-2xl p-7 card-hover glow-subtle"
                style={{
                  background: "var(--card)",
                  border: "1px solid var(--border)",
                }}
              >
                <div className="text-3xl mb-4">{f.icon}</div>
                <h3
                  className="font-semibold text-lg mb-2"
                  style={{ color: "var(--foreground)" }}
                >
                  {f.title}
                </h3>
                <p
                  className="text-sm leading-relaxed"
                  style={{ color: "var(--muted-foreground)" }}
                >
                  {f.desc}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section className="py-24 px-6" style={{ background: "var(--muted)" }}>
        <div className="max-w-5xl mx-auto">
          <h2
            className="font-display text-3xl font-bold text-center mb-12"
            style={{ color: "var(--foreground)" }}
          >
            نتایج واقعی کاربران ما
          </h2>
          <div className="grid md:grid-cols-3 gap-6">
            {testimonials.map((t, i) => (
              <div
                key={i}
                className="rounded-2xl p-6 flex flex-col gap-4"
                style={{
                  background: "var(--card)",
                  border: "1px solid var(--border)",
                }}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div
                      className="w-10 h-10 rounded-full flex items-center justify-center font-bold text-white"
                      style={{
                        background: "linear-gradient(135deg, #7c3aed, #4f46e5)",
                      }}
                    >
                      {t.avatar}
                    </div>
                    <div>
                      <div
                        className="font-medium text-sm"
                        style={{ color: "var(--foreground)" }}
                      >
                        {t.name}
                      </div>
                      <div
                        className="text-xs"
                        style={{ color: "var(--muted-foreground)" }}
                      >
                        {t.role}
                      </div>
                    </div>
                  </div>
                  <div className="text-center">
                    <div className="font-mono font-bold text-lg gradient-text">
                      {t.score}
                    </div>
                    <div
                      className="text-xs"
                      style={{ color: "var(--muted-foreground)" }}
                    >
                      امتیاز
                    </div>
                  </div>
                </div>
                <p
                  className="text-sm leading-relaxed"
                  style={{ color: "var(--secondary-foreground)" }}
                >
                  «{t.text}»
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Competitor table */}
      <section className="py-24 px-6">
        <div className="max-w-4xl mx-auto">
          <h2
            className="font-display text-3xl font-bold text-center mb-12"
            style={{ color: "var(--foreground)" }}
          >
            چرا Nesharo؟
          </h2>
          <div
            className="rounded-2xl overflow-hidden"
            style={{ border: "1px solid var(--border)" }}
          >
            <table className="w-full text-sm">
              <thead>
                <tr
                  style={{
                    background: "var(--secondary)",
                    borderBottom: "1px solid var(--border)",
                  }}
                >
                  <th
                    className="text-right py-4 px-6 font-medium"
                    style={{ color: "var(--muted-foreground)" }}
                  >
                    ابزار
                  </th>
                  <th
                    className="py-4 px-6 font-medium text-center"
                    style={{ color: "var(--muted-foreground)" }}
                  >
                    تولید محتوا
                  </th>
                  <th
                    className="py-4 px-6 font-medium text-center"
                    style={{ color: "var(--muted-foreground)" }}
                  >
                    تحلیل برند
                  </th>
                  <th
                    className="py-4 px-6 font-medium text-center"
                    style={{ color: "var(--muted-foreground)" }}
                  >
                    نقشه راه
                  </th>
                </tr>
              </thead>
              <tbody>
                {competitors.map((c, i) => (
                  <tr
                    key={i}
                    className="table-row-hover"
                    style={{
                      borderBottom:
                        i < competitors.length - 1
                          ? "1px solid var(--border)"
                          : "none",
                      background: c.highlight
                        ? "rgba(124,58,237,0.06)"
                        : undefined,
                    }}
                  >
                    <td
                      className="py-4 px-6 font-medium"
                      style={{
                        color: c.highlight ? "#c4b5fd" : "var(--foreground)",
                      }}
                    >
                      {c.name}
                      {c.expensive && (
                        <span className="tag tag-orange mr-2">گران‌قیمت</span>
                      )}
                      {c.highlight && (
                        <span className="tag tag-violet mr-2">
                          شما اینجایید
                        </span>
                      )}
                    </td>
                    {[c.content, c.audit, c.roadmap].map((val, j) => (
                      <td key={j} className="py-4 px-6 text-center">
                        {val === true ? (
                          <span style={{ color: "#4ade80" }}>✓</span>
                        ) : val === false ? (
                          <span style={{ color: "var(--muted-foreground)" }}>
                            —
                          </span>
                        ) : (
                          <span
                            className="text-xs"
                            style={{ color: "#fb923c" }}
                          >
                            {val}
                          </span>
                        )}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </section>

      {/* Pricing is available from the authenticated plans flow */}

      {/* CTA */}
      <section className="py-24 px-6 text-center hero-gradient">
        <div className="max-w-2xl mx-auto">
          <h2
            className="font-display text-4xl font-bold mb-6"
            style={{ color: "var(--foreground)" }}
          >
            اولین تحلیل برند شما رایگان است
          </h2>
          <p className="mb-8" style={{ color: "var(--secondary-foreground)" }}>
            همین الان وارد شوید، پیج اینستاگرام خود را متصل کنید و Brand Score
            خود را دریافت کنید.
          </p>
          <button
            className="px-10 py-4 rounded-xl font-semibold text-white transition-all text-base"
            style={{
              background: "linear-gradient(135deg, #7c3aed, #4f46e5)",
              boxShadow: "0 0 40px rgba(124,58,237,0.35)",
            }}
            onClick={onEnterApp}
            onMouseEnter={(e) =>
              (e.currentTarget.style.transform = "translateY(-2px)")
            }
            onMouseLeave={(e) =>
              (e.currentTarget.style.transform = "translateY(0)")
            }
          >
            شروع رایگان ←
          </button>
        </div>
      </section>

      {/* Footer */}
      <footer
        className="py-10 px-6 text-center"
        style={{ borderTop: "1px solid var(--border)" }}
      >
        <div className="flex items-center justify-center gap-2 mb-3">
          <div
            className="w-6 h-6 rounded-md flex items-center justify-center text-white font-bold text-xs"
            style={{ background: "linear-gradient(135deg, #7c3aed, #4f46e5)" }}
          >
            B
          </div>
          <span
            className="font-display font-semibold"
            style={{ color: "var(--foreground)" }}
          >
            Nesharo
          </span>
        </div>
        <p className="text-xs" style={{ color: "var(--muted-foreground)" }}>
          © ۱۴۰۳ Nesharo — هوش مصنوعی پرسونال برند
        </p>
      </footer>
    </div>
  )
}
