#!/usr/bin/env node

const fs = require("fs");
const path = require("path");

const DEFAULT_CONFIG = {
  adapter: "python",
};

function loadWorkflowConfig() {
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

function loadAdapter(name) {
  const adapterPath = path.join(__dirname, "adapters", `${name}.js`);
  if (!fs.existsSync(adapterPath)) {
    throw new Error(`ERROR: adapter '${name}' not found at ${adapterPath}`);
  }

  // eslint-disable-next-line global-require, import/no-dynamic-require
  return require(adapterPath);
}

module.exports = {
  loadWorkflowConfig,
  loadAdapter,
};
