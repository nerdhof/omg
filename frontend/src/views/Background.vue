<template>
  <div class="page-background">
    <div class="container">
      <WaveText text="OMG - 39C3 power circus - oPEN mUSIC gENERATOR" tag="h1" />
      <p style="color: var(--color-neutral); margin-bottom: 30px;">
        An open and free music generation app for the 39C3 power circus.
        Generates lyrics and music for your show - all with free and open source models.
      </p>
      <Navigation />
    </div>

    <!-- Slideshow Container -->
    <div class="slideshow-container">
      <div class="slideshow-wrapper">
        <div 
          v-for="(slide, index) in slides" 
          :key="index"
          class="slide"
          :class="{ active: currentSlide === index }"
        >
          <div 
            class="slide-content clickable"
            @click="handleSlideClick"
            :title="currentSlide < slides.length - 1 ? 'Click to go to next slide' : 'Click to go back to first slide'"
          >
            <div v-if="slide.image" class="slide-image">
              <img :src="slide.image" :alt="stripHtml(slide.title)" />
            </div>
            <div class="slide-text">
              <h2 v-if="slide.title" v-html="slide.title"></h2>
              <div v-html="slide.content"></div>
            </div>
          </div>
        </div>
      </div>

      <!-- Navigation Controls -->
      <div class="slideshow-controls">
        <button 
          @click.stop="previousSlide" 
          :disabled="currentSlide === 0"
          class="nav-button prev-button"
        >
          ← Previous
        </button>
        <div class="slide-indicators">
          <span 
            v-for="(slide, index) in slides" 
            :key="index"
            class="indicator"
            :class="{ active: currentSlide === index }"
            @click.stop="goToSlide(index)"
          ></span>
        </div>
        <button 
          @click.stop="nextSlide" 
          :disabled="currentSlide === slides.length - 1"
          class="nav-button next-button"
        >
          Next →
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import Navigation from '../components/Navigation.vue'
import WaveText from '../components/WaveText.vue'

export default {
  name: 'Background',
  components: {
    Navigation,
    WaveText
  },
  data() {
    return {
      currentSlide: 0,
      slides: [
        {
          title: '<span style="font-weight: 100">&lt;&lt;39C3</span><span style="font-weight: 10"> - Chaos Communication Congress</span>',
          content: `
            <p>39C3 is this year's edition of the world's largest hacker convention, the <strong>Chaos Communication Congress</strong>. More than a congress, this is <strong>5 days of a community-driven, utopian cyberpunk world for the whole family</strong>. A gathering where hackers, makers, artists, and curious minds come together to share knowledge, build projects, and create something extraordinary.</p>
          `,
          image: '/images/ccc-building-night.jpg'
        },
        {
          title: '<span style="font-weight: 10">The</span><span style="font-weight: 100"> Community</span>',
          content: `
            <p>I'm a long-time member of the <strong>c-base hackerspace</strong> and part of the <strong>Chaos Computer Family</strong> for years. In fact, I even met my wife there – the community has been central to my life. This is where ideas become reality, where collaboration happens, and where lifelong connections are made.</p>
          `,
          image: '/images/hackathon-indoor.jpg'
        },
        {
          title: '<span style="font-weight: 10">Combining</span><span style="font-weight: 100"> Circus</span><span style="font-weight: 10"> with </span><span style="font-weight: 100"> Chaos</span>',
          content: `
            <p>As I started juggling, some of the guys training with me are joining in this year. We want to <strong>combine circus with chaos</strong> – bringing together the art of performance with the spirit of hacking. This means open-sourcing everything: <strong>lighted prop building</strong> including 3D prints, chip designs, and embedded software. We're planning a circus show at the congress and spreading the fun of juggling throughout the event.</p>
          `,
          image: '/images/light-play-night.jpg'
        },
        {
          title: '<span style="font-weight: 100">The</span><span style="font-weight: 10"> Missing Piece</span>',
          content: `
            <p>But we're still <strong>lacking music for the show</strong>. Creating original music that fits the energy and spirit of our performance is essential, but traditional music production can be expensive and restrictive. We need something that matches our ethos: <strong>open, free, and hackable</strong>.</p>
          `,
          image: '/images/cch-building-night.jpg'
        },
        {
          title: '<span style="font-weight: 10">Enter</span><span style="font-weight: 100"> Open </span><span style="font-weight: 10"> Source AI</span>',
          content: `
            <p>That's where <strong>AI comes into play</strong>. However, we want to keep all components <strong>free and hackable</strong>, so we're focused exclusively on <strong>Open Source Networks</strong>. No proprietary models, no locked APIs, no restrictions – just pure, open-source technology that anyone can use, modify, and improve. This project embodies the hacker spirit: building something useful, sharing it freely, and making it better together.</p>
          `,
          image: '/images/hackathon-wide.jpg'
        }
      ]
    }
  },
  mounted() {
    // Add keyboard navigation
    window.addEventListener('keydown', this.handleKeyPress)
  },
  beforeUnmount() {
    // Clean up keyboard listener
    window.removeEventListener('keydown', this.handleKeyPress)
  },
  methods: {
    stripHtml(html) {
      const div = document.createElement('div')
      div.innerHTML = html
      return div.textContent || div.innerText || ''
    },
    nextSlide() {
      if (this.currentSlide < this.slides.length - 1) {
        this.currentSlide++
      }
    },
    previousSlide() {
      if (this.currentSlide > 0) {
        this.currentSlide--
      }
    },
    goToSlide(index) {
      this.currentSlide = index
    },
    handleKeyPress(event) {
      // Arrow keys for navigation
      if (event.key === 'ArrowRight') {
        this.nextSlide()
      } else if (event.key === 'ArrowLeft') {
        this.previousSlide()
      }
    },
    handleSlideClick() {
      // Advance to next slide, or loop back to first if on last slide
      if (this.currentSlide < this.slides.length - 1) {
        this.nextSlide()
      } else {
        this.currentSlide = 0
      }
    }
  }
}
</script>

