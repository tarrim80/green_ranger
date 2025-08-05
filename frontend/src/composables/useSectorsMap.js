import { computed } from "vue";
import { useSectorStore } from "@/stores/sectorStore";

export function useSectorsMap() {
  const sectorStore = useSectorStore();

  const sectorsAsGeoJSON = computed(() => {
    const features = sectorStore.getSectors.map((sector) => ({
      type: "Feature",
      properties: { ...sector },
      geometry: sector.geometry,
    }));
    return { type: "FeatureCollection", features: features };
  });

  const refreshSectors = async () => {
    await sectorStore.refreshSectors();
  };

  const geoJsonStyle = (feature) => ({
    color: feature.properties.color,
    weight: 2,
    opacity: 1,
    fillOpacity: 0.3,
  });

  return {
    sectorsAsGeoJSON,
    refreshSectors,
    geoJsonStyle,
  };
}
