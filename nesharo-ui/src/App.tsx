import { useEffect, useState } from "react"
import Landing from "./pages/Landing"
import Dashboard from "./pages/Dashboard"
import BrandAudit from "./pages/BrandAudit"
import Roadmap from "./pages/Roadmap"
import ContentAI from "./pages/ContentAI"
import Settings from "./pages/Settings"
import PricingPlans from "./pages/PricingPlans"
import AdminPanel from "./pages/AdminPanel"
import AuthFlow from "./pages/AuthFlow"
import Profile from "./pages/Profile"
import { type Brand } from "./data"
import { api, clearAccessToken, saveAccessToken } from "./services/apiClient"
import { useAppState } from "./state/AppContext"

type Page = "dashboard" | "audit" | "roadmap" | "content" | "calendar" | "competitors" | "analytics" | "reports" | "billing" | "settings" | "profile"

const basePath = import.meta.env.BASE_URL.replace(/\/$/, "")
export function appUrl(path: string) {
  return `${basePath}/#${path}`
}
function routeFromLocation() {
  const route = window.location.hash.slice(1)
  return route || "/"
}
const nav: { id: Page; icon: string; label: string }[] = [
  { id: "dashboard", icon: "⌂", label: "داشبورد" },
  { id: "audit", icon: "◈", label: "Brand Audit" },
  { id: "roadmap", icon: "◌", label: "Roadmap" },
  { id: "content", icon: "✦", label: "Content AI" },
  { id: "calendar", icon: "□", label: "تقویم محتوا" },
  { id: "competitors", icon: "◎", label: "رقبا" },
  { id: "analytics", icon: "↗", label: "آنالیتیکس" },
  { id: "reports", icon: "▤", label: "گزارش‌ها" },
]
function Toast({ message, onClose }: { message: string; onClose: () => void }) {
  useEffect(() => {
    const timer = setTimeout(onClose, 2800)
    return () => clearTimeout(timer)
  }, [message, onClose])
  return (
    <div
      className="fixed bottom-5 left-5 z-[80] rounded-xl px-4 py-3 shadow-xl"
      style={{ background: "var(--foreground)", color: "var(--card)" }}
    >
      ✓ {message} <button onClick={onClose}>×</button>
    </div>
  )
}
function BrandModal({
  onClose,
  onAdd,
}: {
  onClose: () => void
  onAdd: (brand: Brand) => void
}) {
  const [name, setName] = useState("")
  const [industry, setIndustry] = useState("")
  const [step, setStep] = useState(1)
  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
      style={{ background: "#0b102066" }}
    >
      <div
        className="w-full max-w-lg rounded-2xl p-6"
        style={{ background: "var(--card)", border: "1px solid var(--border)" }}
      >
        <div className="flex justify-between mb-6">
          <div>
            <small style={{ color: "var(--muted-foreground)" }}>
              گام {step} از ۲
            </small>
            <h2 className="text-xl font-bold">افزودن برند جدید</h2>
          </div>
          <button onClick={onClose}>×</button>
        </div>
        {step === 1 ? (
          <div className="space-y-4">
            <Field
              label="نام برند"
              value={name}
              onChange={setName}
              placeholder="آکادمی رشد"
            />
            <Field
              label="حوزه فعالیت"
              value={industry}
              onChange={setIndustry}
              placeholder="کوچینگ کسب‌وکار"
            />
          </div>
        ) : (
          <div className="space-y-4">
            <Field
              label="مخاطب هدف"
              value=""
              onChange={() => {}}
              placeholder="کارآفرینان جوان"
            />
            <label className="block text-sm">
              لحن برند
              <select
                className="w-full mt-2 rounded-xl p-3"
                style={{
                  background: "var(--secondary)",
                  border: "1px solid var(--border)",
                }}
              >
                <option>آموزشی و صمیمی</option>
                <option>حرفه‌ای و مطمئن</option>
              </select>
            </label>
          </div>
        )}
        <div className="flex gap-3 mt-7">
          <button
            onClick={step === 1 ? onClose : () => setStep(1)}
            className="flex-1 py-3 rounded-xl"
            style={{ background: "var(--secondary)" }}
          >
            انصراف
          </button>
          <button
            onClick={() =>
              step === 1
                ? setStep(2)
                : onAdd({
                    id: Date.now().toString(),
                    name: name || "برند جدید",
                    handle: "@new.brand",
                    industry: industry || "حوزه فعالیت",
                    audience: "مخاطبان شما",
                    tone: "آموزشی و صمیمی",
                    score: 0,
                  })
            }
            className="flex-1 py-3 rounded-xl text-white"
            style={{ background: "var(--primary)" }}
          >
            {step === 1 ? "ادامه" : "ساخت برند"}
          </button>
        </div>
      </div>
    </div>
  )
}
function Field({
  label,
  value,
  onChange,
  placeholder,
}: {
  label: string
  value: string
  onChange: (value: string) => void
  placeholder: string
}) {
  return (
    <label className="block text-sm">
      {label}
      <input
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        className="w-full mt-2 rounded-xl p-3"
        style={{
          background: "var(--secondary)",
          border: "1px solid var(--border)",
          outline: "none",
        }}
      />
    </label>
  )
}
function Sidebar({
  page,
  setPage,
  brand,
  onBrandClick,
  onExit,
}: {
  page: Page
  setPage: (page: Page) => void
  brand: Brand
  onBrandClick: () => void
  onExit: () => void
}) {
  return (
    <aside
      className="fixed right-0 top-0 bottom-0 hidden w-64 flex-col md:flex"
      style={{
        background: "var(--card)",
        borderLeft: "1px solid var(--border)",
        zIndex: 40,
      }}
    >
      <div className="p-5 border-b" style={{ borderColor: "var(--border)" }}>
        <div className="flex items-center gap-2">
          <div
            className="w-9 h-9 rounded-xl flex items-center justify-center text-white font-bold"
            style={{ background: "linear-gradient(135deg,#6d28d9,#8b5cf6)" }}
          >
            N
          </div>
          <div>
            <b>Nesharo</b>
            <div
              className="text-[11px]"
              style={{ color: "var(--muted-foreground)" }}
            >
              Brand Intelligence
            </div>
          </div>
        </div>
      </div>
      <button
        onClick={onBrandClick}
        className="m-4 rounded-xl p-3 text-right"
        style={{
          background: "var(--secondary)",
          border: "1px solid var(--border)",
        }}
      >
        ◈ <span className="text-sm font-semibold">{brand.name}</span>
        <span className="float-left">⌄</span>
      </button>
      <nav className="flex-1 overflow-y-auto px-3">
        <div
          className="px-3 pb-2 text-[11px]"
          style={{ color: "var(--muted-foreground)" }}
        >
          WORKSPACE
        </div>
        {nav.map((item) => (
          <button
            key={item.id}
            onClick={() => setPage(item.id)}
            className={`w-full flex items-center gap-3 rounded-xl px-3 py-3 mb-1 text-right ${
              page === item.id ? "nav-active" : ""
            }`}
          >
            <span className="w-5 text-center">{item.icon}</span>
            <span className="text-sm">{item.label}</span>
          </button>
        ))}
        <div
          className="px-3 pt-5 pb-2 text-[11px]"
          style={{ color: "var(--muted-foreground)" }}
        >
          حساب
        </div>
        {[
          ["billing", "اشتراک و صورتحساب"],
          ["profile", "پروفایل"],
          ["settings", "تنظیمات"],
        ].map(([id, label]) => (
          <button
            key={id}
            onClick={() => setPage(id as Page)}
            className={`w-full flex items-center gap-3 rounded-xl px-3 py-3 mb-1 text-right ${
              page === id ? "nav-active" : ""
            }`}
          >
            <span>⚙</span>
            <span className="text-sm">{label}</span>
          </button>
        ))}
      </nav>
      <button
        onClick={onExit}
        className="m-4 p-3 text-sm text-right"
        style={{
          color: "var(--muted-foreground)",
          borderTop: "1px solid var(--border)",
        }}
      >
        ↩ خروج
      </button>
    </aside>
  )
}
function Header({
  brand,
  onTheme,
  onBrandClick,
  onNotify,
}: {
  brand: Brand
  onTheme: () => void
  onBrandClick: () => void
  onNotify: () => void
}) {
  return (
    <header
      className="sticky top-0 z-30 flex items-center gap-3 px-5 py-3 md:px-8"
      style={{
        background: "var(--background)dd",
        backdropFilter: "blur(14px)",
        borderBottom: "1px solid var(--border)",
      }}
    >
      <button
        className="hidden md:block rounded-xl px-3 py-2 text-sm"
        style={{ background: "var(--card)", border: "1px solid var(--border)" }}
        onClick={onBrandClick}
      >
        ◈ {brand.name} ⌄
      </button>
      <div className="mr-auto flex gap-2">
        <button
          onClick={onTheme}
          className="w-9 h-9 rounded-xl"
          style={{
            background: "var(--card)",
            border: "1px solid var(--border)",
          }}
        >
          ☼
        </button>
        <button
          onClick={onNotify}
          className="w-9 h-9 rounded-xl"
          style={{
            background: "var(--card)",
            border: "1px solid var(--border)",
          }}
        >
          ♢
        </button>
        <div
          className="w-9 h-9 rounded-full flex items-center justify-center text-white font-bold"
          style={{ background: "var(--primary)" }}
        >
          آ
        </div>
      </div>
    </header>
  )
}
function WorkspacePage({
  page,
  toast,
}: {
  page: Page
  toast: (value: string) => void
}) {
  const data: Record<string, [string, string[]]> = {
    calendar: [
      "تقویم محتوا",
      [
        "شنبه · کاروسل آموزشی · آماده",
        "دوشنبه · ریلز قبل و بعد لوگو · برنامه‌ریزی",
      ],
    ],
    competitors: [
      "هوش رقابتی",
      [
        "@design.school · ۸۲K · تعامل ۶.۲٪",
        "@creativecoach · ۴۶K · تعامل ۵.۸٪",
      ],
    ],
    analytics: [
      "آنالیتیکس",
      [
        "فالوور · ۴۲,۱۸۰ · +۳.۲٪",
        "Reach · ۱۸۲K · +۱۸٪",
        "Engagement · ۸.۴٪ · +۱.۱٪",
      ],
    ],
    reports: [
      "گزارش‌ها",
      ["گزارش ماهانه رشد · آماده دریافت", "تحلیل برند · ۲ ساعت پیش"],
    ],
    billing: [
      "اشتراک و صورتحساب",
      ["پلن فعلی · Pro", "مصرف این ماه · ۶۴٪", "تمدید بعدی · ۲۸ شهریور ۱۴۰۳"],
    ],
  }
  const [title, items] = data[page] || data.analytics
  return (
    <div className="p-5 md:p-8 max-w-6xl mx-auto">
      <h1 className="text-2xl font-bold">{title}</h1>
      <div className="grid md:grid-cols-3 gap-4 my-8">
        {["این هفته", "این ماه", "امتیاز برند"].map((item, i) => (
          <div
            key={item}
            className="rounded-2xl p-5"
            style={{
              background: "var(--card)",
              border: "1px solid var(--border)",
            }}
          >
            <small style={{ color: "var(--muted-foreground)" }}>{item}</small>
            <b className="text-2xl block mt-3">{["۱۲", "۴۸", "۷۲"][i]}</b>
          </div>
        ))}
      </div>
      <div
        className="rounded-2xl p-5"
        style={{ background: "var(--card)", border: "1px solid var(--border)" }}
      >
        {items.map((item) => (
          <div
            key={item}
            className="p-4 rounded-xl mb-2"
            style={{ background: "var(--secondary)" }}
          >
            {item}
            <button
              onClick={() => toast("خروجی آماده شد")}
              className="float-left text-xs"
            >
              جزئیات
            </button>
          </div>
        ))}
      </div>
    </div>
  )
}
function AdminGate({ onLogout }: { onLogout: () => void }) {
  const [allowed, setAllowed] = useState<boolean | null>(null)
  useEffect(() => {
    api.profile()
      .then(({ user }) => setAllowed(user.role === "ADMIN" || user.role === "SUPER_ADMIN"))
      .catch(() => setAllowed(false))
  }, [])
  if (allowed === null) return <div className="min-h-screen flex items-center justify-center">در حال بررسی دسترسی...</div>
  if (!allowed) return <Landing onEnterApp={onLogout} />
  return <AdminPanel onLogout={onLogout} />
}

