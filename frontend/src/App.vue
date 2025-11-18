<template>
  <div id="app">
    <MusicForm @submit="handleGenerate" :preset="currentPreset" />
    <QueueView @use-preset="handleUsePreset" />
  </div>
</template>

<script>
import MusicForm from './components/MusicForm.vue'
import QueueView from './components/QueueView.vue'
import { musicAPI } from './services/api'

export default {
  name: 'App',
  components: {
    MusicForm,
    QueueView
  },
  data() {
    return {
      currentPreset: null
    }
  },
  methods: {
    generateRandomSeed() {
      // Generate a random 32-bit integer seed
      return Math.floor(Math.random() * 2147483647)
    },
    async handleGenerate(formData) {
      try {
        const numVersions = formData.num_versions || 1
        // Check if seed is provided (including 0 as a valid seed)
        // With v-model.number, seed will be a number if provided, or null/undefined if empty
        const baseSeed = (formData.seed !== null && formData.seed !== undefined && formData.seed !== '')
          ? (typeof formData.seed === 'number' ? formData.seed : parseInt(formData.seed))
          : this.generateRandomSeed()
        
        // Submit each version as a separate queue item
        for (let i = 0; i < numVersions; i++) {
          // First version uses the base seed (from UI or generated), subsequent versions use random seeds
          const seed = i === 0 ? baseSeed : this.generateRandomSeed()
          
          const requestData = {
            prompt: formData.prompt.trim(),
            duration: formData.duration,
            num_versions: 1, // Each queue item generates only 1 version
            lyrics: formData.lyrics && formData.lyrics.trim() !== '' ? formData.lyrics.trim() : null,
            seed: seed
          }
          
          await musicAPI.generateMusic(requestData)
        }
        
        // Clear preset after successful submission
        this.currentPreset = null
        
        // QueueView will auto-refresh to show the new items
      } catch (error) {
        alert(error.response?.data?.detail || 'Failed to submit generation request')
        console.error('Generation error:', error)
      }
    },
    handleUsePreset(preset) {
      // Set preset to load into form
      this.currentPreset = preset
      
      // Scroll to form
      this.$nextTick(() => {
        const formElement = document.querySelector('.container')
        if (formElement) {
          formElement.scrollIntoView({ behavior: 'smooth', block: 'start' })
        }
      })
    }
  }
}
</script>

