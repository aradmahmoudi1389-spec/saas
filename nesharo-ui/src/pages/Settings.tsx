import { useState } from "react"

export default function Settings({
  onToast,
}: {
  onToast: (message: string) => void
}) {
  const [section, setSection] = useState("account")
  const [saved, setSaved] = useState(false)
  const [apiKey, setApiKey] = useState("")
  const sections = [
    ["account", "حساب کاربری", "◉"],
    ["security", "امنیت", "◇"],
    ["team", "اعضای تیم", "♧"],
    ["billing", "اشتراک و مصرف", "▣"],
    ["ai", "تنظیمات هوش مصنوعی", "✦"],
  ]
  return (
    <div className="p-5 md:p-8 max-w-6xl mx-auto">
      <div className="mb-8">
        <h1 className="text-2xl font-bold">تنظیمات</h1>
        <p
          className="text-sm mt-2"
          style={{ color: "var(--muted-foreground)" }}
        >
          فضای کاری و حساب Nesharo را مدیریت کنید.
        </p>
      </div>
      <div className="grid md:grid-cols-[220px_1fr] gap-6">
        <aside
          className="rounded-2xl p-2 h-fit"
          style={{
            background: "var(--card)",
            border: "1px solid var(--border)",
          }}
        >
          {sections.map(([id, label, icon]) => (
            <button
              key={id}
              onClick={() => setSection(id)}
              className={`w-full flex items-center gap-3 p-3 rounded-xl text-right mb-1 ${
                section === id ? "nav-active" : ""
              }`}
            >
              <span>{icon}</span>
              <span className="text-sm">{label}</span>
            </button>
          ))}
        </aside>
        <section
          className="rounded-2xl p-6"
          style={{
            background: "var(--card)",
            border: "1px solid var(--border)",
          }}
        >
          {section === "account" && (
            <>
              <h2 className="font-bold text-lg mb-6">اطلاعات حساب</h2>
              <div className="grid md:grid-cols-2 gap-4">
                <Field label="نام" value="آرمین حسینی" />
                <Field label="نام کاربری" value="@armin.design" />
                <Field label="شماره موبایل" value="۰۹۱۲۱۲۳۴۵۶۷" />
                <Field label="ایمیل" value="armin@example.com" />
              </div>
            </>
          )}
          {section === "security" && (
            <>
              <h2 className="font-bold text-lg mb-6">امنیت حساب</h2>
              <div className="space-y-3">
                <SettingRow
                  title="تأیید دومرحله‌ای"
                  desc="امنیت حساب را با کد یکبارمصرف بیشتر کنید."
                  action="فعال‌سازی"
                />
                <SettingRow
                  title="نشست‌های فعال"
                  desc="۲ دستگاه در حال استفاده از حساب هستند."
                  action="مشاهده"
                />
                <SettingRow
                  title="خروج از همه دستگاه‌ها"
                  desc="تمام نشست‌های دیگر را پایان دهید."
                  action="خروج"
                />
              </div>
            </>
          )}
          {section === "team" && (
            <>
              <h2 className="font-bold text-lg mb-2">اعضای تیم</h2>
              <p
                className="text-sm mb-6"
                style={{ color: "var(--muted-foreground)" }}
              >
                همکاران را دعوت کنید و سطح دسترسی آن‌ها را تعیین کنید.
              </p>
              <div className="flex gap-3 mb-6">
                <input
                  className="flex-1 rounded-xl p-3"
                  placeholder="ایمیل همکار"
                  style={{
                    background: "var(--secondary)",
                    border: "1px solid var(--border)",
                    outline: "none",
                  }}
                />
                <button
                  onClick={() => onToast("دعوت‌نامه ارسال شد")}
                  className="px-5 rounded-xl text-white"
                  style={{ background: "var(--primary)" }}
                >
                  دعوت
                </button>
              </div>
              <SettingRow
                title="سارا احمدی"
                desc="sara@example.com · ویرایشگر"
                action="مدیریت"
              />
              <SettingRow
                title="شما"
                desc="armin@example.com · مدیر"
                action=""
              />
            </>
          )}
          {section === "billing" && (
            <>
              <h2 className="font-bold text-lg mb-6">اشتراک و مصرف</h2>
              <div
                className="rounded-2xl p-5 mb-5"
                style={{
                  background: "linear-gradient(135deg,#6d28d9,#8b5cf6)",
                  color: "#fff",
                }}
              >
                <div className="flex justify-between">
                  <span>پلن فعلی</span>
                  <b>PRO</b>
                </div>
                <div className="text-3xl font-bold mt-5">۶۴٪</div>
                <div className="text-sm opacity-80">مصرف اعتبار این ماه</div>
                <div
                  className="h-2 rounded-full mt-4"
                  style={{ background: "#ffffff44" }}
                >
                  <div
                    className="h-2 rounded-full bg-white"
                    style={{ width: "64%" }}
                  />
                </div>
              </div>
              <SettingRow
                title="تمدید اشتراک"
                desc="۲۸ شهریور ۱۴۰۳ · کارت پایان‌یافته با ۱۲۳۴"
                action="مدیریت"
              />
            </>
          )}
          {section === "ai" && (
            <>
              <h2 className="font-bold text-lg mb-2">
                اتصال مدل‌های هوش مصنوعی
              </h2>
              <p
                className="text-sm mb-6"
                style={{ color: "var(--muted-foreground)" }}
              >
                کلیدها فقط در محیط امن ذخیره می‌شوند و در رابط کاربری نمایش داده
                نمی‌شوند.
              </p>
              <label className="block text-sm mb-4">
                کلید API سفارشی
                <input
                  type="password"
                  value={apiKey}
                  onChange={(e) => setApiKey(e.target.value)}
                  className="w-full mt-2 rounded-xl p-3"
                  placeholder="sk-..."
                  style={{
                    background: "var(--secondary)",
                    border: "1px solid var(--border)",
                    outline: "none",
                  }}
                />
              </label>
              <div className="flex flex-wrap gap-2 mb-6">
                {["OpenAI", "Claude", "Perplexity"].map((x) => (
                  <span key={x} className="tag badge-violet">
                    {x} · متصل نیست
                  </span>
                ))}
              </div>
            </>
          )}
          <button
            onClick={() => {
              setSaved(true)
              onToast("تنظیمات ذخیره شد")
              setTimeout(() => setSaved(false), 2000)
            }}
            className="mt-7 px-5 py-3 rounded-xl text-white"
            style={{ background: "var(--primary)" }}
          >
            {saved ? "ذخیره شد ✓" : "ذخیره تغییرات"}
          </button>
        </section>
      </div>
    </div>
  )
}
function Field({ label, value }: { label: string; value: string }) {
  return (
    <label className="text-sm">
      {label}
      <input
        defaultValue={value}
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
function SettingRow({
  title,
  desc,
  action,
}: {
  title: string
  desc: string
  action: string
}) {
  return (
    <div
      className="flex items-center justify-between gap-4 p-4 rounded-xl"
      style={{ background: "var(--secondary)" }}
    >
      <div>
        <div className="text-sm font-semibold">{title}</div>
        <div
          className="text-xs mt-1"
          style={{ color: "var(--muted-foreground)" }}
        >
          {desc}
        </div>
      </div>
      {action && (
        <button
          className="text-xs px-3 py-2 rounded-lg"
          style={{
            background: "var(--card)",
            border: "1px solid var(--border)",
          }}
        >
          {action}
        </button>
      )}
    </div>
  )
}
