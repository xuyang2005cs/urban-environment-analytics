export const METRIC_META: Record<string, { label: string; unit: string; digits?: number }> = {
  temperature: { label: '气温', unit: '°C', digits: 1 },
  relative_humidity: { label: '相对湿度', unit: '%', digits: 0 },
  precipitation: { label: '降水', unit: 'mm', digits: 1 },
  wind_speed: { label: '风速', unit: 'km/h', digits: 1 },
  surface_pressure: { label: '地表气压', unit: 'hPa', digits: 0 },
  air_quality_index: { label: 'AQI', unit: '', digits: 0 },
  pm2_5: { label: 'PM2.5', unit: 'μg/m³', digits: 1 },
  pm10: { label: 'PM10', unit: 'μg/m³', digits: 1 },
  nitrogen_dioxide: { label: 'NO₂', unit: 'μg/m³', digits: 1 },
  ozone: { label: 'O₃', unit: 'μg/m³', digits: 1 },
}

export function value(value: number | null | undefined, metric: string) {
  if (value == null || Number.isNaN(value)) return '—'
  const meta = METRIC_META[metric] ?? { unit: '', digits: 1 }
  return `${value.toFixed(meta.digits ?? 1)}${meta.unit ? ` ${meta.unit}` : ''}`
}

export function dateTime(iso: string, timezone?: string) {
  return new Intl.DateTimeFormat('zh-CN', {
    timeZone: timezone,
    month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', hour12: false,
  }).format(new Date(iso))
}

export function shortTime(iso: string) {
  return new Intl.DateTimeFormat('zh-CN', { month: 'numeric', day: 'numeric', hour: '2-digit' }).format(new Date(iso))
}

export function weatherLabel(code: number | null) {
  if (code == null) return '状态待同步'
  if (code === 0) return '晴朗'
  if (code <= 3) return '多云'
  if (code <= 48) return '雾'
  if (code <= 57) return '毛毛雨'
  if (code <= 67) return '降雨'
  if (code <= 77) return '降雪'
  if (code <= 82) return '阵雨'
  if (code <= 86) return '阵雪'
  return '雷暴'
}

export function aqiLevel(aqi: number | null | undefined) {
  if (aqi == null) return { label: '暂无', tone: 'muted' }
  if (aqi <= 20) return { label: '优', tone: 'good' }
  if (aqi <= 40) return { label: '良', tone: 'fair' }
  if (aqi <= 60) return { label: '一般', tone: 'moderate' }
  if (aqi <= 80) return { label: '较差', tone: 'poor' }
  if (aqi <= 100) return { label: '差', tone: 'bad' }
  return { label: '很差', tone: 'severe' }
}
