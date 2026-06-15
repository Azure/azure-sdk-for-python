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

function isPathInside(parent, child) {
  const relative = path.relative(parent, child);
  return relative === "" || (!relative.startsWith("..") && !path.isAbsolute(relative));
}

function relativePathUnderRoot(root, filePath) {
  const absoluteRoot = path.resolve(root);
  const absoluteFilePath = path.resolve(filePath);
  const relativePath = path.relative(absoluteRoot, absoluteFilePath);

  if (relativePath.startsWith("..") || path.isAbsolute(relativePath)) {
    throw new Error(`ERROR: API artifact path escapes checkout root: ${filePath}`);
  }

  return { absoluteRoot, absoluteFilePath, relativePath };
}

function requirePlainFileUnderRoot(root, filePath) {
  const { absoluteRoot, absoluteFilePath, relativePath } = relativePathUnderRoot(root, filePath);

  let currentPath = absoluteRoot;
  for (const part of relativePath.split(path.sep).filter(Boolean)) {
    currentPath = path.join(currentPath, part);
    const stat = fs.lstatSync(currentPath);
    if (stat.isSymbolicLink()) {
      throw new Error(`ERROR: API artifact path must not contain symlinks: ${filePath}`);
    }
  }

  const stat = fs.statSync(absoluteFilePath);
  if (!stat.isFile()) {
    throw new Error(`ERROR: API artifact must be a regular file: ${filePath}`);
  }

  const realRoot = fs.realpathSync(absoluteRoot);
  const realFilePath = fs.realpathSync(absoluteFilePath);
  if (!isPathInside(realRoot, realFilePath)) {
    throw new Error(`ERROR: API artifact real path escapes checkout root: ${filePath}`);
  }
}

function lstatOrUndefined(filePath) {
  try {
    return fs.lstatSync(filePath);
  } catch (error) {
    if (error?.code === "ENOENT") {
      return undefined;
    }
    throw error;
  }
}

function requireWritableArtifactPath(root, filePath) {
  if (lstatOrUndefined(filePath)) {
    requirePlainFileUnderRoot(root, filePath);
    return;
  }

  const parentDir = path.dirname(filePath);
  const { absoluteRoot, relativePath } = relativePathUnderRoot(root, parentDir);

  let currentPath = absoluteRoot;
  for (const part of relativePath.split(path.sep).filter(Boolean)) {
    currentPath = path.join(currentPath, part);
    const stat = fs.lstatSync(currentPath);
    if (stat.isSymbolicLink()) {
      throw new Error(`ERROR: API artifact path must not contain symlinks: ${filePath}`);
    }
    if (!stat.isDirectory()) {
      throw new Error(`ERROR: API artifact parent path must be a directory: ${filePath}`);
    }
  }
}

function readFileOrUndefined(root, filePath) {
  if (!lstatOrUndefined(filePath)) {
    return undefined;
  }
  requirePlainFileUnderRoot(root, filePath);
  return fs.readFileSync(filePath);
}

function readRequiredFile(root, filePath) {
  if (!lstatOrUndefined(filePath)) {
    throw new Error(`ERROR: required API artifact is missing from working branch checkout: ${filePath}`);
  }
  requirePlainFileUnderRoot(root, filePath);
  return fs.readFileSync(filePath);
}

function artifactsDiffer(workingRoot, reviewRoot, packageDir) {
  const workingPaths = artifactPaths(workingRoot, packageDir);
  const reviewPaths = artifactPaths(reviewRoot, packageDir);

  return workingPaths.some((workingPath, index) => {
    const reviewPath = reviewPaths[index];
    return !readRequiredFile(workingRoot, workingPath).equals(Buffer.from(readFileOrUndefined(reviewRoot, reviewPath) || ""));
  });
}

function copyApiArtifacts(workingRoot, reviewRoot, packageDir) {
  const workingPaths = artifactPaths(workingRoot, packageDir);
  const reviewPaths = artifactPaths(reviewRoot, packageDir);

  for (const [index, workingPath] of workingPaths.entries()) {
    requirePlainFileUnderRoot(workingRoot, workingPath);
    fs.mkdirSync(path.dirname(reviewPaths[index]), { recursive: true });
    requireWritableArtifactPath(reviewRoot, reviewPaths[index]);
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