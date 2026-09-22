export type PaymentProvider = "zarinpal" | "nextpay" | "idpay" | "sandbox"
export type PaymentPlan = "starter" | "pro" | "business"
export type PaymentStatus = "idle" | "redirecting" | "verifying" | "success" | "failed"

export type PaymentRequest = {
  provider: PaymentProvider
  plan: PaymentPlan
  amount: number
  callbackUrl: string
}

export type PaymentResponse = {
  status: PaymentStatus
  authority?: string
  message: string
}

export async function createPayment(
  request: PaymentRequest,
): Promise<PaymentResponse> {
  if (request.provider === "sandbox") {
    return {
      status: "redirecting",
      authority: `sandbox-${Date.now()}`,
      message: "درگاه آزمایشی آماده است.",
    }
  }
  return {
    status: "failed",
    message: `اتصال ${request.provider} هنوز پیکربندی نشده است.`,
  }
}

export async function verifyPayment(
  authority: string,
  provider: PaymentProvider,
): Promise<PaymentResponse> {
  if (provider === "sandbox" && authority.startsWith("sandbox-")) {
    return {
      status: "success",
      authority,
      message: "پرداخت آزمایشی با موفقیت تأیید شد.",
    }
  }
  return { status: "failed", message: "تأیید پرداخت انجام نشد." }
}
