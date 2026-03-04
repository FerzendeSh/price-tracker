<template>
  <div class="settings-page">
    <h1>Account Settings</h1>

    <!-- Account info -->
    <div class="card section">
      <h2>Profile</h2>
      <div class="info-grid">
        <div class="info-row">
          <span class="label">Username</span>
          <span class="value">{{ authStore.user?.username }}</span>
        </div>
        <div class="info-row">
          <span class="label">Email</span>
          <span class="value">
            {{ authStore.user?.email }}
            <span v-if="authStore.user?.email_verified" class="badge-green">Verified</span>
            <span v-else class="badge-yellow">Not verified</span>
          </span>
        </div>
        <div class="info-row">
          <span class="label">Role</span>
          <span class="value">
            <span v-if="authStore.user?.is_admin" class="badge-purple">Admin</span>
            <span v-else class="badge-gray">User</span>
          </span>
        </div>
      </div>
    </div>

    <!-- Change Password -->
    <div class="card section">
      <h2>Change Password</h2>
      <form @submit.prevent="handleChangePassword" class="pw-form">
        <div class="field">
          <label>Current Password</label>
          <div class="password-row">
            <input
              v-model="pw.current"
              :type="showCurrent ? 'text' : 'password'"
              required
              autocomplete="current-password"
            />
            <button type="button" class="toggle-pw" @click="showCurrent = !showCurrent" tabindex="-1">
              {{ showCurrent ? '🙈' : '👁️' }}
            </button>
          </div>
        </div>

        <div class="field">
          <label>New Password</label>
          <div class="password-row">
            <input
              v-model="pw.newPw"
              :type="showNew ? 'text' : 'password'"
              required
              minlength="8"
              autocomplete="new-password"
            />
            <button type="button" class="toggle-pw" @click="showNew = !showNew" tabindex="-1">
              {{ showNew ? '🙈' : '👁️' }}
            </button>
            <button type="button" class="generate-btn" @click="generatePassword" tabindex="-1" title="Generate strong password">
              🔐 Generate
            </button>
          </div>

          <!-- Strength meter -->
          <div v-if="pw.newPw" class="strength-meter">
            <div class="strength-bar">
              <div class="strength-fill" :class="strengthClass" :style="{ width: strengthPercent + '%' }"></div>
            </div>
            <span class="strength-label" :class="strengthClass">{{ strengthLabel }}</span>
          </div>

          <!-- Requirements checklist -->
          <ul v-if="pw.newPw" class="pw-checklist">
            <li :class="{ met: checks.length }">At least 8 characters</li>
            <li :class="{ met: checks.upper }">Uppercase letter</li>
            <li :class="{ met: checks.lower }">Lowercase letter</li>
            <li :class="{ met: checks.number }">Number</li>
            <li :class="{ met: checks.special }">Special character (!@#$…)</li>
          </ul>
        </div>

        <div class="field">
          <label>Confirm New Password</label>
          <div class="password-row">
            <input
              v-model="pw.confirm"
              :type="showConfirm ? 'text' : 'password'"
              required
              minlength="8"
              autocomplete="new-password"
            />
            <button type="button" class="toggle-pw" @click="showConfirm = !showConfirm" tabindex="-1">
              {{ showConfirm ? '🙈' : '👁️' }}
            </button>
          </div>
          <p v-if="pw.confirm && pw.confirm !== pw.newPw" class="mismatch">Passwords do not match</p>
        </div>

        <div class="pw-actions">
          <button
            class="btn-primary"
            type="submit"
            :disabled="pwLoading || !canSubmit"
          >
            {{ pwLoading ? 'Saving…' : 'Change Password' }}
          </button>
        </div>
        <p v-if="pwError" class="error">{{ pwError }}</p>
        <p v-if="pwSuccess" class="success">{{ pwSuccess }}</p>
      </form>
    </div>

    <!-- Danger zone -->
    <div class="card section danger-section">
      <h2>Danger Zone</h2>
      <template v-if="authStore.user?.is_admin">
        <p class="admin-notice">
          🛡️ Admin accounts cannot be deleted. To delete this account,
          first demote yourself from the Admin panel.
        </p>
      </template>
      <template v-else>
        <p>
          Permanently delete your account and all associated data (products, price history, alerts).
          This action <strong>cannot be undone</strong>.
        </p>
        <button class="btn-danger" @click="handleDelete" :disabled="deleting">
          {{ deleting ? 'Deleting…' : 'Delete My Account' }}
        </button>
        <p v-if="error" class="error">{{ error }}</p>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "../store/auth.js";
import api from "../api/index.js";

const authStore = useAuthStore();
const router = useRouter();
const deleting = ref(false);
const error = ref("");

// ── Change Password ─────────────────────────────────────────
const pw = reactive({ current: "", newPw: "", confirm: "" });
const showCurrent = ref(false);
const showNew = ref(false);
const showConfirm = ref(false);
const pwLoading = ref(false);
const pwError = ref("");
const pwSuccess = ref("");

const checks = computed(() => ({
  length: pw.newPw.length >= 8,
  upper: /[A-Z]/.test(pw.newPw),
  lower: /[a-z]/.test(pw.newPw),
  number: /[0-9]/.test(pw.newPw),
  special: /[^A-Za-z0-9]/.test(pw.newPw),
}));

const strengthScore = computed(() => {
  const c = checks.value;
  let score = 0;
  if (c.length) score++;
  if (c.upper) score++;
  if (c.lower) score++;
  if (c.number) score++;
  if (c.special) score++;
  if (pw.newPw.length >= 12) score++;
  return score;
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

const canSubmit = computed(() => {
  return pw.current && pw.newPw && pw.confirm && pw.newPw === pw.confirm && checks.value.length;
});

function generatePassword() {
  const upper = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
  const lower = "abcdefghijklmnopqrstuvwxyz";
  const digits = "0123456789";
  const specials = "!@#$%^&*_+-=?";
  const all = upper + lower + digits + specials;
  let arr = [
    upper[Math.floor(Math.random() * upper.length)],
    lower[Math.floor(Math.random() * lower.length)],
    digits[Math.floor(Math.random() * digits.length)],
    specials[Math.floor(Math.random() * specials.length)],
  ];
  for (let i = arr.length; i < 16; i++) {
    arr.push(all[Math.floor(Math.random() * all.length)]);
  }
  for (let i = arr.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [arr[i], arr[j]] = [arr[j], arr[i]];
  }
  pw.newPw = arr.join("");
  showNew.value = true;
}

async function handleChangePassword() {
  pwError.value = "";
  pwSuccess.value = "";
  if (pw.newPw !== pw.confirm) {
    pwError.value = "Passwords do not match";
    return;
  }
  pwLoading.value = true;
  try {
    await api.put("/auth/change-password", {
      current_password: pw.current,
      new_password: pw.newPw,
    });
    pwSuccess.value = "Password changed successfully!";
    pw.current = "";
    pw.newPw = "";
    pw.confirm = "";
    showCurrent.value = false;
    showNew.value = false;
    showConfirm.value = false;
  } catch (e) {
    pwError.value = e.response?.data?.detail || "Failed to change password";
  } finally {
    pwLoading.value = false;
  }
}

async function handleDelete() {
  const confirmed = confirm(
    "Are you sure you want to permanently delete your account? All your products and price history will be lost.",
  );
  if (!confirmed) return;

  const doubleConfirm = confirm("This is irreversible. Really delete your account?");
  if (!doubleConfirm) return;

  deleting.value = true;
  error.value = "";
  try {
    await authStore.deleteAccount();
    router.push("/login");
  } catch (e) {
    error.value = e.response?.data?.detail || "Failed to delete account";
  } finally {
    deleting.value = false;
  }
}
</script>

<style scoped>
.settings-page h1 {
  margin-bottom: 1.5rem;
}

.section {
  padding: 1.5rem;
  margin-bottom: 1.5rem;
}
.section h2 {
  margin: 0 0 1rem;
  font-size: 1.1rem;
}

/* ---------- Profile info ---------- */
.info-grid {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}
.info-row {
  display: flex;
  gap: 1rem;
  align-items: center;
}
.info-row .label {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--text-muted);
  min-width: 90px;
}
.info-row .value {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

/* ---------- Badges ---------- */
.badge-green {
  background: #ecfdf5;
  color: #059669;
  padding: 0.15rem 0.5rem;
  border-radius: 4px;
  font-size: 0.78rem;
  font-weight: 500;
}
.badge-yellow {
  background: #fefce8;
  color: #ca8a04;
  padding: 0.15rem 0.5rem;
  border-radius: 4px;
  font-size: 0.78rem;
  font-weight: 500;
}
.badge-purple {
  background: #f3e8ff;
  color: #7c3aed;
  padding: 0.15rem 0.5rem;
  border-radius: 4px;
  font-size: 0.78rem;
  font-weight: 500;
}
.badge-gray {
  background: #f3f4f6;
  color: #6b7280;
  padding: 0.15rem 0.5rem;
  border-radius: 4px;
  font-size: 0.78rem;
  font-weight: 500;
}

/* ---------- Danger zone ---------- */
.danger-section {
  border: 1px solid #fca5a5;
  background: #fef2f2;
}
.danger-section h2 {
  color: #dc2626;
}
.danger-section p {
  font-size: 0.9rem;
  margin-bottom: 1rem;
  color: #7f1d1d;
}
.admin-notice {
  color: #92400e !important;
  background: #fef3c7;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  border: 1px solid #fde68a;
  font-size: 0.9rem;
}
.btn-danger {
  background: #dc2626;
  color: #fff;
  border: none;
  padding: 0.6rem 1.25rem;
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.9rem;
  cursor: pointer;
  transition: background 0.15s;
}
.btn-danger:hover:not(:disabled) {
  background: #b91c1c;
}
.btn-danger:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
.error {
  color: #dc2626;
  font-size: 0.85rem;
  margin-top: 0.5rem;
}
.success {
  color: #059669;
  font-size: 0.85rem;
  margin-top: 0.5rem;
}

/* ── Change Password form ───────────── */
.pw-form {
  max-width: 420px;
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
.mismatch {
  color: #dc2626;
  font-size: 0.78rem;
  margin-top: 0.25rem;
}
.pw-actions {
  margin-top: 0.25rem;
}
.btn-primary {
  background: var(--primary);
  color: #fff;
  border: none;
  padding: 0.6rem 1.25rem;
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.9rem;
  cursor: pointer;
  transition: background 0.15s;
}
.btn-primary:hover:not(:disabled) {
  background: #4338ca;
}
.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* ── Strength meter ─────────────────── */
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
.str-vweak  { background: #ef4444; color: #ef4444; }
.str-weak   { background: #f97316; color: #f97316; }
.str-fair   { background: #eab308; color: #eab308; }
.str-good   { background: #22c55e; color: #22c55e; }
.str-strong { background: #059669; color: #059669; }
.str-vstrong { background: #047857; color: #047857; }

/* ── Password checklist ─────────────── */
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
</style>
