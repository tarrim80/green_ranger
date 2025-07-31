<template>
  <div style="height: 85vh; width: 100%">
    <l-map
      ref="map"
      v-model:zoom="zoom"
      :center="[43.238949, 76.889709]"
    >
      <l-tile-layer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        layer-type="base"
        name="OpenStreetMap"
        attribution="© <a href='http://www.openstreetmap.org/copyright'>OpenStreetMap</a> contributors"
      >
      </l-tile-layer>
    </l-map>
  </div>
</template>

<script setup>
import "leaflet/dist/leaflet.css";
import L from "leaflet";
import { LMap, LTileLayer } from "@vue-leaflet/vue-leaflet";
import { ref } from "vue";

const zoom = ref(12);
</script>
