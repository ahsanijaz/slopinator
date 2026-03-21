import { NavLink } from 'react-router-dom'

const links = [
  { to: '/', label: 'Upload' },
  { to: '/queue', label: 'Queue' },
  { to: '/templates', label: 'Templates' },
  { to: '/themes', label: 'Themes' },
  { to: '/history', label: 'History' },
]

export default function Sidebar() {
  return (
    <nav className="sidebar">
      <div className="sidebar-title">Slopinator</div>
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
    </nav>
  )
}
