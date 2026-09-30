import ReactECharts from 'echarts-for-react'
import type { SeriesPoint } from '../api/types'
import { METRIC_META, shortTime } from '../lib/format'

export function TimeSeriesChart({ points, metrics, height = 320 }: { points: SeriesPoint[]; metrics: string[]; height?: number }) {
  const option = {
    animationDuration: 450,
    color: ['#1f6b57', '#287f91', '#b47626', '#665b8d'],
    grid: { top: 32, right: 16, bottom: 38, left: 48 },
    tooltip: { trigger: 'axis', backgroundColor: '#142821', borderWidth: 0, textStyle: { color: '#fff' } },
    legend: { top: 0, right: 0, textStyle: { color: '#52615b' } },
    xAxis: { type: 'category', boundaryGap: false, data: points.map((p) => shortTime(p.timestamp)), axisLine: { lineStyle: { color: '#ccd5cf' } }, axisLabel: { color: '#66746e', hideOverlap: true } },
    yAxis: { type: 'value', splitLine: { lineStyle: { color: '#e4e9e5' } }, axisLabel: { color: '#66746e' } },
    series: metrics.map((metric, index) => ({ name: METRIC_META[metric]?.label ?? metric, type: 'line', data: points.map((p) => p.values[metric]), symbol: 'none', smooth: .18, lineStyle: { width: index === 0 ? 2.4 : 1.6 }, areaStyle: index === 0 ? { opacity: .07 } : undefined, connectNulls: false })),
  }
  return <div className="chart-wrap"><ReactECharts option={option} style={{ height }} opts={{ renderer: 'svg' }}/><details className="chart-summary"><summary>读取图表数据摘要</summary><p>{points.length} 个小时观测点；指标：{metrics.map((m) => METRIC_META[m]?.label ?? m).join('、')}。</p></details></div>
}
