import apiClient from "./api";

export const userService = {
  getAllUsers() {
    return apiClient.get("/users/");
  },

  registerUser(userData) {
    return apiClient.post("/auth/jwt/register", userData);
  },
};
