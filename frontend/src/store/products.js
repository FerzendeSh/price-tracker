import { defineStore } from "pinia";
import api from "../api/index.js";

export const useProductStore = defineStore("products", {
  state: () => ({
    products: [],
    currentProduct: null,
    priceHistory: [],
    loading: false,
    error: null,
  }),

  actions: {
    async fetchProducts() {
      this.loading = true;
      this.error = null;
      try {
        const { data } = await api.get("/products/");
        this.products = data;
      } catch (err) {
        this.error = err.response?.data?.detail || "Failed to fetch products";
      } finally {
        this.loading = false;
      }
    },

    async fetchProduct(id) {
      this.loading = true;
      try {
        const { data } = await api.get(`/products/${id}`);
        this.currentProduct = data;
      } catch (err) {
        this.error = err.response?.data?.detail || "Product not found";
      } finally {
        this.loading = false;
      }
    },

    async createProduct(payload) {
      const { data } = await api.post("/products/", payload);
      this.products.unshift(data);
      return data;
    },

    async updateProduct(id, payload) {
      const { data } = await api.put(`/products/${id}`, payload);
      const idx = this.products.findIndex((p) => p.id === id);
      if (idx !== -1) this.products[idx] = data;
      this.currentProduct = data;
      return data;
    },

    async deleteProduct(id) {
      await api.delete(`/products/${id}`);
      this.products = this.products.filter((p) => p.id !== id);
    },

    async fetchPriceHistory(productId, limit = 100) {
      const { data } = await api.get(
        `/products/${productId}/prices?limit=${limit}`
      );
      this.priceHistory = data;
      return data;
    },

    async checkPriceNow(productId) {
      const { data } = await api.post(`/track/${productId}/check`);
      this.priceHistory.unshift(data);
      return data;
    },
  },
});
