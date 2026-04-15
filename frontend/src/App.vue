<script setup lang="ts">
import { computed } from "vue";
import { useI18n } from "vue-i18n";
import { RouterLink, RouterView, useRoute } from "vue-router";

const { locale, t } = useI18n();
const route = useRoute();

const languages = [
  { code: "kk", label: "Қазақша" },
  { code: "ru", label: "Русский" },
  { code: "en", label: "English" },
];

const navItems = computed(() => [
  { key: "admin", routeName: "admin", label: t("app.roleAdmin") },
  { key: "instructor", routeName: "instructor", label: t("app.roleInstructor") },
  { key: "tv", routeName: "tv", label: t("app.roleTv") },
]);

const shellClass = computed(() => (route.name === "tv" ? "app-shell app-shell-tv" : "app-shell"));
const title = computed(() => t((route.meta.titleKey as string) || "app.brand"));
const subtitle = computed(() => t((route.meta.subtitleKey as string) || "platform.defaultSubtitle"));
const isTv = computed(() => route.name === "tv");
</script>

<template>
  <div :class="shellClass">
    <div class="shell-frame">
      <header class="shell-topbar">
        <div class="brand-wrap">
          <div class="brand-dot" />
          <div>
            <div class="brand-row">
              <h1 class="brand-title">{{ t("app.brand") }}</h1>
              <span class="live-pill">{{ t("app.live") }}</span>
            </div>
            <p class="brand-subtitle">{{ t("platform.defaultSubtitle") }}</p>
          </div>
        </div>

        <div v-if="!isTv" class="toolbar-row">
          <label class="lang-control">
            <span>{{ t("app.language") }}</span>
            <select v-model="locale">
              <option v-for="language in languages" :key="language.code" :value="language.code">
                {{ language.label }}
              </option>
            </select>
          </label>
          <div class="theme-pill">{{ t("app.lightTheme") }}</div>
        </div>
      </header>

      <div v-if="!isTv" class="shell-layout">
        <aside class="left-nav card">
          <p class="left-nav-title">{{ t("app.previewRoles") }}</p>
          <nav class="left-nav-list">
            <RouterLink
              v-for="item in navItems"
              :key="item.key"
              :to="{ name: item.routeName }"
              class="nav-item"
              :class="{ active: route.name === item.routeName }"
            >
              <span>{{ item.label }}</span>
            </RouterLink>
          </nav>
        </aside>

        <main class="main-content">
          <section class="page-head card">
            <p class="eyebrow">{{ t("app.eyebrow") }}</p>
            <h2>{{ title }}</h2>
            <p class="muted">{{ subtitle }}</p>
          </section>
          <RouterView />
        </main>
      </div>

      <main v-else class="tv-content">
        <RouterView />
      </main>
    </div>
  </div>
</template>
