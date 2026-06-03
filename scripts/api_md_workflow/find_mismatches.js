#!/usr/bin/env node

const fs = require("fs");

const { appendGithubOutput, envPath, getDefaultLogger, readLines, runAsync, writeLines } = require("./common");

async function main() {
  const packagesFile = envPath("API_MD_PACKAGES_FILE", ".artifacts/affected_package_dirs.txt");
  const mismatchesFile = envPath("API_MD_MISMATCHES_FILE", ".artifacts/mismatched_api_files.txt");
  const missingFile = envPath("API_MD_MISSING_FILE", ".artifacts/missing_api_files.txt");
  const packages = readLines(packagesFile);

  const mismatches = [];
  const missing = [];
  for (const pkgDir of packages) {
    const apiFile = `${pkgDir}/API.md`;

    // Enforce that each affected package has a committed API.md file.
    if (!fs.existsSync(apiFile) || !fs.statSync(apiFile).isFile()) {
      missing.push(apiFile);
      continue;
    }

    const diffResult = await runAsync("git", ["ls-files", "--error-unmatch", "--", apiFile], {
      check: false,
    });
    if (diffResult.status !== 0) {
      missing.push(apiFile);
      continue;
    }

    const quietDiffResult = await runAsync("git", ["diff", "--quiet", "--", apiFile], {
      check: false,
    });
    if (quietDiffResult.status !== 0) {
      mismatches.push(apiFile);
    }
  }

  writeLines(mismatchesFile, mismatches);
  writeLines(missingFile, missing);
  appendGithubOutput("mismatch_count", mismatches.length);
  appendGithubOutput("missing_count", missing.length);
  appendGithubOutput("issue_count", mismatches.length + missing.length);
}

main().catch(async (error) => {
  const logger = await getDefaultLogger();
  logger.error(error instanceof Error ? error.message : String(error));
  process.exit(1);
});
