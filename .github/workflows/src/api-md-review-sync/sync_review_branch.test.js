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