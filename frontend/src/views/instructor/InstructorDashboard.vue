<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useI18n } from "vue-i18n";
import { useRouter } from "vue-router";

import { clearInstructorToken, instructorApiFetch } from "../../api";

interface CurrentEntry {
  queue_number: string;
  iin?: string | null;
  photo_url?: string | null;
}

interface InstructorBase {
  id: number;
  name: string;
  login: string;
  instructor_number: number;
  status: string;
  accepted_count: number;
  is_active: boolean;
}

interface InstructorDashboardResponse {
  instructor: InstructorBase;
  current_entry?: CurrentEntry | null;
}

interface InstructorActionResponse {
  instructor_id: number;
  instructor_number: number;
  status: string;
  message: string;
  current_entry?: CurrentEntry | null;
}

interface TvRow {
  queue_number: string;
  status: string;
  instructor_number?: number | null;
}

const { t } = useI18n();
const router = useRouter();
const loading = ref(false);
const error = ref("");
const message = ref("");
const instructor = ref<InstructorBase | null>(null);
const currentEntry = ref<CurrentEntry | null>(null);
const upcoming = ref<TvRow[]>([]);

function statusClass(status: string): string {
  return `status-pill ${status}`;
}

async function loadUpcoming() {
  try {
    const rows = await instructorApiFetch<TvRow[]>("/queue/tv");
    upcoming.value = rows.filter((item) => item.status === "waiting").slice(0, 3);
  } catch {
    upcoming.value = [];
  }
}

async function loadDashboard() {
  loading.value = true;
  error.value = "";
  try {
    const payload = await instructorApiFetch<InstructorDashboardResponse>("/instructor/me");
    instructor.value = payload.instructor;
    currentEntry.value = payload.current_entry || null;
    message.value = "";
    await loadUpcoming();
  } catch (err) {
    if (err instanceof Error && err.message.toLowerCase().includes("authentication")) {
      clearInstructorToken();
      await router.push("/instructor/login");
      return;
    }
    error.value = err instanceof Error ? err.message : "Unknown error";
  } finally {
    loading.value = false;
  }
}

async function sendAction(action: "available" | "next") {
  loading.value = true;
  error.value = "";
  try {
    const payload = await instructorApiFetch<InstructorActionResponse>(
      `/instructor/me/${action}`,
      { method: "POST" },
    );
    if (instructor.value) {
      instructor.value = {
        ...instructor.value,
        status: payload.status,
      };
      if (action === "next") {
        instructor.value.accepted_count += currentEntry.value ? 1 : 0;
      }
    }
    currentEntry.value = payload.current_entry || null;
    message.value = payload.message;
    await loadUpcoming();
  } catch (err) {
    if (err instanceof Error && err.message.toLowerCase().includes("authentication")) {
      clearInstructorToken();
      await router.push("/instructor/login");
      return;
    }
    error.value = err instanceof Error ? err.message : "Unknown error";
  } finally {
    loading.value = false;
  }
}

async function logout() {
  try {
    await instructorApiFetch("/instructor/logout", { method: "POST" });
  } finally {
    clearInstructorToken();
    await router.push("/instructor/login");
  }
}

onMounted(loadDashboard);
</script>

<template>
  <section class="view-stack">
    <header class="hero card">
      <div>
        <p class="eyebrow">{{ t("instructor.queueControl") }}</p>
        <h2>{{ t("instructor.title") }}</h2>
        <p class="muted">{{ t("instructor.subtitle") }}</p>
      </div>

      <div class="header-actions">
        <span v-if="instructor" :class="statusClass(instructor.status)">{{ t(`status.${instructor.status}`) }}</span>
        <button class="action-button" :disabled="loading" @click="sendAction('available')">
          {{ t("instructor.available") }}
        </button>
        <button class="action-button secondary" :disabled="loading" @click="sendAction('next')">
          {{ t("instructor.next") }}
        </button>
        <button class="ghost-button" :disabled="loading" @click="logout">
          {{ t("instructor.logout") }}
        </button>
      </div>
    </header>

    <section class="split-grid">
      <section class="view-stack">
        <article class="card detail-card">
          <p class="label">{{ t("instructor.profile") }}</p>
          <h3>{{ instructor?.name || t("instructor.waiting") }}</h3>
          <p class="muted">{{ t("instructor.login") }}: {{ instructor?.login || "—" }}</p>
          <p class="muted">{{ t("instructor.queueDesk") }}: #{{ instructor?.instructor_number || "—" }}</p>
          <p class="muted">{{ t("instructor.accepted") }}: {{ instructor?.accepted_count || 0 }}</p>
          <p class="muted">{{ t("instructor.publicTvHint") }}</p>
        </article>

        <article class="card detail-card">
          <p class="label">{{ t("instructor.nextInLine") }}</p>
          <div class="list-stack" style="margin-top: 10px">
            <div v-for="item in upcoming" :key="item.queue_number" class="list-item">
              <div class="list-item-head">
                <strong>{{ item.queue_number }}</strong>
                <span :class="statusClass(item.status)">{{ t(`status.${item.status}`) }}</span>
              </div>
            </div>
            <p v-if="!upcoming.length" class="muted">{{ t("instructor.waiting") }}</p>
          </div>
        </article>
      </section>

      <section class="card detail-card">
        <p class="label">{{ t("instructor.currentUser") }}</p>
        <div class="detail-grid" style="margin-top: 10px">
          <div>
            <div class="current-user">
              <p><strong>{{ t("instructor.queueNumber") }}:</strong> {{ currentEntry?.queue_number || "—" }}</p>
              <p><strong>{{ t("instructor.iin") }}:</strong> {{ currentEntry?.iin || "—" }}</p>
              <img
                v-if="currentEntry?.photo_url"
                :src="currentEntry.photo_url"
                alt="User photo"
                class="user-photo"
              />
              <p v-else class="muted">{{ t("instructor.userPhoto") }}</p>
            </div>
          </div>

          <div class="view-stack">
            <article class="card form-card">
              <p class="label">{{ t("instructor.statusLabel") }}</p>
              <p class="muted">{{ message || t("instructor.waiting") }}</p>
            </article>
            <article class="card info-panel">
              <p class="label">{{ t("instructor.focusHintTitle") }}</p>
              <p class="muted">{{ t("instructor.focusHint") }}</p>
            </article>
          </div>
        </div>

        <p v-if="error" class="error-text" style="margin-top: 10px">{{ error }}</p>
      </section>
    </section>
  </section>
</template>
