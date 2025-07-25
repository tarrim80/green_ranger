<!-- frontend-worktree/src/components/layouts/MainLayout.vue -->
<template>
  <v-app-bar app color="primary">
    <v-app-bar-title>Зелёный Рейнджер</v-app-bar-title>
    
    <v-spacer></v-spacer>

    <!-- Если пользователь НЕ залогинен -->
    <v-btn v-if="!authStore.isAuthenticated" to="/login">
      Войти
    </v-btn>

    <!-- Если пользователь залогинен -->
    <template v-else>
      <span>Привет, Пользователь!</span> <!-- Позже здесь будет имя -->
      <v-btn @click="authStore.logout()">
        Выйти
      </v-btn>
    </template>
  </v-app-bar>

  <v-main>
    <v-container>
      <router-view />
    </v-container>
  </v-main>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth';
const authStore = useAuthStore();
</script>
