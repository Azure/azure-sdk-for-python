---
description: Analyze failed Azure SDK pull-request pipelines.
on:
  check_suite:
    types: [completed]
  permissions:
    checks: read
  steps:
    - name: Check whether analysis should run
      id: analysis_gate
      uses: actions/github-script@v9.0.0
      with:
        script: |
          const suite = context.payload.check_suite;
          core.setOutput("run_analysis", "false");
          if (suite.app?.slug !== "azure-pipelines" || !suite.pull_requests.length) {
            core.info("Skipping analysis because this is not an Azure Pipelines suite for a pull request.");
            return;
          }
          const suites = await github.paginate(github.rest.checks.listSuitesForRef, {
            ...context.repo,
            ref: suite.head_sha,
          });
          const pipelineSuites = suites.filter(candidate => candidate.app?.slug === "azure-pipelines");
          if (!pipelineSuites.length || pipelineSuites.some(candidate => candidate.status !== "completed")) {
            core.info("Skipping analysis until all Azure Pipelines suites are completed.");
            return;
          }
          if (!pipelineSuites.some(candidate => candidate.conclusion === "failure")) {
            core.info("Skipping analysis because no Azure Pipelines suites failed.");
            return;
          }
          const prNumbers = [...new Set(suite.pull_requests.map(pull => pull.number))];
          const pulls = await Promise.all(prNumbers.map(async pullNumber => {
            const { data: pull } = await github.rest.pulls.get({
              ...context.repo,
              pull_number: pullNumber,
            });
            return pull;
          }));
          const matchingPulls = pulls.filter(
            pull => pull.state === "open" && pull.head.sha === suite.head_sha
          );
          if (matchingPulls.length !== 1) {
            core.info(
              `Skipping analysis because ${matchingPulls.length} open pull requests point to ${suite.head_sha}; expected exactly one.`
            );
            return;
          }
          const pull = matchingPulls[0];
          const prNumber = pull.number;
          core.setOutput("run_analysis", "true");
          core.setOutput("pr_number", String(prNumber));
          core.setOutput("head_sha", suite.head_sha);
          core.setOutput(
            "auto_fix_supported",
            String(pull.head.repo?.full_name === `${context.repo.owner}/${context.repo.repo}`)
          );

if: needs.pre_activation.outputs.run_analysis == 'true'

concurrency:
  group: "pipeline-analysis-next-steps-${{ github.event.check_suite.head_sha }}"
  cancel-in-progress: true

permissions:
  actions: read
  checks: read
  contents: read
  copilot-requests: write
  pull-requests: read

checkout:
  sparse-checkout: |
    eng
    .github/skills

network:
  allowed:
    - defaults
    - github
    - dev.azure.com
    - aka.ms
    - containers

pre-agent-steps:
  - name: Install Azure SDK MCP server
    shell: pwsh
    run: |
      $installDirectory = Join-Path $HOME "bin"
      ./eng/common/mcp/azure-sdk-mcp.ps1 -InstallDirectory $installDirectory

      $mcpDirectory = Join-Path $env:RUNNER_TEMP "azsdk-mcp"
      New-Item -ItemType Directory -Path $mcpDirectory -Force | Out-Null
      $mcpExecutable = Join-Path $mcpDirectory "azsdk"
      Copy-Item (Join-Path $installDirectory "azsdk") $mcpExecutable
      chmod +x $mcpExecutable
      if ($LASTEXITCODE) {
        throw "Failed to mark the Azure SDK MCP executable."
      }

tools:
  github:
    toolsets: [pull_requests]

mcp-servers:
  azure-sdk-mcp:
    type: stdio
    container: "mcr.microsoft.com/dotnet/runtime-deps:8.0-noble"
    args:
      - "-v"
      - "${RUNNER_TEMP}/azsdk-mcp/azsdk:/usr/local/bin/azsdk:ro"
    entrypoint: "/usr/local/bin/azsdk"
    entrypointArgs: ["mcp"]
    env:
      GH_TOKEN: "${{ github.token }}"
      GITHUB_TOKEN: "${{ github.token }}"
    allowed:
      - azsdk_analyze_pipeline
      - azsdk_get_failed_test_run_data
      - azsdk_get_failed_test_case_data

jobs:
  pre-activation:
    outputs:
      run_analysis: ${{ steps.analysis_gate.outputs.run_analysis }}
      pr_number: ${{ steps.analysis_gate.outputs.pr_number }}
      head_sha: ${{ steps.analysis_gate.outputs.head_sha }}
      auto_fix_supported: ${{ steps.analysis_gate.outputs.auto_fix_supported }}

