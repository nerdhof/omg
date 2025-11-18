<template>
  <div class="container">
    <h1>Open Music Generator</h1>
    <p style="color: var(--color-secondary-tint-05); margin-bottom: 30px;">
      Create AI-generated music by specifying a prompt and optional lyrics
    </p>

    <form @submit.prevent="handleSubmit">
      <div class="form-group">
        <label for="prompt">Prompt *</label>
        <textarea
          id="prompt"
          v-model="form.prompt"
          required
          placeholder="Describe the music you want to generate, e.g., 'A relaxing jazz piece with smooth saxophone melodies' or 'Upbeat electronic dance music with a driving beat'"
          rows="4"
        />
        <small style="color: var(--color-secondary-tint-05); display: block; margin-top: 5px;">
          Describe the style, mood, instruments, or any other characteristics of the music
        </small>
      </div>

      <div class="form-group">
        <label for="topic">Topic (Optional)</label>
        <div style="display: flex; gap: 10px; align-items: flex-start;">
          <input
            id="topic"
            type="text"
            v-model="topic"
            placeholder="Enter a topic for lyrics generation..."
            style="flex: 1;"
          />
          <button
            type="button"
            @click="generateOrRefineLyrics"
            :disabled="isGeneratingLyrics || !topic || !form.prompt"
            style="white-space: nowrap;"
          >
            {{ isGeneratingLyrics ? 'Generating...' : (form.lyrics ? 'Refine Lyrics' : 'Write Lyrics') }}
          </button>
        </div>
        <small style="color: var(--color-secondary-tint-05); display: block; margin-top: 5px;">
          Enter a topic and click the button to generate or refine lyrics
        </small>
      </div>

      <div class="form-group">
        <label for="lyrics">Lyrics (Optional)</label>
        <div style="display: flex; gap: 10px; align-items: flex-start;">
          <textarea
            id="lyrics"
            v-model="form.lyrics"
            placeholder="Enter lyrics for the music (optional)..."
            rows="6"
            style="flex: 1;"
          />
          <button
            type="button"
            @click="undoLyrics"
            :disabled="lyricsHistory.length === 0"
            style="white-space: nowrap;"
          >
            Undo
          </button>
        </div>
        <small style="color: var(--color-secondary-tint-05); display: block; margin-top: 5px;">
          If provided, the music will be generated to match these lyrics
        </small>
      </div>

      <div class="form-group">
        <label for="duration">
          Duration (seconds)
          <span class="range-value">{{ form.duration }}s</span>
        </label>
        <input
          id="duration"
          type="range"
          v-model.number="form.duration"
          min="10"
          max="300"
          step="5"
        />
        <div style="display: flex; justify-content: space-between; font-size: 12px; color: var(--color-secondary-tint-05);">
          <span>10s</span>
          <span>300s</span>
        </div>
      </div>

      <div class="form-group">
        <label for="numVersions">Number of Versions</label>
        <select id="numVersions" v-model.number="form.num_versions">
          <option :value="1">1 version</option>
          <option :value="2">2 versions</option>
          <option :value="3">3 versions</option>
          <option :value="4">4 versions</option>
          <option :value="5">5 versions</option>
        </select>
      </div>

      <div class="form-group">
        <label for="provider">Model Provider</label>
        <select id="provider" v-model="form.provider">
          <option value="">Default (from server)</option>
          <option value="ace-step">ACE-Step</option>
          <option value="song-generation">SongGeneration</option>
        </select>
        <small style="color: var(--color-secondary-tint-05); display: block; margin-top: 5px;">
          Choose which model to use for generation. Leave as "Default" to use the server's default provider.
        </small>
      </div>

      <div class="form-group">
        <label for="seed">Seed (Optional)</label>
        <input
          id="seed"
          type="number"
          v-model.number="form.seed"
          placeholder="Leave empty for random seed"
          min="0"
        />
        <small style="color: var(--color-secondary-tint-05); display: block; margin-top: 5px;">
          Specify a seed for reproducible generation. Leave empty to generate a random seed.
        </small>
      </div>

      <button type="submit" :disabled="isSubmitting">
        {{ isSubmitting ? 'Generating...' : 'Generate Music' }}
      </button>
    </form>
  </div>
