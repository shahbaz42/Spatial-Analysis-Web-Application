<template>
  <div ref="mapContainer" class="w-full h-full">
    <!-- Map will be rendered here -->
  </div>
  
  <!-- Map Controls Overlay -->
  <div class="absolute top-4 right-4 space-y-2">
    <button
      @click="zoomIn"
      class="p-2 bg-white rounded-lg shadow-lg hover:bg-gray-50 transition-colors"
      title="Zoom In"
    >
      <Plus class="w-5 h-5 text-gray-700" />
    </button>
    <button
      @click="zoomOut"
      class="p-2 bg-white rounded-lg shadow-lg hover:bg-gray-50 transition-colors"
      title="Zoom Out"
    >
      <Minus class="w-5 h-5 text-gray-700" />
    </button>
    <button
      @click="resetView"
      class="p-2 bg-white rounded-lg shadow-lg hover:bg-gray-50 transition-colors"
      title="Reset View"
    >
      <Home class="w-5 h-5 text-gray-700" />
    </button>
  </div>

  <!-- Site Detail Popup -->
  <div
    v-if="siteStore.selectedSite && popupPosition"
    class="absolute bg-white rounded-lg shadow-xl p-4 w-72 z-10"
    :style="{
      left: `${popupPosition.x}px`,
      top: `${popupPosition.y}px`,
      transform: 'translate(-50%, -100%) translateY(-10px)'
    }"
  >
    <button
      @click="closePopup"
      class="absolute top-2 right-2 p-1 hover:bg-gray-100 rounded"
    >
      <X class="w-4 h-4 text-gray-500" />
    </button>
    
    <SitePopup :site="siteStore.selectedSite" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, computed } from 'vue';
import mapboxgl from 'mapbox-gl';
import { Plus, Minus, Home, X } from 'lucide-vue-next';
import { useSiteStore } from '@/stores/siteStore';
import { MAPBOX_TOKEN, DEFAULT_MAP_CENTER, DEFAULT_MAP_ZOOM, getScoreColor } from '@/config';
import SitePopup from '@/components/SitePopup.vue';
import type { Site } from '@/types';

const siteStore = useSiteStore();
const mapContainer = ref<HTMLDivElement>();
const map = ref<mapboxgl.Map>();
const markers = ref<Map<number, mapboxgl.Marker>>(new Map());
const popupPosition = ref<{ x: number; y: number } | null>(null);

onMounted(() => {
  if (!MAPBOX_TOKEN) {
    console.error('Mapbox token is not configured. Please set VITE_MAPBOX_TOKEN in .env file');
    return;
  }

  mapboxgl.accessToken = MAPBOX_TOKEN;

  map.value = new mapboxgl.Map({
    container: mapContainer.value!,
    style: 'mapbox://styles/mapbox/dark-v11',
    center: DEFAULT_MAP_CENTER,
    zoom: DEFAULT_MAP_ZOOM,
  });

  map.value.addControl(new mapboxgl.NavigationControl(), 'top-left');
  
  // Update markers when sites change
  watch(() => siteStore.filteredSites, updateMarkers, { immediate: true, deep: true });
  
  // Watch selected site to center map
  watch(() => siteStore.selectedSite, (site) => {
    if (site && map.value) {
      map.value.flyTo({
        center: [site.longitude, site.latitude],
        zoom: 12,
        duration: 1000,
      });
      updatePopupPosition(site);
    } else {
      popupPosition.value = null;
    }
  });
});

onUnmounted(() => {
  map.value?.remove();
});

function updateMarkers(sites: Site[]) {
  if (!map.value) return;

  // Remove old markers
  markers.value.forEach((marker) => marker.remove());
  markers.value.clear();

  // Add new markers
  sites.forEach((site) => {
    const score = site.total_suitability_score ?? 0;
    const color = getScoreColor(score);

    // Create custom marker element
    const el = document.createElement('div');
    el.className = 'custom-marker';
    el.style.width = '24px';
    el.style.height = '24px';
    el.style.borderRadius = '50%';
    el.style.backgroundColor = color;
    el.style.border = '2px solid white';
    el.style.cursor = 'pointer';
    el.style.boxShadow = '0 2px 4px rgba(0,0,0,0.3)';
    el.style.transition = 'transform 0.2s';

    // Add hover effect
    el.addEventListener('mouseenter', () => {
      el.style.transform = 'scale(1.2)';
    });
    el.addEventListener('mouseleave', () => {
      el.style.transform = 'scale(1)';
    });

    // Highlight selected site
    if (siteStore.selectedSite?.site_id === site.site_id) {
      el.style.transform = 'scale(1.5)';
      el.style.border = '3px solid #fbbf24';
      el.style.boxShadow = '0 0 20px rgba(251, 191, 36, 0.6)';
    }

    const marker = new mapboxgl.Marker(el)
      .setLngLat([site.longitude, site.latitude])
      .addTo(map.value!);

    el.addEventListener('click', () => {
      siteStore.selectSite(site);
    });

    markers.value.set(site.site_id, marker);
  });
}

function updatePopupPosition(site: Site) {
  if (!map.value) return;
  
  const point = map.value.project([site.longitude, site.latitude]);
  popupPosition.value = {
    x: point.x,
    y: point.y,
  };
}

function zoomIn() {
  map.value?.zoomIn();
}

function zoomOut() {
  map.value?.zoomOut();
}

function resetView() {
  map.value?.flyTo({
    center: DEFAULT_MAP_CENTER,
    zoom: DEFAULT_MAP_ZOOM,
    duration: 1000,
  });
  siteStore.selectSite(null);
}

function closePopup() {
  siteStore.selectSite(null);
  popupPosition.value = null;
}
</script>

<style scoped>
:deep(.mapboxgl-ctrl-logo) {
  display: none !important;
}
</style>
