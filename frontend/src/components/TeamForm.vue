<template>
  <v-form ref="form" @submit.prevent="saveTeam">
    <v-container>
      <v-row>
        <v-col cols="12">
          <v-text-field
            v-model="formData.name"
            label="Название команды"
            :rules="[rules.required]"
            required
          ></v-text-field>
        </v-col>

        <v-col cols="12">
          <v-select
            v-model="formData.leader_id"
            :items="props.users"
            item-title="fullname"
            item-value="id"
            label="Лидер команды"
            :rules="[rules.required]"
            required
          ></v-select>
        </v-col>

        <v-col cols="12">
          <v-select
            v-model="formData.member_ids"
            :items="props.users"
            item-title="fullname"
            item-value="id"
            label="Участники"
            multiple
            chips
            closable-chips
            :rules="[rules.required, rules.leaderIsMember]"
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
import { ref, watch, computed } from 'vue';
import { useUiStore } from '@/stores/uiStore';

const props = defineProps({
  teamData: { type: Object, default: null },
  users: { type: Array, required: true },
  onSave: { type: Function, required: true },
});

const uiStore = useUiStore();
const form = ref(null);
const formData = ref({});

const rules = {
  required: (v) => (Array.isArray(v) ? v.length > 0 : !!v) || 'Поле обязательно для заполнения.',
  leaderIsMember: computed(() => {
    return (v) => (v && v.includes(formData.value.leader_id)) || 'Лидер команды должен быть в списке участников.';
  }),
};

const updateFormData = (data) => {
  if (data) {
    formData.value = {
      id: data.id,
      name: data.name,
      leader_id: data.leader.id,
      member_ids: data.members.map(m => m.id),
    };
  } else {
    formData.value = {
      name: '',
      leader_id: null,
      member_ids: [],
    };
  }
};

watch(() => props.teamData, (newTeamData) => {
  updateFormData(newTeamData);
}, { immediate: true });


const saveTeam = async () => {
  const { valid } = await form.value.validate();
  if (!valid) return;
  props.onSave(formData.value);
};
</script>
