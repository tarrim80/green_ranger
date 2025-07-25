// frontend/src/stores/auth.js
import { defineStore } from "pinia";
import apiClient from "@/services/api";
import router from "@/router";

export const useAuthStore = defineStore("auth", {
  state: () => ({
    accessToken: localStorage.getItem("accessToken") || null,
    refreshToken: localStorage.getItem("refreshToken") || null,
    user: null,
  }),
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

        router.push("/");
      } catch (error) {
        console.error("Ошибка аутентификации:", error);
        alert("Неверный логин или пароль!");
      }
    },
  },
});
