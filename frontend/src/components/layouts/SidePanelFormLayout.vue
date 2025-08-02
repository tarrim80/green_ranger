<template>
  <v-navigation-drawer
    v-model="uiStore.isPanelOpen"
    location="right"
    :width="panelWidth"
  >
    <v-list-item density="compact">
      <v-list-item-title>{{ uiStore.panelTitle }}</v-list-item-title>
      <template #append>
        <v-btn
          icon="mdi-close"
          variant="text"
          @click="uiStore.closePanel"
        ></v-btn>
      </template>
    </v-list-item>
    <v-divider></v-divider>

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
import { computed } from "vue";
import { useUiStore } from "@/stores/uiStore";
const uiStore = useUiStore();

const panelWidth = computed(() => {
  return window.innerWidth * 0.25;
});
</script>
