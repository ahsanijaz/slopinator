import { useEffect, useState } from 'react'
import client from '../api/client'

export default function SettingsPanel({ onClose }) {
  const [token, setToken] = useState(() => localStorage.getItem('admin_token'))
  const [password, setPassword] = useState('')
  const [loginError, setLoginError] = useState('')
  const [mode, setMode] = useState('auto')
  const [saving, setSaving] = useState(false)
  const [msg, setMsg] = useState('')

  useEffect(() => {
    if (token) fetchSettings()
  }, [token])

  const fetchSettings = async () => {
    try {
      const res = await client.get('/api/admin/settings', {
        headers: { Authorization: `Bearer ${token}` },
      })
      setMode(res.data.pipeline_mode)
    } catch {
      // Token expired — clear it
      localStorage.removeItem('admin_token')
      setToken(null)
    }
  }

  const handleLogin = async (e) => {
    e.preventDefault()
    setLoginError('')
    try {
      const res = await client.post('/api/admin/login', { password })
      localStorage.setItem('admin_token', res.data.access_token)
      setToken(res.data.access_token)
      setPassword('')
    } catch {
      setLoginError('Incorrect password.')
    }
  }

  const handleSave = async () => {
    setSaving(true)
    setMsg('')
    try {
      await client.put('/api/admin/settings', { pipeline_mode: mode }, {
        headers: { Authorization: `Bearer ${token}` },
      })
      setMsg('Saved.')
    } catch {
      setMsg('Failed to save.')
    }
    setSaving(false)
  }

  const handleLogout = () => {
    localStorage.removeItem('admin_token')
    setToken(null)
  }

  return (
    <div style={overlayStyle} onClick={onClose}>
      <div style={panelStyle} onClick={e => e.stopPropagation()}>
        <div style={headerStyle}>
          <span style={{ fontWeight: 700, fontSize: 16, color: '#fff' }}>Admin Settings</span>
          <button style={closeBtnStyle} onClick={onClose}>✕</button>
        </div>

        {!token ? (
          <form onSubmit={handleLogin}>
            <p style={{ color: '#888', fontSize: 13, marginBottom: 16 }}>Enter admin password to continue.</p>
            <input
              type="password"
              placeholder="Password"
              value={password}
              onChange={e => setPassword(e.target.value)}
              style={inputStyle}
              autoFocus
            />
            {loginError && <p style={{ color: '#ef4444', fontSize: 12, marginTop: 6 }}>{loginError}</p>}
            <button type="submit" style={{ ...saveBtnStyle, marginTop: 12 }}>Login</button>
          </form>
        ) : (
          <>
            <div style={sectionStyle}>
              <p style={labelStyle}>Pipeline Mode</p>
              <p style={{ color: '#666', fontSize: 12, marginBottom: 12 }}>
                Controls what happens after a video is generated.
              </p>

              <div style={{ display: 'flex', gap: 10 }}>
                <ModeCard
                  active={mode === 'auto'}
                  onClick={() => setMode('auto')}
                  title="Auto"
                  desc="Videos are generated and posted to TikTok automatically with no intervention."
                />
                <ModeCard
                  active={mode === 'review'}
                  onClick={() => setMode('review')}
                  title="Review"
                  desc="Videos land in a review queue. You approve, edit captions, then post."
                />
              </div>
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 20 }}>
              <button style={logoutBtnStyle} onClick={handleLogout}>Logout</button>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                {msg && <span style={{ fontSize: 12, color: msg === 'Saved.' ? '#22c55e' : '#ef4444' }}>{msg}</span>}
                <button style={saveBtnStyle} onClick={handleSave} disabled={saving}>
                  {saving ? 'Saving...' : 'Save'}
                </button>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  )
}

function ModeCard({ active, onClick, title, desc }) {
  return (
    <div onClick={onClick} style={{
      flex: 1, padding: 14, borderRadius: 8, cursor: 'pointer',
      border: `2px solid ${active ? '#6c63ff' : '#2a2a2a'}`,
      background: active ? '#1e1a2e' : '#161616',
      transition: 'all 0.15s',
    }}>
      <div style={{ fontSize: 14, fontWeight: 700, color: active ? '#a78bfa' : '#ccc', marginBottom: 6 }}>
        {active ? '● ' : '○ '}{title}
      </div>
      <div style={{ fontSize: 12, color: '#666', lineHeight: 1.5 }}>{desc}</div>
    </div>
  )
}

const overlayStyle = {
  position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.6)',
  zIndex: 1000, display: 'flex', alignItems: 'flex-end', justifyContent: 'flex-start',
}
const panelStyle = {
  background: '#1a1a1a', border: '1px solid #2a2a2a', borderRadius: '12px 12px 0 0',
  padding: 24, width: 420, marginLeft: 220, marginBottom: 0,
  boxShadow: '0 -4px 32px rgba(0,0,0,0.5)',
}
const headerStyle = {
  display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20,
}
const closeBtnStyle = {
  background: 'none', border: 'none', color: '#666', cursor: 'pointer', fontSize: 18,
}
const sectionStyle = { borderTop: '1px solid #2a2a2a', paddingTop: 16 }
const labelStyle = { fontSize: 13, fontWeight: 600, color: '#ccc', marginBottom: 4 }
const inputStyle = {
  width: '100%', padding: '9px 12px', background: '#111', border: '1px solid #333',
  borderRadius: 6, color: '#e0e0e0', fontSize: 14,
}
const saveBtnStyle = {
  padding: '8px 20px', background: '#6c63ff', color: '#fff',
  border: 'none', borderRadius: 6, cursor: 'pointer', fontSize: 13, fontWeight: 600,
}
const logoutBtnStyle = {
  padding: '8px 14px', background: 'transparent', color: '#666',
  border: '1px solid #333', borderRadius: 6, cursor: 'pointer', fontSize: 12,
}
