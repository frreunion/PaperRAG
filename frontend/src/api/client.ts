const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "";

export async function apiRequest<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, options);
  if (!response.ok) {
    const detail = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(detail.detail ?? "请求失败");
  }
  return response.json() as Promise<T>;
}
