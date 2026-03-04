<template>
  <div id="app">
    <NavBar />
    <main class="container">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import NavBar from "./components/NavBar.vue";
import { useAuthStore } from "./store/auth.js";
import { onMounted } from "vue";

const auth = useAuthStore();
onMounted(() => {
  if (auth.isLoggedIn) auth.fetchUser();
});
</script>

<style>
:root {
  --primary: #4f46e5;
  --primary-hover: #4338ca;
  --danger: #ef4444;
  --bg: #f9fafb;
  --card-bg: #ffffff;
  --text: #111827;
  --text-muted: #6b7280;
  --border: #e5e7eb;
  --radius: 8px;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  background: var(--bg);
  color: var(--text);
  line-height: 1.6;
}

.container {
  max-width: 960px;
  margin: 2rem auto;
  padding: 0 1rem;
}

button {
  cursor: pointer;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: var(--radius);
  font-size: 0.9rem;
  font-weight: 500;
  transition: background 0.2s;
}

.btn-primary {
  background: var(--primary);
  color: white;
}
.btn-primary:hover {
  background: var(--primary-hover);
}

.btn-danger {
  background: var(--danger);
  color: white;
}
.btn-danger:hover {
  background: #dc2626;
}

.btn-secondary {
  background: var(--border);
  color: var(--text);
}
.btn-secondary:hover {
  background: #d1d5db;
}

input,
select {
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  font-size: 0.9rem;
  width: 100%;
}

input:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.15);
}

.card {
  background: var(--card-bg);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 1.5rem;
  margin-bottom: 1rem;
}

.error {
  color: var(--danger);
  font-size: 0.85rem;
  margin-top: 0.25rem;
}
</style>