<template>
  <div class="page-architecture">
    <div class="container">
      <h1>OMG - 39C3 power circus - oPEN mUSIC gENERATOR</h1>
      <p style="color: var(--color-neutral); margin-bottom: 30px;">
        An open and free music generation app for the 39C3 power circus.
        Generates lyrics and music for your show - all with free and open source mdoels.
      </p>
      <Navigation />
    </div>
    <div class="container">
      <h2>System Architecture</h2>
      <p style="color: var(--color-neutral); margin-bottom: 30px; text-align: center;">
        Three-tier microservices architecture with detailed backend and AI model service components.
        The diagram shows the data flow from user interface through orchestration to AI model processing.
      </p>
      <ArchitectureDiagram :auto-play="true" :show-controls="false" />
    </div>
  </div>
</template>

<script>
import Navigation from '../components/Navigation.vue'
import ArchitectureDiagram from '../components/ArchitectureDiagram.vue'

export default {
  name: 'Architecture',
  components: {
    Navigation,
    ArchitectureDiagram
  }
}
</script>

<style scoped>
/* Architecture page - Neon Orange theme (39C3 style guide) */
.page-architecture :deep(.container) {
  border-color: #666;
}

.page-architecture :deep(.container:hover) {
  border-color: var(--color-additional-01);
  box-shadow: 0 0 20px rgba(255, 55, 25, 0.2), 0 0 40px rgba(255, 55, 25, 0.1);
}

.page-architecture :deep(h1) {
  color: var(--color-additional-01);
  text-shadow: 0 0 10px rgba(255, 55, 25, 0.5);
}

.page-architecture :deep(h1:hover) {
  text-shadow: 0 0 15px rgba(255, 55, 25, 0.8);
}

.page-architecture :deep(h2:hover) {
  color: var(--color-additional-01);
  text-shadow: 0 0 10px rgba(255, 55, 25, 0.5);
}

.page-architecture :deep(button:hover:not(:disabled)) {
  background: var(--color-additional-01);
  border-color: var(--color-additional-01);
  box-shadow: 0 0 20px rgba(255, 55, 25, 0.5);
}

.page-architecture :deep(input[type="text"]:hover),
.page-architecture :deep(input[type="number"]:hover),
.page-architecture :deep(select:hover),
.page-architecture :deep(textarea:hover) {
  border-color: var(--color-additional-01);
  box-shadow: 0 0 10px rgba(255, 55, 25, 0.2), 0 0 20px rgba(255, 55, 25, 0.1);
  background: rgba(255, 55, 25, 0.03);
}

.page-architecture :deep(input[type="text"]:focus),
.page-architecture :deep(input[type="number"]:focus),
.page-architecture :deep(select:focus),
.page-architecture :deep(textarea:focus) {
  border-color: var(--color-additional-01);
  box-shadow: 0 0 10px rgba(255, 55, 25, 0.3);
}
</style>

