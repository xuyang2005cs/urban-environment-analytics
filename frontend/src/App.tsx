import { lazy, Suspense } from 'react'
import { Navigate, Route, Routes } from 'react-router-dom'
import { AppShell } from './components/AppShell'

const AboutPage = lazy(() => import('./pages/AboutPage').then((module) => ({ default: module.AboutPage })))
const CityPage = lazy(() => import('./pages/CityPage').then((module) => ({ default: module.CityPage })))
const ComparePage = lazy(() => import('./pages/ComparePage').then((module) => ({ default: module.ComparePage })))
const OverviewPage = lazy(() => import('./pages/OverviewPage').then((module) => ({ default: module.OverviewPage })))
const PipelinePage = lazy(() => import('./pages/PipelinePage').then((module) => ({ default: module.PipelinePage })))
const QualityPage = lazy(() => import('./pages/QualityPage').then((module) => ({ default: module.QualityPage })))

export function App() {
  return <Suspense fallback={<div className="route-loading" role="status">正在打开观测页面…</div>}><Routes><Route element={<AppShell/>}>
    <Route index element={<Navigate to="/overview" replace/>}/>
    <Route path="overview" element={<OverviewPage/>}/>
    <Route path="cities/:cityId" element={<CityPage/>}/>
    <Route path="compare" element={<ComparePage/>}/>
    <Route path="quality" element={<QualityPage/>}/>
    <Route path="pipeline" element={<PipelinePage/>}/>
    <Route path="about" element={<AboutPage/>}/>
    <Route path="*" element={<Navigate to="/overview" replace/>}/>
  </Route></Routes></Suspense>
}
