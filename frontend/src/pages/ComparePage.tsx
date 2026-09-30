import { BarChart3, ChevronDown, Map as MapIcon } from 'lucide-react'
import { useState } from 'react'
import type { City, Comparison, Overview } from '../api/types'
import { useApi } from '../api/useApi'
import { AsyncState, EmptyState } from '../components/AsyncState'
import { CityMap } from '../components/CityMap'
import { METRIC_META, value } from '../lib/format'

const metrics = ['temperature', 'precipitation', 'wind_speed', 'air_quality_index', 'pm2_5']

export function ComparePage() {
  const [metric, setMetric] = useState('temperature')
  const [view, setView] = useState<'grid' | 'map'>('grid')
  const result = useApi<Comparison>(`/api/comparison?metric=${metric}&days=7`)
  const cities = useApi<City[]>('/api/meta/cities')
  const overview = useApi<Overview>('/api/overview?city=beijing')
  const max = Math.max(...(result.data?.items.map((item) => Math.abs(item.value)) ?? [1]), 1)

  return <div className="page compare-page">
    <header className="page-heading"><div><p className="eyebrow">Cross-city analysis</p><h1>城市环境比较</h1></div><p>以相同时间窗口观察六座城市，不生成主观综合排名。</p></header>
    <div className="compare-controls"><label>比较指标<div><select value={metric} onChange={(event) => setMetric(event.target.value)}>{metrics.map((item) => <option key={item} value={item}>{METRIC_META[item].label}</option>)}</select><ChevronDown/></div></label><div className="segmented" role="group" aria-label="视图切换"><button className={view === 'grid' ? 'active' : ''} onClick={() => setView('grid')}><BarChart3/>网格</button><button className={view === 'map' ? 'active' : ''} onClick={() => setView('map')}><MapIcon/>地图</button></div><span className="city-count">已选择 {cities.data?.length ?? 6} 座城市 · 最近 7 天</span></div>
    <AsyncState loading={result.loading} error={result.error} retry={result.retry}>
      {result.data?.items.length ? (view === 'grid'
        ? <section className="comparison-field"><div className="comparison-axis"><span>较低</span><strong>{METRIC_META[metric].label} · {result.data.unit}</strong><span>较高</span></div><div className="comparison-grid">{result.data.items.map((item, index) => <article key={item.city.id} className="comparison-row"><div className="comparison-rank">{String(index + 1).padStart(2, '0')}</div><div className="comparison-city"><strong>{item.city.name}</strong><span>{item.city.country}</span></div><div className="comparison-bar-track"><span style={{ width: `${Math.max(4, Math.abs(item.value) / max * 100)}%` }}/></div><div className="comparison-value"><strong>{value(item.value, metric)}</strong><span>最新 {value(item.latest, metric)}</span></div></article>)}</div><p className="method-note">均值基于当前分析窗口中的有效小时记录；缺失值不计入计算。</p></section>
        : <section className="compare-map">{overview.data ? <CityMap cities={overview.data.cities}/> : <div className="map-placeholder">正在读取城市位置…</div>}<div className="map-legend"><strong>{METRIC_META[metric].label}</strong>{result.data.items.map((item) => <span key={item.city.id}>{item.city.name}<b>{value(item.value, metric)}</b></span>)}</div></section>)
        : <EmptyState title="当前窗口没有比较数据" detail="调整指标或确认分析层已完成更新。"/>}
    </AsyncState>
  </div>
}
