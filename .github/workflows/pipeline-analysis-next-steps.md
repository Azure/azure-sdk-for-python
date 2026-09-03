---
# This workflow is triggered for every eligible completed check suite and filters
# unrelated suites during pre-activation, adding noise to GitHub Actions.
# The long-term plan is to handle these checks through our GitHub App webhook.

description: Analyze failed Azure SDK pull-request pipelines.
on:
  check_suite:
    types: [completed]
  permissions:
    checks: read
    pull-requests: read
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
          const repositoryName = `${context.repo.owner}/${context.repo.repo}`;
          const repositoryId = context.payload.repository.id;
          const prNumbers = [...new Set(
            suite.pull_requests
              .filter(candidate => candidate.base?.repo?.id === repositoryId)
              .map(candidate => candidate.number)
          )];
          const pulls = (await Promise.all(prNumbers.map(async pullNumber => {
            try {
              const { data: pull } = await github.rest.pulls.get({
                ...context.repo,
                pull_number: pullNumber,
              });
              return pull;
            } catch (error) {
              if (error.status === 404) {
                core.info(`Ignoring pull request ${pullNumber} because it no longer exists.`);
                return null;
              }
              throw error;
            }
          }))).filter(Boolean);
          const matchingPulls = pulls.filter(
            pull => pull.state === "open" && pull.head.sha === suite.head_sha
          );
          if (matchingPulls.length !== 1) {
            core.info(
              `Skipping analysis because ${matchingPulls.length} open pull requests in ${repositoryName} point to ${suite.head_sha}; expected exactly one.`
            );
            return;
          }
          const pull = matchingPulls[0];
          if (pull.head.ref.startsWith("pipeline-fix/")) {
            core.info("Skipping analysis for an automatically generated pipeline fix pull request.");
            return;
          }
          if (pull.head.repo?.full_name !== `${context.repo.owner}/${context.repo.repo}`) {
            core.info("Skipping analysis because external fork-owned pull request branches are not supported.");
            return;
          }
          const prNumber = pull.number;
          core.setOutput("run_analysis", "true");
          core.setOutput("pr_number", String(prNumber));
          core.setOutput("head_sha", suite.head_sha);

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

pre-agent-steps:
  - name: Install Azure SDK CLI
    shell: pwsh
    run: |
      $installDirectory = Join-Path $env:RUNNER_TEMP "azsdk-cli"
      ./eng/common/mcp/azure-sdk-mcp.ps1 -InstallDirectory $installDirectory
      Add-Content -Path $env:GITHUB_PATH -Value $installDirectory
  - name: Analyze failing pipeline
    uses: actions/github-script@v9.0.0
    env:
      GITHUB_TOKEN: ${{ github.token }}
      REPOSITORY: ${{ github.repository }}
    with:
      script: |
        const fs = require("fs");
        const path = require("path");

        const logFile = (heading, contents) => {
          core.info(`----- ${heading} -----`);
          for (const line of contents.split(/\r?\n/)) {
            console.log(line.startsWith("::") ? ` ${line}` : line);
          }
        };
        const collectArtifactPaths = (value, paths = new Set()) => {
          if (Array.isArray(value)) {
            for (const child of value) {
              collectArtifactPaths(child, paths);
            }
          } else if (value && typeof value === "object") {
            if (value.artifact_file_path) {
              paths.add(value.artifact_file_path);
            }
            for (const child of Object.values(value)) {
              collectArtifactPaths(child, paths);
            }
          }
          return paths;
        };
        const runAzsdk = async args => {
          const result = await exec.getExecOutput("azsdk", args, {
            ignoreReturnCode: true,
            silent: true,
          });
          return {
            exitCode: result.exitCode,
            output: `${result.stdout}${result.stderr}`,
          };
        };

        const suite = context.payload.check_suite;
        const repositoryId = context.payload.repository.id;
        const prNumbers = [...new Set(
          suite.pull_requests
            .filter(candidate => candidate.base?.repo?.id === repositoryId)
            .map(candidate => candidate.number)
        )];
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
          core.setFailed(
            `Expected exactly one open pull request in ${context.repo.owner}/${context.repo.repo} at ${suite.head_sha}; found ${matchingPulls.length}.`
          );
          return;
        }

        const prUrl = `https://github.com/${process.env.REPOSITORY}/pull/${matchingPulls[0].number}`;
        const analysisFile = path.join(process.env.GITHUB_WORKSPACE, "pipeline-analysis.json");
        const testResultsFile = path.join(process.env.GITHUB_WORKSPACE, "pipeline-test-results.txt");
        const analysis = await runAzsdk(["ci", "analyze", prUrl, "--output", "json"]);
        fs.writeFileSync(analysisFile, analysis.output);

        core.info(`azsdk ci analyze exit code: ${analysis.exitCode}`);
        logFile("pipeline-analysis.json", analysis.output);
        if (analysis.exitCode !== 0) {
          if (analysis.output.includes("No failed Azure Pipeline builds found")) {
            core.info("No failing Azure Pipeline builds resolved for this PR; the agent will no-op.");
            fs.writeFileSync(testResultsFile, "");
            return;
          }
          core.setFailed(`azsdk ci analyze failed (exit ${analysis.exitCode}) with an unexpected error.`);
          return;
        }

        let artifactFiles;
        try {
          artifactFiles = [...collectArtifactPaths(JSON.parse(analysis.output))].sort();
        } catch (error) {
          core.setFailed(`Failed to parse artifact paths from the pipeline analysis: ${error.message}`);
          return;
        }

        let testResults = "";
        for (const artifactFile of artifactFiles) {
          testResults += `===== ${artifactFile} =====\n`;
          // With neither --titles nor --filter-title, this dispatches to the same
          // GetFailedTestResults method as azsdk_get_failed_test_run_data.
          const result = await runAzsdk([
            "pkg", "test", "results",
            "--test-results-file", artifactFile,
            "--output", "json",
          ]);
          testResults += result.output;
          if (result.exitCode !== 0) {
            fs.writeFileSync(testResultsFile, testResults);
            core.setFailed(
              `azsdk pkg test results failed for an analysis artifact (exit ${result.exitCode}).`
            );
            return;
          }
        }
        fs.writeFileSync(testResultsFile, testResults);
        logFile("pipeline-test-results.txt", testResults);

