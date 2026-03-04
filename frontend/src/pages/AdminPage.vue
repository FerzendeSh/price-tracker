<template>
  <div class="admin-page">
    <h1>Admin Dashboard</h1>

    <!-- System Stats -->
    <div v-if="stats" class="stats-row">
      <div class="stat card">
        <span class="stat-value">{{ stats.total_users }}</span>
        <span class="stat-label">Total Users</span>
      </div>
      <div class="stat card">
        <span class="stat-value">{{ stats.verified_users }}</span>
        <span class="stat-label">Verified</span>
      </div>
      <div class="stat card">
        <span class="stat-value">{{ stats.unverified_users }}</span>
        <span class="stat-label">Unverified</span>
      </div>
      <div class="stat card">
        <span class="stat-value">{{ stats.total_products }}</span>
        <span class="stat-label">Total Products</span>
      </div>
    </div>

    <!-- Users Table -->
    <div class="card table-card">
      <div class="table-header">
        <h2>Users</h2>
        <div class="table-actions">
          <button class="btn-small btn-refresh" @click="fetchData" :disabled="loading" title="Refresh">
            🔄 Refresh
          </button>
          <input
            v-model="search"
            type="text"
            placeholder="Search users…"
            class="search-input"
          />
        </div>
      </div>

      <div v-if="loading" class="loading">Loading…</div>
      <div v-else-if="error" class="error">{{ error }}</div>
      <div v-else class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>#</th>
              <th>Username</th>
              <th>Email</th>
              <th>Verified</th>
              <th>Admin</th>
              <th>Products</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(user, index) in filteredUsers" :key="user.id">
              <td>{{ index + 1 }}</td>
              <td>
                <strong>{{ user.username }}</strong>
                <span v-if="user.id === authStore.user?.id" class="you-badge">You</span>
              </td>
              <td>{{ user.email }}</td>
              <td>
                <span :class="user.email_verified ? 'badge-green' : 'badge-yellow'">
                  {{ user.email_verified ? 'Yes' : 'No' }}
                </span>
              </td>
              <td>
                <span :class="user.is_admin ? 'badge-purple' : 'badge-gray'">
                  {{ user.is_admin ? 'Admin' : 'User' }}
                </span>
              </td>
              <td>{{ user.product_count }}</td>
              <td class="actions">
                <!-- Toggle admin -->
                <button
                  v-if="user.id !== authStore.user?.id"
                  class="btn-small"
                  :class="user.is_admin ? 'btn-warn' : 'btn-primary'"
                  @click="toggleAdmin(user)"
                  :disabled="actionLoading === user.id"
                >
                  {{ user.is_admin ? 'Demote' : 'Promote' }}
                </button>

                <!-- Verify email -->
                <button
                  v-if="!user.email_verified"
                  class="btn-small btn-green"
                  @click="verifyUser(user)"
                  :disabled="actionLoading === user.id"
                >
                  Verify
                </button>

                <!-- Delete user -->
                <button
                  v-if="user.id !== authStore.user?.id"
                  class="btn-small btn-danger"
                  @click="deleteUser(user)"
                  :disabled="actionLoading === user.id"
                >
                  Delete
                </button>
              </td>
            </tr>
          </tbody>
        </table>
        <p v-if="filteredUsers.length === 0" class="empty">No matching users.</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from "vue";
import { useAuthStore } from "../store/auth.js";
import api from "../api/index.js";

const authStore = useAuthStore();

const users = ref([]);
const stats = ref(null);
const loading = ref(true);
const error = ref("");
const search = ref("");
const actionLoading = ref(null);
let pollTimer = null;

const filteredUsers = computed(() => {
  if (!search.value.trim()) return users.value;
  const q = search.value.toLowerCase();
  return users.value.filter(
    (u) =>
      u.username.toLowerCase().includes(q) ||
      u.email.toLowerCase().includes(q) ||
      String(u.id).includes(q),
  );
});

async function fetchData() {
  loading.value = true;
  error.value = "";
  try {
    const [usersRes, statsRes] = await Promise.all([
      api.get("/admin/users"),
      api.get("/admin/stats"),
    ]);
    users.value = usersRes.data;
    stats.value = statsRes.data;
  } catch (e) {
    error.value = e.response?.data?.detail || "Failed to load admin data";
  } finally {
    loading.value = false;
  }
}

