import fs from "fs";
import path from "path";
import { execFile } from "../../../shared/src/exec.js";

const ANSI = {
  bold: "\u001b[1m",
  cyan: "\u001b[36m",
  yellow: "\u001b[33m",
  reset: "\u001b[0m",
};

function styleLog(text, ...styles) {
  return `${styles.join("")}${text}${ANSI.reset}`;
}

async function runNode(scriptRelativePath, workspace, core) {
  await execFile("node", [scriptRelativePath], {
    cwd: workspace,
    logger: core,
    logOutput: true,
  });
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
    lines.push("============================================================");
    lines.push(styleLog(`PACKAGE: ${packageName}`, ANSI.bold, ANSI.cyan));
    lines.push(`PATH:    ${packageDir}`);
    lines.push(`API FILE: ${apiFile}`);
    lines.push(styleLog(`Regenerate from the ${packageName} package root:`, ANSI.bold, ANSI.yellow));
    lines.push(styleLog(`  azpysdk apistub .`, ANSI.bold, ANSI.yellow));
    lines.push("============================================================");
  }
  lines.push("");
  return lines.join("\n");
}

export default async function apiMdConsistency({ core }) {
  const workspace = process.env.GITHUB_WORKSPACE || process.cwd();

  await runNode(".github/workflows/src/api-md-consistency/find_affected.js", workspace, core);

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

  await runNode(".github/workflows/src/api-md-consistency/regenerate.js", workspace, core);
  await runNode(".github/workflows/src/api-md-consistency/find_mismatches.js", workspace, core);

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
      "To regenerate api.md and api.metadata.yml locally, run the command shown for each package from the repository root.",
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
