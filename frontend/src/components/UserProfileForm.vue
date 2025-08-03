<template>
  <v-form ref="form" @submit.prevent="saveProfile">
    <v-container>
      <v-row>
        <v-col cols="12" class="py-2">
          <v-text-field
            v-model="formData.firstname"
            label="Имя"
            :rules="[rules.required]"
            density="compact"
            hide-details="auto"
            variant="outlined"
            required
          ></v-text-field>
        </v-col>
        <v-col cols="12" class="py-2">
          <v-text-field
            v-model="formData.lastname"
            label="Фамилия"
            :rules="[rules.required]"
            density="compact"
            hide-details="auto"
            variant="outlined"
            required
          ></v-text-field>
        </v-col>
        <v-col cols="12" class="py-2">
           <v-text-field
            :model-value="authStore.currentUser.email"
            label="Email"
            density="compact"
            hide-details="auto"
            variant="outlined"
            readonly
            disabled
          ></v-text-field>
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="12" class="d-flex justify-center">
            <v-btn variant="tonal" @click="uiStore.openChangePasswordDialog" class="mr-2">Сменить пароль</v-btn>
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="12" class="d-flex justify-end">
            <v-btn variant="text" @click="emit('close')">Отмена</v-btn>
            <v-btn color="primary" type="submit" :loading="loading">Сохранить</v-btn>
        </v-col>
      </v-row>
    </v-container>
  </v-form>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { useUiStore } from '@/stores/uiStore';

const emit = defineEmits(['close']);

const authStore = useAuthStore();
const uiStore = useUiStore();
const form = ref(null);
const loading = ref(false);

const formData = ref({
  firstname: '',
  lastname: '',
});

const rules = {
  required: (v) => !!v || "Поле обязательно для заполнения.",
};

onMounted(() => {
  if (authStore.currentUser) {
    formData.value.firstname = authStore.currentUser.firstname;
    formData.value.lastname = authStore.currentUser.lastname;
  }
});

const saveProfile = async () => {
  if (!form.value) return;
  const { valid } = await form.value.validate();
  if (!valid) return;

  loading.value = true;
  try {
    await authStore.updateUserProfile(formData.value);
    uiStore.showInfoDialog("Успех", "Данные профиля обновлены.");
    emit('close');
  } catch (error) {
    const errorDetail = error.response?.data?.detail || "Произошла ошибка при обновлении профиля.";
    uiStore.showInfoDialog("Ошибка", errorDetail);
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
:deep(.v-field__input) {
  font-size: 0.875rem !important;
}
:deep(.v-label.v-field-label) {
  font-size: 0.875rem !important;
}
</style>
