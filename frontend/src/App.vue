<template>
  <div class="flex h-screen w-screen overflow-hidden bg-gray-900">
    <!-- Left Sidebar -->
    <Sidebar class="flex-shrink-0" />
    
    <!-- Main Content Area -->
    <div class="flex-1 flex flex-col relative">
      <!-- Header -->
      <Header />
      
      <!-- Map Container -->
      <div class="flex-1 relative">
        <MapView />
      </div>
      
      <!-- Bottom Site Cards -->
      <BottomSiteBar />
    </div>

    <!-- Loading Overlay -->
    <LoadingOverlay v-if="siteStore.analyzing" />

    <!-- Error Notification -->
    <ErrorNotification />
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue';
import { useSiteStore } from '@/stores/siteStore';
import Sidebar from '@/components/Sidebar.vue';
import Header from '@/components/Header.vue';
import MapView from '@/components/MapView.vue';
import BottomSiteBar from '@/components/BottomSiteBar.vue';
import LoadingOverlay from '@/components/LoadingOverlay.vue';
import ErrorNotification from '@/components/ErrorNotification.vue';

const siteStore = useSiteStore();

onMounted(async () => {
  // Load initial data
  try {
    await Promise.all([
      siteStore.fetchSites({ limit: 100 }),
      siteStore.fetchStatistics(),
    ]);
  } catch (error) {
    console.error('Failed to load initial data:', error);
  }
});
</script>
