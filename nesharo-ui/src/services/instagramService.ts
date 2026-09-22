export type InstagramProfile = {
  handle: string
  followers: number
  engagement: number
  bio: string
  connected: boolean
}

export type AuditProgress = {
  label: string
  status: "pending" | "active" | "done"
}

export const auditSteps: AuditProgress[] = [
  { label: "دریافت اطلاعات پروفایل", status: "pending" },
  { label: "تحلیل بیو و جایگاه‌سازی", status: "pending" },
  { label: "بررسی هویت بصری و محتوا", status: "pending" },
  { label: "محاسبه امتیاز برند", status: "pending" },
]

export async function analyzeInstagram(
  handle: string,
  onProgress?: (steps: AuditProgress[]) => void,
): Promise<InstagramProfile> {
  const steps = auditSteps.map((step) => ({ ...step }))
  for (let index = 0; index < steps.length; index += 1) {
    steps[index].status = "active"
    onProgress?.(steps.map((step) => ({ ...step })))
    await new Promise((resolve) => setTimeout(resolve, 300))
    steps[index].status = "done"
  }
  onProgress?.(steps)
  return {
    handle,
    followers: 42180,
    engagement: 8.4,
    bio: "مدرس طراحی برای ساختن برندهای ماندگار",
    connected: false,
  }
}
