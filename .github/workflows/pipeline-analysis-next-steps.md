---
# Pipeline Analysis - Next Steps (agentic workflow)
#
# When a pull request's Azure DevOps CI fails, `pipeline-analysis-next-steps-trigger.yml`
# dispatches this workflow with the PR number. A deterministic setup step runs the existing `azsdk ci analyze` tool to produce structured failure data; the Copilot
# agent then turns that into a concise, human-readable "Pipeline Analysis Next Steps" comment on the PR.
#
# Copilot runs on the built-in token via `copilot-requests: write` (billed to the org) # The agent job is read-only; the comment is posted by a separate
# gh-aw safe-outputs job.
#
# The agent has read-only access to the repository's skills under `.github/skills/` (checked
# out from the default branch, NOT the PR branch). It consults the azsdk pipeline-analysis skill
# to categorize failures; drop in additional pipeline skills and the agent will pick them up.
#
# Skill invocations emit usage telemetry to the azsdk producer (Application Insights) via the
# Copilot PostToolUse hook in `.github/hooks/hooks.json`. That hook only recognizes a skill
# invocation from the `skill`, `view`, or `read_file` tools (matching `/skills/<name>/SKILL.md`),
# so the prompt requires skills to be read with `view` - reading them via shell `cat` would make
# the invocations invisible to telemetry. Ingestion uses the InstrumentationKey baked into the
# azsdk connection string, so it only needs egress to the ingestion endpoint (see network.allowed)
# - not an Azure login.
#
# After editing this file, run 'gh aw compile pipeline-analysis-next-steps' to regenerate the
# lock file.
description: "Analyze a pull request's failing Azure DevOps pipeline with the azsdk analyze tool and post a Copilot-authored 'Pipeline Analysis Next Steps' comment."
run-name: "Pipeline Analysis - Next Steps / PR #${{ github.event.inputs.pr_number }} / ${{ github.event.inputs.ci_head_sha }}"

on:
  workflow_dispatch:
    inputs:
      pr_number:
        description: "Pull request number whose failing pipeline should be analyzed"
        required: true
        type: string
      ci_conclusion:
        description: "Conclusion of the completed azure-pipelines PR-CI check run (e.g. failure) for CI-triggered runs"
        required: false
        type: string
      ci_head_sha:
        description: "Head SHA of the completed PR-CI check run, for stale-commit detection on CI-triggered runs"
        required: false
        type: string

# The workflow is always dispatched (by the trigger workflow or manually); never runs off the
# repository-associated PR of its own ref.
if: ${{ github.event_name == 'workflow_dispatch' }}

engine: copilot

# Agent job runs read-only; copilot-requests:write bills the Copilot CLI usage to the org. The
# separate safe-outputs job receives the pull-requests:write scope it needs to post the comment.
permissions:
  contents: read
  pull-requests: read
  actions: read
  checks: read
  copilot-requests: write

# network.allowed also governs content sanitization: dev.azure.com and aka.ms must be allowed
# so the Azure DevOps build links and the CI-fix link in the analysis survive in the comment.
# *.in.applicationinsights.azure.com lets the azsdk telemetry producer (the Copilot PostToolUse
# hook -> `azsdk ingest-telemetry`) upload skill-invocation telemetry from inside the sandbox;
# ingestion authenticates with the InstrumentationKey in the azsdk connection string, so no Azure
# login is required - only egress to the ingestion endpoint. Mirrors issue-triage.
network:
  allowed:
    - defaults
    - github
    - dev.azure.com
    - aka.ms
    - "*.in.applicationinsights.azure.com"

# Sparse-checkout keeps the agent's tree minimal: eng (azsdk CLI installer + telemetry hook
# script), .github/skills (read-only skills the agent consults), and .github/hooks (so Copilot
# loads the PostToolUse hook that emits skill-invocation telemetry to the azsdk producer).
# `documentation` is only present in azure-rest-api-specs; sparse-checkout silently ignores it in
# repos that do not have it, so the same workflow file stays syncable across all language repos.
checkout:
  sparse-checkout: |
    eng
    .github/skills
    .github/hooks
    documentation/ci-fix.md

