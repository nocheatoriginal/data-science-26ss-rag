import { VectorDbView } from "./view.js";
import { VectorDbViewModel } from "./view-model.js";

function startApp() {
  const viewModel = new VectorDbViewModel();
  const view = new VectorDbView(viewModel);
  view.start();
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", startApp, { once: true });
} else {
  startApp();
}
