<template>
  <div v-if="authStore.isAuthenticated">
    <v-list nav density="compact">
      <v-list-item
        prepend-icon="mdi-map-outline"
        title="Карта"
        to="/"
        exact
      ></v-list-item>
    </v-list>
  </div>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth';
const authStore = useAuthStore();
</script>
