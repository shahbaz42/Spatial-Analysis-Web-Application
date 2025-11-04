<template>
  <header
    class="bg-gray-800 h-auto border-b border-gray-700 px-6 py-4 flex flex-wrap items-center justify-between gap-y-3 sm:h-20"
  >
    <!-- Left Section -->
    <div class="flex items-center space-x-5">
      <Sun class="w-6 h-6 text-primary-500" />
      <div>
        <h1 class="text-2xl font-bold text-white">Solar Site Analyzer</h1>
        <p class="text-sm text-gray-400">
          Identify optimal locations for solar installations
        </p>
      </div>
    </div>

    <!-- Right Section (Stats Summary) -->
    <div
      v-if="siteStore.statistics"
      class="flex flex-wrap items-center gap-x-6 gap-y-2 text-sm mt-3 sm:mt-0"
    >
      <div class="flex items-center space-x-2">
        <MapPin class="w-4 h-4 text-gray-400" />
        <span class="text-gray-300">
          <strong class="text-white">{{ siteStore.totalSites }}</strong> Sites
        </span>
      </div>
      <div class="flex items-center space-x-2">
        <TrendingUp class="w-4 h-4 text-gray-400" />
        <span class="text-gray-300">
          Avg Score:
          <strong class="text-white">{{
            siteStore.statistics.average_score.toFixed(1)
          }}</strong>
        </span>
      </div>
      <div class="flex items-center space-x-2">
        <Target class="w-4 h-4 text-gray-400" />
        <span class="text-gray-300">
          <strong class="text-white">{{ siteStore.analyzedSites }}</strong> Analyzed
        </span>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { Sun, MapPin, TrendingUp, Target } from 'lucide-vue-next'
import { useSiteStore } from '@/stores/siteStore'

const siteStore = useSiteStore()
</script>
