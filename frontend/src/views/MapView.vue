<template>
  <base-map @ready="handleMapReady">
  </base-map>
</template>


<script setup>
import "@geoman-io/leaflet-geoman-free/dist/leaflet-geoman.css";
import L from "leaflet";
import "@geoman-io/leaflet-geoman-free";

import { useRoute } from "vue-router";
import { ref, computed, watch, onMounted, onUnmounted } from "vue";

import BaseMap from "@/components/BaseMap.vue";
import CreateSectorForm from "@/components/CreateSectorForm.vue";

import { useAuthStore } from "@/stores/authStore";
import { useUiStore } from "@/stores/uiStore";
import { useMapStore } from "@/stores/mapStore";
import { useUserStore } from "@/stores/userStore";
import { useSectorStore } from "@/stores/sectorStore";
import { useTeamStore } from "@/stores/teamStore";

import { useSectorsMap } from "@/composables/useSectorsMap";
import { useMapLayout } from "@/composables/useMapLayout";
import { ROLES } from "@/constants/roles";
import { sectorService } from "@/services/sectorService";
import { generateUniqueRandomColor } from "@/utils/colorGenerator";

const route = useRoute();
const authStore = useAuthStore();
const uiStore = useUiStore();
const mapStore = useMapStore();
const userStore = useUserStore();
const sectorStore = useSectorStore();
const teamStore = useTeamStore();

const { sectorsAsGeoJSON, refreshSectors, geoJsonStyle } = useSectorsMap();
const { panAndZoomTo } = useMapLayout();

let geoJsonLayer = null;
let currentlyEditingLayer = null;
let temporaryDrawingLayer = null;
const isDrawing = ref(false);
let originalGeometryString = null;

const handleMapReady = (map) => {
  mapStore.setMapInstance(map);
};

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

const dynamicStyle = computed(() => {
  const fillOpacity = isManagementMode.value ? 0.8 : 0.3;
  return (feature) => ({
    ...geoJsonStyle(feature),
    fillOpacity: fillOpacity,
  });
});

const onDrawStart = () => (isDrawing.value = true);
const onDrawEnd = () => (isDrawing.value = false);

