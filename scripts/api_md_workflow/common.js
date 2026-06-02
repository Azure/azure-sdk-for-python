#!/usr/bin/env node

const fs = require("fs");
const path = require("path");
const { spawnSync } = require("child_process");

const REPO_ROOT = path.resolve(__dirname, "..", "..");
const DEFAULT_CONSISTENCY_MARKER = "<!-- api-md-consistency-comment -->";
const DEFAULT_APPLY_MARKER = "<!-- api-md-apply-result-comment -->";

function run(cmd, args, options = {}) {
  const result = spawnSync(cmd, args, {
    check: false,
    cwd: options.cwd,
    env: options.env,
    encoding: "utf-8",
    stdio: options.capture ? "pipe" : "inherit",
  });

  if ((options.check ?? true) && result.status !== 0) {
    throw new Error(`Command failed (${result.status}): ${[cmd, ...args].join(" ")}`);
  }

  return result;
}

function readLines(filePath) {
  if (!fs.existsSync(filePath)) {
    return [];
  }

  return fs
    .readFileSync(filePath, "utf-8")
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter((line) => Boolean(line));
}

function writeLines(filePath, lines) {
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
  if (!lines.length) {
    fs.writeFileSync(filePath, "", "utf-8");
    return;
  }
  fs.writeFileSync(filePath, `${lines.join("\n")}\n`, "utf-8");
}

function appendGithubOutput(key, value) {
  const outputPath = process.env.GITHUB_OUTPUT;
  if (!outputPath) {
    return;
  }

  fs.appendFileSync(outputPath, `${key}=${value}\n`, "utf-8");
}

function envPath(name, fallback) {
  return process.env[name] || fallback;
}

function requireEnv(name) {
  const value = process.env[name];
  if (!value) {
    throw new Error(`Environment variable ${name} is required`);
  }
  return value;
}

module.exports = {
  REPO_ROOT,
  DEFAULT_CONSISTENCY_MARKER,
  DEFAULT_APPLY_MARKER,
  run,
  readLines,
  writeLines,
  appendGithubOutput,
  envPath,
  requireEnv,
};
