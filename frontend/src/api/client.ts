export class ApiError extends Error {
  constructor(
    message: string,
    readonly status: number,
  ) {
    super(message)
  }
}

export async function api<T>(path: string, signal?: AbortSignal): Promise<T> {
  const response = await fetch(path, { signal })
  if (!response.ok) {
    const body = (await response.json().catch(() => null)) as { detail?: string } | null
    throw new ApiError(body?.detail ?? '数据查询失败', response.status)
  }
  return response.json() as Promise<T>
}

export function query(params: Record<string, string | string[] | undefined>): string {
  const result = new URLSearchParams()
  for (const [name, value] of Object.entries(params)) {
    if (Array.isArray(value)) value.forEach((item) => result.append(name, item))
    else if (value) result.set(name, value)
  }
  const encoded = result.toString()
  return encoded ? `?${encoded}` : ''
}
