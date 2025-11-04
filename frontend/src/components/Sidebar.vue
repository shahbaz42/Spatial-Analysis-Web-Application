<template>
  <aside class="w-80 bg-gray-800 border-r border-gray-700 flex flex-col overflow-hidden">
    <!-- Sidebar Header -->
    <div class="px-6 py-4 border-b border-gray-700">
      <h2 class="text-lg font-semibold text-white flex items-center space-x-2">
        <Sliders class="w-5 h-5" />
        <span>Analysis Controls</span>
      </h2>
    </div>

    <!-- Scrollable Content -->
    <div class="flex-1 overflow-y-auto px-6 py-4 space-y-6">
      <!-- Weights Section -->
      <section>
        <h3 class="text-sm font-semibold text-gray-300 mb-3 flex items-center space-x-2">
          <Weight class="w-4 h-4" />
          <span>Factor Weights</span>
        </h3>

        <div class="space-y-4">
          <WeightSlider
            label="Solar Irradiance"
            :icon="Sun"
            v-model="localWeights.solar"
            color="text-yellow-500"
          />
          <WeightSlider
            label="Available Area"
            :icon="Maximize"
            v-model="localWeights.area"
            color="text-blue-500"
          />
          <WeightSlider
            label="Grid Distance"
            :icon="Zap"
            v-model="localWeights.grid_distance"
            color="text-green-500"
          />
          <WeightSlider
            label="Terrain Slope"
            :icon="Mountain"
            v-model="localWeights.slope"
            color="text-purple-500"
          />
          <WeightSlider
            label="Infrastructure"
            :icon="Building"
            v-model="localWeights.infrastructure"
            color="text-orange-500"
          />
        </div>

        <!-- Weight Sum Validation -->
        <div class="mt-4 p-3 rounded-lg" :class="weightSumClass">
          <div class="flex items-center justify-between text-sm">
            <span class="font-medium">Total Weight:</span>
            <span class="font-bold">{{ weightSum.toFixed(2) }}</span>
          </div>
          <div v-if="!isWeightSumValid" class="mt-1 text-xs">
            Weights must sum to 1.00
          </div>
        </div>

        <!-- Action Buttons -->
        <div class="mt-4 space-y-2">
          <button
            @click="applyWeights"
            :disabled="!isWeightSumValid || siteStore.analyzing"
            class="w-full px-4 py-2 bg-primary-600 hover:bg-primary-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white font-medium rounded-lg transition-colors flex items-center justify-center space-x-2"
          >
            <RefreshCw class="w-4 h-4" :class="{ 'animate-spin': siteStore.analyzing }" />
            <span>{{ siteStore.analyzing ? 'Analyzing...' : 'Recalculate Scores' }}</span>
          </button>

          <button
            @click="resetToDefaults"
            class="w-full px-4 py-2 bg-gray-700 hover:bg-gray-600 text-gray-200 font-medium rounded-lg transition-colors flex items-center justify-center space-x-2"
          >
            <RotateCcw class="w-4 h-4" />
            <span>Reset to Defaults</span>
          </button>
        </div>
      </section>

      <!-- Filters Section -->
      <section class="pt-6 border-t border-gray-700">
        <h3 class="text-sm font-semibold text-gray-300 mb-3 flex items-center space-x-2">
          <Filter class="w-4 h-4" />
          <span>Score Filters</span>
        </h3>

        <div class="space-y-4">
          <RangeSlider
            label="Score Range"
            :icon="Sliders"
            :min="0"
            :max="100"
            :step="1"
            v-model="scoreRange"
            color="text-blue-400"
          />

          <button
            @click="resetFilters"
            class="w-full px-4 py-2 bg-gray-700 hover:bg-gray-600 text-gray-200 font-medium rounded-lg transition-colors flex items-center justify-center space-x-2"
          >
            <X class="w-4 h-4" />
            <span>Clear Filters</span>
          </button>
        </div>
      </section>

      <!-- Filtered Results Info -->
      <section class="p-4 bg-gray-700 rounded-lg">
        <div class="flex items-center justify-between text-sm">
          <span class="text-gray-300">Showing:</span>
          <span class="font-bold text-white">{{ siteStore.filteredSites.length }} sites</span>
        </div>
      </section>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import {
  Sliders,
  Weight,
  Sun,
  Maximize,
  Zap,
  Mountain,
  Building,
  RefreshCw,
  RotateCcw,
  Filter,
  X,
} from 'lucide-vue-next';
import { useSiteStore } from '@/stores/siteStore';
import { DEFAULT_WEIGHTS } from '@/config';
import WeightSlider from '@/components/WeightSlider.vue';
import RangeSlider from '@/components/RangeSlider.vue';
import type { AnalysisWeights } from '@/types';

const siteStore = useSiteStore();

const localWeights = ref<AnalysisWeights>({ ...siteStore.weights });

// Use the store filters to keep the dual range in sync
const scoreRange = ref<[number, number]>([
  siteStore.filters.minScore,
  siteStore.filters.maxScore,
]);

watch(scoreRange, (newVal) => {
  siteStore.filters.minScore = newVal[0];
  siteStore.filters.maxScore = newVal[1];
});

function resetFilters() {
  siteStore.resetFilters();
  scoreRange.value = [siteStore.filters.minScore, siteStore.filters.maxScore];
}

// Watch store filters and update slider when reset
watch(
  () => [siteStore.filters.minScore, siteStore.filters.maxScore],
  ([min, max]) => {
    scoreRange.value = [min, max];
  }
);

// Sync weights
watch(() => siteStore.weights, (newWeights) => {
  localWeights.value = { ...newWeights };
}, { deep: true });

const weightSum = computed(() =>
  Object.values(localWeights.value).reduce((sum, val) => sum + val, 0)
);

const isWeightSumValid = computed(() => Math.abs(weightSum.value - 1.0) < 0.01);

const weightSumClass = computed(() =>
  isWeightSumValid.value
    ? 'bg-green-900/30 border border-green-700 text-green-300'
    : 'bg-red-900/30 border border-red-700 text-red-300'
);

async function applyWeights() {
  try {
    await siteStore.analyzeSitesWithWeights(localWeights.value);
  } catch (error) {
    console.error('Failed to apply weights:', error);
  }
}

function resetToDefaults() {
  localWeights.value = { ...DEFAULT_WEIGHTS };
  siteStore.resetWeights();
}
</script>
