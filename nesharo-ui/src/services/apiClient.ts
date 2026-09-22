export type ApiError = { code: string; message: string; details?: unknown }
export type ApiResponse<T> = { ok: true; data: T } | { ok: false; error: ApiError }

const baseUrl = import.meta.env.VITE_API_URL ?? 'http://localhost:4000/api/v1'

export async function apiRequest<T>(path: string, init: RequestInit = {}): Promise<T> {
  const response = await fetch(`${baseUrl}${path}`, { ...init, credentials: 'include', headers: { 'Content-Type': 'application/json', ...init.headers } })
  const payload = (await response.json()) as ApiResponse<T>
  if (!response.ok || !payload.ok) throw new Error(payload.ok ? 'درخواست ناموفق بود.' : payload.error.message)
  return payload.data
}

export const api = {
  register: (body: { phone: string; password: string; firstName: string }) => apiRequest('/auth/register', { method: 'POST', body: JSON.stringify(body) }),
  login: (body: { phone: string; password: string }) => apiRequest('/auth/login', { method: 'POST', body: JSON.stringify(body) }),
  logout: () => apiRequest('/auth/logout', { method: 'POST' }),
  dashboard: () => apiRequest('/dashboard'),
  brands: () => apiRequest('/brands'),
  createBrand: (body: Record<string, string>) => apiRequest('/brands', { method: 'POST', body: JSON.stringify(body) }),
  roadmap: () => apiRequest('/roadmap'),
  updateTask: (taskId: string, body: { status?: string; progress?: number }) => apiRequest(`/roadmap/tasks/${taskId}`, { method: 'PATCH', body: JSON.stringify(body) }),
}
