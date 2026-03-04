<template>
  <div class="card product-card">
    <div class="product-header">
      <router-link :to="`/products/${product.id}`" class="product-name">
        {{ product.name }}
      </router-link>
      <div class="price-area">
        <span v-if="product.latest_price != null" class="price">
          {{ sym }}{{ Number(product.latest_price).toFixed(2) }}
        </span>
        <span v-else class="price muted">No price yet</span>
        <span
          v-if="product.price_change != null"
          class="change"
          :class="product.price_change < 0 ? 'down' : product.price_change > 0 ? 'up' : ''"
        >
          {{ product.price_change > 0 ? "▲" : product.price_change < 0 ? "▼" : "—" }}
          {{ Math.abs(product.price_change_pct) }}%
        </span>
      </div>
    </div>
    <p class="url">{{ product.url }}</p>
    <p v-if="product.description" class="desc">{{ product.description }}</p>
    <div class="product-footer">
      <div class="meta">
        <span class="currency-badge">{{ product.currency }}</span>
        <span v-if="product.target_price" class="target">
          Target: {{ sym }}{{ Number(product.target_price).toFixed(2) }}
        </span>
      </div>
      <div class="actions">
        <button class="btn-secondary" @click="$emit('edit', product)">
          Edit
        </button>
        <button class="btn-primary" @click="$emit('check', product.id)">
          Check Now
        </button>
        <button class="btn-danger" @click="$emit('delete', product.id)">
          Delete
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from "vue";
import { useCurrencyStore } from "../store/currency.js";

const props = defineProps({ product: { type: Object, required: true } });
defineEmits(["check", "delete", "edit"]);

const currencyStore = useCurrencyStore();
const sym = computed(() => currencyStore.getSymbol(props.product.currency));
</script>

<style scoped>
.product-card {
  transition: box-shadow 0.2s;
}
.product-card:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}
.product-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}
.product-name {
  font-weight: 600;
  font-size: 1.1rem;
  color: var(--primary);
  text-decoration: none;
}
.product-name:hover {
  text-decoration: underline;
}
.price-area {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.price {
  font-weight: 700;
  font-size: 1.1rem;
  color: #059669;
}
.price.muted {
  color: var(--text-muted);
  font-weight: 400;
  font-size: 0.9rem;
}
.change {
  font-size: 0.8rem;
  font-weight: 600;
  padding: 0.15rem 0.4rem;
  border-radius: 4px;
}
.change.down {
  color: #059669;
  background: #ecfdf5;
}
.change.up {
  color: #dc2626;
  background: #fef2f2;
}
.url {
  color: var(--text-muted);
  font-size: 0.8rem;
  word-break: break-all;
}
.desc {
  margin-top: 0.25rem;
  font-size: 0.9rem;
}
.product-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 0.75rem;
}
.meta {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}
.currency-badge {
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.15rem 0.5rem;
  border-radius: 4px;
  background: #eef2ff;
  color: var(--primary);
}
.target {
  font-size: 0.85rem;
  color: var(--text-muted);
}
.actions {
  display: flex;
  gap: 0.5rem;
}
</style>