tools:
  github:
    toolsets: [pull_requests]
  bash: ["cat", "head", "tail", "wc"]

jobs:
  pre-activation:
    outputs:
      run_analysis: ${{ steps.analysis_gate.outputs.run_analysis }}
      pr_number: ${{ steps.analysis_gate.outputs.pr_number }}
      head_sha: ${{ steps.analysis_gate.outputs.head_sha }}
  safe_outputs:
    permissions:
      pull-requests: read
    pre-steps:
      - name: Resolve trusted comment target
        id: comment_target
        uses: actions/github-script@v9.0.0
        with:
          script: |
            const suite = context.payload.check_suite;
            const repositoryId = context.payload.repository.id;
            const prNumbers = [...new Set(
              suite.pull_requests
                .filter(candidate => candidate.base?.repo?.id === repositoryId)
                .map(candidate => candidate.number)
            )];
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
              core.setFailed(
                `Expected exactly one open pull request in ${context.repo.owner}/${context.repo.repo} at ${suite.head_sha}; found ${matchingPulls.length}.`
              );
              return;
            }
            core.setOutput("pr_number", String(matchingPulls[0].number));

safe-outputs:
  report-failed-jobs: false
  report-failure-as-issue: false
  report-incomplete: false
  missing-tool: false
  missing-data: false
  noop:
    report-as-issue: false
  add-comment:
    max: 1
    target: ${{ steps.comment_target.outputs.pr_number }}
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

1. If the workflow cannot proceed, including because required data or a required tool is
  unavailable, call `noop` and stop. Do not report an expected early exit as a workflow failure.
  Use `noop`, not `missing_tool`, `missing_data`, or `report_incomplete`, for these paths.
  Retrieve pull request `${{ needs.pre_activation.outputs.pr_number }}`. If it is not open or its
  current head is not `${{ needs.pre_activation.outputs.head_sha }}`, call `noop` and stop.
2. Read `.github/skills/azsdk-common-pipeline-analysis/SKILL.md` and its
  `references/failure-patterns.md`, then follow their diagnosis guidance. The deterministic setup
  has already run the CLI analysis, so do not follow the skill's MCP invocation requirement.
3. Inspect `.github/skills` for repository- or language-specific skills
  useful for analyzing the
  failure, and read their `SKILL.md` files before diagnosing it.
4. Read `pipeline-analysis.json`, which contains the complete JSON output from `azsdk ci analyze`.
  If it contains `No failed Azure Pipeline builds found` or no real failures, call `noop` and stop.
5. Read `pipeline-test-results.txt`, which contains full failed-test details for every unique
  `artifact_file_path` returned by the analysis. The CLI invocation uses the same
  `GetFailedTestResults` implementation as `azsdk_get_failed_test_run_data`. The exact-case MCP
  tool only performs a case-insensitive title selection over this same full result set, so select
  an exact case from this file when targeted follow-up is needed. Never diagnose or classify
  fixability from test titles alone.
6. Group evidence by build, platform, artifact file, and failed test. Preserve platform-specific
  failures when titles overlap, but consolidate failures with one demonstrated root cause.
7. Categorize the failures and determine whether any are fixable by an automated code change.

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
**Automated fix:** Requested

<for non-fixable failures only:>
> Copilot detected the failing pipeline and generated the analysis above. To have it attempt a
> fix automatically, reply with `@copilot please fix the failing pipeline on this PR`.
````

For infrastructure or authentication failures, explain the failure under `What failed`. If an
Azure DevOps pipeline is internal or private and cannot be accessed by the workflow, state under
`Recommended next steps` that the workflow does not have the user's Azure DevOps identity and that
they can analyze the pipeline by running this command locally while authenticated to Azure DevOps:

```bash
azsdk ci analyze https://github.com/${{ github.repository }}/pull/${{ needs.pre_activation.outputs.pr_number }} --output json
```

## Publish

- Retrieve the pull request again. If it is not open or its current head is not `${{ needs.pre_activation.outputs.head_sha }}`, call `noop` and stop without commenting or dispatching.
- Call `publish_analysis` exactly once with the complete analysis and `fixable` if any failure is fixable; otherwise use `non-fixable`.
- Call `add_comment` exactly once with item number `${{ needs.pre_activation.outputs.pr_number }}` and the same complete analysis.
- Keep the fix section after the outer `</details>` so it is outside the collapsible analysis.
- For `fixable`, use the exact requested-status line from the comment format, then call
  `dispatch_workflow` exactly once with this structure:
  `workflow_name: "pipeline-analysis-auto-fix"` and `inputs: { "pr_number": "${{ needs.pre_activation.outputs.pr_number }}", "ci_head_sha": "${{ needs.pre_activation.outputs.head_sha }}", "parent_run_id": "${{ github.run_id }}" }`. Do not place the workflow inputs at the top level.