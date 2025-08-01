<template>
  <v-app-bar app color="primary" height="48">
    <v-app-bar-title>Зелёный Рейнджер</v-app-bar-title>

    <v-spacer></v-spacer>

    <v-btn v-if="!authStore.isAuthenticated" to="/login">
      Войти
    </v-btn>

    <template v-else>
      <span>Привет, Пользователь!</span>
      <v-btn @click="authStore.logout()">
        Выйти
      </v-btn>
    </template>
  </v-app-bar>

  <v-main>
    <router-view v-if="$route.name === 'Map'" />
    <v-container v-else fluid>
      <router-view />
    </v-container>
  </v-main>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth';
const authStore = useAuthStore();
</script>
