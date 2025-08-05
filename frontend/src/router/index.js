import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from "@/stores/authStore";
import { useUiStore } from "@/stores/uiStore";
import { ROLES } from "@/constants/roles";

import AppLayout from "@/components/layouts/AppLayout.vue";
import LoginView from "@/views/LoginView.vue";
import RegisterView from "@/views/RegisterView.vue";
import MapView from "@/views/MapView.vue";
import TeamsView from "@/views/TeamsView.vue";
import UsersView from "@/views/UsersView.vue";
import DefectTypesView from "@/views/DefectTypesView.vue";

const routes = [
  {
    path: "/",
    component: AppLayout,
    children: [
      {
        path: "",
        name: "Map",
        component: MapView,
        meta: { isMapView: true },
      },
      {
        path: "sectors",
        name: "Sectors",
        component: MapView,
        meta: {
          requiresAuth: true,
          requiredRole: [ROLES.ADMIN, ROLES.CURATOR],
          isMapView: true,
        },
      },
      {
        path: "teams",
        name: "Teams",
        component: TeamsView,
        meta: {
          requiresAuth: true,
          requiredRole: [ROLES.ADMIN],
        },
      },
      {
        path: "users",
        name: "Users",
        component: UsersView,
        meta: {
          requiresAuth: true,
          requiredRole: [ROLES.ADMIN],
        },
      },
      {
        path: "defect-types",
        name: "DefectTypes",
        component: DefectTypesView,
        meta: {
          requiresAuth: true,
          requiredRole: [ROLES.ADMIN],
        },
      },
    ],
  },
  {
    path: "/login",
    name: "Login",
    component: LoginView,
  },
  {
    path: "/register",
    name: "Register",
    component: RegisterView,
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore();
  const uiStore = useUiStore();
  const requiresAuth = to.matched.some((record) => record.meta.requiresAuth);
  const requiredRole = to.meta.requiredRole;

  if (uiStore.isPanelOpen) {
    uiStore.closePanel();
  }

  if (requiresAuth && !authStore.isAuthenticated) {
    next({ name: "Login" });
  } else if (
    requiredRole &&
    (!authStore.userRole || !requiredRole.includes(authStore.userRole))
  ) {
    uiStore.showInfoDialog(
      "Ошибка доступа",
      "У вас нет прав для доступа к этой странице."
    );
    next(from.path === to.path ? "/" : from.path);
  } else {
    next();
  }
});

export default router;
