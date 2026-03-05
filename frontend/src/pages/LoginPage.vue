<template>
  <div class="auth-page">
    <div class="card auth-card">
      <h2>Login</h2>
      <form @submit.prevent="handleLogin">
        <div class="field">
          <label>Username</label>
          <input v-model="form.username" required />
        </div>
        <div class="field">
          <label>Password</label>
          <input v-model="form.password" type="password" required minlength="8" />
        </div>
        <p v-if="error" class="error">{{ error }}</p>
        <button class="btn-primary full" type="submit" :disabled="loading">
          {{ loading ? "Logging in…" : "Login" }}
        </button>
      </form>
      <p class="switch">
        Don't have an account?
        <router-link to="/register">Register</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from "vue";
import { useAuthStore } from "../store/auth.js";
import { useRouter } from "vue-router";

const auth = useAuthStore();
const router = useRouter();
const loading = ref(false);
const error = ref("");
const form = reactive({ username: "", password: "" });

async function handleLogin() {
  error.value = "";
  loading.value = true;
  try {
    await auth.login(form.username, form.password);
    router.push("/");
  } catch (err) {
    if (err.response) {
      // Server responded with an error
      const detail = err.response.data?.detail;
      error.value = typeof detail === "string" ? detail : "Login failed — invalid request";
    } else if (err.request) {
      // Request sent but no response (backend unreachable / cold-starting)
      error.value = "Cannot reach server — it may be starting up. Please wait 30 seconds and try again.";
    } else {
      error.value = "Login failed";
    }
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
.auth-page {
  display: flex;
  justify-content: center;
  margin-top: 4rem;
}
.auth-card {
  width: 100%;
  max-width: 400px;
}
.auth-card h2 {
  margin-bottom: 1.5rem;
}
.field {
  margin-bottom: 1rem;
}
.field label {
  display: block;
  font-size: 0.85rem;
  font-weight: 500;
  margin-bottom: 0.25rem;
  color: var(--text-muted);
}
.full {
  width: 100%;
  padding: 0.6rem;
}
.switch {
  text-align: center;
  margin-top: 1rem;
  font-size: 0.9rem;
  color: var(--text-muted);
}
.switch a {
  color: var(--primary);
  text-decoration: none;
  font-weight: 500;
}
</style>
