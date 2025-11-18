<template>
  <div class="architecture-diagram">
    <div class="diagram-controls" v-if="showControls">
      <button @click="resetAnimation" :disabled="isAnimating">Reset</button>
      <button @click="toggleAnimation" v-if="!isAnimating">Start</button>
      <button @click="toggleAnimation" v-else>Pause</button>
    </div>
    
    <svg 
      :width="svgWidth" 
      :height="svgHeight" 
      viewBox="0 0 1200 800"
      class="diagram-svg"
    >
      <!-- Background -->
      <rect width="1200" height="800" fill="#141414" />
      
      <!-- Frontend (Simple) -->
      <g class="frontend-layer" :class="{ 'active': currentPhase >= 1 }">
        <rect x="50" y="350" width="150" height="100" rx="8" 
          fill="#9673ff" fill-opacity="0.2" stroke="#9673ff" stroke-width="2" />
        <text x="125" y="385" text-anchor="middle" fill="#faf5f5" font-size="16" font-weight="bold">
          Frontend
        </text>
        <text x="125" y="405" text-anchor="middle" fill="#faf5f5" font-size="12">
          Vue.js
        </text>
        <text x="125" y="425" text-anchor="middle" fill="#9673ff" font-size="11">
          Port 5173
        </text>
      </g>
      
      <!-- Backend API (Detailed) -->
      <g class="backend-layer">
        <!-- Backend Container -->
        <rect x="250" y="50" width="400" height="700" rx="8" 
          fill="#141414" fill-opacity="0.8" stroke="#9673ff" stroke-width="3" />
        <text x="450" y="80" text-anchor="middle" fill="#9673ff" font-size="20" font-weight="bold">
          Backend API (FastAPI)
        </text>
        <text x="450" y="100" text-anchor="middle" fill="#9673ff" font-size="14">
          Port 8000
        </text>
        
        <!-- JobManager -->
        <g class="service-box" :class="{ 'active': currentPhase >= 2 }">
          <rect x="280" y="130" width="160" height="100" rx="6" 
            fill="#9673ff" fill-opacity="0.15" stroke="#9673ff" stroke-width="2" />
          <text x="360" y="155" text-anchor="middle" fill="#faf5f5" font-size="14" font-weight="bold">
            JobManager
          </text>
          <text x="360" y="175" text-anchor="middle" fill="#66f2ff" font-size="11">
            Manages jobs
          </text>
          <text x="360" y="190" text-anchor="middle" fill="#66f2ff" font-size="11">
            &amp; queue
          </text>
          <text x="360" y="210" text-anchor="middle" fill="#999" font-size="10">
            /api/v1/jobs
          </text>
        </g>
        
        <!-- LyricsService -->
        <g class="service-box" :class="{ 'active': currentPhase >= 2 }">
          <rect x="460" y="130" width="160" height="100" rx="6" 
            fill="#9673ff" fill-opacity="0.15" stroke="#9673ff" stroke-width="2" />
          <text x="540" y="155" text-anchor="middle" fill="#faf5f5" font-size="14" font-weight="bold">
            LyricsService
          </text>
          <text x="540" y="175" text-anchor="middle" fill="#66f2ff" font-size="11">
            Handles lyrics
          </text>
          <text x="540" y="190" text-anchor="middle" fill="#66f2ff" font-size="11">
            generation
          </text>
          <text x="540" y="210" text-anchor="middle" fill="#999" font-size="10">
            Lyrics API
          </text>
        </g>
        
        <!-- ModelClient -->
        <g class="service-box" :class="{ 'active': currentPhase >= 2 }">
          <rect x="280" y="250" width="160" height="100" rx="6" 
            fill="#9673ff" fill-opacity="0.15" stroke="#9673ff" stroke-width="2" />
          <text x="360" y="275" text-anchor="middle" fill="#faf5f5" font-size="14" font-weight="bold">
            ModelClient
          </text>
          <text x="360" y="295" text-anchor="middle" fill="#66f2ff" font-size="11">
            Communicates
          </text>
          <text x="360" y="310" text-anchor="middle" fill="#66f2ff" font-size="11">
            with Model Service
          </text>
          <text x="360" y="330" text-anchor="middle" fill="#999" font-size="10">
            HTTP Client
          </text>
        </g>
        
        <!-- PromptBuilder -->
        <g class="service-box" :class="{ 'active': currentPhase >= 2 }">
          <rect x="460" y="250" width="160" height="100" rx="6" 
            fill="#9673ff" fill-opacity="0.15" stroke="#9673ff" stroke-width="2" />
          <text x="540" y="275" text-anchor="middle" fill="#faf5f5" font-size="14" font-weight="bold">
            PromptBuilder
          </text>
          <text x="540" y="295" text-anchor="middle" fill="#66f2ff" font-size="11">
            Constructs
          </text>
          <text x="540" y="310" text-anchor="middle" fill="#66f2ff" font-size="11">
            model prompts
          </text>
          <text x="540" y="330" text-anchor="middle" fill="#999" font-size="10">
            Text Processing
          </text>
        </g>
        
        <!-- API Endpoints -->
        <g class="endpoints-box">
          <rect x="280" y="370" width="340" height="80" rx="6" 
            fill="#9673ff" fill-opacity="0.1" stroke="#9673ff" stroke-width="1" stroke-dasharray="4,4" />
          <text x="450" y="395" text-anchor="middle" fill="#faf5f5" font-size="12" font-weight="bold">
            API Endpoints
          </text>
          <text x="450" y="415" text-anchor="middle" fill="#999" font-size="10">
            /api/v1/generate
          </text>
          <text x="450" y="430" text-anchor="middle" fill="#999" font-size="10">
            /api/v1/jobs | /api/v1/audio
          </text>
        </g>
        
        <!-- Technology Badge -->
        <g class="tech-badge">
          <rect x="280" y="470" width="340" height="40" rx="6" 
            fill="#9673ff" fill-opacity="0.1" stroke="#9673ff" stroke-width="1" />
          <text x="450" y="495" text-anchor="middle" fill="#faf5f5" font-size="12">
            FastAPI • Python • Async Operations
          </text>
        </g>
        
        <!-- Internal Flow Arrows -->
        <g class="internal-flow" v-if="currentPhase >= 2">
          <!-- JobManager to LyricsService -->
          <path d="M 440 180 L 460 180" stroke="#00ff00" stroke-width="2" fill="none" 
            marker-end="url(#arrowhead-green)" class="flow-arrow" />
          <!-- JobManager to ModelClient -->
          <path d="M 360 230 L 360 250" stroke="#00ff00" stroke-width="2" fill="none" 
            marker-end="url(#arrowhead-green)" class="flow-arrow" />
          <!-- ModelClient to PromptBuilder -->
          <path d="M 440 300 L 460 300" stroke="#00ff00" stroke-width="2" fill="none" 
            marker-end="url(#arrowhead-green)" class="flow-arrow" />
        </g>
      </g>
      
      <!-- Model Service (Detailed) -->
      <g class="model-service-layer">
        <!-- Model Service Container -->
        <rect x="700" y="50" width="450" height="700" rx="8" 
          fill="#141414" fill-opacity="0.8" stroke="#00ff00" stroke-width="3" />
        <text x="925" y="80" text-anchor="middle" fill="#00ff00" font-size="20" font-weight="bold">
          Model Service (FastAPI)
        </text>
        <text x="925" y="100" text-anchor="middle" fill="#00ff00" font-size="14">
          Port 8001
        </text>
        
        <!-- Music Generation Models Section -->
        <text x="925" y="130" text-anchor="middle" fill="#66f2ff" font-size="16" font-weight="bold">
          Music Generation Models
        </text>
        
        <!-- ACE-Step -->
        <g class="model-box" :class="{ 'active': currentPhase >= 3 && currentPhase < 5 }">
          <rect x="730" y="150" width="190" height="120" rx="6" 
            fill="#00ff00" fill-opacity="0.15" stroke="#00ff00" stroke-width="2" />
          <text x="825" y="175" text-anchor="middle" fill="#faf5f5" font-size="14" font-weight="bold">
            ACE-Step
          </text>
          <text x="825" y="195" text-anchor="middle" fill="#66f2ff" font-size="11">
            Text-to-Music
          </text>
          <text x="825" y="210" text-anchor="middle" fill="#66f2ff" font-size="11">
            Generation
          </text>
          <text x="825" y="235" text-anchor="middle" fill="#999" font-size="10">
            PyTorch Model
          </text>
          <text x="825" y="250" text-anchor="middle" fill="#999" font-size="10">
            /model/v1/generate
          </text>
        </g>
        
        <!-- SongGeneration -->
        <g class="model-box" :class="{ 'active': currentPhase >= 3 && currentPhase < 5 }">
          <rect x="940" y="150" width="190" height="120" rx="6" 
            fill="#00ff00" fill-opacity="0.15" stroke="#00ff00" stroke-width="2" />
          <text x="1035" y="175" text-anchor="middle" fill="#faf5f5" font-size="14" font-weight="bold">
            SongGeneration
          </text>
          <text x="1035" y="195" text-anchor="middle" fill="#66f2ff" font-size="11">
            Alternative
          </text>
          <text x="1035" y="210" text-anchor="middle" fill="#66f2ff" font-size="11">
            Music Model
          </text>
          <text x="1035" y="235" text-anchor="middle" fill="#999" font-size="10">
            HuggingFace
          </text>
          <text x="1035" y="250" text-anchor="middle" fill="#999" font-size="10">
            Provider Switch
          </text>
        </g>
        
        <!-- Provider Switching -->
        <g class="provider-box">
          <rect x="730" y="290" width="400" height="50" rx="6" 
            fill="#00ff00" fill-opacity="0.1" stroke="#00ff00" stroke-width="1" stroke-dasharray="4,4" />
          <text x="930" y="315" text-anchor="middle" fill="#faf5f5" font-size="12" font-weight="bold">
            Provider Switching Mechanism
          </text>
        </g>
        
        <!-- Lyrics Generation Section -->
        <text x="925" y="370" text-anchor="middle" fill="#66f2ff" font-size="16" font-weight="bold">
          Lyrics Generation
        </text>
        
        <!-- Mistral Model -->
        <g class="model-box" :class="{ 'active': currentPhase >= 2 && currentPhase < 5 }">
          <rect x="730" y="390" width="400" height="120" rx="6" 
            fill="#00ff00" fill-opacity="0.15" stroke="#00ff00" stroke-width="2" />
          <text x="930" y="415" text-anchor="middle" fill="#faf5f5" font-size="14" font-weight="bold">
            Mistral / Ministral-3b-instruct
          </text>
          <text x="930" y="435" text-anchor="middle" fill="#66f2ff" font-size="11">
            Large Language Model
          </text>
          <text x="930" y="450" text-anchor="middle" fill="#66f2ff" font-size="11">
            for Lyrics Generation
          </text>
          <text x="930" y="475" text-anchor="middle" fill="#999" font-size="10">
            Transformers • Subprocess Execution
          </text>
          <text x="930" y="490" text-anchor="middle" fill="#999" font-size="10">
            /model/v1/lyrics/generate
          </text>
        </g>
        
        <!-- GenerationJob -->
        <g class="component-box">
          <rect x="730" y="530" width="190" height="100" rx="6" 
            fill="#00ff00" fill-opacity="0.1" stroke="#00ff00" stroke-width="1" />
          <text x="825" y="555" text-anchor="middle" fill="#faf5f5" font-size="13" font-weight="bold">
            GenerationJob
          </text>
          <text x="825" y="575" text-anchor="middle" fill="#66f2ff" font-size="11">
            Async Music
          </text>
          <text x="825" y="590" text-anchor="middle" fill="#66f2ff" font-size="11">
            Generation
          </text>
          <text x="825" y="610" text-anchor="middle" fill="#999" font-size="10">
            Background Tasks
          </text>
        </g>
        
        <!-- Resource Management -->
        <g class="component-box">
          <rect x="940" y="530" width="190" height="100" rx="6" 
            fill="#00ff00" fill-opacity="0.1" stroke="#00ff00" stroke-width="1" />
          <text x="1035" y="555" text-anchor="middle" fill="#faf5f5" font-size="13" font-weight="bold">
            Resource Mgmt
          </text>
          <text x="1035" y="575" text-anchor="middle" fill="#66f2ff" font-size="11">
            GPU/CPU
          </text>
          <text x="1035" y="590" text-anchor="middle" fill="#66f2ff" font-size="11">
            Allocation
          </text>
          <text x="1035" y="610" text-anchor="middle" fill="#999" font-size="10">
            Device Control
          </text>
        </g>
        
        <!-- Technology Badge -->
        <g class="tech-badge">
          <rect x="730" y="650" width="400" height="40" rx="6" 
            fill="#00ff00" fill-opacity="0.1" stroke="#00ff00" stroke-width="1" />
          <text x="930" y="675" text-anchor="middle" fill="#faf5f5" font-size="12">
            FastAPI • PyTorch • Transformers • HuggingFace
          </text>
        </g>
        
        <!-- Model Service Internal Flow -->
        <g class="model-internal-flow" v-if="currentPhase >= 3">
          <!-- To Music Models -->
          <path d="M 925 280 L 825 150" stroke="#00ff00" stroke-width="2" fill="none" 
            marker-end="url(#arrowhead-green)" class="flow-arrow" />
          <path d="M 925 280 L 1035 150" stroke="#00ff00" stroke-width="2" fill="none" 
            marker-end="url(#arrowhead-green)" class="flow-arrow" />
          <!-- To Lyrics Model -->
          <path d="M 925 290 L 930 390" stroke="#00ff00" stroke-width="2" fill="none" 
            marker-end="url(#arrowhead-green)" class="flow-arrow" />
        </g>
      </g>
      
      <!-- Arrow Markers -->
      <defs>
        <marker id="arrowhead-green" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto">
          <polygon points="0 0, 10 3, 0 6" fill="#00ff00" />
        </marker>
        <marker id="arrowhead-purple" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto">
          <polygon points="0 0, 10 3, 0 6" fill="#9673ff" />
        </marker>
      </defs>
      
      <!-- Data Flow Arrows -->
      <!-- Frontend to Backend -->
      <g class="flow-layer" v-if="currentPhase >= 1">
        <path d="M 200 400 L 250 400" stroke="#00ff00" stroke-width="3" fill="none" 
          marker-end="url(#arrowhead-green)" class="flow-arrow request-flow" />
        <circle cx="225" cy="400" r="4" fill="#00ff00" class="flow-dot" />
      </g>
      
      <!-- Backend to Model Service -->
      <g class="flow-layer" v-if="currentPhase >= 3">
        <path d="M 650 400 L 700 400" stroke="#00ff00" stroke-width="3" fill="none" 
          marker-end="url(#arrowhead-green)" class="flow-arrow request-flow" />
        <circle cx="675" cy="400" r="4" fill="#00ff00" class="flow-dot" />
      </g>
      
      <!-- Model Service to Backend (Response) -->
      <g class="flow-layer" v-if="currentPhase >= 5">
        <path d="M 700 450 L 650 450" stroke="#9673ff" stroke-width="3" fill="none" 
          marker-end="url(#arrowhead-purple)" class="flow-arrow response-flow" />
        <circle cx="675" cy="450" r="4" fill="#9673ff" class="flow-dot" />
      </g>
      
      <!-- Backend to Frontend (Response) -->
      <g class="flow-layer" v-if="currentPhase >= 5">
        <path d="M 250 450 L 200 450" stroke="#9673ff" stroke-width="3" fill="none" 
          marker-end="url(#arrowhead-purple)" class="flow-arrow response-flow" />
        <circle cx="225" cy="450" r="4" fill="#9673ff" class="flow-dot" />
      </g>
      
      <!-- Processing Indicator (Pulsing) -->
      <g class="processing-indicator" v-if="currentPhase >= 4 && currentPhase < 5">
        <circle cx="825" cy="210" r="15" fill="#00ff00" fill-opacity="0.3" class="pulse" />
        <circle cx="1035" cy="210" r="15" fill="#00ff00" fill-opacity="0.3" class="pulse" />
        <circle cx="930" cy="450" r="15" fill="#00ff00" fill-opacity="0.3" class="pulse" />
      </g>
    </svg>
  </div>
