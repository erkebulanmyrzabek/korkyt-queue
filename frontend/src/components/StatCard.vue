<script setup lang="ts">
defineProps<{
  title: string;
  value: number | string;
  caption?: string;
}>();
</script>

<template>
  <article class="card stat-card">
    <p class="stat-title">{{ title }}</p>
    <strong class="stat-value">{{ value }}</strong>
    <p v-if="caption" class="stat-caption">{{ caption }}</p>
  </article>
</template>

