<template>
  <div class="map-container">
    <l-map ref="mapInstance" :zoom="zoom" :center="center" @ready="onMapReady">
      <l-tile-layer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        layer-type="base"
        name="OpenStreetMap"
        attribution="© OpenStreetMap contributors"
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
    <confirm-dialog
      v-model="confirmDialog.isOpen"
      :title="confirmDialog.title"
      :text="confirmDialog.text"
      @confirm="confirmDialog.onConfirm"
      @cancel="confirmDialog.onCancel"
    />
  </div>
</template>

<script setup>
import "leaflet/dist/leaflet.css";
import "@geoman-io/leaflet-geoman-free/dist/leaflet-geoman.css";

import L from "leaflet";
import "@geoman-io/leaflet-geoman-free";

import { LMap, LTileLayer, LControlScale, LGeoJson } from "@vue-leaflet/vue-leaflet";
import { ref, computed, onMounted, nextTick, watch } from "vue";

import { useAuthStore } from "@/stores/auth";
import { useUiStore } from "@/stores/uiStore";

import { ROLES } from "@/constants/roles";
import { INITIAL_CENTER, INITIAL_ZOOM } from "@/constants/map";

import { userService } from "@/services/userService";
import { teamService } from "@/services/teamService";
import { sectorService } from "@/services/sectorService";
import { generateUniqueRandomColor } from "@/utils/colorGenerator";

import CreateSectorForm from "@/components/CreateSectorForm.vue";
import ConfirmDialog from "@/components/ConfirmDialog.vue";

const mapInstance = ref(null);
const zoom = ref(INITIAL_ZOOM);
const center = ref(INITIAL_CENTER);

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

const confirmDialog = ref({
  isOpen: false,
  title: '',
  text: '',
  onConfirm: () => {},
  onCancel: () => {},
});

const currentUserRole = computed(() => authStore.userRole);
const currentUserId = computed(() => authStore.currentUser?.id);

const canDraw = computed(() => {
  return [ROLES.ADMIN, ROLES.CURATOR].includes(currentUserRole.value);
});

const isCurrentUserAdmin = computed(() => {
  return currentUserRole.value === ROLES.ADMIN;
});

watch(() => uiStore.isPanelOpen, (isOpen, wasOpen) => {
  if (wasOpen && !isOpen) {
    if (currentlyEditingLayer) {
      currentlyEditingLayer.pm.disable();
      currentlyEditingLayer = null;
      loadSectors();
    }
    if (temporaryDrawingLayer) {
      temporaryDrawingLayer.remove();
      temporaryDrawingLayer = null;
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

const onEachFeature = (feature, layer) => {
  if (feature.properties && feature.properties.name) {
    layer.bindPopup(feature.properties.name);
  }

  layer.on('click', async (e) => {
    L.DomEvent.stopPropagation(e);
    
    if (isDrawing.value || mapObject.pm.globalRemovalModeEnabled()) {
      return;
    }

    if (currentlyEditingLayer) {
      currentlyEditingLayer.pm.disable();
    }
    
    layer.pm.enable({ allowSelfIntersection: false });
    currentlyEditingLayer = layer;
    
    await fetchFormData();
    
    const props = {
      sectorData: { id: feature.properties.id, ...feature.properties },
      curators: curatorList.value,
      teams: teamList.value,
      showCuratorSelection: isCurrentUserAdmin.value,
      preselectedCuratorId: currentUserId.value,
      onSave: handleSave,
    };
    
    uiStore.openPanel(CreateSectorForm, 'Редактирование участка', props);
  });
};

const geoJsonOptions = computed(() => ({
  onEachFeature: onEachFeature,
}));

const loadSectors = async () => {
  try {
    const response = await sectorService.getSectors();
    const features = response.data.map((sector) => ({
      type: "Feature",
      properties: {
        id: sector.id,
        name: sector.name,
        color: sector.color,
        curator_id: sector.curator.id,
        team_id: sector.team ? sector.team.id : null,
      },
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
      drawPolygon: {
        allowIntersection: false,
      },
      drawMarker: false,
      drawCircleMarker: false,
      drawPolyline: false,
      drawRectangle: false,
      drawCircle: false,
      drawText: false,
      editMode: false,
      dragMode: false,
      cutPolygon: false,
      removalMode: true,
      rotateMode: false,
    });
    
    mapObject.on('pm:drawstart', () => {
        isDrawing.value = true;
    });
    
    mapObject.on('pm:drawend', () => {
        isDrawing.value = false;
    });

    mapObject.on("pm:create", async (e) => {
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

      confirmDialog.value = {
        isOpen: true,
        title: 'Подтвердите удаление',
        text: `Вы уверены, что хотите удалить участок "${sectorName}"?`,
        onConfirm: async () => {
          try {
            await sectorService.deleteSector(sectorId);
            await loadSectors();
          } catch (error) {
            console.error("Ошибка при удалении участка:", error);
            alert("Не удалось удалить участок.");
            await loadSectors();
          }
        },
        onCancel: () => {
          e.layer.addTo(mapObject);
        }
      };
    });
  }
};

const handleSave = async (data) => {
  const isUpdating = !!data.id;
  let payload = data;
  
  if (isUpdating) {
    const updatedGeometry = currentlyEditingLayer.toGeoJSON().geometry;
    payload = { ...data, geometry: updatedGeometry };
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

    await loadSectors();
    uiStore.closePanel();
  } catch (error) {
    console.error("Ошибка сохранения:", error);
    alert(`Ошибка: ${JSON.stringify(error.response?.data)}`);
  }
};

onMounted(() => {
  loadSectors();
});
</script>

<style scoped>
.map-container {
  height: 85vh;
  width: 100%;
}
</style>
