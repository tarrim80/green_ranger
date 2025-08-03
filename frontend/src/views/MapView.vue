<template>
  <div></div>
</template>

<script setup>
import "@geoman-io/leaflet-geoman-free/dist/leaflet-geoman.css";
import L from "leaflet";
import "@geoman-io/leaflet-geoman-free";

import { useRoute } from "vue-router";
import { ref, computed, watch, onUnmounted } from "vue";

import CreateSectorForm from "@/components/CreateSectorForm.vue";

import { useAuthStore } from "@/stores/auth";
import { useUiStore } from "@/stores/uiStore";
import { useMapStore } from "@/stores/mapStore";
import { useSectorsMap } from "@/composables/useSectorsMap";
import { useMapLayout } from "@/composables/useMapLayout";
import { ROLES } from "@/constants/roles";
import { userService } from "@/services/userService";
import { teamService } from "@/services/teamService";
import { sectorService } from "@/services/sectorService";
import { generateUniqueRandomColor } from "@/utils/colorGenerator";

const route = useRoute();
const authStore = useAuthStore();
const uiStore = useUiStore();
const mapStore = useMapStore();
const { sectors, loadSectors, geoJsonStyle } = useSectorsMap();
const { panAndZoomTo } = useMapLayout();

let geoJsonLayer = null;
const curatorList = ref([]);
const teamList = ref([]);
let currentlyEditingLayer = null;
let temporaryDrawingLayer = null;
const isDrawing = ref(false);
const originalGeometryString = ref(null);

const isManagementMode = computed(() => {
  const userRole = authStore.userRole;
  const routeName = route.name;
  return (
    routeName === "Sectors" &&
    (userRole === ROLES.ADMIN || userRole === ROLES.CURATOR)
  );
});

const currentUserId = computed(() => authStore.currentUser?.id);
const isCurrentUserAdmin = computed(() => authStore.userRole === ROLES.ADMIN);

const toggleManagementFeatures = (enable) => {
  if (!mapStore.mapInstance) return;

  if (enable) {
    mapStore.mapInstance.pm.setLang("ru");
    mapStore.mapInstance.pm.addControls({
      position: "topleft",
      drawPolygon: { allowIntersection: false },
      removalMode: true,
      drawMarker: false,
      drawCircleMarker: false,
      drawPolyline: false,
      drawRectangle: false,
      drawCircle: false,
      drawText: false,
      editMode: false,
      dragMode: false,
      cutPolygon: false,
      rotateMode: false,
    });
    mapStore.mapInstance.on("pm:drawstart", onDrawStart);
    mapStore.mapInstance.on("pm:drawend", onDrawEnd);
    mapStore.mapInstance.on("pm:create", onCreate);
    mapStore.mapInstance.on("pm:remove", onRemove);
  } else {
    if (mapStore.mapInstance.pm) {
      mapStore.mapInstance.pm.removeControls();
      mapStore.mapInstance.off("pm:drawstart", onDrawStart);
      mapStore.mapInstance.off("pm:drawend", onDrawEnd);
      mapStore.mapInstance.off("pm:create", onCreate);
      mapStore.mapInstance.off("pm:remove", onRemove);
      if (currentlyEditingLayer) {
        currentlyEditingLayer.pm.disable();
        currentlyEditingLayer = null;
      }
    }
  }
};

const dynamicStyle = computed(() => {
  const fillOpacity = isManagementMode.value ? 0.8 : 0.3;

  return (feature) => ({
    color: feature.properties.color,
    weight: 2,
    opacity: 1,
    fillOpacity: fillOpacity,
  });
});


watch(isManagementMode, (newValue) => {
  toggleManagementFeatures(newValue);
});

watch(sectors, (newSectorsData) => {
  if (geoJsonLayer) {
    geoJsonLayer.clearLayers();
    geoJsonLayer.addData(newSectorsData);
    geoJsonLayer.setStyle(dynamicStyle.value); 
  }
});

watch(
  () => mapStore.mapInstance,
  async (newMapInstance) => {
    if (newMapInstance && !geoJsonLayer) {
      geoJsonLayer = L.geoJSON(null, {
        style: dynamicStyle.value,
        onEachFeature: onEachFeature,
      }).addTo(newMapInstance);

      await loadSectors();
      toggleManagementFeatures(isManagementMode.value);
    }
  },
  { immediate: true }
);

watch(() => uiStore.isPanelOpen, async (isOpen, wasOpen) => {
   if (wasOpen && !isOpen) {
    if (currentlyEditingLayer) {
      currentlyEditingLayer.pm.disable();
      currentlyEditingLayer = null;
      originalGeometryString.value = null;
    }
    if (temporaryDrawingLayer) {
      mapStore.mapInstance.removeLayer(temporaryDrawingLayer);
      temporaryDrawingLayer = null;
    }
    await loadSectors();

    if (geoJsonLayer) {
      const allSectorsBounds = geoJsonLayer.getBounds();
      panAndZoomTo(allSectorsBounds);
    }
  }
});

watch(dynamicStyle, (newStyleFunction) => {
  if (geoJsonLayer) {
    geoJsonLayer.setStyle(newStyleFunction);
  }
});

const onEachFeature = (feature, layer) => {
  if (feature.properties && feature.properties.name) {
    layer.bindPopup(feature.properties.name);
  }
  layer.on("click", (e) => {
    if (!isManagementMode.value) return;
    L.DomEvent.stopPropagation(e);
    handleLayerClick(e.target);
  });
};

