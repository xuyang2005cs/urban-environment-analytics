import { Check, Database, ScanSearch, ShieldCheck, TriangleAlert } from 'lucide-react'
import type { QualityRun, QualitySummary } from '../api/types'
import { useApi } from '../api/useApi'
import { AsyncState } from '../components/AsyncState'
import { dateTime } from '../lib/format'

export function QualityPage() {
  const summary = useApi<QualitySummary>('/api/quality/summary')
  const runs = useApi<QualityRun[]>('/api/quality/runs?limit=18')
  return <div className="page quality-page">
    <header className="page-heading"><div><p className="eyebrow">Trust the data</p><h1>数据质量中心</h1></div><p>从完整性、唯一性、连续性与数值范围审视分析数据。</p></header>
    <AsyncState loading={summary.loading || runs.loading} error={summary.error || runs.error} retry={() => { summary.retry(); runs.retry() }}>
      {summary.data && runs.data && <QualityContent summary={summary.data} runs={runs.data}/>} 
    </AsyncState>
  </div>
}

function QualityContent({ summary, runs }: { summary: QualitySummary; runs: QualityRun[] }) {
  const findCheck = (term: string) => summary.checks.find((item) => item.name.toLowerCase().includes(term))
  const completeness = findCheck('completeness')
  const duplicates = findCheck('duplicate')
  const continuity = findCheck('continuity')
  return <>
    <section className={`quality-verdict ${summary.status.toLowerCase()}`}><div className="quality-emblem"><ShieldCheck/></div><div><p>当前质量结论</p><h2>{summary.status === 'PASS' ? '分析数据可信' : '存在需要关注的检查'}</h2><span>{summary.passed} / {summary.total} 项检查通过</span></div><div className="quality-records"><small>覆盖记录</small><strong>{summary.records_checked.toLocaleString()}</strong></div></section>
    <section className="quality-measures"><article><ScanSearch/><span>空值率</span><strong>{((completeness?.value ?? 0) * 100).toFixed(2)}%</strong></article><article><Database/><span>重复率</span><strong>{((duplicates?.value ?? 0) * 100).toFixed(2)}%</strong></article><article><TriangleAlert/><span>时间缺口</span><strong>{continuity?.value ?? 0}</strong></article><article><Check/><span>通过检查</span><strong>{summary.passed}</strong></article></section>
    <section className="quality-checks"><div className="section-heading"><div><p className="eyebrow">Check matrix</p><h2>检查矩阵</h2></div><span>最新质量运行汇总</span></div><div className="check-grid">{summary.checks.map((item) => <article key={item.name}><span className={`check-indicator ${item.status.toLowerCase()}`}/><div><strong>{item.name.replaceAll('_', ' ')}</strong><small>{item.unit}</small></div><b>{item.value.toFixed(item.value < 1 ? 4 : 0)}</b></article>)}</div></section>
    <section className="runs-section"><div className="section-heading"><div><p className="eyebrow">Quality history</p><h2>最近质量运行</h2></div></div><div className="table-scroll"><table><thead><tr><th>时间</th><th>城市</th><th>数据集</th><th>状态</th><th>记录</th><th>空值率</th><th>重复</th><th>缺口</th></tr></thead><tbody>{runs.map((run) => <tr key={run.run_id}><td>{dateTime(run.created_at)}</td><td>{run.city}</td><td>{run.dataset}</td><td><span className={`table-status ${run.status.toLowerCase()}`}>{run.status}</span></td><td>{run.rows}</td><td>{(run.null_ratio * 100).toFixed(2)}%</td><td>{(run.duplicate_ratio * 100).toFixed(2)}%</td><td>{run.timestamp_gaps}</td></tr>)}</tbody></table></div></section>
  </>
}
