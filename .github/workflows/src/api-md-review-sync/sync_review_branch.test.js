import fs from "fs";
import os from "os";
import path from "path";
import assert from "node:assert/strict";
import test from "node:test";

import { artifactsDiffer, copyApiArtifacts, syncReviewBranch } from "./sync_review_branch.js";

function writeArtifacts(root, packageDir, apiText, metadataText) {
  const packagePath = path.join(root, packageDir);
  fs.mkdirSync(packagePath, { recursive: true });
  fs.writeFileSync(path.join(packagePath, "api.md"), apiText, "utf-8");
  fs.writeFileSync(path.join(packagePath, "api.metadata.yml"), metadataText, "utf-8");
}

function createSymlinkOrSkip(t, target, linkPath) {
  try {
    fs.symlinkSync(target, linkPath);
    return true;
  } catch (error) {
    if (["EACCES", "EPERM"].includes(error?.code)) {
      t.skip("symlink creation requires elevated permissions on this platform");
      return false;
    }
    throw error;
  }
}

test("artifactsDiffer is false when both files match", () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "api-md-sync-"));
  const workingRoot = path.join(root, "working");
  const reviewRoot = path.join(root, "review");
  writeArtifacts(workingRoot, "sdk/service/azure-example", "api", "metadata");
  writeArtifacts(reviewRoot, "sdk/service/azure-example", "api", "metadata");

  assert.equal(artifactsDiffer(workingRoot, reviewRoot, "sdk/service/azure-example"), false);
});

test("artifactsDiffer is true when either file differs", () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "api-md-sync-"));
  const workingRoot = path.join(root, "working");
  const reviewRoot = path.join(root, "review");
  writeArtifacts(workingRoot, "sdk/service/azure-example", "api", "new metadata");
  writeArtifacts(reviewRoot, "sdk/service/azure-example", "api", "old metadata");

  assert.equal(artifactsDiffer(workingRoot, reviewRoot, "sdk/service/azure-example"), true);
});

test("artifactsDiffer fails when working artifacts are missing", () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "api-md-sync-"));
  const workingRoot = path.join(root, "working");
  const reviewRoot = path.join(root, "review");
  writeArtifacts(reviewRoot, "sdk/service/azure-example", "api", "metadata");

  assert.throws(() => artifactsDiffer(workingRoot, reviewRoot, "sdk/service/azure-example"), /required API artifact is missing/);
});

test("artifactsDiffer rejects symlinked working artifacts", (t) => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "api-md-sync-"));
  const workingRoot = path.join(root, "working");
  const reviewRoot = path.join(root, "review");
  const packageDir = "sdk/service/azure-example";
  const workingPackagePath = path.join(workingRoot, packageDir);
  const outsideFile = path.join(root, "outside-api.md");
  fs.mkdirSync(workingPackagePath, { recursive: true });
  fs.writeFileSync(outsideFile, "outside", "utf-8");
  if (!createSymlinkOrSkip(t, outsideFile, path.join(workingPackagePath, "api.md"))) {
    return;
  }
  fs.writeFileSync(path.join(workingPackagePath, "api.metadata.yml"), "metadata", "utf-8");
  writeArtifacts(reviewRoot, packageDir, "api", "metadata");

  assert.throws(() => artifactsDiffer(workingRoot, reviewRoot, packageDir), /must not contain symlinks/);
});

test("copyApiArtifacts copies only API files", () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "api-md-sync-"));
  const workingRoot = path.join(root, "working");
  const reviewRoot = path.join(root, "review");
  writeArtifacts(workingRoot, "sdk/service/azure-example", "new api", "new metadata");
  writeArtifacts(reviewRoot, "sdk/service/azure-example", "old api", "old metadata");
  const extraFile = path.join(reviewRoot, "sdk/service/azure-example/README.md");
  fs.writeFileSync(extraFile, "keep", "utf-8");

  copyApiArtifacts(workingRoot, reviewRoot, "sdk/service/azure-example");

  assert.equal(fs.readFileSync(path.join(reviewRoot, "sdk/service/azure-example/api.md"), "utf-8"), "new api");
  assert.equal(fs.readFileSync(path.join(reviewRoot, "sdk/service/azure-example/api.metadata.yml"), "utf-8"), "new metadata");
  assert.equal(fs.readFileSync(extraFile, "utf-8"), "keep");
});

test("copyApiArtifacts rejects symlinked review artifacts", (t) => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "api-md-sync-"));
  const workingRoot = path.join(root, "working");
  const reviewRoot = path.join(root, "review");
  const packageDir = "sdk/service/azure-example";
  const reviewPackagePath = path.join(reviewRoot, packageDir);
  const outsideFile = path.join(root, "outside-review-api.md");
  writeArtifacts(workingRoot, packageDir, "new api", "new metadata");
  fs.mkdirSync(reviewPackagePath, { recursive: true });
  fs.writeFileSync(outsideFile, "outside", "utf-8");
  if (!createSymlinkOrSkip(t, outsideFile, path.join(reviewPackagePath, "api.md"))) {
    return;
  }

  assert.throws(() => copyApiArtifacts(workingRoot, reviewRoot, packageDir), /must not contain symlinks/);
  assert.equal(fs.readFileSync(outsideFile, "utf-8"), "outside");
});

test("syncReviewBranch skips stale working SHA", async () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "api-md-sync-"));
  let committed = false;
  const result = await syncReviewBranch({
    workingRoot: path.join(root, "working"),
    reviewRoot: path.join(root, "review"),
    packageDir: "sdk/service/azure-example",
    reviewBranch: "apireview/review_azure-example_1.1.0",
    workingOwner: "Azure",
    workingBranch: "feature/api-change",
    workingSha: "older",
    lsRemoteHeadFn: async () => "newer",
    commitAndPushFn: async () => {
      committed = true;
      return true;
    },
  });

  assert.equal(result, "stale");
  assert.equal(committed, false);
});