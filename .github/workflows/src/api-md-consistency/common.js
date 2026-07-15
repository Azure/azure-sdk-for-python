#!/usr/bin/env node

import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";
import { execFile, isExecError } from "../../../shared/src/exec.js";
import { defaultLogger } from "../../../shared/src/logger.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = path.resolve(__dirname, "..", "..", "..", "..");

async function getDefaultLogger() {
  return defaultLogger;
}

async function runAsync(cmd, args, options = {}) {
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

export {
  REPO_ROOT,
  getDefaultLogger,
  runAsync,
  readLines,
  writeLines,
  appendGithubOutput,
  envPath,
  requireEnv,
};
