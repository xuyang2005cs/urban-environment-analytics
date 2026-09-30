import { aqiLevel } from '../lib/format'

export function AqiStatus({ value, compact = false }: { value: number | null; compact?: boolean }) {
  const level = aqiLevel(value)
  return <span className={`aqi-status ${level.tone} ${compact ? 'compact' : ''}`}><span className="aqi-dot"/>{compact ? value?.toFixed(0) ?? '—' : `AQI ${value?.toFixed(0) ?? '—'} · ${level.label}`}</span>
}
