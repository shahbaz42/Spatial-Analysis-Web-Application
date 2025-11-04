<template>
  <div class="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
    <div class="bg-gray-800 rounded-lg p-8 shadow-2xl flex flex-col items-center space-y-4">
      <div class="relative">
        <Loader2 class="w-16 h-16 text-primary-500 animate-spin" />
        <Sun class="w-8 h-8 text-yellow-500 absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2" />
      </div>
      <div class="text-center">
        <h3 class="text-xl font-semibold text-white mb-2">Analyzing Sites</h3>
        <p class="text-sm text-gray-400">Recalculating suitability scores...</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Loader2, Sun } from 'lucide-vue-next';
</script>
