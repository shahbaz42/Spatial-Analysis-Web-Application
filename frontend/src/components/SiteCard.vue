<template>
  <div
    :data-site-id="site.site_id"
    class="flex-shrink-0 w-64 bg-gray-700 rounded-lg p-4 cursor-pointer transition-all duration-200 hover:bg-gray-600 border-2"
    :class="isSelected ? 'border-primary-500 shadow-lg shadow-primary-500/20' : 'border-transparent'"
    @click="$emit('click')"
  >
    <div class="flex flex-col h-full space-y-2">
      <!-- Header -->
      <div class="flex items-start justify-between">
        <div class="flex-1 min-w-0">
          <h4 class="font-semibold text-white text-sm truncate">{{ site.site_name }}</h4>
          <p class="text-xs text-gray-400 truncate">{{ site.region }}</p>
        </div>
        <div
          v-if="site.total_suitability_score !== null"
          class="flex-shrink-0 ml-2"
        >
          <div
            class="w-12 h-12 rounded-full flex items-center justify-center font-bold text-sm border-2"
            :style="{
              backgroundColor: scoreColor + '20',
              borderColor: scoreColor,
              color: scoreColor
            }"
          >
            {{ site.total_suitability_score.toFixed(0) }}
          </div>
        </div>
      </div>

      <!-- Score Label -->
      <div
        v-if="site.total_suitability_score !== null"
        class="text-xs px-2 py-1 rounded font-medium inline-block self-start"
        :style="{
          backgroundColor: scoreColor + '20',
          color: scoreColor
        }"
      >
        {{ scoreLabel }}
      </div>

      <!-- Details -->
      <div class="flex-1 grid grid-cols-2 gap-2 text-xs">
        <div class="flex items-center space-x-1 text-gray-300">
          <MapPin class="w-3 h-3 text-gray-500" />
          <span>{{ site.land_type }}</span>
        </div>
        <div class="flex items-center space-x-1 text-gray-300">
          <Calendar class="w-3 h-3 text-gray-500" />
          <span v-if="site.analysis_timestamp">
            {{ formatDate(site.analysis_timestamp) }}
          </span>
          <span v-else class="text-gray-500">Not analyzed</span>
        </div>
      </div>

      <!-- Selection Indicator -->
      <div v-if="isSelected" class="flex items-center space-x-1 text-primary-500 text-xs font-medium">
        <MapPin class="w-3 h-3" />
        <span>Selected on map</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { MapPin, Calendar } from 'lucide-vue-next';
import { getScoreColor, getScoreLabel } from '@/config';
import { format } from 'date-fns';
import type { Site } from '@/types';

interface Props {
  site: Site;
  isSelected: boolean;
}

const props = defineProps<Props>();

defineEmits<{
  click: [];
}>();

const scoreColor = computed(() => getScoreColor(props.site.total_suitability_score));
const scoreLabel = computed(() => getScoreLabel(props.site.total_suitability_score));

function formatDate(dateString: string): string {
  try {
    return format(new Date(dateString), 'MMM d');
  } catch {
    return 'N/A';
  }
}
</script>
