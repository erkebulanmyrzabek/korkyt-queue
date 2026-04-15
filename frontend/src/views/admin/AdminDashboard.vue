<script setup lang="ts">
import { computed, onMounted, reactive, ref } from "vue";
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
  password?: string | null;
  status: string;
  accepted_count: number;
  is_active: boolean;
}

interface CreateInstructorResponse {
  instructor: InstructorItem;
  generated_password: string;
}

interface GeneratedCredentials {
  login: string;
  password: string;
}

const improvements = [
  "Live updates without manual refresh across admin, instructor, and TV views",
  "Estimated wait time and current position in Telegram",
  "One-tap instructor workflow: Available -> Next -> Complete",
  "TV mode optimized for 5-10 meter readability",
  "Component system with predictable sizes, states, and spacing",
];

const { t } = useI18n();
const loading = ref(false);
const error = ref("");
const saving = ref(false);
const saveError = ref("");
const generatedCredentials = ref<GeneratedCredentials | null>(null);
const copyFeedback = ref("");
const search = ref("");
const instructors = ref<InstructorItem[]>([]);
const form = reactive({
  login: "",
});
const summary = ref<DashboardSummary>({
  total_people_in_queue: 0,
  active_instructors: 0,
  available_instructors: 0,
  users_served_today: 0,
});

const filteredInstructors = computed(() => {
  const query = search.value.trim().toLowerCase();
  if (!query) {
    return instructors.value;
  }
  return instructors.value.filter((item) => {
    const target = `${item.name} ${item.login} ${item.instructor_number}`.toLowerCase();
    return target.includes(query);
  });
});

function statusClass(status: string): string {
  return `status-pill ${status}`;
}

function workloadPercent(acceptedCount: number): number {
  return Math.min(100, acceptedCount * 5);
}

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
  generatedCredentials.value = null;
  copyFeedback.value = "";

  try {
    const payload = await apiFetch<CreateInstructorResponse>("/admin/instructors", {
      method: "POST",
      body: JSON.stringify(form),
    });
    generatedCredentials.value = {
      login: payload.instructor.login,
      password: payload.generated_password,
    };
    form.login = "";
    await Promise.all([loadSummary(), loadInstructors()]);
  } catch (err) {
    saveError.value = err instanceof Error ? err.message : "Unknown error";
  } finally {
    saving.value = false;
  }
}

async function copyText(value: string, feedbackKey: string) {
  try {
    if (navigator.clipboard?.writeText) {
      await navigator.clipboard.writeText(value);
    } else {
      const textarea = document.createElement("textarea");
      textarea.value = value;
      textarea.setAttribute("readonly", "");
      textarea.style.position = "absolute";
      textarea.style.left = "-9999px";
      document.body.appendChild(textarea);
      textarea.select();
      document.execCommand("copy");
      document.body.removeChild(textarea);
    }
    copyFeedback.value = t(feedbackKey);
  } catch {
    copyFeedback.value = t("admin.copyFailed");
  }
}

function copyLogin() {
  if (!generatedCredentials.value) {
    return;
  }
  void copyText(generatedCredentials.value.login, "admin.loginCopied");
}

function copyPassword() {
  if (!generatedCredentials.value) {
    return;
  }
  void copyText(generatedCredentials.value.password, "admin.passwordCopied");
}

function copyAllCredentials() {
  if (!generatedCredentials.value) {
    return;
  }
  const pair = `login: ${generatedCredentials.value.login}\npassword: ${generatedCredentials.value.password}`;
  void copyText(pair, "admin.credentialsCopied");
}

onMounted(async () => {
  await Promise.all([loadSummary(), loadInstructors()]);
});
</script>

