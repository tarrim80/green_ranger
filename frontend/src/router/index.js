import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from "@/stores/auth";
import { ROLES } from "@/constants/roles";

import MainLayout from "@/components/layouts/MainLayout.vue";
import LoginView from "@/views/LoginView.vue";
import MapView from "@/views/MapView.vue";
import TeamsView from "@/views/TeamsView.vue";

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
      {
        path: "teams",
        name: "Teams",
        component: TeamsView,
        meta: { requiresAuth: true, requiredRole: ROLES.ADMIN },
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
});

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore();
  const requiresAuth = to.matched.some((record) => record.meta.requiresAuth);
  const requiredRole = to.meta.requiredRole;

  if (requiresAuth && !authStore.isAuthenticated) {
    next({ name: "Login" });
  } else if (requiredRole && authStore.userRole !== requiredRole) {
    alert("У вас нет прав для доступа к этой странице.");
    next(from.path === to.path ? "/" : from.path);
  } else {
    next();
  }
});

export default router;
