<script setup lang="ts">
import { useI18n } from "vue-i18n";

const { t } = useI18n();

const flow = [
  { from: "bot", textKey: "telegram.msgStart" },
  { from: "app", textKey: "telegram.msgEnterIin" },
  { from: "user", textKey: "telegram.msgIin" },
  { from: "app", textKey: "telegram.msgSendPhoto" },
  { from: "user", textKey: "telegram.msgPhoto" },
  { from: "app", textKey: "telegram.msgTicket" },
  { from: "call", textKey: "telegram.msgCall" },
] as const;

const uxItems = [
  "telegram.ux1",
  "telegram.ux2",
  "telegram.ux3",
  "telegram.ux4",
] as const;

const components = [
  "telegram.comp1",
  "telegram.comp2",
  "telegram.comp3",
  "telegram.comp4",
  "telegram.comp5",
  "telegram.comp6",
] as const;
</script>

<template>
  <section class="split-grid">
    <article class="telegram-chat card">
      <header class="section-head">
        <div>
          <p class="eyebrow">{{ t("telegram.title") }}</p>
          <h3>{{ t("telegram.subtitle") }}</h3>
        </div>
        <span class="status-pill waiting">Bot</span>
      </header>

      <div class="chat-stack">
        <div
          v-for="item in flow"
          :key="item.textKey"
          class="chat-bubble"
          :class="[`from-${item.from}`]"
        >
          {{ t(item.textKey) }}
        </div>
      </div>
    </article>

    <section class="view-stack">
      <article class="card info-panel">
        <div class="section-head">
          <div>
            <p class="eyebrow">{{ t("telegram.flowTitle") }}</p>
            <h3>{{ t("telegram.flowSubtitle") }}</h3>
          </div>
        </div>
        <div class="list-stack">
          <div v-for="item in uxItems" :key="item" class="list-item">
            <p class="muted">{{ t(item) }}</p>
          </div>
        </div>
      </article>

      <article class="card info-panel">
        <div class="section-head">
          <div>
            <p class="eyebrow">{{ t("telegram.componentsTitle") }}</p>
            <h3>{{ t("telegram.componentsSubtitle") }}</h3>
          </div>
        </div>
        <div class="component-grid">
          <div v-for="item in components" :key="item" class="component-chip">
            {{ t(item) }}
          </div>
        </div>
      </article>
    </section>
  </section>
</template>
