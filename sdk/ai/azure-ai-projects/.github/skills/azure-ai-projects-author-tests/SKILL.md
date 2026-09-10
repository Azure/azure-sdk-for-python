---
name: azure-ai-projects-author-tests
description: 'Create or update idiomatic azure-ai-projects pytest coverage for newly emitted or merged API changes, keeping new service tests enabled so PR validation surfaces missing Test Proxy recordings. WHEN: author azure-ai-projects tests; update azure-ai-projects tests after TypeSpec emission; add azure-ai-projects feature tests; fix azure-ai-projects tests after API changes. DO NOT USE FOR: other packages; recording or rerecording tests. INVOKES: git, pytest collection, azpysdk, Python validation commands.'
---

# Author tests for azure-ai-projects API changes

Run from `sdk\ai\azure-ai-projects`. Consume the API-delta report from `azure-ai-projects-author-samples`, or recompute it with [..\azure-ai-projects-author-samples\prompts\diff-api-surface.prompt.md](../azure-ai-projects-author-samples/prompts/diff-api-surface.prompt.md).

## 1. Map the delta to tests

Search `tests\` for every affected symbol. Update existing tests and assertions for changed signatures, renames, and removals while preserving their current enabled/skipped state. Add new behavior coverage beside the closest feature tests; Python coverage includes both GA and beta APIs.

Prefer extending an existing sync/async pair. Read its fixtures, decorators, sanitizers, resource naming, assertions, and cleanup before writing code; see [references\test-conventions.md](references/test-conventions.md).

## 2. Write complete, enabled new coverage

Use [templates\test-skeleton.py](templates/test-skeleton.py) and [templates\test-skeleton_async.py](templates/test-skeleton_async.py) only as structural starting points. Replace every placeholder and write the actual service calls, assertions, and cleanup.

- Do not add `skip`, `skipif`, `xfail`, or any other disabling marker to newly created tests, even when Test Proxy recordings do not exist yet.
- Keep sync and async tests behaviorally equivalent when both APIs exist.
- Use `TestBase`, the narrowest existing preparer, `create_client`/`create_async_client`, and `recorded_by_proxy`/`recorded_by_proxy_async`.
- Add sanitized preparer values, function-scoped sanitizers, and files under `tests\test_data` only when the scenario requires them. Never place secrets or live resource identifiers in source.
- Use `RecordedTransport.HTTPX2` only when the path also calls an OpenAI/httpx client. Follow the package's passthrough-wrapper pattern when combining parametrization with recorded decorators.

Do not add recordings and do not modify `assets.json`. Every new test must import and collect successfully while remaining enabled.

## 3. Validate without running new tests live

```powershell
python -m compileall -q <edited-test-paths>
python -m black --check <edited-test-paths>
pytest --collect-only -q <edited-test-paths>
azpysdk pylint .
azpysdk mypy .
```

Run targeted playback for updated pre-existing tests only when recordings already exist. Do not run new service tests live. Leave newly created tests enabled so missing-recording errors surface in PR validation; direct the author to the SDK maintainer for help instead of adding a skip marker.

## 4. Hand off

Report which new tests were added and may need Test Proxy recordings. If PR validation fails for missing recordings, direct the author to the SDK maintainer for help. Then run `azure-ai-projects-update-changelog`.
