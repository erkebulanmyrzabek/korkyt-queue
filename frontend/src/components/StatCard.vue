<script setup lang="ts">
defineProps<{
  title: string;
  value: number | string;
  caption?: string;
  variant?: "blue" | "violet" | "green" | "orange";
}>();
</script>

<template>
  <article class="card stat-card" :class="`stat-${variant || 'blue'}`">
    <div class="stat-inner">
      <p class="stat-title">{{ title }}</p>
      <strong class="stat-value">{{ value }}</strong>
      <p v-if="caption" class="stat-caption">{{ caption }}</p>
    </div>
  </article>
</template>
