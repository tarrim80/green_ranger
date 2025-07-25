// frontend/src/router/index.js
import { createRouter, createWebHistory } from "vue-router";
import MainLayout from "@/components/layouts/MainLayout.vue";
import LoginView from "@/views/LoginView.vue";
import MapView from "@/views/MapView.vue";

const routes = [
  {
    path: "/",
    component: MainLayout,
    children: [
      {
        path: "",
        name: "Map",
        component: MapView,
      },
    ],
  },
  {
    path: "/login",
    name: "Login",
    component: LoginView,
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
  // Vite @ alias fix
  resolve: {
    alias: {
      "@": "/src",
    },
  },
});

export default router;
