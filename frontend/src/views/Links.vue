<template>
  <div class="page-links">
    <div class="container">
      <h1>OMG - 39C3 power circus - oPEN mUSIC gENERATOR</h1>
      <p style="color: var(--color-neutral); margin-bottom: 30px;">
        An open and free music generation app for the 39C3 power circus.
        Generates lyrics and music for your show - all with free and open source mdoels.
      </p>
      <Navigation />
    </div>
    <div class="container">
      <div class="links-grid">
        <div class="link-card">
          <h2>39C3</h2>
          <p>39th Chaos Communication Congress - The world's largest hacker convention</p>
          <a href="https://events.ccc.de/category/39c3/" target="_blank" rel="noopener noreferrer" class="link-button">
            Visit 39C3 →
          </a>
        </div>

        <div class="link-card">
          <h2>Chaos Computer Club</h2>
          <p>The Chaos Computer Club (CCC) is Europe's largest association of hackers</p>
          <a href="https://www.ccc.de/en/" target="_blank" rel="noopener noreferrer" class="link-button">
            Visit CCC →
          </a>
        </div>

        <div class="link-card">
          <h2>c-base</h2>
          <p>A hackerspace and community in Berlin, Germany</p>
          <a href="https://www.c-base.org/" target="_blank" rel="noopener noreferrer" class="link-button">
            Visit c-base →
          </a>
        </div>

        <div class="link-card">
          <h2>OC23 Youth Club</h2>
          <p>The Youth Club of where I learned juggling and meet many nice people.</p>
          <a href="https://www.instagram.com/jfeoc23" target="_blank" rel="noopener noreferrer" class="link-button">
            Visit OC23 →
          </a>
        </div>

        <div class="link-card">
          <h2>ACE-Step Project</h2>
          <p>An open-source AI music generation model developed by ACE Studio and StepFun</p>
          <a href="https://github.com/ace-step/ACE-Step" target="_blank" rel="noopener noreferrer" class="link-button">
            View on GitHub →
          </a>
        </div>

        <div class="link-card">
          <h2>LeVo Song Generation</h2>
          <p>A high-quality song generation model with multi-preference alignment by Tencent AI Lab</p>
          <a href="https://github.com/tencent-ailab/SongGeneration" target="_blank" rel="noopener noreferrer" class="link-button">
            View on GitHub →
          </a>
        </div>

        <div class="link-card">
          <h2>Mistral AI</h2>
          <p>Open-source AI models and technology for developers</p>
          <a href="https://www.mistral.ai/" target="_blank" rel="noopener noreferrer" class="link-button">
            Visit Mistral AI →
          </a>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Navigation from '../components/Navigation.vue'

export default {
  name: 'Links',
  components: {
    Navigation
  }
}
</script>

<style scoped>
/* Links page - Green theme */
.page-links :deep(.container) {
  border-color: #666;
}

.page-links :deep(.container:hover) {
  border-color: var(--color-primary);
  box-shadow: 0 0 20px rgba(0, 255, 0, 0.2), 0 0 40px rgba(0, 255, 0, 0.1);
}

.page-links :deep(h1) {
  color: var(--color-primary);
  text-shadow: 0 0 10px rgba(0, 255, 0, 0.5);
}

.page-links :deep(h1:hover) {
  text-shadow: 0 0 15px rgba(0, 255, 0, 0.8);
}

.page-links :deep(h2:hover) {
  color: var(--color-primary);
  text-shadow: 0 0 10px rgba(0, 255, 0, 0.5);
}

.page-links :deep(button:hover:not(:disabled)) {
  background: var(--color-primary);
  border-color: var(--color-primary);
  box-shadow: 0 0 20px rgba(0, 255, 0, 0.5);
}

.page-links :deep(input[type="text"]:hover),
.page-links :deep(input[type="number"]:hover),
.page-links :deep(select:hover),
.page-links :deep(textarea:hover) {
  border-color: var(--color-primary);
  box-shadow: 0 0 10px rgba(0, 255, 0, 0.2), 0 0 20px rgba(0, 255, 0, 0.1);
  background: rgba(0, 255, 0, 0.03);
}

.page-links :deep(input[type="text"]:focus),
.page-links :deep(input[type="number"]:focus),
.page-links :deep(select:focus),
.page-links :deep(textarea:focus) {
  border-color: var(--color-primary);
  box-shadow: 0 0 10px rgba(0, 255, 0, 0.3);
}

/* Links Grid */
.links-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 30px;
  margin-top: 30px;
}

.link-card {
  background: rgba(20, 20, 20, 0.95);
  border: 2px solid #666;
  border-radius: 8px;
  padding: 30px;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  min-height: 200px;
}

.link-card:hover {
  border-color: var(--color-primary);
  box-shadow: 0 0 20px rgba(0, 255, 0, 0.2), 0 0 40px rgba(0, 255, 0, 0.1);
  transform: translateY(-5px);
}

.link-card h2 {
  color: var(--color-primary);
  text-shadow: 0 0 10px rgba(0, 255, 0, 0.5);
  margin-bottom: 15px;
  font-size: 1.5em;
}

.link-card p {
  color: var(--color-neutral);
  line-height: 1.6;
  margin-bottom: 20px;
  flex-grow: 1;
}

.link-button {
  display: inline-block;
  background: #666;
  color: #ccc;
  border: 2px solid #666;
  padding: 12px 24px;
  border-radius: 6px;
  text-decoration: none;
  font-weight: 600;
  transition: all 0.2s;
  text-align: center;
  margin-top: auto;
}

.link-button:hover {
  background: var(--color-primary);
  color: var(--color-dark);
  border-color: var(--color-primary);
  box-shadow: 0 0 20px rgba(0, 255, 0, 0.5);
  transform: translateY(-2px);
}

/* Responsive Design */
@media (max-width: 768px) {
  .links-grid {
    grid-template-columns: 1fr;
    gap: 20px;
  }

  .link-card {
    min-height: auto;
  }
}
</style>

