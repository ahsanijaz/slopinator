import { useState } from 'react'
import { NavLink } from 'react-router-dom'
import SettingsPanel from './SettingsPanel'

const links = [
  { to: '/', label: 'Upload' },
  { to: '/queue', label: 'Queue' },
  { to: '/templates', label: 'Templates' },
  { to: '/themes', label: 'Themes' },
  { to: '/history', label: 'History' },
  { to: '/review', label: 'Review Queue' },
]

export default function Sidebar() {
  const [showSettings, setShowSettings] = useState(false)

  return (
    <>
      <nav className="sidebar">
        <div className="sidebar-title">Slopinator</div>
        <div style={{ flex: 1 }}>
          {links.map(({ to, label }) => (
            <NavLink
              key={to}
              to={to}
              end={to === '/'}
              className={({ isActive }) => isActive ? 'active' : ''}
            >
              {label}
            </NavLink>
          ))}
        </div>
        <button className="gear-btn" onClick={() => setShowSettings(true)} title="Admin Settings">
          ⚙
        </button>
      </nav>

      {showSettings && <SettingsPanel onClose={() => setShowSettings(false)} />}
    </>
  )
}
