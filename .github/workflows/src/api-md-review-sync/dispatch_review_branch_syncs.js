#!/usr/bin/env node

import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

import { REPO_ROOT } from "../api-md-consistency/common.js";
import { readVersion } from "../api-md-consistency/adapters/python.js";

const REPO_OWNER = "Azure";
const REPO_NAME = "azure-sdk-for-python";
const REPO_SLUG = `${REPO_OWNER}/${REPO_NAME}`;
const SYNC_METADATA_MARKER = "api-md-review-sync";
const SYNC_METADATA_WARNING = "DO NOT MODIFY THESE CONTENTS!";
const SYNC_WORKFLOW_ID = "api-md-sync-review-branch.yml";
const SYNC_WORKFLOW_REF = "main";

function normalizePackageDir(packageDir) {
  const normalized = packageDir.trim().replace(/\\/g, "/");
  if (!normalized.startsWith("sdk/") || normalized.startsWith("/") || `/${normalized}/`.includes("/../")) {
    throw new Error(`ERROR: unsafe package directory: ${packageDir}`);
  }
  return normalized;
}

function readPackageDirs(packageFile) {
  if (!fs.existsSync(packageFile)) {
    throw new Error(`ERROR: package list file does not exist: ${packageFile}`);
  }

  return fs
    .readFileSync(packageFile, "utf-8")
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean)
    .map(normalizePackageDir);
}

function packageRecordFromDir(packageDir, repoRoot = REPO_ROOT) {
  const normalized = normalizePackageDir(packageDir);
  const packagePath = path.join(repoRoot, normalized);
  if (!fs.existsSync(packagePath) || !fs.statSync(packagePath).isDirectory()) {
    throw new Error(`ERROR: package directory does not exist: ${normalized}`);
  }

  return {
    packageName: path.basename(packagePath),
    packageDir: normalized,
    version: readVersion(packagePath),
  };
}

function buildTitleQuery(packageRecord) {
  return (
    `repo:${REPO_SLUG} is:pr is:open in:title ` +
    `"[API Review]" "${packageRecord.packageName}" "${packageRecord.version}"`
  );
}

function parseSyncMetadata(body) {
  const expression = new RegExp(
    `<!--\\s*${SYNC_METADATA_MARKER}\\s*\\n${SYNC_METADATA_WARNING}\\s*\\n([\\s\\S]*?)\\n\\s*-->`,
    "g",
  );
  const matches = [...String(body || "").matchAll(expression)];
  if (matches.length !== 1) {
    return undefined;
  }

  try {
    const parsed = JSON.parse(matches[0][1]);
    return parsed && typeof parsed === "object" && !Array.isArray(parsed) ? parsed : undefined;
  } catch {
    return undefined;
  }
}

function metadataMatches(metadata, packageRecord, workingBranch) {
  return (
    metadata.schemaVersion === 1 &&
    metadata.repository === REPO_SLUG &&
    metadata.packageName === packageRecord.packageName &&
    metadata.packageDir === packageRecord.packageDir &&
    metadata.workingOwner === workingBranch.owner &&
    metadata.workingBranch === workingBranch.branch &&
    typeof metadata.reviewBranch === "string" &&
    metadata.reviewBranch.startsWith("apireview/review_")
  );
}

