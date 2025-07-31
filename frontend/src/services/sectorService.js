import apiClient from "./api";

export const sectorService = {
  getSectors() {
    return apiClient.get("/sectors/");
  },
  createSector(sectorData) {
    return apiClient.post("/sectors/", sectorData);
  },
  updateSector(id, sectorData) {
    return apiClient.patch(`/sectors/${id}`, sectorData);
  },
  deleteSector(id) {
    return apiClient.delete(`/sectors/${id}`);
  },
};
