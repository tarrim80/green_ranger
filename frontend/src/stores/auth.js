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
    reloadKey: 0,
  }),
  getters: {
    isAuthenticated: (state) => !!state.accessToken,
    userRole: (state) => (state.currentUser ? state.currentUser.role : null),
    userFullname: (state) => {
      if (state.currentUser) {
        return `${state.currentUser.firstname || ""} ${
          state.currentUser.lastname || ""
        }`.trim();
      }
      return "";
    },
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

      await this.fetchCurrentUser(true);
    },

    async fetchCurrentUser(isLogin = false) {
      if (this.accessToken) {
        try {
          const response = await apiClient.get("/users/me");
          this.currentUser = response.data;
        } catch (error) {
          console.error("Не удалось получить данные пользователя:", error);
          if (!isLogin) {
            this.logout();
          } else {
            throw error;
          }
        }
      }
    },

    async updateUserProfile(profileData) {
      if (!this.currentUser) return;
      try {
        const response = await apiClient.patch("/users/me", profileData);
        this.currentUser = response.data;
      } catch (error) {
        console.error("Ошибка обновления профиля:", error);
        throw error;
      }
    },

    async changePassword(passwordData) {
      if (!this.currentUser) return;
      try {
        await apiClient.patch("/users/me", {
          password: passwordData.new_password,
          current_password: passwordData.current_password,
        });
      } catch (error) {
        console.error("Ошибка смены пароля:", error);
        throw error;
      }
    },

    async tryAutoLogin() {
      if (this.accessToken) {
        await this.fetchCurrentUser();
      }
    },

    clearAuthData() {
      this.accessToken = null;
      this.refreshToken = null;
      this.currentUser = null;
      localStorage.removeItem("accessToken");
      localStorage.removeItem("refreshToken");
    },

    logout() {
      window.location.replace("/?logout=1");
    },
  },
});