const handleLayerClick = (layer) => {
  if (
    isDrawing.value ||
    mapStore.mapInstance.pm.globalRemovalModeEnabled() ||
    layer === currentlyEditingLayer
  ) {
    return;
  }

  const geometryIsDirty =
    currentlyEditingLayer &&
    JSON.stringify(currentlyEditingLayer.toGeoJSON().geometry) !==
      originalGeometryString.value;

  if (uiStore.isFormDirty || geometryIsDirty) {
    uiStore.showConfirmDialog({
      title: "Несохраненные изменения",
      text: "Вы уверены? Все несохраненные данные будут потеряны.",
      onConfirm: () => {
        if (geometryIsDirty) {
          const originalGeometry = JSON.parse(originalGeometryString.value);
          const originalLatLngs = originalGeometry.coordinates[0].map((p) => [
            p[1],
            p[0],
          ]);
          currentlyEditingLayer.setLatLngs(originalLatLngs);
        }
        startEditing(layer);
      },
    });
  } else {
    startEditing(layer);
  }
};

const startEditing = async (layer) => {
  if (currentlyEditingLayer) {
    currentlyEditingLayer.pm.disable();
  }
  currentlyEditingLayer = layer;
  originalGeometryString.value = JSON.stringify(layer.toGeoJSON().geometry);
  await fetchFormData();
  const feature = layer.feature;
  const sectorData = sectors.value.features.find(
    (f) => f.properties.id === feature.properties.id
  ).properties;
  const props = {
    sectorData,
    curators: curatorList.value,
    teams: teamList.value,
    showCuratorSelection: isCurrentUserAdmin.value,
    preselectedCuratorId: currentUserId.value,
    onSave: handleSave,
  };
  
  uiStore.openPanel(CreateSectorForm, "Редактирование участка", props);
  
  setTimeout(() => {
    panAndZoomTo(currentlyEditingLayer.getBounds());
  }, 300);
  layer.pm.enable({ allowSelfIntersection: false });
};

const fetchFormData = async () => {
  if (curatorList.value.length > 0 && !isCurrentUserAdmin.value) return;
  if (
    curatorList.value.length > 0 &&
    teamList.value.length > 0 &&
    isCurrentUserAdmin.value
  )
    return;
  try {
    const usersPromise = userService.getAllUsers();
    const teamsPromise = isCurrentUserAdmin.value
      ? teamService.getTeams()
      : Promise.resolve({ data: [] });
    const [usersResponse, teamsResponse] = await Promise.all([
      usersPromise,
      teamsPromise,
    ]);
    curatorList.value = usersResponse.data.filter(
      (user) => user.role === ROLES.CURATOR
    );
    teamList.value = teamsResponse.data;
  } catch (error) {
    console.error("Ошибка при загрузке данных для формы:", error);
  }
};

const onDrawStart = () => (isDrawing.value = true);
const onDrawEnd = () => (isDrawing.value = false);

const onCreate = async (e) => {
  temporaryDrawingLayer = e.layer;
  
  const existingColors = sectors.value.features.map(
    (f) => f.properties.color
  );
  const newColor = generateUniqueRandomColor(existingColors);
  await fetchFormData();
  const props = {
    geometry: e.layer.toGeoJSON().geometry,
    curators: curatorList.value,
    teams: teamList.value,
    showCuratorSelection: isCurrentUserAdmin.value,
    preselectedCuratorId: currentUserId.value,
    initialColor: newColor,
    onSave: handleSave,
  };
  uiStore.openPanel(CreateSectorForm, "Создание участка", props);
  setTimeout(() => {
    panAndZoomTo(e.layer.getBounds());
  }, 300);

};

const onRemove = (e) => {
  const sectorId = e.layer.feature.properties.id;
  const sectorName = e.layer.feature.properties.name;
  uiStore.showConfirmDialog({
    title: "Подтвердите удаление",
    text: `Вы уверены, что хотите удалить участок "${sectorName}"?`,
    onConfirm: async () => {
      try {
        await sectorService.deleteSector(sectorId);
        await loadSectors();
      } catch (error) {
        e.layer.addTo(mapStore.mapInstance);
        const errorDetail = error.response?.data?.detail || error.message;
        uiStore.showInfoDialog(
          `Участок "${sectorName}" не был удален`,
          errorDetail
        );
      }
    },
    onCancel: () => e.layer.addTo(mapStore.mapInstance),
  });
};

const handleSave = async (data) => {
  const isUpdating = !!data.id;
  let payload = { ...data };
  if (isUpdating) {
    payload.geometry = currentlyEditingLayer.toGeoJSON().geometry;
  }
  try {
    if (isUpdating) {
      await sectorService.updateSector(payload.id, payload);
    } else {
      await sectorService.createSector(payload);
    }
    if (temporaryDrawingLayer) {
      mapStore.mapInstance.removeLayer(temporaryDrawingLayer);
      temporaryDrawingLayer = null;
    }
    originalGeometryString.value = null;
    uiStore.closePanel();
  } catch (error) {
    const errorDetail =
      error.response?.data?.detail ||
      JSON.stringify(error.response?.data) ||
      error.message;
    uiStore.showInfoDialog(
      "Ошибка сохранения",
      `Не удалось сохранить участок. ${errorDetail}`
    );
  }
};

onUnmounted(() => {
  if (geoJsonLayer) {
    mapStore.mapInstance.removeLayer(geoJsonLayer);
  }
  toggleManagementFeatures(false);
});
</script>
