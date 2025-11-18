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
  },

  /**
   * Get all items in the queue
   */
  async getQueue() {
    const response = await api.get('/api/v1/queue')
    return response.data
  },

  /**
   * Get a specific queue item
   */
  async getQueueItem(jobId) {
    const response = await api.get(`/api/v1/queue/${jobId}`)
    return response.data
  },

  /**
   * Remove an item from the queue (also cancels if processing)
   */
  async removeFromQueue(jobId) {
    const response = await api.delete(`/api/v1/queue/${jobId}`)
    return response.data
  },

  /**
   * Cancel a generation job
   */
  async cancelGeneration(jobId) {
    const response = await api.delete(`/api/v1/queue/${jobId}`)
    return response.data
  },

  /**
   * Reorder items in the queue
   */
  async reorderQueue(jobId, newPosition) {
    const response = await api.patch('/api/v1/queue/reorder', {
      job_id: jobId,
      new_position: newPosition
    })
    return response.data
  },

  /**
   * Get preset information from a queue item
   */
  async getQueueItemPreset(jobId) {
    const response = await api.get(`/api/v1/queue/${jobId}/preset`)
    return response.data
  },

  /**
   * Generate or refine lyrics
   */
  async generateLyrics(data) {
    const response = await api.post('/api/v1/lyrics/generate', {
      current_lyrics: data.current_lyrics || null,
      prompt: data.prompt,
      duration: data.duration,
      topic: data.topic
    })
    return response.data
  }
}

export default api

