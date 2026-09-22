import { useState } from "react"
export default function AdminPanel({ onLogout }: { onLogout: () => void }) {
  const [tab, setTab] = useState("dashboard")
  const tabs = [
    ["dashboard", "داشبورد"],
    ["users", "کاربران"],
    ["plans", "پلن‌ها"],
    ["integrations", "اتصال‌ها"],
    ["settings", "تنظیمات ادمین"],
  ]
  return (
    <div className="min-h-screen" style={{ background: "var(--background)" }}>
      <header
        className="flex justify-between items-center p-5 border-b"
        style={{ borderColor: "var(--border)", background: "var(--card)" }}
      >
        <div>
          <b>Nesharo Admin</b>
          <div
            className="text-xs mt-1"
            style={{ color: "var(--muted-foreground)" }}
          >
            SUPER_ADMIN · محیط مدیریت
          </div>
        </div>
        <button onClick={onLogout} className="text-sm">
          خروج
        </button>
      </header>
      <div className="max-w-7xl mx-auto p-5 md:p-8">
        <div className="flex gap-2 overflow-x-auto mb-8">
          {tabs.map(([id, label]) => (
            <button
              key={id}
              onClick={() => setTab(id)}
              className="px-4 py-2 rounded-xl text-sm"
              style={{
                background: tab === id ? "var(--primary)" : "var(--card)",
                color: tab === id ? "#fff" : "var(--foreground)",
                border: "1px solid var(--border)",
              }}
            >
              {label}
            </button>
          ))}
        </div>
        {tab === "dashboard" && (
          <>
            <h1 className="text-2xl font-bold mb-6">نمای کلی سیستم</h1>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {[
                ["کاربران کل", "۱۲,۴۸۰"],
                ["اشتراک فعال", "۲,۱۸۴"],
                ["درآمد ماهانه", "۱.۸ میلیارد"],
                ["تحلیل انجام‌شده", "۸۴,۲۱۰"],
              ].map(([label, value]) => (
                <div
                  className="rounded-2xl p-5"
                  style={{
                    background: "var(--card)",
                    border: "1px solid var(--border)",
                  }}
                  key={label}
                >
                  <div
                    className="text-sm"
                    style={{ color: "var(--muted-foreground)" }}
                  >
                    {label}
                  </div>
                  <b className="text-2xl block mt-3">{value}</b>
                </div>
              ))}
            </div>
          </>
        )}
        {tab === "users" && (
          <Table
            title="مدیریت کاربران"
            rows={[
              "آرمین حسینی · @armin.design · Pro · ۷۲",
              "نیلوفر رضایی · @nilou.coach · Free · ۶۴",
              "کامران نوری · @kamran.lang · Pro · ۷۸",
            ]}
          />
        )}{" "}
        {tab === "plans" && (
          <Table
            title="مدیریت پلن‌ها"
            rows={[
              "Free · ۵ محتوای اولیه · فعال",
              "Pro · محتوای نامحدود · فعال",
              "Business · سه برند · فعال",
            ]}
          />
        )}{" "}
        {tab === "integrations" && (
          <Config
            title="اتصال‌های سیستم"
            fields={["کلید سرویس SMS", "Merchant ID درگاه", "کلید سرویس AI"]}
          />
        )}{" "}
        {tab === "settings" && (
          <Config
            title="تنظیمات ادمین"
            fields={["شماره ادمین", "رمز عبور جدید", "نام فرستنده پیامک"]}
          />
        )}
      </div>
    </div>
  )
}
function Table({ title, rows }: { title: string; rows: string[] }) {
  return (
    <div
      className="rounded-2xl p-5"
      style={{ background: "var(--card)", border: "1px solid var(--border)" }}
    >
      <h1 className="font-bold text-lg mb-5">{title}</h1>
      {rows.map((row) => (
        <div
          key={row}
          className="p-4 rounded-xl mb-2 text-sm"
          style={{ background: "var(--secondary)" }}
        >
          {row}
          <button
            className="float-left text-xs"
            style={{ color: "var(--primary)" }}
          >
            مدیریت
          </button>
        </div>
      ))}
    </div>
  )
}
function Config({ title, fields }: { title: string; fields: string[] }) {
  return (
    <div
      className="max-w-xl rounded-2xl p-6"
      style={{ background: "var(--card)", border: "1px solid var(--border)" }}
    >
      <h1 className="font-bold text-lg mb-6">{title}</h1>
      {fields.map((field) => (
        <label className="block text-sm mb-4" key={field}>
          {field}
          <input
            type="password"
            className="w-full mt-2 p-3 rounded-xl"
            style={{
              background: "var(--secondary)",
              border: "1px solid var(--border)",
              outline: "none",
            }}
            placeholder="تنظیم نشده"
          />
        </label>
      ))}
      <button
        className="px-5 py-3 rounded-xl text-white"
        style={{ background: "var(--primary)" }}
      >
        ذخیره تنظیمات
      </button>
    </div>
  )
}
