#!/usr/bin/env node

import fs from "fs";

import { appendGithubOutput, envPath, getDefaultLogger, readLines, runAsync, writeLines } from "./common.js";
import { loadAdapter, loadWorkflowConfig } from "./adapter_config.js";

/**
 * Parse a simple key: value YAML file into an object.
 * Only handles flat scalar mappings (no nesting, no multi-line values).
 */
function parseSimpleYaml(text) {
  const result = {};
  for (const line of text.split(/\r?\n/)) {
    const match = line.match(/^(\w+)\s*:\s*(.*)$/);
    if (match) {
      result[match[1]] = match[2].trim();
    }
  }
  return result;
}

async function main() {
  const config = loadWorkflowConfig();
  const adapter = await loadAdapter(config.adapter);

  // Fields to compare in api.metadata.yml. If the adapter doesn't specify,
  // compare all fields (strict default for languages that don't opt out).
  const fieldsToValidate = adapter.metadataFieldsToValidate || null;

  const packagesFile = envPath("API_MD_PACKAGES_FILE", ".artifacts/affected_package_dirs.txt");
  const mismatchesFile = envPath("API_MD_MISMATCHES_FILE", ".artifacts/mismatched_api_files.txt");
  const missingFile = envPath("API_MD_MISSING_FILE", ".artifacts/missing_api_files.txt");
  const packages = readLines(packagesFile);

  const mismatches = [];
  const missing = [];
  for (const pkgDir of packages) {
    const apiFile = `${pkgDir}/api.md`;
    const metadataFile = `${pkgDir}/api.metadata.yml`;

    // Enforce that each affected package has a committed api.md file.
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

    // api.metadata.yml must be present alongside api.md.
    if (!fs.existsSync(metadataFile) || !fs.statSync(metadataFile).isFile()) {
      missing.push(metadataFile);
    } else {
      const committedMeta = await runAsync("git", ["show", `HEAD:${metadataFile}`], {
        check: false,
      });
      if (committedMeta.status !== 0) {
        // Not yet committed — treat as missing
        missing.push(metadataFile);
      } else {
        const current = parseSimpleYaml(fs.readFileSync(metadataFile, "utf-8"));
        const committed = parseSimpleYaml(committedMeta.stdout);

        // Compare only adapter-specified fields, or all fields if not specified.
        const keys = fieldsToValidate || Object.keys({ ...committed, ...current });
        const mismatch = keys.some((key) => current[key] !== committed[key]);
        if (mismatch) {
          mismatches.push(metadataFile);
        }
      }
    }

    // Diff-gate the full api.md content; metadata is field-gated above.
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
