<script setup lang="ts">
import { ref } from "vue";
import { useI18n } from "vue-i18n";

import { apiFetch } from "../../api";

interface CurrentEntry {
  queue_number: string;
  iin?: string | null;
  photo_url?: string | null;
}

interface InstructorResponse {
  instructor_id: number;
  instructor_number: number;
  status: string;
  message: string;
  current_entry?: CurrentEntry | null;
}

const { t } = useI18n();
const instructorId = ref(1);
const loading = ref(false);
const error = ref("");
const payload = ref<InstructorResponse | null>(null);

async function sendAction(action: "available" | "next") {
  loading.value = true;
  error.value = "";
  try {
    payload.value = await apiFetch<InstructorResponse>(
      `/queue/instructors/${instructorId.value}/${action}`,
      { method: "POST" },
    );
  } catch (err) {
    error.value = err instanceof Error ? err.message : "Unknown error";
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <section class="view-stack">
    <header class="hero card">
      <div>
        <p class="eyebrow">{{ t("app.eyebrow") }}</p>
        <h2>{{ t("instructor.title") }}</h2>
        <p class="muted">{{ t("instructor.subtitle") }}</p>
      </div>

      <div class="instructor-actions">
        <label class="field">
          <span>{{ t("instructor.instructorId") }}</span>
          <input v-model.number="instructorId" type="number" min="1" />
        </label>
        <button class="action-button" :disabled="loading" @click="sendAction('available')">
          {{ t("instructor.available") }}
        </button>
        <button class="action-button secondary" :disabled="loading" @click="sendAction('next')">
          {{ t("instructor.next") }}
        </button>
      </div>
    </header>

    <section class="card detail-card">
      <div class="detail-grid">
        <div>
          <p class="label">{{ t("instructor.response") }}</p>
          <h3>{{ payload?.message || t("instructor.waiting") }}</h3>
          <p class="muted">Status: {{ payload?.status || "idle" }}</p>
        </div>

        <div v-if="payload?.current_entry" class="current-user">
          <p><strong>{{ t("instructor.queueNumber") }}:</strong> {{ payload.current_entry.queue_number }}</p>
          <p><strong>{{ t("instructor.iin") }}:</strong> {{ payload.current_entry.iin || "—" }}</p>
          <img
            v-if="payload.current_entry.photo_url"
            :src="payload.current_entry.photo_url"
            alt="User photo"
            class="user-photo"
          />
        </div>
      </div>

      <p v-if="error" class="error-text">{{ error }}</p>
    </section>
  </section>
</template>
