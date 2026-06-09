#!/usr/bin/env node

const fs = require("fs");
const path = require("path");
const { execFileSync } = require("child_process");
const { simpleGit } = require("simple-git");
const { getDefaultLogger } = require("./common");
const { loadAdapter, loadWorkflowConfig } = require("./adapter_config");

const REPO_ROOT = path.resolve(__dirname, "..", "..");
const REPO_OWNER = "Azure";
const REPO_NAME = "azure-sdk-for-python";
const REPO_SLUG = `${REPO_OWNER}/${REPO_NAME}`;
const REMOTE = "origin";
const MAIN_REF = `${REMOTE}/main`;
const SYNC_METADATA_MARKER = "api-md-review-sync";
const SYNC_METADATA_WARNING = "DO NOT MODIFY THESE CONTENTS!";
let logger = console;
let githubApi = null;
let simpleGitClient = null;

function logInfo(message) {
  logger.info(message);
}

function logWarning(message) {
  if (typeof logger.warning === "function") {
    logger.warning(message);
    return;
  }
  logger.warn(message);
}

function logError(message) {
  logger.error(message);
}

function parseArgs(argv) {
  const config = loadWorkflowConfig();
  const args = {
    packageName: null,
    base: null,
    target: null,
    adapter: config.adapter,
    runtimeExecutable: process.env.RUNTIME_EXECUTABLE || null,
  };

  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    if (!arg.startsWith("--")) {
      throw new Error(`Unexpected argument: ${arg}`);
    }

    const key = arg.slice(2);
    const value = argv[i + 1];
    if (!value || value.startsWith("--")) {
      throw new Error(`Missing value for --${key}`);
    }

    i += 1;
    if (key === "package-name") {
      args.packageName = value;
    } else if (key === "base") {
      args.base = value;
    } else if (key === "target") {
      args.target = value;
    } else if (key === "adapter") {
      args.adapter = value;
    } else if (key === "python" || key === "runtime") {
      args.runtimeExecutable = value;
    } else {
      throw new Error(`Unknown option: --${key}`);
    }
  }

  if (!args.packageName) {
    throw new Error("Missing required --package-name");
  }

  if (!args.base) {
    throw new Error("Missing required --base");
  }

  return args;
}

function getSimpleGitClient() {
  if (simpleGitClient) {
    return simpleGitClient;
  }

  simpleGitClient = simpleGit({ baseDir: REPO_ROOT });
  return simpleGitClient;
}

let git = async function gitCommand(args, options = {}) {
  const printable = ["git", ...args].join(" ");
  logInfo(`$ ${printable}`);

  try {
    const stdout = await getSimpleGitClient().raw(args);
    return {
      status: 0,
      stdout,
      stderr: "",
    };
  } catch (error) {
    const status = Number.isInteger(error.exitCode) ? error.exitCode : 1;
    if (options.check ?? true) {
      throw new Error(`Command failed (${status}): ${printable}`);
    }

    return {
      status,
      stdout: error.output || "",
      stderr: error.message || "",
    };
  }
};

async function gitOut(args) {
  return (await git(args, { capture: true })).stdout.trim();
}

function normalizePullRequest(pr) {
  if (!pr || typeof pr !== "object") {
    return null;
  }

  return {
    number: pr.number,
    url: pr.url || pr.html_url,
    state: pr.state,
    updatedAt: pr.updatedAt || pr.updated_at,
    body: pr.body,
    headRefName: pr.headRefName || (pr.head && pr.head.ref),
    headRepositoryOwner:
      pr.headRepositoryOwner ||
      (pr.head && pr.head.repo && pr.head.repo.owner
        ? { login: pr.head.repo.owner.login }
        : { login: undefined }),
  };
}

