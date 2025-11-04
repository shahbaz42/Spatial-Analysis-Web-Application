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
      class="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-primary-600"
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