async function githubRequest(method, apiPath, { token = process.env.GITHUB_TOKEN || process.env.GH_TOKEN, body } = {}) {
  const response = await fetch(`https://api.github.com${apiPath}`, {
    method,
    headers: {
      Accept: "application/vnd.github+json",
      "Content-Type": "application/json",
      "User-Agent": "azure-sdk-python-api-md-workflow",
      "X-GitHub-Api-Version": "2022-11-28",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: body === undefined ? undefined : JSON.stringify(body),
  });

  if (!response.ok) {
    throw new Error(`GitHub API request failed (${response.status}): ${await response.text()}`);
  }

  if (response.status === 204) {
    return undefined;
  }
  return await response.json();
}

async function searchPullRequests(query, limit = 50) {
  const graphqlQuery = `
query($query: String!, $first: Int!) {
  search(query: $query, type: ISSUE, first: $first) {
    nodes {
      ... on PullRequest {
        number
        url
        state
        updatedAt
        body
        headRefName
        headRepositoryOwner { login }
      }
    }
  }
}`;
  const data = await githubRequest("POST", "/graphql", {
    body: { query: graphqlQuery, variables: { query, first: limit } },
  });
  return data?.data?.search?.nodes?.filter(Boolean) || [];
}

async function createWorkflowDispatch(workflowId, ref, inputs) {
  await githubRequest("POST", `/repos/${REPO_SLUG}/actions/workflows/${workflowId}/dispatches`, {
    body: { ref, inputs },
  });
}

async function findMatchingReviewPrs({ searchPullRequestsFn = searchPullRequests, packageRecord, workingBranch }) {
  const candidates = await searchPullRequestsFn(buildTitleQuery(packageRecord), 50);
  const matches = [];
  const seenReviewBranches = new Set();

  for (const pr of candidates) {
    const metadata = parseSyncMetadata(pr.body);
    if (!metadata || !metadataMatches(metadata, packageRecord, workingBranch)) {
      continue;
    }

    if (seenReviewBranches.has(metadata.reviewBranch)) {
      continue;
    }
    seenReviewBranches.add(metadata.reviewBranch);
    matches.push({ pr, metadata });
  }

  return matches;
}

async function dispatchSync({ dispatchFn = createWorkflowDispatch, workflowId, workflowRef, packageRecord, workingBranch, reviewBranch, dryRun = false }) {
  const inputs = {
    packageDir: packageRecord.packageDir,
    reviewBranch,
    workingOwner: workingBranch.owner,
    workingBranch: workingBranch.branch,
    workingSha: workingBranch.sha,
  };

  if (dryRun) {
    console.log(`DRY RUN: would dispatch ${workflowId} for ${reviewBranch}: ${JSON.stringify(inputs)}`);
    return;
  }

  await dispatchFn(workflowId, workflowRef, inputs);
}

async function dispatchForPackages({
  packageDirs,
  workingBranch,
  workflowId = SYNC_WORKFLOW_ID,
  workflowRef = SYNC_WORKFLOW_REF,
  repoRoot = REPO_ROOT,
  searchPullRequestsFn = searchPullRequests,
  dispatchFn = createWorkflowDispatch,
  dryRun = false,
}) {
  if (workingBranch.branch.startsWith("apireview/")) {
    console.log(`Skipping API review branch ${workingBranch.owner}:${workingBranch.branch}.`);
    return 0;
  }

  let dispatchCount = 0;
  for (const packageDir of packageDirs) {
    const packageRecord = packageRecordFromDir(packageDir, repoRoot);
    const matches = await findMatchingReviewPrs({ searchPullRequestsFn, packageRecord, workingBranch });
    if (!matches.length) {
      console.log(`No matching API review PRs found for ${packageRecord.packageName} ${packageRecord.version}.`);
      continue;
    }

    for (const match of matches) {
      await dispatchSync({
        dispatchFn,
        workflowId,
        workflowRef,
        packageRecord,
        workingBranch,
        reviewBranch: match.metadata.reviewBranch,
        dryRun,
      });
      dispatchCount += 1;
      console.log(`Dispatched sync for PR #${match.pr.number} on ${match.metadata.reviewBranch}.`);
    }
  }

  console.log(`Dispatched ${dispatchCount} API review branch sync run(s).`);
  return dispatchCount;
}

function parseArgs(argv) {
  const args = {
    workflowId: SYNC_WORKFLOW_ID,
    workflowRef: SYNC_WORKFLOW_REF,
    repoRoot: REPO_ROOT,
    dryRun: false,
  };

  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];
    if (arg === "--dry-run") {
      args.dryRun = true;
      continue;
    }
    if (!arg.startsWith("--")) {
      throw new Error(`Unexpected argument: ${arg}`);
    }
    const key = arg.slice(2).replace(/-([a-z])/g, (_, letter) => letter.toUpperCase());
    args[key] = argv[index + 1];
    index += 1;
  }

  for (const required of ["packagesFile", "workingOwner", "workingBranch", "workingSha"]) {
    if (!args[required]) {
      throw new Error(`Missing required argument --${required.replace(/[A-Z]/g, (letter) => `-${letter.toLowerCase()}`)}`);
    }
  }

  return args;
}

async function main(argv = process.argv.slice(2)) {
  const args = parseArgs(argv);
  await dispatchForPackages({
    packageDirs: readPackageDirs(args.packagesFile),
    workingBranch: {
      owner: args.workingOwner,
      branch: args.workingBranch,
      sha: args.workingSha,
    },
    workflowId: args.workflowId,
    workflowRef: args.workflowRef,
    repoRoot: args.repoRoot,
    dryRun: args.dryRun,
  });
}

const isCli = process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url);
if (isCli) {
  main().catch((error) => {
    console.error(error instanceof Error ? error.message : String(error));
    process.exit(1);
  });
}

export {
  REPO_SLUG,
  SYNC_METADATA_MARKER,
  SYNC_METADATA_WARNING,
  buildTitleQuery,
  dispatchForPackages,
  findMatchingReviewPrs,
  metadataMatches,
  normalizePackageDir,
  packageRecordFromDir,
  parseSyncMetadata,
  readPackageDirs,
};