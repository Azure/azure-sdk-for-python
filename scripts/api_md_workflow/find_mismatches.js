#!/usr/bin/env node

const fs = require("fs");

const { appendGithubOutput, envPath, readLines, run, writeLines } = require("./common");

function main() {
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

    const trackedResult = run("git", ["ls-files", "--error-unmatch", "--", apiFile], {
      check: false,
    });
    if (trackedResult.status !== 0) {
      missing.push(apiFile);
      continue;
    }

    const diffResult = run("git", ["diff", "--quiet", "--", apiFile], {
      check: false,
    });
    if (diffResult.status !== 0) {
      mismatches.push(apiFile);
    }
  }

  writeLines(mismatchesFile, mismatches);
  writeLines(missingFile, missing);
  appendGithubOutput("mismatch_count", mismatches.length);
  appendGithubOutput("missing_count", missing.length);
  appendGithubOutput("issue_count", mismatches.length + missing.length);
}

try {
  main();
} catch (error) {
  console.error(error instanceof Error ? error.message : String(error));
  process.exit(1);
}
