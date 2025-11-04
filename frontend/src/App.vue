<template>
  <div class="flex h-screen w-screen overflow-hidden bg-gray-900">
    <!-- Mobile Backdrop -->
    <div 
      v-if="sidebarOpen" 
      class="fixed inset-0 bg-black/50 z-20 lg:hidden"
      @click="closeSidebar"
    ></div>

    <!-- Left Sidebar -->
    <Sidebar :is-open="sidebarOpen" @close="closeSidebar" class="flex-shrink-0" />
    
    <!-- Main Content Area -->
    <div class="flex-1 flex flex-col relative">
      <!-- Hamburger Menu Button (Mobile) -->
      <button
        v-if="!sidebarOpen"
        @click="toggleSidebar"
        class="fixed top-4 left-4 z-30 lg:hidden p-2 bg-gray-800 hover:bg-gray-700 rounded-lg shadow-lg transition-colors"
      >
        <Menu class="w-6 h-6 text-white" />
      </button>

      <!-- Header -->
      <Header />
      
      <!-- Map Container -->
      <div class="flex-1 relative">
        <MapView />
      </div>
      
      <!-- Bottom Site Cards -->
      <div class="absolute bottom-0 left-0 right-0 z-20">
        <BottomSiteBar />
      </div>
    </div>

    <!-- Loading Overlay -->
    <LoadingOverlay v-if="siteStore.analyzing" />

    <!-- Error Notification -->
    <ErrorNotification />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { Menu } from 'lucide-vue-next';
import { useSiteStore } from '@/stores/siteStore';
import Sidebar from '@/components/Sidebar.vue';
import Header from '@/components/Header.vue';
import MapView from '@/components/MapView.vue';
import BottomSiteBar from '@/components/BottomSiteBar.vue';
import LoadingOverlay from '@/components/LoadingOverlay.vue';
import ErrorNotification from '@/components/ErrorNotification.vue';

const siteStore = useSiteStore();
const sidebarOpen = ref(false);

function toggleSidebar() {
  sidebarOpen.value = !sidebarOpen.value;
}

function closeSidebar() {
  sidebarOpen.value = false;
}

onMounted(async () => {
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
