import { useEffect, useState } from 'react'
import client from '../api/client'

export default function ReviewPage() {
  const [token] = useState(() => localStorage.getItem('admin_token'))
  const [videos, setVideos] = useState([])
  const [rejected, setRejected] = useState([])
  const [tab, setTab] = useState('queue')
  const [msg, setMsg] = useState({})

  const authHeaders = { Authorization: `Bearer ${token}` }

  const fetchAll = () => {
    if (!token) return
    client.get('/api/admin/review-queue', { headers: authHeaders })
      .then(r => setVideos(r.data)).catch(() => {})
    client.get('/api/admin/rejected', { headers: authHeaders })
      .then(r => setRejected(r.data)).catch(() => {})
  }

  useEffect(() => { fetchAll() }, [token])

  if (!token) {
    return (
      <div>
        <h1>Review Queue</h1>
        <p>You must be logged in as admin. Open settings (⚙ bottom-left) to login.</p>
      </div>
    )
  }

  const list = tab === 'queue' ? videos : rejected

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <h1 style={{ marginBottom: 0 }}>Review Queue</h1>
        <div style={{ display: 'flex', gap: 8 }}>
          <TabBtn active={tab === 'queue'} onClick={() => setTab('queue')}>
            Pending ({videos.length})
          </TabBtn>
          <TabBtn active={tab === 'rejected'} onClick={() => setTab('rejected')}>
            Rejected ({rejected.length})
          </TabBtn>
        </div>
      </div>

      {list.length === 0 ? (
        <p>{tab === 'queue' ? 'No videos pending review.' : 'No rejected videos.'}</p>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
          {list.map(v => (
            <VideoCard
              key={v.id}
              video={v}
              token={token}
              onAction={() => { fetchAll(); setMsg(m => ({ ...m, [v.id]: '' })) }}
              msg={msg[v.id]}
              setMsg={(text) => setMsg(m => ({ ...m, [v.id]: text }))}
              isRejected={tab === 'rejected'}
            />
          ))}
        </div>
      )}
    </div>
  )
}

function VideoCard({ video, token, onAction, msg, setMsg, isRejected }) {
  const [caption, setCaption] = useState(video.caption || '')
  const [hashtags, setHashtags] = useState(video.hashtags || '')
  const [loading, setLoading] = useState(false)

  const authHeaders = { Authorization: `Bearer ${token}` }

  const approve = async () => {
    setLoading(true)
    try {
      await client.post(`/api/admin/approve/${video.id}`, { caption, hashtags }, { headers: authHeaders })
      setMsg('Approved — scheduled for posting.')
      onAction()
    } catch { setMsg('Failed.') }
    setLoading(false)
  }

  const reject = async () => {
    setLoading(true)
    try {
      await client.post(`/api/admin/reject/${video.id}`, {}, { headers: authHeaders })
      setMsg('Rejected.')
      onAction()
    } catch { setMsg('Failed.') }
    setLoading(false)
  }

  const deleteVideo = async () => {
    if (!confirm('Permanently delete this video?')) return
    setLoading(true)
    try {
      await client.delete(`/api/admin/videos/${video.id}`, { headers: authHeaders })
      onAction()
    } catch { setMsg('Failed to delete.') }
    setLoading(false)
  }

  const videoUrl = video.video_path
    ? `http://localhost:8000/api/admin/media/video/${video.video_path.split('/').pop()}?token=${token}`
    : null

  const imageUrl = video.image_path
    ? `http://localhost:8000/api/admin/media/upload/${video.image_path.split('/').pop()}?token=${token}`
    : null

  return (
    <div style={cardStyle}>
      <div style={{ display: 'flex', gap: 20, flexWrap: 'wrap' }}>

        {/* Source image */}
        <div style={{ flex: '0 0 180px' }}>
          <p style={metaLabelStyle}>Source Image</p>
          {imageUrl ? (
            <img
              src={imageUrl}
              alt={video.image_filename}
              style={{ width: 180, height: 180, objectFit: 'cover', borderRadius: 8, background: '#111' }}
              onError={e => { e.target.style.display = 'none' }}
            />
          ) : (
            <div style={placeholderStyle}>No image</div>
          )}
          <p style={{ fontSize: 11, color: '#555', marginTop: 4, wordBreak: 'break-all' }}>
            {video.image_filename}
          </p>
        </div>

        {/* Video player */}
        <div style={{ flex: '0 0 320px' }}>
          <p style={metaLabelStyle}>Generated Video</p>
          {videoUrl ? (
            <video
              src={videoUrl}
              controls
              style={{ width: 320, borderRadius: 8, background: '#000', maxHeight: 200 }}
            />
          ) : (
            <div style={{ ...placeholderStyle, width: 320, height: 180 }}>
              Video not yet generated<br />
              <span style={{ fontSize: 11, color: '#555' }}>Grok API key needed</span>
            </div>
          )}
        </div>

        {/* Prompt + caption editing */}
        <div style={{ flex: 1, minWidth: 220 }}>
          <p style={metaLabelStyle}>Prompt Used</p>
          <p style={{ fontSize: 12, color: '#666', fontStyle: 'italic', marginBottom: 16, lineHeight: 1.5 }}>
            {video.prompt_used}
          </p>

          <p style={metaLabelStyle}>Caption</p>
          <textarea
            value={caption}
            onChange={e => setCaption(e.target.value)}
            placeholder="Auto-generated caption will appear here..."
            style={textareaStyle}
          />

          <p style={{ ...metaLabelStyle, marginTop: 12 }}>Hashtags</p>
          <input
            value={hashtags}
            onChange={e => setHashtags(e.target.value)}
            placeholder="#aesthetic, #cinematic, ..."
            style={inputStyle}
          />
          <p style={{ fontSize: 11, color: '#555', marginTop: 4 }}>Comma-separated</p>
        </div>
      </div>

      {/* Action bar */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 20, paddingTop: 16, borderTop: '1px solid #2a2a2a' }}>
        <div style={{ display: 'flex', gap: 8 }}>
          {!isRejected && (
            <button style={approveBtnStyle} onClick={approve} disabled={loading}>
              ✓ Approve & Schedule
            </button>
          )}
          {isRejected && (
            <button style={approveBtnStyle} onClick={approve} disabled={loading}>
              ↩ Re-approve
            </button>
          )}
          {!isRejected && (
            <button style={rejectBtnStyle} onClick={reject} disabled={loading}>
              ✕ Reject
            </button>
          )}
          <button style={deleteBtnStyle} onClick={deleteVideo} disabled={loading}>
            🗑 Delete
          </button>
        </div>
        {msg && (
          <span style={{ fontSize: 12, color: msg.includes('Failed') ? '#ef4444' : '#22c55e' }}>{msg}</span>
        )}
        <span style={{ fontSize: 11, color: '#444' }}>
          {new Date(video.created_at).toLocaleString()}
        </span>
      </div>
    </div>
  )
}

