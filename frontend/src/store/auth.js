import { defineStore } from "pinia";
import api from "../api/index.js";

export const useAuthStore = defineStore("auth", {
  state: () => ({
    token: localStorage.getItem("token") || null,
    user: null,
  }),

  getters: {
    isLoggedIn: (state) => !!state.token,
    isAdmin: (state) => state.user?.is_admin === true,
  },

  actions: {
    async register(username, email, password) {
      const { data } = await api.post("/auth/register", {
        username,
        email,
        password,
      });
      return data;
    },

    async login(username, password) {
      const { data } = await api.post("/auth/login", { username, password });
      this.token = data.access_token;
      localStorage.setItem("token", data.access_token);
      await this.fetchUser();
    },

    async fetchUser() {
      try {
        const { data } = await api.get("/auth/me");
        this.user = data;
      } catch {
        this.logout();
      }
    },

    logout() {
      this.token = null;
      this.user = null;
      localStorage.removeItem("token");
    },

    async deleteAccount() {
      await api.delete("/auth/me");
      this.logout();
    },
  },
});
