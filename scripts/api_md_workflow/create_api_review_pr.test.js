const assert = require("node:assert/strict");
const test = require("node:test");

const workflow = require("./create_api_review_pr");

function commandResult(stdout = "[]", status = 0) {
  return {
    status,
    stdout,
    stderr: "",
  };
}

function stubGitNoTags() {
  return commandResult("", 1);
}

function stubGhWithSearchResults(results) {
  return (args) => {
    if (args.includes("--search")) {
      return commandResult(JSON.stringify(results));
    }

    return commandResult("[]");
  };
}

function parseSyncMetadataBlock(block) {
  const jsonText = block
    .replace(/^<!-- api-md-review-sync\n/, "")
    .replace(/^DO NOT MODIFY THESE CONTENTS!\n/, "")
    .replace(/\n-->$/, "");
  return JSON.parse(jsonText);
}

test("targetReferenceInfo links matching open PR from direct head query", () => {
  workflow.__setCommandRunners({
    git: stubGitNoTags,
    gh: (args) => {
      if (args.includes("--head")) {
        return commandResult(
          JSON.stringify([
            {
              number: 45678,
              url: "https://github.com/Azure/azure-sdk-for-python/pull/45678",
              state: "OPEN",
              updatedAt: "2026-06-05T00:00:00Z",
              headRefName: "users/example/direct-feature",
              headRepositoryOwner: { login: "example" },
            },
          ]),
        );
      }

      return commandResult("[]");
    },
  });

  assert.deepEqual(workflow.targetReferenceInfo("example:users/example/direct-feature"), {
    label: "Working PR",
    markdown: "[PR #45678](https://github.com/Azure/azure-sdk-for-python/pull/45678)",
  });
});

test("targetReferenceInfo links matching open PR for owner-qualified branch target", () => {
  workflow.__setCommandRunners({
    git: stubGitNoTags,
    gh: stubGhWithSearchResults([
      {
        number: 12345,
        url: "https://github.com/Azure/azure-sdk-for-python/pull/12345",
        state: "OPEN",
        updatedAt: "2026-06-05T00:00:00Z",
        headRefName: "users/example/feature",
        headRepositoryOwner: { login: "example" },
      },
    ]),
  });

  assert.deepEqual(workflow.targetReferenceInfo("example:users/example/feature"), {
    label: "Working PR",
    markdown: "[PR #12345](https://github.com/Azure/azure-sdk-for-python/pull/12345)",
  });
});

test("targetReferenceInfo keeps origin/main as branch when search returns fork PRs named main", () => {
  workflow.__setCommandRunners({
    git: stubGitNoTags,
    gh: stubGhWithSearchResults([
      {
        number: 23456,
        url: "https://github.com/Azure/azure-sdk-for-python/pull/23456",
        state: "OPEN",
        updatedAt: "2026-06-05T00:00:00Z",
        headRefName: "main",
        headRepositoryOwner: { login: "example" },
      },
    ]),
  });

  assert.deepEqual(workflow.targetReferenceInfo("origin/main"), {
    label: "Working branch",
    markdown: "[branch `origin/main`](https://github.com/Azure/azure-sdk-for-python/tree/main)",
  });
});

test("targetReferenceInfo keeps branch reference when no open PR matches both owner and branch", () => {
  workflow.__setCommandRunners({
    git: stubGitNoTags,
    gh: stubGhWithSearchResults([
      {
        number: 34567,
        url: "https://github.com/Azure/azure-sdk-for-python/pull/34567",
        state: "OPEN",
        updatedAt: "2026-06-05T00:00:00Z",
        headRefName: "users/example/feature",
        headRepositoryOwner: { login: "someone-else" },
      },
    ]),
  });

  assert.deepEqual(workflow.targetReferenceInfo("example:users/example/feature"), {
    label: "Working branch",
    markdown: "[branch `example:users/example/feature`](https://github.com/example/azure-sdk-for-python/tree/users%2Fexample%2Ffeature)",
  });
});

