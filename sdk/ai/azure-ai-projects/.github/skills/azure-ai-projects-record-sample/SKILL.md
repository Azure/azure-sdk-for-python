---
name: azure-ai-projects-record-sample
description: 'Record, play back, or run an azure-ai-projects Python sample live with the Test Proxy. WHEN: record sample, rerecord sample, record and playback, record only, playback only, live test locally, validate recording. Always prompts for an execution mode. Scans required environment variables and passes effective .env values as pytest command-line arguments. DO NOT USE FOR: authoring tests or samples; non-sample service tests; other packages.'
argument-hint: 'Sample path or node ID; choose mode when prompted'
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

Do not silently substitute one mode for another. Include the selected mode in the final report.

## 1. Preview the plan

Run the orchestrator without `-Run`:

```powershell
.\.github\skills\azure-ai-projects-record-sample\scripts\InvokeSampleTest.ps1 `
   -SamplePath "<sample-path-or-filename>" `
   -Mode "<mode>"
```

It deterministically resolves the collected pytest node, scans required sample variables, detects selected `AdditionalSampleTestDetail` values and LLM validation, reads effective `.env` assignments, maps supported pytest options, selects mode flags, and prints a plan. The plan includes the resolved sample path, pytest node, and effective environment variables as `key=value` entries. Pytest command previews remain redacted. Treat the preview as sensitive and do not paste it into reports or source files.

If multiple nodes execute the sample, the script lists them and stops. Ask the user which scenario to use, then rerun preview with `-NodeId "<node-id>"`. If a required name is missing or empty, report the name and remind the user to check `.env`; do not invent a value.

Lower-level scripts under `scripts\` are for diagnosing the orchestrator only. Do not repeat their work manually during a normal run.

## 2. Obtain approval

For `record-and-playback`, `record-only`, and `live-test-locally`, use the question tool to ask for input confirmation immediately before execution:

**Confirm inputs:** "Use sample `<resolved-sample-path>`, pytest node `<resolved-node-id>`, and the displayed `key=value` environment variables?"

Include the preview's environment entries plus missing and empty variable names in the question's supporting message. If the user does not confirm, update the requested sample, node, or `.env` as directed and rerun preview before asking again.

Also ask the action-specific approval in the same question-tool call:

- For `record-and-playback` and `record-only`: **Approve recording:** "Start recording now? It may update Test Proxy recordings."
- For `live-test-locally`: **Approve live test:** "Start the live test locally without recording now?"

Do not run unless both input confirmation and action approval are `Yes`. `playback-only` needs neither confirmation.

## 3. Execute

Use the same sample, selected node, and mode from preview:

```powershell
# record-and-playback or record-only
.\.github\skills\azure-ai-projects-record-sample\scripts\InvokeSampleTest.ps1 `
   -SamplePath "<sample>" -NodeId "<node-id>" -Mode "<mode>" `
   -Run -ConfirmSelection -ConfirmRecording

# playback-only
.\.github\skills\azure-ai-projects-record-sample\scripts\InvokeSampleTest.ps1 `
   -SamplePath "<sample>" -NodeId "<node-id>" -Mode "playback-only" -Run

# live-test-locally
.\.github\skills\azure-ai-projects-record-sample\scripts\InvokeSampleTest.ps1 `
   -SamplePath "<sample>" -NodeId "<node-id>" -Mode "live-test-locally" `
   -Run -ConfirmSelection -ConfirmLive
```

The orchestrator keeps values internal, loads only relevant `.env` names, and handles all mode flags. Immediately before recording, it stops `*testproxy*` processes and deletes `.pytest_cache`. `record-and-playback` proceeds to playback even when recording fails. After a successful hosted-agent recording it runs `tests\samples\repair_hosted_agent_sample_recording.py` before playback or completion.

Recording modes invoke `scripts\TestRecordingGitConflicts.ps1` during preview and again immediately before cleanup. Treat that script's result as authoritative; do not reproduce its conflict checks in the skill workflow.

## 4. Diagnose only relevant failures

If playback fails, inspect only the selected node's mismatch and named recording. Make the smallest sanitizer or deterministic-input fix. Before another recording attempt, rerun preview and ask both recording questions again.

Do not repair unrelated failures, edit recordings by hand, or fall back to bare pytest/VS Code playback. Never stage, commit, or push recordings unless explicitly requested.

## 5. Validate and report

Run `git diff --check` and `git status --short`. Report the selected mode, sample, and node; environment variable names used; required, harness-supplied, missing, and empty names; recording, repair, playback, and live results; and changed recording paths. Do not repeat environment values in the final report. Report unselected steps as `not run`. Never claim `record-and-playback` success unless playback passed.