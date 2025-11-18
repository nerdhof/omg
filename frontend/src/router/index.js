import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Background from '../views/Background.vue'
import Architecture from '../views/Architecture.vue'
import Links from '../views/Links.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/background',
    name: 'Background',
    component: Background
  },
  {
    path: '/architecture',
    name: 'Architecture',
    component: Architecture
  },
  {
    path: '/links',
    name: 'Links',
    component: Links
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router

