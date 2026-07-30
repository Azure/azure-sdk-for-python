---
# Pipeline Analysis - Auto Fix (agentic workflow)
#
# Companion to `pipeline-analysis-next-steps.md`. Where that workflow only *explains* a failing
# Azure DevOps CI run, this one attempts to *fix* it.
#
# Delivery model: the fix is NOT pushed onto the contributor's branch. The agent's changes are
# published to a separate `copilot-pipeline-fix/*` branch and offered as a draft pull request.
# The PR initially targets the original PR's CI-enabled base branch so the repository's normal
# Azure DevOps PR pipeline runs. After that CI proves the fix,
# `pipeline-analysis-fix-validation.yml` retargets the same PR to the original PR's head branch.
# Nothing lands without a human merge.
#
# Fork PRs are skipped by the dispatcher: the head branch lives in the fork, so a base-repo
# workflow cannot push a branch there or open a PR against it.
#
# Branches created here are cleaned up after 7 days by
# `pipeline-analysis-fix-branch-cleanup.yml`, and the draft PR auto-closes via `expires: 7`.
#
# After editing this file, run 'gh aw compile pipeline-analysis-auto-fix' to regenerate the
# lock file.
description: "Attempt an automated fix for a pull request's failing Azure DevOps pipeline and publish it as a draft PR targeting the original PR's branch."
run-name: "Pipeline Analysis - Auto Fix / PR #${{ github.event.inputs.pr_number }} / ${{ github.event.inputs.ci_head_sha }}"

on:
  workflow_dispatch:
    inputs:
      pr_number:
        description: "Pull request number whose failing pipeline should be fixed"
        required: true
        type: string
      pr_head_ref:
        description: "Head branch of that pull request; the validated fix PR is retargeted here"
        required: true
        type: string
      ci_head_sha:
        description: "Head SHA of the completed PR-CI check run; identifies the validation baseline"
        required: true
        type: string
      analysis_run_id:
        description: "Run ID of the successful next-steps workflow containing the analysis artifact"
        required: true
        type: string
      validation_base_ref:
        description: "CI-enabled base branch the draft fix PR initially targets"
        required: true
        type: string

if: ${{ github.event_name == 'workflow_dispatch' }}

engine: copilot

permissions:
  contents: read
  pull-requests: read
  actions: read
  checks: read
  copilot-requests: write

network:
  allowed:
    - defaults
    - github
    - dev.azure.com
    - aka.ms
    - "*.in.applicationinsights.azure.com"

# Check out the exact failing commit, not the mutable branch. The stale guard below separately
# verifies that this commit is still the PR head before the agent publishes anything.
checkout:
  ref: ${{ github.event.inputs.ci_head_sha }}
  # The create-pull-request handler compares the fix with the validation base.
  fetch-depth: 0

