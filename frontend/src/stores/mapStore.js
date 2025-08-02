import { defineStore } from "pinia";

export const useMapStore = defineStore("map", {
  state: () => ({
    mapInstance: null,
  }),
  actions: {
    setMapInstance(map) {
      this.mapInstance = map;
    },
  },
});
