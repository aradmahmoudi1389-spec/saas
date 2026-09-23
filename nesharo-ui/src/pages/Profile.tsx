import { useEffect, useState } from "react"
import { api } from "../services/apiClient"
import { useAppState } from "../state/AppContext"

type ProfileData = {
  user: { phone: string | null; email: string | null; firstName: string | null; lastName: string | null; role: string }
  imageUrl: string | null
  bio: string | null
  profession: string | null
  niche: string | null
  targetAudience: string | null
  productsServices: string | null
  mainGoal: string | null
  onboardingComplete: boolean
  instagramHandle: string | null
  followers: number | null
  following: number | null
}

const onboardingFields: [keyof ProfileData, string][] = [
  ["profession", "حرفه"],
  ["niche", "حوزه تخصصی"],
  ["targetAudience", "مخاطب هدف"],
  ["productsServices", "محصولات و خدمات"],
  ["mainGoal", "هدف اصلی"],
  ["instagramHandle", "آیدی اینستاگرام"],
]

export default function Profile({ onToast }: { onToast: (message: string) => void }) {
  const { activeBrand } = useAppState()
  const [data, setData] = useState<ProfileData | null>(null)
  const [error, setError] = useState("")
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    api.profile()
      .then((result) => setData(result as unknown as ProfileData))
      .catch((cause) => setError(cause instanceof Error ? cause.message : "دریافت پروفایل انجام نشد."))
  }, [])

  if (error) return <div className="p-8 text-sm" style={{ color: "var(--muted-foreground)" }}>{error}</div>
  if (!data) return <div className="p-8 text-sm" style={{ color: "var(--muted-foreground)" }}>در حال بارگذاری پروفایل...</div>

  const update = (key: keyof ProfileData, value: string) =>
    setData((current) => (current ? { ...current, [key]: value } : current))

  return (
    <div className="p-5 md:p-8 max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold">پروفایل</h1>
      <p className="text-sm mt-2" style={{ color: "var(--muted-foreground)" }}>
        هویت شخصی و اطلاعات پایه‌ای که در تحلیل برند استفاده می‌شود.
      </p>
      <div className="grid sm:grid-cols-2 gap-4 mt-8">
        <Readonly label="نام" value={data.user.firstName ?? "ثبت نشده"} />
        <Readonly label="نام خانوادگی" value={data.user.lastName ?? "ثبت نشده"} />
        <Readonly label="شماره موبایل" value={data.user.phone ?? "ثبت نشده"} />
        <Readonly label="ایمیل" value={data.user.email ?? "ثبت نشده"} />
        <Readonly label="نقش" value={data.user.role} />
        <Readonly label="برند فعال" value={activeBrand.name} />
      </div>
      <div className="rounded-2xl p-6 mt-6" style={{ background: "var(--card)", border: "1px solid var(--border)" }}>
        <h2 className="font-bold text-lg mb-5">اطلاعات تکمیلی برند شخصی</h2>
        <div className="grid sm:grid-cols-2 gap-4">
          {onboardingFields.map(([key, label]) => (
            <label className="text-sm" key={key}>
              {label}
              <input
                value={(data[key] as string | null) ?? ""}
                onChange={(event) => update(key, event.target.value)}
                className="w-full mt-2 rounded-xl p-3"
                style={{ background: "var(--secondary)", border: "1px solid var(--border)", outline: "none" }}
              />
            </label>
          ))}
        </div>
        <label className="block text-sm mt-4">
          بیوگرافی
          <textarea
            value={data.bio ?? ""}
            onChange={(event) => update("bio", event.target.value)}
            rows={3}
            className="w-full mt-2 rounded-xl p-3"
            style={{ background: "var(--secondary)", border: "1px solid var(--border)", outline: "none" }}
          />
        </label>
        <button
          disabled={saving}
          onClick={async () => {
            setSaving(true)
            try {
              await api.updateProfile({
                bio: data.bio,
                profession: data.profession,
                niche: data.niche,
                targetAudience: data.targetAudience,
                productsServices: data.productsServices,
                mainGoal: data.mainGoal,
                instagramHandle: data.instagramHandle,
              })
              onToast("پروفایل ذخیره شد")
            } catch (cause) {
              onToast(cause instanceof Error ? cause.message : "ذخیره پروفایل انجام نشد")
            } finally {
              setSaving(false)
            }
          }}
          className="mt-6 px-5 py-3 rounded-xl text-white disabled:opacity-60"
          style={{ background: "var(--primary)" }}
        >
          {saving ? "در حال ذخیره..." : "ذخیره پروفایل"}
        </button>
      </div>
    </div>
  )
}

function Readonly({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl p-4" style={{ background: "var(--card)", border: "1px solid var(--border)" }}>
      <div className="text-xs" style={{ color: "var(--muted-foreground)" }}>{label}</div>
      <div className="text-sm font-semibold mt-2" dir="auto">{value}</div>
    </div>
  )
}