steps:
  - name: Validate dispatch eligibility
    shell: bash
    env:
      GH_TOKEN: ${{ github.token }}
      AUTO_FIX_MODE: ${{ vars.PIPELINE_ANALYSIS_AUTO_FIX_MODE }}
      PR_NUMBER: ${{ github.event.inputs.pr_number }}
      EXPECTED_HEAD_REF: ${{ github.event.inputs.pr_head_ref }}
      EXPECTED_HEAD_SHA: ${{ github.event.inputs.ci_head_sha }}
      EXPECTED_BASE_REF: ${{ github.event.inputs.validation_base_ref }}
    run: |
      set -euo pipefail
      pr_json="$(gh pr view "$PR_NUMBER" --repo "$GITHUB_REPOSITORY" \
        --json baseRefName,headRefName,headRefOid,isCrossRepository,isDraft,labels,state)"

      case "${AUTO_FIX_MODE:-disabled}" in
        enabled) ;;
        pilot)
          if ! jq -e '[.labels[].name] | index("pipeline-auto-fix") != null' \
               <<<"$pr_json" >/dev/null; then
            echo "::error::Pilot mode requires the pipeline-auto-fix label."
            exit 1
          fi
          ;;
        disabled|"")
          echo "::error::Pipeline auto-fix is disabled."
          exit 1
          ;;
        *)
          echo "::error::Unknown PIPELINE_ANALYSIS_AUTO_FIX_MODE '$AUTO_FIX_MODE'."
          exit 1
          ;;
      esac

      if [ "$(jq -r '.state' <<<"$pr_json")" != "OPEN" ] ||
         [ "$(jq -r '.isDraft' <<<"$pr_json")" = "true" ] ||
         [ "$(jq -r '.isCrossRepository' <<<"$pr_json")" = "true" ] ||
         [ "$(jq -r '.headRefName' <<<"$pr_json")" != "$EXPECTED_HEAD_REF" ] ||
         [ "$(jq -r '.headRefOid' <<<"$pr_json")" != "$EXPECTED_HEAD_SHA" ] ||
         [ "$(jq -r '.baseRefName' <<<"$pr_json")" != "$EXPECTED_BASE_REF" ]; then
        echo "::error::Dispatch inputs do not match an open, non-draft, same-repository PR."
        exit 1
      fi
      case "$EXPECTED_HEAD_REF" in
        copilot-pipeline-fix/*)
          echo "::error::Automated fix PRs cannot recursively trigger auto-fix."
          exit 1
          ;;
      esac
  - name: Install azsdk CLI
    shell: pwsh
    run: |
      $dir = Join-Path $HOME 'bin'
      ./eng/common/mcp/azure-sdk-mcp.ps1 -InstallDirectory $dir
      Add-Content -Path $env:GITHUB_PATH -Value $dir
  - name: Verify analysis run
    shell: bash
    env:
      GH_TOKEN: ${{ github.token }}
      ANALYSIS_RUN_ID: ${{ github.event.inputs.analysis_run_id }}
      EXPECTED_RUN_TITLE: "Pipeline Analysis - Next Steps / PR #${{ github.event.inputs.pr_number }} / ${{ github.event.inputs.ci_head_sha }}"
    run: |
      set -euo pipefail
      run_json="$(gh run view "$ANALYSIS_RUN_ID" --repo "$GITHUB_REPOSITORY" \
        --json conclusion,displayTitle,event)"
      if [ "$(jq -r '.event' <<<"$run_json")" != "workflow_dispatch" ] ||
         [ "$(jq -r '.displayTitle' <<<"$run_json")" != "$EXPECTED_RUN_TITLE" ] ||
         [ "$(jq -r '.conclusion' <<<"$run_json")" != "success" ]; then
        echo "::error::Analysis run $ANALYSIS_RUN_ID is not the successful run for this PR and SHA."
        exit 1
      fi
  - name: Download pipeline analysis
    uses: actions/download-artifact@v8
    with:
      name: pipeline-analysis
      path: ${{ github.workspace }}
      run-id: ${{ github.event.inputs.analysis_run_id }}
      github-token: ${{ github.token }}
  - name: Verify pipeline analysis
    shell: bash
    env:
      ANALYSIS_RUN_ID: ${{ github.event.inputs.analysis_run_id }}
    run: |
      set -euo pipefail
      if [ ! -s "$GITHUB_WORKSPACE/pipeline-analysis.txt" ]; then
        echo "::error::Analysis run $ANALYSIS_RUN_ID did not provide a non-empty pipeline-analysis.txt artifact."
        exit 1
      fi
      sed 's/^::/ ::/' "$GITHUB_WORKSPACE/pipeline-analysis.txt"

tools:
  github:
    toolsets: [context, repos, pull_requests, actions]
  edit:
  # Read commands plus the artifact download and the repo's own check runner, so the agent can
  # both diagnose and verify a formatting/lint fix before proposing it.
  bash:
    - "cat"
    - "ls"
    - "head"
    - "tail"
    - "wc"
    - "find"
    - "grep"
    - "git diff:*"
    - "git status:*"
    - "azsdk ci test-results:*"
    - "azpysdk:*"

safe-outputs:
  create-pull-request:
    title-prefix: "[pipeline-fix] "
    labels: [automated]
    draft: true
    max: 1
    # Signed replay cannot preserve the original PR commits when the temporary validation base
    # differs from the checked-out head. Push the complete branch directly instead.
    signed-commits: false
    # Carry routing metadata in a compiler-controlled prefix instead of relying on the agent to
    # reproduce it in the branch field.
    branch-prefix: "copilot-pipeline-fix/pr-${{ github.event.inputs.pr_number }}-${{ github.event.inputs.ci_head_sha }}/"
    # Validate against the original PR's base branch first. The validation workflow retargets to the
    # contributor's branch only after Azure DevOps CI proves the fix.
    base-branch: ${{ github.event.inputs.validation_base_ref }}
    # Keep generated branches under one prefix so the 7-day cleanup workflow can find them.
    allowed-branches:
      - "copilot-pipeline-fix/*"
    expires: 7
    if-no-changes: "ignore"
    fallback-as-issue: false
  noop:
    report-as-issue: false
  missing-tool:
    create-issue: false
  missing-data:
    create-issue: false
  report-incomplete:
    create-issue: false
  report-failure-as-issue: false

timeout-minutes: 30
concurrency: pipeline-analysis-auto-fix-${{ github.event.inputs.pr_number }}
---

# Pipeline Analysis - Auto Fix

You are the Azure SDK Tools **pipeline auto-fix** agent for `${{ github.repository }}`.

A CI pipeline failed on pull request **#${{ github.event.inputs.pr_number }}**. That PR's head
branch (`${{ github.event.inputs.pr_head_ref }}`) is checked out in your workspace, and the exact
analysis produced by next-steps run `${{ github.event.inputs.analysis_run_id }}` is available at
**`pipeline-analysis.txt`**.

Your job is to attempt a **narrow, high-confidence fix** and publish it as a draft pull request.
The PR initially targets `${{ github.event.inputs.validation_base_ref }}` so the full upstream PR
pipeline runs. A separate workflow retargets it to `${{ github.event.inputs.pr_head_ref }}` only
after CI validates the fix. You are not merging anything - the PR author decides.

## Step 0 - Read the analysis and decide whether to act

1. Read `pipeline-analysis.txt`.
2. If it is empty, contains `No failed Azure Pipeline builds found`, or shows no real failure, use
   the `noop` safe output and stop.
3. Stale-commit guard: if `${{ github.event.inputs.ci_head_sha }}` is non-empty, compare it with
   the PR's current head SHA. If they differ, the run is for a superseded commit - `noop` and stop.
4. **Only proceed if the failure is deterministically fixable from the repository itself** -
   formatting, linting, a changelog or README validation error, a spelling failure, a missing
   import, a stale snippet. If the failure is a flaky test, an infrastructure/auth error, a live
   test, or anything whose root cause you cannot see in the code, use `noop` and stop. A wrong fix
   is worse than none.

## Step 1 - Understand the failure

Consult the repository's skills before changing anything. **Read every `SKILL.md` with the `view`
tool, not with `cat`** - the Copilot `PostToolUse` telemetry hook only recognizes skill invocations
from the `view`/`read_file` tools, so a shell read is not counted.

- Read `.github/skills/azsdk-common-pipeline-analysis/SKILL.md` and its
  `references/failure-patterns.md` for the failure categories and pattern-to-fix mappings.
- If a skill under `.github/skills/` describes how to fix this specific failure, read its
  `SKILL.md` with `view` and follow it.
- If `pipeline-analysis.txt` only names artifacts and you need their contents, run:
  `azsdk ci test-results "https://github.com/${{ github.repository }}/pull/${{ github.event.inputs.pr_number }}"`
- If `${{ github.repository }}` is `Azure/azure-rest-api-specs`, also read
  `documentation/ci-fix.md` and prefer its documented local commands. It does not exist in other
  repositories - skip it there.

## Step 2 - Make the smallest fix that addresses the reported failure

- Change only what the failure requires. Do not reformat unrelated files, bump versions, or
  refactor.
- Never modify CI configuration, pipeline YAML, or `eng/` tooling to make a check pass.
- Where the repo offers a deterministic fixer, prefer it over hand-editing (for example
  `azpysdk black <target>` for Python formatting).
- Verify your change where you cheaply can (re-run the same lint/format command) and say in the PR
  body exactly what you ran and what it reported. If you could not verify locally, say that
  plainly instead of implying it is proven.

## Step 3 - Publish the fix

Emit exactly one `create-pull-request` safe output.

- Use `fix` as the source branch name. The safe-output handler prepends the immutable
  `copilot-pipeline-fix/pr-${{ github.event.inputs.pr_number }}-${{ github.event.inputs.ci_head_sha }}/`
  routing prefix and may append a uniqueness suffix.
- Title: a one-line summary of the fix.
- Body must contain:
  - which pipeline check failed, with the Azure DevOps build link from the analysis;
  - the root cause in one or two sentences;
  - what you changed and why it addresses that specific failure;
  - what you ran to verify, or an explicit statement that it is unverified;
  - a closing note that the PR temporarily targets `${{ github.event.inputs.validation_base_ref }}`
    for CI validation, must not be merged there, and will be retargeted automatically to
    `${{ github.event.inputs.pr_head_ref }}` if validation passes.

## Constraints (non-negotiable)

1. **One draft PR, initially targeting the validation branch.** Never push directly to
   `${{ github.event.inputs.pr_head_ref }}`. The validation workflow, not the agent, retargets the
   PR after CI passes.
2. **No speculative fixes.** If you are not confident the change addresses the reported failure,
   `noop`. Silence is an acceptable outcome; a plausible-looking wrong patch is not.
3. **Ground every claim in `pipeline-analysis.txt` or in output you actually produced.** Do not
   assert that a check now passes unless you ran it and saw it pass.
4. **Do not touch** CI/pipeline definitions, `eng/`, secrets, or dependency lock files to force a
   check green.
5. Do not use `gh` or GitHub write APIs directly - publishing happens only through the
   `create-pull-request` safe output.
