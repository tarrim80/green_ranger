<template>
  <v-app>
    <router-view />
    <side-panel-form-layout v-if="uiStore.isPanelOpen" />
  </v-app>
</template>

<script setup>
import SidePanelFormLayout from "@/components/layouts/SidePanelFormLayout.vue";
import { useUiStore } from "@/stores/uiStore";
const uiStore = useUiStore();
</script>
