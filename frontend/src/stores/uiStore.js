import { defineStore } from "pinia";
import { markRaw } from "vue";

export const useUiStore = defineStore("ui", {
  state: () => ({
    isPanelOpen: false,
    panelComponent: null,
    panelProps: {},
    panelTitle: "",

    isInfoDialogOpen: false,
    infoDialogTitle: "",
    infoDialogText: "",

    isConfirmDialogOpen: false,
    confirmDialogTitle: "",
    confirmDialogText: "",
    confirmDialogOnConfirm: () => {},
    confirmDialogOnCancel: () => {},

    isFormDirty: false,
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
      this.isFormDirty = false;
    },

    showInfoDialog(title, text) {
      this.infoDialogTitle = title;
      this.infoDialogText = text;
      this.isInfoDialogOpen = true;
    },
    hideInfoDialog() {
      this.isInfoDialogOpen = false;
    },

    showConfirmDialog({ title, text, onConfirm, onCancel = () => {} }) {
      this.confirmDialogTitle = title;
      this.confirmDialogText = text;
      this.confirmDialogOnConfirm = onConfirm;
      this.confirmDialogOnCancel = onCancel;
      this.isConfirmDialogOpen = true;
    },
    hideConfirmDialog() {
      this.isConfirmDialogOpen = false;
      this.confirmDialogOnConfirm = () => {};
      this.confirmDialogOnCancel = () => {};
    },

    triggerConfirm() {
      this.confirmDialogOnConfirm();
      this.hideConfirmDialog();
    },

    triggerCancel() {
      this.confirmDialogOnCancel();
      this.hideConfirmDialog();
    },

    setFormDirty(isDirty) {
      this.isFormDirty = isDirty;
    },
  },
});
