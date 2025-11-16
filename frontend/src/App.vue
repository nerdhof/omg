<template>
  <div id="app">
    <MusicForm @submit="handleGenerate" />
    <MusicPlayer v-if="currentJobId" :job-id="currentJobId" />
  </div>
</template>

<script>
import MusicForm from './components/MusicForm.vue'
import MusicPlayer from './components/MusicPlayer.vue'
import { musicAPI } from './services/api'

export default {
  name: 'App',
  components: {
    MusicForm,
    MusicPlayer
  },
  data() {
    return {
      currentJobId: null
    }
  },
  methods: {
    async handleGenerate(formData) {
      try {
        const response = await musicAPI.generateMusic(formData)
        this.currentJobId = response.job_id
      } catch (error) {
        alert(error.response?.data?.detail || 'Failed to submit generation request')
        console.error('Generation error:', error)
      }
    }
  }
}
</script>

