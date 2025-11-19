<template>
  <div class="page-links">
    <div class="container">
      <WaveText text="OMG - 39C3 power circus - oPEN mUSIC gENERATOR" tag="h1" />
      <p style="color: var(--color-neutral); margin-bottom: 30px;">
        An open and free music generation app for the 39C3 power circus.
        Generates lyrics and music for your show - all with free and open source mdoels.
      </p>
      <Navigation />
    </div>
    <div class="container">
      <div class="links-grid">
        <div 
          v-for="(card, index) in cards" 
          :key="index"
          class="link-card"
          :class="{ 'flickering': card.isFlickering }"
          :style="{ 
            '--flicker-color': card.flickerColor,
            '--flicker-rgba-40': card.flickerRgba40,
            '--flicker-rgba-20': card.flickerRgba20,
            '--flicker-rgba-80': card.flickerRgba80,
            '--flicker-rgba-60': card.flickerRgba60,
            '--flicker-rgba-50': card.flickerRgba50,
            '--flicker-rgba-30': card.flickerRgba30,
            '--flicker-rgba-70': card.flickerRgba70,
            '--flicker-rgba-90': card.flickerRgba90
          }"
        >
          <h2>
            <span style="font-weight: 100">{{ card.title.split(' ')[0] }}</span>
            <span style="font-weight: 10">{{ card.title.split(' ').slice(1).join(' ') ? ' ' + card.title.split(' ').slice(1).join(' ') : '' }}</span>
          </h2>
          <p>{{ card.description }}</p>
          <a :href="card.url" target="_blank" rel="noopener noreferrer" class="link-button">
            {{ card.buttonText }} →
          </a>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Navigation from '../components/Navigation.vue'
import WaveText from '../components/WaveText.vue'

