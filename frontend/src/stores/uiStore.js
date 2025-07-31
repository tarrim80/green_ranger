import { defineStore } from "pinia";
import { markRaw } from "vue";

export const useUiStore = defineStore("ui", {
  state: () => ({
    isPanelOpen: false,
    panelComponent: null,
    panelProps: {},
    panelTitle: "",
  }),
  actions: {
    openPanel(component, title, props = {}) {
      this.panelComponent = markRaw(component);
      this.panelTitle = title;
      this.panelProps = props;
      this.isPanelOpen = true;
    },
    closePanel() {
      this.isPanelOpen = false;
      this.panelComponent = null;
      this.panelProps = {};
      this.panelTitle = "";
    },
  },
});