<style scoped>
/* Background page - Cyan theme */
.page-background :deep(.container) {
  border-color: #666;
}

.page-background :deep(.container:hover) {
  border-color: var(--color-additional-02);
  box-shadow: 0 0 20px rgba(102, 242, 255, 0.2), 0 0 40px rgba(102, 242, 255, 0.1);
}

.page-background :deep(h1) {
  color: var(--color-additional-02);
  text-shadow: 0 0 10px rgba(102, 242, 255, 0.5);
}

.page-background :deep(h1:hover) {
  text-shadow: 0 0 15px rgba(102, 242, 255, 0.8);
}

.page-background :deep(h2:hover) {
  color: var(--color-additional-02);
  text-shadow: 0 0 10px rgba(102, 242, 255, 0.5);
}

.page-background :deep(button:hover:not(:disabled)) {
  background: var(--color-additional-02);
  border-color: var(--color-additional-02);
  box-shadow: 0 0 20px rgba(102, 242, 255, 0.5);
}

.page-background :deep(input[type="text"]:hover),
.page-background :deep(input[type="number"]:hover),
.page-background :deep(select:hover),
.page-background :deep(textarea:hover) {
  border-color: var(--color-additional-02);
  box-shadow: 0 0 10px rgba(102, 242, 255, 0.2), 0 0 20px rgba(102, 242, 255, 0.1);
  background: rgba(102, 242, 255, 0.03);
}

.page-background :deep(input[type="text"]:focus),
.page-background :deep(input[type="number"]:focus),
.page-background :deep(select:focus),
.page-background :deep(textarea:focus) {
  border-color: var(--color-additional-02);
  box-shadow: 0 0 10px rgba(102, 242, 255, 0.3);
}

/* Slideshow Styles */
.slideshow-container {
  position: relative;
  margin-top: 20px;
}

.slideshow-wrapper {
  position: relative;
  min-height: 500px;
  overflow: hidden;
}