</template>

<script>
import { musicAPI } from '../services/api.js'

export default {
  name: 'MusicForm',
  emits: ['submit'],
  props: {
    preset: {
      type: Object,
      default: null
    }
  },
  data() {
    return {
      form: {
        prompt: '',
        lyrics: '',
        duration: 30,
        num_versions: 1,
        seed: '',
        provider: ''
      },
      topic: '',
      lyricsHistory: [],
      isSubmitting: false,
      isGeneratingLyrics: false
    }
  },
  watch: {
    preset(newPreset) {
      if (newPreset) {
        this.loadPreset(newPreset)
      }
    }
  },
  methods: {
    loadPreset(preset) {
      // Load preset data into form
      // The preset has: prompt, duration, num_versions, lyrics (optional), seed (optional), provider (optional)
      this.form.prompt = preset.prompt || ''
      this.form.lyrics = preset.lyrics || ''
      this.form.duration = preset.duration || 30
      this.form.num_versions = preset.num_versions || 1
      this.form.seed = preset.seed || ''
      this.form.provider = preset.provider || ''
      // Reset topic and history when loading preset
      this.topic = ''
      this.lyricsHistory = []
    },
    async generateOrRefineLyrics() {
      if (!this.topic || !this.topic.trim()) {
        alert('Please enter a topic for the lyrics')
        return
      }

      if (!this.form.prompt || !this.form.prompt.trim()) {
        alert('Please provide a prompt describing the music')
        return
      }

      this.isGeneratingLyrics = true
      try {
        // Save current lyrics to history before generating new ones
        // History is a stack: oldest versions first, newest at the end
        if (this.form.lyrics && this.form.lyrics.trim()) {
          this.lyricsHistory.push(this.form.lyrics)
        }

        const response = await musicAPI.generateLyrics({
          current_lyrics: this.form.lyrics && this.form.lyrics.trim() ? this.form.lyrics : null,
          prompt: this.form.prompt,
          duration: this.form.duration,
          topic: this.topic
        })

        this.form.lyrics = response.lyrics
      } catch (error) {
        console.error('Failed to generate lyrics:', error)
        const errorMessage = error.response?.data?.detail || error.message || 'Failed to generate lyrics'
        alert(`Error: ${errorMessage}`)
        // If we added current lyrics to history, remove it since generation failed
        if (this.lyricsHistory.length > 0 && this.form.lyrics && this.form.lyrics.trim()) {
          // Remove the last item if it matches current lyrics
          const lastIndex = this.lyricsHistory.length - 1
          if (this.lyricsHistory[lastIndex] === this.form.lyrics) {
            this.lyricsHistory.pop()
          }
        }
      } finally {
        this.isGeneratingLyrics = false
      }
    },
    undoLyrics() {
      if (this.lyricsHistory.length === 0) {
        return
      }

      // Get the previous version from history (most recent entry)
      const previousLyrics = this.lyricsHistory.pop()
      
      // Save current lyrics to history (so we can undo multiple times and potentially redo)
      const currentLyrics = this.form.lyrics || ''
      if (currentLyrics.trim()) {
        this.lyricsHistory.push(currentLyrics)
      }

      // Restore the previous version
      this.form.lyrics = previousLyrics || ''
    },
    async handleSubmit() {
      if (!this.form.prompt || this.form.prompt.trim() === '') {
        alert('Please provide a prompt describing the music you want to generate')
        return
      }

      this.isSubmitting = true
      try {
        // Topic is not in form, so it's automatically excluded from submission
        await this.$emit('submit', { ...this.form })
      } finally {
        this.isSubmitting = false
      }
    }
  }
}
</script>

