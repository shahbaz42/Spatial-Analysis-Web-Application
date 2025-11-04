<template>
  <div ref="mapContainer" class="w-full h-full">
    <!-- Map will be rendered here -->
  </div>
  
  <!-- Map Controls Overlay -->
  <div class="absolute top-4 right-4 space-y-2">
    <button
    @click="zoomIn"
    class="p-2 bg-white hover:bg-gray-50 transition-colors rounded-l-lg border-r border-gray-200"
    title="Zoom In"
  >
    <Plus class="w-5 h-5 text-gray-700" />
  </button>

  <button
    @click="zoomOut"
    class="p-2 bg-white hover:bg-gray-50 transition-colors border-r border-gray-200"
    title="Zoom Out"
  >
    <Minus class="w-5 h-5 text-gray-700" />
  </button>

  <button
    @click="resetView"
    class="p-2 bg-white hover:bg-gray-50 transition-colors rounded-r-lg"
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
import { ref, onMounted, onUnmounted, watch } from 'vue';
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
let popupUpdateInterval: number | null = null;

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

  // map.value.addControl(new mapboxgl.NavigationControl(), 'top-left');
  
  // Update popup position during map movement
  map.value.on('move', () => {
    if (siteStore.selectedSite) {
      updatePopupPosition(siteStore.selectedSite);
    }
  });
  
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
  if (popupUpdateInterval) {
    clearInterval(popupUpdateInterval);
  }
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
    const isSelected = siteStore.selectedSite?.site_id === site.site_id;

    // Create wrapper for proper positioning
    const wrapper = document.createElement('div');
    wrapper.className = 'marker-wrapper';
    wrapper.style.position = 'relative';
    
    // Create inner marker element that can scale
    const el = document.createElement('div');
    el.className = 'custom-marker';
    el.style.width = isSelected ? '36px' : '24px';
    el.style.height = isSelected ? '36px' : '24px';
    el.style.borderRadius = '50%';
    el.style.backgroundColor = color;
    el.style.border = isSelected ? '3px solid #fbbf24' : '2px solid white';
    el.style.cursor = 'pointer';
    el.style.boxShadow = isSelected ? '0 0 20px rgba(251, 191, 36, 0.6)' : '0 2px 4px rgba(0,0,0,0.3)';
    el.style.transition = 'width 0.2s, height 0.2s, border 0.2s, box-shadow 0.2s';
    el.style.position = 'absolute';
    el.style.top = '50%';
    el.style.left = '50%';
    el.style.transform = 'translate(-50%, -50%)';
    el.style.willChange = 'width, height';

    // Add hover effect - only change size, not transform
    el.addEventListener('mouseenter', () => {
      if (!isSelected) {
        el.style.width = '28px';
        el.style.height = '28px';
      }
    });
    el.addEventListener('mouseleave', () => {
      if (!isSelected) {
        el.style.width = '24px';
        el.style.height = '24px';
      }
    });

    wrapper.appendChild(el);

    const marker = new mapboxgl.Marker({
      element: wrapper,
      anchor: 'center'
    })
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
