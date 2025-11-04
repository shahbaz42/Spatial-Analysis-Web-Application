<template>
  <Transition name="slide-up">
    <div
      v-if="siteStore.error"
      class="fixed bottom-6 right-6 bg-red-600 text-white rounded-lg shadow-2xl p-4 max-w-md z-50"
    >
      <div class="flex items-start space-x-3">
        <AlertCircle class="w-5 h-5 flex-shrink-0 mt-0.5" />
        <div class="flex-1 min-w-0">
          <h4 class="font-semibold mb-1">Error</h4>
          <p class="text-sm opacity-90">{{ siteStore.error }}</p>
        </div>
        <button
          @click="siteStore.clearError"
          class="flex-shrink-0 p-1 hover:bg-red-700 rounded transition-colors"
        >
          <X class="w-4 h-4" />
        </button>
      </div>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { watch } from 'vue';
import { AlertCircle, X } from 'lucide-vue-next';
import { useSiteStore } from '@/stores/siteStore';

const siteStore = useSiteStore();

// Auto-dismiss error after 5 seconds
watch(() => siteStore.error, (error) => {
  if (error) {
    setTimeout(() => {
      siteStore.clearError();
    }, 5000);
  }
});
</script>

<style scoped>
.slide-up-enter-active,
.slide-up-leave-active {
  transition: all 0.3s ease;
}

.slide-up-enter-from {
  transform: translateY(100%);
  opacity: 0;
}

.slide-up-leave-to {
  transform: translateY(100%);
  opacity: 0;
}
</style>