</template>

<script>
export default {
  name: 'ArchitectureDiagram',
  props: {
    autoPlay: {
      type: Boolean,
      default: true
    },
    showControls: {
      type: Boolean,
      default: true
    }
  },
  data() {
    return {
      currentPhase: 0,
      isAnimating: false,
      animationInterval: null,
      svgWidth: 1200,
      svgHeight: 800
    }
  },
  mounted() {
    if (this.autoPlay) {
      this.startAnimation()
    }
    // Make SVG responsive
    this.updateDimensions()
    window.addEventListener('resize', this.updateDimensions)
  },
  beforeUnmount() {
    this.stopAnimation()
    window.removeEventListener('resize', this.updateDimensions)
  },
  methods: {
    startAnimation() {
      if (this.isAnimating) return
      this.isAnimating = true
      this.currentPhase = 0
      
      // Phase 1: Frontend to Backend (0-15s)
      setTimeout(() => {
        if (this.isAnimating) this.currentPhase = 1
      }, 0)
      
      // Phase 2: Backend internal processing (15-25s)
      setTimeout(() => {
        if (this.isAnimating) this.currentPhase = 2
      }, 15000)
      
      // Phase 3: Backend to Model Service (25-35s)
      setTimeout(() => {
        if (this.isAnimating) this.currentPhase = 3
      }, 25000)
      
      // Phase 4: AI model processing (35-45s)
      setTimeout(() => {
        if (this.isAnimating) this.currentPhase = 4
      }, 35000)
      
      // Phase 5: Response flow (45-55s)
      setTimeout(() => {
        if (this.isAnimating) this.currentPhase = 5
      }, 45000)
      
      // Phase 6: Completed state (55-60s)
      setTimeout(() => {
        if (this.isAnimating) this.currentPhase = 6
      }, 55000)
      
      // Loop after 60 seconds
      setTimeout(() => {
        if (this.isAnimating) {
          this.resetAnimation()
          this.startAnimation()
        }
      }, 60000)
    },
    stopAnimation() {
      this.isAnimating = false
    },
    toggleAnimation() {
      if (this.isAnimating) {
        this.stopAnimation()
      } else {
        this.startAnimation()
      }
    },
    resetAnimation() {
      this.stopAnimation()
      this.currentPhase = 0
    },
    updateDimensions() {
      const container = this.$el
      if (container) {
        const containerWidth = container.clientWidth || 1200
        this.svgWidth = Math.min(containerWidth, 1200)
        this.svgHeight = 800
      }
    }
  }
}
</script>

