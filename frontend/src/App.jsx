import { useState } from 'react'

import { fetchAiSummary, fetchReport, fetchStats, fetchSuspicious, uploadCsv } from './api/client'
import AISummaryPanel from './components/AISummaryPanel'
import AnalysisPanel from './components/AnalysisPanel'
import ChartsPanel from './components/ChartsPanel'
import UploadCard from './components/UploadCard'

export default function App() {
  const [datasetId, setDatasetId] = useState('')
  const [stats, setStats] = useState(null)
  const [suspicious, setSuspicious] = useState(null)
  const [aiSummary, setAiSummary] = useState(null)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [isUploading, setIsUploading] = useState(false)
  const [aiLoading, setAiLoading] = useState(false)
  const [error, setError] = useState('')

  const handleUpload = async (file) => {
    setError('')
    setIsUploading(true)
    setUploadProgress(0)
    setAiSummary(null)

    try {
      const uploadRes = await uploadCsv(file, (e) => {
        if (e.total) setUploadProgress(Math.round((e.loaded / e.total) * 100))
      })
      const id = uploadRes.data.dataset_id
      setDatasetId(id)

      const [statsRes, suspiciousRes] = await Promise.all([fetchStats(id), fetchSuspicious(id)])
      setStats(statsRes.data)
      setSuspicious(suspiciousRes.data)
    } catch (err) {
      setError(err?.response?.data?.detail || 'Upload/analysis failed')
    } finally {
      setIsUploading(false)
    }
  }

  const handleGenerateAi = async () => {
    if (!datasetId) return
    setAiLoading(true)
    setError('')
    try {
      const res = await fetchAiSummary(datasetId)
      setAiSummary(res.data)
    } catch (err) {
      setError(err?.response?.data?.detail || 'AI summary failed')
    } finally {
      setAiLoading(false)
    }
  }

  const handleDownloadReport = async (format = 'markdown') => {
    if (!datasetId) return
    try {
      const res = await fetchReport(datasetId, format)
      const blob =
        format === 'markdown'
          ? new Blob([res.data], { type: 'text/markdown' })
          : new Blob([JSON.stringify(res.data, null, 2)], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `ad-security-report-${datasetId}.${format === 'markdown' ? 'md' : 'json'}`
      a.click()
      URL.revokeObjectURL(url)
    } catch (err) {
      setError(err?.response?.data?.detail || 'Report download failed')
    }
  }

  return (
    <main className="mx-auto max-w-6xl space-y-6 px-4 py-8">
      <header>
        <h1 className="text-3xl font-bold">AI-assisted AD Log Analysis</h1>
        <p className="text-sm text-slate-400">
          Upload Windows Active Directory security logs and analyze suspicious activity locally with AI assistance.
        </p>
      </header>

      <UploadCard onFileSelected={handleUpload} progress={uploadProgress} isUploading={isUploading} />

      {error && <div className="rounded-lg border border-rose-500 bg-rose-950 p-3 text-sm text-rose-200">{error}</div>}

      {datasetId && (
        <div className="rounded-lg border border-slate-700 bg-slate-900 p-3 text-xs text-slate-300">
          Dataset ID: <span className="font-mono">{datasetId}</span>
        </div>
      )}

      <AnalysisPanel stats={stats} suspicious={suspicious} />
      {stats && <ChartsPanel stats={stats} />}
      {stats && <AISummaryPanel aiSummary={aiSummary} loading={aiLoading} onGenerate={handleGenerateAi} />}

      {stats && (
        <div className="flex gap-2">
          <button
            onClick={() => handleDownloadReport('markdown')}
            className="rounded-lg bg-indigo-500 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-400"
          >
            Download report (Markdown)
          </button>
          <button
            onClick={() => handleDownloadReport('json')}
            className="rounded-lg bg-slate-700 px-4 py-2 text-sm font-medium text-white hover:bg-slate-600"
          >
            Download report (JSON)
          </button>
        </div>
      )}
    </main>
  )
}
