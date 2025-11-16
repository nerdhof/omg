import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
})

export const musicAPI = {
  /**
   * Submit a music generation request
   */
  async generateMusic(data) {
    const response = await api.post('/api/v1/generate', data)
    return response.data
  },

  /**
   * Get job status
   */
  async getJobStatus(jobId) {
    const response = await api.get(`/api/v1/jobs/${jobId}`)
    return response.data
  },

  /**
   * Get audio file URL for a version
   */
  getAudioUrl(versionId) {
    return `${API_BASE_URL}/api/v1/versions/${versionId}/audio`
  }
}

export default api

