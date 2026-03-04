<template>
  <div class="auth-page">
    <div class="card auth-card verify-card">
      <div v-if="loading" class="center">
        <p>Verifying your email…</p>
      </div>
      <div v-else-if="success" class="center">
        <h2>Email Verified!</h2>
        <p class="success-text">Your email has been verified successfully.</p>
        <button class="btn-primary inline-btn" @click="goToLogin">Go to Login</button>
      </div>
      <div v-else class="center">
        <h2>Verification Failed</h2>
        <p class="error-text">{{ error }}</p>
        <button class="btn-secondary inline-btn" @click="goToLogin">Go to Login</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import api from "../api/index.js";
import { useAuthStore } from "../store/auth.js";

const auth = useAuthStore();
const router = useRouter();

function goToLogin() {
  // Log out first so the guest guard doesn't redirect to Dashboard
  if (auth.isLoggedIn) auth.logout();
  router.push("/login");
}

const route = useRoute();
const loading = ref(true);
const success = ref(false);
const error = ref("");

onMounted(async () => {
  const token = route.query.token;
  if (!token) {
    error.value = "No verification token provided.";
    loading.value = false;
    return;
  }
  try {
    await api.get(`/auth/verify?token=${token}`);
    success.value = true;
  } catch (err) {
    error.value =
      err.response?.data?.detail || "Invalid or expired verification link.";
  } finally {
    loading.value = false;
  }
});
</script>

<style scoped>
.auth-page {
  display: flex;
  justify-content: center;
  margin-top: 4rem;
}
.verify-card {
  width: 100%;
  max-width: 440px;
  text-align: center;
  padding: 2.5rem 2rem;
}
.verify-card h2 {
  margin-bottom: 0.75rem;
}
.center {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
}
.success-text {
  color: #059669;
}
.error-text {
  color: #dc2626;
}
.inline-btn {
  display: inline-block;
  margin-top: 0.5rem;
  padding: 0.5rem 1.5rem;
  border-radius: 6px;
  text-decoration: none;
  font-weight: 600;
}
</style>
