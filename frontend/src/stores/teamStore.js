import { defineStore } from "pinia";
import { teamService } from "@/services/teamService";

export const useTeamStore = defineStore("team", {
  state: () => ({
    teams: [],
    loading: false,
  }),
  getters: {
    getTeams: (state) => state.teams,
  },
  actions: {
    async fetchTeams() {
      if (this.teams.length > 0) {
        return;
      }
      this.loading = true;
      try {
        const response = await teamService.getTeams();
        this.teams = response.data;
      } catch (error) {
        console.error("Ошибка при загрузке команд:", error);
      } finally {
        this.loading = false;
      }
    },
    async refreshTeams() {
      this.loading = true;
      try {
        const response = await teamService.getTeams();
        this.teams = response.data;
      } catch (error) {
        console.error("Ошибка при обновлении команд:", error);
      } finally {
        this.loading = false;
      }
    },
    async createTeam(teamData) {
      return teamService.createTeam(teamData);
    },
    async updateTeam(id, teamData) {
      const updateTeamDetails = teamService.updateTeam(id, teamData);
      const syncMembers = teamService.syncTeamMembers(id, teamData.member_ids);

      await Promise.all([updateTeamDetails, syncMembers]);
    },
    async deleteTeam(id) {
      return teamService.deleteTeam(id);
    },
    clearTeams() {
      this.teams = [];
    },
  },
});
