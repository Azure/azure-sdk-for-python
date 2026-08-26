---
name: azure-ai-projects-author-samples
description: 'Create or update idiomatic azure-ai-projects Python samples for newly emitted or merged API changes. WHEN: author azure-ai-projects samples; update azure-ai-projects samples after TypeSpec emission; add azure-ai-projects feature samples; fix azure-ai-projects samples after API changes. DO NOT USE FOR: other packages; Test Proxy recording. INVOKES: git, azpysdk, Python validation commands.'
---

# Author samples for azure-ai-projects API changes

Run from `sdk\ai\azure-ai-projects`. This workflow handles both uncommitted emission output and already-merged changes.

## 1. Establish the API delta

Regenerate `api.md` with `azpysdk apistub .`. Choose the comparison base explicitly:

```powershell
# Uncommitted emission/customization changes
git diff HEAD -- api.md azure\ai\projects

# Committed or merged changes
git diff <base-ref>...HEAD -- api.md azure\ai\projects
```

Use [prompts\diff-api-surface.prompt.md](prompts/diff-api-surface.prompt.md) to classify additions, signature changes, renames, and removals. Do not use the latest release as the base when the requested scope is a particular emission or merge.

## 2. Map changes to existing coverage

Search `samples\` and `tests\` for every affected public symbol. Update all stale call sites for renames, removals, and changed parameters. Add a new sample only for a meaningful end-to-end workflow, not for every new model or overload.

Bucket work beside the closest existing feature. Read the neighboring sync/async pair before editing; see [references\sample-conventions.md](references/sample-conventions.md).

## 3. Author or update samples

- Keep sync and async samples behaviorally equivalent when both clients expose the feature.
- Start new files from [templates\sample-skeleton.py](templates/sample-skeleton.py) and [templates\sample-skeleton_async.py](templates/sample-skeleton_async.py), then replace every placeholder.
- Use only public imports and the final customized API surface from `api.md`; never import generated internals.
- Make the workflow runnable against a real Foundry project, narrate useful results, and clean up created resources in `finally` where failure could leak them.
- Preserve nearby sample voice, environment-variable names, authentication style, and preview wording. Python samples already cover beta APIs, so do not exclude a feature merely because it is under `.beta`.

## 4. Keep recorded sample tests green

Check `tests\samples\test_samples.py` and `test_samples_async.py`. Existing folders are often auto-discovered by `get_sample_paths` or `get_async_sample_paths`; when no recording exists, add each new filename to that test's `samples_to_skip` with a concrete recording-needed reason. For a new sample folder, add matching sync/async harness coverage but keep the new cases excluded until recordings are supplied.

Do not create recordings or modify `assets.json`.

## 5. Validate

Run targeted syntax and formatting checks for every edited sample, then package checks:

```powershell
python -m compileall -q <edited-sample-paths>
python -m black --check <edited-sample-paths>
azpysdk pylint .
azpysdk mypy .
```

Fix source problems; do not weaken lint or type-check settings. Do not run samples live unless the user explicitly requests it.

## 6. Hand off

Run `azure-ai-projects-author-tests` for affected behavior, then `azure-ai-projects-update-changelog`.
