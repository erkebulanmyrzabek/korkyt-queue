<script setup lang="ts">
import { useI18n } from "vue-i18n";
import { RouterLink, RouterView } from "vue-router";

const { locale, t } = useI18n();

const languages = [
  { code: "kk", label: "Қазақша" },
  { code: "ru", label: "Русский" },
  { code: "en", label: "English" },
];
</script>

<template>
  <div class="app-shell">
    <header class="topbar">
      <div>
        <p class="eyebrow">{{ t("app.eyebrow") }}</p>
        <h1 class="brand">{{ t("app.brand") }}</h1>
      </div>

      <nav class="nav">
        <RouterLink to="/admin" class="nav-link">{{ t("nav.admin") }}</RouterLink>
        <RouterLink to="/instructor" class="nav-link">{{ t("nav.instructor") }}</RouterLink>
        <RouterLink to="/tv" class="nav-link">{{ t("nav.tv") }}</RouterLink>
      </nav>

      <label class="language-switcher">
        <span>{{ t("app.language") }}</span>
        <select v-model="locale">
          <option v-for="language in languages" :key="language.code" :value="language.code">
            {{ language.label }}
          </option>
        </select>
      </label>
    </header>

    <main class="page-shell">
      <RouterView />
    </main>
  </div>
</template>

