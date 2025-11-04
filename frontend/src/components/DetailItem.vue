<template>
  <div class="flex items-center space-x-2">
    <component :is="icon" class="w-4 h-4 text-gray-400" />
    <div class="flex flex-col">
      <span class="text-xs text-gray-500">{{ label }}</span>
      <span class="text-sm font-medium text-gray-900">{{ value }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Component } from 'vue';

interface Props {
  label: string;
  value: string;
  icon: Component;
}

defineProps<Props>();
</script>
