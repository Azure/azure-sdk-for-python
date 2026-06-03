#!/usr/bin/env node

const fs = require("fs");
const path = require("path");
const { pathToFileURL } = require("url");

const REPO_ROOT = path.resolve(__dirname, "..", "..");
const SHARED_SRC_ROOT = path.join(REPO_ROOT, ".github", "shared", "src");
const sharedModuleCache = new Map();

async function loadSharedModule(fileName) {
  if (sharedModuleCache.has(fileName)) {
    return sharedModuleCache.get(fileName);
  }

  const filePath = path.join(SHARED_SRC_ROOT, fileName);
  const modulePromise = import(pathToFileURL(filePath).href);
  sharedModuleCache.set(fileName, modulePromise);
  return modulePromise;
}

async function getDefaultLogger() {
  const { defaultLogger } = await loadSharedModule("logger.js");
  return defaultLogger;
}

async function runAsync(cmd, args, options = {}) {
  const { execFile, isExecError } = await loadSharedModule("exec.js");
  const check = options.check ?? true;
  const logger = options.logger ?? (await getDefaultLogger());

  try {
    const result = await execFile(cmd, args, {
      cwd: options.cwd,
      logger,
      maxBuffer: options.maxBuffer,
    });

    return {
      status: 0,
      stdout: result.stdout ?? "",
      stderr: result.stderr ?? "",
    };
  } catch (error) {
    if (!isExecError(error)) {
      throw error;
    }

    const status = Number.isInteger(error.code) ? error.code : 1;
    const stdout = error.stdout ?? "";
    const stderr = error.stderr ?? "";

    if (!check) {
      return { status, stdout, stderr };
    }

    throw new Error(`Command failed (${status}): ${[cmd, ...args].join(" ")}`);
  }
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
  loadSharedModule,
  getDefaultLogger,
  runAsync,
  readLines,
  writeLines,
  appendGithubOutput,
  envPath,
  requireEnv,
};
