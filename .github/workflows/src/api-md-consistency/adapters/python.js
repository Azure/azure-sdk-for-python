#!/usr/bin/env node

import fs from "fs";
import path from "path";
import { spawnSync } from "child_process";

function run(cmd, args, options = {}) {
  const logger = options.logger || console;
  const printable = [cmd, ...args].join(" ");
  logger.info(`$ ${printable}`);
  const result = spawnSync(cmd, args, {
    cwd: options.cwd,
    env: options.env,
    encoding: "utf-8",
    stdio: options.capture ? "pipe" : "inherit",
    shell: options.shell ?? false,
  });

  if (result.error) {
    const errorMessage = result.error instanceof Error ? result.error.message : String(result.error);
    throw new Error(`Command failed to start: ${printable}\n${errorMessage}`);
  }

  if ((options.check ?? true) && result.status !== 0) {
    throw new Error(`Command failed (${result.status}): ${printable}`);
  }

  return result;
}

function findPackageDir(repoRoot, packageName) {
  const sdkDir = path.join(repoRoot, "sdk");
  const serviceDirs = fs.readdirSync(sdkDir, { withFileTypes: true });
  const matches = [];

  for (const serviceDir of serviceDirs) {
    if (!serviceDir.isDirectory()) {
      continue;
    }

    const candidate = path.join(sdkDir, serviceDir.name, packageName);
    if (!fs.existsSync(candidate) || !fs.statSync(candidate).isDirectory()) {
      continue;
    }

    const hasBuildFile = fs.existsSync(path.join(candidate, "pyproject.toml")) || fs.existsSync(path.join(candidate, "setup.py"));
    if (hasBuildFile) {
      matches.push(candidate);
    }
  }

  if (matches.length === 0) {
    throw new Error(`ERROR: package '${packageName}' not found under sdk/*/`);
  }

  if (matches.length > 1) {
    throw new Error(`ERROR: multiple matches for '${packageName}': ${matches.join(", ")}`);
  }

  return matches[0];
}

function isPackageDir(repoRoot, packageDirRelative) {
  const candidate = path.join(repoRoot, packageDirRelative);
  if (!fs.existsSync(candidate) || !fs.statSync(candidate).isDirectory()) {
    return false;
  }

  return fs.existsSync(path.join(candidate, "pyproject.toml")) || fs.existsSync(path.join(candidate, "setup.py"));
}

function* walkFiles(startDir) {
  const entries = fs.readdirSync(startDir, { withFileTypes: true });
  for (const entry of entries) {
    const fullPath = path.join(startDir, entry.name);
    if (entry.isDirectory()) {
      yield* walkFiles(fullPath);
    } else {
      yield fullPath;
    }
  }
}

function readVersion(packageDir) {
  const versionRegex = /^\s*VERSION\s*[:=]\s*["']([^"']+)["']/m;
  const candidates = [];

  for (const file of walkFiles(packageDir)) {
    const name = path.basename(file);
    if (name === "_version.py" || name === "version.py") {
      // Skip generated code directories — they often contain stale versions
      const relative = path.relative(packageDir, file);
      if (relative.includes("_generated") || relative.includes("generated_")) {
        continue;
      }
      candidates.push(file);
    }
  }

  for (const candidate of candidates) {
    let text;
    try {
      text = fs.readFileSync(candidate, "utf-8");
    } catch {
      continue;
    }

    const match = text.match(versionRegex);
    if (match) {
      return match[1];
    }
  }

  throw new Error(`ERROR: could not find a version string in ${packageDir}`);
}

function generateApiForPackage({
  repoRoot,
  packageName,
  runtimeExecutable,
  logger,
  refLabel,
}) {
  const activeLogger = logger || console;
  if (refLabel) {
    activeLogger.info(`--- Generating api.md on ${refLabel} ---`);
  }

  const packageDir = findPackageDir(repoRoot, packageName);
  if (runtimeExecutable || process.env.RUNTIME_EXECUTABLE) {
    const pythonExecutable = runtimeExecutable || process.env.RUNTIME_EXECUTABLE;
    run(
      pythonExecutable,
      ["-m", "azpysdk.main", "apistub", packageName],
      {
        cwd: repoRoot,
        check: true,
        logger: activeLogger,
      },
    );
    return;
  }

  run("azpysdk", ["apistub", packageName], {
    cwd: repoRoot,
    check: true,
    logger: activeLogger,
    shell: process.platform === "win32",
  });
}

// Fields in api.metadata.yml that must match between working tree and committed version.
// pythonVersion is excluded because it varies across CI environments.
const metadataFieldsToValidate = ["apiMdSha256", "parserVersion"];
const name = "python";

export {
  name,
  isPackageDir,
  findPackageDir,
  readVersion,
  generateApiForPackage,
  metadataFieldsToValidate,
};
