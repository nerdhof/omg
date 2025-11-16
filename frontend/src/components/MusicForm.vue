<template>
  <div class="container">
    <h1>Generate Music</h1>
    <p style="color: #666; margin-bottom: 30px;">
      Create AI-generated music by specifying style, topic, and other parameters
    </p>

    <form @submit.prevent="handleSubmit">
      <div class="form-group">
        <label for="style">Music Style *</label>
        <select id="style" v-model="form.style" required>
          <option value="">Select a style</option>
          <option value="jazz">Jazz</option>
          <option value="rock">Rock</option>
          <option value="classical">Classical</option>
          <option value="electronic">Electronic</option>
          <option value="pop">Pop</option>
          <option value="blues">Blues</option>
          <option value="country">Country</option>
          <option value="hip-hop">Hip-Hop</option>
          <option value="ambient">Ambient</option>
          <option value="folk">Folk</option>
        </select>
      </div>

      <div class="form-group">
        <label for="topic">Topic (Optional)</label>
        <input
          id="topic"
          type="text"
          v-model="form.topic"
          placeholder="e.g., nature, love, adventure"
        />
      </div>

      <div class="form-group">
        <label for="refrain">Refrain Line (Optional)</label>
        <input
          id="refrain"
          type="text"
          v-model="form.refrain"
          placeholder="e.g., 'In the morning light'"
        />
      </div>

      <div class="form-group">
        <label for="text">Complete Text/Lyrics (Optional)</label>
        <textarea
          id="text"
          v-model="form.text"
          placeholder="Enter complete lyrics or text for the music..."
        />
        <small style="color: #666; display: block; margin-top: 5px;">
          If provided, this will be used as the primary prompt
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
        <div style="display: flex; justify-content: space-between; font-size: 12px; color: #666;">
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

      <button type="submit" :disabled="isSubmitting">
        {{ isSubmitting ? 'Generating...' : 'Generate Music' }}
      </button>
    </form>
  </div>
</template>

<script>
export default {
  name: 'MusicForm',
  emits: ['submit'],
  data() {
    return {
      form: {
        style: '',
        topic: '',
        refrain: '',
        text: '',
        duration: 30,
        num_versions: 3
      },
      isSubmitting: false
    }
  },
  methods: {
    async handleSubmit() {
      if (!this.form.style) {
        alert('Please select a music style')
        return
      }

      this.isSubmitting = true
      try {
        await this.$emit('submit', { ...this.form })
      } finally {
        this.isSubmitting = false
      }
    }
  }
}
</script>

