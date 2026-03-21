import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import UploadPage from './pages/UploadPage'
import QueuePage from './pages/QueuePage'
import TemplatesPage from './pages/TemplatesPage'
import ThemesPage from './pages/ThemesPage'
import HistoryPage from './pages/HistoryPage'
import ReviewPage from './pages/ReviewPage'

export default function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<UploadPage />} />
        <Route path="/queue" element={<QueuePage />} />
        <Route path="/templates" element={<TemplatesPage />} />
        <Route path="/themes" element={<ThemesPage />} />
        <Route path="/history" element={<HistoryPage />} />
        <Route path="/review" element={<ReviewPage />} />
      </Routes>
    </Layout>
  )
}
