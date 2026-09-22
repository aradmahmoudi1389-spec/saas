import { useState } from "react"
import { requestOtp, verifyOtp } from "../services/smsService"

export default function AuthFlow({
  onSuccess,
  onAdmin,
}: {
  onSuccess: () => void
  onAdmin: () => void
}) {
  const [phone, setPhone] = useState("")
  const [code, setCode] = useState("")
  const [step, setStep] = useState<"phone" | "otp">("phone")
  const [message, setMessage] = useState("")
  const send = async () => {
    if (phone.length < 10) {
      setMessage("شماره موبایل را کامل وارد کنید.")
      return
    }
    const request = requestOtp(phone)
    await request.result
    setCode(request.code)
    setStep("otp")
    setMessage("کد آزمایشی آماده شد. در اتصال واقعی از طریق پیامک ارسال می‌شود.")
  }
  const verify = () => {
    const result = verifyOtp(phone, code)
    if (result.ok) onSuccess()
    else setMessage(result.message)
  }
  return (
    <div
      className="fixed inset-0 z-[60] flex items-center justify-center p-4"
      style={{ background: "#0b102066" }}
    >
      <div
        className="w-full max-w-md rounded-2xl p-6"
        style={{ background: "var(--card)", border: "1px solid var(--border)" }}
      >
        <div className="flex justify-between">
          <div>
            <div
              className="text-xs"
              style={{ color: "var(--muted-foreground)" }}
            >
              Nesharo Authentication
            </div>
            <h2 className="text-xl font-bold mt-2">
              {step === "phone" ? "ورود با شماره موبایل" : "تأیید شماره موبایل"}
            </h2>
          </div>
          <button
            onClick={onAdmin}
            className="text-xs"
            style={{ color: "var(--muted-foreground)" }}
          >
            ورود ادمین
          </button>
        </div>
        {step === "phone" ? (
          <>
            <label className="block text-sm mt-7">
              شماره موبایل
              <input
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                dir="ltr"
                placeholder="۰۹۱۲۱۲۳۴۵۶۷"
                className="w-full mt-2 p-3 rounded-xl"
                style={{
                  background: "var(--secondary)",
                  border: "1px solid var(--border)",
                  outline: "none",
                }}
              />
            </label>
            <button
              onClick={send}
              className="w-full mt-5 py-3 rounded-xl text-white"
              style={{ background: "var(--primary)" }}
            >
              ارسال کد تأیید
            </button>
          </>
        ) : (
          <>
            <label className="block text-sm mt-7">
              کد ۶ رقمی
              <input
                value={code}
                onChange={(e) => setCode(e.target.value)}
                dir="ltr"
                maxLength={6}
                className="w-full mt-2 p-3 rounded-xl tracking-[.5em] text-center"
                style={{
                  background: "var(--secondary)",
                  border: "1px solid var(--border)",
                  outline: "none",
                }}
              />
            </label>
            <div className="flex gap-2 mt-5">
              <button
                onClick={() => setStep("phone")}
                className="flex-1 py-3 rounded-xl"
                style={{ background: "var(--secondary)" }}
              >
                تغییر شماره
              </button>
              <button
                onClick={verify}
                className="flex-1 py-3 rounded-xl text-white"
                style={{ background: "var(--primary)" }}
              >
                تأیید و ورود
              </button>
            </div>
          </>
        )}
        {message && (
          <p
            className="text-xs mt-4"
            style={{ color: "var(--muted-foreground)" }}
          >
            {message}
          </p>
        )}
      </div>
    </div>
  )
}
