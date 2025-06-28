import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      "/send-email": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
      "/screenshots": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
});
