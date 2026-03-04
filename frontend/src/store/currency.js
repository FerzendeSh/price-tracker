import { defineStore } from "pinia";
import api from "../api/index.js";

export const useCurrencyStore = defineStore("currency", {
  state: () => ({
    currencies: [],
    loaded: false,
  }),

  getters: {
    /** Lookup map: "USD" → { code, symbol, name } */
    byCode: (state) => {
      const map = {};
      for (const c of state.currencies) map[c.code] = c;
      return map;
    },
  },

  actions: {
    async fetchCurrencies() {
      if (this.loaded) return;
      try {
        const { data } = await api.get("/currencies");
        this.currencies = data;
        this.loaded = true;
      } catch {
        // fallback
        this.currencies = [{ code: "USD", symbol: "$", name: "US Dollar" }];
      }
    },

    getSymbol(code) {
      return this.byCode[code]?.symbol ?? code;
    },
  },
});
