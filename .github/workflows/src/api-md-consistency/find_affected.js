#!/usr/bin/env node

import {
  REPO_ROOT,
  appendGithubOutput,
  envPath,
  getDefaultLogger,
  requireEnv,
  runAsync,
  writeLines,
} from "./common.js";
import { loadAdapter, loadWorkflowConfig } from "./adapter_config.js";
import { includesSegment } from "../../../shared/src/path.js";

async function main() {
  const config = loadWorkflowConfig();
  const adapterName = config.adapter;
  const adapter = await loadAdapter(adapterName);
  if (typeof adapter.isPackageDir !== "function") {
    throw new Error(`ERROR: adapter '${adapterName}' does not implement isPackageDir(repoRoot, packageDirRelative).`);
  }

  const baseRef = requireEnv("API_MD_BASE_REF");
  const packagesFile = envPath("API_MD_PACKAGES_FILE", ".artifacts/affected_package_dirs.txt");
  const changedFile = envPath("API_MD_CHANGED_FILE", ".artifacts/changed_package_dirs.txt");

  await runAsync("git", ["fetch", "--no-tags", "--depth=1", "origin", baseRef], {
    cwd: REPO_ROOT,
  });
  const diff = (
    await runAsync("git", ["diff", "--name-only", `origin/${baseRef}..HEAD`], {
      cwd: REPO_ROOT,
    })
  ).stdout;

  const changedDirs = new Set();
  for (const filePath of diff.split(/\r?\n/)) {
    const trimmed = filePath.trim();
    if (!trimmed) {
      continue;
    }
    if (!includesSegment(trimmed, "sdk")) {
      continue;
    }

    const parts = trimmed.split("/");
    if (parts.length < 3 || parts[0] !== "sdk") {
      continue;
    }

    changedDirs.add(parts.slice(0, 3).join("/"));
  }

  const sortedChanged = [...changedDirs].sort();
  writeLines(changedFile, sortedChanged);

  const affected = [];
  for (const packageDir of sortedChanged) {
    if (adapter.isPackageDir(REPO_ROOT, packageDir)) {
      affected.push(packageDir);
    }
  }

  writeLines(packagesFile, affected);
  appendGithubOutput("count", affected.length);
}

main().catch(async (error) => {
  const logger = await getDefaultLogger();
  logger.error(error instanceof Error ? error.message : String(error));
  process.exit(1);
});
