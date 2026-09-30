export function Sparkline({ values, label }: { values: number[]; label: string }) {
  if (values.length < 2) return <span className="spark-empty" aria-label={`${label}暂无趋势`}>—</span>
  const min = Math.min(...values); const max = Math.max(...values); const range = max - min || 1
  const points = values.map((point, index) => `${(index / (values.length - 1)) * 92 + 4},${34 - ((point - min) / range) * 26}`).join(' ')
  return <svg className="sparkline" viewBox="0 0 100 40" role="img" aria-label={`${label}趋势，最低${min.toFixed(1)}，最高${max.toFixed(1)}`}><polyline points={points}/></svg>
}