async function toggleAdmin(user) {
  actionLoading.value = user.id;
  try {
    await api.patch(`/admin/users/${user.id}/toggle-admin`);
    await fetchData();
  } catch (e) {
    alert(e.response?.data?.detail || "Failed to toggle admin");
  } finally {
    actionLoading.value = null;
  }
}

async function verifyUser(user) {
  actionLoading.value = user.id;
  try {
    await api.patch(`/admin/users/${user.id}/verify`);
    await fetchData();
  } catch (e) {
    alert(e.response?.data?.detail || "Failed to verify user");
  } finally {
    actionLoading.value = null;
  }
}

async function deleteUser(user) {
  if (!confirm(`Delete user "${user.username}" and all their data? This cannot be undone.`)) return;
  actionLoading.value = user.id;
  try {
    await api.delete(`/admin/users/${user.id}`);
    await fetchData();
  } catch (e) {
    alert(e.response?.data?.detail || "Failed to delete user");
  } finally {
    actionLoading.value = null;
  }
}

onMounted(() => {
  fetchData();
  // Poll every 15 seconds to keep dashboard in sync with DB
  pollTimer = setInterval(fetchData, 15000);
});

onUnmounted(() => {
  if (pollTimer) clearInterval(pollTimer);
});
</script>

<style scoped>
.admin-page h1 {
  margin-bottom: 1.5rem;
}

/* ---------- Stats ---------- */
.stats-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
}
.stat {
  text-align: center;
  padding: 1rem;
}
.stat-value {
  display: block;
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--primary);
}
.stat-label {
  font-size: 0.85rem;
  color: var(--text-muted);
}

/* ---------- Table ---------- */
.table-card {
  padding: 1.25rem;
}
.table-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1rem;
  flex-wrap: wrap;
  gap: 0.75rem;
}
.table-header h2 {
  margin: 0;
  font-size: 1.15rem;
}
.table-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.btn-refresh {
  background: #f3f4f6;
  color: #374151;
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 0.4rem 0.65rem;
  font-size: 0.82rem;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.15s;
}
.btn-refresh:hover:not(:disabled) {
  background: #e5e7eb;
}
.search-input {
  padding: 0.45rem 0.75rem;
  border: 1px solid var(--border);
  border-radius: 6px;
  font-size: 0.9rem;
  min-width: 200px;
}
.table-wrap {
  overflow-x: auto;
}
table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
}
th, td {
  text-align: left;
  padding: 0.6rem 0.75rem;
  border-bottom: 1px solid var(--border);
  white-space: nowrap;
}
th {
  font-weight: 600;
  color: var(--text-muted);
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.02em;
}
tbody tr:hover {
  background: rgba(79, 70, 229, 0.04);
}

/* ---------- Badges ---------- */
.badge-green {
  background: #ecfdf5;
  color: #059669;
  padding: 0.15rem 0.5rem;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: 500;
}
.badge-yellow {
  background: #fefce8;
  color: #ca8a04;
  padding: 0.15rem 0.5rem;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: 500;
}
.badge-purple {
  background: #f3e8ff;
  color: #7c3aed;
  padding: 0.15rem 0.5rem;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: 500;
}
.badge-gray {
  background: #f3f4f6;
  color: #6b7280;
  padding: 0.15rem 0.5rem;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: 500;
}
.you-badge {
  background: #dbeafe;
  color: #2563eb;
  padding: 0.1rem 0.4rem;
  border-radius: 3px;
  font-size: 0.7rem;
  font-weight: 600;
  margin-left: 0.35rem;
}

/* ---------- Action buttons ---------- */
.actions {
  display: flex;
  gap: 0.35rem;
}
.btn-small {
  padding: 0.3rem 0.6rem;
  font-size: 0.78rem;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-weight: 500;
  transition: opacity 0.15s;
}
.btn-small:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
.btn-small.btn-primary {
  background: var(--primary);
  color: #fff;
}
.btn-small.btn-warn {
  background: #f59e0b;
  color: #fff;
}
.btn-small.btn-green {
  background: #059669;
  color: #fff;
}
.btn-small.btn-danger {
  background: #dc2626;
  color: #fff;
}
.btn-small:hover:not(:disabled) {
  opacity: 0.85;
}

.loading, .empty {
  text-align: center;
  padding: 2rem;
  color: var(--text-muted);
}
.error {
  color: #dc2626;
  padding: 1rem;
}
</style>
