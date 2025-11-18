<template>
  <div class="container">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
      <h2>Generation Queue</h2>
      <button @click="refreshQueue" :disabled="loading" class="btn-secondary" style="font-size: 14px;">
        {{ loading ? 'Refreshing...' : 'Refresh' }}
      </button>
    </div>

    <div v-if="error" class="error">
      {{ error }}
    </div>

    <div v-if="loading && queueItems.length === 0" class="loading">
      <p>Loading queue...</p>
    </div>

    <div v-else-if="queueItems.length === 0" style="text-align: center; padding: 40px; color: var(--color-neutral);">
      <p>Queue is empty. Submit a generation request to add items to the queue.</p>
    </div>

    <div v-else class="queue-list">
      <div
        v-for="item in queueItems"
        :key="item.job_id"
        class="queue-item"
        :class="{
          'queue-item-processing': item.status === 'processing',
          'queue-item-completed': item.status === 'completed',
          'queue-item-failed': item.status === 'failed',
          'queue-item-cancelled': item.status === 'cancelled'
        }"
      >
        <div class="queue-item-header">
          <div class="queue-item-position">
            <span class="position-number">#{{ item.queue_position }}</span>
            <span class="status-badge" :class="`status-${item.status}`">
              {{ item.status }}
            </span>
          </div>
          <div class="queue-item-actions">
            <button
              v-if="item.status === 'processing'"
              @click="cancelGeneration(item.job_id)"
              :disabled="removing"
              class="btn-icon btn-cancel"
              title="Cancel"
            >
              ⏹
            </button>
            <button
              v-if="item.status !== 'processing'"
              @click="moveUp(item.job_id, item.queue_position)"
              :disabled="item.queue_position === 1 || moving"
              class="btn-icon"
              title="Move up"
            >
              ↑
            </button>
            <button
              v-if="item.status !== 'processing'"
              @click="moveDown(item.job_id, item.queue_position)"
              :disabled="item.queue_position === queueItems.length || moving"
              class="btn-icon"
              title="Move down"
            >
              ↓
            </button>
            <button
              @click="useAsPreset(item.job_id)"
              class="btn-icon"
              title="Use as preset"
            >
              📋
            </button>
            <button
              @click="removeFromQueue(item.job_id)"
              :disabled="removing"
              class="btn-icon btn-danger"
              title="Remove"
            >
              ×
            </button>
          </div>
        </div>

        <div class="queue-item-content">
          <div class="queue-item-info">
            <div class="queue-item-prompt">
              <strong>Prompt:</strong> {{ item.prompt.length > 100 ? item.prompt.substring(0, 100) + '...' : item.prompt }}
            </div>
            <div class="queue-item-details">
              <span>Duration: {{ item.duration }}s</span>
              <span v-if="item.provider">Provider: {{ item.provider }}</span>
              <span v-if="item.seed !== null && item.seed !== undefined">Seed: {{ item.seed }}</span>
              <span v-if="item.lyrics">Has lyrics</span>
            </div>
          </div>

          <div v-if="item.status === 'processing' && item.progress !== null && item.progress !== undefined" class="progress-section">
            <div class="progress-bar">
              <div class="progress-fill" :style="{ width: `${item.progress}%` }"></div>
            </div>
            <span class="progress-text">{{ Math.round(item.progress) }}%</span>
          </div>

          <div v-if="item.status === 'completed' && item.versions && item.versions.length > 0" class="queue-item-versions">
            <div v-for="version in item.versions" :key="version.id" class="version-container">
              <div class="version-controls">
                <audio
                  :src="getAudioUrl(version.id)"
                  controls
                  class="audio-player"
                />
                <button
                  @click="downloadVersion(version.id)"
                  class="btn-secondary"
                  style="font-size: 12px; padding: 6px 12px; margin-left: 10px;"
                >
                  Download
                </button>
              </div>
            </div>
          </div>

          <div v-if="item.status === 'failed'" class="error" style="margin-top: 10px; font-size: 14px;">
            {{ item.error || 'Generation failed' }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { musicAPI } from '../services/api'

export default {
  name: 'QueueView',
  emits: ['use-preset'],
  data() {
    return {
      queueItems: [],
      loading: false,
      error: null,
      removing: false,
      moving: false,
      pollInterval: null
    }
  },
  mounted() {
    this.refreshQueue()
    // Auto-refresh every 5 seconds
    this.pollInterval = setInterval(() => {
      this.refreshQueue()
    }, 5000)
  },
  beforeUnmount() {
    if (this.pollInterval) {
      clearInterval(this.pollInterval)
    }
  },
  methods: {
    async refreshQueue() {
      this.loading = true
      this.error = null

      try {
        const data = await musicAPI.getQueue()
        this.queueItems = data.items || []
      } catch (err) {
        this.error = err.response?.data?.detail || 'Failed to fetch queue'
        console.error('Queue fetch error:', err)
      } finally {
        this.loading = false
      }
    },
    async cancelGeneration(jobId) {
      if (!confirm('Are you sure you want to cancel this generation?')) {
        return
      }

      this.removing = true
      try {
        await musicAPI.cancelGeneration(jobId)
        await this.refreshQueue()
      } catch (err) {
        alert(err.response?.data?.detail || 'Failed to cancel generation')
        console.error('Cancel error:', err)
      } finally {
        this.removing = false
      }
    },
    async removeFromQueue(jobId) {
      if (!confirm('Are you sure you want to remove this item from the queue?')) {
        return
      }

      this.removing = true
      try {
        await musicAPI.removeFromQueue(jobId)
        await this.refreshQueue()
      } catch (err) {
        alert(err.response?.data?.detail || 'Failed to remove item from queue')
        console.error('Remove error:', err)
      } finally {
        this.removing = false
      }
    },
    async moveUp(jobId, currentPosition) {
      if (currentPosition <= 1) return
      await this.reorderQueue(jobId, currentPosition - 1)
    },
    async moveDown(jobId, currentPosition) {
      if (currentPosition >= this.queueItems.length) return
      await this.reorderQueue(jobId, currentPosition + 1)
    },
    async reorderQueue(jobId, newPosition) {
      this.moving = true
      try {
        await musicAPI.reorderQueue(jobId, newPosition)
        await this.refreshQueue()
      } catch (err) {
        alert(err.response?.data?.detail || 'Failed to reorder queue')
        console.error('Reorder error:', err)
      } finally {
        this.moving = false
      }
    },
    async useAsPreset(jobId) {
      try {
        const preset = await musicAPI.getQueueItemPreset(jobId)
        this.$emit('use-preset', preset)
      } catch (err) {
        alert(err.response?.data?.detail || 'Failed to load preset')
        console.error('Preset error:', err)
      }
    },
    getAudioUrl(versionId) {
      return musicAPI.getAudioUrl(versionId)
    },
    downloadVersion(versionId) {
      const url = musicAPI.getAudioUrl(versionId)
      const link = document.createElement('a')
      link.href = url
      link.download = `music-version-${versionId}.wav`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
    }
  }
}
</script>

<style scoped>
.queue-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.queue-item {
  background: rgba(20, 20, 20, 0.8);
  border-radius: 8px;
  padding: 20px;
  border: 2px solid #666;
  transition: all 0.3s;
}

.queue-item:hover {
  border-color: var(--color-secondary);
  box-shadow: 0 0 20px rgba(150, 115, 255, 0.2), 0 0 40px rgba(150, 115, 255, 0.1);
  background: rgba(150, 115, 255, 0.03);
}

.queue-item-processing {
  border-color: var(--color-additional-02);
  background: rgba(102, 242, 255, 0.1);
  box-shadow: 0 0 20px rgba(102, 242, 255, 0.3);
}

.queue-item-processing:hover {
  border-color: var(--color-additional-02);
  background: rgba(102, 242, 255, 0.15);
  box-shadow: 0 0 25px rgba(102, 242, 255, 0.4);
}

.queue-item-completed {
  border-color: #666;
  background: rgba(20, 20, 20, 0.8);
}

.queue-item-completed:hover {
  border-color: var(--color-primary);
  background: rgba(0, 255, 0, 0.05);
  box-shadow: 0 0 20px rgba(0, 255, 0, 0.3);
}

.queue-item-failed {
  border-color: #666;
  background: rgba(20, 20, 20, 0.8);
}

.queue-item-failed:hover {
  border-color: var(--color-additional-01);
  background: rgba(255, 55, 25, 0.1);
  box-shadow: 0 0 15px rgba(255, 55, 25, 0.2);
}

.queue-item-cancelled {
  border-color: #666;
  background: rgba(20, 20, 20, 0.8);
}

.queue-item-cancelled:hover {
  border-color: var(--color-additional-02);
  background: rgba(102, 242, 255, 0.1);
  box-shadow: 0 0 15px rgba(102, 242, 255, 0.2);
}

.queue-item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.queue-item-position {
  display: flex;
  align-items: center;
  gap: 12px;
}

.position-number {
  font-size: 18px;
  font-weight: 700;
  color: var(--color-neutral);
  min-width: 40px;
  transition: color 0.3s, text-shadow 0.3s;
}

.queue-item:hover .position-number {
  color: var(--color-secondary);
  text-shadow: 0 0 5px rgba(150, 115, 255, 0.5);
}

.queue-item-processing .position-number {
  color: var(--color-additional-02);
  text-shadow: 0 0 5px rgba(102, 242, 255, 0.5);
}

.queue-item-completed:hover .position-number {
  color: var(--color-primary);
  text-shadow: 0 0 5px rgba(0, 255, 0, 0.5);
}

.queue-item-actions {
  display: flex;
  gap: 8px;
}

.btn-icon {
  background: #666;
  color: #ccc;
  border: 1px solid #666;
  width: 32px;
  height: 32px;
  border-radius: 6px;
  font-size: 18px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  padding: 0;
}

.btn-icon:hover:not(:disabled) {
  background: var(--color-secondary);
  color: var(--color-neutral);
  border-color: var(--color-secondary);
  transform: scale(1.1);
  box-shadow: 0 0 10px rgba(150, 115, 255, 0.5);
}

.btn-icon:disabled {
  opacity: 0.3;
  cursor: not-allowed;
  background: #444;
  border-color: #444;
  color: #666;
}

.btn-danger {
  background: #666;
  border-color: #666;
}

.btn-danger:hover:not(:disabled) {
  background: var(--color-additional-01);
  border-color: var(--color-additional-01);
  box-shadow: 0 0 10px rgba(255, 55, 25, 0.5);
}

.btn-cancel {
  background: #666;
  color: #ccc;
  border-color: #666;
}

.btn-cancel:hover:not(:disabled) {
  background: var(--color-additional-02);
  color: var(--color-dark);
  border-color: var(--color-additional-02);
  box-shadow: 0 0 10px rgba(102, 242, 255, 0.5);
}

.queue-item-content {
  margin-top: 10px;
}

.queue-item-info {
  margin-bottom: 10px;
}

.queue-item-prompt {
  margin-bottom: 8px;
  color: var(--color-neutral);
  line-height: 1.5;
  transition: color 0.3s;
}

.queue-item:hover .queue-item-prompt {
  color: var(--color-neutral);
}

.queue-item-details {
  display: flex;
  gap: 15px;
  font-size: 14px;
  color: var(--color-neutral);
  transition: color 0.3s;
}

.queue-item:hover .queue-item-details {
  color: var(--color-neutral);
}

.progress-section {
  margin-top: 10px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.progress-bar {
  flex: 1;
  height: 20px;
  background: var(--color-dark);
  border: 1px solid #666;
  border-radius: 10px;
  overflow: hidden;
  transition: border-color 0.3s;
}

.queue-item-processing .progress-bar {
  border-color: var(--color-additional-02);
}

.queue-item:hover .progress-bar {
  border-color: #888;
}

.queue-item-processing:hover .progress-bar {
  border-color: var(--color-additional-02);
}

.progress-fill {
  height: 100%;
  background: #666;
  transition: width 0.3s ease, background 0.3s, box-shadow 0.3s;
  border-radius: 10px;
}

.queue-item-processing .progress-fill {
  background: linear-gradient(90deg, var(--color-additional-02) 0%, var(--color-additional-02) 100%);
  box-shadow: 0 0 10px rgba(102, 242, 255, 0.5);
}

.queue-item:hover .progress-fill {
  background: linear-gradient(90deg, var(--color-secondary) 0%, var(--color-primary) 100%);
  box-shadow: 0 0 10px rgba(150, 115, 255, 0.5);
}

.queue-item-processing:hover .progress-fill {
  background: linear-gradient(90deg, var(--color-additional-02) 0%, var(--color-additional-02) 100%);
  box-shadow: 0 0 15px rgba(102, 242, 255, 0.7);
}

.progress-text {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-neutral);
  min-width: 50px;
  transition: color 0.3s, text-shadow 0.3s;
}

.queue-item-processing .progress-text {
  color: var(--color-additional-02);
  text-shadow: 0 0 5px rgba(102, 242, 255, 0.5);
}

.queue-item:hover .progress-text {
  color: var(--color-secondary);
  text-shadow: 0 0 5px rgba(150, 115, 255, 0.5);
}

.queue-item-processing:hover .progress-text {
  color: var(--color-additional-02);
  text-shadow: 0 0 8px rgba(102, 242, 255, 0.7);
}

.queue-item-versions {
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #666;
  transition: border-color 0.3s;
}

.queue-item:hover .queue-item-versions {
  border-top-color: #888;
}

.version-container {
  margin-bottom: 10px;
}

.version-container:last-child {
  margin-bottom: 0;
}

.version-controls {
  display: flex;
  align-items: center;
  gap: 8px;
}

.audio-player {
  flex: 1;
  max-width: 400px;
  height: 32px;
}
</style>