async function createOctokitGithubApi() {
  const { Octokit } = await import("@octokit/rest");
  const token = resolveGithubToken();
  const octokit = new Octokit(token ? { auth: token } : {});

  async function searchPullRequests(query, limit) {
    const result = await octokit.graphql(
      `query($query: String!, $first: Int!) {
        search(query: $query, type: ISSUE, first: $first) {
          nodes {
            ... on PullRequest {
              number
              url
              state
              updatedAt
              body
              headRefName
              headRepositoryOwner {
                login
              }
            }
          }
        }
      }`,
      { query, first: limit },
    );

    return (result.search.nodes || []).map(normalizePullRequest).filter(Boolean);
  }

  return {
    async listPullRequestsByHead(head, limit) {
      const result = await octokit.rest.pulls.list({
        owner: REPO_OWNER,
        repo: REPO_NAME,
        head,
        state: "open",
        per_page: limit,
      });
      return result.data.map(normalizePullRequest).filter(Boolean);
    },

    searchPullRequests,

    async listPullRequestsByBranches(base, head, limit) {
      const result = await octokit.rest.pulls.list({
        owner: REPO_OWNER,
        repo: REPO_NAME,
        base,
        head: `${REPO_OWNER}:${head}`,
        state: "open",
        per_page: limit,
      });
      return result.data.map(normalizePullRequest).filter(Boolean);
    },

    async updatePullRequestBody(number, body) {
      await octokit.rest.pulls.update({
        owner: REPO_OWNER,
        repo: REPO_NAME,
        pull_number: number,
        body,
      });
    },

    async createDraftPullRequest(base, head, title, body) {
      const result = await octokit.rest.pulls.create({
        owner: REPO_OWNER,
        repo: REPO_NAME,
        base,
        head,
        title,
        body,
        draft: true,
      });
      return result.data;
    },
  };
}

function resolveGithubToken() {
  const token = process.env.GITHUB_TOKEN || process.env.GH_TOKEN;
  if (token) {
    return token;
  }

  try {
    return execFileSync("gh", ["auth", "token"], {
      cwd: REPO_ROOT,
      encoding: "utf-8",
      stdio: ["ignore", "pipe", "ignore"],
    }).trim();
  } catch {
    return null;
  }
}

async function getGithubApi() {
  if (!githubApi) {
    githubApi = await createOctokitGithubApi();
  }

  return githubApi;
}

async function ensureCleanWorktree() {
  const status = await gitOut(["status", "--porcelain"]);
  if (status) {
    throw new Error(`ERROR: working tree is not clean. Commit or stash changes before running.\n${status}`);
  }
}

async function currentBranch() {
  return gitOut(["rev-parse", "--abbrev-ref", "HEAD"]);
}

async function currentBranchOrSha() {
  const name = await currentBranch();
  if (name === "HEAD") {
    return gitOut(["rev-parse", "--short", "HEAD"]);
  }
  return name;
}

async function tagExists(tag) {
  const result = await git(["rev-parse", "--verify", "--quiet", `refs/tags/${tag}`], {
    capture: true,
    check: false,
  });
  return result.status === 0;
}

async function validateBaseTag(packageName, baseTag) {
  if (!baseTag.startsWith(`${packageName}_`)) {
    throw new Error(`ERROR: --base tag '${baseTag}' must start with '${packageName}_'.`);
  }

  const version = baseTag.slice(packageName.length + 1);
  if (!version) {
    throw new Error(`ERROR: --base tag '${baseTag}' is missing the version suffix.`);
  }

  if (!(await tagExists(baseTag))) {
    throw new Error(`ERROR: tag '${baseTag}' does not exist in this repository.`);
  }

  return version;
}

function isExplicitPackageTag(target, packageName = null) {
  if (target.includes(":")) {
    return false;
  }

  if (packageName) {
    return target.startsWith(`${packageName}_`);
  }

  return target.includes("_");
}

async function resolveTargetTag(target, packageName = null) {
  if (!isExplicitPackageTag(target, packageName)) {
    return null;
  }

  if (await tagExists(target)) {
    return target;
  }

  await git(["fetch", REMOTE, "tag", target], { check: false, capture: true });
  return (await tagExists(target)) ? target : null;
}

async function tryRemoteBranchRef(branch) {
  const result = await git(["fetch", REMOTE, branch], { check: false, capture: true });
  return result.status === 0 ? `${REMOTE}/${branch}` : null;
}

async function remoteBranchRef(branch) {
  const branchRef = await tryRemoteBranchRef(branch);
  if (!branchRef) {
    throw new Error(`ERROR: branch '${branch}' does not exist on ${REMOTE}.`);
  }

  return branchRef;
}

