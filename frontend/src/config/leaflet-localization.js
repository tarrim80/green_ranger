import L from "leaflet";

export function applyLeafletLocalization() {
  L.Control.Zoom.prototype.options.zoomInTitle = "Приблизить";
  L.Control.Zoom.prototype.options.zoomOutTitle = "Отдалить";
}
