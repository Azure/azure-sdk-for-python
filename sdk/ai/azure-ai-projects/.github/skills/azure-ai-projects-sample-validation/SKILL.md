---
name: azure-ai-projects-sample-validation
description: 'Validate one or more azure-ai-projects Python samples by recording, playback, local live test, or Azure DevOps live test. WHEN: validate sample, wildcard sample search, record samples, rerecord samples, playback samples, live test locally, live test in ADO pipeline. Resolves recorded-sample pytest nodes and supports repeatable NAME=VALUE overrides. DO NOT USE FOR: authoring samples/tests; non-sample tests; other packages.'
argument-hint: 'Sample path or wildcard; optional pytest-node wildcard and NAME=VALUE overrides'
---

# Record and verify an azure-ai-projects sample

Run from `sdk\ai\azure-ai-projects`. This workflow may modify Test Proxy recordings. Never commit `.env`, credentials, access tokens, API keys, or unsanitized resource identifiers.

## Execution modes

Before previewing, always use the question tool to ask the user to choose exactly one mode. Do this even when the request appears to imply a mode; never infer or default it.

| Mode | `AZURE_TEST_RUN_LIVE` | `AZURE_SKIP_LIVE_RECORDING` | Behavior |
| --- | --- | --- | --- |
| `record-and-playback` | `true`, then `false` | `false`, then `true` | Record, then verify playback even if recording fails. |
| `record-only` | `true` | `false` | Record without running playback. |
| `playback-only` | `false` | `true` | Run only from an existing recording. |
| `live-test-locally` | `true` | `true` | Contact the live service locally without creating or updating a recording. |
| `live-test-by-pipeline` | `true` | `true` | Queue ADO definition `8392`, run selected nodes live without recording, and wait for completion. |

Do not silently substitute one mode for another. Include the selected mode in the final report.

## 1. Preview the plan

Run the orchestrator without `-Run`:

```powershell
.\.github\skills\azure-ai-projects-sample-validation\scripts\InvokeSampleValidation.ps1 `
   -SamplePattern "samples\hosted_agents\sample_*.py" `
   -TestPattern "*from_image*" `
   -Mode "<mode>"
```

It deterministically resolves the collected pytest node, scans required sample variables, detects selected `AdditionalSampleTestDetail` values and LLM validation, reads effective `.env` assignments, maps supported pytest options, selects mode flags, and prints a plan. The plan includes the resolved sample path, pytest node, and effective environment variables as `key=value` entries. Pytest command previews remain redacted. Treat the preview as sensitive and do not paste it into reports or source files.

For wildcard selections, the same plan includes every matching sample path and pytest node.

`-SamplePattern` supports exact paths/names and PowerShell wildcards; `samples/**/*.py` selects the complete recorded-sample harness. Optional `-TestPattern` filters pytest node IDs. Every match runs in every mode. Add repeatable `-EnvironmentVariable "NAME=VALUE"` overrides; they take precedence over `.env`.

The manual ADO form combines both selectors into one required `Selection` parameter using `sample pattern | test pattern` syntax. For example, `samples\hosted_agents\sample_*.py | *` runs every hosted-agent node, while `samples\hosted_agents\sample_*.py | *remote_build*` filters those nodes. The queue script creates this combined value automatically.

If a required name is missing or empty, report the name and remind the user to check `.env`; do not invent a value.

Lower-level scripts under `scripts\` are for diagnosing the orchestrator only. Do not repeat their work manually during a normal run.

## 2. Obtain approval

For `record-and-playback`, `record-only`, and `live-test-locally`, use the question tool to ask for input confirmation immediately before execution:

`live-test-by-pipeline` uses the same input confirmation and an ADO-specific action approval.

**Confirm inputs:** "Use sample `<resolved-sample-path>`, pytest node `<resolved-node-id>`, and the displayed `key=value` environment variables?"

For wildcard selections, substitute the full resolved sample and node lists.

Include the preview's environment entries plus missing and empty variable names in the question's supporting message. If the user does not confirm, update the requested sample, node, or `.env` as directed and rerun preview before asking again.

Also ask the action-specific approval in the same question-tool call:

- For `record-and-playback` and `record-only`: **Approve recording:** "Start recording now? It may update Test Proxy recordings."
- For `live-test-locally`: **Approve live test:** "Start the live test locally without recording now?"
- For `live-test-by-pipeline`: **Approve pipeline:** include organization/project, definition ID, and source branch; the branch must be pushed before queueing.

Do not run unless both input confirmation and action approval are `Yes`. `playback-only` needs neither confirmation.

## 3. Execute

Use the same sample, selected node, and mode from preview:

For wildcard validation, preserve the same sample pattern, test pattern, and environment overrides.

```powershell
# record-and-playback or record-only
.\.github\skills\azure-ai-projects-sample-validation\scripts\InvokeSampleValidation.ps1 `
   -SamplePattern "<pattern>" -TestPattern "<optional-pattern>" -Mode "<record-mode>" `
   -Run -ConfirmSelection -ConfirmRecording

# playback-only
.\.github\skills\azure-ai-projects-sample-validation\scripts\InvokeSampleValidation.ps1 `
   -SamplePattern "<pattern>" -TestPattern "<optional-pattern>" -Mode "playback-only" -Run

# live-test-locally
.\.github\skills\azure-ai-projects-sample-validation\scripts\InvokeSampleValidation.ps1 `
   -SamplePattern "<pattern>" -TestPattern "<optional-pattern>" -Mode "live-test-locally" `
   -Run -ConfirmSelection -ConfirmLive

# live-test-by-pipeline
.\.github\skills\azure-ai-projects-sample-validation\scripts\InvokeSampleValidation.ps1 `
   -SamplePattern "<pattern>" -TestPattern "<optional-pattern>" -Mode "live-test-by-pipeline" `
   -Run -ConfirmSelection -ConfirmPipeline
```

The orchestrator loads only relevant `.env` names and handles all mode flags. Immediately before recording, it stops `*testproxy*` processes and deletes `.pytest_cache`. `record-and-playback` proceeds to playback even when recording fails. After successful hosted-agent recordings it runs `tests\samples\repair_hosted_agent_sample_recording.py` for every selected hosted-agent node before playback or completion. ADO selectors use runtime parameters; values use masked secret build variables. Pipeline mode attaches separate Azure SDK API and `print()` output logs to each JUnit test result, publishes an unfiltered Markdown summary containing every test outcome, waits until ADO completes, and fails when the run fails or times out.

Recording modes invoke `scripts\TestRecordingGitConflicts.ps1` during preview and again immediately before cleanup. Treat that script's result as authoritative; do not reproduce its conflict checks in the skill workflow.

## 4. Diagnose only relevant failures

If playback fails, inspect only the selected node's mismatch and named recording. Make the smallest sanitizer or deterministic-input fix. Before another recording attempt, rerun preview and ask both recording questions again.

For multi-node selections, apply that rule independently to each selected failure.

Do not repair unrelated failures, edit recordings by hand, or fall back to bare pytest/VS Code playback. Never stage, commit, or push recordings unless explicitly requested.

## 5. Validate and report

Run `git diff --check` and `git status --short`. Report the selected mode and node; required, harness-supplied, missing, and empty names; recording, repair, playback, and live results; and changed recording paths. Report unselected steps as `not run`. Never claim `record-and-playback` success unless playback passed.

Also report sample/test patterns, selected sample/node counts, and the pipeline link when applicable. Do not repeat environment values in the final report.