function forkUrl(owner) {
  return `https://github.com/${owner}/azure-sdk-for-python.git`;
}

async function tryForkBranchRef(owner, branch) {
  const result = await git(["fetch", forkUrl(owner), branch], { check: false, capture: true });
  return result.status === 0 ? "FETCH_HEAD" : null;
}

async function resolveTargetRef(target, packageName = null) {
  if (!target.includes(":")) {
    const branchRef = await tryRemoteBranchRef(target);
    if (branchRef) {
      return branchRef;
    }

    const targetTag = await resolveTargetTag(target, packageName);
    if (targetTag) {
      return targetTag;
    }

    throw new Error(`ERROR: --target '${target}' is neither a branch on ${REMOTE} nor a tag in this repository.`);
  }

  const [owner, branch] = target.split(":", 2);
  if (!owner || !branch) {
    throw new Error(`ERROR: invalid --target '${target}'. Expected 'tag', 'branch', or 'owner:branch'.`);
  }

  const branchRef = await tryForkBranchRef(owner, branch);
  if (!branchRef) {
    throw new Error(`ERROR: branch '${branch}' does not exist in fork '${owner}'.`);
  }

  return branchRef;
}

function packageRelDir(packageDir) {
  return path.relative(REPO_ROOT, packageDir).split(path.sep).join("/");
}

function normalizePackageDir(packageDir) {
  if (path.isAbsolute(packageDir)) {
    return packageRelDir(packageDir);
  }

  return packageDir.split(path.sep).join("/");
}

function apiMdPath(packageDir) {
  return path.join(packageDir, "api.md");
}

function apiMdRel(packageDir) {
  return `${packageRelDir(packageDir)}/api.md`;
}

function metadataPath(packageDir) {
  return path.join(packageDir, "api.metadata.yml");
}

function metadataRel(packageDir) {
  return `${packageRelDir(packageDir)}/api.metadata.yml`;
}

function apiReviewBranchName(kind, packageName, version) {
  return `apireview/${kind}_${packageName}_${version}`;
}

function parseSimpleYaml(text) {
  const result = {};
  for (const line of text.split(/\r?\n/)) {
    const match = line.match(/^(\w+)\s*:\s*(.*)$/);
    if (match) {
      result[match[1]] = match[2].trim();
    }
  }
  return result;
}

function metadataShaOrNull(metadataBytes) {
  if (!metadataBytes) {
    return null;
  }

  const metadata = parseSimpleYaml(metadataBytes.toString("utf-8"));
  return metadata.apiMdSha256 || null;
}

function branchRemoteRef(branch) {
  return `${REMOTE}/${branch}`;
}

async function listRemoteBranchesWithPrefix(prefix) {
  const result = await git(["ls-remote", "--heads", REMOTE, `refs/heads/${prefix}*`], {
    capture: true,
    check: false,
  });

  if (result.status !== 0 || !result.stdout.trim()) {
    return [];
  }

  return result.stdout
    .split(/\r?\n/)
    .map((line) => line.trim().split(/\s+/, 2)[1] || "")
    .filter((ref) => ref.startsWith("refs/heads/"))
    .map((ref) => ref.slice("refs/heads/".length))
    .filter((branch) => branch === prefix || branch.startsWith(`${prefix}_`));
}

async function fetchRemoteBranch(branch) {
  await git(["fetch", REMOTE, branch]);
  return branchRemoteRef(branch);
}

async function readRefFileBytes(ref, relativePath) {
  const result = await git(["show", `${ref}:${relativePath}`], {
    capture: true,
    check: false,
  });

  if (result.status !== 0) {
    return null;
  }

  return Buffer.from(result.stdout, "utf-8");
}

function desiredBranchState(result) {
  if (result === null) {
    return {
      hasApiMd: false,
      hasMetadata: false,
      apiMdSha256: null,
    };
  }

  return {
    hasApiMd: true,
    hasMetadata: Boolean(result.metadata),
    apiMdSha256: metadataShaOrNull(result.metadata),
  };
}

function apiResultsHaveApiDiff(baseResult, targetResult) {
  return !Buffer.from(baseResult.apiMd).equals(Buffer.from(targetResult.apiMd));
}

