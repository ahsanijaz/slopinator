import { useEffect, useRef, useState } from 'react'
import client from '../api/client'

export default function UploadPage() {
  const [themes, setThemes] = useState([])
  const [templates, setTemplates] = useState([])
  const [selectedTheme, setSelectedTheme] = useState('')
  const [selectedTemplate, setSelectedTemplate] = useState('')
  const [files, setFiles] = useState([])
  const [uploading, setUploading] = useState(false)
  const [results, setResults] = useState([])
  const [dragging, setDragging] = useState(false)
  const inputRef = useRef()

  useEffect(() => {
    client.get('/api/themes/').then(r => setThemes(r.data)).catch(() => {})
    client.get('/api/templates/').then(r => setTemplates(r.data)).catch(() => {})
  }, [])

  const handleDrop = (e) => {
    e.preventDefault()
    setDragging(false)
    const dropped = Array.from(e.dataTransfer.files).filter(f => f.type.startsWith('image/'))
    setFiles(prev => [...prev, ...dropped])
  }

  const handleFileSelect = (e) => {
    const selected = Array.from(e.target.files)
    setFiles(prev => [...prev, ...selected])
  }

  const removeFile = (idx) => setFiles(prev => prev.filter((_, i) => i !== idx))

  const handleUpload = async () => {
    if (!files.length) return
    setUploading(true)
    setResults([])
    const uploaded = []

    for (const file of files) {
      const form = new FormData()
      form.append('file', file)
      if (selectedTheme) form.append('theme_id', selectedTheme)
      if (selectedTemplate) form.append('template_id', selectedTemplate)
      try {
        const res = await client.post('/api/images/upload', form)
        uploaded.push({ name: file.name, status: 'queued', data: res.data })
      } catch (err) {
        uploaded.push({ name: file.name, status: 'error', error: err.response?.data?.detail })
      }
    }

    setResults(uploaded)
    setFiles([])
    setUploading(false)
  }

  return (
    <div>
      <h1>Upload Images</h1>

      <div style={{ display: 'flex', gap: 16, marginBottom: 20 }}>
        <div style={{ flex: 1 }}>
          <label style={labelStyle}>Theme (optional)</label>
          <select style={selectStyle} value={selectedTheme} onChange={e => setSelectedTheme(e.target.value)}>
            <option value="">— use default —</option>
            {themes.map(t => <option key={t.id} value={t.id}>{t.name}</option>)}
          </select>
        </div>
        <div style={{ flex: 1 }}>
          <label style={labelStyle}>Template (optional)</label>
          <select style={selectStyle} value={selectedTemplate} onChange={e => setSelectedTemplate(e.target.value)}>
            <option value="">— use default —</option>
            {templates.map(t => <option key={t.id} value={t.id}>{t.name}</option>)}
          </select>
        </div>
      </div>

      <div
        style={{
          ...dropzoneStyle,
          borderColor: dragging ? '#6c63ff' : '#333',
          background: dragging ? '#1e1a2e' : '#161616',
        }}
        onDragOver={e => { e.preventDefault(); setDragging(true) }}
        onDragLeave={() => setDragging(false)}
        onDrop={handleDrop}
        onClick={() => inputRef.current.click()}
      >
        <p style={{ color: '#888', marginBottom: 8 }}>Drag & drop images here, or click to select</p>
        <p style={{ color: '#555', fontSize: 12 }}>PNG, JPG, WEBP supported</p>
        <input ref={inputRef} type="file" accept="image/*" multiple hidden onChange={handleFileSelect} />
      </div>

      {files.length > 0 && (
        <div style={{ marginTop: 16 }}>
          <p style={{ color: '#aaa', marginBottom: 8, fontSize: 13 }}>{files.length} file(s) selected:</p>
          {files.map((f, i) => (
            <div key={i} style={fileRowStyle}>
              <span style={{ fontSize: 13 }}>{f.name}</span>
              <button style={removeBtnStyle} onClick={() => removeFile(i)}>✕</button>
            </div>
          ))}
          <button style={uploadBtnStyle} onClick={handleUpload} disabled={uploading}>
            {uploading ? 'Uploading...' : `Add ${files.length} image(s) to queue`}
          </button>
        </div>
      )}

      {results.length > 0 && (
        <div style={{ marginTop: 20 }}>
          <p style={{ color: '#aaa', fontSize: 13, marginBottom: 8 }}>Upload results:</p>
          {results.map((r, i) => (
            <div key={i} style={{ ...fileRowStyle, borderColor: r.status === 'error' ? '#ff4444' : '#2a4a2a' }}>
              <span style={{ fontSize: 13 }}>{r.name}</span>
              <span style={{ fontSize: 12, color: r.status === 'error' ? '#ff6666' : '#66bb6a' }}>
                {r.status === 'error' ? `Error: ${r.error}` : 'Queued'}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

const labelStyle = { display: 'block', fontSize: 12, color: '#888', marginBottom: 6 }
const selectStyle = {
  width: '100%', padding: '8px 10px', background: '#1a1a1a',
  border: '1px solid #333', borderRadius: 6, color: '#e0e0e0', fontSize: 13,
}
const dropzoneStyle = {
  border: '2px dashed #333', borderRadius: 10, padding: '40px 20px',
  textAlign: 'center', cursor: 'pointer', transition: 'all 0.2s',
}
const fileRowStyle = {
  display: 'flex', justifyContent: 'space-between', alignItems: 'center',
  padding: '8px 12px', background: '#1a1a1a', border: '1px solid #2a2a2a',
  borderRadius: 6, marginBottom: 6,
}
const removeBtnStyle = {
  background: 'none', border: 'none', color: '#666', cursor: 'pointer', fontSize: 14,
}
const uploadBtnStyle = {
  marginTop: 12, padding: '10px 20px', background: '#6c63ff', color: '#fff',
  border: 'none', borderRadius: 6, cursor: 'pointer', fontSize: 14, fontWeight: 600,
}
