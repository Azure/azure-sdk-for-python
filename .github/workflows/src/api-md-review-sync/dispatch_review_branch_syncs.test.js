import fs from "fs";
import os from "os";
import path from "path";
import assert from "node:assert/strict";
import test from "node:test";

import {
  REPO_SLUG,
  SYNC_METADATA_MARKER,
  SYNC_METADATA_WARNING,
  buildTitleQuery,
  dispatchForPackages,
  evaluateFinalCiGate,
  findMatchingReviewPrs,
  githubRequest,
  parseSyncMetadata,
  requiredChecksGate,
} from "./dispatch_review_branch_syncs.js";

function metadataBlock(overrides = {}) {
  const metadata = {
    schemaVersion: 1,
    repository: REPO_SLUG,
    packageName: "azure-example",
    packageDir: "sdk/service/azure-example",
    baseBranch: "apireview/base_azure-example_1.0.0",
    reviewBranch: "apireview/review_azure-example_1.1.0",
    workingOwner: "Azure",
    workingBranch: "feature/api-change",
    workingPrNumber: 123,
    ...overrides,
  };
  return [`<!-- ${SYNC_METADATA_MARKER}`, SYNC_METADATA_WARNING, JSON.stringify(metadata, null, 2), "-->"].join("\n");
}

test("parseSyncMetadata accepts one valid block", () => {
  const metadata = parseSyncMetadata(`Review body\n\n${metadataBlock()}`);

  assert.equal(metadata.packageName, "azure-example");
  assert.equal(metadata.workingBranch, "feature/api-change");
});

test("parseSyncMetadata ignores malformed and duplicate blocks", () => {
  assert.equal(parseSyncMetadata("<!-- unrelated -->"), undefined);
  assert.equal(parseSyncMetadata(`<!-- ${SYNC_METADATA_MARKER}\n{}\n-->`), undefined);
  assert.equal(parseSyncMetadata(`${metadataBlock()}\n${metadataBlock()}`), undefined);
});

test("buildTitleQuery filters by API review package and version", () => {
  const query = buildTitleQuery({ packageName: "azure-example", packageDir: "sdk/service/azure-example", version: "1.1.0b1" });

  assert.match(query, /"\[API Review\]"/);
  assert.match(query, /"azure-example"/);
  assert.match(query, /"1\.1\.0b1"/);
});

test("findMatchingReviewPrs selects only matching metadata", async () => {
  const matches = await findMatchingReviewPrs({
    searchPullRequestsFn: async () => [
      { number: 1, body: metadataBlock() },
      { number: 2, body: metadataBlock({ packageDir: "sdk/service/other" }) },
      { number: 3, body: metadataBlock({ workingBranch: "other-branch" }) },
    ],
    packageRecord: { packageName: "azure-example", packageDir: "sdk/service/azure-example", version: "1.1.0" },
    workingBranch: { owner: "Azure", branch: "feature/api-change", sha: "abc123" },
  });

  assert.deepEqual(matches.map((match) => match.pr.number), [1]);
});

test("dispatchForPackages triggers one run per matching review branch", async () => {
  const repoRoot = fs.mkdtempSync(path.join(os.tmpdir(), "api-md-dispatch-"));
  const packageDir = path.join(repoRoot, "sdk", "service", "azure-example");
  fs.mkdirSync(packageDir, { recursive: true });
  fs.writeFileSync(path.join(packageDir, "_version.py"), 'VERSION = "1.1.0"\n', "utf-8");

  const dispatches = [];
  const count = await dispatchForPackages({
    packageDirs: ["sdk/service/azure-example"],
    workingBranch: { owner: "Azure", branch: "feature/api-change", sha: "abc123" },
    workflowId: "sync.yml",
    workflowRef: "main",
    repoRoot,
    searchPullRequestsFn: async () => [
      { number: 1, body: metadataBlock({ reviewBranch: "apireview/review_azure-example_1.1.0" }) },
      { number: 2, body: metadataBlock({ reviewBranch: "apireview/review_azure-example_1.1.0_b" }) },
    ],
    dispatchFn: async (workflowId, ref, inputs) => dispatches.push({ workflowId, ref, inputs }),
  });

  assert.equal(count, 2);
  assert.equal(dispatches.length, 2);
  assert.equal(dispatches[0].inputs.packageDir, "sdk/service/azure-example");
  assert.equal(dispatches[0].inputs.workingSha, "abc123");
});

