#!/usr/bin/env node

const path = require("path");

const { REPO_ROOT, envPath, getDefaultLogger, readLines } = require("./common");
const { loadAdapter, loadWorkflowConfig } = require("./adapter_config");

async function main() {
  const logger = await getDefaultLogger();
  const config = loadWorkflowConfig();
  const adapter = loadAdapter(config.adapter);
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
