<template>
  <v-layout>
    <v-navigation-drawer v-if="authStore.isAuthenticated" permanent>
      <v-list-item
        v-if="authStore.currentUser"
        :title="authStore.currentUser.fullname"
        :subtitle="authStore.currentUser.role"
      ></v-list-item>
      <v-divider></v-divider>
      
      <router-view name="sidebar"></router-view>
      
    </v-navigation-drawer>

    <v-app-bar color="primary" height="48">
      <v-app-bar-title>Зелёный Рейнджер</v-app-bar-title>
      <v-spacer></v-spacer>
      <v-btn v-if="!authStore.isAuthenticated" to="/login">Войти</v-btn>
      <v-btn v-else @click="authStore.logout()">Выйти</v-btn>
    </v-app-bar>

    <v-main style="height: 100vh;">
      <router-view />
    </v-main>
  </v-layout>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth';
const authStore = useAuthStore();
</script>
