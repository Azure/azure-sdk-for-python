---
page_type: sample
languages:
   - python
products:
   - azure
   - azure-ai-language-service
name: Azure AI Language Question Answering Authoring Python samples
description: Code samples that demonstrate how to author (create, update, deploy, export/import) Question Answering projects using the azure-ai-language-questionanswering-authoring package.
---

# Azure AI Language Question Answering Authoring Samples

These samples show how to use the `azure-ai-language-questionanswering-authoring` client library to manage (author) Question Answering projects: create a project, update sources and QnA pairs, manage synonyms, deploy, and export/import assets. They complement runtime (query) samples found in the separate `azure-ai-language-questionanswering` package.

> NOTE: This library version is in preview; APIs and models may change before GA.

## Prerequisites

1. An Azure subscription.
2. An Azure AI Language resource with Question Answering enabled (custom subdomain endpoint recommended).
3. Python 3.9+.
4. Install the package:
    - Release: `pip install --pre azure-ai-language-questionanswering-authoring`
    - Dev/editable from repo root: `pip install -e .` (run inside the package directory)  
    Optional for AAD auth: `pip install azure-identity`

## Environment variables

Set the following (key auth shown below). If using AAD, set the identity environment variables (`AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_CLIENT_SECRET`) instead of the key.

| Variable | Required | Purpose |
|----------|----------|---------|
| `AZURE_QUESTIONANSWERING_ENDPOINT` | Yes | Your resource endpoint (`https://<name>.cognitiveservices.azure.com/`). |
| `AZURE_QUESTIONANSWERING_KEY` | Yes (for key auth) | API key for the resource. |
| `AZURE_QUESTIONANSWERING_PROJECT` | Optional* | Existing project name used by export/import samples; created if absent in some scenarios. |

Example (PowerShell):
```powershell
$env:AZURE_QUESTIONANSWERING_ENDPOINT="https://<your-resource>.cognitiveservices.azure.com/"
$env:AZURE_QUESTIONANSWERING_KEY="<api-key>"
$env:AZURE_QUESTIONANSWERING_PROJECT="myProject"
```

## Sample list

| File (sync) | Scenario | Key operations | Async equivalent |
|-------------|----------|----------------|------------------|
| `sample_create_and_deploy_project.py` | Create a project, add a knowledge source, deploy to `production` | `create_project`, `begin_update_sources`, `begin_deploy_project` | `async_samples/sample_create_and_deploy_project_async.py` |
| `sample_export_import_project.py` | Export an existing project then import as a new one | `begin_export`, `begin_import_assets` | `async_samples/sample_export_import_project_async.py` |
| `sample_update_knowledge_sources.py` | Batch modify sources, add QnA pairs, manage synonyms | `begin_update_sources`, `begin_update_qnas`, `update_synonyms` | `async_samples/sample_update_knowledge_sources_async.py` |

All async samples mirror their sync counterparts and reside in `async_samples/`.

## Running samples

Navigate to this `samples` directory (paths shown PowerShell; adjust for your shell):

Run a single sync sample:
```powershell
python sample_create_and_deploy_project.py
```

Run corresponding async sample:
```powershell
python async_samples/sample_create_and_deploy_project_async.py
```

Optionally run all samples with tox (from package root):
```powershell
tox run -e samples -c ../../../eng/tox/tox.ini --root .
```

If you see authentication errors:
- Verify endpoint spelling (must be the custom subdomain).
- For key auth: confirm the key matches the resource.
- For AAD: ensure the service principal has the appropriate Cognitive Services role.

## Snippets & documentation extraction

To surface code blocks in reference documentation or README files, enclose regions with:
```python
# [START my_region]
... code ...
# [END my_region]
```
Keywords must be unique across sync + async samples. These markers allow Sphinx `literalinclude` + snippet tooling to pull consistent, tested code.
See the repository guide for details: `doc/dev/code_snippets.md`.

## Long-running operations

Authoring operations that start with `begin_` return an `LROPoller`. In the current preview, `.result()` returns `None` (no payload). Treat completion as success; poller exceptions surface service errors.

## Cleanup

Delete temporary or experimental projects to keep your resource tidy. Use the `begin_delete_project` LRO:
```python
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.questionanswering.authoring import QuestionAnsweringAuthoringClient

client = QuestionAnsweringAuthoringClient(endpoint, AzureKeyCredential(key))
client.begin_delete_project(project_name="FAQ").result()  # returns None on completion
```
Remove exported JSON/TSV assets under `./ExportedProject` if no longer needed.

## Next steps

- Explore authoring samples in more depth (open each file for inline comments)
- Try runtime Q&A with the `azure-ai-language-questionanswering` package
- Read the authoring REST documentation
- Review the main Authoring client README for conceptual details

## Troubleshooting quick notes

- 401 / 403: Check key validity or AAD role assignment
- 404 on project: Ensure you created it (see create/deploy sample)
- Empty export file: Make sure the project has at least one QnA/source

## Contributing

Issues and contributions are welcome. See the repository `CONTRIBUTING.md` for guidelines.

<!-- LINKS -->
[rest_authoring]: https://learn.microsoft.com/rest/api/language/question-answering-projects
[code_snippets_guide]: https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/code_snippets.md
[authoring_readme]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-questionanswering-authoring/README.md
[runtime_package]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-questionanswering/README.md
