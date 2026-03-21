import { useEffect, useState } from 'react'
import client from '../api/client'

const STATUS_COLORS = {
  pending: '#f59e0b',
  processing: '#6c63ff',
  done: '#22c55e',
  failed: '#ef4444',
}

export default function QueuePage() {
  const [queueData, setQueueData] = useState(null)
  const [images, setImages] = useState([])
  const [triggering, setTriggering] = useState(false)
  const [message, setMessage] = useState('')

  const fetchData = () => {
    client.get('/api/queue/').then(r => setQueueData(r.data)).catch(() => {})
    client.get('/api/images/').then(r => setImages(r.data)).catch(() => {})
  }

  useEffect(() => {
    fetchData()
    const interval = setInterval(fetchData, 5000)
    return () => clearInterval(interval)
  }, [])

  const triggerProcessing = async () => {
    setTriggering(true)
    setMessage('')
    try {
      await client.post('/api/queue/process')
      setMessage('Queue processing started.')
      setTimeout(fetchData, 1000)
    } catch {
      setMessage('Failed to trigger queue.')
    }
    setTriggering(false)
  }

  const deleteImage = async (id) => {
    await client.delete(`/api/images/${id}`)
    fetchData()
  }

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <h1 style={{ marginBottom: 0 }}>Queue</h1>
        <button style={triggerBtnStyle} onClick={triggerProcessing} disabled={triggering}>
          {triggering ? 'Starting...' : 'Process Queue'}
        </button>
      </div>

      {message && <p style={{ color: '#6c63ff', marginBottom: 16, fontSize: 13 }}>{message}</p>}

      {queueData && (
        <div style={{ display: 'flex', gap: 12, marginBottom: 28 }}>
          {Object.entries(queueData.counts).map(([status, count]) => (
            <div key={status} style={statCardStyle}>
              <div style={{ fontSize: 28, fontWeight: 700, color: STATUS_COLORS[status] }}>{count}</div>
              <div style={{ fontSize: 12, color: '#888', textTransform: 'capitalize' }}>{status}</div>
            </div>
          ))}
        </div>
      )}

      <h2 style={{ fontSize: 16, color: '#ccc', marginBottom: 12 }}>Images</h2>
      {images.length === 0 ? (
        <p>No images yet. Upload some from the Upload page.</p>
      ) : (
        <table style={tableStyle}>
          <thead>
            <tr>
              {['ID', 'Filename', 'Status', 'Uploaded', ''].map(h => (
                <th key={h} style={thStyle}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {images.map(img => (
              <tr key={img.id}>
                <td style={tdStyle}>{img.id}</td>
                <td style={tdStyle}>{img.filename}</td>
                <td style={tdStyle}>
                  <span style={{ color: STATUS_COLORS[img.status] || '#aaa', fontSize: 12, fontWeight: 600 }}>
                    {img.status}
                  </span>
                </td>
                <td style={tdStyle}>{new Date(img.uploaded_at).toLocaleString()}</td>
                <td style={tdStyle}>
                  {img.status === 'pending' && (
                    <button style={deleteBtnStyle} onClick={() => deleteImage(img.id)}>Remove</button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  )
}

const triggerBtnStyle = {
  padding: '8px 18px', background: '#6c63ff', color: '#fff',
  border: 'none', borderRadius: 6, cursor: 'pointer', fontSize: 13, fontWeight: 600,
}
const statCardStyle = {
  background: '#1a1a1a', border: '1px solid #2a2a2a', borderRadius: 8,
  padding: '16px 24px', textAlign: 'center', minWidth: 90,
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
