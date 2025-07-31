import apiClient from "./api";

export const userService = {
  getAllUsers() {
    return apiClient.get("/users/");
  },
};
