#!/usr/bin/env node

const fs = require("fs");
const path = require("path");
const { spawnSync } = require("child_process");
const { getDefaultLogger } = require("./common");
const { loadAdapter, loadWorkflowConfig } = require("./adapter_config");

const REPO_ROOT = path.resolve(__dirname, "..", "..");
const REMOTE = "origin";
const MAIN_REF = `${REMOTE}/main`;
let logger = console;

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

  return args;
}

function run(cmd, args, options = {}) {
  const printable = [cmd, ...args].join(" ");
  logInfo(`$ ${printable}`);
  const result = spawnSync(cmd, args, {
    cwd: options.cwd ?? REPO_ROOT,
    env: options.env,
    encoding: "utf-8",
    stdio: options.capture ? "pipe" : "inherit",
    shell: false,
  });

  if (result.error) {
    const errorMessage = result.error instanceof Error ? result.error.message : String(result.error);
    throw new Error(`Command failed to start: ${printable}\n${errorMessage}`);
  }

  if ((options.check ?? true) && result.status !== 0) {
    throw new Error(`Command failed (${result.status}): ${printable}`);
  }

  return result;
}

let cachedGitExecutable = undefined;
let cachedGitAwareEnv = undefined;

function resolveGitExecutable() {
  if (cachedGitExecutable !== undefined) {
    return cachedGitExecutable;
  }

  if (process.platform !== "win32") {
    const resolved = spawnSync("git", ["--exec-path"], {
      cwd: REPO_ROOT,
      encoding: "utf-8",
      env: process.env,
    });
    cachedGitExecutable = resolved.status === 0 ? "git" : "git";
    return cachedGitExecutable;
  }

  cachedGitExecutable = findPreferredGitExecutable() || "git";
  return cachedGitExecutable;
}

function git(args, options = {}) {
  return run(resolveGitExecutable(), args, {
    ...options,
    env: buildGitAwareEnv(options.env),
  });
}

function gh(args, options = {}) {
  return run("gh", args, {
    ...options,
    env: buildGitAwareEnv(options.env),
  });
}

function gitOut(args) {
  return git(args, { capture: true }).stdout.trim();
}

function ensureCleanWorktree() {
  const status = gitOut(["status", "--porcelain"]);
  if (status) {
    throw new Error(`ERROR: working tree is not clean. Commit or stash changes before running.\n${status}`);
  }
}

function currentBranch() {
  return gitOut(["rev-parse", "--abbrev-ref", "HEAD"]);
}

function currentBranchOrSha() {
  const name = currentBranch();
  if (name === "HEAD") {
    return gitOut(["rev-parse", "--short", "HEAD"]);
  }
  return name;
}

function tagExists(tag) {
  const result = git(["rev-parse", "--verify", "--quiet", `refs/tags/${tag}`], {
    capture: true,
    check: false,
  });
  return result.status === 0;
}

function validateBaseTag(packageName, baseTag) {
  if (!baseTag.startsWith(`${packageName}_`)) {
    throw new Error(`ERROR: --base tag '${baseTag}' must start with '${packageName}_'.`);
  }

  const version = baseTag.slice(packageName.length + 1);
  if (!version) {
    throw new Error(`ERROR: --base tag '${baseTag}' is missing the version suffix.`);
  }

  if (!tagExists(baseTag)) {
    throw new Error(`ERROR: tag '${baseTag}' does not exist in this repository.`);
  }

  return version;
}

function remoteBranchRef(branch) {
  git(["fetch", REMOTE, branch]);
  return `${REMOTE}/${branch}`;
}

function resolveTargetRef(target) {
  if (!target.includes(":")) {
    return remoteBranchRef(target);
  }

  const [owner, branch] = target.split(":", 2);
  if (!owner || !branch) {
    throw new Error(`ERROR: invalid --target '${target}'. Expected either 'branch' or 'owner:branch'.`);
  }

  const forkUrl = `https://github.com/${owner}/azure-sdk-for-python.git`;
  git(["fetch", forkUrl, branch]);
  return "FETCH_HEAD";
}