function branchStateMatchesDesired(actual, desired) {
  return (
    actual.hasApiMd === desired.hasApiMd &&
    actual.hasMetadata === desired.hasMetadata &&
    actual.apiMdSha256 === desired.apiMdSha256
  );
}

async function readBranchState(ref, apiRelative, metaRelative) {
  const metadataBytes = await readRefFileBytes(ref, metaRelative);
  const apiMdBytes = await readRefFileBytes(ref, apiRelative);

  return {
    hasApiMd: Boolean(apiMdBytes),
    hasMetadata: Boolean(metadataBytes),
    apiMdSha256: metadataShaOrNull(metadataBytes),
  };
}

function branchSuffixFromIndex(index) {
  let value = index;
  let suffix = "";

  do {
    suffix = String.fromCharCode(97 + (value % 26)) + suffix;
    value = Math.floor(value / 26) - 1;
  } while (value >= 0);

  return suffix;
}

function compareBranchCandidates(left, right, preferredBranch) {
  if (left === preferredBranch && right !== preferredBranch) {
    return -1;
  }

  if (right === preferredBranch && left !== preferredBranch) {
    return 1;
  }

  return left.localeCompare(right);
}

function nextAvailableBranchName(preferredBranch, existingBranches) {
  if (!existingBranches.has(preferredBranch)) {
    return preferredBranch;
  }

  let index = 0;
  while (existingBranches.has(`${preferredBranch}_${branchSuffixFromIndex(index)}`)) {
    index += 1;
  }

  return `${preferredBranch}_${branchSuffixFromIndex(index)}`;
}

async function isAncestorRef(ancestorRef, branchRef) {
  const result = await git(["merge-base", "--is-ancestor", ancestorRef, branchRef], {
    capture: true,
    check: false,
  });
  return result.status === 0;
}

async function resolveBranchSelection({ preferredBranch, desiredState, apiRelative, metaRelative, requiredAncestorRef = null }) {
  const existingBranches = new Set(await listRemoteBranchesWithPrefix(preferredBranch));
  const orderedCandidates = [...existingBranches].sort((left, right) =>
    compareBranchCandidates(left, right, preferredBranch),
  );

  for (const candidateBranch of orderedCandidates) {
    const remoteRef = await fetchRemoteBranch(candidateBranch);
    const actualState = await readBranchState(remoteRef, apiRelative, metaRelative);
    if (!branchStateMatchesDesired(actualState, desiredState)) {
      continue;
    }

    if (requiredAncestorRef && !(await isAncestorRef(requiredAncestorRef, remoteRef))) {
      continue;
    }

    return {
      branchName: candidateBranch,
      reused: true,
      remoteRef,
    };
  }

  return {
    branchName: nextAvailableBranchName(preferredBranch, existingBranches),
    reused: false,
    remoteRef: null,
  };
}

function ensureBranchStateHasMetadataSha(branchLabel, state) {
  if (state.hasApiMd && !state.apiMdSha256) {
    throw new Error(`ERROR: ${branchLabel} is missing apiMdSha256 in api.metadata.yml.`);
  }
}

function selectBestPr(prs) {
  const candidates = prs.filter((pr) =>
    pr && typeof pr === "object" && "number" in pr && "url" in pr && "state" in pr && "updatedAt" in pr,
  );
  if (candidates.length === 0) {
    return null;
  }

  const openPrs = candidates.filter((pr) => String(pr.state || "").toLowerCase() === "open");
  const pool = openPrs.length ? openPrs : candidates;
  pool.sort((a, b) => String(b.updatedAt || "").localeCompare(String(a.updatedAt || "")));
  return pool[0];
}

function branchReferenceParts(headSelector) {
  if (headSelector === MAIN_REF) {
    return {
      owner: "Azure",
      branch: "main",
      display: headSelector,
    };
  }

  if (headSelector.includes(":")) {
    const [owner, branch] = headSelector.split(":", 2);
    return {
      owner,
      branch,
      display: headSelector,
    };
  }

  return {
    owner: "Azure",
    branch: headSelector,
    display: headSelector,
  };
}

