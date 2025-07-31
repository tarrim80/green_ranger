<template>
  <v-navigation-drawer
    v-model="uiStore.isPanelOpen"
    location="right"
    :width="panelWidth"
  >
    <v-toolbar color="primary">
      <v-toolbar-title>{{ uiStore.panelTitle }}</v-toolbar-title>
      <v-spacer></v-spacer>
      <v-btn icon @click="uiStore.closePanel">
        <v-icon>mdi-close</v-icon>
      </v-btn>
    </v-toolbar>

    <v-sheet class="pa-4">
      <component
        :is="uiStore.panelComponent"
        v-if="uiStore.panelComponent"
        v-bind="uiStore.panelProps"
      />
    </v-sheet>
  </v-navigation-drawer>
</template>

<script setup>
import { computed } from 'vue';
import { useUiStore } from "@/stores/uiStore";
const uiStore = useUiStore();

const panelWidth = computed(() => {
  return window.innerWidth * 0.32;
});
</script>
