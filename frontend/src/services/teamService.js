import apiClient from "./api";

export const teamService = {
  getTeams() {
    return apiClient.get("/teams/");
  },
};
