<template>
  <div>
    <h1>Dashboard</h1>

    <!-- Email verification banner -->
    <div v-if="authStore.user && !authStore.user.email_verified" class="verify-banner card">
      <p>
        📧 Please verify your email (<strong>{{ authStore.user.email }}</strong>)
        to receive price drop alerts.
      </p>
      <button class="btn-secondary" @click="resendVerification" :disabled="resending">
        {{ resending ? 'Sending…' : 'Resend Verification Email' }}
      </button>
      <span v-if="resendMsg" class="resend-msg">{{ resendMsg }}</span>
    </div>

    <!-- Stats row -->
    <div v-if="store.products.length" class="stats-row">
      <div class="stat card">
        <span class="stat-value">{{ store.products.length }}</span>
        <span class="stat-label">Products</span>
      </div>
      <div class="stat card">
        <span class="stat-value">{{ priceDropCount }}</span>
        <span class="stat-label">Price Drops</span>
      </div>
      <div class="stat card">
        <span class="stat-value">{{ belowTargetCount }}</span>
        <span class="stat-label">Below Target</span>
      </div>
      <div class="stat card">
        <span class="stat-value">{{ noPriceCount }}</span>
        <span class="stat-label">No Data</span>
      </div>
    </div>

    <AddProductForm />

    <!-- Sort / Filter bar -->
    <div v-if="store.products.length" class="toolbar">
      <input
        v-model="search"
        type="text"
        placeholder="Search products…"
        class="search-input"
      />
      <select v-model="sortKey" class="sort-select">
        <option value="name">Sort: Name</option>
        <option value="price-asc">Sort: Price ↑</option>
        <option value="price-desc">Sort: Price ↓</option>
        <option value="newest">Sort: Newest</option>
        <option value="oldest">Sort: Oldest</option>
      </select>
    </div>

    <div v-if="store.loading" class="loading">Loading…</div>
    <p v-else-if="store.error" class="error">{{ store.error }}</p>
    <div v-else-if="store.products.length === 0" class="empty">
      <p>You haven't added any products yet. Add one above!</p>
    </div>
    <div v-else>
      <p v-if="sortedProducts.length === 0" class="empty">No matching products.</p>
      <ProductCard
        v-for="product in sortedProducts"
        :key="product.id"
        :product="product"
        @check="checkPrice"
        @delete="deleteProduct"
        @edit="openEdit"
      />
    </div>

    <EditProductModal
      :visible="showEdit"
      :product="editTarget"
      @close="showEdit = false"
      @saved="onSaved"
    />
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import { useProductStore } from "../store/products.js";
import { useCurrencyStore } from "../store/currency.js";
import { useAuthStore } from "../store/auth.js";
import AddProductForm from "../components/AddProductForm.vue";
import ProductCard from "../components/ProductCard.vue";
import EditProductModal from "../components/EditProductModal.vue";
import api from "../api/index.js";

const store = useProductStore();
const currencyStore = useCurrencyStore();
const authStore = useAuthStore();

const checking = ref(null);
const showEdit = ref(false);
const editTarget = ref(null);
const search = ref("");
const sortKey = ref("newest");
const resending = ref(false);
const resendMsg = ref("");

onMounted(() => {
  store.fetchProducts();
  currencyStore.fetchCurrencies();
  if (!authStore.user) authStore.fetchUser();
});

async function resendVerification() {
  resending.value = true;
  resendMsg.value = "";
  try {
    await api.post("/auth/resend-verification");
    resendMsg.value = "Sent! Check your inbox.";
  } catch {
    resendMsg.value = "Failed to send. Try again later.";
  } finally {
    resending.value = false;
  }
}

/* ---------- Computed stats ---------- */
const priceDropCount = computed(
  () => store.products.filter((p) => p.price_change != null && p.price_change < 0).length,
);
const belowTargetCount = computed(
  () =>
    store.products.filter(
      (p) =>
        p.target_price != null &&
        p.latest_price != null &&
        Number(p.latest_price) <= Number(p.target_price),
    ).length,
);
const noPriceCount = computed(
  () => store.products.filter((p) => p.latest_price == null).length,
);

/* ---------- Sort & filter ---------- */
const sortedProducts = computed(() => {
  let list = [...store.products];

  // Filter by search
  if (search.value.trim()) {
    const q = search.value.toLowerCase();
    list = list.filter(
      (p) =>
        p.name.toLowerCase().includes(q) ||
        p.url.toLowerCase().includes(q) ||
        (p.description || "").toLowerCase().includes(q),
    );
  }

  // Sort
  switch (sortKey.value) {
    case "name":
      list.sort((a, b) => a.name.localeCompare(b.name));
      break;
    case "price-asc":
      list.sort((a, b) => (a.latest_price ?? Infinity) - (b.latest_price ?? Infinity));
      break;
    case "price-desc":
      list.sort((a, b) => (b.latest_price ?? -Infinity) - (a.latest_price ?? -Infinity));
      break;
    case "newest":
      list.sort((a, b) => b.id - a.id);
      break;
    case "oldest":
      list.sort((a, b) => a.id - b.id);
      break;
  }

  return list;
});

/* ---------- Actions ---------- */
function openEdit(product) {
  editTarget.value = product;
  showEdit.value = true;
}

async function onSaved() {
  await store.fetchProducts();
}

async function checkPrice(productId) {
  checking.value = productId;
  try {
    await store.checkPriceNow(productId);
    await store.fetchProducts();
  } catch (err) {
    alert(err.response?.data?.detail || "Could not check price");
  } finally {
    checking.value = null;
  }
}

async function deleteProduct(productId) {
  if (!confirm("Delete this product and all its price history?")) return;
  try {
    await store.deleteProduct(productId);
  } catch (err) {
    alert(err.response?.data?.detail || "Delete failed");
  }
}
</script>

<style scoped>
h1 {
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

/* ---------- Toolbar ---------- */
.toolbar {
  display: flex;
  gap: 0.75rem;
  margin-bottom: 1rem;
}
.search-input {
  flex: 1;
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--border);
  border-radius: 6px;
  font-size: 0.95rem;
}
.sort-select {
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--border);
  border-radius: 6px;
  font-size: 0.95rem;
  background: #fff;
}

.loading,
.empty {
  text-align: center;
  padding: 3rem;
  color: var(--text-muted);
}

/* ---------- Verify banner ---------- */
.verify-banner {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
  background: #fefce8;
  border: 1px solid #fde68a;
  margin-bottom: 1.5rem;
  padding: 1rem 1.25rem;
}
.verify-banner p {
  flex: 1;
  margin: 0;
  font-size: 0.9rem;
}
.resend-msg {
  font-size: 0.8rem;
  color: #059669;
}
</style>
