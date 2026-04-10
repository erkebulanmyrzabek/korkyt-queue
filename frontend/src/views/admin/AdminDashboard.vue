<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useI18n } from "vue-i18n";

import { apiFetch } from "../../api";
import StatCard from "../../components/StatCard.vue";

interface DashboardSummary {
  total_people_in_queue: number;
  active_instructors: number;
  available_instructors: number;
  users_served_today: number;
}

const { t } = useI18n();
const loading = ref(false);
const error = ref("");
const summary = ref<DashboardSummary>({
  total_people_in_queue: 0,
  active_instructors: 0,
  available_instructors: 0,
  users_served_today: 0,
});

async function loadSummary() {
  loading.value = true;
  error.value = "";
  try {
    summary.value = await apiFetch<DashboardSummary>("/dashboard/summary");
  } catch (err) {
    error.value = err instanceof Error ? err.message : "Unknown error";
  } finally {
    loading.value = false;
  }
}

onMounted(loadSummary);
</script>

<template>
  <section class="view-stack">
    <header class="hero card">
      <div>
        <p class="eyebrow">{{ t("app.eyebrow") }}</p>
        <h2>{{ t("admin.title") }}</h2>
        <p class="muted">{{ t("admin.subtitle") }}</p>
      </div>
      <button class="action-button" :disabled="loading" @click="loadSummary">
        {{ t("admin.refresh") }}
      </button>
    </header>

    <section class="stats-grid">
      <StatCard :title="t('admin.totalQueue')" :value="summary.total_people_in_queue" />
      <StatCard :title="t('admin.activeInstructors')" :value="summary.active_instructors" />
      <StatCard :title="t('admin.availableInstructors')" :value="summary.available_instructors" />
      <StatCard :title="t('admin.servedToday')" :value="summary.users_served_today" />
    </section>

    <section class="card info-panel">
      <p class="muted">{{ t("admin.note") }}</p>
      <p v-if="error" class="error-text">{{ error }}</p>
    </section>
  </section>
</template>

