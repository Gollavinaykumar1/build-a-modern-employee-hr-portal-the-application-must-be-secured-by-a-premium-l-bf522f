import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  base: "/build-a-modern-employee-hr-portal-the-application-must-be-secured-by-a-premium-l-bf522f/",
  build: { outDir: "dist", assetsDir: "assets" },
  server: { port: 3000 },
});