# Deterministic pre-agent steps: install the azsdk CLI (the analyze tool is a plain stdio MCP
# server that gh-aw's MCP Gateway cannot host, so we drive its CLI surface) and run the
# analysis into a workspace file for the agent to read.
steps:
  - name: Install azsdk CLI
    shell: pwsh
    run: |
      # Install to the azsdk common install directory ($HOME/bin) rather than a custom path so the
      # Copilot telemetry hook (eng/common/scripts/azsdk_tool_telemetry.ps1), which locates the
      # binary via Get-CommonInstallDirectory, can run `azsdk ingest-telemetry` on skill
      # invocations. Still add it to PATH so the analyze step below resolves `azsdk`.
      $dir = Join-Path $HOME 'bin'
      ./eng/common/mcp/azure-sdk-mcp.ps1 -InstallDirectory $dir
      Add-Content -Path $env:GITHUB_PATH -Value $dir
  - name: Analyze failing pipeline
    shell: bash
    env:
      GITHUB_TOKEN: ${{ github.token }}
      PR_URL: "https://github.com/${{ github.repository }}/pull/${{ github.event.inputs.pr_number }}"
    run: |
      set -uo pipefail
      # `azsdk ci analyze` exits non-zero both when it finds no failing builds (it sets a
      # "No failed Azure Pipeline builds found ..." response error) and on real auth/network/CLI
      # errors. Only the former is an acceptable no-op; every other non-zero exit must fail this
      # step so the run surfaces the problem instead of the agent silently treating an error as
      # "nothing to report" and finishing green.
      exit_code=0
      azsdk ci analyze "$PR_URL" > "$GITHUB_WORKSPACE/pipeline-analysis.txt" 2>&1 || exit_code=$?
      echo "azsdk ci analyze exit code: $exit_code"
      echo "----- pipeline-analysis.txt -----"
      # The file holds PR-controlled build output. Prefix any line that looks like a GitHub
      # Actions workflow command (starts with `::`) with a space so it is logged as plain text
      # instead of being interpreted.
      sed 's/^::/ ::/' "$GITHUB_WORKSPACE/pipeline-analysis.txt"
      if [ "$exit_code" -ne 0 ]; then
        if grep -qF "No failed Azure Pipeline builds found" "$GITHUB_WORKSPACE/pipeline-analysis.txt"; then
          echo "No failing Azure Pipeline builds resolved for this PR; the agent will no-op."
        else
          echo "::error::azsdk ci analyze failed (exit $exit_code) with an unexpected error; failing the step."
          exit "$exit_code"
        fi
      fi

post-steps:
  - name: Upload pipeline analysis
    uses: actions/upload-artifact@v7
    with:
      name: pipeline-analysis
      path: pipeline-analysis.txt
      if-no-files-found: error
      retention-days: 7

tools:
  github:
    toolsets: [context, repos, pull_requests, actions]
  # Read-only: the agent reads the analysis file plus the checked-out skills under
  # `.github/skills/` (find/ls to discover them, cat/head/tail to read). No write tools.
  # `azsdk ci test-results` is allowed because `azsdk ci analyze` reports artifact *names* only;
  # fetching their contents is a read-only download and is often required to explain a failure.
  bash: ["cat", "ls", "head", "tail", "wc", "find", "azsdk ci test-results:*"]

safe-outputs:
  # A single, self-updating "Pipeline Analysis Next Steps" comment on the PR. hide-older-comments
  # collapses this workflow's previous comments so only the latest analysis stays visible.
  add-comment:
    max: 1
    target: "${{ github.event.inputs.pr_number }}"
    hide-older-comments: true
  # Let the agent cleanly do nothing when the tool reports no failing builds. report-as-issue:
  # false stops gh-aw's default of opening/updating an "[aw] No-Op Runs" tracking issue on every
  # stale/no-failure run.
  noop:
    report-as-issue: false
  # Failures surface on the PR/run; do not open tracking issues.
  missing-tool:
    create-issue: false
  missing-data:
    create-issue: false
  report-incomplete:
    create-issue: false
  report-failure-as-issue: false

timeout-minutes: 20
concurrency: pipeline-analysis-next-steps-${{ github.event.inputs.pr_number }}
---

# Pipeline Analysis - Next Steps

You are the Azure SDK Tools **pipeline next-steps** agent for `${{ github.repository }}`.

A CI pipeline failed on pull request **#${{ github.event.inputs.pr_number }}**. A deterministic
setup step already ran the azsdk pipeline analyze tool
(`azsdk ci analyze <pr>`) and wrote its full output to **`pipeline-analysis.txt`** in the
workspace root. Your job is to turn that raw tool output into one concise, actionable
**"Pipeline Analysis Next Steps"** comment on the PR.

## Step 0 - Read the analysis and validate

1. Read `pipeline-analysis.txt` (it is in the current working directory).
2. If the file is empty, or contains `No failed Azure Pipeline builds found`, or otherwise
   shows no real pipeline/test failures, then there is nothing to report: use the `noop` safe
   output and stop. Do **not** post a comment in that case.
3. Stale-commit guard: if `${{ github.event.inputs.ci_head_sha }}` is non-empty, fetch
   the PR's current head SHA. If they differ, the completed run is for a superseded commit -
   use `noop` and stop rather than posting stale analysis.

## Step 1 - Analyze the failures

