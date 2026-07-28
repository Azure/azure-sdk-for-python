#!/usr/bin/env node

import path from "path";

import { REPO_ROOT, envPath, getDefaultLogger, readLines } from "./common.js";
import { loadAdapter, loadWorkflowConfig } from "./adapter_config.js";

async function main() {
  const logger = await getDefaultLogger();
  const config = loadWorkflowConfig();
  const adapter = await loadAdapter(config.adapter);
  if (typeof adapter.generateApiForPackage !== "function") {
    throw new Error(
      `ERROR: adapter '${config.adapter}' does not implement generateApiForPackage({ repoRoot, packageName, runtimeExecutable }).`,
    );
  }

  const packagesFile = envPath("API_MD_PACKAGES_FILE", ".artifacts/affected_package_dirs.txt");
  const packages = readLines(packagesFile);
  if (!packages.length) {
    return;
  }

  const runtimeExecutable = process.env.RUNTIME_EXECUTABLE || null;
  for (const pkgDir of packages) {
    const packageName = path.basename(pkgDir);
    logger.info(`Generating api.md for ${packageName}`);
    await adapter.generateApiForPackage({
      repoRoot: REPO_ROOT,
      packageName,
      runtimeExecutable,
      logger,
    });
  }
}

main().catch(async (error) => {
  const logger = await getDefaultLogger();
  logger.error(error instanceof Error ? error.message : String(error));
  process.exit(1);
});
