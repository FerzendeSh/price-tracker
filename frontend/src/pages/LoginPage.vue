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

const MAX_RETRIES = 3;
const RETRY_DELAY_MS = 5000;

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function handleLogin() {
  error.value = "";
  loading.value = true;

  for (let attempt = 1; attempt <= MAX_RETRIES; attempt++) {
    try {
      await auth.login(form.username, form.password);
      router.push("/");
      return; // success — exit
    } catch (err) {
      const status = err.response?.status;

      // 502/503/504 = backend cold-starting — retry automatically
      if (status && status >= 502 && status <= 504 && attempt < MAX_RETRIES) {
        error.value = `Server is waking up… retrying (${attempt}/${MAX_RETRIES})`;
        await sleep(RETRY_DELAY_MS);
        continue;
      }

      // Final attempt or non-retryable error — show message
      if (err.response) {
        const detail = err.response.data?.detail;
        if (typeof detail === "string") {
          error.value = detail;
        } else if (Array.isArray(detail)) {
          error.value = detail.map((e) => e.msg).join("; ") || "Validation error";
        } else if (status >= 502 && status <= 504) {
          error.value = "Server is still starting up. Please wait a minute and try again.";
        } else {
          error.value = `Login failed (${status})`;
        }
      } else if (err.request) {
        error.value = "Cannot reach server — it may be starting up. Please wait 30 seconds and try again.";
      } else {
        error.value = "Login failed";
      }
    }
  }

  loading.value = false;
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
