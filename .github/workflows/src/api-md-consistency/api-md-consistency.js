const fs = require("fs");
const path = require("path");
const { spawnSync } = require("child_process");

function runNode(scriptRelativePath, workspace, core) {
  const result = spawnSync("node", [scriptRelativePath], {
    cwd: workspace,
    env: process.env,
    encoding: "utf-8",
  });

  if (result.stdout) {
    core.info(result.stdout.trimEnd());
  }
  if (result.stderr) {
    core.info(result.stderr.trimEnd());
  }
  if (result.status !== 0) {
    throw new Error(`Command failed (${result.status}): node ${scriptRelativePath}`);
  }
}

function readLines(fileRelativePath, workspace) {
  const fullPath = path.join(workspace, fileRelativePath);
  if (!fs.existsSync(fullPath)) {
    return [];
  }

  return fs
    .readFileSync(fullPath, "utf-8")
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter((line) => Boolean(line));
}

function formatIssueSection(title, apiFiles) {
  if (!apiFiles.length) {
    return "";
  }

  const lines = [title];
  for (const apiFile of apiFiles) {
    const packageDir = apiFile.replace(/\/(api\.md|api\.metadata\.yml)$/, "");
    const packageName = path.basename(packageDir);
    lines.push(`- ${packageDir}`);
    lines.push(`  API file: ${apiFile}`);
    lines.push(`  Regenerate: azpysdk apistub --md --extract-metadata ${packageName} --dest-dir ${packageDir}`);
  }
  lines.push("");
  return lines.join("\n");
}

module.exports = async function apiMdConsistency({ core }) {
  const workspace = process.env.GITHUB_WORKSPACE || process.cwd();

  runNode("scripts/api_md_workflow/find_affected.js", workspace, core);

  const affected = readLines(process.env.API_MD_PACKAGES_FILE, workspace);
  const changedCount = affected.length;
  core.setOutput("changed_count", String(changedCount));

  if (changedCount === 0) {
    core.setOutput("mismatch_count", "0");
    core.setOutput("missing_count", "0");
    core.setOutput("issue_count", "0");
    return {
      changedCount,
      mismatchCount: 0,
      missingCount: 0,
      issueCount: 0,
    };
  }

  runNode("scripts/api_md_workflow/regenerate.js", workspace, core);
  runNode("scripts/api_md_workflow/find_mismatches.js", workspace, core);

  const mismatches = readLines(process.env.API_MD_MISMATCHES_FILE, workspace);
  const missing = readLines(process.env.API_MD_MISSING_FILE, workspace);

  const mismatchCount = mismatches.length;
  const missingCount = missing.length;
  const issueCount = mismatchCount + missingCount;

  core.setOutput("mismatch_count", String(mismatchCount));
  core.setOutput("missing_count", String(missingCount));
  core.setOutput("issue_count", String(issueCount));

  if (issueCount > 0) {
    const messageParts = [
      "Generated api.md or api.metadata.yml does not match the committed files, or required API files are missing, for one or more affected packages.",
      "api.metadata.yml must be committed alongside api.md, and selected metadata fields are part of pass/fail gating.",
      "",
      formatIssueSection("Mismatched packages:", mismatches),
      formatIssueSection("Missing required API files:", missing),
      "To regenerate api.md locally, run the command shown for each package from the repository root.",
    ].filter((part) => part !== "");

    core.setFailed(messageParts.join("\n"));
  }

  return {
    changedCount,
    mismatchCount,
    missingCount,
    issueCount,
  };
};
