<template>
  <nav class="navbar">
    <router-link to="/" class="brand">Price Tracker</router-link>
    <div class="nav-links">
      <template v-if="auth.isLoggedIn">
        <router-link to="/" class="home-link">Home</router-link>
        <router-link v-if="auth.isAdmin" to="/admin" class="admin-link">Admin</router-link>
        <router-link to="/settings" class="settings-link">Settings</router-link>
        <span class="greeting">{{ auth.user?.username }}</span>
        <button class="btn-secondary" @click="logout">Logout</button>
      </template>
      <template v-else>
        <router-link to="/login">Login</router-link>
        <router-link to="/register">Register</router-link>
      </template>
    </div>
  </nav>
</template>

<script setup>
import { useAuthStore } from "../store/auth.js";
import { useRouter } from "vue-router";

const auth = useAuthStore();
const router = useRouter();

function logout() {
  auth.logout();
  router.push("/login");
}
</script>

<style scoped>
.navbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 2rem;
  background: var(--card-bg);
  border-bottom: 1px solid var(--border);
}

.brand {
  font-weight: 700;
  font-size: 1.2rem;
  color: var(--primary);
  text-decoration: none;
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.nav-links a {
  color: var(--text);
  text-decoration: none;
  font-weight: 500;
}

.nav-links a:hover {
  color: var(--primary);
}

.greeting {
  color: var(--text-muted);
  font-size: 0.9rem;
}

.home-link {
  color: var(--text) !important;
  text-decoration: none;
  font-weight: 600;
  font-size: 0.9rem;
}
.home-link:hover {
  color: var(--primary) !important;
}

.admin-link {
  background: #7c3aed;
  color: #fff !important;
  padding: 0.3rem 0.75rem;
  border-radius: 6px;
  font-size: 0.85rem;
  font-weight: 600;
  text-decoration: none;
}
.admin-link:hover {
  background: #6d28d9;
  color: #fff !important;
}

.settings-link {
  color: var(--text-muted) !important;
  text-decoration: none;
  font-size: 0.9rem;
  font-weight: 500;
}
.settings-link:hover {
  color: var(--primary) !important;
}
</style>
