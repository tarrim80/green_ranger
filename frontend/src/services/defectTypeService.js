import apiClient from "./api";

export const defectTypeService = {
  getDefectTypes() {
    return apiClient.get("/defect-types/");
  },

  getDefectTypeById(id) {
    return apiClient.get(`/defect-types/${id}/`);
  },

  createDefectType(data) {
    return apiClient.post("/defect-types/", data, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
  },

  updateDefectType(id, data) {
    return apiClient.patch(`/defect-types/${id}/`, data);
  },

  addPhotos(id, files) {
    const formData = new FormData();
    for (const file of files) {
      formData.append("files", file);
    }
    return apiClient.post(`/defect-types/${id}/images/`, formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
  },

  deleteDefectType(id) {
    return apiClient.delete(`/defect-types/${id}/`);
  },

  removePhoto(photoId) {
    return apiClient.delete(`/photos/${photoId}/`);
  },
};