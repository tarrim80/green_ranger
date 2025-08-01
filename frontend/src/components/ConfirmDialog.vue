<template>
  <v-dialog v-model="uiStore.isConfirmDialogOpen" @update:model-value="uiStore.triggerCancel" persistent max-width="500px">
    <v-card>
      <v-card-title class="text-h5">{{ uiStore.confirmDialogTitle }}</v-card-title>
      <v-card-text>{{ uiStore.confirmDialogText }}</v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn variant="text" @click="uiStore.triggerCancel">Отмена</v-btn>
        <v-btn color="primary" variant="flat" @click="uiStore.triggerConfirm">Подтвердить</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { useUiStore } from '@/stores/uiStore';
const uiStore = useUiStore();
</script>
