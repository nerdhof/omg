<template>
  <nav class="navigation">
    <div class="nav-container">
      <router-link to="/" class="nav-link nav-link-home">OMG</router-link>
      <router-link to="/background" class="nav-link nav-link-background">Background</router-link>
      <router-link to="/architecture" class="nav-link nav-link-architecture">Architecture</router-link>
      <router-link to="/links" class="nav-link nav-link-links">Links</router-link>
    </div>
  </nav>
</template>

<script>
export default {
  name: 'Navigation'
}
</script>

<style scoped>
.navigation {
  background-color: var(--color-dark);
  padding: 1rem 0;
}

.nav-container {
  max-width: 1200px;
  margin: 1 auto;
  padding: 0 2rem;
  display: flex;
  gap: 0;
  align-items: center;
  justify-content: center;
}

.nav-link {
  color: var(--color-neutral);
  text-decoration: none;
  font-family: 'OfficerSans', sans-serif;
  font-size: 1rem;
  padding: 0.5rem 0.5rem;
  border-radius: 4px;
  transition: all 0.2s ease;
}

.nav-link:hover {
  color: var(--color-primary);
  background-color: rgba(0, 255, 0, 0.1);
}

/* Home - Violet */
.nav-link-home.router-link-active {
  color: var(--color-secondary);
  font-weight: bold;
  background-color: rgba(150, 115, 255, 0.1);
}

.nav-link-home:hover {
  color: var(--color-secondary);
  background-color: rgba(150, 115, 255, 0.1);
}

/* Background - Cyan */
.nav-link-background.router-link-active {
  color: var(--color-additional-02);
  font-weight: bold;
  background-color: rgba(102, 242, 255, 0.1);
}

.nav-link-background:hover {
  color: var(--color-additional-02);
  background-color: rgba(102, 242, 255, 0.1);
}

/* Architecture - Neon Orange */
.nav-link-architecture.router-link-active {
  color: var(--color-additional-01);
  font-weight: bold;
  background-color: rgba(255, 55, 25, 0.1);
}

.nav-link-architecture:hover {
  color: var(--color-additional-01);
  background-color: rgba(255, 55, 25, 0.1);
}

/* Links - Green */
.nav-link-links.router-link-active {
  color: var(--color-primary);
  font-weight: bold;
  background-color: rgba(0, 255, 0, 0.1);
}

.nav-link-links:hover {
  color: var(--color-primary);
  background-color: rgba(0, 255, 0, 0.1);
}
</style>

