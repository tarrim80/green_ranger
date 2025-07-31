import "@mdi/font/css/materialdesignicons.css";
import { createApp } from "vue";
import { createPinia } from "pinia";
import App from "./App.vue";
import router from "./router";
import { useAuthStore } from "@/stores/auth";
import { applyLeafletLocalization } from "@/config/leaflet-localization";

import "vuetify/styles";
import { createVuetify } from "vuetify";
import * as components from "vuetify/components";
import * as directives from "vuetify/directives";
import colors from "vuetify/util/colors";

applyLeafletLocalization();

const vuetify = createVuetify({
  components,
  directives,
  theme: {
    themes: {
      light: {
        dark: false,
        colors: {
          primary: colors.teal.accent3,
          secondary: colors.grey.darken3,
        },
      },
    },
  },
});

const pinia = createPinia();
const app = createApp(App);

app.use(vuetify);
app.use(pinia);

const authStore = useAuthStore();

authStore.tryAutoLogin().then(() => {
  app.use(router);
  app.mount("#app");
});
