import apiClient from "./api";

export const teamService = {
  getTeams() {
    return apiClient.get("/teams/");
  },
  createTeam(teamData) {
    return apiClient.post("/teams/", teamData);
  },
  updateTeam(id, teamData) {
    const { id: teamId, ...payload } = teamData;
    return apiClient.patch(`/teams/${id}`, payload);
  },
  deleteTeam(id) {
    return apiClient.delete(`/teams/${id}`);
  },
};
