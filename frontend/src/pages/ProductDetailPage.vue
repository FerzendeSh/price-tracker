<template>
  <div v-if="store.loading" class="loading">Loading…</div>
  <div v-else-if="!product" class="empty">Product not found.</div>
  <div v-else>
    <router-link to="/" class="back">&larr; Back to Dashboard</router-link>

    <div class="card product-detail">
      <div class="header">
        <div>
          <h1>{{ product.name }}</h1>
          <a :href="product.url" target="_blank" class="url">{{ product.url }}</a>
          <p v-if="product.description" class="desc">{{ product.description }}</p>
        </div>
        <div class="price-box">
          <div v-if="product.latest_price != null" class="current-price">
            {{ sym }}{{ Number(product.latest_price).toFixed(2) }}
          </div>
          <div v-else class="no-price">No price data</div>
          <span
            v-if="product.price_change != null"
            class="change-badge"
            :class="product.price_change < 0 ? 'down' : product.price_change > 0 ? 'up' : ''"
          >
            {{ product.price_change > 0 ? "▲" : product.price_change < 0 ? "▼" : "—" }}
            {{ Math.abs(product.price_change_pct) }}%
          </span>
          <div class="detail-meta">
            <span class="currency-badge">{{ product.currency }}</span>
            <span v-if="product.target_price" class="target">
              Target: {{ sym }}{{ Number(product.target_price).toFixed(2) }}
            </span>
          </div>
        </div>
      </div>

      <div class="actions">
        <button class="btn-secondary" @click="showEdit = true">Edit</button>
        <button class="btn-primary" @click="checkNow" :disabled="checking">
          {{ checking ? "Checking…" : "Check Price Now" }}
        </button>
        <button class="btn-danger" @click="handleDelete">Delete Product</button>
      </div>
    </div>

    <div class="card">
      <h2>Price History</h2>
      <PriceChart
        :history="store.priceHistory"
        :product-name="product.name"
        :currency="product.currency"
      />
    </div>

    <div class="card" v-if="store.priceHistory.length">
      <h3>History Table</h3>
      <table class="history-table">
        <thead>
          <tr>
            <th>Date</th>
            <th>Price</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="entry in store.priceHistory" :key="entry.id">
            <td>{{ formatDate(entry.timestamp) }}</td>
            <td>{{ sym }}{{ Number(entry.price).toFixed(2) }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <EditProductModal
      :visible="showEdit"
      :product="product"
      @close="showEdit = false"
      @saved="onSaved"
    />
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useProductStore } from "../store/products.js";
import { useCurrencyStore } from "../store/currency.js";
import PriceChart from "../components/PriceChart.vue";
import EditProductModal from "../components/EditProductModal.vue";

const route = useRoute();
const router = useRouter();
const store = useProductStore();
const currencyStore = useCurrencyStore();
const checking = ref(false);
const showEdit = ref(false);

const product = computed(() => store.currentProduct);
const sym = computed(() => currencyStore.getSymbol(product.value?.currency));

onMounted(async () => {
  const id = Number(route.params.id);
  await Promise.all([
    store.fetchProduct(id),
    store.fetchPriceHistory(id),
    currencyStore.fetchCurrencies(),
  ]);
});

async function checkNow() {
  checking.value = true;
  try {
    await store.checkPriceNow(product.value.id);
    await store.fetchProduct(product.value.id);
    await store.fetchPriceHistory(product.value.id);
  } catch (err) {
    alert(err.response?.data?.detail || "Could not check price");
  } finally {
    checking.value = false;
  }
}

async function onSaved() {
  await store.fetchProduct(product.value.id);
}

async function handleDelete() {
  if (!confirm("Delete this product and all its price history?")) return;
  await store.deleteProduct(product.value.id);
  router.push("/");
}

function formatDate(ts) {
  return new Date(ts).toLocaleString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}
</script>

<style scoped>
.back {
  display: inline-block;
  margin-bottom: 1rem;
  color: var(--primary);
  text-decoration: none;
  font-weight: 500;
}
.back:hover {
  text-decoration: underline;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 2rem;
}

h1 {
  font-size: 1.5rem;
  margin-bottom: 0.25rem;
}

.url {
  color: var(--text-muted);
  font-size: 0.8rem;
  word-break: break-all;
}

.desc {
  margin-top: 0.5rem;
  color: var(--text-muted);
}

.price-box {
  text-align: right;
  flex-shrink: 0;
}

.current-price {
  font-size: 2rem;
  font-weight: 700;
  color: #059669;
}

.change-badge {
  display: inline-block;
  font-size: 0.85rem;
  font-weight: 600;
  padding: 0.15rem 0.5rem;
  border-radius: 4px;
  margin-top: 0.25rem;
}
.change-badge.down {
  color: #059669;
  background: #ecfdf5;
}
.change-badge.up {
  color: #dc2626;
  background: #fef2f2;
}

.detail-meta {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 0.5rem;
}

.currency-badge {
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.15rem 0.5rem;
  border-radius: 4px;
  background: #eef2ff;
  color: var(--primary);
}

.no-price {
  color: var(--text-muted);
}

.target {
  font-size: 0.85rem;
  color: var(--text-muted);
}

.actions {
  display: flex;
  gap: 0.75rem;
  margin-top: 1rem;
}

h2,
h3 {
  margin-bottom: 0.75rem;
}

.history-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
}

.history-table th,
.history-table td {
  text-align: left;
  padding: 0.5rem 0.75rem;
  border-bottom: 1px solid var(--border);
}

.history-table th {
  font-weight: 600;
  color: var(--text-muted);
}

.loading,
.empty {
  text-align: center;
  padding: 3rem;
  color: var(--text-muted);
}
</style>