test("targetReferenceInfo treats existing target tag as tag and does not query PRs", () => {
  let prLookupCount = 0;

  workflow.__setCommandRunners({
    git: (args) => {
      if (args[0] === "rev-parse" && args.includes("refs/tags/azure-example_1.2.3")) {
        return commandResult("", 0);
      }

      if (args[0] === "rev-list") {
        return commandResult("abc123def456\n", 0);
      }

      return commandResult("", 1);
    },
    gh: () => {
      prLookupCount += 1;
      return commandResult("[]");
    },
  });

  assert.deepEqual(workflow.targetReferenceInfo("azure-example_1.2.3"), {
    label: "Target tag",
    markdown: "[tag `azure-example_1.2.3`](https://github.com/Azure/azure-sdk-for-python/commit/abc123def456)",
  });
  assert.equal(prLookupCount, 0);
});

test("buildSyncMetadataObject creates hidden metadata for origin branch target", () => {
  workflow.__setCommandRunners({
    git: stubGitNoTags,
    gh: (args) => {
      if (args.includes("--head")) {
        return commandResult(
          JSON.stringify([
            {
              number: 47203,
              url: "https://github.com/Azure/azure-sdk-for-python/pull/47203",
              state: "OPEN",
              updatedAt: "2026-06-05T00:00:00Z",
              headRefName: "feature/api-change",
              headRepositoryOwner: { login: "Azure" },
            },
          ]),
        );
      }

      return commandResult("[]");
    },
  });

  const metadata = workflow.buildSyncMetadataObject({
    packageName: "azure-example",
    packageDir: "sdk/service/azure-example",
    baseBranch: "apireview/base_azure-example_1.0.0",
    reviewBranch: "apireview/review_azure-example_1.1.0",
    headSelector: "feature/api-change",
  });
  const block = workflow.buildSyncMetadataBlock(metadata);

  assert.ok(block.startsWith("<!-- api-md-review-sync\nDO NOT MODIFY THESE CONTENTS!\n"));
  assert.ok(block.endsWith("\n-->"));
  assert.deepEqual(parseSyncMetadataBlock(block), {
    schemaVersion: 1,
    repository: "Azure/azure-sdk-for-python",
    packageName: "azure-example",
    packageDir: "sdk/service/azure-example",
    baseBranch: "apireview/base_azure-example_1.0.0",
    reviewBranch: "apireview/review_azure-example_1.1.0",
    workingOwner: "Azure",
    workingBranch: "feature/api-change",
    workingPrNumber: 47203,
  });
});

test("buildSyncMetadataObject records fork owner and branch target", () => {
  workflow.__setCommandRunners({
    git: stubGitNoTags,
    gh: stubGhWithSearchResults([
      {
        number: 47204,
        url: "https://github.com/Azure/azure-sdk-for-python/pull/47204",
        state: "OPEN",
        updatedAt: "2026-06-05T00:00:00Z",
        headRefName: "users/example/feature",
        headRepositoryOwner: { login: "example" },
      },
    ]),
  });

  const metadata = workflow.buildSyncMetadataObject({
    packageName: "azure-example",
    packageDir: "sdk/service/azure-example",
    baseBranch: "apireview/base_azure-example_1.0.0",
    reviewBranch: "apireview/review_azure-example_1.1.0",
    headSelector: "example:users/example/feature",
  });

  assert.equal(metadata.workingOwner, "example");
  assert.equal(metadata.workingBranch, "users/example/feature");
  assert.equal(metadata.workingPrNumber, 47204);
});

test("buildSyncMetadataObject omits metadata for tag targets", () => {
  let prLookupCount = 0;

  workflow.__setCommandRunners({
    git: (args) => {
      if (args[0] === "rev-parse" && args.includes("refs/tags/azure-example_1.2.3")) {
        return commandResult("", 0);
      }

      return commandResult("", 1);
    },
    gh: () => {
      prLookupCount += 1;
      return commandResult("[]");
    },
  });

  assert.equal(
    workflow.buildSyncMetadataObject({
      packageName: "azure-example",
      packageDir: "sdk/service/azure-example",
      baseBranch: "apireview/base_azure-example_1.0.0",
      reviewBranch: "apireview/review_azure-example_1.1.0",
      headSelector: "azure-example_1.2.3",
    }),
    null,
  );
  assert.equal(prLookupCount, 0);
});

