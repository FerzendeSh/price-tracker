<template>
  <form class="card add-form" @submit.prevent="submit">
    <h3>Add Product to Track</h3>
    <div class="form-grid">
      <div class="field">
        <label>Name</label>
        <input v-model="form.name" required placeholder="e.g. MacBook Pro" />
      </div>
      <div class="field">
        <label>URL</label>
        <input v-model="form.url" required type="url" placeholder="https://..." />
      </div>
      <div class="field">
        <label>Target Price (optional)</label>
        <input
          v-model.number="form.target_price"
          type="number"
          step="0.01"
          min="0"
          placeholder="Alert when price drops to this"
        />
      </div>
      <div class="field">
        <label>Description (optional)</label>
        <input v-model="form.description" placeholder="Short note" />
      </div>
    </div>
    <p class="hint">Currency is automatically detected from the product page.</p>
    <p v-if="error" class="error">{{ error }}</p>
    <button class="btn-primary" type="submit" :disabled="loading">
      {{ loading ? "Adding…" : "Add Product" }}
    </button>
  </form>
</template>

<script setup>
import { reactive, ref } from "vue";
import { useProductStore } from "../store/products.js";

const store = useProductStore();
const loading = ref(false);
const error = ref("");

const form = reactive({
  name: "",
  url: "",
  target_price: null,
  description: "",
});

async function submit() {
  error.value = "";
  loading.value = true;
  try {
    const payload = { name: form.name, url: form.url };
    if (form.target_price) payload.target_price = form.target_price;
    if (form.description) payload.description = form.description;
    await store.createProduct(payload);
    form.name = "";
    form.url = "";
    form.target_price = null;
    form.description = "";
  } catch (err) {
    error.value = err.response?.data?.detail || "Failed to add product";
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
.add-form h3 {
  margin-bottom: 1rem;
}
.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
  margin-bottom: 0.75rem;
}
.field label {
  display: block;
  font-size: 0.85rem;
  font-weight: 500;
  margin-bottom: 0.25rem;
  color: var(--text-muted);
}
.hint {
  font-size: 0.8rem;
  color: var(--text-muted);
  margin-bottom: 0.75rem;
}
@media (max-width: 600px) {
  .form-grid {
    grid-template-columns: 1fr;
  }
}
</style>
