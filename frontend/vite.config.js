import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    proxy: {
      "/auth": "http://localhost:8000",
      "/products": "http://localhost:8000",
      "/track": "http://localhost:8000",
      "/admin": "http://localhost:8000",
      "/currencies": "http://localhost:8000",
      "/prices": "http://localhost:8000",
    },
  },
});