export type City = {
  id: string
  name: string
  country: string
  latitude: number
  longitude: number
  timezone: string
}

export type Observation = {
  city: string
  observed_at: string
  local_time: string
  temperature: number | null
  relative_humidity: number | null
  precipitation: number | null
  wind_speed: number | null
  surface_pressure: number | null
  weather_code: number | null
  pm2_5: number | null
  pm10: number | null
  nitrogen_dioxide: number | null
  ozone: number | null
  air_quality_index: number | null
}

export type SeriesPoint = { timestamp: string; values: Record<string, number | null> }
export type CitySnapshot = { city: City; observation: Observation; temperature_sparkline: number[] }

export type Overview = {
  selected: CitySnapshot
  cities: CitySnapshot[]
  recent_weather: SeriesPoint[]
  recent_air_quality: SeriesPoint[]
  pipeline: { status: string; last_run: string | null; rows_inserted: number; quality_status: string | null }
}

export type CitySummary = {
  city: City
  latest: Observation
  period_start: string
  period_end: string
  rows: number
  means: Record<string, number | null>
  totals: Record<string, number | null>
}

export type Series = { city: City; start: string; end: string; points: SeriesPoint[] }

export type Comparison = {
  metric: string
  unit: string
  start: string
  end: string
  items: { city: City; value: number; latest: number | null }[]
}

export type QualitySummary = {
  status: string
  passed: number
  total: number
  records_checked: number
  checks: { name: string; status: string; value: number; unit: string }[]
}

export type QualityRun = {
  run_id: string
  city: string
  dataset: string
  created_at: string
  status: string
  rows: number
  null_ratio: number
  duplicate_ratio: number
  timestamp_gaps: number
  invalid_numeric: number
  range_violations: number
}

export type CollectionRun = {
  started_at: string
  status: string
  city: string
  dataset: string
  rows_fetched: number
  rows_inserted: number
  rows_skipped: number
  quality_status: string | null
  duration_ms: number | null
  error_type: string | null
}

export type Watermark = {
  city: string
  dataset: string
  latest_timestamp: string
  updated_at: string
}

export type Anomaly = { city: string; timestamp: string; metric: string; value: number; score: number }
export type Correlation = { metric_x: string; metric_y: string; correlation: number | null; status: string }
