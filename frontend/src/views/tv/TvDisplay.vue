<script setup lang="ts">
import { onMounted, onUnmounted, ref } from "vue";
import { useI18n } from "vue-i18n";

import { apiFetch } from "../../api";

interface TvRow {
  queue_number: string;
  status: string;
  instructor_number?: number | null;
}

const { t } = useI18n();
const rows = ref<TvRow[]>([]);
const error = ref("");
let timer: number | undefined;

async function loadRows() {
  try {
    rows.value = await apiFetch<TvRow[]>("/queue/tv");
    error.value = "";
  } catch (err) {
    error.value = err instanceof Error ? err.message : "Unknown error";
  }
}

onMounted(async () => {
  await loadRows();
  timer = window.setInterval(loadRows, 5000);
});

onUnmounted(() => {
  if (timer) {
    clearInterval(timer);
  }
});
</script>

<template>
  <section class="view-stack tv-mode">
    <header class="hero card tv-hero">
      <div>
        <p class="eyebrow">{{ t("app.eyebrow") }}</p>
        <h2>{{ t("tv.title") }}</h2>
        <p class="muted">{{ t("tv.subtitle") }}</p>
      </div>
    </header>

    <section class="card table-card">
      <table class="queue-table">
        <thead>
          <tr>
            <th>{{ t("tv.queue") }}</th>
            <th>{{ t("tv.status") }}</th>
            <th>{{ t("tv.instructor") }}</th>
          </tr>
        </thead>
        <tbody v-if="rows.length">
          <tr
            v-for="row in rows"
            :key="row.queue_number"
            :class="{ highlighted: row.status === 'assigned' || row.status === 'in_service' }"
          >
            <td>{{ row.queue_number }}</td>
            <td>{{ row.status }}</td>
            <td>{{ row.instructor_number ?? "—" }}</td>
          </tr>
        </tbody>
      </table>

      <p v-if="!rows.length" class="muted">{{ t("tv.empty") }}</p>
      <p v-if="error" class="error-text">{{ error }}</p>
    </section>
  </section>
</template>

