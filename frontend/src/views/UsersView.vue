<template>
  <div>
    <v-row>
      <v-col>
        <h2 class="text-h4 mb-4">Пользователи</h2>
      </v-col>
    </v-row>
    <v-row>
      <v-col>
        <v-card>
          <v-data-table
            :headers="headers"
            :items="users"
            :loading="loading"
            item-key="id"
            :row-props="rowProps"
            items-per-page-text="Показывать по"
          >
            <template v-slot:item.is_active="{ value }">
              <v-chip :color="value ? 'success' : 'default'" size="small">
                {{ value ? 'Активен' : 'Неактивен' }}
              </v-chip>
            </template>

            <template v-slot:item.actions="{ item }">
              <v-tooltip location="top" text="Редактировать роль">
                <template v-slot:activator="{ props }">
                  <v-icon v-bind="props" small class="mr-4" @click="openEditForm(item)">mdi-pencil</v-icon>
                </template>
              </v-tooltip>

              <v-tooltip v-if="item.is_active" location="top" text="Деактивировать">
                 <template v-slot:activator="{ props }">
                  <v-icon v-bind="props" small @click="toggleUserStatus(item)" color="error">mdi-account-off</v-icon>
                </template>
              </v-tooltip>

              <v-tooltip v-else location="top" text="Активировать">
                 <template v-slot:activator="{ props }">
                  <v-icon v-bind="props" small @click="toggleUserStatus(item)" color="success">mdi-account-check</v-icon>
                </template>
              </v-tooltip>
            </template>
          </v-data-table>
        </v-card>
      </v-col>
    </v-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { userService } from '@/services/userService';
import { useUiStore } from '@/stores/uiStore';
import { useAuthStore } from '@/stores/auth';
import UserEditForm from '@/components/UserEditForm.vue';

const uiStore = useUiStore();
const authStore = useAuthStore();
const users = ref([]);
const loading = ref(true);

const headers = [
  { title: 'Полное имя', key: 'fullname', sortable: true },
  { title: 'Роль', key: 'role', sortable: true },
  { title: 'Статус', key: 'is_active', sortable: true },
  { title: 'Действия', key: 'actions', sortable: false, align: 'end' },
];

const rowProps = ({ item }) => {
  return {
    class: !item.is_active ? 'inactive-user-row' : ''
  };
};

const fetchData = async () => {
  loading.value = true;
  try {
    const response = await userService.getAllUsers();
    users.value = response.data.filter(user => user.id !== authStore.currentUser.id);
  } catch (error) {
    uiStore.showInfoDialog('Ошибка', 'Не удалось загрузить список пользователей.');
  } finally {
    loading.value = false;
  }
};

const handleSave = async (userData) => {
  try {
    await userService.updateUser(userData.id, { role: userData.role });
    uiStore.closePanel();
    await fetchData();
  } catch (error) {
    const errorDetail = error.response?.data?.detail || "Произошла ошибка";
    uiStore.showInfoDialog('Ошибка сохранения', errorDetail);
  }
};

const openEditForm = (user) => {
  const props = {
    userData: user,
    onSave: handleSave,
  };
  uiStore.openPanel(UserEditForm, 'Редактирование роли', props);
};

const toggleUserStatus = (user) => {
  const actionText = user.is_active ? 'деактивировать' : 'активировать';
  uiStore.showConfirmDialog({
    title: `Подтвердите действие`,
    text: `Вы уверены, что хотите ${actionText} пользователя ${user.fullname}?`,
    onConfirm: async () => {
      try {
        await userService.updateUser(user.id, { is_active: !user.is_active });
        await fetchData();
      } catch (error) {
        const errorDetail = error.response?.data?.detail || "Произошла ошибка";
        uiStore.showInfoDialog('Ошибка', errorDetail);
      }
    }
  });
};

onMounted(fetchData);
</script>

<style>
.inactive-user-row {
  background-color: #f5f5f5;
  color: #9e9e9e;
  text-decoration: line-through;
}

.inactive-user-row .v-icon:not(.text-success) {
  color: #9e9e9e !important;
}
</style>
