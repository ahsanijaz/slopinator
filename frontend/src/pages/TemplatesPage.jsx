import { useEffect, useState } from 'react'
import client from '../api/client'

export default function TemplatesPage() {
  const [templates, setTemplates] = useState([])
  const [form, setForm] = useState({ name: '', template_str: '' })
  const [error, setError] = useState('')

  const fetchTemplates = () => client.get('/api/templates/').then(r => setTemplates(r.data)).catch(() => {})

  useEffect(() => { fetchTemplates() }, [])

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    try {
      await client.post('/api/templates/', form)
      setForm({ name: '', template_str: '' })
      fetchTemplates()
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create template.')
    }
  }

  const handleDelete = async (id) => {
    await client.delete(`/api/templates/${id}`)
    fetchTemplates()
  }

  return (
    <div>
      <h1>Prompt Templates</h1>

      <form onSubmit={handleSubmit} style={formStyle}>
        <div style={{ marginBottom: 10 }}>
          <label style={labelStyle}>Template Name</label>
          <input
            style={{ ...inputStyle, width: 280 }}
            placeholder="e.g. Cinematic landscape"
            value={form.name}
            onChange={e => setForm(f => ({ ...f, name: e.target.value }))}
            required
          />
        </div>
        <div style={{ marginBottom: 10 }}>
          <label style={labelStyle}>Template String</label>
          <textarea
            style={{ ...inputStyle, width: '100%', minHeight: 72, resize: 'vertical', fontFamily: 'monospace' }}
            placeholder='e.g. A {theme} style cinematic video of {subject} with dramatic lighting'
            value={form.template_str}
            onChange={e => setForm(f => ({ ...f, template_str: e.target.value }))}
            required
          />
          <p style={{ fontSize: 11, color: '#555', marginTop: 4 }}>
            Use <code style={{ color: '#6c63ff' }}>{'{subject}'}</code> and <code style={{ color: '#6c63ff' }}>{'{theme}'}</code> as placeholders — they'll be filled in automatically.
          </p>
        </div>
        <button type="submit" style={addBtnStyle}>Add Template</button>
        {error && <p style={{ color: '#ef4444', fontSize: 12, marginTop: 8 }}>{error}</p>}
      </form>

      {templates.length === 0 ? (
        <p>No templates yet. Add one above.</p>
      ) : (
        <table style={tableStyle}>
          <thead>
            <tr>
              {['Name', 'Template', ''].map(h => (
                <th key={h} style={thStyle}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {templates.map(t => (
              <tr key={t.id}>
                <td style={{ ...tdStyle, whiteSpace: 'nowrap' }}>{t.name}</td>
                <td style={{ ...tdStyle, color: '#888', fontFamily: 'monospace', fontSize: 12 }}>{t.template_str}</td>
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
