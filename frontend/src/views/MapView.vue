<template>
  <div class="map-container">
    <l-map :zoom="zoom" :center="center" @ready="onMapReady">
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
      ></l-geo-json>
    </l-map>

    <create-sector-modal
      v-model="isModalOpen"
      :curators="curatorList"
      :teams="teamList"
      :geometry="newSectorGeometry"
      :show-curator-selection="isCurrentUserAdmin"
      :preselected-curator-id="currentUserId"
      @save="handleSaveSector"
      @cancel="handleCancelCreation"
    />
  </div>
</template>

<script setup>
import "leaflet/dist/leaflet.css";
import "@geoman-io/leaflet-geoman-free/dist/leaflet-geoman.css";

import L from "leaflet";
import "@geoman-io/leaflet-geoman-free";

import { LMap, LTileLayer, LControlScale, LGeoJson } from "@vue-leaflet/vue-leaflet";
import { ref, computed, onMounted } from "vue";
import { useAuthStore } from "@/stores/auth";
import { ROLES } from "@/constants/roles";
import { INITIAL_CENTER, INITIAL_ZOOM } from "@/constants/map";
import { userService } from "@/services/userService";
import { teamService } from "@/services/teamService";
import { sectorService } from "@/services/sectorService";

import CreateSectorModal from "@/components/CreateSectorModal.vue";

const zoom = ref(INITIAL_ZOOM);
const center = ref(INITIAL_CENTER);
const authStore = useAuthStore();

const isModalOpen = ref(false);
const newSectorGeometry = ref({});
const curatorList = ref([]);
const teamList = ref([]);
const sectors = ref({ type: "FeatureCollection", features: [] });
let drawnLayerGroup = null;

const currentUserRole = computed(() => authStore.userRole);
const currentUserId = computed(() => authStore.currentUser?.id);

const canDraw = computed(() => {
  return [ROLES.ADMIN, ROLES.CURATOR].includes(currentUserRole.value);
});

const isCurrentUserAdmin = computed(() => {
  return currentUserRole.value === ROLES.ADMIN;
});

const geoJsonStyle = (feature) => {
  return {
    color: feature.properties.color,
    weight: 2,
    opacity: 1,
    fillOpacity: 0.3,
  };
};

const geoJsonOptions = {
  onEachFeature: (feature, layer) => {
    if (feature.properties && feature.properties.name) {
      layer.bindPopup(feature.properties.name);
    }
  },
};

const loadSectors = async () => {
  try {
    const response = await sectorService.getSectors();
    const features = response.data.map((sector) => ({
      type: "Feature",
      properties: {
        name: sector.name,
        color: sector.color,
      },
      geometry: sector.geometry,
    }));
    sectors.value = { type: "FeatureCollection", features: features };
  } catch (error) {
    console.error("Ошибка при загрузке участков:", error);
  }
};

const fetchRequiredData = async () => {
  try {
    const usersResponse = await userService.getAllUsers();
    curatorList.value = usersResponse.data.filter(
      (user) => user.role === ROLES.CURATOR
    );
    
    if (isCurrentUserAdmin.value) {
      const teamsResponse = await teamService.getTeams();
      teamList.value = teamsResponse.data;
    }
  } catch (error) {
    console.error("Ошибка при загрузке данных:", error);
  }
};

const onMapReady = (mapObject) => {
  drawnLayerGroup = new L.FeatureGroup();
  mapObject.addLayer(drawnLayerGroup);

  if (canDraw.value) {
    mapObject.pm.setLang("ru");
    mapObject.pm.addControls({
      position: "topleft",
      drawPolygon: true,
      drawMarker: false,
      drawCircleMarker: false,
      drawPolyline: false,
      drawRectangle: false,
      drawCircle: false,
      drawText: false,
      editMode: true,
      dragMode: false,
      cutPolygon: false,
      removalMode: true,
      rotateMode: false,
    });
    mapObject.on("pm:create", async (e) => {
      await fetchRequiredData();
      
      const layer = e.layer;
      drawnLayerGroup.addLayer(layer);
      newSectorGeometry.value = layer.toGeoJSON().geometry;
      isModalOpen.value = true;
    });
  }
};

const handleSaveSector = async (sectorData) => {
  try {
    await sectorService.createSector(sectorData);
    alert(`Участок "${sectorData.name}" успешно создан!`);
    drawnLayerGroup.clearLayers();
    await loadSectors();
  } catch (error) {
    console.error("Ошибка при создании участка:", error);
    alert(`Не удалось создать участок. Ошибка: ${JSON.stringify(error.response?.data)}`);
  }
};

const handleCancelCreation = () => {
  if (drawnLayerGroup) {
    drawnLayerGroup.clearLayers();
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
