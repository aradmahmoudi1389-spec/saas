export type ApiError = { code: string; message: string; details?: unknown }
export type ApiResponse<T> = { ok: true; data: T } | { ok: false; error: ApiError }
export type AuthResult = {
  user: { id: string; phone: string | null; firstName: string | null; role: "USER" | "ADMIN" | "SUPER_ADMIN" }
  accessToken: string
}
export type ApiBrand = {
  id: string
  name: string
  industry: string | null
  audience: string | null
  tone: string | null
  positioning?: string | null
}

const baseUrl = import.meta.env.VITE_API_URL ?? "https://saas-bg0w.onrender.com/api/v1"

export async function apiRequest<T>(path: string, init: RequestInit = {}): Promise<T> {
  const response = await fetch(`${baseUrl}${path}`, {
    ...init,
    credentials: "include",
    headers: { "Content-Type": "application/json", ...init.headers },
  })
  const payload = (await response.json()) as ApiResponse<T>
  if (!response.ok || !payload.ok) {
    throw new Error(payload.ok ? "درخواست ناموفق بود." : payload.error.message)
  }
  return payload.data
}

export const api = {
  register: (body: { phone: string; password: string; firstName: string }) =>
    apiRequest<AuthResult>("/auth/register", {
      method: "POST",
      body: JSON.stringify(body),
    }),
  login: (body: { phone: string; password: string }) =>
    apiRequest<AuthResult>("/auth/login", {
      method: "POST",
      body: JSON.stringify(body),
    }),
  profile: () =>
    apiRequest<{
      user: { id: string; phone: string | null; email: string | null; firstName: string | null; lastName: string | null; role: "USER" | "ADMIN" | "SUPER_ADMIN" }
    }>("/profile"),

    apiRequest<{
      brands: ApiBrand[]
      analysis: unknown
      roadmap: unknown
      recentContent: unknown[]
      unreadNotifications: unknown[]
    }>("/dashboard"),
  brands: () => apiRequest<ApiBrand[]>("/brands"),
  createBrand: (body: Omit<ApiBrand, "id">) =>
    apiRequest<ApiBrand>("/brands", {
      method: "POST",
      body: JSON.stringify(body),
    }),
  roadmap: () => apiRequest<unknown[]>("/roadmap"),
  updateTask: (taskId: string, body: { status?: string; progress?: number }) =>
    apiRequest<unknown>(`/roadmap/tasks/${taskId}`, {
      method: "PATCH",
      body: JSON.stringify(body),
    }),
}
