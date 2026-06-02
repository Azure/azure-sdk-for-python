#!/usr/bin/env node

const fs = require("fs");
const path = require("path");
const { spawnSync } = require("child_process");

function run(cmd, args, options = {}) {
  const printable = [cmd, ...args].join(" ");
  console.log(`$ ${printable}`);
  const result = spawnSync(cmd, args, {
    cwd: options.cwd,
    env: options.env,
    encoding: "utf-8",
    stdio: options.capture ? "pipe" : "inherit",
  });

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

function generateApiMdBytes({
  repoRoot,
  packageName,
  packageDir,
  generateScriptPath,
  exportScriptPath,
  runtimeExecutable,
  refLabel,
}) {
  const executable = runtimeExecutable || process.env.PYTHON || "python";
  console.log(`--- Generating API.md on ${refLabel} ---`);
  const env = {
    ...process.env,
    AZSDK_REPO_ROOT: repoRoot,
    AZSDK_EXPORT_SCRIPT: exportScriptPath,
  };

  run(executable, [generateScriptPath, packageName], {
    cwd: repoRoot,
    env,
    check: true,
  });

  const apiMdPath = path.join(packageDir, "API.md");
  if (!fs.existsSync(apiMdPath)) {
    throw new Error(`ERROR: did not produce ${apiMdPath}`);
  }

  return fs.readFileSync(apiMdPath);
}

function generateApiForPackage({ repoRoot, packageName, runtimeExecutable }) {
  const executable = runtimeExecutable || process.env.PYTHON || "python";
  const generateScriptPath = path.join(repoRoot, "scripts", "generate_api_text.py");
  run(executable, [generateScriptPath, packageName], {
    cwd: repoRoot,
    check: true,
  });
}

module.exports = {
  name: "python",
  isPackageDir,
  findPackageDir,
  readVersion,
  generateApiForPackage,
  generateApiMdBytes,
};
