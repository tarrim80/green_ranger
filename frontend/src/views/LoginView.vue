<template>
  <v-container class="fill-height">
    <v-row align="center" justify="center">
      <v-col cols="12" sm="8" md="4">
        <v-form @submit.prevent="handleLogin">
          <v-card class="elevation-12">
            <v-toolbar color="primary" dark flat>
              <v-toolbar-title>Вход в систему</v-toolbar-title>
            </v-toolbar>
            <v-card-text>
              <v-text-field
                v-model="email"
                label="Email"
                name="login"
                prepend-icon="mdi-account"
                type="text"
                required
              ></v-text-field>
              <v-text-field
                v-model="password"
                id="password"
                label="Пароль"
                name="password"
                prepend-icon="mdi-lock"
                type="password"
                required
              ></v-text-field>
            </v-card-text>
            <v-card-actions>
              <v-btn to="/register" variant="text">Создать аккаунт</v-btn>
              <v-spacer></v-spacer>
              <v-btn color="primary" type="submit">Войти</v-btn>
            </v-card-actions>
          </v-card>
        </v-form>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref } from 'vue';
import { useAuthStore } from '@/stores/auth';

const email = ref('');
const password = ref('');
const authStore = useAuthStore();

const handleLogin = () => {
  authStore.login({ email: email.value, password: password.value });
};
</script>
