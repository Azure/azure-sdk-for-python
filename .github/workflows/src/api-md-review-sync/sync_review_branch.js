#!/usr/bin/env node

import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

import { runAsync } from "../api-md-consistency/common.js";

const REPO_NAME = "azure-sdk-for-python";
const API_ARTIFACTS = ["api.md", "api.metadata.yml"];

function normalizePackageDir(packageDir) {
  const normalized = packageDir.trim().replace(/\\/g, "/");
  if (!normalized.startsWith("sdk/") || normalized.startsWith("/") || `/${normalized}/`.includes("/../")) {
    throw new Error(`ERROR: unsafe package directory: ${packageDir}`);
  }
  return normalized;
}

function artifactPaths(root, packageDir) {
  const normalized = normalizePackageDir(packageDir);
  return API_ARTIFACTS.map((artifact) => path.join(root, normalized, artifact));
}

function readFileOrUndefined(filePath) {
  return fs.existsSync(filePath) ? fs.readFileSync(filePath) : undefined;
}

function artifactsDiffer(workingRoot, reviewRoot, packageDir) {
  const workingPaths = artifactPaths(workingRoot, packageDir);
  const reviewPaths = artifactPaths(reviewRoot, packageDir);

  return workingPaths.some((workingPath, index) => {
    const reviewPath = reviewPaths[index];
    return !Buffer.from(readFileOrUndefined(workingPath) || "").equals(Buffer.from(readFileOrUndefined(reviewPath) || ""));
  });
}

function copyApiArtifacts(workingRoot, reviewRoot, packageDir) {
  const workingPaths = artifactPaths(workingRoot, packageDir);
  const reviewPaths = artifactPaths(reviewRoot, packageDir);

  for (const [index, workingPath] of workingPaths.entries()) {
    if (!fs.existsSync(workingPath)) {
      throw new Error(`ERROR: required API artifact is missing from working branch checkout: ${workingPath}`);
    }
    fs.mkdirSync(path.dirname(reviewPaths[index]), { recursive: true });
    fs.copyFileSync(workingPath, reviewPaths[index]);
  }
}

async function lsRemoteHead(owner, branch, cwd) {
  const remoteUrl = `https://github.com/${owner}/${REPO_NAME}.git`;
  const result = await runAsync("git", ["ls-remote", remoteUrl, `refs/heads/${branch}`], { cwd, check: false });
  if (result.status !== 0 || !result.stdout.trim()) {
    return undefined;
  }
  return result.stdout.trim().split(/\s+/)[0];
}

async function commitAndPush(reviewRoot, packageDir, reviewBranch, workingSha) {
  const normalized = normalizePackageDir(packageDir);
  const gitPaths = API_ARTIFACTS.map((artifact) => `${normalized}/${artifact}`);

  await runAsync("git", ["config", "user.name", "github-actions[bot]"], { cwd: reviewRoot });
  await runAsync("git", ["config", "user.email", "github-actions[bot]@users.noreply.github.com"], { cwd: reviewRoot });
  await runAsync("git", ["add", ...gitPaths], { cwd: reviewRoot });

  const diff = await runAsync("git", ["diff", "--cached", "--quiet"], { cwd: reviewRoot, check: false });
  if (diff.status === 0) {
    return false;
  }

  const packageName = path.basename(normalized);
  await runAsync("git", ["commit", "-m", `[API Review] Sync api.md for ${packageName} from ${workingSha.slice(0, 7)}`], {
    cwd: reviewRoot,
  });
  await runAsync("git", ["push", "origin", `HEAD:${reviewBranch}`, "--force-with-lease"], { cwd: reviewRoot });
  return true;
}

async function syncReviewBranch({
  workingRoot,
  reviewRoot,
  packageDir,
  reviewBranch,
  workingOwner,
  workingBranch,
  workingSha,
  lsRemoteHeadFn = lsRemoteHead,
  commitAndPushFn = commitAndPush,
}) {
  const currentHead = await lsRemoteHeadFn(workingOwner, workingBranch, reviewRoot);
  if (currentHead !== workingSha) {
    console.log(`Skipping stale sync: ${workingOwner}:${workingBranch} is at ${currentHead}, not ${workingSha}.`);
    return "stale";
  }

  if (!artifactsDiffer(workingRoot, reviewRoot, packageDir)) {
    console.log(`Review branch ${reviewBranch} is already current for ${packageDir}.`);
    return "current";
  }

  copyApiArtifacts(workingRoot, reviewRoot, packageDir);
  if (await commitAndPushFn(reviewRoot, packageDir, reviewBranch, workingSha)) {
    console.log(`Updated ${reviewBranch} with API artifacts from ${workingSha}.`);
    return "updated";
  }

  console.log(`No staged changes after copying API artifacts for ${packageDir}.`);
  return "current";
}

function parseArgs(argv) {
  const args = {};
  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];
    if (!arg.startsWith("--")) {
      throw new Error(`Unexpected argument: ${arg}`);
    }
    const key = arg.slice(2).replace(/-([a-z])/g, (_, letter) => letter.toUpperCase());
    args[key] = argv[index + 1];
    index += 1;
  }

  for (const required of ["workingRoot", "reviewRoot", "packageDir", "reviewBranch", "workingOwner", "workingBranch", "workingSha"]) {
    if (!args[required]) {
      throw new Error(`Missing required argument --${required.replace(/[A-Z]/g, (letter) => `-${letter.toLowerCase()}`)}`);
    }
  }

  return args;
}

async function main(argv = process.argv.slice(2)) {
  await syncReviewBranch(parseArgs(argv));
}

const isCli = process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url);
if (isCli) {
  main().catch((error) => {
    console.error(error instanceof Error ? error.message : String(error));
    process.exit(1);
  });
}

export {
  API_ARTIFACTS,
  artifactPaths,
  artifactsDiffer,
  copyApiArtifacts,
  normalizePackageDir,
  syncReviewBranch,
};