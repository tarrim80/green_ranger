<template>
  <v-container fluid>
    <v-row>
      <v-col>
        <h1 class="text-h4">Управление командами</h1>
      </v-col>
    </v-row>
    <v-row>
      <v-col>
        <v-btn color="primary" @click="openCreateForm">Создать команду</v-btn>
      </v-col>
    </v-row>
    <v-row>
      <v-col>
        <v-data-table
          :headers="headers"
          :items="teams"
          :loading="loading"
          item-key="id"
          class="elevation-1"
        >
          <template v-slot:item.leader="{ item }">
            {{ item.leader.fullname }}
          </template>
          <template v-slot:item.members="{ item }">
            <v-chip
              v-for="member in item.members"
              :key="member.id"
              class="ma-1"
              size="small"
            >
              {{ member.fullname }}
            </v-chip>
          </template>
          <template v-slot:item.actions="{ item }">
            <v-icon small class="mr-2" @click="openEditForm(item)">mdi-pencil</v-icon>
            <v-icon small @click="deleteTeam(item)">mdi-delete</v-icon>
          </template>
        </v-data-table>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { teamService } from '@/services/teamService';
import { userService } from '@/services/userService';
import { useUiStore } from '@/stores/uiStore';
import TeamForm from '@/components/TeamForm.vue';

const uiStore = useUiStore();
const teams = ref([]);
const users = ref([]);
const loading = ref(true);

const headers = [
  { title: 'Название', key: 'name', sortable: true },
  { title: 'Лидер', key: 'leader', sortable: true },
  { title: 'Участники', key: 'members', sortable: false },
  { title: 'Действия', key: 'actions', sortable: false },
];

const fetchData = async () => {
  loading.value = true;
  try {
    const [teamsResponse, usersResponse] = await Promise.all([
      teamService.getTeams(),
      userService.getAllUsers(),
    ]);
    teams.value = teamsResponse.data;
    users.value = usersResponse.data;
  } catch (error) {
    uiStore.showInfoDialog('Ошибка', 'Не удалось загрузить данные.');
  } finally {
    loading.value = false;
  }
};

const handleSave = async (teamData) => {
  try {
    if (teamData.id) {
      await teamService.updateTeam(teamData.id, teamData);
    } else {
      await teamService.createTeam(teamData);
    }
    uiStore.closePanel();
    await fetchData();
  } catch (error) {
    const errorDetail = error.response?.data?.detail || JSON.stringify(error.response?.data) || "Произошла ошибка";
    uiStore.showInfoDialog('Ошибка сохранения', errorDetail);
  }
};

const openCreateForm = () => {
  const props = {
    users: users.value,
    onSave: handleSave,
  };
  uiStore.openPanel(TeamForm, 'Создание команды', props);
};

const openEditForm = (team) => {
  const props = {
    teamData: team,
    users: users.value,
    onSave: handleSave,
  };
  uiStore.openPanel(TeamForm, 'Редактирование команды', props);
};

const deleteTeam = (team) => {
  uiStore.showConfirmDialog({
    title: 'Подтвердите удаление',
    text: `Вы уверены, что хотите удалить команду "${team.name}"?`,
    onConfirm: async () => {
      try {
        await teamService.deleteTeam(team.id);
        await fetchData();
      } catch (error) {
        const errorDetail = error.response?.data?.detail || "Произошла ошибка";
        uiStore.showInfoDialog('Ошибка удаления', errorDetail);
      }
    }
  });
};

onMounted(fetchData);
</script>
