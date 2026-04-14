import React from "react";
import ReactDOM from "react-dom/client";
import "@/index.css";
import App from "@/App";

// Suppress errors from browser extensions (MetaMask, etc.)
window.addEventListener('error', (event) => {
  if (event.filename && event.filename.startsWith('chrome-extension://')) {
    event.stopImmediatePropagation();
    event.preventDefault();
    return true;
  }
}, true);

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
