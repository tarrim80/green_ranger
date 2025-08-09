import { defineStore } from "pinia";
import { defectTypeService } from "@/services/defectTypeService";
import { getFullUrl } from "@/utils/url";

const transformImagePaths = (defectType) => {
  if (defectType && defectType.images && defectType.images.length > 0) {
    return {
      ...defectType,
      images: defectType.images.map((image) => ({
        ...image,
        file_path: getFullUrl(image["file_path"]),
        thumbnail_path: getFullUrl(image["thumbnail_path"]),
      })),
    };
  }
  return defectType;
};

export const useDefectTypeStore = defineStore("defectType", {
  state: () => ({
    defectTypes: [],
    loading: false,
  }),

  getters: {
    getDefectTypes: (state) => state.defectTypes,
  },

  actions: {
    async fetchDefectTypes() {
      if (this.defectTypes.length > 0) {
        return;
      }
      this.loading = true;
      try {
        const response = await defectTypeService.getDefectTypes();
        this.defectTypes = response.data.map(transformImagePaths);
      } catch (error) {
        console.error("Ошибка при загрузке видов дефектов:", error);
      } finally {
        this.loading = false;
      }
    },

    async refreshDefectTypes() {
      this.loading = true;
      try {
        const response = await defectTypeService.getDefectTypes();
        this.defectTypes = response.data.map(transformImagePaths);
      } catch (error) {
        console.error("Ошибка при обновлении видов дефектов:", error);
      } finally {
        this.loading = false;
      }
    },

    async createDefectType(data) {
      return defectTypeService.createDefectType(data);
    },

    async updateDefectType(id, { textData, newPhotos }) {
      await defectTypeService.updateDefectType(id, textData);
      if (newPhotos && newPhotos.length > 0) {
        await defectTypeService.addPhotos(id, newPhotos);
      }
    },

    async deleteDefectType(id) {
      return defectTypeService.deleteDefectType(id);
    },

    async removePhoto(photoId) {
      return defectTypeService.removePhoto(photoId);
    },

    clearDefectTypes() {
      this.defectTypes = [];
    },
  },
});