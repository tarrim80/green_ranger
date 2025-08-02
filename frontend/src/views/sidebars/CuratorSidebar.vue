<template>
  <v-list nav density="compact">
    <v-list-item
      prepend-icon="mdi-map-outline"
      title="Обзорная карта"
      to="/"
      exact
    ></v-list-item>
    <v-list-item
      prepend-icon="mdi-map-marker-path"
      title="Управление участками"
      to="/sectors"
    ></v-list-item>
    <v-list-item
      prepend-icon="mdi-checkbox-marked-circle-outline"
      title="На проверку"
      to="/review"
    ></v-list-item>
  </v-list>
</template>

<script setup>
</script>
