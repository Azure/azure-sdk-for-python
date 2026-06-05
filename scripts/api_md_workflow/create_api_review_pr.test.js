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