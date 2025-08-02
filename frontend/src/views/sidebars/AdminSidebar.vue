<template>
  <v-list nav density="compact">
    <v-list-item
      prepend-icon="mdi-map-outline"
      title="Участки"
      to="/"
      exact
    ></v-list-item>
    <v-list-item
      prepend-icon="mdi-account-group-outline"
      title="Команды"
      to="/teams"
    ></v-list-item>
    <v-list-item
      prepend-icon="mdi-account-multiple-outline"
      title="Пользователи"
      to="/users"
    ></v-list-item>
    <v-list-item
      prepend-icon="mdi-book-open-variant"
      title="Виды дефектов"
      to="/defect-types"
    ></v-list-item>
  </v-list>
</template>

<script setup>
</script>