test("buildSyncMetadataObject records main branch target", () => {
  workflow.__setCommandRunners({
    git: stubGitNoTags,
    gh: () => commandResult("[]"),
  });

  const metadata = workflow.buildSyncMetadataObject({
    packageName: "azure-example",
    packageDir: "sdk/service/azure-example",
    baseBranch: "apireview/base_azure-example_1.0.0",
    reviewBranch: "apireview/review_azure-example_1.1.0",
    headSelector: "main",
  });

  assert.equal(metadata.workingOwner, "Azure");
  assert.equal(metadata.workingBranch, "main");
  assert.equal(metadata.workingPrNumber, null);
});

test("buildSyncMetadataObject records null working PR for branch target without PR", () => {
  workflow.__setCommandRunners({
    git: stubGitNoTags,
    gh: () => commandResult("[]"),
  });

  const metadata = workflow.buildSyncMetadataObject({
    packageName: "azure-example",
    packageDir: "sdk/service/azure-example",
    baseBranch: "apireview/base_azure-example_1.0.0",
    reviewBranch: "apireview/review_azure-example_1.1.0",
    headSelector: "feature/no-pr",
  });

  assert.equal(metadata.workingOwner, "Azure");
  assert.equal(metadata.workingBranch, "feature/no-pr");
  assert.equal(metadata.workingPrNumber, null);
});

test("buildReviewPrBody calls out static tag-to-tag reviews", () => {
  const body = workflow.buildReviewPrBody({
    packageName: "azure-example",
    targetVersion: "1.2.3",
    baseVersion: "1.2.2",
    workingReference: {
      label: "Target tag",
      markdown: "[tag `azure-example_1.2.3`](https://github.com/Azure/azure-sdk-for-python/commit/abc123)",
    },
    baselineRef: "[tag `azure-example_1.2.2`](https://github.com/Azure/azure-sdk-for-python/commit/def456)",
    syncMetadataBlock: null,
  });

  assert.ok(body.includes("Static tag-to-tag review"));
  assert.ok(body.includes("cannot be automatically updated from a working branch"));
  assert.equal(body.includes("api-md-review-sync"), false);
});

test("apiResultsHaveApiDiff returns false for identical API markdown", () => {
  assert.equal(
    workflow.apiResultsHaveApiDiff(
      { apiMd: Buffer.from("# API\n\nclass Same\n"), metadata: Buffer.from("apiMdSha256: old") },
      { apiMd: Buffer.from("# API\n\nclass Same\n"), metadata: Buffer.from("apiMdSha256: new") },
    ),
    false,
  );
});

test("apiResultsHaveApiDiff returns true for changed API markdown", () => {
  assert.equal(
    workflow.apiResultsHaveApiDiff(
      { apiMd: Buffer.from("# API\n\nclass Old\n") },
      { apiMd: Buffer.from("# API\n\nclass New\n") },
    ),
    true,
  );
});

test("replaceSyncMetadataBlock replaces stale hidden metadata", () => {
  const oldBlock = workflow.buildSyncMetadataBlock({
    schemaVersion: 1,
    repository: "Azure/azure-sdk-for-python",
    packageName: "old-package",
    packageDir: "sdk/service/old-package",
    baseBranch: "apireview/base_old-package_1.0.0",
    reviewBranch: "apireview/review_old-package_1.1.0",
    workingOwner: "Azure",
    workingBranch: "old-feature",
  });
  const newBlock = workflow.buildSyncMetadataBlock({
    schemaVersion: 1,
    repository: "Azure/azure-sdk-for-python",
    packageName: "azure-example",
    packageDir: "sdk/service/azure-example",
    baseBranch: "apireview/base_azure-example_1.0.0",
    reviewBranch: "apireview/review_azure-example_1.1.0",
    workingOwner: "Azure",
    workingBranch: "feature/api-change",
  });

  const body = workflow.replaceSyncMetadataBlock(`Review body\n\n${oldBlock}`, newBlock);

  assert.ok(body.startsWith("Review body\n\n<!-- api-md-review-sync"));
  assert.ok(body.includes("DO NOT MODIFY THESE CONTENTS!"));
  assert.ok(body.includes('"packageName": "azure-example"'));
  assert.equal(body.includes("old-package"), false);
  assert.equal((body.match(/api-md-review-sync/g) || []).length, 1);
});