test("dispatchForPackages skips apireview working branches", async () => {
  const dispatches = [];
  const count = await dispatchForPackages({
    packageDirs: ["sdk/service/azure-example"],
    workingBranch: { owner: "Azure", branch: "apireview/review_azure-example_1.1.0", sha: "abc123" },
    dispatchFn: async (workflowId, ref, inputs) => dispatches.push({ workflowId, ref, inputs }),
  });

  assert.equal(count, 0);
  assert.deepEqual(dispatches, []);
});

test("requiredChecksGate waits for required Azure DevOps status contexts", () => {
  const result = requiredChecksGate({
    requiredStatusChecks: { contexts: ["Azure Pipelines / python"], checks: [] },
    combinedStatus: { state: "pending", statuses: [{ context: "Azure Pipelines / python", state: "pending" }] },
    checkRuns: [],
  });

  assert.equal(result.ready, false);
  assert.match(result.reason, /Azure Pipelines/);
});

test("requiredChecksGate accepts required check runs that completed successfully", () => {
  const result = requiredChecksGate({
    requiredStatusChecks: { contexts: [], checks: [{ context: "API.md Consistency" }] },
    combinedStatus: { state: "success", statuses: [] },
    checkRuns: [{ name: "API.md Consistency", status: "completed", conclusion: "success" }],
  });

  assert.equal(result.ready, true);
});

test("githubRequest can suppress forbidden required-check reads", async () => {
  const originalFetch = globalThis.fetch;
  globalThis.fetch = async () => new Response("forbidden", { status: 403 });

  try {
    const result = await githubRequest("GET", "/repos/Azure/azure-sdk-for-python/branches/main/protection/required_status_checks", {
      allow403: true,
      allow404: true,
    });

    assert.equal(result, undefined);
  } finally {
    globalThis.fetch = originalFetch;
  }
});

test("evaluateFinalCiGate exits when consistency has not passed", async () => {
  const result = await evaluateFinalCiGate({
    workingSha: "abc123",
    getCommitPullRequestsFn: async () => [
      {
        state: "open",
        head: { sha: "abc123", ref: "feature/api-change", repo: { owner: { login: "Azure" } } },
        base: { ref: "main" },
      },
    ],
    getWorkflowRunsForShaFn: async () => [],
  });

  assert.equal(result.ready, false);
  assert.match(result.reason, /consistency has not passed/);
});

test("evaluateFinalCiGate skips API review working branches before CI checks", async () => {
  let checkedConsistency = false;
  const result = await evaluateFinalCiGate({
    workingSha: "abc123",
    getCommitPullRequestsFn: async () => [
      {
        state: "open",
        head: { sha: "abc123", ref: "apireview/review_azure-example_1.1.0", repo: { owner: { login: "Azure" } } },
        base: { ref: "main" },
      },
    ],
    getWorkflowRunsForShaFn: async () => {
      checkedConsistency = true;
      return [{ id: 42, status: "completed", conclusion: "success" }];
    },
  });

  assert.equal(result.ready, false);
  assert.match(result.reason, /Skipping API review branch/);
  assert.equal(checkedConsistency, false);
});

test("evaluateFinalCiGate resolves working branch when full CI is green", async () => {
  const result = await evaluateFinalCiGate({
    workingSha: "abc123",
    getCommitPullRequestsFn: async () => [
      {
        state: "open",
        head: { sha: "abc123", ref: "feature/api-change", repo: { owner: { login: "Azure" } } },
        base: { ref: "main" },
      },
    ],
    getWorkflowRunsForShaFn: async () => [{ id: 42, status: "completed", conclusion: "success" }],
    getRequiredStatusChecksForBranchFn: async () => ({ contexts: ["Azure Pipelines / python"], checks: [] }),
    getCombinedStatusForShaFn: async () => ({
      state: "success",
      statuses: [{ context: "Azure Pipelines / python", state: "success" }],
    }),
    getCheckRunsForShaFn: async () => [{ name: "API.md Consistency", status: "completed", conclusion: "success" }],
  });

  assert.equal(result.ready, true);
  assert.equal(result.consistencyRunId, "42");
  assert.deepEqual(result.workingBranch, { owner: "Azure", branch: "feature/api-change", sha: "abc123" });
});
