import apiClient from "./api";

export const sectorService = {
  getSectors() {
    return apiClient.get("/sectors/");
  },
  createSector(sectorData) {
    return apiClient.post("/sectors/", sectorData);
  },
};