function AppWorkspace({ initialPage = "dashboard", onRoute }: { initialPage?: Page; onRoute?: (page: Page) => void }) {
  const { setSession, activeBrand, addBrand } = useAppState()
  const [inApp, setInApp] = useState(false)
  const [authOpen, setAuthOpen] = useState(initialPage === "profile")
  const [adminPath, setAdminPath] = useState(false)
  const [page, setPage] = useState<Page>(initialPage)
  const navigate = (next: Page) => {
    setPage(next)
    onRoute?.(next)
  }
  const [brand, setBrand] = useState(activeBrand)
  const [brandModal, setBrandModal] = useState(false)
  const [toastMessage, setToastMessage] = useState("")
  const [theme, setTheme] = useState<"light" | "dark">("light")
  useEffect(() => {
    document.documentElement.dataset.theme = theme
  }, [theme])
  useEffect(() => {
    setBrand(activeBrand)
  }, [activeBrand])
  useEffect(() => {
    api.profile()
      .then(({ user }) => {
        setSession({ phone: user.phone ?? "", firstName: user.firstName ?? "", role: user.role })
        setInApp(true)
      })
      .catch(() => undefined)
  }, [setSession])
  const toast = (value: string) => setToastMessage(value)
  const logout = async () => {
    try {
      await api.logout()
    } finally {
      clearAccessToken()
      setSession(null)
      setInApp(false)
    }
  }
  if (adminPath) return <AdminGate onLogout={() => setAdminPath(false)} />
  if (!inApp)
    return (
      <>
        <Landing onEnterApp={() => setAuthOpen(true)} />
        {authOpen && (
          <AuthFlow
            onSuccess={(result) => {
              saveAccessToken(result.accessToken)
              setSession({
                phone: result.user.phone ?? "",
                firstName: result.user.firstName ?? "",
                role: result.user.role,
              })
              setAuthOpen(false)
              setInApp(true)
            }}
            onAdmin={(result) => {
              saveAccessToken(result.accessToken)
              setSession({
                phone: result.user.phone ?? "",
                firstName: result.user.firstName ?? "",
                role: result.user.role,
              })
              setAuthOpen(false)
              setAdminPath(true)
            }}
          />
        )}
      </>
    )
  return (
    <div className="min-h-screen">
      <Sidebar
        page={page}
        setPage={setPage}
        brand={brand}
        onBrandClick={() => setBrandModal(true)}
        onExit={logout}
      />
      <div className="md:mr-64">
        <Header
          brand={brand}
          onBrandClick={() => setBrandModal(true)}
          onTheme={() => setTheme(theme === "light" ? "dark" : "light")}
          onNotify={() => toast("۳ اعلان جدید دارید")}
        />
        <main>
          {page === "dashboard" && <Dashboard />}
          {page === "audit" && <BrandAudit />}
          {page === "roadmap" && <Roadmap />}
          {page === "content" && <ContentAI />}
          {page === "settings" && <Settings onToast={toast} />}
          {page === "profile" && <Profile onToast={toast} />}
          {!["dashboard", "audit", "roadmap", "content", "settings", "profile"].includes(
            page,
          ) && <WorkspacePage page={page} toast={toast} />}
        </main>
      </div>
      {brandModal && (
        <BrandModal
          onClose={() => setBrandModal(false)}
          onAdd={async (newBrand) => {
            try {
              const saved = await api.createBrand({
                name: newBrand.name,
                industry: newBrand.industry,
                audience: newBrand.audience,
                tone: newBrand.tone,
              })
              const mapped = {
                ...newBrand,
                id: saved.id,
                industry: saved.industry ?? newBrand.industry,
                audience: saved.audience ?? newBrand.audience,
                tone: saved.tone ?? newBrand.tone,
              }
              addBrand(mapped)
              setBrand(mapped)
              setBrandModal(false)
              toast("برند جدید ساخته شد")
            } catch (error) {
              toast(error instanceof Error ? error.message : "ساخت برند انجام نشد")
            }
          }}
        />
      )}
      {toastMessage && (
        <Toast message={toastMessage} onClose={() => setToastMessage("")} />
      )}
    </div>
  )
}
export default function App() {
  const [notice, setNotice] = useState("")
  const route = routeFromLocation()
  const goHome = () => { window.location.href = appUrl("/") }
  if (route === "/pricing-plans") return <PricingPlans onToast={setNotice} />
  if (route.startsWith("/admin")) return <AdminGate onLogout={goHome} />
  return (
    <>
      <AppWorkspace initialPage={route === "/profile" ? "profile" : "dashboard"} onRoute={(page) => { window.location.hash = `/${page}` }} />
      {notice && (
        <div
          className="fixed bottom-5 left-5 z-50 rounded-xl px-4 py-3 text-white"
          style={{ background: "var(--foreground)" }}
        >
          {notice}
        </div>
      )}
    </>
  )
}
