<template>
  <div class="map-container">
    <l-map
      ref="mapRef"
      :zoom="props.zoom"
      :center="props.center"
      @ready="onMapReady"
    >
      <l-tile-layer
        :url="MAP_URL"
        layer-type="base"
        name="OpenStreetMap"
        :attribution="MAP_ATTRIBUTION"
      >
      </l-tile-layer>
      <l-control-scale position="bottomleft" :imperial="false" />
      <slot></slot>
    </l-map>
  </div>
</template>

<script setup>
import "leaflet/dist/leaflet.css";
import { LMap, LTileLayer, LControlScale } from "@vue-leaflet/vue-leaflet";
import { ref } from "vue";
import {
  INITIAL_CENTER,
  INITIAL_ZOOM,
  MAP_URL,
  MAP_ATTRIBUTION,
} from "@/constants/map";

const props = defineProps({
  zoom: {
    type: Number,
    default: INITIAL_ZOOM,
  },
  center: {
    type: Array,
    default: () => INITIAL_CENTER,
  },
});

const emit = defineEmits(["ready"]);

const mapRef = ref(null);

const onMapReady = () => {
  if (mapRef.value && mapRef.value.leafletObject) {
    emit("ready", mapRef.value.leafletObject);
  }
};
</script>

<style scoped>
.map-container {
  height: 100%;
  width: 100%;
}
</style>
