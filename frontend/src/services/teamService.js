import apiClient from "./api";

export const teamService = {
  getTeams() {
    return apiClient.get("/teams/");
  },
  createTeam(teamData) {
    return apiClient.post("/teams/", teamData);
  },
  updateTeam(id, teamData) {
    const { id: teamId, member_ids, ...payload } = teamData;
    return apiClient.patch(`/teams/${id}`, payload);
  },
  syncTeamMembers(id, memberIds) {
    return apiClient.post(`/teams/${id}/sync_members`, {
      member_ids: memberIds,
    });
  },
  deleteTeam(id) {
    return apiClient.delete(`/teams/${id}`);
  },
};