<template>
  <section class="view-stack">
    <header class="hero card">
      <div>
        <p class="eyebrow">{{ t("admin.metrics") }}</p>
        <h2>{{ t("admin.title") }}</h2>
        <p class="muted">{{ t("admin.subtitle") }}</p>
      </div>
      <button class="action-button" :disabled="loading || saving" @click="loadSummary">
        {{ t("admin.refresh") }}
      </button>
    </header>

    <section class="stats-grid">
      <StatCard :title="t('admin.totalQueue')" :value="summary.total_people_in_queue" :caption="t('admin.waitingHint')" variant="blue" />
      <StatCard :title="t('admin.activeCalls')" :value="Math.max(0, summary.active_instructors - summary.available_instructors)" :caption="t('admin.activeHint')" variant="violet" />
      <StatCard :title="t('admin.servedToday')" :value="summary.users_served_today" :caption="t('admin.servedHint')" variant="green" />
      <StatCard :title="t('admin.avgWait')" :value="t('admin.avgWaitValue')" :caption="t('admin.avgWaitHint')" variant="orange" />
    </section>

    <section class="split-grid">
      <section class="card table-card">
        <div class="section-head">
          <div>
            <p class="eyebrow">{{ t("admin.instructorsEyebrow") }}</p>
            <h3>{{ t("admin.instructorsTitle") }}</h3>
          </div>
          <span class="status-pill waiting">{{ t("admin.activeInstructors") }}: {{ summary.active_instructors }}</span>
        </div>

        <div class="header-actions" style="margin-bottom: 10px">
          <input v-model="search" class="search-input" type="search" :placeholder="t('admin.search')" />
        </div>

        <div class="table-wrapper">
          <table class="data-table">
            <thead>
              <tr>
                <th>{{ t("admin.name") }}</th>
                <th>{{ t("admin.login") }}</th>
                <th>{{ t("admin.status") }}</th>
                <th>{{ t("admin.workload") }}</th>
                <th>{{ t("admin.instructorNumber") }}</th>
                <th>{{ t("admin.password") }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="instructor in filteredInstructors" :key="instructor.id">
                <td>{{ instructor.name }}</td>
                <td>{{ instructor.login }}</td>
                <td>
                  <span :class="statusClass(instructor.status)">{{ t(`status.${instructor.status}`) }}</span>
                </td>
                <td>
                  <div class="workload-wrap">
                    <div class="workload-head">
                      <span>{{ instructor.accepted_count }} users</span>
                      <span>{{ workloadPercent(instructor.accepted_count) }}%</span>
                    </div>
                    <div class="workload-track">
                      <div class="workload-fill" :style="{ width: `${workloadPercent(instructor.accepted_count)}%` }" />
                    </div>
                  </div>
                </td>
                <td>#{{ instructor.instructor_number }}</td>
                <td>{{ instructor.password || "—" }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <div class="view-stack">
        <section class="card form-card">
          <div class="section-head">
            <div>
              <p class="eyebrow">{{ t("admin.createEyebrow") }}</p>
              <h3>{{ t("admin.createTitle") }}</h3>
            </div>
          </div>

          <div class="form-grid">
            <label class="field">
              <span>{{ t("admin.login") }}</span>
              <input v-model="form.login" type="text" />
            </label>
          </div>
          <p class="muted form-hint">{{ t("admin.autoNumberHint") }}</p>

          <div class="header-actions" style="margin-top: 10px">
            <button class="action-button" :disabled="saving" @click="createInstructor">
              {{ t("admin.createButton") }}
            </button>
          </div>

          <div v-if="generatedCredentials" class="success-panel">
            <p class="label">{{ t("admin.credentialsIssued") }}</p>
            <div class="credential-grid">
              <div class="credential-row">
                <span class="muted credential-label">{{ t("admin.login") }}</span>
                <div class="credential-main">
                  <strong class="credential-value">{{ generatedCredentials.login }}</strong>
                  <button class="ghost-button copy-btn" type="button" @click="copyLogin">
                    {{ t("admin.copyLogin") }}
                  </button>
                </div>
              </div>
              <div class="credential-row">
                <span class="muted credential-label">{{ t("admin.password") }}</span>
                <div class="credential-main">
                  <strong class="credential-value">{{ generatedCredentials.password }}</strong>
                  <button class="ghost-button copy-btn" type="button" @click="copyPassword">
                    {{ t("admin.copyPassword") }}
                  </button>
                </div>
              </div>
            </div>
            <button class="action-button copy-all-btn" type="button" @click="copyAllCredentials">
              {{ t("admin.copyAllCredentials") }}
            </button>
            <p v-if="copyFeedback" class="copy-feedback">{{ copyFeedback }}</p>
          </div>

          <p v-if="saveError" class="error-text">{{ saveError }}</p>
        </section>

        <section class="card info-panel">
          <div class="section-head">
            <div>
              <p class="eyebrow">{{ t("admin.topImprovements") }}</p>
              <h3>{{ t("admin.note") }}</h3>
            </div>
          </div>
          <div class="list-stack">
            <article v-for="(item, idx) in improvements" :key="item" class="list-item">
              <div class="list-item-head">
                <strong>0{{ idx + 1 }}</strong>
              </div>
              <p class="muted">{{ item }}</p>
            </article>
          </div>
          <p v-if="error" class="error-text" style="margin-top: 10px">{{ error }}</p>
        </section>
      </div>
    </section>
  </section>
</template>
