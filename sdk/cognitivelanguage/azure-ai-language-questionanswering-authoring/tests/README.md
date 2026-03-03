# Question Answering Authoring Tests

This folder contains live tests for the Question Answering Authoring client.

## Test strategy

These tests use a **session-scoped unique project** created in `conftest.py`:

- Create a unique project name per session
- Run authoring operations (create/deploy/import/export/update)
- Delete the project in teardown (best-effort cleanup)

This keeps tests isolated and reduces flakiness from shared state.

## Live / playback behavior

Set the following environment variables before running live tests:

- `AZURE_TEST_RUN_LIVE=true`
- `AZURE_QUESTIONANSWERING_ENDPOINT`
- `AZURE_QUESTIONANSWERING_KEY`
- `AZURE_QUESTIONANSWERING_PROJECT` (used as project name prefix)

If `AZURE_TEST_RUN_LIVE` is not `true`, live-only tests are skipped.

When `AZURE_TEST_RUN_LIVE=false`, tests run in playback mode using sanitized environment values and recorded interactions.

## Install dev dependencies

Run from package directory:

```powershell
cd sdk/cognitivelanguage/azure-ai-language-questionanswering-authoring
pip install -r dev_requirements.txt
```

## Run tests

```powershell
pytest tests
```

Run a single test example:

```powershell
pytest -q tests/test_update_knowledge_sources.py::TestSourcesQnasSynonyms::test_add_qna_with_explicitlytaggedheading -q
```
