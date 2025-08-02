<template>
  <div class="map-container">
    <l-map ref="mapInstance" :zoom="zoom" :center="center" @ready="onMapReady">
      <l-tile-layer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        layer-type="base"
        name="OpenStreetMap"
        :attribution="mapAttribution"
      >
      </l-tile-layer>
      <l-control-scale position="bottomleft" :imperial="false" />
      <l-geo-json
        v-if="sectors.features.length > 0"
        :geojson="sectors"
        :options-style="geoJsonStyle"
        :options="geoJsonOptions"
        ref="geoJsonLayer"
      ></l-geo-json>
    </l-map>
  </div>
</template>

<script setup>
import "leaflet/dist/leaflet.css";
import "@geoman-io/leaflet-geoman-free/dist/leaflet-geoman.css";

import L from "leaflet";
import "@geoman-io/leaflet-geoman-free";

import { LMap, LTileLayer, LControlScale, LGeoJson } from "@vue-leaflet/vue-leaflet";
import { ref, computed, onMounted, watch } from "vue";

import { useAuthStore } from "@/stores/auth";
import { useUiStore } from "@/stores/uiStore";

import { ROLES } from "@/constants/roles";
import { INITIAL_CENTER, INITIAL_ZOOM } from "@/constants/map";

import { userService } from "@/services/userService";
import { teamService } from "@/services/teamService";
import { sectorService } from "@/services/sectorService";
import { generateUniqueRandomColor } from "@/utils/colorGenerator";

import CreateSectorForm from "@/components/CreateSectorForm.vue";

const mapInstance = ref(null);
const zoom = ref(INITIAL_ZOOM);
const center = ref(INITIAL_CENTER);
const mapAttribution = ref('© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors | ТОО "Теплица геоинформационных технологий" 2025г.');

const authStore = useAuthStore();
const uiStore = useUiStore();

const geoJsonLayer = ref(null);
const curatorList = ref([]);
const teamList = ref([]);
const sectors = ref({ type: "FeatureCollection", features: [] });

let currentlyEditingLayer = null;
let temporaryDrawingLayer = null;
let mapObject = null;
const isDrawing = ref(false);
const originalGeometryString = ref(null);

const currentUserRole = computed(() => authStore.userRole);
const currentUserId = computed(() => authStore.currentUser?.id);

const canDraw = computed(() => {
  return [ROLES.ADMIN, ROLES.CURATOR].includes(currentUserRole.value);
});

const isCurrentUserAdmin = computed(() => {
  return currentUserRole.value === ROLES.ADMIN;
});

watch(() => uiStore.isPanelOpen, async (isOpen, wasOpen) => {
  if (wasOpen && !isOpen) {
    if (currentlyEditingLayer) {
      currentlyEditingLayer.pm.disable();
      currentlyEditingLayer = null;
      originalGeometryString.value = null;
      await loadSectors();
    }
    if (temporaryDrawingLayer) {
      temporaryDrawingLayer.remove();
      temporaryDrawingLayer = null;
    }

    if (geoJsonLayer.value && geoJsonLayer.value.leafletObject.getBounds().isValid()) {
      const allSectorsBounds = geoJsonLayer.value.leafletObject.getBounds();
      const currentMapViewBounds = mapObject.getBounds();
      
      if (!currentMapViewBounds.contains(allSectorsBounds)) {
        const center = allSectorsBounds.getCenter();
        const zoom = mapObject.getBoundsZoom(allSectorsBounds);
        mapObject.setView(center, zoom);
      }
    }
  }
  if (mapObject) {
    mapObject.invalidateSize();
  }
});

const geoJsonStyle = (feature) => ({
  color: feature.properties.color,
  weight: 2,
  opacity: 1,
  fillOpacity: 0.3,
});

const openEditPanel = async (layer) => {
    if (currentlyEditingLayer) {
      currentlyEditingLayer.pm.disable();
    }

    const bounds = layer.getBounds();
    const center = bounds.getCenter();
    const zoom = mapObject.getBoundsZoom(bounds);
    mapObject.setView(center, zoom);
    
    layer.pm.enable({ allowSelfIntersection: false });
    currentlyEditingLayer = layer;
    originalGeometryString.value = JSON.stringify(layer.toGeoJSON().geometry);
    
    await fetchFormData();

    const feature = layer.feature;
    const sectorData = sectors.value.features.find(f => f.properties.id === feature.properties.id).properties;
    
    const props = {
      sectorData,
      curators: curatorList.value,
      teams: teamList.value,
      showCuratorSelection: isCurrentUserAdmin.value,
      preselectedCuratorId: currentUserId.value,
      onSave: handleSave,
    };
    
    uiStore.openPanel(CreateSectorForm, 'Редактирование участка', props);
};

