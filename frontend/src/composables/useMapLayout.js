import { useMapStore } from "@/stores/mapStore";

export function useMapLayout() {
  const mapStore = useMapStore();

  const panAndZoomTo = (bounds) => {
    const map = mapStore.mapInstance;
    if (!map || !bounds || !bounds.isValid()) {
      return;
    }
    map.invalidateSize({ animate: true });
    map.fitBounds(bounds, {
      animate: true,
      duration: 0.75,
    });
  };

  return {
    panAndZoomTo,
  };
}
