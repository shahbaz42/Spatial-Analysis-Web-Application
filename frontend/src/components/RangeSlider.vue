<template>
  <div>
    <!-- Label and values -->
    <div class="flex items-center justify-between mb-2">
      <label class="text-sm text-gray-300 flex items-center space-x-2">
        <component :is="icon" :class="['w-4 h-4', color]" />
        <span>{{ label }}</span>
      </label>
      <span class="text-sm font-medium text-white">
        {{ formatValue(modelValue[0]) }} - {{ formatValue(modelValue[1]) }}
      </span>
    </div>

    <!-- Dual Range Slider Container -->
    <div class="relative w-full h-2 py-3">
      <!-- Track Background -->
      <div class="absolute w-full h-1.5 bg-gray-700 rounded-lg"></div>

      <!-- Highlighted Active Range -->
      <div
        class="absolute h-1.5 bg-blue-500 rounded-lg"
        :style="{
          left: `${((modelValue[0] - min) / (max - min)) * 100}%`,
          width: `${((modelValue[1] - modelValue[0]) / (max - min)) * 100}%`,
        }"
      ></div>

      <!-- Min Handle -->
      <input
        type="range"
        :min="min"
        :max="max"
        :step="step"
        :value="modelValue[0]"
        @input="onMinChange"
        class="range-thumb w-full absolute"
      />

      <!-- Max Handle -->
      <input
        type="range"
        :min="min"
        :max="max"
        :step="step"
        :value="modelValue[1]"
        @input="onMaxChange"
        class="range-thumb w-full absolute"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Component } from 'vue';

interface Props {
  label: string;
  icon: Component;
  modelValue: [number, number];
  color?: string;
  min?: number;
  max?: number;
  step?: number;
}

const props = withDefaults(defineProps<Props>(), {
  color: 'text-gray-400',
  min: 0,
  max: 1,
  step: 0.01,
});

const emit = defineEmits<{
  'update:modelValue': [[number, number]];
}>();

const onMinChange = (event: Event) => {
  const input = event.target as HTMLInputElement;
  const newMin = parseFloat(input.value);
  if (newMin > props.modelValue[1]) {
    input.value = props.modelValue[0].toString();
    return;
  }
  emit('update:modelValue', [newMin, props.modelValue[1]]);
};

const onMaxChange = (event: Event) => {
  const input = event.target as HTMLInputElement;
  const newMax = parseFloat(input.value);
  if (newMax < props.modelValue[0]) {
    input.value = props.modelValue[1].toString();
    return;
  }
  emit('update:modelValue', [props.modelValue[0], newMax]);
};

const formatValue = (value: number): string => {
  if (value >= 1000) {
    return new Intl.NumberFormat('en-US').format(Math.round(value));
  }
  if (value >= 1) {
    return value.toFixed(1);
  }
  return value.toFixed(2);
};
</script>

<style scoped>
.range-thumb {
  -webkit-appearance: none;
  appearance: none;
  background: none;
  pointer-events: none;
  height: 2rem;
  padding: 0;
}

/* Hide default track */
.range-thumb::-webkit-slider-runnable-track {
  height: 0.5rem;
  background: transparent;
}

.range-thumb::-moz-range-track {
  height: 0.5rem;
  background: transparent;
}

/* WebKit Thumb */
.range-thumb::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  height: 1rem;
  width: 1rem;
  background-color: #3b82f6;
  border-radius: 9999px;
  cursor: pointer;
  margin-top: -1.05rem;
  pointer-events: all;
}

/* Firefox Thumb */
.range-thumb::-moz-range-thumb {
  height: 1rem;
  width: 1rem;
  background-color: #3b82f6;
  border-radius: 9999px;
  cursor: pointer;
  border: none;
  pointer-events: all;
  margin-top: -0.25rem;
}
</style>