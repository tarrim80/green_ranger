import { defineStore } from "pinia";
import { sectorService } from "@/services/sectorService";

export const useSectorStore = defineStore("sector", {
  state: () => ({
    sectors: [],
    loading: false,
  }),
  getters: {
    getSectors: (state) => state.sectors,
  },
  actions: {
    async fetchSectors() {
      if (this.sectors.length > 0) {
        return;
      }
      this.loading = true;
      try {
        const response = await sectorService.getSectors();
        this.sectors = response.data;
      } catch (error) {
        console.error("Ошибка при загрузке участков:", error);
      } finally {
        this.loading = false;
      }
    },
    async refreshSectors() {
      this.loading = true;
      try {
        const response = await sectorService.getSectors();
        this.sectors = response.data;
      } catch (error) {
        console.error("Ошибка при обновлении участков:", error);
      } finally {
        this.loading = false;
      }
    },
  },
});
