<template>
  <div>
    <v-row align="center">
      <v-col>
        <h2 class="text-h5">Команды</h2>
      </v-col>
    </v-row>
    <v-row align="center">
      <v-col>
        <v-btn color="primary" @click="openCreateForm">Создать команду</v-btn>
      </v-col>
      <v-col class="text-right">
        <span class="text-subtitle-1 font-weight-medium">
          Свободных волонтеров: {{ freeVolunteersCount }}
        </span>
      </v-col>
    </v-row>
    <v-row>
      <v-col>
        <v-data-table
          :headers="headers"
          :items="processedTeams"
          :loading="loading"
          item-key="id"
          class="elevation-1"
          items-per-page-text="Показывать по"
        >
          <template v-slot:item.leader="{ item }">
            {{ item.leader.fullname }}
          </template>
          <template v-slot:item.sectorName="{ item }">
            <span v-if="item.sectorName">{{ item.sectorName }}</span>
            <v-chip v-else size="small">Участок не назначен</v-chip>
          </template>
          <template v-slot:item.actions="{ item }">
            <v-icon small class="mr-2" @click="openEditForm(item.originalItem)">mdi-pencil</v-icon>
            <v-icon small @click="deleteTeam(item.originalItem)">mdi-delete</v-icon>
          </template>
        </v-data-table>
      </v-col>
    </v-row>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue';
import { useUiStore } from '@/stores/uiStore';
import { useSectorStore } from '@/stores/sectorStore';
import { useUserStore } from '@/stores/userStore';
import { useTeamStore } from '@/stores/teamStore';
import TeamForm from '@/components/TeamForm.vue';

const uiStore = useUiStore();
const sectorStore = useSectorStore();
const userStore = useUserStore();
const teamStore = useTeamStore();

const headers = [
  { title: 'Название', key: 'name', sortable: true },
  { title: 'Лидер', key: 'leader', sortable: true },
  { title: 'Количество участников', key: 'membersCount', sortable: true, align: 'center' },
  { title: 'Участок', key: 'sectorName', sortable: true },
  { title: 'Куратор', key: 'curatorName', sortable: true },
  { title: 'Действия', key: 'actions', sortable: false },
];

const teams = computed(() => teamStore.getTeams);
const volunteers = computed(() => userStore.getVolunteers);
const loading = computed(() => teamStore.loading || userStore.loading || sectorStore.loading);

const processedTeams = computed(() => {
  return teams.value.map(team => {
    const assignedSector = sectorStore.getSectors.find(sector => sector.team?.id === team.id);
    return {
      ...team,
      originalItem: team, 
      membersCount: team.members.length,
      sectorName: assignedSector ? assignedSector.name : null,
      curatorName: assignedSector ? assignedSector.curator.fullname : '',
    };
  });
});

const freeVolunteersCount = computed(() => {
  return userStore.getFreeVolunteers.length;
});

const handleSave = async (teamData) => {
  try {
    if (teamData.id) {
      await teamStore.updateTeam(teamData.id, teamData);
    } else {
      await teamStore.createTeam(teamData);
    }
    uiStore.closePanel();
    await teamStore.refreshTeams();
    await userStore.refreshUsers();

  } catch (error) {
    const errorDetail = error.response?.data?.detail || JSON.stringify(error.response?.data) || "Произошла ошибка";
    uiStore.showInfoDialog('Ошибка сохранения', errorDetail);
  }
};

const openCreateForm = () => {
  const props = {
    users: volunteers.value,
    onSave: handleSave,
  };
  uiStore.openPanel(TeamForm, 'Создание команды', props);
};

const openEditForm = (team) => {
  const props = {
    teamData: team,
    users: volunteers.value,
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
        await teamStore.deleteTeam(team.id);
        await teamStore.refreshTeams();
        await userStore.refreshUsers();
      } catch (error) {
        const errorDetail = error.response?.data?.detail || "Произошла ошибка";
        uiStore.showInfoDialog('Ошибка удаления', errorDetail);
      }
    }
  });
};

onMounted(() => {
  teamStore.fetchTeams();
  userStore.fetchUsers();
  sectorStore.fetchSectors();
});
</script>
