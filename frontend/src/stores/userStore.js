import { defineStore } from "pinia";
import { userService } from "@/services/userService";
import { ROLES } from "@/constants/roles";

export const useUserStore = defineStore("user", {
  state: () => ({
    users: [],
    loading: false,
  }),
  getters: {
    getUsers: (state) => state.users,
    getVolunteers: (state) =>
      state.users.filter((user) => user.role === ROLES.VOLUNTEER),
    getCurators: (state) =>
      state.users.filter((user) => user.role === ROLES.CURATOR),
    getFreeVolunteers: (state) =>
      state.users.filter(
        (user) => user.role === ROLES.VOLUNTEER && !user.team_id
      ),
  },
  actions: {
    async fetchUsers() {
      if (this.users.length > 0) {
        return;
      }
      this.loading = true;
      try {
        const response = await userService.getAllUsers();
        this.users = response.data;
      } catch (error) {
        console.error("Ошибка при загрузке пользователей:", error);
      } finally {
        this.loading = false;
      }
    },
    async refreshUsers() {
      this.loading = true;
      try {
        const response = await userService.getAllUsers();
        this.users = response.data;
      } catch (error) {
        console.error("Ошибка при обновлении пользователей:", error);
      } finally {
        this.loading = false;
      }
    },
    async updateUser(id, userData) {
      try {
        await userService.updateUser(id, userData);
        await this.refreshUsers();
      } catch (e) {
        console.error("Ошибка при обновлении пользователя:", e);
        throw e;
      }
    },
  },
});