async function targetBranchExists(headSelector) {
  const { owner, branch } = branchReferenceParts(headSelector);
  if (owner === "Azure") {
    return Boolean(await tryRemoteBranchRef(branch));
  }

  return Boolean(await tryForkBranchRef(owner, branch));
}

async function syncWorkingBranchInfo(headSelector, packageName = null) {
  if (!headSelector) {
    return null;
  }

  if (await targetBranchExists(headSelector)) {
    const { owner, branch } = branchReferenceParts(headSelector);
    return { owner, branch };
  }

  const targetTag = await resolveTargetTag(headSelector, packageName);
  if (targetTag) {
    return null;
  }

  return null;
}

async function buildSyncMetadataObject({ packageName, packageDir, baseBranch, reviewBranch, headSelector }) {
  const workingBranch = await syncWorkingBranchInfo(headSelector, packageName);
  if (!workingBranch) {
    return null;
  }

  const metadata = {
    schemaVersion: 1,
    repository: "Azure/azure-sdk-for-python",
    packageName,
    packageDir: normalizePackageDir(packageDir),
    baseBranch,
    reviewBranch,
    workingOwner: workingBranch.owner,
    workingBranch: workingBranch.branch,
  };

  const workingPr = await findOpenPrForHead(headSelector);
  metadata.workingPrNumber = workingPr && Number.isInteger(workingPr.number) ? workingPr.number : null;

  return metadata;
}

function buildSyncMetadataBlock(metadata) {
  if (!metadata) {
    return null;
  }

  return [
    `<!-- ${SYNC_METADATA_MARKER}`,
    SYNC_METADATA_WARNING,
    JSON.stringify(metadata, null, 2),
    "-->",
  ].join("\n");
}

function replaceSyncMetadataBlock(body, metadataBlock) {
  const cleanedBody = String(body || "")
    .replace(new RegExp(`<!--\\s*${SYNC_METADATA_MARKER}[\\s\\S]*?-->\\s*`, "g"), "")
    .trimEnd();

  if (!metadataBlock) {
    return cleanedBody;
  }

  return `${cleanedBody}\n\n${metadataBlock}`;
}

function buildReviewPrBody({ packageName, targetVersion, baseVersion, workingReference, baselineRef, syncMetadataBlock }) {
  const lines = [
    `Automated API review PR for ${packageName}.`,
    "",
    `- **${workingReference.label}:** ${workingReference.markdown} (version ${targetVersion})`,
    `- **Baseline:** ${baselineRef} (version ${baseVersion})`,
  ];

  if (workingReference.label === "Target tag") {
    lines.push("- **Update behavior:** Static tag-to-tag review; this PR cannot be automatically updated from a working branch.");
  }

  lines.push("", "Generated by scripts/api_md_workflow/create_api_review_pr.js.");

  return replaceSyncMetadataBlock(lines.join("\n"), syncMetadataBlock);
}

async function updatePrBody(prNumber, body) {
  const github = await getGithubApi();
  await github.updatePullRequestBody(prNumber, body);
}

async function ensurePrBodySyncMetadata(pr, metadataBlock) {
  if (!metadataBlock || !pr || !Number.isInteger(pr.number)) {
    return;
  }

  const desiredBody = replaceSyncMetadataBlock(pr.body || "", metadataBlock);
  if (desiredBody === (pr.body || "")) {
    return;
  }

  try {
    await updatePrBody(pr.number, desiredBody);
    logInfo(`Updated API review sync metadata on PR #${pr.number}.`);
    return;
  } catch (error) {
    const details = error instanceof Error ? error.message : String(error);
    logWarning(`WARNING: failed to update API review sync metadata on PR #${pr.number}.` + (details ? `\n  ${details}` : ""));
  }
}

