<template>
  <div class="auth-page">
    <div class="card auth-card">
      <h2>Register</h2>
      <form @submit.prevent="handleRegister">
        <div class="field">
          <label>Username</label>
          <input v-model="form.username" required minlength="3" maxlength="30" />
        </div>
        <div class="field">
          <label>Email</label>
          <input v-model="form.email" type="email" required />
        </div>
        <div class="field">
          <label>Password</label>
          <div class="password-row">
            <input
              v-model="form.password"
              :type="showPassword ? 'text' : 'password'"
              required
              minlength="8"
            />
            <button type="button" class="toggle-pw" @click="showPassword = !showPassword" tabindex="-1">
              {{ showPassword ? '🙈' : '👁️' }}
            </button>
            <button type="button" class="generate-btn" @click="generatePassword" tabindex="-1" title="Generate strong password">
              🔐 Generate
            </button>
          </div>

          <!-- Strength meter -->
          <div v-if="form.password" class="strength-meter">
            <div class="strength-bar">
              <div class="strength-fill" :class="strengthClass" :style="{ width: strengthPercent + '%' }"></div>
            </div>
            <span class="strength-label" :class="strengthClass">{{ strengthLabel }}</span>
          </div>

          <!-- Requirements checklist -->
          <ul v-if="form.password" class="pw-checklist">
            <li :class="{ met: checks.length }">At least 8 characters</li>
            <li :class="{ met: checks.upper }">Uppercase letter</li>
            <li :class="{ met: checks.lower }">Lowercase letter</li>
            <li :class="{ met: checks.number }">Number</li>
            <li :class="{ met: checks.special }">Special character (!@#$…)</li>
          </ul>
        </div>
        <p v-if="error" class="error">{{ error }}</p>
        <button class="btn-primary full" type="submit" :disabled="loading">
          {{ loading ? "Creating…" : "Register" }}
        </button>
      </form>
      <p class="switch">
        Already have an account?
        <router-link to="/login">Login</router-link>
      </p>
    </div>

    <!-- Success Popup Modal -->
    <Teleport to="body">
      <div v-if="showSuccessModal" class="modal-overlay" @click.self="closeModal">
        <div class="modal-box">
          <div class="modal-icon">✉️</div>
          <h3>Account Created!</h3>
          <p>
            A verification email has been sent to <strong>{{ registeredEmail }}</strong>.
            Please check your inbox (and spam folder) and click the link to verify your account.
          </p>
          <button class="btn-primary full" @click="closeModal">Go to Login</button>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { reactive, ref, computed } from "vue";
import { useAuthStore } from "../store/auth.js";
import { useRouter } from "vue-router";

const auth = useAuthStore();
const router = useRouter();
const loading = ref(false);
const error = ref("");
const showPassword = ref(false);
const showSuccessModal = ref(false);
const registeredEmail = ref("");
const form = reactive({ username: "", email: "", password: "" });

// ── Password generator ──────────────────────────────────────
function generatePassword() {
  const upper = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
  const lower = "abcdefghijklmnopqrstuvwxyz";
  const digits = "0123456789";
  const specials = "!@#$%^&*_+-=?";
  const all = upper + lower + digits + specials;

  // Guarantee at least one of each type
  let pw = [
    upper[Math.floor(Math.random() * upper.length)],
    lower[Math.floor(Math.random() * lower.length)],
    digits[Math.floor(Math.random() * digits.length)],
    specials[Math.floor(Math.random() * specials.length)],
  ];

  // Fill to 16 chars
  for (let i = pw.length; i < 16; i++) {
    pw.push(all[Math.floor(Math.random() * all.length)]);
  }

  // Shuffle
  for (let i = pw.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [pw[i], pw[j]] = [pw[j], pw[i]];
  }

  form.password = pw.join("");
  showPassword.value = true; // show so user can see the generated password
}

// ── Strength checks ─────────────────────────────────────────
const checks = computed(() => ({
  length: form.password.length >= 8,
  upper: /[A-Z]/.test(form.password),
  lower: /[a-z]/.test(form.password),
  number: /[0-9]/.test(form.password),
  special: /[^A-Za-z0-9]/.test(form.password),
}));

const strengthScore = computed(() => {
  const c = checks.value;
  let score = 0;
  if (c.length) score++;
  if (c.upper) score++;
  if (c.lower) score++;
  if (c.number) score++;
  if (c.special) score++;
  // Bonus for length > 12
  if (form.password.length >= 12) score++;
  return score; // 0–6
});

const strengthPercent = computed(() => Math.min((strengthScore.value / 6) * 100, 100));

const strengthLabel = computed(() => {
  const s = strengthScore.value;
  if (s <= 1) return "Very weak";
  if (s === 2) return "Weak";
  if (s === 3) return "Fair";
  if (s === 4) return "Good";
  if (s === 5) return "Strong";
  return "Very strong";
});

const strengthClass = computed(() => {
  const s = strengthScore.value;
  if (s <= 1) return "str-vweak";
  if (s === 2) return "str-weak";
  if (s === 3) return "str-fair";
  if (s === 4) return "str-good";
  if (s === 5) return "str-strong";
  return "str-vstrong";
});

// ── Registration ────────────────────────────────────────────
async function handleRegister() {
  error.value = "";
  loading.value = true;
  try {
    registeredEmail.value = form.email;
    await auth.register(form.username, form.email, form.password);

    // Clear the form
    form.username = "";
    form.email = "";
    form.password = "";
    showPassword.value = false;

    // Show success popup
    showSuccessModal.value = true;
  } catch (err) {
    error.value = err.response?.data?.detail || "Registration failed";
  } finally {
    loading.value = false;
  }
}

function closeModal() {
  showSuccessModal.value = false;
  router.push("/login");
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
.success {
  color: #059669;
  font-size: 0.85rem;
  margin-top: 0.25rem;
}

/* ── Password row ───────────────────────── */
.password-row {
  display: flex;
  gap: 0.35rem;
}
.password-row input {
  flex: 1;
  min-width: 0;
}
.toggle-pw {
  background: none;
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 0 0.5rem;
  cursor: pointer;
  font-size: 1rem;
}
.generate-btn {
  background: var(--primary);
  color: #fff;
  border: none;
  border-radius: 6px;
  padding: 0.4rem 0.65rem;
  font-size: 0.78rem;
  font-weight: 600;
  cursor: pointer;
  white-space: nowrap;
  transition: background 0.15s;
}
.generate-btn:hover {
  background: #4338ca;
}

/* ── Strength meter ─────────────────────── */
.strength-meter {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 0.4rem;
}
.strength-bar {
  flex: 1;
  height: 6px;
  background: #e5e7eb;
  border-radius: 3px;
  overflow: hidden;
}
.strength-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.25s, background 0.25s;
}
.strength-label {
  font-size: 0.75rem;
  font-weight: 600;
  white-space: nowrap;
}

/* Strength colors */
.str-vweak  { background: #ef4444; color: #ef4444; }
.str-weak   { background: #f97316; color: #f97316; }
.str-fair   { background: #eab308; color: #eab308; }
.str-good   { background: #22c55e; color: #22c55e; }
.str-strong { background: #059669; color: #059669; }
.str-vstrong { background: #047857; color: #047857; }

/* ── Password checklist ─────────────────── */
.pw-checklist {
  list-style: none;
  padding: 0;
  margin: 0.4rem 0 0;
  display: flex;
  flex-wrap: wrap;
  gap: 0.15rem 0.75rem;
}
.pw-checklist li {
  font-size: 0.72rem;
  color: #9ca3af;
  transition: color 0.15s;
}
.pw-checklist li::before {
  content: "✕ ";
  color: #d1d5db;
}
.pw-checklist li.met {
  color: #059669;
}
.pw-checklist li.met::before {
  content: "✓ ";
  color: #059669;
}

/* ── Success Modal ──────────────────────── */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.2s ease;
}
.modal-box {
  background: #fff;
  border-radius: 12px;
  padding: 2rem 2.5rem;
  max-width: 420px;
  width: 90%;
  text-align: center;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
  animation: slideUp 0.3s ease;
}
.modal-icon {
  font-size: 3rem;
  margin-bottom: 0.75rem;
}
.modal-box h3 {
  font-size: 1.35rem;
  margin: 0 0 0.75rem;
  color: #059669;
}
.modal-box p {
  font-size: 0.92rem;
  color: #4b5563;
  line-height: 1.5;
  margin-bottom: 1.5rem;
}
.modal-box p strong {
  color: #1f2937;
}
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
@keyframes slideUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
