import axios from 'axios'

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export const api = axios.create({
  baseURL: BASE_URL,
  timeout: 30000,
})

export const uploadCsv = (file, onUploadProgress) => {
  const form = new FormData()
  form.append('file', file)
  return api.post('/upload', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress,
  })
}

export const fetchStats = (datasetId) => api.get(`/dataset/${datasetId}/stats`)
export const fetchSuspicious = (datasetId) => api.get(`/dataset/${datasetId}/suspicious`)
export const fetchAiSummary = (datasetId) => api.post(`/dataset/${datasetId}/ai/summary`)
export const fetchReport = (datasetId, format = 'markdown') =>
  api.get(`/dataset/${datasetId}/report`, {
    params: { format },
    responseType: format === 'markdown' ? 'text' : 'json',
  })
