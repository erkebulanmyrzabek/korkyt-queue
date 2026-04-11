<script setup lang="ts">
import { computed } from "vue";
import { useI18n } from "vue-i18n";
import { RouterView, useRoute } from "vue-router";

const { locale, t } = useI18n();
const route = useRoute();

const languages = [
  { code: "kk", label: "Қазақша" },
  { code: "ru", label: "Русский" },
  { code: "en", label: "English" },
];

const showHeader = computed(() => route.name !== "tv");
const title = computed(() => t((route.meta.titleKey as string) || "app.brand"));
const subtitle = computed(() => t((route.meta.subtitleKey as string) || "platform.defaultSubtitle"));
</script>

<template>
  <div class="app-shell" :class="{ 'tv-shell': route.name === 'tv' }">
    <header v-if="showHeader" class="topbar">
      <div>
        <p class="eyebrow">{{ t("app.eyebrow") }}</p>
        <h1 class="brand">{{ title }}</h1>
        <p class="muted platform-meta">{{ subtitle }}</p>
      </div>

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
