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
          @click="toggleProfileView"
          :active="isProfileViewActive"
      >
        <template v-slot:prepend>
          <v-icon size="36">mdi-account-circle</v-icon>
        </template>
      </v-list-item>
      <v-divider></v-divider>

      <div class="sidebar-content">
        <v-slide-y-transition hide-on-leave>
          <div v-if="!isProfileViewActive" class="sidebar-menu">
            <admin-sidebar v-if="authStore.userRole === ROLES.ADMIN" />
            <curator-sidebar v-else-if="authStore.userRole === ROLES.CURATOR" />
            <volunteer-sidebar v-else-if="authStore.userRole === ROLES.VOLUNTEER" />
            <default-sidebar v-else />
          </div>
        </v-slide-y-transition>
        
        <transition :name="profileTransitionName">
          <div v-if="isProfileViewActive">
            <user-profile-form @close="toggleProfileView" />
          </div>
        </transition>
      </div>
    </v-navigation-drawer>

    <side-panel-form-layout v-if="uiStore.isPanelOpen" />

    <v-main>
       <router-view v-slot="{ Component, route }">
        <div v-if="route.meta.isMapView" style="height: 100%; width: 100%;">
          <component :is="Component" />
        </div>
        <v-container fluid v-else>
          <component :is="Component" />
        </v-container>
      </router-view>
    </v-main>
  </v-layout>
</template>

<script setup>
import { ref } from 'vue';
import { useAuthStore } from "@/stores/auth";
import { useUiStore } from "@/stores/uiStore";
import { ROLES } from "@/constants/roles";

import SidePanelFormLayout from "@/components/layouts/SidePanelFormLayout.vue";
import UserProfileForm from '@/components/UserProfileForm.vue';
import AdminSidebar from "@/views/sidebars/AdminSidebar.vue";
import CuratorSidebar from "@/views/sidebars/CuratorSidebar.vue";
import VolunteerSidebar from "@/views/sidebars/VolunteerSidebar.vue";
import DefaultSidebar from "@/views/sidebars/DefaultSidebar.vue";

const authStore = useAuthStore();
const uiStore = useUiStore();

const isProfileViewActive = ref(false);
const profileTransitionName = ref('expand');

const toggleProfileView = () => {
  if (isProfileViewActive.value) {
    profileTransitionName.value = 'fade-out';
  } else {
    profileTransitionName.value = 'expand';
  }
  isProfileViewActive.value = !isProfileViewActive.value;
};

const params = new URLSearchParams(window.location.search);
if (params.get("logout") === "1") {
  authStore.clearAuthData();
  window.history.replaceState(history.state, "", "/");
};
</script>

<style>
.sidebar-content {
  overflow: hidden;
  position: relative;
}
.sidebar-menu {
  transition: opacity 0.3s ease-in-out;
}
.expand-enter-active, .expand-leave-active {
  transition: all 0.3s ease-in-out;
  overflow: hidden;
}
.expand-enter-from, .expand-leave-to {
  max-height: 0;
  opacity: 0;
}
.expand-enter-to, .expand-leave-from {
  max-height: 500px;
  opacity: 1;
}
.fade-out-leave-active {
  transition: opacity 0.1s ease;
  position: absolute;
  width: 100%;
}
.fade-out-leave-to {
  opacity: 0;
}
</style>
