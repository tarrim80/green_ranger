import { defineStore } from "pinia";
import apiClient from "@/services/api";
import router from "@/router";
import { useUiStore } from "./uiStore";
import { userService } from "@/services/userService";

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
      const uiStore = useUiStore();
      try {
        const formData = new FormData();
        formData.append("username", credentials.email);
        formData.append("password", credentials.password);

        const response = await apiClient.post("/auth/jwt/login", formData, {
          headers: { "Content-Type": "multipart/form-data" },
        });

        await this.setTokensAndUser(response.data);
        router.push("/");
      } catch (error) {
        console.error("Ошибка аутентификации:", error);
        this.logout();
        uiStore.showInfoDialog("Ошибка входа", "Неверный логин или пароль!");
      }
    },

    async register(userData) {
      const uiStore = useUiStore();
      const payload = {
        ...userData,
        telegram_id: Date.now(),
      };
      try {
        await userService.registerUser(payload);
        uiStore.showInfoDialog(
          "Регистрация успешна",
          "Теперь вы можете войти в систему, используя свою почту и пароль."
        );
        router.push("/login");
      } catch (error) {
        console.error("Ошибка регистрации:", error);
        const errorDetail =
          error.response?.data?.detail || "Произошла неизвестная ошибка.";
        uiStore.showInfoDialog("Ошибка регистрации", errorDetail);
      }
    },

    async setTokensAndUser(tokenData) {
      this.accessToken = tokenData.access_token;
      this.refreshToken = tokenData.refresh_token;

      localStorage.setItem("accessToken", this.accessToken);
      localStorage.setItem("refreshToken", this.refreshToken);

      await this.fetchCurrentUser();
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
