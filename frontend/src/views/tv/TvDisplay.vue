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

const highlightStatuses = new Set(["assigned", "in_service"]);

function statusClass(status: string): string {
  return `status-pill ${status}`;
}

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
  <section class="tv-mode">
    <div class="tv-grid">
      <article class="tv-highlight">
        <p class="tv-kicker">{{ t("tv.highlight") }}</p>
        <h2 style="margin-top: 6px">{{ t("app.brand") }}</h2>

        <template v-if="rows.length">
          <p class="tv-kicker" style="margin-top: 26px">{{ t("tv.queueNo") }}</p>
          <p class="tv-number">{{ rows[0].queue_number }}</p>
          <div class="tv-desk">{{ t("tv.serviceWindow") }} #{{ rows[0].instructor_number ?? "—" }}</div>
        </template>

        <p v-else class="muted" style="margin-top: 16px">{{ t("tv.empty") }}</p>
      </article>

      <section class="view-stack">
        <article class="tv-side-card">
          <p style="font-size: 1.1rem; font-weight: 700">{{ t("tv.nextInLine") }}</p>
          <div class="list-stack" style="margin-top: 10px">
            <div
              v-for="row in rows.slice(1, 6)"
              :key="row.queue_number"
              class="tv-row"
              :class="{ highlighted: highlightStatuses.has(row.status) }"
            >
              <strong style="font-size: 1.45rem">{{ row.queue_number }}</strong>
              <span :class="statusClass(row.status)">{{ t(`status.${row.status}`) }}</span>
            </div>
          </div>
        </article>

        <article class="tv-note">
          <p class="tv-kicker">Accessibility</p>
          <p style="font-size: 1.15rem; margin-top: 6px">{{ t("tv.readability") }}</p>
          <ul style="margin: 8px 0 0 18px; padding: 0">
            <li>{{ t("tv.rule1") }}</li>
            <li>{{ t("tv.rule2") }}</li>
            <li>{{ t("tv.rule3") }}</li>
          </ul>
        </article>
      </section>
    </div>

    <p v-if="error" class="error-text" style="margin-top: 10px">{{ error }}</p>
  </section>
</template>