.slide {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  opacity: 0;
  transform: translateX(50px);
  transition: opacity 0.6s ease, transform 0.6s ease;
  pointer-events: none;
}

.slide.active {
  opacity: 1;
  transform: translateX(0);
  pointer-events: auto;
  position: relative;
}

.slide-content {
  display: flex;
  gap: 30px;
  align-items: center;
  background: rgba(20, 20, 20, 0.95);
  border: 2px solid #666;
  border-radius: 8px;
  padding: 30px;
  transition: border-color 0.3s, box-shadow 0.3s;
}

.slide-content.clickable {
  cursor: pointer;
}

.slide-content:hover {
  border-color: var(--color-additional-02);
  box-shadow: 0 0 20px rgba(102, 242, 255, 0.2), 0 0 40px rgba(102, 242, 255, 0.1);
}

.slide-image {
  flex: 0 0 40%;
  max-width: 500px;
  border-radius: 8px;
  overflow: hidden;
  border: 2px solid rgba(102, 242, 255, 0.3);
}

.slide-image img {
  width: 100%;
  height: auto;
  display: block;
  transition: transform 0.3s ease;
}

.slide-content:hover .slide-image img {
  transform: scale(1.05);
}

.slide-text {
  flex: 1;
  color: var(--color-neutral);
}

.slide-text h2 {
  color: var(--color-additional-02);
  text-shadow: 0 0 10px rgba(102, 242, 255, 0.5);
  margin-bottom: 20px;
  font-size: 2em;
}

.slide-text p {
  margin-bottom: 20px;
  line-height: 1.8;
  font-size: 1.1em;
  padding: 15px 20px;
  background: rgba(102, 242, 255, 0.05);
  border-left: 4px solid rgba(102, 242, 255, 0.4);
  border-radius: 4px;
  transition: all 0.3s ease;
}

.slide-text p:hover {
  background: rgba(102, 242, 255, 0.08);
  border-left-color: var(--color-additional-02);
  transform: translateX(5px);
  box-shadow: 0 2px 8px rgba(102, 242, 255, 0.1);
}

.slide-text p:last-child {
  margin-bottom: 0;
}

.slide-text strong {
  color: var(--color-additional-02);
  text-shadow: 0 0 5px rgba(102, 242, 255, 0.3);
}

/* Navigation Controls */
.slideshow-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 30px;
  padding: 20px;
  background: rgba(20, 20, 20, 0.95);
  border: 2px solid #666;
  border-radius: 8px;
}

.nav-button {
  background: #666;
  color: #ccc;
  border: 2px solid #666;
  padding: 12px 24px;
  border-radius: 6px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.nav-button:hover:not(:disabled) {
  background: var(--color-additional-02);
  color: var(--color-dark);
  border-color: var(--color-additional-02);
  box-shadow: 0 0 20px rgba(102, 242, 255, 0.5);
  transform: translateY(-2px);
}

.nav-button:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.slide-indicators {
  display: flex;
  gap: 10px;
  align-items: center;
}

.indicator {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #666;
  cursor: pointer;
  transition: all 0.3s;
  border: 2px solid transparent;
}

.indicator:hover {
  background: var(--color-additional-02);
  box-shadow: 0 0 10px rgba(102, 242, 255, 0.5);
  transform: scale(1.2);
}

.indicator.active {
  background: var(--color-additional-02);
  box-shadow: 0 0 15px rgba(102, 242, 255, 0.8);
  border-color: var(--color-additional-02);
  transform: scale(1.3);
}

/* Responsive Design */
@media (max-width: 768px) {
  .slide-content {
    flex-direction: column;
  }

  .slide-image {
    flex: 1;
    max-width: 100%;
    width: 100%;
  }

  .slide-text h2 {
    font-size: 1.5em;
  }

  .slide-text p {
    font-size: 1em;
  }

  .slideshow-controls {
    flex-wrap: wrap;
    gap: 15px;
  }

  .slide-indicators {
    order: 3;
    width: 100%;
    justify-content: center;
    margin-top: 10px;
  }
}
</style>
