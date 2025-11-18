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

    <div v-else-if="queueItems.length === 0" style="text-align: center; padding: 40px; color: #666;">
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
            <p style="margin-bottom: 10px; color: #666;">
              <strong>{{ item.versions.length }}</strong> version(s) generated
            </p>
            <div class="version-links">
              <button
                v-for="(version, idx) in item.versions"
                :key="version.id"
                @click="playVersion(version.id)"
                class="btn-secondary"
                style="font-size: 12px; padding: 6px 12px; margin-right: 8px;"
              >
                Play Version {{ idx + 1 }}
              </button>
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
    playVersion(versionId) {
      const url = musicAPI.getAudioUrl(versionId)
      window.open(url, '_blank')
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
  background: #f8f9fa;
  border-radius: 8px;
  padding: 20px;
  border: 2px solid #e0e0e0;
  transition: all 0.3s;
}

.queue-item-processing {
  border-color: #667eea;
  background: #f0f4ff;
  box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
}

.queue-item-completed {
  border-color: #d1e7dd;
  background: #f0f9f4;
}

.queue-item-failed {
  border-color: #f8d7da;
  background: #fef0f0;
}

.queue-item-cancelled {
  border-color: #ffc107;
  background: #fffbf0;
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
  color: #667eea;
  min-width: 40px;
}

.queue-item-actions {
  display: flex;
  gap: 8px;
}

.btn-icon {
  background: #6c757d;
  color: white;
  border: none;
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
  background: #5a6268;
  transform: scale(1.1);
}

.btn-icon:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-danger {
  background: #dc3545;
}

.btn-danger:hover:not(:disabled) {
  background: #c82333;
}

.btn-cancel {
  background: #ffc107;
  color: #000;
}

.btn-cancel:hover:not(:disabled) {
  background: #e0a800;
}

.queue-item-content {
  margin-top: 10px;
}

.queue-item-info {
  margin-bottom: 10px;
}

.queue-item-prompt {
  margin-bottom: 8px;
  color: #333;
  line-height: 1.5;
}

.queue-item-details {
  display: flex;
  gap: 15px;
  font-size: 14px;
  color: #666;
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
  background: #e0e0e0;
  border-radius: 10px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  transition: width 0.3s ease;
  border-radius: 10px;
}

.progress-text {
  font-size: 14px;
  font-weight: 600;
  color: #667eea;
  min-width: 50px;
}

.queue-item-versions {
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #e0e0e0;
}

.version-links {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
</style>