function TabBtn({ active, onClick, children }) {
  return (
    <button onClick={onClick} style={{
      padding: '6px 14px', fontSize: 13, borderRadius: 6, cursor: 'pointer',
      background: active ? '#6c63ff' : 'transparent',
      color: active ? '#fff' : '#888',
      border: `1px solid ${active ? '#6c63ff' : '#333'}`,
    }}>
      {children}
    </button>
  )
}

const cardStyle = {
  background: '#1a1a1a', border: '1px solid #2a2a2a', borderRadius: 12, padding: 20,
}
const metaLabelStyle = { fontSize: 11, color: '#555', fontWeight: 600, textTransform: 'uppercase', letterSpacing: 1, marginBottom: 8 }
const placeholderStyle = {
  width: 180, height: 180, background: '#111', borderRadius: 8,
  display: 'flex', alignItems: 'center', justifyContent: 'center',
  fontSize: 12, color: '#444', textAlign: 'center',
}
const textareaStyle = {
  width: '100%', minHeight: 72, padding: '8px 10px', background: '#111',
  border: '1px solid #2a2a2a', borderRadius: 6, color: '#ccc', fontSize: 13,
  resize: 'vertical', fontFamily: 'inherit',
}
const inputStyle = {
  width: '100%', padding: '8px 10px', background: '#111',
  border: '1px solid #2a2a2a', borderRadius: 6, color: '#ccc', fontSize: 13,
}
const approveBtnStyle = {
  padding: '8px 16px', background: '#16a34a', color: '#fff',
  border: 'none', borderRadius: 6, cursor: 'pointer', fontSize: 13, fontWeight: 600,
}
const rejectBtnStyle = {
  padding: '8px 16px', background: 'transparent', color: '#f87171',
  border: '1px solid #f87171', borderRadius: 6, cursor: 'pointer', fontSize: 13,
}
const deleteBtnStyle = {
  padding: '8px 14px', background: 'transparent', color: '#555',
  border: '1px solid #333', borderRadius: 6, cursor: 'pointer', fontSize: 13,
}
