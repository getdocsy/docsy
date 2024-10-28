import { defineConfig } from "tsup";

export default defineConfig({
  clean: true,
  entry: ['./src/index.ts'],
  outDir: "dist",
  external: ['readline'],
  format: ['esm',],
});