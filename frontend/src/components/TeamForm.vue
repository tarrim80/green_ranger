<template>
  <v-form ref="form" @submit.prevent="saveTeam">
    <v-container>
      <v-row>
        <v-col cols="12">
          <v-text-field
            v-model="formData.name"
            label="Название команды"
            :rules="[rules.required]"
            density="compact"
            hide-details="auto"
            required
          ></v-text-field>
        </v-col>

        <v-col cols="12">
          <p class="text-subtitle-2 mb-2">Состав команды</p>
          <div class="chip-container selected-container pa-2">
            <v-chip
              v-for="volunteer in selectedVolunteers"
              :key="volunteer.id"
              class="ma-1"
            >
              <v-icon
                start
                :color="volunteer.id === formData.leader_id ? 'amber' : 'grey-lighten-1'"
                @click.stop="setLeader(volunteer)"
              >
                mdi-crown
              </v-icon>
              {{ volunteer.fullname }}
              <v-icon
                end
                size="small"
                icon="mdi-close-circle"
                @click="removeMember(volunteer)"
              ></v-icon>
            </v-chip>
            <p v-if="selectedVolunteers.length === 0" class="text-caption text-grey">
              Добавьте участников из списка ниже
            </p>
          </div>
        </v-col>

        <v-col cols="12">
          <p class="text-subtitle-2 my-2">Доступные волонтеры</p>
          <div class="chip-container available-container pa-2">
            <v-chip
              v-for="volunteer in availableVolunteers"
              :key="volunteer.id"
              @click="addMember(volunteer)"
              class="ma-1"
            >
              <v-icon start>mdi-plus-circle-outline</v-icon>
              {{ volunteer.fullname }}
            </v-chip>
             <p v-if="availableVolunteers.length === 0" class="text-caption text-grey">
              Нет свободных волонтеров
            </p>
          </div>
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
import { ref, watch, computed } from "vue";
import { useUiStore } from "@/stores/uiStore";
import { useUserStore } from "@/stores/userStore";

const props = defineProps({
  teamData: { type: Object, default: null },
  users: { type: Array, required: true },
  onSave: { type: Function, required: true },
});

const uiStore = useUiStore();
const userStore = useUserStore();
const form = ref(null);

const formData = ref({
  id: null,
  name: '',
  leader_id: null,
  member_ids: [],
});

const isEditing = computed(() => !!props.teamData);

const selectableVolunteers = computed(() => {
  if (isEditing.value) {
    const originalTeamId = props.teamData.id;
    return userStore.getVolunteers.filter(
      (v) => !v.team_id || v.team_id === originalTeamId
    );
  } else {
    return userStore.getFreeVolunteers;
  }
});

const selectedVolunteers = computed(() => {
  const memberIdsSet = new Set(formData.value.member_ids);
  return props.users.filter((v) => memberIdsSet.has(v.id));
});

const availableVolunteers = computed(() => {
  const memberIdsSet = new Set(formData.value.member_ids);
  return selectableVolunteers.value.filter((v) => !memberIdsSet.has(v.id));
});

const rules = {
  required: (v) => !!v || "Поле обязательно для заполнения.",
  leaderRequired: (v) => !!v || "Необходимо назначить лидера.",
};

const addMember = (volunteer) => {
  formData.value.member_ids.push(volunteer.id);
  if (formData.value.member_ids.length === 1) {
    setLeader(volunteer);
  }
};

const removeMember = (volunteer) => {
  if (volunteer.id === formData.value.leader_id) {
    uiStore.showInfoDialog(
      "Действие запрещено",
      "Нельзя удалить лидера команды. Сначала назначьте нового лидера."
    );
    return;
  }
  const index = formData.value.member_ids.indexOf(volunteer.id);
  if (index > -1) {
    formData.value.member_ids.splice(index, 1);
  }
};

const setLeader = (volunteer) => {
  formData.value.leader_id = volunteer.id;
};

const updateFormData = (data) => {
  if (data) {
    formData.value = {
      id: data.id,
      name: data.name,
      leader_id: data.leader.id,
      member_ids: data.members.map((m) => m.id),
    };
  } else {
    formData.value = {
      id: null,
      name: "",
      leader_id: null,
      member_ids: [],
    };
  }
};

watch(
  () => props.teamData,
  (newTeamData) => {
    updateFormData(newTeamData);
  },
  { immediate: true }
);

const saveTeam = async () => {
  const { valid } = await form.value.validate();
  if (!valid) return;
  
  if (!formData.value.leader_id && formData.value.member_ids.length > 0) {
      uiStore.showInfoDialog("Ошибка", "В команде должен быть назначен лидер.");
      return;
  }
  
  props.onSave(formData.value);
};
</script>

<style scoped>
.chip-container {
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  min-height: 80px;
  width: 100%;
}
</style>
