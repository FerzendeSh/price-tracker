import axios from "axios";

const MAX_RETRIES = 6;
const RETRY_DELAY_MS = 10000; // 10 seconds between retries

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "/",
  headers: { "Content-Type": "application/json" },
  timeout: 90000, // 90s — covers Render free-tier cold starts
});

// Attach JWT token to every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Global retry for 502/503/504 (Render cold-start)
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const config = error.config;
    const status = error.response?.status;

    // Only retry on gateway errors, and don't retry forever
    if (status && status >= 502 && status <= 504) {
      config.__retryCount = config.__retryCount || 0;
      if (config.__retryCount < MAX_RETRIES) {
        config.__retryCount += 1;
        await sleep(RETRY_DELAY_MS);
        return api(config);
      }
    }

    // 401 handling
    if (status === 401) {
      const url = config?.url || "";
      const isAuthEndpoint =
        url.includes("/auth/login") || url.includes("/auth/register");

      if (!isAuthEndpoint) {
        localStorage.removeItem("token");
        window.location.href = "/login";
      }
    }

    return Promise.reject(error);
  }
);

export default api;
