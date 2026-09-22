import { useState } from "react"
import {
  createPayment,
  verifyPayment,
  type PaymentPlan,
  type PaymentProvider,
} from "../services/paymentService"

const plans: {
  id: PaymentPlan
  name: string
  price: string
  features: string[]
}[] = [
  {
    id: "starter",
    name: "Starter",
    price: "رایگان",
    features: ["۵ محتوای اولیه", "تحلیل پایه برند", "امتیاز برند"],
  },
  {
    id: "pro",
    name: "Pro",
    price: "۷۹۹٬۰۰۰ تومان / ماه",
    features: ["تولید نامحدود محتوا", "Roadmap کامل", "گزارش هفتگی"],
  },
  {
    id: "business",
    name: "Business",
    price: "۲٬۴۹۰٬۰۰۰ تومان / ماه",
    features: ["۳ برند فعال", "همکاری تیمی", "پشتیبانی اختصاصی"],
  },
]
export default function PricingPlans({
  onToast,
}: {
  onToast: (message: string) => void
}) {
  const [selected, setSelected] = useState<PaymentPlan>("pro")
  const [provider, setProvider] = useState<PaymentProvider>("sandbox")
  const [status, setStatus] = useState("")
  const pay = async () => {
    setStatus("در حال آماده‌سازی درگاه...")
    const res = await createPayment({
      provider,
      plan: selected,
      amount: selected === "pro" ? 799000 : 2490000,
      callbackUrl: "/pricing-plans/callback",
    })
    if (res.status === "redirecting" && res.authority) {
      setStatus("در حال تأیید پرداخت آزمایشی...")
      const verified = await verifyPayment(res.authority, provider)
      setStatus(verified.message)
      if (verified.status === "success") onToast("اشتراک شما فعال شد")
    } else setStatus(res.message)
  }
  return (
    <div className="p-5 md:p-8 max-w-6xl mx-auto">
      <div className="max-w-2xl mb-10">
        <span className="tag badge-violet">رشد مستمر برند شخصی</span>
        <h1 className="text-3xl font-bold mt-4">برندی بساز که به یاد بماند</h1>
        <p className="mt-3" style={{ color: "var(--muted-foreground)" }}>
          پلن مناسب مسیر خود را انتخاب کنید. شروع با Starter رایگان است.
        </p>
      </div>
      <div className="grid md:grid-cols-3 gap-5">
        {plans.map((plan) => (
          <button
            key={plan.id}
            onClick={() => setSelected(plan.id)}
            className="text-right rounded-2xl p-6"
            style={{
              background: "var(--card)",
              border: `2px solid ${
                selected === plan.id ? "var(--primary)" : "var(--border)"
              }`,
            }}
          >
            <div className="flex justify-between">
              <h2 className="font-bold text-lg">{plan.name}</h2>
              {selected === plan.id && (
                <span className="tag badge-violet">انتخاب شد</span>
              )}
            </div>
            <div className="text-xl font-bold mt-6">{plan.price}</div>
            <ul
              className="mt-6 space-y-3 text-sm"
              style={{ color: "var(--secondary-foreground)" }}
            >
              {plan.features.map((x) => (
                <li key={x}>✓ {x}</li>
              ))}
            </ul>
          </button>
        ))}
      </div>
      {selected !== "starter" && (
        <div
          className="max-w-xl mt-8 rounded-2xl p-6"
          style={{
            background: "var(--card)",
            border: "1px solid var(--border)",
          }}
        >
          <h2 className="font-bold">تکمیل خرید</h2>
          <div className="flex gap-2 mt-4">
            {([
              "sandbox",
              "zarinpal",
              "nextpay",
              "idpay",
            ] as PaymentProvider[]).map((item) => (
              <button
                key={item}
                onClick={() => setProvider(item)}
                className="tag"
                style={{
                  background:
                    provider === item ? "var(--primary)" : "var(--secondary)",
                  color: provider === item ? "#fff" : "var(--foreground)",
                }}
              >
                {item}
              </button>
            ))}
          </div>
          <button
            onClick={pay}
            className="mt-5 w-full py-3 rounded-xl text-white"
            style={{ background: "var(--primary)" }}
          >
            ادامه به پرداخت
          </button>
          {status && (
            <p
              className="text-sm mt-4"
              style={{ color: "var(--secondary-foreground)" }}
            >
              {status}
            </p>
          )}
        </div>
      )}
    </div>
  )
}
