import { useEffect, useState } from 'react'
import client from '../api/client'

export default function ThemesPage() {
  const [themes, setThemes] = useState([])
  const [form, setForm] = useState({ name: '', description: '', is_default: false })
  const [error, setError] = useState('')

  const fetchThemes = () => client.get('/api/themes/').then(r => setThemes(r.data)).catch(() => {})

  useEffect(() => { fetchThemes() }, [])

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    try {
      await client.post('/api/themes/', form)
      setForm({ name: '', description: '', is_default: false })
      fetchThemes()
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create theme.')
    }
  }

  const handleDelete = async (id) => {
    await client.delete(`/api/themes/${id}`)
    fetchThemes()
  }

  return (
    <div>
      <h1>Themes</h1>

      <form onSubmit={handleSubmit} style={formStyle}>
        <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap', alignItems: 'flex-end' }}>
          <div>
            <label style={labelStyle}>Name</label>
            <input
              style={inputStyle}
              placeholder="e.g. cinematic"
              value={form.name}
              onChange={e => setForm(f => ({ ...f, name: e.target.value }))}
              required
            />
          </div>
          <div style={{ flex: 1, minWidth: 180 }}>
            <label style={labelStyle}>Description</label>
            <input
              style={{ ...inputStyle, width: '100%' }}
              placeholder="Optional description"
              value={form.description}
              onChange={e => setForm(f => ({ ...f, description: e.target.value }))}
            />
          </div>
          <label style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 13, color: '#aaa', marginBottom: 1 }}>
            <input
              type="checkbox"
              checked={form.is_default}
              onChange={e => setForm(f => ({ ...f, is_default: e.target.checked }))}
            />
            Default
          </label>
          <button type="submit" style={addBtnStyle}>Add Theme</button>
        </div>
        {error && <p style={{ color: '#ef4444', fontSize: 12, marginTop: 8 }}>{error}</p>}
      </form>

      {themes.length === 0 ? (
        <p>No themes yet. Add one above.</p>
      ) : (
        <table style={tableStyle}>
          <thead>
            <tr>
              {['Name', 'Description', 'Default', ''].map(h => (
                <th key={h} style={thStyle}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {themes.map(t => (
              <tr key={t.id}>
                <td style={tdStyle}>{t.name}</td>
                <td style={{ ...tdStyle, color: '#888' }}>{t.description || '—'}</td>
                <td style={tdStyle}>{t.is_default ? '✓' : ''}</td>
                <td style={tdStyle}>
                  <button style={deleteBtnStyle} onClick={() => handleDelete(t.id)}>Delete</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  )
}

const labelStyle = { display: 'block', fontSize: 12, color: '#888', marginBottom: 4 }
const inputStyle = {
  padding: '8px 10px', background: '#1a1a1a', border: '1px solid #333',
  borderRadius: 6, color: '#e0e0e0', fontSize: 13,
}
const formStyle = {
  background: '#1a1a1a', border: '1px solid #2a2a2a', borderRadius: 8,
  padding: 16, marginBottom: 24,
}
const addBtnStyle = {
  padding: '8px 16px', background: '#6c63ff', color: '#fff',
  border: 'none', borderRadius: 6, cursor: 'pointer', fontSize: 13, fontWeight: 600,
}
const tableStyle = { width: '100%', borderCollapse: 'collapse', fontSize: 13 }
const thStyle = {
  textAlign: 'left', padding: '8px 12px', color: '#888',
  borderBottom: '1px solid #2a2a2a', fontWeight: 500,
}
const tdStyle = { padding: '10px 12px', borderBottom: '1px solid #1e1e1e', color: '#ccc' }
const deleteBtnStyle = {
  padding: '4px 10px', background: 'transparent', border: '1px solid #ef4444',
  color: '#ef4444', borderRadius: 4, cursor: 'pointer', fontSize: 12,
}
