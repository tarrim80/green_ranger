import axios from "axios";
import { useAuthStore } from "@/stores/auth";

const apiClient = axios.create({
  baseURL: "http://localhost:8000/api/v1",
  headers: {
    "Content-Type": "application/json",
  },
});

apiClient.interceptors.request.use(
  (config) => {
    const authStore = useAuthStore();
    const token = authStore.accessToken;
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    const authStore = useAuthStore();

    if (error.response.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      if (originalRequest.url.includes("/auth/jwt/refresh")) {
        authStore.logout();
        return Promise.reject(error);
      }

      try {
        const response = await axios.post(
          `${apiClient.defaults.baseURL}/auth/jwt/refresh`,
          {},
          {
            headers: {
              Authorization: `Bearer ${authStore.refreshToken}`,
            },
          }
        );

        await authStore.setTokensAndUser(response.data);

        originalRequest.headers[
          "Authorization"
        ] = `Bearer ${authStore.accessToken}`;

        return apiClient(originalRequest);
      } catch (refreshError) {
        authStore.logout();
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export default apiClient;
