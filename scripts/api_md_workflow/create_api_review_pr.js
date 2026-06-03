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
  });

  if ((options.check ?? true) && result.status !== 0) {
    throw new Error(`Command failed (${result.status}): ${printable}`);
  }

  return result;
}

function git(args, options = {}) {
  return run("git", args, options);
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

function findRealGitExe() {
  if (process.platform !== "win32") {
    return null;
  }

  const seen = new Set();
  const entries = (process.env.PATH || "").split(path.delimiter);
  for (const rawEntry of entries) {
    const entry = rawEntry.replace(/^"|"$/g, "");
    if (!entry) {
      continue;
    }

    const key = entry.toLowerCase();
    if (seen.has(key)) {
      continue;
    }
    seen.add(key);

    const candidate = path.join(entry, "git.exe");
    if (fs.existsSync(candidate)) {
      return candidate;
    }
  }

  const fallback = "C:\\Program Files\\Git\\cmd\\git.exe";
  return fs.existsSync(fallback) ? fallback : null;
}

function envWithRealGit() {
  const env = { ...process.env };
  const realGit = findRealGitExe();
  if (!realGit) {
    return env;
  }

  const gitDir = path.dirname(realGit);
  const current = env.PATH || "";
  const parts = current.split(path.delimiter);
  const first = parts[0] || "";
  if (first.replace(/\\+$/, "").toLowerCase() !== gitDir.replace(/\\+$/, "").toLowerCase()) {
    env.PATH = `${gitDir}${path.delimiter}${current}`;
    logInfo(`(prepending real git to PATH for gh: ${gitDir})`);
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

function findOpenPrForHead(headSelector) {
  const env = envWithRealGit();
  const selectors = [headSelector];
  if (headSelector.includes(":")) {
    const branchOnly = headSelector.split(":", 2)[1];
    if (branchOnly && !selectors.includes(branchOnly)) {
      selectors.push(branchOnly);
    }
  }

  const allPrs = [];
  for (const selector of selectors) {
    const direct = run(
      "gh",
      [
        "pr",
        "list",
        "--repo",
        "Azure/azure-sdk-for-python",
        "--head",
        selector,
        "--state",
        "all",
        "--json",
        "number,url,state,updatedAt",
        "--limit",
        "50",
      ],
      { check: false, capture: true, env },
    );

    if (direct.status === 0) {
      const prs = parseJsonOrNull(direct.stdout);
      if (prs) {
        allPrs.push(...prs);
      }
    }
  }

  for (const selector of selectors) {
    const searchQuery = `repo:Azure/azure-sdk-for-python head:${selector}`;
    const search = run(
      "gh",
      [
        "pr",
        "list",
        "--repo",
        "Azure/azure-sdk-for-python",
        "--search",
        searchQuery,
        "--state",
        "all",
        "--json",
        "number,url,state,updatedAt",
        "--limit",
        "50",
      ],
      { check: false, capture: true, env },
    );

    if (search.status === 0) {
      const prs = parseJsonOrNull(search.stdout);
      if (prs) {
        allPrs.push(...prs);
      }
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

function workingReferenceMarkdown(headSelector) {
  const pr = findOpenPrForHead(headSelector);
  if (pr) {
    return `[PR #${pr.number}](${pr.url})`;
  }

  if (headSelector.includes(":")) {
    const [owner, branch] = headSelector.split(":", 2);
    const branchUrl = `https://github.com/${owner}/azure-sdk-for-python/tree/${encodeURIComponent(branch)}`;
    return `[branch \`${headSelector}\`](${branchUrl})`;
  }

  const branchUrl = `https://github.com/Azure/azure-sdk-for-python/tree/${encodeURIComponent(headSelector)}`;
  return `[branch \`${headSelector}\`](${branchUrl})`;
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
    run("git", ["clean", "-fd", "--", packageRelative], { check: false });
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

    const baseBranch = `base_${args.packageName}_${baseVersion}`;
    const reviewBranch = `review_${args.packageName}_${targetVersion}`;

    logInfo(`\n=== Creating base branch ${baseBranch} ===`);
    git(["checkout", "-B", baseBranch, MAIN_REF]);

    const apiPath = apiMdPath(packageDir);
    const apiRelative = apiMdRel(packageDir);
    const metaFilePath = metadataPath(packageDir);
    const metaRelative = metadataRel(packageDir);

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

    const title = `[API Review] ${args.packageName} ${targetVersion} (base ${baseVersion})`;
    const workingSelector = args.target || originalBranch;
    const workingRef = workingReferenceMarkdown(workingSelector);
    const baselineDescription = args.base
      ? `tag \`${args.base}\``
      : "_empty_";

    const body = [
      `Automated API review PR for \`${args.packageName}\`.`,
      "",
      `- **Working branch:** ${workingRef}`,
      `- **Target:** \`${args.target || "origin/main"}\` (version \`${targetVersion}\`)`,
      `- **Baseline:** ${baselineDescription} (version \`${baseVersion}\`)`,
      "",
      "Generated by `scripts/api_md_workflow/create_api_review_pr.js`.",
    ].join("\n");

    logInfo("\n=== Opening PR ===");
    const compareUrl = `https://github.com/Azure/azure-sdk-for-python/compare/${baseBranch}...${reviewBranch}?expand=1`;
    const prCreate = run(
      "gh",
      [
        "pr",
        "create",
        "--repo",
        "Azure/azure-sdk-for-python",
        "--base",
        baseBranch,
        "--head",
        reviewBranch,
        "--title",
        title,
        "--body",
        body,
        "--draft",
      ],
      { check: false, env: envWithRealGit() },
    );

    if (prCreate.status !== 0) {
      logWarning(
        "\nWARNING: `gh pr create` failed. Both branches were pushed successfully -- open the PR manually here:\n" +
          `  ${compareUrl}\n` +
          `  Title: ${title}`,
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
