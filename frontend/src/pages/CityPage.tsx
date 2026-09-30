import { CalendarDays, ChevronDown, Droplets, Gauge, MapPin, Umbrella, Wind } from 'lucide-react'
import { lazy, Suspense, useMemo, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import type { CitySummary, Series } from '../api/types'
import { useApi } from '../api/useApi'
import { AqiStatus } from '../components/AqiStatus'
import { AsyncState, EmptyState } from '../components/AsyncState'
import { ObservationGlyph } from '../components/ObservationGlyph'
import { WeatherIcon } from '../components/WeatherIcon'
import { dateTime, METRIC_META, value, weatherLabel } from '../lib/format'

const cityNames: Record<string,string> = { beijing:'北京', shanghai:'上海', guangzhou:'广州', shenzhen:'深圳', tokyo:'东京', osaka:'大阪' }
const TimeSeriesChart = lazy(() => import('../components/TimeSeriesChart').then((module) => ({ default: module.TimeSeriesChart })))
const weatherMetrics = ['temperature','relative_humidity','wind_speed','precipitation','surface_pressure']
const airMetrics = ['air_quality_index','pm2_5','pm10','nitrogen_dioxide','ozone']

export function CityPage() {
  const { cityId = 'beijing' } = useParams(); const [weatherMetric,setWeatherMetric] = useState('temperature'); const [airMetric,setAirMetric] = useState('air_quality_index')
  const summary = useApi<CitySummary>(`/api/cities/${cityId}/summary?days=7`)
  const weather = useApi<Series>(`/api/cities/${cityId}/weather-series?days=7&metrics=${weatherMetric}`)
  const air = useApi<Series>(`/api/cities/${cityId}/air-quality-series?days=7&metrics=${airMetric}`)
  const state = useMemo(() => ({ loading: summary.loading || weather.loading || air.loading, error: summary.error || weather.error || air.error, retry: () => { summary.retry(); weather.retry(); air.retry() } }), [summary,weather,air])
  return <div className="page city-page"><header className="page-heading"><div><p className="eyebrow">City observation</p><h1>{cityNames[cityId] ?? cityId} · 环境详情</h1></div><div className="city-switch"><label htmlFor="city-select">切换城市</label><div><select id="city-select" value={cityId} onChange={(event) => location.assign(`/cities/${event.target.value}`)}>{Object.entries(cityNames).map(([id,name]) => <option key={id} value={id}>{name}</option>)}</select><ChevronDown/></div></div></header>
    <AsyncState {...state}>{summary.data && weather.data && air.data ? <CityContent summary={summary.data} weather={weather.data} air={air.data} weatherMetric={weatherMetric} airMetric={airMetric} onWeather={setWeatherMetric} onAir={setAirMetric}/> : <EmptyState title="没有可显示的观测" detail="请确认采集管道已经写入此城市的数据。"/>}</AsyncState>
  </div>
}

function MetricSelect({ value: selected, items, onChange, label }: { value:string; items:string[]; onChange:(v:string)=>void; label:string }) { return <label className="metric-select"><span className="sr-only">{label}</span><select value={selected} onChange={(e)=>onChange(e.target.value)}>{items.map((m)=><option key={m} value={m}>{METRIC_META[m].label}</option>)}</select><ChevronDown/></label> }

function CityContent({summary,weather,air,weatherMetric,airMetric,onWeather,onAir}:{summary:CitySummary;weather:Series;air:Series;weatherMetric:string;airMetric:string;onWeather:(v:string)=>void;onAir:(v:string)=>void}) {
 const o=summary.latest
 return <><section className="city-hero"><div className="city-hero-main"><div><p><MapPin size={16}/>{summary.city.country} · {summary.city.name}</p><h2>{value(o.temperature,'temperature')}</h2><span><WeatherIcon code={o.weather_code} size={30}/>{weatherLabel(o.weather_code)}</span><AqiStatus value={o.air_quality_index}/></div><ObservationGlyph humidity={o.relative_humidity} aqi={o.air_quality_index} wind={o.wind_speed} precipitation={o.precipitation}/></div><dl className="city-facts"><div><dt><Droplets/>湿度</dt><dd>{value(o.relative_humidity,'relative_humidity')}</dd></div><div><dt><Wind/>风速</dt><dd>{value(o.wind_speed,'wind_speed')}</dd></div><div><dt><Gauge/>气压</dt><dd>{value(o.surface_pressure,'surface_pressure')}</dd></div><div><dt><Umbrella/>降水</dt><dd>{value(o.precipitation,'precipitation')}</dd></div></dl><footer><span><CalendarDays/>数据范围 {dateTime(summary.period_start)}—{dateTime(summary.period_end)}</span><span>{summary.rows} 条小时观测</span></footer></section>
 <section className="trend-section"><div className="section-heading"><div><p className="eyebrow">Weather timeline</p><h2>天气变化</h2></div><MetricSelect value={weatherMetric} items={weatherMetrics} onChange={onWeather} label="天气指标"/></div><Suspense fallback={<div className="chart-loading">正在绘制天气趋势…</div>}><TimeSeriesChart points={weather.points} metrics={[weatherMetric]}/></Suspense></section>
 <section className="trend-section air-trend"><div className="section-heading"><div><p className="eyebrow">Air quality timeline</p><h2>空气质量</h2></div><MetricSelect value={airMetric} items={airMetrics} onChange={onAir} label="空气质量指标"/></div><Suspense fallback={<div className="chart-loading">正在绘制空气质量趋势…</div>}><TimeSeriesChart points={air.points} metrics={[airMetric]}/></Suspense><div className="metric-note"><strong>指标不共用坐标轴</strong><span>每次聚焦单一量纲，避免将浓度、指数与气象值机械叠加。</span></div></section>
 <div className="next-city"><span>继续探索</span><Link to="/compare">比较六座城市 →</Link></div></>
}
