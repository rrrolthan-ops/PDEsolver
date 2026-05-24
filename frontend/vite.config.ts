/// <reference types="vitest" />
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    strictPort: true,
    host: true,
  },
  test: {
    globals: true,
    environment: "jsdom",
    setupFiles: ["./src/test-setup.ts"],
    css: false,
    // The e2e/ directory is for Playwright tests — they have a different
    // runtime (real browser + real backend) and would crash under Vitest.
    exclude: ["**/node_modules/**", "**/dist/**", "e2e/**"],
  },
});
