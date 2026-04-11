<script setup lang="ts">
import { onMounted, reactive, ref } from "vue";
import { useI18n } from "vue-i18n";

import { apiFetch } from "../../api";
import StatCard from "../../components/StatCard.vue";

interface DashboardSummary {
  total_people_in_queue: number;
  active_instructors: number;
  available_instructors: number;
  users_served_today: number;
}

interface InstructorItem {
  id: number;
  name: string;
  login: string;
  instructor_number: number;
  status: string;
  accepted_count: number;
  is_active: boolean;
}

interface CreateInstructorResponse {
  instructor: InstructorItem;
  generated_password: string;
}

const { t } = useI18n();
const loading = ref(false);
const error = ref("");
const saving = ref(false);
const saveError = ref("");
const successPassword = ref("");
const instructors = ref<InstructorItem[]>([]);
const form = reactive({
  name: "",
  login: "",
  instructor_number: 1,
});
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
    summary.value = await apiFetch<DashboardSummary>("/admin/dashboard/summary");
  } catch (err) {
    error.value = err instanceof Error ? err.message : "Unknown error";
  } finally {
    loading.value = false;
  }
}

async function loadInstructors() {
  try {
    instructors.value = await apiFetch<InstructorItem[]>("/admin/instructors");
  } catch (err) {
    saveError.value = err instanceof Error ? err.message : "Unknown error";
  }
}

async function createInstructor() {
  saving.value = true;
  saveError.value = "";
  successPassword.value = "";

  try {
    const payload = await apiFetch<CreateInstructorResponse>("/admin/instructors", {
      method: "POST",
      body: JSON.stringify(form),
    });
    successPassword.value = payload.generated_password;
    form.name = "";
    form.login = "";
    form.instructor_number += 1;
    await Promise.all([loadSummary(), loadInstructors()]);
  } catch (err) {
    saveError.value = err instanceof Error ? err.message : "Unknown error";
  } finally {
    saving.value = false;
  }
}

onMounted(async () => {
  await Promise.all([loadSummary(), loadInstructors()]);
});
</script>

<template>
  <section class="view-stack">
    <header class="hero card">
      <div>
        <p class="eyebrow">{{ t("app.eyebrow") }}</p>
        <h2>{{ t("admin.title") }}</h2>
        <p class="muted">{{ t("admin.subtitle") }}</p>
      </div>
      <button class="action-button" :disabled="loading || saving" @click="loadSummary">
        {{ t("admin.refresh") }}
      </button>
    </header>

    <section class="stats-grid">
      <StatCard :title="t('admin.totalQueue')" :value="summary.total_people_in_queue" />
      <StatCard :title="t('admin.activeInstructors')" :value="summary.active_instructors" />
      <StatCard :title="t('admin.availableInstructors')" :value="summary.available_instructors" />
      <StatCard :title="t('admin.servedToday')" :value="summary.users_served_today" />
    </section>

    <section class="split-grid">
      <section class="card form-card">
        <div class="section-head">
          <div>
            <p class="eyebrow">{{ t("admin.createEyebrow") }}</p>
            <h3>{{ t("admin.createTitle") }}</h3>
          </div>
        </div>

        <div class="form-grid">
          <label class="field">
            <span>{{ t("admin.name") }}</span>
            <input v-model="form.name" type="text" />
          </label>
          <label class="field">
            <span>{{ t("admin.login") }}</span>
            <input v-model="form.login" type="text" />
          </label>
          <label class="field">
            <span>{{ t("admin.instructorNumber") }}</span>
            <input v-model.number="form.instructor_number" type="number" min="1" />
          </label>
        </div>

        <div class="header-actions">
          <button class="action-button" :disabled="saving" @click="createInstructor">
            {{ t("admin.createButton") }}
          </button>
        </div>

        <div v-if="successPassword" class="success-panel">
          <p class="label">{{ t("admin.generatedPassword") }}</p>
          <strong class="credential-box">{{ successPassword }}</strong>
        </div>

        <p v-if="saveError" class="error-text">{{ saveError }}</p>
      </section>

      <section class="card info-panel">
        <p class="muted">{{ t("admin.note") }}</p>
        <p v-if="error" class="error-text">{{ error }}</p>
      </section>
    </section>

    <section class="card table-card">
      <div class="section-head">
        <div>
          <p class="eyebrow">{{ t("admin.instructorsEyebrow") }}</p>
          <h3>{{ t("admin.instructorsTitle") }}</h3>
        </div>
      </div>

      <div class="table-wrapper">
        <table class="data-table">
          <thead>
            <tr>
              <th>{{ t("admin.name") }}</th>
              <th>{{ t("admin.login") }}</th>
              <th>{{ t("admin.instructorNumber") }}</th>
              <th>{{ t("admin.status") }}</th>
              <th>{{ t("admin.accepted") }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="instructor in instructors" :key="instructor.id">
              <td>{{ instructor.name }}</td>
              <td>{{ instructor.login }}</td>
              <td>{{ instructor.instructor_number }}</td>
              <td>{{ instructor.status }}</td>
              <td>{{ instructor.accepted_count }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </section>
</template>
