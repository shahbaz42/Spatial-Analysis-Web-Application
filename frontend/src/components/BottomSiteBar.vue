<template>
  <div class="h-48 bg-gray-800 border-t border-gray-700 overflow-hidden flex flex-col">
    <!-- Header -->
    <div class="px-6 py-3 border-b border-gray-700 flex items-center justify-between">
      <div class="flex items-center space-x-3">
        <Layers class="w-5 h-5 text-gray-400" />
        <h3 class="text-sm font-semibold text-white">
          Top Sites ({{ siteStore.sortedSites.length }})
        </h3>
      </div>
      
      <div class="flex items-center space-x-2">
        <button
          @click="scrollLeft"
          class="p-1 hover:bg-gray-700 rounded transition-colors"
          :disabled="!canScrollLeft"
          :class="{ 'opacity-50 cursor-not-allowed': !canScrollLeft }"
        >
          <ChevronLeft class="w-5 h-5 text-gray-400" />
        </button>
        <button
          @click="scrollRight"
          class="p-1 hover:bg-gray-700 rounded transition-colors"
          :disabled="!canScrollRight"
          :class="{ 'opacity-50 cursor-not-allowed': !canScrollRight }"
        >
          <ChevronRight class="w-5 h-5 text-gray-400" />
        </button>
      </div>
    </div>

    <!-- Scrollable Cards Container -->
    <div
      ref="scrollContainer"
      class="flex-1 overflow-x-auto overflow-y-hidden px-6 py-4"
      @scroll="updateScrollState"
    >
      <div class="flex space-x-4 h-full">
        <SiteCard
          v-for="site in siteStore.sortedSites"
          :key="site.site_id"
          :site="site"
          :is-selected="siteStore.selectedSite?.site_id === site.site_id"
          @click="handleSiteClick(site)"
        />
        
        <!-- Empty State -->
        <div
          v-if="siteStore.sortedSites.length === 0"
          class="flex items-center justify-center w-full text-gray-500"
        >
          <div class="text-center">
            <Search class="w-12 h-12 mx-auto mb-2 opacity-50" />
            <p class="text-sm">No sites match the current filters</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';
import { Layers, ChevronLeft, ChevronRight, Search } from 'lucide-vue-next';
import { useSiteStore } from '@/stores/siteStore';
import SiteCard from '@/components/SiteCard.vue';
import type { Site } from '@/types';

const siteStore = useSiteStore();
const scrollContainer = ref<HTMLDivElement>();
const canScrollLeft = ref(false);
const canScrollRight = ref(false);

onMounted(() => {
  updateScrollState();
  window.addEventListener('resize', updateScrollState);
});

onUnmounted(() => {
  window.removeEventListener('resize', updateScrollState);
});

function updateScrollState() {
  if (!scrollContainer.value) return;
  
  const { scrollLeft, scrollWidth, clientWidth } = scrollContainer.value;
  canScrollLeft.value = scrollLeft > 0;
  canScrollRight.value = scrollLeft < scrollWidth - clientWidth - 1;
}

function scrollLeft() {
  if (!scrollContainer.value) return;
  scrollContainer.value.scrollBy({ left: -300, behavior: 'smooth' });
}

function scrollRight() {
  if (!scrollContainer.value) return;
  scrollContainer.value.scrollBy({ left: 300, behavior: 'smooth' });
}

function handleSiteClick(site: Site) {
  siteStore.selectSite(site);
  
  // Scroll selected card into view
  setTimeout(() => {
    const selectedCard = document.querySelector(`[data-site-id="${site.site_id}"]`);
    if (selectedCard && scrollContainer.value) {
      selectedCard.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' });
    }
  }, 100);
}
</script>

<style scoped>
/* Hide scrollbar but keep functionality */
div::-webkit-scrollbar {
  display: none;
}
div {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
</style>
