# Question Answering (Inference) Tests

This folder contains live tests for the Question Answering Inference client.

## Test strategy

These tests use a **session-scoped seeded project** created during test setup:

- Create a unique project name per test session
- Seed deterministic QnA records using the Authoring client
- Deploy the project for query tests
- Delete the project in teardown (best-effort cleanup)

This avoids cross-run project pollution and removes dependency on pre-existing shared projects.

## Live test requirements

Set the following environment variables before running live tests:

- `AZURE_TEST_RUN_LIVE=true`
- `AZURE_QUESTIONANSWERING_ENDPOINT`
- `AZURE_QUESTIONANSWERING_KEY`
- `AZURE_QUESTIONANSWERING_PROJECT` (used as project name prefix)

If `AZURE_TEST_RUN_LIVE` is not `true`, seeding-dependent tests are skipped.

## Install dev dependencies

Run from package directory:

```powershell
cd sdk/cognitivelanguage/azure-ai-language-questionanswering
pip install -r dev_requirements.txt
```

## Run tests

```powershell
pytest tests
```

Quick collection check:

```powershell
pytest -q tests --collect-only
```
