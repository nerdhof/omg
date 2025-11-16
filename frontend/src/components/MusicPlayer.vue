<template>
  <div class="container">
    <h2>Generated Versions</h2>

    <div v-if="loading" class="loading">
      <p>Loading versions...</p>
    </div>

    <div v-else-if="error" class="error">
      {{ error }}
    </div>

    <div v-else-if="jobStatus === 'pending' || jobStatus === 'processing'">
      <div class="status-badge" :class="`status-${jobStatus}`">
        {{ jobStatus }}
      </div>
      <div v-if="progress !== null" class="progress-bar">
        <div class="progress-fill" :style="{ width: `${progress}%` }"></div>
      </div>
      <p style="margin-top: 10px; color: #666;">
        {{ jobStatus === 'pending' ? 'Job queued...' : 'Generating music...' }}
      </p>
    </div>

    <div v-else-if="jobStatus === 'completed' && versions.length > 0">
      <p style="margin-bottom: 20px; color: #666;">
        Select a version to play and download
      </p>
      <div class="versions-grid">
        <div
          v-for="(version, index) in versions"
          :key="version.id"
          class="version-card"
          :class="{ selected: selectedVersion === version.id }"
          @click="selectVersion(version.id)"
        >
          <div class="version-header">
            <span class="version-title">Version {{ index + 1 }}</span>
            <span class="status-badge status-completed">Ready</span>
          </div>
          
          <audio
            v-if="selectedVersion === version.id"
            :ref="`audio-${version.id}`"
            :src="getAudioUrl(version.id)"
            controls
            class="audio-player"
            @loadedmetadata="onAudioLoaded"
          />

          <div class="audio-controls">
            <button
              v-if="selectedVersion !== version.id"
              @click.stop="selectVersion(version.id)"
              class="btn-secondary"
            >
              Select & Play
            </button>
            <button
              @click.stop="downloadAudio(version.id)"
              class="btn-secondary"
            >
              Download
            </button>
          </div>
        </div>
      </div>
    </div>

    <div v-else-if="jobStatus === 'failed'">
      <div class="error">
        Generation failed. Please try again.
      </div>
    </div>

    <div v-else-if="versions.length === 0 && jobStatus === 'completed'">
      <p style="color: #666;">No versions generated.</p>
    </div>
  </div>
</template>

<script>
import { musicAPI } from '../services/api'

export default {
  name: 'MusicPlayer',
  props: {
    jobId: {
      type: String,
      default: null
    }
  },
  data() {
    return {
      jobStatus: null,
      progress: null,
      versions: [],
      selectedVersion: null,
      loading: false,
      error: null,
      pollInterval: null
    }
  },
  watch: {
    jobId(newJobId) {
      if (newJobId) {
        this.startPolling(newJobId)
      } else {
        this.stopPolling()
      }
    }
  },
  beforeUnmount() {
    this.stopPolling()
  },
  methods: {
    async fetchJobStatus() {
      if (!this.jobId) return

      this.loading = true
      this.error = null

      try {
        const data = await musicAPI.getJobStatus(this.jobId)
        this.jobStatus = data.status
        this.progress = data.progress
        this.versions = data.versions || []

        if (data.error) {
          this.error = data.error
        }

        // Stop polling if job is completed or failed
        if (data.status === 'completed' || data.status === 'failed') {
          this.stopPolling()
        }
      } catch (err) {
        this.error = err.response?.data?.detail || 'Failed to fetch job status'
        this.stopPolling()
      } finally {
        this.loading = false
      }
    },
    startPolling(jobId) {
      // Initial fetch
      this.fetchJobStatus()

      // Poll every 2 seconds
      this.pollInterval = setInterval(() => {
        this.fetchJobStatus()
      }, 2000)
    },
    stopPolling() {
      if (this.pollInterval) {
        clearInterval(this.pollInterval)
        this.pollInterval = null
      }
    },
    selectVersion(versionId) {
      this.selectedVersion = versionId
    },
    getAudioUrl(versionId) {
      return musicAPI.getAudioUrl(versionId)
    },
    downloadAudio(versionId) {
      const url = this.getAudioUrl(versionId)
      const link = document.createElement('a')
      link.href = url
      link.download = `music-version-${versionId}.wav`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
    },
    onAudioLoaded() {
      // Audio metadata loaded
    }
  }
}
</script>