const onEachFeature = (feature, layer) => {
  if (feature.properties && feature.properties.name) {
    layer.bindPopup(feature.properties.name);
  }

  if ([ROLES.ADMIN, ROLES.CURATOR].includes(currentUserRole.value)) {
    layer.on('click', (e) => {
      L.DomEvent.stopPropagation(e);
      const newLayer = e.target;

      if (isDrawing.value || mapObject.pm.globalRemovalModeEnabled() || newLayer === currentlyEditingLayer) {
        return;
      }

      const geometryIsDirty = currentlyEditingLayer && 
        JSON.stringify(currentlyEditingLayer.toGeoJSON().geometry) !== originalGeometryString.value;

      if (uiStore.isFormDirty || geometryIsDirty) {
        uiStore.showConfirmDialog({
          title: 'Несохраненные изменения',
          text: 'Вы уверены, что хотите отменить изменения? Все несохраненные данные будут потеряны.',
          onConfirm: () => {
            if (geometryIsDirty) {
              const originalGeometry = JSON.parse(originalGeometryString.value);
              const originalLatLngs = originalGeometry.coordinates[0].map(p => [p[1], p[0]]);
              currentlyEditingLayer.setLatLngs(originalLatLngs);
            }
            openEditPanel(newLayer);
          },
          onCancel: () => {},
        });
      } else {
        openEditPanel(newLayer);
      }
    });
  }
};

const geoJsonOptions = computed(() => ({
  onEachFeature: onEachFeature,
}));

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

const fetchFormData = async () => {
  if (curatorList.value.length > 0 && !isCurrentUserAdmin.value) return;
  if (curatorList.value.length > 0 && teamList.value.length > 0 && isCurrentUserAdmin.value) return;

  try {
    const usersPromise = userService.getAllUsers();
    const teamsPromise = isCurrentUserAdmin.value ? teamService.getTeams() : Promise.resolve({ data: [] });

    const [usersResponse, teamsResponse] = await Promise.all([usersPromise, teamsPromise]);
    
    curatorList.value = usersResponse.data.filter(
      (user) => user.role === ROLES.CURATOR
    );
    teamList.value = teamsResponse.data;
  } catch (error) {
    console.error("Ошибка при загрузке данных для формы:", error);
  }
};

const onMapReady = (map) => {
  mapObject = map;

  if (canDraw.value) {
    mapObject.pm.setLang("ru");

    mapObject.pm.addControls({
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
    
    mapObject.on('pm:drawstart', () => {
        isDrawing.value = true;
    });
    
    mapObject.on('pm:drawend', () => {
        isDrawing.value = false;
    });

    mapObject.on("pm:create", async (e) => {
      const bounds = e.layer.getBounds();
      const center = bounds.getCenter();
      const zoom = mapObject.getBoundsZoom(bounds);
      mapObject.setView(center, zoom);

      const existingColors = sectors.value.features.map(f => f.properties.color);
      const newColor = generateUniqueRandomColor(existingColors);
      
      temporaryDrawingLayer = e.layer;
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
      uiStore.openPanel(CreateSectorForm, 'Создание участка', props);
    });

    mapObject.on("pm:remove", (e) => {
      const sectorId = e.layer.feature.properties.id;
      const sectorName = e.layer.feature.properties.name;

      uiStore.showConfirmDialog({
        title: 'Подтвердите удаление',
        text: `Вы уверены, что хотите удалить участок "${sectorName}"?`,
        onConfirm: async () => {
          try {
            await sectorService.deleteSector(sectorId);
            await loadSectors();
          } catch (error) {
            e.layer.addTo(mapObject);
            const errorDetail = error.response?.data?.detail || error.message;
            uiStore.showInfoDialog(`Участок "${sectorName}" не был удален`, errorDetail);
          }
        },
        onCancel: () => {
          e.layer.addTo(mapObject);
        }
      });
    });
  }
};

const handleSave = async (data) => {
  const isUpdating = !!data.id;
  let payload = { ...data };
  
  if (isUpdating) {
    const updatedGeometry = currentlyEditingLayer.toGeoJSON().geometry;
    payload.geometry = updatedGeometry;
  }
  
  try {
    if (isUpdating) {
      await sectorService.updateSector(payload.id, payload);
    } else {
      await sectorService.createSector(payload);
    }

    if(temporaryDrawingLayer) {
        temporaryDrawingLayer.remove();
        temporaryDrawingLayer = null;
    }
    
    originalGeometryString.value = null;
    await loadSectors();
    uiStore.closePanel();
  } catch (error) {
    const errorDetail = error.response?.data?.detail || JSON.stringify(error.response?.data) || error.message;
    uiStore.showInfoDialog("Ошибка сохранения", `Не удалось сохранить участок. ${errorDetail}`);
  }
};

onMounted(() => {
  loadSectors();
});
</script>

<style scoped>
.map-container {
  height: 100%;
  width: 100%;
}
</style>
