<template>
  <v-app>
    <router-view />
    <side-panel-form-layout v-if="uiStore.isPanelOpen" />
    <info-dialog />
    <confirm-dialog />
  </v-app>
</template>

<script setup>
import { onMounted, onBeforeUnmount } from 'vue';
import SidePanelFormLayout from "@/components/layouts/SidePanelFormLayout.vue";
import InfoDialog from "@/components/InfoDialog.vue";
import ConfirmDialog from "@/components/ConfirmDialog.vue";
import { useUiStore } from "@/stores/uiStore";

const uiStore = useUiStore();

const handleKeydown = (event) => {
  if (uiStore.isInfoDialogOpen) {
    if (event.key === 'Enter' || event.key === 'Escape') {
      uiStore.hideInfoDialog();
    }
    return;
  }

  if (uiStore.isConfirmDialogOpen) {
    if (event.key === 'Enter') {
      uiStore.triggerConfirm();
    } else if (event.key === 'Escape') {
      uiStore.triggerCancel();
    }
    return;
  }

  if (uiStore.isPanelOpen) {
    if (event.key === 'Escape') {
      uiStore.closePanel();
    }
  }
};

onMounted(() => {
  window.addEventListener('keydown', handleKeydown);
});

onBeforeUnmount(() => {
  window.removeEventListener('keydown', handleKeydown);
});
</script>

<style>
html {
  overflow-y: auto !important;
}
</style>
