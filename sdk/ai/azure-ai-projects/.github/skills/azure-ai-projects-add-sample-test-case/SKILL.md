---
name: azure-ai-projects-add-sample-test-case
description: 'Register azure-ai-projects samples and synchronize required environment names using PowerShell. WHEN: add sample test case; register samples as tests; enable excluded sample tests; update sample environment template or servicePreparer sanitization. Checks test IDs, updates include/exclude lists, creates sync/async folder tests, and adds missing template entries and sanitized servicePreparer defaults. DO NOT USE FOR: authoring samples; recording tests; other packages.'
argument-hint: 'One or more sample paths, separated by spaces'
---

# Add sample test cases

1. Collect all requested sample paths. Accept package-relative paths, paths relative to `samples/`, absolute paths, or unique filenames. Do not infer additional samples or sync/async counterparts.
2. Run the [PowerShell script](./scripts/AddSampleTestCase.ps1) in preview mode, passing the paths as an array:

   ```powershell
   ./.github/skills/azure-ai-projects-add-sample-test-case/scripts/AddSampleTestCase.ps1 `
       -SamplePath @("samples/agents/sample_agent_basic.py", "samples/agents/sample_agent_basic_async.py")
   ```

    Use `-PackageRoot` when targeting a different checkout and `-PythonExecutable` for the configured interpreter. The bundled Python helpers use only the standard library; they parse source without importing tests, loading `.env`, or contacting services.
3. Review the full preview, including environment additions. The [local scanner copy](./scripts/GetSampleRequiredEnvironmentVariables.ps1) scans every selected sample, including already-registered ones. It recognizes literal required reads and bare `get`/`getenv` calls without defaults or `or` fallbacks; it does not follow imported helpers or dynamic names and can match comments. Keep this copy identical to the sample-validation skill's scanner until the scripts move to a shared location.
    Missing names are appended as blank `NAME=` entries to `.env.template`; missing lowercase keywords with deterministic sanitized playback values are added only to `servicePreparer` in `tests/test_base.py`. Existing entries, values, and other preparers are preserved. New `servicePreparer` keys become required by every live test using it, and custom preparers are not automatically extended.
    Review placeholder formats. Common project endpoints, connection ARM IDs, UUIDs, and numeric suffixes get structural defaults. `USER_INPUT` and names ending in `_USER_INPUT` get readable questions, such as `AI_SEARCH_USER_INPUT` → `What is ai search user input?`; other names get `sanitized-<name>`. For special formats or file paths use `-SanitizedValue @{ "NAME" = "fictional-playback-value" }` and rerun preview. This mapping must never contain live secrets and does not overwrite existing defaults.
    Present the preview and obtain explicit approval before rerunning the same command with `-Apply` and the same overrides. `-WhatIf` is also supported. Never apply after an input, parsing, or ambiguous-registration error.
4. Existing discovered IDs and active `AdditionalSampleTestDetail` variants are left alone. Missing samples are added to `samples_to_test` or removed from `samples_to_skip`, preserving existing preparers and other cases. A missing folder gets a new method in the sync/async harness with `servicePreparer`, recording decorators, and an explicit include list containing only the requested samples.
5. Validate changed Python files with syntax checks and `pytest --collect-only`; confirm the reported sample IDs collect, rerun preview to verify idempotency, then run `git diff --check`. Report registered/already-present samples, environment additions, and changed files. Do not execute samples, read or modify `.env`, overwrite existing preparer defaults, or create recordings. Hand off to `azure-ai-projects-sample-validation` when recording or execution is requested.