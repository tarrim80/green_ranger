<template>
  <v-container class="fill-height">
    <v-row align="center" justify="center">
      <v-col cols="12" sm="8" md="5">
        <v-form ref="form" @submit.prevent="handleRegister">
          <v-card class="elevation-12">
            <v-toolbar color="primary" dark flat>
              <v-toolbar-title>Регистрация</v-toolbar-title>
            </v-toolbar>
            <v-card-text>
              <v-text-field
                v-model="formData.email"
                label="Email"
                prepend-icon="mdi-email"
                type="email"
                :rules="[rules.required, rules.email]"
                required
              ></v-text-field>
              <v-text-field
                v-model="formData.firstname"
                label="Имя"
                prepend-icon="mdi-account"
                type="text"
                :rules="[rules.required]"
                required
              ></v-text-field>
              <v-text-field
                v-model="formData.lastname"
                label="Фамилия"
                prepend-icon="mdi-account-outline"
                type="text"
                :rules="[rules.required]"
                required
              ></v-text-field>
              <v-text-field
                v-model="formData.password"
                label="Пароль"
                prepend-icon="mdi-lock"
                type="password"
                :rules="[rules.required, rules.passwordLength]"
                required
              ></v-text-field>
              <v-text-field
                v-model="formData.passwordConfirm"
                label="Подтвердите пароль"
                prepend-icon="mdi-lock-check"
                type="password"
                :rules="[rules.required, rules.passwordMatch]"
                required
              ></v-text-field>
            </v-card-text>
            <v-card-actions>
              <v-btn to="/login" variant="text">Уже есть аккаунт?</v-btn>
              <v-spacer></v-spacer>
              <v-btn color="primary" type="submit">Зарегистрироваться</v-btn>
            </v-card-actions>
          </v-card>
        </v-form>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, watch } from 'vue';
import { useAuthStore } from '@/stores/auth';

const authStore = useAuthStore();
const form = ref(null);
const formData = ref({
  email: '',
  firstname: '',
  lastname: '',
  password: '',
  passwordConfirm: '',
});

const rules = {
  required: value => !!value || 'Поле обязательно для заполнения.',
  passwordLength: value => value.length >= 3 || 'Пароль должен быть не менее 3 символов.',
  email: value => /.+@.+\..+/.test(value) || 'E-mail должен быть валидным.',
  passwordMatch: value => value === formData.value.password || 'Пароли не совпадают.',
};

watch(() => formData.value.password, () => {
  if (form.value) {
    form.value.validate();
  }
});

const handleRegister = async () => {
    if (!form.value) return;
    const { valid } = await form.value.validate();
    if (!valid) return;

    await authStore.register({
        email: formData.value.email,
        password: formData.value.password,
        firstname: formData.value.firstname,
        lastname: formData.value.lastname,
    });
};
</script>