async function findOpenPrForHead(headSelector) {
  const { owner, branch } = branchReferenceParts(headSelector);
  const selector = `${owner}:${branch}`;
  const allPrs = [];
  const github = await getGithubApi();

  try {
    allPrs.push(...(await github.listPullRequestsByHead(selector, 50)));
  } catch {
    // Fall back to search below. GitHub's head filtering can be stricter for fork branch names.
  }

  const searchQuery = `repo:${REPO_SLUG} is:pr is:open head:${branch}`;
  try {
    allPrs.push(...(await github.searchPullRequests(searchQuery, 50)));
  } catch {
    // Treat lookup failures as no matching working PR; the PR body can still link the branch.
  }

  if (allPrs.length === 0) {
    return null;
  }

  const deduped = new Map();
  for (const pr of allPrs) {
    if (
      pr &&
      typeof pr === "object" &&
      "number" in pr &&
      pr.headRefName === branch &&
      pr.headRepositoryOwner &&
      pr.headRepositoryOwner.login === owner
    ) {
      deduped.set(pr.number, pr);
    }
  }

  return selectBestPr([...deduped.values()]);
}

async function findOpenPrForBranches(baseBranch, headBranch) {
  const github = await getGithubApi();

  try {
    const prs = await github.listPullRequestsByBranches(baseBranch, headBranch, 20);
    if (prs.length > 0) {
      return selectBestPr(prs);
    }
  } catch {
    // Fall back to search below.
  }

  try {
    const prs = await github.searchPullRequests(`repo:${REPO_SLUG} is:pr is:open head:${headBranch} base:${baseBranch}`, 20);
    return selectBestPr(prs);
  } catch {
    return null;
  }
}

async function createDraftPr(baseBranch, headBranch, title, body) {
  const github = await getGithubApi();

  try {
    const createdPr = await github.createDraftPullRequest(baseBranch, headBranch, title, body);
    return {
      ok: true,
      url: createdPr && typeof createdPr.html_url === "string" ? createdPr.html_url : createdPr.url || "",
      stderr: "",
      stdout: "",
    };
  } catch (error) {
    return {
      ok: false,
      status: error && Number.isInteger(error.status) ? error.status : 1,
      stdout: "",
      stderr: error instanceof Error ? error.message : String(error),
    };
  }
}

function branchReferenceMarkdown(headSelector) {
  const { owner, branch, display } = branchReferenceParts(headSelector);
  const branchUrl = `https://github.com/${owner}/azure-sdk-for-python/tree/${encodeURIComponent(branch)}`;
  return `[branch \`${display}\`](${branchUrl})`;
}

async function baselineReferenceMarkdown(baseTag) {
  if (!baseTag) {
    return "empty";
  }

  const commitSha = await gitOut(["rev-list", "-n", "1", baseTag]);
  const commitUrl = `https://github.com/Azure/azure-sdk-for-python/commit/${commitSha}`;
  return `[tag \`${baseTag}\`](${commitUrl})`;
}

async function targetReferenceInfo(headSelector, packageName = null) {
  if (await targetBranchExists(headSelector)) {
    const pr = await findOpenPrForHead(headSelector);
    if (pr) {
      return {
        label: "Working PR",
        markdown: `[PR #${pr.number}](${pr.url})`,
      };
    }

    return {
      label: "Working branch",
      markdown: branchReferenceMarkdown(headSelector),
    };
  }

  const targetTag = await resolveTargetTag(headSelector, packageName);
  if (targetTag) {
    return {
      label: "Target tag",
      markdown: await baselineReferenceMarkdown(targetTag),
    };
  }

  return {
    label: "Working branch",
    markdown: branchReferenceMarkdown(headSelector),
  };
}

function writeBytes(filePath, bytes) {
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
  fs.writeFileSync(filePath, bytes);
}

