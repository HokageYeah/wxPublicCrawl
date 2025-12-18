<template>
  <div class="flex items-center justify-center">
    <div class="relative">
      <!-- Spinner -->
      <div class="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-primary"></div>
      
      <!-- Label -->
      <div v-if="label" class="mt-2 text-sm text-secondary text-center">{{ label }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  label?: string;
}>();
</script> 