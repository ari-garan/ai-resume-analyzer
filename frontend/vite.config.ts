import { createHash } from "node:crypto";
import { readdirSync, readFileSync, writeFileSync } from "node:fs";
import { relative, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { defineConfig } from "vite";

const frontendRoot = fileURLToPath(new URL(".", import.meta.url));

function sourceFiles(directory: string): string[] {
  return readdirSync(directory, { withFileTypes: true }).flatMap((entry) => {
    const path = resolve(directory, entry.name);
    return entry.isDirectory() ? sourceFiles(path) : [path];
  });
}

function sourceFingerprint(): string {
  const files = [
    ...sourceFiles(resolve(frontendRoot, "src")),
    resolve(frontendRoot, "index.html"),
    resolve(frontendRoot, "package.json"),
    resolve(frontendRoot, "vite.config.ts"),
  ].sort();
  const hash = createHash("sha256");
  for (const file of files) {
    hash.update(relative(frontendRoot, file).replaceAll("\\", "/")).update("\0");
    hash.update(readFileSync(file)).update("\0");
  }
  return hash.digest("hex");
}

export default defineConfig({
  plugins: [{
    name: "scoreboare-build-fingerprint",
    closeBundle() {
      writeFileSync(resolve(frontendRoot, "dist", ".build-source-hash"), sourceFingerprint());
    },
  }],
  server: {
    host: "127.0.0.1",
    port: 5173,
    proxy: { "/api": "http://127.0.0.1:8001" },
  },
  build: { outDir: "dist", emptyOutDir: true },
});
