<template>
  <v-layout>
    <v-app-bar color="primary" height="48">
      <v-app-bar-title>Зелёный Рейнджер</v-app-bar-title>
      <v-spacer></v-spacer>
      <v-btn v-if="!authStore.isAuthenticated" to="/login">Войти</v-btn>
      <v-btn v-else @click="authStore.logout()">Выйти</v-btn>
    </v-app-bar>

    <v-navigation-drawer v-if="authStore.isAuthenticated" permanent>
      <v-list-item
          v-if="authStore.currentUser"
          :title="authStore.userFullname"
          :subtitle="authStore.currentUser.role"
      ></v-list-item>
      <v-divider></v-divider>

      <admin-sidebar v-if="authStore.userRole === ROLES.ADMIN" />
      <curator-sidebar v-else-if="authStore.userRole === ROLES.CURATOR" />
      <volunteer-sidebar v-else-if="authStore.userRole === ROLES.VOLUNTEER" />
      <default-sidebar v-else />
    </v-navigation-drawer>

    <side-panel-form-layout v-if="uiStore.isPanelOpen" />

    <v-main style="position: relative">
      <base-map @ready="handleMapReady" />
      <div style="position: absolute; top: 10px; left: 60px; z-index: 1000">
        <router-view />
      </div>
    </v-main>
  </v-layout>
</template>

<script setup>
import { useAuthStore } from "@/stores/auth";
import { useMapStore } from "@/stores/mapStore";
import { ROLES } from "@/constants/roles";
import AdminSidebar from "@/views/sidebars/AdminSidebar.vue";
import CuratorSidebar from "@/views/sidebars/CuratorSidebar.vue";
import VolunteerSidebar from "@/views/sidebars/VolunteerSidebar.vue";
import DefaultSidebar from "@/views/sidebars/DefaultSidebar.vue";
import BaseMap from "@/components/BaseMap.vue";
import SidePanelFormLayout from "@/components/layouts/SidePanelFormLayout.vue";
import { useUiStore } from "@/stores/uiStore";

const authStore = useAuthStore();
const mapStore = useMapStore();
const uiStore = useUiStore();

const handleMapReady = (map) => {
  mapStore.setMapInstance(map);
};
</script>
