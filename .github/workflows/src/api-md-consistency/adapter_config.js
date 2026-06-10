#!/usr/bin/env node

import fs from "fs";
import path from "path";
import { fileURLToPath, pathToFileURL } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

const DEFAULT_CONFIG = {
  adapter: "python",
};

export function loadWorkflowConfig() {
  const configPath = path.join(__dirname, "api_md_workflow.config.json");
  if (!fs.existsSync(configPath)) {
    return { ...DEFAULT_CONFIG };
  }

  const raw = fs.readFileSync(configPath, "utf-8");
  let parsed;
  try {
    parsed = JSON.parse(raw);
  } catch (error) {
    throw new Error(
      `ERROR: invalid JSON in ${configPath}: ${error instanceof Error ? error.message : String(error)}`,
    );
  }

  if (!parsed || typeof parsed !== "object") {
    throw new Error(`ERROR: ${configPath} must contain a JSON object.`);
  }

  return {
    ...DEFAULT_CONFIG,
    ...parsed,
  };
}

export async function loadAdapter(name) {
  const adapterPath = path.join(__dirname, "adapters", `${name}.js`);
  if (!fs.existsSync(adapterPath)) {
    throw new Error(`ERROR: adapter '${name}' not found at ${adapterPath}`);
  }

  return import(pathToFileURL(adapterPath).href);
}
