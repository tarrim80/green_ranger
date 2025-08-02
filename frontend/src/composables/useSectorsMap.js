import { ref } from "vue";
import { sectorService } from "@/services/sectorService";

export function useSectorsMap() {
  const sectors = ref({ type: "FeatureCollection", features: [] });

  const loadSectors = async () => {
    try {
      const response = await sectorService.getSectors();
      const features = response.data.map((sector) => ({
        type: "Feature",
        properties: { ...sector },
        geometry: sector.geometry,
      }));
      sectors.value = { type: "FeatureCollection", features: features };
    } catch (error) {
      console.error("Ошибка при загрузке участков:", error);
    }
  };

  const geoJsonStyle = (feature) => ({
    color: feature.properties.color,
    weight: 2,
    opacity: 1,
    fillOpacity: 0.3,
  });

  return {
    sectors,
    loadSectors,
    geoJsonStyle,
  };
}
