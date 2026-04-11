<script setup lang="ts">
import { reactive, ref } from "vue";
import { useI18n } from "vue-i18n";
import { useRouter } from "vue-router";

import { apiFetch, setInstructorToken } from "../../api";

interface InstructorBase {
  id: number;
  name: string;
  login: string;
  instructor_number: number;
  status: string;
  accepted_count: number;
  is_active: boolean;
}

interface InstructorLoginResponse {
  access_token: string;
  token_type: string;
  instructor: InstructorBase;
}

const { t } = useI18n();
const router = useRouter();
const loading = ref(false);
const error = ref("");
const form = reactive({
  login: "",
  password: "",
});

async function submitLogin() {
  loading.value = true;
  error.value = "";

  try {
    const payload = await apiFetch<InstructorLoginResponse>("/instructor/login", {
      method: "POST",
      body: JSON.stringify(form),
    });
    setInstructorToken(payload.access_token);
    await router.push("/instructor");
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
        <h2>{{ t("instructor.loginTitle") }}</h2>
        <p class="muted">{{ t("instructor.loginSubtitle") }}</p>
      </div>
    </header>

    <section class="card form-card auth-card">
      <div class="form-grid single-column">
        <label class="field">
          <span>{{ t("instructor.login") }}</span>
          <input v-model="form.login" type="text" autocomplete="username" />
        </label>
        <label class="field">
          <span>{{ t("instructor.password") }}</span>
          <input v-model="form.password" type="password" autocomplete="current-password" />
        </label>
      </div>

      <div class="header-actions">
        <button class="action-button" :disabled="loading" @click="submitLogin">
          {{ t("instructor.signIn") }}
        </button>
      </div>

      <p class="muted">{{ t("instructor.publicTvHint") }}</p>
      <p v-if="error" class="error-text">{{ error }}</p>
    </section>
  </section>
</template>
