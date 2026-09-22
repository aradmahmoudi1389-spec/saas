import { useState } from "react"
import { api, type AuthResult } from "../services/apiClient"

export default function AuthFlow({
  onSuccess,
  onAdmin,
}: {
  onSuccess: (result: AuthResult) => void
  onAdmin: () => void
}) {
  const [phone, setPhone] = useState("")
  const [code, setCode] = useState("")
  const [password, setPassword] = useState("")
  const [firstName, setFirstName] = useState("")
  const [mode, setMode] = useState<"login" | "register">("register")
  const [step, setStep] = useState<"phone" | "otp">("phone")
  const [message, setMessage] = useState("")
  const [busy, setBusy] = useState(false)

  const send = () => {
    if (!/^09\d{9}$/.test(phone)) return setMessage("شماره موبایل را کامل وارد کنید.")
    if (mode === "register" && !firstName.trim()) return setMessage("نام خود را وارد کنید.")
    if (password.length < 8) return setMessage("رمز عبور باید حداقل ۸ کاراکتر باشد.")
    setCode("123456")
    setStep("otp")
    setMessage("کد آزمایشی ۱۲۳۴۵۶ است. در اتصال واقعی از طریق پیامک ارسال می‌شود.")
  }

  const verify = async () => {
    if (code !== "123456") return setMessage("کد تأیید نادرست است.")
    setBusy(true)
    try {
      const result = mode === "register"
        ? await api.register({ phone, password, firstName })
        : await api.login({ phone, password })
      onSuccess(result)
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "ورود انجام نشد.")
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="fixed inset-0 z-[60] flex items-center justify-center p-4" style={{ background: "#0b102066" }}>
      <div className="w-full max-w-md rounded-2xl p-6" style={{ background: "var(--card)", border: "1px solid var(--border)" }}>
        <div className="flex justify-between"><div><div className="text-xs" style={{ color: "var(--muted-foreground)" }}>Nesharo Authentication</div><h2 className="text-xl font-bold mt-2">{step === "phone" ? "ورود به حساب" : "تأیید شماره موبایل"}</h2></div><button onClick={onAdmin} className="text-xs" style={{ color: "var(--muted-foreground)" }}>ورود ادمین</button></div>
        {step === "phone" ? <>
          <div className="flex gap-2 mt-6">{([["register", "ثبت‌نام"], ["login", "ورود"]] as const).map(([value, label]) => <button key={value} onClick={() => setMode(value)} className="flex-1 py-2 rounded-xl text-sm" style={{ background: mode === value ? "var(--primary)" : "var(--secondary)", color: mode === value ? "#fff" : "var(--foreground)" }}>{label}</button>)}</div>
          {mode === "register" && <label className="block text-sm mt-5">نام و نام خانوادگی<input value={firstName} onChange={(e) => setFirstName(e.target.value)} className="w-full mt-2 p-3 rounded-xl" style={{ background: "var(--secondary)", border: "1px solid var(--border)", outline: "none" }} /></label>}
          <label className="block text-sm mt-4">شماره موبایل<input value={phone} onChange={(e) => setPhone(e.target.value.replace(/\D/g, ""))} dir="ltr" maxLength={11} placeholder="09121234567" className="w-full mt-2 p-3 rounded-xl" style={{ background: "var(--secondary)", border: "1px solid var(--border)", outline: "none" }} /></label>
          <label className="block text-sm mt-4">رمز عبور<input value={password} onChange={(e) => setPassword(e.target.value)} type="password" dir="ltr" className="w-full mt-2 p-3 rounded-xl" style={{ background: "var(--secondary)", border: "1px solid var(--border)", outline: "none" }} /></label>
          <button onClick={send} className="w-full mt-5 py-3 rounded-xl text-white" style={{ background: "var(--primary)" }}>ارسال کد تأیید</button>
        </> : <>
          <label className="block text-sm mt-7">کد ۶ رقمی<input value={code} onChange={(e) => setCode(e.target.value.replace(/\D/g, ""))} dir="ltr" maxLength={6} className="w-full mt-2 p-3 rounded-xl tracking-[.5em] text-center" style={{ background: "var(--secondary)", border: "1px solid var(--border)", outline: "none" }} /></label>
          <div className="flex gap-2 mt-5"><button onClick={() => setStep("phone")} className="flex-1 py-3 rounded-xl" style={{ background: "var(--secondary)" }}>تغییر اطلاعات</button><button disabled={busy} onClick={verify} className="flex-1 py-3 rounded-xl text-white disabled:opacity-60" style={{ background: "var(--primary)" }}>{busy ? "در حال ورود..." : "تأیید و ورود"}</button></div>
        </>}
        {message && <p className="text-xs mt-4" style={{ color: "var(--muted-foreground)" }}>{message}</p>}
      </div>
    </div>
  )
}
