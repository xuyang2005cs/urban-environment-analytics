import { ArrowRight, Droplets, Gauge, MapPin, Umbrella, Wind } from 'lucide-react'
import { Link } from 'react-router-dom'
import type { Overview } from '../api/types'
import { useApi } from '../api/useApi'
import { AqiStatus } from '../components/AqiStatus'
import { AsyncState } from '../components/AsyncState'
import { CityMap } from '../components/CityMap'
import { ObservationGlyph } from '../components/ObservationGlyph'
import { Sparkline } from '../components/Sparkline'
import { WeatherIcon } from '../components/WeatherIcon'
import { FadeContent } from '../components/motion/FadeContent'
import { dateTime, value, weatherLabel } from '../lib/format'

export function OverviewPage() {
  const state = useApi<Overview>('/api/overview?city=beijing')
  return <div className="page overview-page"><header className="page-heading"><div><p className="eyebrow">Latest urban observation</p><h1>城市环境概览</h1></div><p>六座城市的天气与空气质量观测，统一于同一条时间轴。</p></header>
    <AsyncState {...state}>{state.data && <OverviewContent data={state.data}/>}</AsyncState>
  </div>
}

function OverviewContent({ data }: { data: Overview }) {
  const { city, observation } = data.selected
  return <>
    <FadeContent><section className="weather-hero" aria-labelledby="hero-city">
      <div className="hero-copy"><p className="hero-location"><MapPin size={16}/>{city.country} · {city.name}</p><h2 id="hero-city">{city.name}</h2><p className="hero-time">当地观测 {dateTime(observation.observed_at, city.timezone)}</p><div className="hero-condition"><WeatherIcon code={observation.weather_code} size={54}/><div><strong>{value(observation.temperature, 'temperature')}</strong><span>{weatherLabel(observation.weather_code)}</span></div></div><AqiStatus value={observation.air_quality_index}/></div>
      <div className="hero-glyph"><ObservationGlyph humidity={observation.relative_humidity} aqi={observation.air_quality_index} wind={observation.wind_speed} precipitation={observation.precipitation}/><span>环境观测图形</span></div>
      <dl className="hero-measures">
        <div><dt><Droplets/>湿度</dt><dd>{value(observation.relative_humidity,'relative_humidity')}</dd></div>
        <div><dt><Wind/>风速</dt><dd>{value(observation.wind_speed,'wind_speed')}</dd></div>
        <div><dt><Gauge/>气压</dt><dd>{value(observation.surface_pressure,'surface_pressure')}</dd></div>
        <div><dt><Umbrella/>降水</dt><dd>{value(observation.precipitation,'precipitation')}</dd></div>
      </dl>
      <Link className="hero-link" to={`/cities/${city.id}`}>查看城市详情 <ArrowRight size={18}/></Link>
    </section></FadeContent>
    <FadeContent delay={0.05}><section className="section-block"><div className="section-heading"><div><p className="eyebrow">City instruments</p><h2>六城观测站</h2></div><span>点击城市进入历史趋势</span></div><div className="city-card-grid">{data.cities.map(({ city: item, observation: obs, temperature_sparkline }) => <Link className="city-card" to={`/cities/${item.id}`} key={item.id}><div className="city-card-top"><div><strong>{item.name}</strong><span>{dateTime(obs.observed_at,item.timezone)}</span></div><WeatherIcon code={obs.weather_code} size={34}/></div><div className="city-card-reading"><b>{value(obs.temperature,'temperature')}</b><AqiStatus value={obs.air_quality_index} compact/></div><Sparkline values={temperature_sparkline} label={`${item.name}气温`}/><div className="city-card-foot"><span>PM2.5 {obs.pm2_5?.toFixed(1) ?? '—'}</span><span>{weatherLabel(obs.weather_code)}</span></div></Link>)}</div></section></FadeContent>
    <FadeContent><section className="section-block map-section"><div className="section-heading"><div><p className="eyebrow">Observation geography</p><h2>观测网络</h2></div><span>地图标记可直接进入城市</span></div><CityMap cities={data.cities}/></section></FadeContent>
    <section className="pipeline-strip"><div><span className={`status-signal ${data.pipeline.status.toLowerCase()}`}/><div><small>最近管道状态</small><strong>{data.pipeline.status === 'SUCCESS' ? '数据链路正常' : data.pipeline.status}</strong></div></div><dl><div><dt>最近运行</dt><dd>{data.pipeline.last_run ? dateTime(data.pipeline.last_run) : '—'}</dd></div><div><dt>新增记录</dt><dd>{data.pipeline.rows_inserted}</dd></div><div><dt>质量状态</dt><dd>{data.pipeline.quality_status ?? '—'}</dd></div></dl><Link to="/pipeline">打开管道监控 <ArrowRight size={16}/></Link></section>
  </>
}