export default {
  name: 'Links',
  components: {
    Navigation,
    WaveText
  },
  data() {
    return {
      colors: [
        { hex: '#66f2ff', rgb: [102, 242, 255] },  // cyan
        { hex: '#9673ff', rgb: [150, 115, 255] }, // purple
        { hex: '#00ff00', rgb: [0, 255, 0] },     // green
        { hex: '#ff3719', rgb: [255, 55, 25] }    // red
      ],
      cards: [
        {
          title: 'c-base',
          description: 'A hackerspace and community in Berlin, Germany',
          url: 'https://www.c-base.org/',
          buttonText: 'Visit c-base',
          flickerColor: '#66f2ff',
          flickerRgba40: 'rgba(102, 242, 255, 0.4)',
          flickerRgba20: 'rgba(102, 242, 255, 0.2)',
          flickerRgba80: 'rgba(102, 242, 255, 0.8)',
          flickerRgba60: 'rgba(102, 242, 255, 0.6)',
          flickerRgba50: 'rgba(102, 242, 255, 0.5)',
          flickerRgba30: 'rgba(102, 242, 255, 0.3)',
          flickerRgba70: 'rgba(102, 242, 255, 0.7)',
          flickerRgba90: 'rgba(102, 242, 255, 0.9)',
          isFlickering: false
        },
        {
          title: '<<39C3',
          description: '39th Chaos Communication Congress - The world\'s largest hacker convention',
          url: 'https://events.ccc.de/category/39c3/',
          buttonText: 'Visit 39C3',
          flickerColor: '#66f2ff',
          flickerRgba40: 'rgba(102, 242, 255, 0.4)',
          flickerRgba20: 'rgba(102, 242, 255, 0.2)',
          flickerRgba80: 'rgba(102, 242, 255, 0.8)',
          flickerRgba60: 'rgba(102, 242, 255, 0.6)',
          flickerRgba50: 'rgba(102, 242, 255, 0.5)',
          flickerRgba30: 'rgba(102, 242, 255, 0.3)',
          flickerRgba70: 'rgba(102, 242, 255, 0.7)',
          flickerRgba90: 'rgba(102, 242, 255, 0.9)',
          isFlickering: false
        },
        {
          title: 'Chaos Computer Club',
          description: 'The Chaos Computer Club (CCC) is Europe\'s largest association of hackers',
          url: 'https://www.ccc.de/en/',
          buttonText: 'Visit CCC',
          flickerColor: '#66f2ff',
          flickerRgba40: 'rgba(102, 242, 255, 0.4)',
          flickerRgba20: 'rgba(102, 242, 255, 0.2)',
          flickerRgba80: 'rgba(102, 242, 255, 0.8)',
          flickerRgba60: 'rgba(102, 242, 255, 0.6)',
          flickerRgba50: 'rgba(102, 242, 255, 0.5)',
          flickerRgba30: 'rgba(102, 242, 255, 0.3)',
          flickerRgba70: 'rgba(102, 242, 255, 0.7)',
          flickerRgba90: 'rgba(102, 242, 255, 0.9)',
          isFlickering: false
        },
        {
          title: 'Sven Tastic',
          description: 'The amazing performer behind the 39C3 power circus show.',
          url: 'https://www.instagram.com/sventastictube/',
          buttonText: 'Follow on Instagram',
          flickerColor: '#9673ff',
          flickerRgba40: 'rgba(150, 115, 255, 0.4)',
          flickerRgba20: 'rgba(150, 115, 255, 0.2)',
          flickerRgba80: 'rgba(150, 115, 255, 0.8)',
          flickerRgba60: 'rgba(150, 115, 255, 0.6)',
          flickerRgba50: 'rgba(150, 115, 255, 0.5)',
          flickerRgba30: 'rgba(150, 115, 255, 0.3)',
          flickerRgba70: 'rgba(150, 115, 255, 0.7)',
          flickerRgba90: 'rgba(150, 115, 255, 0.9)',
          isFlickering: false
        },
        {
          title: 'OMG Project',
          description: 'Open Music Generator - An open and free music generation application for the 39C3 power circus',
          url: 'https://github.com/nerdhof/omg',
          buttonText: 'View on GitHub',
          flickerColor: '#00ff00',
          flickerRgba40: 'rgba(0, 255, 0, 0.4)',
          flickerRgba20: 'rgba(0, 255, 0, 0.2)',
          flickerRgba80: 'rgba(0, 255, 0, 0.8)',
          flickerRgba60: 'rgba(0, 255, 0, 0.6)',
          flickerRgba50: 'rgba(0, 255, 0, 0.5)',
          flickerRgba30: 'rgba(0, 255, 0, 0.3)',
          flickerRgba70: 'rgba(0, 255, 0, 0.7)',
          flickerRgba90: 'rgba(0, 255, 0, 0.9)',
          isFlickering: false
        },
        {
          title: 'OC23 Youth Club',
          description: 'The Youth Club of where I learned juggling and meet many nice people.',
          url: 'https://www.instagram.com/jfeoc23',
          buttonText: 'Visit OC23',
          flickerColor: '#9673ff',
          flickerRgba40: 'rgba(150, 115, 255, 0.4)',
          flickerRgba20: 'rgba(150, 115, 255, 0.2)',
          flickerRgba80: 'rgba(150, 115, 255, 0.8)',
          flickerRgba60: 'rgba(150, 115, 255, 0.6)',
          flickerRgba50: 'rgba(150, 115, 255, 0.5)',
          flickerRgba30: 'rgba(150, 115, 255, 0.3)',
          flickerRgba70: 'rgba(150, 115, 255, 0.7)',
          flickerRgba90: 'rgba(150, 115, 255, 0.9)',
          isFlickering: false
        },
        {
          title: 'ACE-Step Project',
          description: 'An open-source AI music generation model developed by ACE Studio and StepFun',
          url: 'https://github.com/ace-step/ACE-Step',
          buttonText: 'View on GitHub',
          flickerColor: '#ff3719',
          flickerRgba40: 'rgba(255, 55, 25, 0.4)',
          flickerRgba20: 'rgba(255, 55, 25, 0.2)',
          flickerRgba80: 'rgba(255, 55, 25, 0.8)',
          flickerRgba60: 'rgba(255, 55, 25, 0.6)',
          flickerRgba50: 'rgba(255, 55, 25, 0.5)',
          flickerRgba30: 'rgba(255, 55, 25, 0.3)',
          flickerRgba70: 'rgba(255, 55, 25, 0.7)',
          flickerRgba90: 'rgba(255, 55, 25, 0.9)',
          isFlickering: false
        },
        {
          title: 'LeVo Song Generation',
          description: 'A high-quality song generation model with multi-preference alignment by Tencent AI Lab',
          url: 'https://github.com/tencent-ailab/SongGeneration',
          buttonText: 'View on GitHub',
          flickerColor: '#ff3719',
          flickerRgba40: 'rgba(255, 55, 25, 0.4)',
          flickerRgba20: 'rgba(255, 55, 25, 0.2)',
          flickerRgba80: 'rgba(255, 55, 25, 0.8)',
          flickerRgba60: 'rgba(255, 55, 25, 0.6)',
          flickerRgba50: 'rgba(255, 55, 25, 0.5)',
          flickerRgba30: 'rgba(255, 55, 25, 0.3)',
          flickerRgba70: 'rgba(255, 55, 25, 0.7)',
          flickerRgba90: 'rgba(255, 55, 25, 0.9)',
          isFlickering: false
        },
        {
          title: 'Mistral AI',
          description: 'Open-source AI models and technology for developers',
          url: 'https://www.mistral.ai/',
          buttonText: 'Visit Mistral AI',
          flickerColor: '#ff3719',
          flickerRgba40: 'rgba(255, 55, 25, 0.4)',
          flickerRgba20: 'rgba(255, 55, 25, 0.2)',
          flickerRgba80: 'rgba(255, 55, 25, 0.8)',
          flickerRgba60: 'rgba(255, 55, 25, 0.6)',
          flickerRgba50: 'rgba(255, 55, 25, 0.5)',
          flickerRgba30: 'rgba(255, 55, 25, 0.3)',
          flickerRgba70: 'rgba(255, 55, 25, 0.7)',
          flickerRgba90: 'rgba(255, 55, 25, 0.9)',
          isFlickering: false
        }
      ],
      flickerInterval: null
    }
  },
  mounted() {
    this.startRandomFlickering()
  },
  beforeUnmount() {
    if (this.flickerInterval) {
      clearInterval(this.flickerInterval)
    }
  },
  methods: {
    assignRandomColor(card) {
      // Pick a random color from the 4 available colors
      const randomColor = this.colors[Math.floor(Math.random() * this.colors.length)]
      const [r, g, b] = randomColor.rgb
      
      // Assign the color and all rgba variations
      card.flickerColor = randomColor.hex
      card.flickerRgba40 = `rgba(${r}, ${g}, ${b}, 0.4)`
      card.flickerRgba20 = `rgba(${r}, ${g}, ${b}, 0.2)`
      card.flickerRgba80 = `rgba(${r}, ${g}, ${b}, 0.8)`
      card.flickerRgba60 = `rgba(${r}, ${g}, ${b}, 0.6)`
      card.flickerRgba50 = `rgba(${r}, ${g}, ${b}, 0.5)`
      card.flickerRgba30 = `rgba(${r}, ${g}, ${b}, 0.3)`
      card.flickerRgba70 = `rgba(${r}, ${g}, ${b}, 0.7)`
      card.flickerRgba90 = `rgba(${r}, ${g}, ${b}, 0.9)`
    },
    startRandomFlickering() {
      // Randomly turn cards on/off at different intervals
      this.cards.forEach((card, index) => {
        const baseDelay = Math.random() * 2000 // 0-2 seconds initial delay
        const initialState = Math.random() > 0.5 // Randomly start on or off
        
        setTimeout(() => {
          this.toggleCardState(index, initialState)
        }, baseDelay)
      })
    },
    toggleCardState(index, turnOn) {
      const card = this.cards[index]
      if (!card) return
      
      if (turnOn) {
        // Assign a random color when turning on
        this.assignRandomColor(card)
        
        // Turn the card on (flickering state)
        card.isFlickering = true
        
        // Random duration to stay on: 1-5 seconds
        const onDuration = 1000 + Math.random() * 4000
        
        setTimeout(() => {
          // Turn off and schedule next toggle
          this.toggleCardState(index, false)
        }, onDuration)
      } else {
        // Turn the card off (normal state)
        card.isFlickering = false
        
        // Random duration to stay off: 1-5 seconds
        const offDuration = 1000 + Math.random() * 4000
        
        setTimeout(() => {
          // Turn on and schedule next toggle
          this.toggleCardState(index, true)
        }, offDuration)
      }
    }
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

.link-card.flickering {
  border-color: var(--flicker-color);
  box-shadow: 0 0 20px var(--flicker-rgba-40), 
              0 0 40px var(--flicker-rgba-20);
  animation: pulseGlow 2s ease-in-out infinite;
  transition: border-color 0.3s ease, box-shadow 0.3s ease;
}

.link-card.flickering h2 {
  color: var(--flicker-color);
  text-shadow: 0 0 15px var(--flicker-rgba-80), 
               0 0 25px var(--flicker-rgba-60);
  transition: color 0.3s ease, text-shadow 0.3s ease;
  animation: pulseText 2s ease-in-out infinite;
}

.link-card.flickering p {
  color: var(--flicker-color);
  text-shadow: 0 0 10px var(--flicker-rgba-50);
  transition: color 0.3s ease, text-shadow 0.3s ease;
}

@keyframes pulseGlow {
  0%, 100% {
    box-shadow: 0 0 20px var(--flicker-rgba-40), 
                0 0 40px var(--flicker-rgba-20);
  }
  50% {
    box-shadow: 0 0 30px var(--flicker-rgba-50), 
                0 0 60px var(--flicker-rgba-30);
  }
}

@keyframes pulseText {
  0%, 100% {
    text-shadow: 0 0 15px var(--flicker-rgba-80), 
                  0 0 25px var(--flicker-rgba-60);
  }
  50% {
    text-shadow: 0 0 20px var(--flicker-rgba-90), 
                  0 0 35px var(--flicker-rgba-70);
  }
}

.link-card:hover {
  border-color: var(--flicker-color);
  box-shadow: 0 0 20px var(--flicker-rgba-40), 0 0 40px var(--flicker-rgba-20);
  transform: translateY(-5px);
}

.link-card h2 {
  color: white;
  text-shadow: 0 0 10px var(--flicker-rgba-50);
  margin-bottom: 15px;
  font-size: 1.5em;
  transition: color 0.3s, text-shadow 0.3s;
}

.link-card:hover h2 {
  color: var(--flicker-color);
  text-shadow: 0 0 15px var(--flicker-rgba-80), 0 0 25px var(--flicker-rgba-60);
}

.link-card p {
  color: white;
  line-height: 1.6;
  margin-bottom: 20px;
  flex-grow: 1;
  transition: color 0.3s, text-shadow 0.3s;
}

.link-card:hover p {
  color: var(--flicker-color);
  text-shadow: 0 0 10px var(--flicker-rgba-50);
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
  background: var(--flicker-color);
  color: var(--color-dark);
  border-color: var(--flicker-color);
  box-shadow: 0 0 20px var(--flicker-rgba-50);
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

