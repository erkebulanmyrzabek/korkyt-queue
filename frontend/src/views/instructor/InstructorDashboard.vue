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

const { t } = useI18n();
const router = useRouter();
const loading = ref(false);
const error = ref("");
const message = ref("");
const instructor = ref<InstructorBase | null>(null);
const currentEntry = ref<CurrentEntry | null>(null);

async function loadDashboard() {
  loading.value = true;
  error.value = "";
  try {
    const payload = await instructorApiFetch<InstructorDashboardResponse>("/instructor/me");
    instructor.value = payload.instructor;
    currentEntry.value = payload.current_entry || null;
    message.value = "";
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
    }
    currentEntry.value = payload.current_entry || null;
    message.value = payload.message;
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
        <p class="eyebrow">{{ t("app.eyebrow") }}</p>
        <h2>{{ t("instructor.title") }}</h2>
        <p class="muted">{{ t("instructor.subtitle") }}</p>
      </div>

      <div class="header-actions">
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

    <section class="card detail-card">
      <div class="detail-grid">
        <div>
          <p class="label">{{ t("instructor.profile") }}</p>
          <h3>{{ instructor?.name || t("instructor.waiting") }}</h3>
          <p class="muted">{{ t("instructor.login") }}: {{ instructor?.login || "—" }}</p>
          <p class="muted">{{ t("instructor.queueDesk") }}: {{ instructor?.instructor_number || "—" }}</p>
          <p class="muted">{{ t("instructor.statusLabel") }}: {{ instructor?.status || "idle" }}</p>
          <p class="muted">{{ t("instructor.accepted") }}: {{ instructor?.accepted_count || 0 }}</p>
        </div>

        <div v-if="currentEntry" class="current-user">
          <p><strong>{{ t("instructor.queueNumber") }}:</strong> {{ currentEntry.queue_number }}</p>
          <p><strong>{{ t("instructor.iin") }}:</strong> {{ currentEntry.iin || "—" }}</p>
          <img
            v-if="currentEntry.photo_url"
            :src="currentEntry.photo_url"
            alt="User photo"
            class="user-photo"
          />
        </div>
      </div>

      <p class="muted">{{ message || t("instructor.waiting") }}</p>
      <p v-if="error" class="error-text">{{ error }}</p>
    </section>
  </section>
</template>
