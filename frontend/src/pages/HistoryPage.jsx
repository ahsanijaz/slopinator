import { useEffect, useState } from 'react'
import client from '../api/client'

const STATUS_COLORS = {
  pending: '#f59e0b',
  generating: '#6c63ff',
  ready: '#22c55e',
  pending_review: '#fb923c',
  approved: '#34d399',
  rejected: '#f87171',
  failed: '#ef4444',
}

export default function HistoryPage() {
  const [videos, setVideos] = useState([])

  useEffect(() => {
    client.get('/api/videos/').then(r => setVideos(r.data)).catch(() => {})
    const interval = setInterval(() => {
      client.get('/api/videos/').then(r => setVideos(r.data)).catch(() => {})
    }, 10000)
    return () => clearInterval(interval)
  }, [])

  return (
    <div>
      <h1>Generated Videos</h1>

      {videos.length === 0 ? (
        <p>No videos generated yet. Upload images and process the queue.</p>
      ) : (
        <table style={tableStyle}>
          <thead>
            <tr>
              {['ID', 'Image ID', 'Prompt', 'Status', 'Created'].map(h => (
                <th key={h} style={thStyle}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {videos.map(v => (
              <tr key={v.id}>
                <td style={tdStyle}>{v.id}</td>
                <td style={tdStyle}>{v.image_id}</td>
                <td style={{ ...tdStyle, maxWidth: 320, color: '#888', fontSize: 12, fontStyle: 'italic' }}>
                  {v.prompt_used}
                </td>
                <td style={tdStyle}>
                  <span style={{ color: STATUS_COLORS[v.status] || '#aaa', fontWeight: 600, fontSize: 12 }}>
                    {v.status}
                  </span>
                </td>
                <td style={{ ...tdStyle, whiteSpace: 'nowrap', color: '#666', fontSize: 12 }}>
                  {new Date(v.created_at).toLocaleString()}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  )
}

const tableStyle = { width: '100%', borderCollapse: 'collapse', fontSize: 13 }
const thStyle = {
  textAlign: 'left', padding: '8px 12px', color: '#888',
  borderBottom: '1px solid #2a2a2a', fontWeight: 500,
}
const tdStyle = { padding: '10px 12px', borderBottom: '1px solid #1e1e1e', color: '#ccc' }
