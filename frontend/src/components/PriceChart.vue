<template>
  <div class="chart-wrapper">
    <Line v-if="chartData" :data="chartData" :options="chartOptions" />
    <p v-else class="muted">No price history to display.</p>
  </div>
</template>

<script setup>
import { computed } from "vue";
import { Line } from "vue-chartjs";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from "chart.js";
import { useCurrencyStore } from "../store/currency.js";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
);

const props = defineProps({
  history: { type: Array, required: true },
  productName: { type: String, default: "Price" },
  currency: { type: String, default: "USD" },
});

const currencyStore = useCurrencyStore();
const sym = computed(() => currencyStore.getSymbol(props.currency));

const chartData = computed(() => {
  if (!props.history.length) return null;

  const sorted = [...props.history].reverse();

  return {
    labels: sorted.map((h) =>
      new Date(h.timestamp).toLocaleDateString("en-US", {
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      })
    ),
    datasets: [
      {
        label: props.productName,
        data: sorted.map((h) => Number(h.price)),
        borderColor: "#4f46e5",
        backgroundColor: "rgba(79, 70, 229, 0.1)",
        fill: true,
        tension: 0.3,
        pointRadius: 3,
      },
    ],
  };
});

const chartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false },
    tooltip: {
      callbacks: {
        label: (ctx) => `${sym.value}${ctx.parsed.y.toFixed(2)}`,
      },
    },
  },
  scales: {
    y: {
      ticks: {
        callback: (v) => `${sym.value}${v}`,
      },
    },
  },
}));
</script>

<style scoped>
.chart-wrapper {
  height: 300px;
  margin: 1rem 0;
}
.muted {
  color: var(--text-muted);
  text-align: center;
  padding: 2rem;
}
</style>
