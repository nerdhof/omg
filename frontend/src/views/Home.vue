<template>
  <div class="page-home">
    <div class="container">
      <WaveText text="OMG - 39C3 power circus - oPEN mUSIC gENERATOR" tag="h1" />
      <p style="color: var(--color-neutral); margin-bottom: 30px;">
        An open and free music generation app for the 39C3 power circus.
        Generates lyrics and music for your show - all with free and open source mdoels.
      </p>
      <Navigation />
    </div>
    <MusicForm @submit="handleGenerate" :preset="currentPreset" />
    <QueueView @use-preset="handleUsePreset" />
  </div>
</template>

<script>
import MusicForm from '../components/MusicForm.vue'
import QueueView from '../components/QueueView.vue'
import Navigation from '../components/Navigation.vue'
import WaveText from '../components/WaveText.vue'
import { musicAPI } from '../services/api'

export default {
  name: 'Home',
  components: {
    MusicForm,
    QueueView,
    Navigation,
    WaveText
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
            seed: seed,
            provider: formData.provider && formData.provider.trim() !== '' ? formData.provider.trim() : null
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

<style scoped>
/* Home page - Violet theme (keep as is, but ensure menu button is highlighted) */
.page-home :deep(.container) {
  border-color: #666;
}

.page-home :deep(.container:hover) {
  border-color: var(--color-secondary);
  box-shadow: 0 0 20px rgba(150, 115, 255, 0.2), 0 0 40px rgba(150, 115, 255, 0.1);
}

.page-home :deep(h1) {
  color: var(--color-secondary);
  text-shadow: 0 0 10px rgba(150, 115, 255, 0.5);
}

.page-home :deep(h1:hover) {
  text-shadow: 0 0 15px rgba(150, 115, 255, 0.8);
}
</style>

