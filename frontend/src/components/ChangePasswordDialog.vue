<template>
  <v-dialog v-model="uiStore.isChangePasswordDialogOpen" @update:model-value="uiStore.closeChangePasswordDialog" persistent max-width="500px">
    <v-card>
      <v-card-title class="text-h5">Смена пароля</v-card-title>
      <v-form ref="form" @submit.prevent="handleChangePassword">
        <v-card-text>
          <v-text-field
            v-model="passwordData.current_password"
            label="Текущий пароль"
            type="password"
            :rules="[rules.required]"
            density="compact"
            variant="outlined"
            required
            class="mb-2"
          ></v-text-field>
          <v-text-field
            v-model="passwordData.new_password"
            label="Новый пароль"
            type="password"
            :rules="[rules.required, rules.passwordLength]"
            density="compact"
            variant="outlined"
            required
            class="mb-2"
          ></v-text-field>
          <v-text-field
            v-model="passwordData.new_password_confirm"
            label="Подтвердите новый пароль"
            type="password"
            :rules="[rules.required, rules.passwordMatch]"
            density="compact"
            variant="outlined"
            required
          ></v-text-field>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn variant="text" @click="uiStore.closeChangePasswordDialog">Отмена</v-btn>
          <v-btn color="primary" variant="flat" type="submit" :loading="loading">Сменить пароль</v-btn>
        </v-card-actions>
      </v-form>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { ref, reactive, watch } from 'vue';
import { useUiStore } from '@/stores/uiStore';
import { useAuthStore } from '@/stores/auth';

const uiStore = useUiStore();
const authStore = useAuthStore();
const form = ref(null);
const loading = ref(false);

const passwordData = reactive({
  current_password: '',
  new_password: '',
  new_password_confirm: '',
});

const rules = {
  required: (v) => !!v || 'Поле обязательно.',
  passwordLength: (v) => (v && v.length >= 3) || 'Пароль должен быть не менее 3 символов.',
  passwordMatch: (v) => v === passwordData.new_password || 'Пароли не совпадают.',
};

watch(() => uiStore.isChangePasswordDialogOpen, (isOpen) => {
  if (isOpen) {
    form.value?.reset();
    passwordData.current_password = '';
    passwordData.new_password = '';
    passwordData.new_password_confirm = '';
  }
});

const handleChangePassword = async () => {
  if (!form.value) return;
  const { valid } = await form.value.validate();
  if (!valid) return;

  loading.value = true;
  try {
    await authStore.changePassword({
      current_password: passwordData.current_password,
      new_password: passwordData.new_password,
    });
    uiStore.closeChangePasswordDialog();
    uiStore.showInfoDialog("Успех", "Пароль успешно изменен.");
  } catch (error) {
    const errorDetail = error.response?.data?.detail || "Произошла ошибка.";
    uiStore.showInfoDialog("Ошибка смены пароля", errorDetail);
  } finally {
    loading.value = false;
  }
};
</script>
