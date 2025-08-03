<template>
  <v-form ref="form" @submit.prevent="saveUser">
    <v-container>
      <v-row>
        <v-col cols="12" class="py-2">
          <v-text-field
            :model-value="props.userData.fullname"
            label="Пользователь"
            density="compact"
            hide-details="auto"
            variant="outlined"
            readonly
            disabled
          ></v-text-field>
        </v-col>

        <v-col cols="12" class="py-2">
          <v-select
            v-model="formData.role"
            :items="availableRoles"
            label="Роль"
            :rules="[rules.required]"
            density="compact"
            hide-details="auto"
            variant="outlined"
            required
          ></v-select>
        </v-col>
      </v-row>
    </v-container>
    <v-card-actions>
      <v-spacer></v-spacer>
      <v-btn variant="text" @click="uiStore.closePanel()">Отмена</v-btn>
      <v-btn color="primary" variant="flat" type="submit">Сохранить</v-btn>
    </v-card-actions>
  </v-form>
</template>

<script setup>
import { ref, watch } from 'vue';
import { useUiStore } from '@/stores/uiStore';
import { ROLES } from '@/constants/roles';

const props = defineProps({
  userData: { type: Object, required: true },
  onSave: { type: Function, required: true },
});

const uiStore = useUiStore();
const form = ref(null);
const formData = ref({ role: '' });

const availableRoles = Object.values(ROLES);

const rules = {
  required: (v) => !!v || "Поле обязательно для заполнения.",
};

watch(
  () => props.userData,
  (newUserData) => {
    if (newUserData) {
      formData.value.role = newUserData.role;
    }
  },
  { immediate: true }
);

const saveUser = async () => {
  const { valid } = await form.value.validate();
  if (!valid) return;

  const payload = {
    id: props.userData.id,
    ...formData.value,
  };
  props.onSave(payload);
};
</script>