function packageRelDir(packageDir) {
  return path.relative(REPO_ROOT, packageDir).split(path.sep).join("/");
}

function apiMdPath(packageDir) {
  return path.join(packageDir, "API.md");
}

function apiMdRel(packageDir) {
  return `${packageRelDir(packageDir)}/API.md`;
}

function metadataPath(packageDir) {
  return path.join(packageDir, "API.metadata.yml");
}

function metadataRel(packageDir) {
  return `${packageRelDir(packageDir)}/API.metadata.yml`;
}

function apiReviewBranchName(kind, packageName, version) {
  return `apireview/${kind}_${packageName}_${version}`;
}

function scoreGitCandidate(candidate) {
  const normalized = candidate.replace(/\//g, "\\").toLowerCase();
  if (normalized.includes("\\program files\\git\\cmd\\git.exe")) {
    return 0;
  }

  if (normalized.includes("\\program files\\git\\bin\\git.exe")) {
    return 1;
  }

  if (normalized.includes("\\git\\cmd\\git.exe")) {
    return 2;
  }

  if (normalized.includes("\\git\\bin\\git.exe")) {
    return 3;
  }

  if (normalized.includes("\\windows\\")) {
    return 100;
  }

  return 10;
}

function findPreferredGitExecutable() {
  if (process.platform !== "win32") {
    return null;
  }

  const candidates = new Set();
  const roots = [process.env.ProgramW6432, process.env.ProgramFiles, process.env["ProgramFiles(x86)"], process.env.LocalAppData];
  for (const root of roots) {
    if (!root) {
      continue;
    }

    candidates.add(path.join(root, "Git", "cmd", "git.exe"));
    candidates.add(path.join(root, "Git", "bin", "git.exe"));
    candidates.add(path.join(root, "Programs", "Git", "cmd", "git.exe"));
    candidates.add(path.join(root, "Programs", "Git", "bin", "git.exe"));
  }

  const pathKey = getPathEnvKey(process.env);
  for (const rawEntry of (process.env[pathKey] || "").split(path.delimiter)) {
    const entry = rawEntry.replace(/^"|"$/g, "");
    if (!entry) {
      continue;
    }

    candidates.add(path.join(entry, "git.exe"));
  }

  const existing = [...candidates].filter((candidate) => fs.existsSync(candidate));
  existing.sort((left, right) => scoreGitCandidate(left) - scoreGitCandidate(right) || left.localeCompare(right));
  return existing[0] || null;
}

function getGitExecPath(gitExecutable) {
  if (process.platform === "win32" && !path.isAbsolute(gitExecutable)) {
    return null;
  }

  const result = spawnSync(gitExecutable, ["--exec-path"], {
    cwd: REPO_ROOT,
    encoding: "utf-8",
  });

  if (result.status !== 0) {
    return null;
  }

  return result.stdout.trim() || null;
}

function samePathEntry(left, right) {
  if (process.platform === "win32") {
    return left.replace(/\\+$/, "").toLowerCase() === right.replace(/\\+$/, "").toLowerCase();
  }

  return left === right;
}

function getPathEnvKey(env) {
  return Object.keys(env).find((key) => key.toLowerCase() === "path") || "PATH";
}

function buildGitAwareEnv(baseEnv = process.env) {
  if (baseEnv === process.env && cachedGitAwareEnv) {
    return cachedGitAwareEnv;
  }

  const env = { ...baseEnv };
  const pathKey = getPathEnvKey(env);
  const gitExecutable = resolveGitExecutable();
  const gitExecPath = getGitExecPath(gitExecutable);

  if (path.isAbsolute(gitExecutable)) {
    const gitDir = path.dirname(gitExecutable);
    const currentEntries = (env[pathKey] || "").split(path.delimiter).filter(Boolean);
    const first = currentEntries[0] || "";
    if (!first || !samePathEntry(first, gitDir)) {
      env[pathKey] = [gitDir, ...currentEntries].join(path.delimiter);
      logInfo(`(using resolved git executable: ${gitExecutable})`);
    }
  }

  if (gitExecPath) {
    env.GIT_EXEC_PATH = gitExecPath;
  }

  if (baseEnv === process.env) {
    cachedGitAwareEnv = env;
  }

  return env;
}

function parseJsonOrNull(text) {
  try {
    const value = JSON.parse(text || "[]");
    return Array.isArray(value) ? value : null;
  } catch {
    return null;
  }
}

function parseJsonObjectOrNull(text) {
  try {
    const value = JSON.parse(text || "null");
    return value && typeof value === "object" && !Array.isArray(value) ? value : null;
  } catch {
    return null;
  }
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

function listRemoteBranchesWithPrefix(prefix) {
  const result = git(["ls-remote", "--heads", REMOTE, `refs/heads/${prefix}*`], {
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

function fetchRemoteBranch(branch) {
  git(["fetch", REMOTE, branch]);
  return branchRemoteRef(branch);
}

function readRefFileBytes(ref, relativePath) {
  const result = git(["show", `${ref}:${relativePath}`], {
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

function branchStateMatchesDesired(actual, desired) {
  return (
    actual.hasApiMd === desired.hasApiMd &&
    actual.hasMetadata === desired.hasMetadata &&
    actual.apiMdSha256 === desired.apiMdSha256
  );
}

function readBranchState(ref, apiRelative, metaRelative) {
  const metadataBytes = readRefFileBytes(ref, metaRelative);
  const apiMdBytes = readRefFileBytes(ref, apiRelative);

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

function isAncestorRef(ancestorRef, branchRef) {
  const result = git(["merge-base", "--is-ancestor", ancestorRef, branchRef], {
    capture: true,
    check: false,
  });
  return result.status === 0;
}

function resolveBranchSelection({ preferredBranch, desiredState, apiRelative, metaRelative, requiredAncestorRef = null }) {
  const existingBranches = new Set(listRemoteBranchesWithPrefix(preferredBranch));
  const orderedCandidates = [...existingBranches].sort((left, right) =>
    compareBranchCandidates(left, right, preferredBranch),
  );

  for (const candidateBranch of orderedCandidates) {
    const remoteRef = fetchRemoteBranch(candidateBranch);
    const actualState = readBranchState(remoteRef, apiRelative, metaRelative);
    if (!branchStateMatchesDesired(actualState, desiredState)) {
      continue;
    }

    if (requiredAncestorRef && !isAncestorRef(requiredAncestorRef, remoteRef)) {
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
    throw new Error(`ERROR: ${branchLabel} is missing apiMdSha256 in API.metadata.yml.`);
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

function exactHeadSelector(headSelector) {
  const { owner, branch } = branchReferenceParts(headSelector);
  return `${owner}:${branch}`;
}

function findOpenPrForHead(headSelector) {
  const selector = exactHeadSelector(headSelector);
  const allPrs = [];

  const direct = gh(
    [
      "pr",
      "list",
      "--repo",
      "Azure/azure-sdk-for-python",
      "--head",
      selector,
      "--state",
      "open",
      "--json",
      "number,url,state,updatedAt",
      "--limit",
      "50",
    ],
    { check: false, capture: true },
  );

  if (direct.status === 0) {
    const prs = parseJsonOrNull(direct.stdout);
    if (prs) {
      allPrs.push(...prs);
    }
  }

  const searchQuery = `repo:Azure/azure-sdk-for-python is:pr is:open head:${selector}`;
  const search = gh(
    [
      "pr",
      "list",
      "--repo",
      "Azure/azure-sdk-for-python",
      "--search",
      searchQuery,
      "--state",
      "open",
      "--json",
      "number,url,state,updatedAt",
      "--limit",
      "50",
    ],
    { check: false, capture: true },
  );

  if (search.status === 0) {
    const prs = parseJsonOrNull(search.stdout);
    if (prs) {
      allPrs.push(...prs);
    }
  }

  if (allPrs.length === 0) {
    return null;
  }

  const deduped = new Map();
  for (const pr of allPrs) {
    if (pr && typeof pr === "object" && "number" in pr) {
      deduped.set(pr.number, pr);
    }
  }

  return selectBestPr([...deduped.values()]);
}

function findOpenPrForBranches(baseBranch, headBranch) {
  const direct = gh(
    [
      "pr",
      "list",
      "--repo",
      "Azure/azure-sdk-for-python",
      "--base",
      baseBranch,
      "--head",
      headBranch,
      "--state",
      "open",
      "--json",
      "number,url,state,updatedAt",
      "--limit",
      "20",
    ],
    { check: false, capture: true },
  );

  if (direct.status === 0) {
    const prs = parseJsonOrNull(direct.stdout);
    if (prs && prs.length > 0) {
      return selectBestPr(prs);
    }
  }

  const search = gh(
    [
      "pr",
      "list",
      "--repo",
      "Azure/azure-sdk-for-python",
      "--search",
      `repo:Azure/azure-sdk-for-python is:pr is:open head:${headBranch} base:${baseBranch}`,
      "--json",
      "number,url,state,updatedAt",
      "--limit",
      "20",
    ],
    { check: false, capture: true },
  );

  if (search.status !== 0) {
    return null;
  }

  const prs = parseJsonOrNull(search.stdout);
  return prs ? selectBestPr(prs) : null;
}

function createDraftPr(baseBranch, headBranch, title, body) {
  const result = gh(
    [
      "api",
      "repos/Azure/azure-sdk-for-python/pulls",
      "--method",
      "POST",
      "--field",
      `base=${baseBranch}`,
      "--field",
      `head=${headBranch}`,
      "--field",
      `title=${title}`,
      "--field",
      `body=${body}`,
      "--field",
      "draft=true",
    ],
    { check: false, capture: true },
  );

  if (result.status === 0) {
    const createdPr = parseJsonObjectOrNull(result.stdout);
    return {
      ok: true,
      url: createdPr && typeof createdPr.html_url === "string" ? createdPr.html_url : "",
      stderr: result.stderr || "",
      stdout: result.stdout || "",
    };
  }

  return {
    ok: false,
    status: result.status,
    stdout: result.stdout || "",
    stderr: result.stderr || "",
  };
}

function branchReferenceMarkdown(headSelector) {
  const { owner, branch, display } = branchReferenceParts(headSelector);
  const branchUrl = `https://github.com/${owner}/azure-sdk-for-python/tree/${encodeURIComponent(branch)}`;
  return `[branch \`${display}\`](${branchUrl})`;
}

function workingReferenceMarkdown(headSelector) {
  const pr = findOpenPrForHead(headSelector);
  if (pr) {
    return `[PR #${pr.number}](${pr.url})`;
  }

  return branchReferenceMarkdown(headSelector);
}

function baselineReferenceMarkdown(baseTag) {
  if (!baseTag) {
    return "empty";
  }

  const commitSha = gitOut(["rev-list", "-n", "1", baseTag]);
  const commitUrl = `https://github.com/Azure/azure-sdk-for-python/commit/${commitSha}`;
  return `[tag \`${baseTag}\`](${commitUrl})`;
}

function writeBytes(filePath, bytes) {
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
  fs.writeFileSync(filePath, bytes);
}

function generateApiBytesForRef({
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
  git(["checkout", ref, "--", packageRelative]);

  try {
    const version = adapter.readVersion(packageDir);

    adapter.generateApiForPackage({
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
    git(["checkout", "HEAD", "--", packageRelative]);
    // Clean any untracked files that the generation may have left behind
    git(["clean", "-fd", "--", packageRelative], { check: false });
  }
}

function main() {
  const args = parseArgs(process.argv.slice(2));
  const adapter = loadAdapter(args.adapter);

  const packageDir = adapter.findPackageDir(REPO_ROOT, args.packageName);
  logInfo(`Found package at: ${packageDir}`);

  ensureCleanWorktree();
  const originalBranch = currentBranch();
  if (originalBranch === "HEAD") {
    throw new Error("ERROR: refusing to run from a detached HEAD.");
  }

  git(["fetch", REMOTE, "main"]);

  let baseVersion = "none";
  if (args.base) {
    baseVersion = validateBaseTag(args.packageName, args.base);
  }

  const targetRef = args.target ? resolveTargetRef(args.target) : MAIN_REF;

  try {
    let baseResult = null;
    if (args.base) {
      logInfo(`\n=== Capturing baseline API.md from tag ${args.base} ===`);
      baseResult = generateApiBytesForRef({
        adapter,
        repoRoot: REPO_ROOT,
        packageName: args.packageName,
        packageDir,
        runtimeExecutable: args.runtimeExecutable,
        ref: args.base,
        refLabel: args.base,
        logger,
      });
    }

    logInfo(`\n=== Capturing target API.md from ${targetRef} ===`);
    const targetResult = generateApiBytesForRef({
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

    const apiPath = apiMdPath(packageDir);
    const apiRelative = apiMdRel(packageDir);
    const metaFilePath = metadataPath(packageDir);
    const metaRelative = metadataRel(packageDir);
    const desiredBaseState = desiredBranchState(baseResult);
    const desiredReviewState = desiredBranchState(targetResult);

    ensureBranchStateHasMetadataSha("baseline API result", desiredBaseState);
    ensureBranchStateHasMetadataSha("target API result", desiredReviewState);

    const baseSelection = resolveBranchSelection({
      preferredBranch: apiReviewBranchName("base", args.packageName, baseVersion),
      desiredState: desiredBaseState,
      apiRelative,
      metaRelative,
    });
    const baseBranch = baseSelection.branchName;

    if (baseSelection.reused) {
      logInfo(`\n=== Reusing base branch ${baseBranch} ===`);
      git(["checkout", "-B", baseBranch, baseSelection.remoteRef]);
    } else {
      logInfo(`\n=== Creating base branch ${baseBranch} ===`);
      git(["checkout", "-B", baseBranch, MAIN_REF]);

      if (baseResult !== null) {
        writeBytes(apiPath, baseResult.apiMd);
        git(["add", apiRelative]);
        if (baseResult.metadata) {
          writeBytes(metaFilePath, baseResult.metadata);
          git(["add", metaRelative]);
        }
        git(["commit", "-m", `[API Review] Baseline API.md for ${args.packageName} ${baseVersion}`]);
      } else {
        const tracked = git(["ls-files", "--error-unmatch", apiRelative], {
          capture: true,
          check: false,
        });

        if (tracked.status === 0) {
          git(["rm", apiRelative]);
          const metaTracked = git(["ls-files", "--error-unmatch", metaRelative], {
            capture: true,
            check: false,
          });
          if (metaTracked.status === 0) {
            git(["rm", metaRelative]);
          }
          git(["commit", "-m", `[API Review] Remove API.md for ${args.packageName} (empty baseline)`]);
        } else {
          if (fs.existsSync(apiPath)) {
            fs.unlinkSync(apiPath);
          }
          if (fs.existsSync(metaFilePath)) {
            fs.unlinkSync(metaFilePath);
          }
          git(["commit", "--allow-empty", "-m", `[API Review] Empty baseline for ${args.packageName}`]);
        }
      }

      git(["push", "--force-with-lease", REMOTE, baseBranch]);
    }

    const reviewSelection = resolveBranchSelection({
      preferredBranch: apiReviewBranchName("review", args.packageName, targetVersion),
      desiredState: desiredReviewState,
      apiRelative,
      metaRelative,
      requiredAncestorRef: baseBranch,
    });
    const reviewBranch = reviewSelection.branchName;

    if (reviewSelection.reused) {
      logInfo(`\n=== Reusing review branch ${reviewBranch} ===`);
      git(["checkout", "-B", reviewBranch, reviewSelection.remoteRef]);
    } else {
      logInfo(`\n=== Creating review branch ${reviewBranch} ===`);
      git(["checkout", "-B", reviewBranch, baseBranch]);
      writeBytes(apiPath, targetResult.apiMd);
      git(["add", apiRelative]);
      if (targetResult.metadata) {
        writeBytes(metaFilePath, targetResult.metadata);
        git(["add", metaRelative]);
      }

      const diff = git(["diff", "--cached", "--quiet"], {
        capture: true,
        check: false,
      });

      if (diff.status === 0) {
        git([
          "commit",
          "--allow-empty",
          "-m",
          `[API Review] API.md for ${args.packageName} ${targetVersion} (no diff vs baseline)`,
        ]);
      } else {
        git(["commit", "-m", `[API Review] API.md for ${args.packageName} ${targetVersion}`]);
      }

      git(["push", "--force-with-lease", REMOTE, reviewBranch]);
    }

    const title = `[API Review] ${args.packageName} ${targetVersion} (base ${baseVersion})`;
    const workingSelector = args.target || originalBranch;
    const workingRef = workingReferenceMarkdown(workingSelector);
    const baselineRef = baselineReferenceMarkdown(args.base);

    const body = [
      `Automated API review PR for ${args.packageName}.`,
      "",
      `- **Working branch:** ${workingRef} (version ${targetVersion})`,
      `- **Baseline:** ${baselineRef} (version ${baseVersion})`,
      "",
      "Generated by scripts/api_md_workflow/create_api_review_pr.js.",
    ].join("\n");

    if (baseSelection.reused && reviewSelection.reused) {
      const existingPr = findOpenPrForBranches(baseBranch, reviewBranch);
      if (existingPr) {
        logInfo(`\n=== Reusing existing PR #${existingPr.number} ===`);
        logInfo(existingPr.url);
        return 0;
      }
    }

    logInfo("\n=== Opening PR ===");
    const compareUrl = `https://github.com/Azure/azure-sdk-for-python/compare/${baseBranch}...${reviewBranch}?expand=1`;
    const prCreate = createDraftPr(baseBranch, reviewBranch, title, body);

    if (prCreate.ok) {
      if (prCreate.url) {
        logInfo(prCreate.url);
      }
    } else {
      const existingPr = findOpenPrForBranches(baseBranch, reviewBranch);
      if (existingPr) {
        logInfo(`\n=== Reusing existing PR #${existingPr.number} ===`);
        logInfo(existingPr.url);
        return 0;
      }

      const errorDetails = [
        `Exit code: ${prCreate.status}`,
        prCreate.stderr ? `stderr: ${prCreate.stderr.replace(/\r?\n/g, " ").trim()}` : "",
        prCreate.stdout ? `stdout: ${prCreate.stdout.replace(/\r?\n/g, " ").trim()}` : "",
        "Debug repro: GH_DEBUG=1 gh api repos/Azure/azure-sdk-for-python/pulls --method POST --field base=<base> --field head=<head> --field title=<title> --field body=<body> --field draft=true",
      ]
        .filter(Boolean)
        .join("\n  ");
      logWarning(
        "\nWARNING: `gh api` PR creation failed. Both branches were pushed successfully -- open the PR manually here:\n" +
          `  ${compareUrl}\n` +
          `  Title: ${title}` +
          (errorDetails ? `\n  ${errorDetails}` : ""),
      );
    }

    return 0;
  } finally {
    git(["checkout", originalBranch], { check: false });
  }
}

(async () => {
  logger = await getDefaultLogger();
  try {
    process.exit(main());
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    logError(message);
    process.exit(1);
  }
})();