<style scoped>
.architecture-diagram {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  background: var(--color-dark);
}

.diagram-controls {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  justify-content: center;
}

.diagram-controls button {
  background: #666;
  color: #ccc;
  border: 2px solid #666;
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.diagram-controls button:hover:not(:disabled) {
  background: var(--color-secondary);
  color: var(--color-neutral);
  border-color: var(--color-secondary);
  box-shadow: 0 0 15px rgba(150, 115, 255, 0.5);
}

.diagram-controls button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.diagram-svg {
  width: 100%;
  height: auto;
  display: block;
}

/* Active states */
.frontend-layer.active rect,
.backend-layer.active rect,
.model-service-layer.active rect {
  stroke-width: 3;
  filter: drop-shadow(0 0 10px currentColor);
}

.service-box.active rect,
.model-box.active rect {
  stroke-width: 3;
  fill-opacity: 0.3;
  filter: drop-shadow(0 0 8px currentColor);
  animation: pulse-border 2s ease-in-out infinite;
}

.component-box.active rect {
  stroke-width: 2;
  fill-opacity: 0.2;
}

@keyframes pulse-border {
  0%, 100% {
    stroke-width: 2;
    filter: drop-shadow(0 0 8px currentColor);
  }
  50% {
    stroke-width: 3;
    filter: drop-shadow(0 0 15px currentColor);
  }
}

/* Flow animations */
.flow-arrow {
  stroke-dasharray: 10, 5;
  animation: flow-arrow 2s linear infinite;
}

.request-flow {
  stroke: var(--color-primary);
}

.response-flow {
  stroke: var(--color-secondary);
}

@keyframes flow-arrow {
  0% {
    stroke-dashoffset: 0;
    opacity: 1;
  }
  100% {
    stroke-dashoffset: -15;
    opacity: 0.8;
  }
}

.flow-dot {
  animation: flow-dot 2s ease-in-out infinite;
}

@keyframes flow-dot {
  0%, 100% {
    opacity: 0.5;
    r: 4;
  }
  50% {
    opacity: 1;
    r: 6;
  }
}

/* Processing pulse */
.pulse {
  animation: pulse-circle 1.5s ease-in-out infinite;
}

@keyframes pulse-circle {
  0%, 100% {
    opacity: 0.3;
    r: 15;
  }
  50% {
    opacity: 0.6;
    r: 20;
  }
}

/* Internal flow */
.internal-flow .flow-arrow,
.model-internal-flow .flow-arrow {
  stroke-dasharray: 8, 4;
  animation: flow-arrow 1.5s linear infinite;
}

/* Hover effects */
.service-box:hover rect,
.model-box:hover rect,
.component-box:hover rect {
  stroke-width: 3;
  fill-opacity: 0.25;
  transition: all 0.3s ease;
}

/* Responsive adjustments */
@media (max-width: 1200px) {
  .architecture-diagram {
    padding: 10px;
  }
  
  .diagram-svg {
    transform: scale(0.9);
    transform-origin: top left;
  }
}

@media (max-width: 768px) {
  .diagram-svg {
    transform: scale(0.7);
    transform-origin: top left;
  }
}
</style>