safe-outputs:
  noop:
    report-as-issue: false
  add-comment:
    max: 1
    target: ${{ needs.pre_activation.outputs.pr_number }}
    hide-older-comments: true
  dispatch-workflow:
    workflows:
      - pipeline-analysis-auto-fix
    max: 1
  jobs:
    publish-analysis:
      description: Publish the pipeline analysis and its fixability classification
      runs-on: ubuntu-latest
      needs: safe_outputs
      inputs:
        fixability:
          type: choice
          options: [fixable, non-fixable]
          required: true
        analysis:
          type: string
          required: true
      steps:
        - name: Read analysis
          uses: actions/github-script@v9.0.0
          with:
            script: |
              const fs = require("fs");
              const output = JSON.parse(fs.readFileSync(process.env.GH_AW_AGENT_OUTPUT, "utf8"));
              const item = output.items.find(item => item.type === "publish_analysis");
              if (!item) {
                core.setFailed("No pipeline analysis was produced.");
                return;
              }
---

# Pipeline Analysis Next Steps

## Process

1. Retrieve pull request `${{ needs.pre_activation.outputs.pr_number }}`. If it is not
  open or its current head is not `${{ needs.pre_activation.outputs.head_sha }}`, call `noop` and stop.
2. Read `.github/skills/azsdk-common-pipeline-analysis/SKILL.md` and its
  `references/failure-patterns.md`, then follow their diagnosis guidance.
3. Call `azsdk_analyze_pipeline` with
  `pipelineIdentifier: "https://github.com/${{ github.repository }}/pull/${{ needs.pre_activation.outputs.pr_number }}"`.
4. Inspect every `failed_pipeline_tests` entry returned by the analysis. If an
  `artifact_file_path` is present, call `azsdk_get_failed_test_run_data` exactly once per unique
  artifact with `failedTestRunsPath` set to that path. Call `azsdk_get_failed_test_case_data` only
  when one exact `testCaseTitle` needs targeted follow-up. Never diagnose or classify fixability
  from test titles alone.
5. Group evidence by build, platform, artifact file, and failed test. Preserve platform-specific
  failures when titles overlap, but consolidate failures with one demonstrated root cause.
6. Categorize the failures and determine whether any are fixable by an automated code change.
  Automated fixing is supported only when `${{ needs.pre_activation.outputs.auto_fix_supported }}`
  is `true`. For a fork-owned source branch, still diagnose the failure, but classify the analysis
  as `non-fixable` and explain that this workflow cannot safely create a fix targeting the
  contributor's branch.

## Comment format

````markdown
<details>
<summary><strong>[Pilot] PR Pipeline Failure Analysis</strong></summary>

### What failed
<failed pipeline, stage, job, or tests; include Azure DevOps links>

<details>
<summary>Relevant pipeline output</summary>

```text
<short relevant excerpt; replace any triple backticks in the source>
```

</details>

### Recommended next steps
- <specific action supported by the failure data>
- See https://aka.ms/ci-fix

</details>

<for fixable failures only:>
**Automated fix:** [requested from this analysis run](https://github.com/${{ github.repository }}/actions/runs/${{ github.run_id }})

<!-- pipeline-auto-fix-authorized -->

<for non-fixable failures only:>
> Copilot detected the failing pipeline and generated the analysis above. To have it attempt a
> fix automatically, reply with `@copilot please fix the failing pipeline on this PR`.
````

For infrastructure or authentication failures, explain the failure under `What failed`. If an
Azure DevOps pipeline is internal or private and cannot be accessed by the workflow, state under
`Recommended next steps` that the workflow does not have the user's Azure DevOps identity and that
they can analyze the pipeline by running this command locally while authenticated to Azure DevOps:

```bash
azsdk azp analyze https://github.com/${{ github.repository }}/pull/${{ needs.pre_activation.outputs.pr_number }}
```

## Publish

- Retrieve the pull request again. If it is not open or its current head is not `${{ needs.pre_activation.outputs.head_sha }}`, call `noop` and stop without commenting or dispatching.
- Call `publish_analysis` exactly once with the complete analysis and `fixable` if any failure is fixable; otherwise use `non-fixable`.
- Call `add_comment` exactly once with item number `${{ needs.pre_activation.outputs.pr_number }}` and the same complete analysis.
- Keep the fix section after the outer `</details>` so it is outside the collapsible analysis.
- For `fixable`, use the exact requested-status line and hidden authorization marker from the
  comment format, then call `dispatch_workflow` exactly once with this structure:
  `workflow_name: "pipeline-analysis-auto-fix"` and `inputs: { "pr_number": "${{ needs.pre_activation.outputs.pr_number }}", "ci_head_sha": "${{ needs.pre_activation.outputs.head_sha }}", "parent_run_id": "${{ github.run_id }}" }`. Do not place the workflow inputs at the top level.
- Never publish `fixable` or call `dispatch_workflow` when
  `${{ needs.pre_activation.outputs.auto_fix_supported }}` is not `true`.