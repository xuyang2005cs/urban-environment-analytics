import { useCallback, useEffect, useState } from 'react'

import { api } from './client'

export function useApi<T>(path: string) {
  const [data, setData] = useState<T | null>(null)
  const [error, setError] = useState<Error | null>(null)
  const [loading, setLoading] = useState(true)
  const [version, setVersion] = useState(0)

  const retry = useCallback(() => setVersion((value) => value + 1), [])

  useEffect(() => {
    const controller = new AbortController()
    setLoading(true)
    setError(null)
    api<T>(path, controller.signal)
      .then(setData)
      .catch((reason: Error) => {
        if (reason.name !== 'AbortError') setError(reason)
      })
      .finally(() => setLoading(false))
    return () => controller.abort()
  }, [path, version])

  return { data, error, loading, retry }
}
