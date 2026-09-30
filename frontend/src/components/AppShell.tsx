import { Activity, Building2, GitCompareArrows, Info, Map, Menu, Route, X } from 'lucide-react'
import { useState } from 'react'
import { NavLink, Outlet } from 'react-router-dom'

const links = [
  { to: '/overview', label: '环境概览', icon: Map },
  { to: '/cities/beijing', label: '城市观测', icon: Building2 },
  { to: '/compare', label: '城市比较', icon: GitCompareArrows },
  { to: '/quality', label: '数据质量', icon: Activity },
  { to: '/pipeline', label: '管道监控', icon: Route },
  { to: '/about', label: '关于系统', icon: Info },
]

export function AppShell() {
  const [open, setOpen] = useState(false)
  return <div className="app-shell">
    <a className="skip-link" href="#main-content">跳到主要内容</a>
    <aside className={`side-nav ${open ? 'open' : ''}`}>
      <div className="brand"><span className="brand-mark"><i/><i/><i/></span><div><strong>Urban Environment</strong><small>城市环境观测系统</small></div></div>
      <button className="menu-close" onClick={() => setOpen(false)} aria-label="关闭导航"><X/></button>
      <nav aria-label="主要导航">{links.map(({ to, label, icon: Icon }) => <NavLink key={to} to={to} onClick={() => setOpen(false)} className={({ isActive }) => isActive ? 'active' : ''}><Icon size={18}/><span>{label}</span></NavLink>)}</nav>
      <div className="nav-foot"><span className="live-dot"/>公开数据观测<br/><small>Open-Meteo · DuckDB</small></div>
    </aside>
    <div className="page-frame">
      <header className="mobile-header"><button onClick={() => setOpen(true)} aria-label="打开导航"><Menu/></button><strong>Urban Environment</strong></header>
      <main id="main-content" tabIndex={-1}><Outlet/></main>
    </div>
    {open && <button className="nav-scrim" onClick={() => setOpen(false)} aria-label="关闭导航遮罩"/>}
    <nav className="bottom-nav" aria-label="移动端主要导航">{links.slice(0,5).map(({to,label,icon:Icon}) => <NavLink key={to} to={to}><Icon/><span>{label.slice(0,2)}</span></NavLink>)}</nav>
  </div>
}
