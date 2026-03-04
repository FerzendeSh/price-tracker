<template>
  <teleport to="body">
    <div v-if="visible" class="modal-overlay" @click.self="$emit('close')">
      <div class="modal-content card">
        <h3>Edit Product</h3>
        <form @submit.prevent="save" class="edit-form">
          <div class="field">
            <label>Name</label>
            <input v-model="form.name" required />
          </div>

          <div class="field">
            <label>URL</label>
            <input v-model="form.url" type="url" required />
          </div>

          <div class="field">
            <label>Description</label>
            <textarea v-model="form.description" rows="2"></textarea>
          </div>

          <div class="field">
            <label>Target Price</label>
            <input
              v-model.number="form.target_price"
              type="number"
              step="0.01"
              min="0"
              placeholder="Alert when price drops to this"
            />
          </div>

          <p v-if="error" class="error">{{ error }}</p>

          <div class="modal-actions">
            <button type="button" class="btn-secondary" @click="$emit('close')">
              Cancel
            </button>
            <button type="submit" class="btn-primary" :disabled="saving">
              {{ saving ? "Saving…" : "Save Changes" }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </teleport>
</template>

<script setup>
import { reactive, ref, watch } from "vue";
import { useProductStore } from "../store/products.js";

const props = defineProps({
  visible: { type: Boolean, default: false },
  product: { type: Object, default: null },
});
const emit = defineEmits(["close", "saved"]);

const productStore = useProductStore();

const form = reactive({
  name: "",
  url: "",
  description: "",
  target_price: null,
});

const saving = ref(false);
const error = ref("");

// Sync form with product whenever modal opens or product changes
watch(
  () => props.product,
  (p) => {
    if (p) {
      form.name = p.name || "";
      form.url = p.url || "";
      form.description = p.description || "";
      form.target_price = p.target_price ?? null;
    }
  },
  { immediate: true },
);

async function save() {
  saving.value = true;
  error.value = "";
  try {
    const payload = {
      name: form.name,
      url: form.url,
      description: form.description || null,
      target_price: form.target_price || null,
    };
    await productStore.updateProduct(props.product.id, payload);
    emit("saved");
    emit("close");
  } catch (e) {
    error.value = e.response?.data?.detail || "Failed to save changes";
  } finally {
    saving.value = false;
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 999;
}
.modal-content {
  width: 95%;
  max-width: 520px;
  max-height: 90vh;
  overflow-y: auto;
  animation: fadeIn 0.15s ease;
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}
.modal-content h3 {
  margin-bottom: 1rem;
}
.edit-form {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}
.field {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}
.field label {
  font-size: 0.85rem;
  font-weight: 500;
}
.field input,
.field textarea,
.field select {
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--border);
  border-radius: 6px;
  font-size: 0.95rem;
}
.error {
  color: #dc2626;
  font-size: 0.85rem;
}
.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  margin-top: 0.5rem;
}
</style>
