<template>
  <div>
    <div class="flex items-center justify-between mb-2">
      <label class="text-sm text-gray-300 flex items-center space-x-2">
        <component :is="icon" :class="['w-4 h-4', color]" />
        <span>{{ label }}</span>
      </label>
      <span class="text-sm font-medium text-white">{{ modelValue.toFixed(2) }}</span>
    </div>

    <input
      type="range"
      min="0"
      max="1"
      step="0.01"
      :value="modelValue"
      @input="$emit('update:modelValue', parseFloat(($event.target as HTMLInputElement).value))"
      class="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer range-slider"
    />
  </div>
</template>

<script setup lang="ts">
import type { Component } from 'vue';

interface Props {
  label: string;
  icon: Component;
  modelValue: number;
  color?: string;
}

withDefaults(defineProps<Props>(), {
  color: 'text-gray-400',
});

defineEmits<{
  'update:modelValue': [value: number];
}>();
</script>

<style scoped>
/* ===== Range Track ===== */
.range-slider::-webkit-slider-runnable-track {
  height: 0.4rem;
  background-color: #374151; /* Tailwind gray-700 */
  border-radius: 0.25rem;
}

.range-slider::-moz-range-track {
  height: 0.4rem;
  background-color: #374151;
  border-radius: 0.25rem;
}

/* ===== Range Thumb ===== */
.range-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  height: 1rem;
  width: 1rem;
  background-color: #3b82f6; /* Tailwind blue-500 */
  border-radius: 9999px;
  margin-top: -0.3rem; /* aligns thumb with track */
  cursor: pointer;
}

.range-slider::-moz-range-thumb {
  height: 1rem;
  width: 1rem;
  background-color: #3b82f6;
  border-radius: 9999px;
  cursor: pointer;
  border: none;
}
</style>
