/**
 * SMS adapter layer.
 *
 * No real gateway is connected. Each provider below is a placeholder that
 * documents the request shape; `sendOtp` falls back to a local sandbox that
 * always accepts the code printed by `requestOtp` during development.
 */

export type SmsProvider = "kavenegar" | "melipayamak" | "farazsms" | "sandbox"

export type OtpRequest = {
  phone: string
  code: string
  template?: string
}

export type OtpResult = {
  ok: boolean
  provider: SmsProvider
  message: string
}

export type GatewayConfig = {
  provider: SmsProvider
  apiKey: string
  sender: string
}

export const defaultSmsConfig: GatewayConfig = {
  provider: "sandbox",
  apiKey: "",
  sender: "",
}

const providers: Record<Exclude<SmsProvider, "sandbox">, (
  cfg: GatewayConfig,
  req: OtpRequest,
) => Promise<OtpResult>> = {
  kavenegar: async () => ({
    ok: false,
    provider: "kavenegar",
    message: "کلید Kavenegar تنظیم نشده است؛ ارسال واقعی انجام نمی‌شود.",
  }),
  melipayamak: async () => ({
    ok: false,
    provider: "melipayamak",
    message: "اعتبار Melipayamak تنظیم نشده است؛ ارسال واقعی انجام نمی‌شود.",
  }),
  farazsms: async () => ({
    ok: false,
    provider: "farazsms",
    message: "اعتبار FarazSMS تنظیم نشده است؛ ارسال واقعی انجام نمی‌شود.",
  }),
}

let config: GatewayConfig = defaultSmsConfig
const pending = new Map<string, string>()

export function configureSms(next: Partial<GatewayConfig>): GatewayConfig {
  config = { ...config, ...next }
  return config
}

export function getSmsConfig(): GatewayConfig {
  return config
}

export function generateOtp(): string {
  return String(Math.floor(100000 + Math.random() * 900000))
}

export function requestOtp(
  phone: string,
): { code: string; result: Promise<OtpResult> } {
  const code = generateOtp()
  pending.set(phone, code)
  return { code, result: sendOtp({ phone, code }) }
}

export async function sendOtp(request: OtpRequest): Promise<OtpResult> {
  if (config.provider === "sandbox" || !config.apiKey) {
    return {
      ok: true,
      provider: "sandbox",
      message: "حالت آزمایشی: کد تأیید بدون ارسال پیامک معتبر است.",
    }
  }
  return providers[config.provider](config, request)
}

export function verifyOtp(phone: string, code: string): OtpResult {
  const expected = pending.get(phone)
  if (!expected) {
    return {
      ok: false,
      provider: config.provider,
      message: "برای این شماره کدی درخواست نشده است.",
    }
  }
  if (expected !== code) {
    return {
      ok: false,
      provider: config.provider,
      message: "کد وارد‌شده نادرست است.",
    }
  }
  pending.delete(phone)
  return {
    ok: true,
    provider: config.provider,
    message: "شماره با موفقیت تأیید شد.",
  }
}
