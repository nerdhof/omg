<template>
  <component :is="tag" :class="['wave-text', className, { 'static-weights': !animated }]">
    <span 
      v-for="(char, index) in chars" 
      :key="index" 
      :style="getCharStyle(index)"
      :class="{ 'first-word': isInFirstWord(index) && !animated }"
    >
      {{ char === ' ' ? '\u00A0' : char }}
    </span>
  </component>
</template>

<script>
export default {
  name: 'WaveText',
  props: {
    text: {
      type: String,
      required: true
    },
    tag: {
      type: String,
      default: 'h1'
    },
    delay: {
      type: Number,
      default: 0.05
    },
    className: {
      type: String,
      default: ''
    },
    animated: {
      type: Boolean,
      default: true
    },
    firstWordWeight: {
      type: Number,
      default: 100
    },
    restWeight: {
      type: Number,
      default: 10
    }
  },
  computed: {
    chars() {
      return this.text.split('')
    },
    firstWordEndIndex() {
      // Find the index where the first word ends (first space)
      const firstSpaceIndex = this.text.indexOf(' ')
      return firstSpaceIndex === -1 ? this.text.length : firstSpaceIndex
    }
  },
  methods: {
    getCharStyle(index) {
      if (this.animated) {
        return { animationDelay: `${index * this.delay}s` }
      } else {
        return { 
          fontWeight: this.isInFirstWord(index) ? this.firstWordWeight : this.restWeight 
        }
      }
    },
    isInFirstWord(index) {
      return index < this.firstWordEndIndex
    }
  }
}
</script>

<style scoped>
.wave-text {
  display: block;
  font-kerning: none;
  text-align: center;
}

.wave-text span {
  display: inline-block;
  font-kerning: none;
}

.wave-text:not(.static-weights) span {
  animation: font_weight_wave 3s ease-in-out infinite alternate;
}

.wave-text.static-weights span {
  transition: font-weight 0.3s;
}
</style>