async function generateApiBytesForRef({
  adapter,
  repoRoot,
  packageName,
  packageDir,
  runtimeExecutable,
  ref,
  refLabel,
  logger,
}) {
  const packageRelative = packageRelDir(packageDir);
  logInfo(`Overlaying package source from ${refLabel} (${ref})`);

  // Overlay just the package directory from the target ref onto the working tree
  await git(["checkout", ref, "--", packageRelative]);

  try {
    const version = adapter.readVersion(packageDir);

    await adapter.generateApiForPackage({
      repoRoot,
      packageName,
      runtimeExecutable,
      logger,
      refLabel,
    });

    const outputPath = apiMdPath(packageDir);
    if (!fs.existsSync(outputPath)) {
      throw new Error(`ERROR: did not produce ${outputPath}`);
    }

    const result = { apiMd: fs.readFileSync(outputPath), metadata: null, version };

    const metaPath = metadataPath(packageDir);
    if (fs.existsSync(metaPath)) {
      result.metadata = fs.readFileSync(metaPath);
    }

    return result;
  } finally {
    // Restore the package directory to the current branch state
    await git(["reset", "--", packageRelative], { check: false });
    await git(["checkout", "HEAD", "--", packageRelative]);
    // Clean any untracked files that the generation may have left behind
    await git(["clean", "-fd", "--", packageRelative], { check: false });
  }
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const adapter = loadAdapter(args.adapter);

  const packageDir = adapter.findPackageDir(REPO_ROOT, args.packageName);
  logInfo(`Found package at: ${packageDir}`);

  await ensureCleanWorktree();
  const originalBranch = await currentBranch();
  if (originalBranch === "HEAD") {
    throw new Error("ERROR: refusing to run from a detached HEAD.");
  }

  await git(["fetch", REMOTE, "main"]);

  const baseVersion = await validateBaseTag(args.packageName, args.base);

  const targetRef = args.target ? await resolveTargetRef(args.target, args.packageName) : MAIN_REF;

  try {
    logInfo(`\n=== Capturing baseline api.md from tag ${args.base} ===`);
    const baseResult = await generateApiBytesForRef({
      adapter,
      repoRoot: REPO_ROOT,
      packageName: args.packageName,
      packageDir,
      runtimeExecutable: args.runtimeExecutable,
      ref: args.base,
      refLabel: args.base,
      logger,
    });

    logInfo(`\n=== Capturing target api.md from ${targetRef} ===`);
    const targetResult = await generateApiBytesForRef({
      adapter,
      repoRoot: REPO_ROOT,
      packageName: args.packageName,
      packageDir,
      runtimeExecutable: args.runtimeExecutable,
      ref: targetRef,
      refLabel: targetRef,
      logger,
    });
    const targetVersion = targetResult.version;

    if (!apiResultsHaveApiDiff(baseResult, targetResult)) {
      logInfo(
        `\nNo API differences found for ${args.packageName} between ${args.base} (version ${baseVersion}) and ${targetRef} (version ${targetVersion}). No API review branches or PR were created.`,
      );
      return 0;
    }

    const apiPath = apiMdPath(packageDir);
    const apiRelative = apiMdRel(packageDir);
    const metaFilePath = metadataPath(packageDir);
    const metaRelative = metadataRel(packageDir);
    const desiredBaseState = desiredBranchState(baseResult);
    const desiredReviewState = desiredBranchState(targetResult);

    ensureBranchStateHasMetadataSha("baseline API result", desiredBaseState);
    ensureBranchStateHasMetadataSha("target API result", desiredReviewState);

    const baseSelection = await resolveBranchSelection({
      preferredBranch: apiReviewBranchName("base", args.packageName, baseVersion),
      desiredState: desiredBaseState,
      apiRelative,
      metaRelative,
    });
    const baseBranch = baseSelection.branchName;

    if (baseSelection.reused) {
      logInfo(`\n=== Reusing base branch ${baseBranch} ===`);
      await git(["checkout", "-B", baseBranch, baseSelection.remoteRef]);
    } else {
      logInfo(`\n=== Creating base branch ${baseBranch} ===`);
      await git(["checkout", "-B", baseBranch, MAIN_REF]);
      writeBytes(apiPath, baseResult.apiMd);
      await git(["add", apiRelative]);
      if (baseResult.metadata) {
        writeBytes(metaFilePath, baseResult.metadata);
        await git(["add", metaRelative]);
      }
      await git(["commit", "-m", `[API Review] Baseline api.md for ${args.packageName} ${baseVersion}`]);

      await git(["push", "--force-with-lease", REMOTE, baseBranch]);
    }

    const reviewSelection = await resolveBranchSelection({
      preferredBranch: apiReviewBranchName("review", args.packageName, targetVersion),
      desiredState: desiredReviewState,
      apiRelative,
      metaRelative,
      requiredAncestorRef: baseBranch,
    });
    const reviewBranch = reviewSelection.branchName;

    if (reviewSelection.reused) {
      logInfo(`\n=== Reusing review branch ${reviewBranch} ===`);
      await git(["checkout", "-B", reviewBranch, reviewSelection.remoteRef]);
    } else {
      logInfo(`\n=== Creating review branch ${reviewBranch} ===`);
      await git(["checkout", "-B", reviewBranch, baseBranch]);
      writeBytes(apiPath, targetResult.apiMd);
      await git(["add", apiRelative]);
      if (targetResult.metadata) {
        writeBytes(metaFilePath, targetResult.metadata);
        await git(["add", metaRelative]);
      }
      await git(["commit", "-m", `[API Review] api.md for ${args.packageName} ${targetVersion}`]);

      await git(["push", "--force-with-lease", REMOTE, reviewBranch]);
    }

    const title = `[API Review] ${args.packageName} ${targetVersion} (base ${baseVersion})`;
    const workingSelector = args.target || "main";
    const workingReference = await targetReferenceInfo(workingSelector, args.packageName);
    const baselineRef = await baselineReferenceMarkdown(args.base);
    const syncMetadata = await buildSyncMetadataObject({
      packageName: args.packageName,
      packageDir,
      baseBranch,
      reviewBranch,
      headSelector: workingSelector,
    });
    const syncMetadataBlock = buildSyncMetadataBlock(syncMetadata);

    const body = buildReviewPrBody({
      packageName: args.packageName,
      targetVersion,
      baseVersion,
      workingReference,
      baselineRef,
      syncMetadataBlock,
    });

    if (baseSelection.reused && reviewSelection.reused) {
      const existingPr = await findOpenPrForBranches(baseBranch, reviewBranch);
      if (existingPr) {
        await ensurePrBodySyncMetadata(existingPr, syncMetadataBlock);
        logInfo(`\n=== Reusing existing PR #${existingPr.number} ===`);
        logInfo(existingPr.url);
        return 0;
      }
    }

    logInfo("\n=== Opening PR ===");
    const compareUrl = `https://github.com/Azure/azure-sdk-for-python/compare/${baseBranch}...${reviewBranch}?expand=1`;
    const prCreate = await createDraftPr(baseBranch, reviewBranch, title, body);

    if (prCreate.ok) {
      if (prCreate.url) {
        logInfo(prCreate.url);
      }
    } else {
      const existingPr = await findOpenPrForBranches(baseBranch, reviewBranch);
      if (existingPr) {
        await ensurePrBodySyncMetadata(existingPr, syncMetadataBlock);
        logInfo(`\n=== Reusing existing PR #${existingPr.number} ===`);
        logInfo(existingPr.url);
        return 0;
      }

      const errorDetails = [
        `Exit code: ${prCreate.status}`,
        prCreate.stderr ? `stderr: ${prCreate.stderr.replace(/\r?\n/g, " ").trim()}` : "",
        prCreate.stdout ? `stdout: ${prCreate.stdout.replace(/\r?\n/g, " ").trim()}` : "",
        "Debug repro: use the GitHub REST API endpoint POST /repos/Azure/azure-sdk-for-python/pulls with base/head/title/body/draft=true.",
      ]
        .filter(Boolean)
        .join("\n  ");
      logWarning(
        "\nWARNING: GitHub PR creation failed. Both branches were pushed successfully -- open the PR manually here:\n" +
          `  ${compareUrl}\n` +
          `  Title: ${title}` +
          (errorDetails ? `\n  ${errorDetails}` : ""),
      );
    }

    return 0;
  } finally {
    await git(["checkout", originalBranch], { check: false });
  }
}

if (require.main === module) {
  (async () => {
    logger = await getDefaultLogger();
    try {
      process.exit(await main());
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      logError(message);
      process.exit(1);
    }
  })();
} else {
  module.exports = {
    __setCommandRunners({ git: gitRunner }) {
      if (gitRunner) {
        git = gitRunner;
      }
    },
    __setGithubApi(api) {
      githubApi = api;
    },
    buildSyncMetadataBlock,
    buildSyncMetadataObject,
    buildReviewPrBody,
    apiResultsHaveApiDiff,
    replaceSyncMetadataBlock,
    targetReferenceInfo,
  };
}