**Consult the repository's skills first.** The skills directory is checked out read-only at
`.github/skills/` (from the default branch — this is *not* the PR's code):

> **Read every `SKILL.md` with the `view` tool, not with `cat`/`head`/`tail`.** Skill-usage
> telemetry is emitted by the Copilot `PostToolUse` hook, which only recognizes a skill invocation
> from the `view`/`read_file` tools (or an explicit `skill` call). A skill read through a shell
> command is invisible to telemetry and will not be counted.

- Read `.github/skills/azsdk-common-pipeline-analysis/SKILL.md` and its
  `references/failure-patterns.md` - they define the failure categories and the pattern-to-fix
  mappings you apply below.
- The pipeline analysis has **already been run for you** (its output is in
  `pipeline-analysis.txt`), so ignore any skill instructions about invoking `azsdk` /
  `azsdk_analyze_pipeline` MCP tools - you do not have them and do not need them.
- Keep the comment in the exact format defined in Step 2; do **not** adopt the skill's own
  output format from `references/output-format.md`.
- If another skill under `.github/skills/` is directly relevant to the specific failure you are
  analyzing (for example, a skill describing how to fix a particular pipeline failure), read its
  `SKILL.md` with the `view` tool and apply it too. Ignore skills unrelated to the failures at hand.

Apply those categories and pattern-to-fix mappings to the `pipeline-analysis.txt` output to
determine what failed and the most likely root cause(s), and preserve any Azure DevOps build URLs
from the output so reviewers can jump to the logs.

### Step 1a - Fetch artifact contents if the analysis only names them

`azsdk ci analyze` reports the *names* of published artifacts, not their contents. If
`pipeline-analysis.txt` references artifacts (for example test-results or log artifacts) and their
names alone are not enough to explain the failure, download them:

```bash
azsdk ci test-results "https://github.com/${{ github.repository }}/pull/${{ github.event.inputs.pr_number }}"
```

Only do this when the analysis is insufficient on its own - it is an extra network call. If the
command fails or returns nothing, continue with what `pipeline-analysis.txt` already gave you and
do not treat the failure as fatal.

### Step 1b - azure-rest-api-specs only: consult the CI fix guide

If `${{ github.repository }}` is `Azure/azure-rest-api-specs`, also read `documentation/ci-fix.md`
from the checked-out tree. It documents how to reproduce and fix that repo's specific checks
(Swagger BreakingChange, ModelValidation, SemanticValidation, PrettierCheck, TypeSpec Validation,
Avocado, and the SDK Validation suites), including the exact local commands. Prefer its guidance
over generic advice, and cite the relevant commands in your recommended next steps.

For every other repository this file does not exist - skip this step entirely and do not mention it.

## Step 2 - Compose the "Pipeline Analysis Next Steps" comment

Post exactly one comment using the `add-comment` safe output, in this shape:

````markdown
<details>
<summary><strong>[Pilot] PR Pipeline Failure Analysis</strong></summary>

A CI pipeline failed on this pull request. Here is an automated analysis of what went wrong
and how to get the build green.

### What failed
<one short paragraph or a few bullets: the failing pipeline(s)/stage(s) and the most likely
root cause, with Azure DevOps build links where available>

### Recommended next steps
- <specific, actionable step tied to the failure above>
- <additional steps as needed>
- See the CI troubleshooting guide: https://aka.ms/ci-fix
- Push new commits to address the failures; this comment updates automatically on the next
  failing run.

<details>
<summary>Raw pipeline analysis (azsdk ci analyze)</summary>

```
<the relevant portion of pipeline-analysis.txt, trimmed if very long>
```

</details>

</details>

> Copilot detected the failing pipeline and generated the analysis above. To have it attempt a
> fix automatically, reply with `@copilot please fix the failing pipeline on this PR`.
````

## Constraints (non-negotiable)

1. **Read-only.** Do not check out, build, run, or modify PR code. (Reading the repository's own
   checked-out `.github/skills/` guidance is fine - that is not PR code, and `azsdk ci test-results`
   only downloads published artifacts.) Your only mutating action is posting the single comment via
   the `add-comment` safe output. Do not use `gh`, the GitHub MCP write tools, or direct API calls
   to comment.
2. **One comment.** Emit at most one `add-comment`. Keep it concise and skimmable; put the raw
   tool output inside the collapsible `<details>` block, trimming it if it is very long.
3. **The `@copilot` line is an example only.** Write it in backticks exactly as shown so it does
   not ping anyone. Do not @-mention any real user.
4. **Ground every claim in the tool output.** If `pipeline-analysis.txt` does not support a
   conclusion, do not state it. When failures are ambiguous, point reviewers at the linked
   build logs instead of guessing.
5. If there is nothing meaningful to report (see Step 0), use `noop` and post nothing.
