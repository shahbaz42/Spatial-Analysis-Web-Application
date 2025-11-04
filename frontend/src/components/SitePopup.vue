<template>
  <div class="space-y-3">
    <div>
      <h3 class="font-bold text-lg text-gray-900">{{ site.site_name }}</h3>
      <p class="text-sm text-gray-500">{{ site.region }} • {{ site.land_type }}</p>
    </div>

    <div v-if="site.total_suitability_score !== null" class="space-y-2">
      <div class="flex items-center justify-between">
        <span class="text-sm font-medium text-gray-700">Suitability Score</span>
        <div class="flex items-center space-x-2">
          <span class="text-2xl font-bold" :style="{ color: scoreColor }">
            {{ site.total_suitability_score.toFixed(1) }}
          </span>
          <span class="text-xs px-2 py-1 rounded-full font-medium" :style="{
            backgroundColor: scoreColor + '20',
            color: scoreColor
          }">
            {{ scoreLabel }}
          </span>
        </div>
      </div>

      <!-- Score Bar -->
      <div class="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
        <div
          class="h-full transition-all duration-300"
          :style="{
            width: `${site.total_suitability_score}%`,
            backgroundColor: scoreColor
          }"
        ></div>
      </div>
    </div>

    <!-- Additional Details -->
    <div v-if="siteStore.selectedSiteDetail" class="grid grid-cols-2 gap-2 pt-2 border-t border-gray-200">
      <DetailItem
        label="Area"
        :value="`${formatNumber(siteStore.selectedSiteDetail.area_sqm)} m²`"
        :icon="Maximize"
      />
      <DetailItem
        label="Solar"
        :value="`${formatNumber(siteStore.selectedSiteDetail.solar_irradiance_kwh)} kWh`"
        :icon="Sun"
      />
      <DetailItem
        label="Grid"
        :value="`${siteStore.selectedSiteDetail.grid_distance_km.toFixed(1)} km`"
        :icon="Zap"
      />
      <DetailItem
        label="Slope"
        :value="`${siteStore.selectedSiteDetail.slope_degrees.toFixed(1)}°`"
        :icon="Mountain"
      />
    </div>

    <div class="flex items-center space-x-2 pt-2 text-xs text-gray-500">
      <MapPin class="w-3 h-3" />
      <span>{{ site.latitude.toFixed(4) }}, {{ site.longitude.toFixed(4) }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { MapPin, Sun, Maximize, Zap, Mountain } from 'lucide-vue-next';
import { useSiteStore } from '@/stores/siteStore';
import { getScoreColor, getScoreLabel } from '@/config';
import DetailItem from '@/components/DetailItem.vue';
import type { Site } from '@/types';

interface Props {
  site: Site;
}

const props = defineProps<Props>();
const siteStore = useSiteStore();

const scoreColor = computed(() => getScoreColor(props.site.total_suitability_score));
const scoreLabel = computed(() => getScoreLabel(props.site.total_suitability_score));

function formatNumber(num: number): string {
  return new Intl.NumberFormat('en-US').format(num);
}
</script>
