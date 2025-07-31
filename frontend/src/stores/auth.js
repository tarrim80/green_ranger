import { defineStore } from "pinia";
import apiClient from "@/services/api";
import router from "@/router";

export const useAuthStore = defineStore("auth", {
  state: () => ({
    accessToken: localStorage.getItem("accessToken") || null,
    refreshToken: localStorage.getItem("refreshToken") || null,
    currentUser: null,
  }),
  getters: {
    isAuthenticated: (state) => !!state.accessToken,
    userRole: (state) => (state.currentUser ? state.currentUser.role : null),
  },
  actions: {
    async login(credentials) {
      try {
        const formData = new FormData();
        formData.append("username", credentials.email);
        formData.append("password", credentials.password);

        const response = await apiClient.post("/auth/jwt/login", formData, {
          headers: { "Content-Type": "multipart/form-data" },
        });

        this.accessToken = response.data.access_token;
        this.refreshToken = response.data.refresh_token;

        localStorage.setItem("accessToken", this.accessToken);
        localStorage.setItem("refreshToken", this.refreshToken);

        await this.fetchCurrentUser();

        router.push("/");
      } catch (error) {
        console.error("Ошибка аутентификации:", error);
        this.logout();
        alert("Неверный логин или пароль!");
      }
    },

    async fetchCurrentUser() {
      if (this.accessToken) {
        try {
          const response = await apiClient.get("/users/me");
          this.currentUser = response.data;
        } catch (error) {
          console.error("Не удалось получить данные пользователя:", error);
          this.logout();
        }
      }
    },

    async tryAutoLogin() {
      if (this.accessToken) {
        await this.fetchCurrentUser();
      }
    },

    logout() {
      this.accessToken = null;
      this.refreshToken = null;
      this.currentUser = null;

      localStorage.removeItem("accessToken");
      localStorage.removeItem("refreshToken");

      router.push("/login");
    },
  },
});
