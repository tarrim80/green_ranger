<template>
  <div>
    <v-row>
      <v-col>
        <h2 class="text-h5">Пользователи</h2>
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
            <template v-slot:no-data>
            <div class="text-center py-4">Нет элементов для отображения</div>
            </template>  
          </v-data-table>
        </v-card>
      </v-col>
    </v-row>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue';
import { useUiStore } from '@/stores/uiStore';
import { useAuthStore } from '@/stores/authStore';
import { useUserStore } from '@/stores/userStore';
import UserEditForm from '@/components/UserEditForm.vue';

const uiStore = useUiStore();
const authStore = useAuthStore();
const userStore = useUserStore();

const users = computed(() => {
  return userStore.getUsers.filter(user => user.id !== authStore.currentUser.id);
});
const loading = computed(() => userStore.loading);

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

const handleSave = async (userData) => {
  try {
    await userStore.updateUser(userData.id, { role: userData.role });
    uiStore.closePanel();
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
        await userStore.updateUser(user.id, { is_active: !user.is_active });
      } catch (error) {
        const errorDetail = error.response?.data?.detail || "Произошла ошибка";
        uiStore.showInfoDialog('Ошибка', errorDetail);
      }
    }
  });
};

onMounted(() => {
  userStore.fetchUsers();
});</script>

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
