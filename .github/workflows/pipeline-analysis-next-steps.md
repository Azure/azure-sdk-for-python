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
    shell: bash
    env:
      GITHUB_TOKEN: ${{ github.token }}
      REPOSITORY: ${{ github.repository }}
    run: |
      set -uo pipefail
      mapfile -t event_context < <(python3 - "$GITHUB_EVENT_PATH" "$REPOSITORY" <<'PY'
      import json
      import sys

      with open(sys.argv[1], encoding="utf-8") as event_file:
          event = json.load(event_file)
          suite = event["check_suite"]

      print(suite["head_sha"])
      repository = sys.argv[2]
      repository_id = event["repository"]["id"]
      numbers = {
          pull["number"]
          for pull in suite["pull_requests"]
          if pull.get("base", {}).get("repo", {}).get("id") == repository_id
      }
      for number in sorted(numbers):
          print(number)
      PY
      )
      head_sha="${event_context[0]}"
      matching_prs=()
      for pr_number in "${event_context[@]:1}"; do
        pull_json=$(gh api "repos/${REPOSITORY}/pulls/${pr_number}")
        read -r state pull_head_sha < <(python3 -c \
          'import json, sys; pull = json.load(sys.stdin); print(pull["state"], pull["head"]["sha"])' \
          <<< "$pull_json")
        if [[ "$state" == "open" && "$pull_head_sha" == "$head_sha" ]]; then
          matching_prs+=("$pr_number")
        fi
      done
      if [[ ${#matching_prs[@]} -ne 1 ]]; then
        echo "::error::Expected exactly one open pull request in ${REPOSITORY} at ${head_sha}; found ${#matching_prs[@]}."
        exit 1
      fi
      PR_URL="https://github.com/${REPOSITORY}/pull/${matching_prs[0]}"
      analysis_file="$GITHUB_WORKSPACE/pipeline-analysis.json"
      test_results_file="$GITHUB_WORKSPACE/pipeline-test-results.txt"
      exit_code=0
      azsdk ci analyze "$PR_URL" --output json > "$analysis_file" 2>&1 || exit_code=$?

      echo "azsdk ci analyze exit code: $exit_code"
      echo "----- pipeline-analysis.json -----"
      sed 's/^::/ ::/' "$analysis_file"
      if [ "$exit_code" -ne 0 ]; then
        if grep -qF "No failed Azure Pipeline builds found" "$analysis_file"; then
          echo "No failing Azure Pipeline builds resolved for this PR; the agent will no-op."
          : > "$test_results_file"
          exit 0
        fi
        echo "::error::azsdk ci analyze failed (exit $exit_code) with an unexpected error."
        exit "$exit_code"
      fi

      : > "$test_results_file"
      artifact_files=$(python3 - "$analysis_file" <<'PY'
      import json
      import sys

      def artifact_paths(value):
          if isinstance(value, dict):
              path = value.get("artifact_file_path")
              if path:
                  yield path
              for child in value.values():
                  yield from artifact_paths(child)
          elif isinstance(value, list):
              for child in value:
                  yield from artifact_paths(child)

      with open(sys.argv[1], encoding="utf-8") as analysis:
          print("\n".join(sorted(set(artifact_paths(json.load(analysis))))))
      PY
      ) || {
        echo "::error::Failed to parse artifact paths from the pipeline analysis."
        exit 1
      }
      while IFS= read -r artifact_file; do
        [ -n "$artifact_file" ] || continue
        printf '%s\n' "===== $artifact_file =====" >> "$test_results_file"
        test_exit_code=0
        # With neither --titles nor --filter-title, this dispatches to the same
        # GetFailedTestResults method as azsdk_get_failed_test_run_data.
        azsdk pkg test results --test-results-file "$artifact_file" --output json \
          >> "$test_results_file" 2>&1 || test_exit_code=$?
        if [ "$test_exit_code" -ne 0 ]; then
          echo "::error::azsdk pkg test results failed for an analysis artifact (exit $test_exit_code)."
          exit "$test_exit_code"
        fi
      done <<< "$artifact_files"

      echo "----- pipeline-test-results.txt -----"
      sed 's/^::/ ::/' "$test_results_file"

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

safe-outputs:
  noop:
    report-as-issue: false
  add-comment:
    max: 1
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
  `references/failure-patterns.md`, then follow their diagnosis guidance. The deterministic setup
  has already run the CLI analysis, so do not follow the skill's MCP invocation requirement.
3. Read `pipeline-analysis.json`, which contains the complete JSON output from `azsdk ci analyze`.
  If it contains `No failed Azure Pipeline builds found` or no real failures, call `noop` and stop.
4. Read `pipeline-test-results.txt`, which contains full failed-test details for every unique
  `artifact_file_path` returned by the analysis. The CLI invocation uses the same
  `GetFailedTestResults` implementation as `azsdk_get_failed_test_run_data`. The exact-case MCP
  tool only performs a case-insensitive title selection over this same full result set, so select
  an exact case from this file when targeted follow-up is needed. Never diagnose or classify
  fixability from test titles alone.
5. Group evidence by build, platform, artifact file, and failed test. Preserve platform-specific
  failures when titles overlap, but consolidate failures with one demonstrated root cause.
6. Categorize the failures and determine whether any are fixable by an automated code change.

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
**Automated fix:** In progress

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