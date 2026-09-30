import { AlertTriangle, RefreshCw } from 'lucide-react'
import type { ReactNode } from 'react'

export function AsyncState({ loading, error, children, retry }: { loading: boolean; error: Error | null; children: ReactNode; retry?: () => void }) {
  if (loading) return <div className="loading-panel" role="status"><span className="loading-line" /><span className="loading-line short" /><span className="sr-only">正在加载环境观测数据</span></div>
  if (error) return <div className="error-panel" role="alert"><AlertTriangle size={22}/><div><strong>暂时无法读取数据</strong><p>{error.message}</p></div>{retry && <button className="button quiet" onClick={retry}><RefreshCw size={16}/>重试</button>}</div>
  return children
}

export function EmptyState({ title, detail }: { title: string; detail: string }) {
  return <div className="empty-state"><span className="empty-mark" aria-hidden="true"/><strong>{title}</strong><p>{detail}</p></div>
}