const toggleManagementFeatures = (enable) => {
  if (!mapStore.mapInstance || !mapStore.mapInstance.pm) return;
  
  if (enable) {
    mapStore.mapInstance.pm.setLang("ru");
    mapStore.mapInstance.pm.addControls({
      position: "topleft",
      drawPolygon: { allowIntersection: false },
      removalMode: false,
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
  } else {
    mapStore.mapInstance.pm.removeControls();
    mapStore.mapInstance.off("pm:drawstart", onDrawStart);
    mapStore.mapInstance.off("pm:drawend", onDrawEnd);
    mapStore.mapInstance.off("pm:create", onCreate);
    if (currentlyEditingLayer) {
      currentlyEditingLayer.pm.disable();
      currentlyEditingLayer = null;
    }
  }
};

watch(() => mapStore.mapInstance, (newMapInstance) => {
    if (newMapInstance && !geoJsonLayer) {
      geoJsonLayer = L.geoJSON(null, {
        style: dynamicStyle.value,
        onEachFeature: onEachFeature,
      }).addTo(newMapInstance);
      
      watch(() => sectorStore.getSectors, (newSectors) => {
        if (geoJsonLayer) {
            geoJsonLayer.clearLayers();
            if (newSectors && newSectors.length > 0) {
                const geoJsonData = sectorsAsGeoJSON.value;
                geoJsonLayer.addData(geoJsonData);
                geoJsonLayer.setStyle(dynamicStyle.value);
            }
        }
      }, { immediate: true });

      toggleManagementFeatures(isManagementMode.value);
    }
  },
  { immediate: true }
);

watch(isManagementMode, (newValue) => {
  toggleManagementFeatures(newValue);
});

watch(dynamicStyle, (newStyleFunction) => {
  if (geoJsonLayer) {
    geoJsonLayer.setStyle(newStyleFunction);
  }
});

watch(() => uiStore.isPanelOpen, async (isOpen, wasOpen) => {
   if (wasOpen && !isOpen) {
    if (currentlyEditingLayer) {
      currentlyEditingLayer.pm.disable();
      currentlyEditingLayer = null;
      originalGeometryString = null;
    }
    if (temporaryDrawingLayer) {
      mapStore.mapInstance.removeLayer(temporaryDrawingLayer);
      temporaryDrawingLayer = null;
    }
    await refreshSectors();

    if (geoJsonLayer && geoJsonLayer.getBounds().isValid()) {
      const allSectorsBounds = geoJsonLayer.getBounds();
      panAndZoomTo(allSectorsBounds);
    }
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
    layer === currentlyEditingLayer
  ) {
    return;
  }
  
  const sectorProps = layer.feature.properties;
  if (!isCurrentUserAdmin.value && sectorProps.curator.id !== currentUserId.value) {
    return;
  }

  const geometryIsDirty =
    currentlyEditingLayer &&
    JSON.stringify(currentlyEditingLayer.toGeoJSON().geometry) !==
      originalGeometryString;

  if (uiStore.isFormDirty || geometryIsDirty) {
    uiStore.showConfirmDialog({
      title: "Несохраненные изменения",
      text: "Вы уверены? Все несохраненные данные будут потеряны.",
      onConfirm: () => {
        if (geometryIsDirty) {
          const originalGeometry = JSON.parse(originalGeometryString);
          const originalLatLngs = originalGeometry.coordinates[0].map((p) => [p[1],p[0]]);
          currentlyEditingLayer.setLatLngs(originalLatLngs);
        }
        startEditing(layer);
      },
    });
  } else {
    startEditing(layer);
  }
};

const handleDelete = (sectorToDelete) => {
  uiStore.showConfirmDialog({
    title: "Подтвердите удаление",
    text: `Вы уверены, что хотите удалить участок "${sectorToDelete.name}"?`,
    onConfirm: async () => {
      try {
        await sectorService.deleteSector(sectorToDelete.id);
        uiStore.closePanel();
        await refreshSectors();
      } catch (error) {
        const errorDetail = error.response?.data?.detail || error.message;
        uiStore.showInfoDialog(
          `Участок "${sectorToDelete.name}" не был удален`,
          errorDetail
        );
      }
    },
  });
};

const startEditing = (layer) => {
  if (currentlyEditingLayer) {
    currentlyEditingLayer.pm.disable();
  }
  currentlyEditingLayer = layer;
  originalGeometryString = JSON.stringify(layer.toGeoJSON().geometry);
  
  const sectorData = layer.feature.properties;
  
  const props = {
    sectorData,
    curators: userStore.getCurators,
    teams: teamStore.getTeams,
    showCuratorSelection: isCurrentUserAdmin.value,
    canDelete: isCurrentUserAdmin.value,
    preselectedCuratorId: currentUserId.value,
    onSave: handleSave,
    onDelete: handleDelete,
  };
  
  uiStore.openPanel(CreateSectorForm, "Редактирование участка", props);
  
  setTimeout(() => {
    panAndZoomTo(currentlyEditingLayer.getBounds());
  }, 300);
  layer.pm.enable({ allowSelfIntersection: false });
};

const onCreate = (e) => {
  temporaryDrawingLayer = e.layer;
  
  const existingColors = sectorsAsGeoJSON.value.features.map(f => f.properties.color);
  const newColor = generateUniqueRandomColor(existingColors);
  
  const props = {
    geometry: e.layer.toGeoJSON().geometry,
    curators: userStore.getCurators,
    teams: teamStore.getTeams,
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
    originalGeometryString = null;
    await refreshSectors();
    await teamStore.refreshTeams();
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

onMounted(() => {
  sectorStore.fetchSectors();
});

onUnmounted(() => {
  mapStore.setMapInstance(null);
  geoJsonLayer = null;
});
</script>
