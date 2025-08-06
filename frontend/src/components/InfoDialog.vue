<template>
  <v-dialog v-model="uiStore.isInfoDialogOpen" @update:model-value="uiStore.hideInfoDialog" persistent max-width="500px">
    <v-card>
      <v-card-title class="text-h5">{{ uiStore.infoDialogTitle }}</v-card-title>
      <v-card-text>{{ uiStore.infoDialogText }}</v-card-text>
      <v-card-actions class="px-4">
        <v-spacer></v-spacer>
        <v-btn color="primary" variant="flat" @click="uiStore.hideInfoDialog">ОК</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { useUiStore } from '@/stores/uiStore';
const uiStore = useUiStore();
</script>
