# Authoring Samples

These samples demonstrate how to use the `azure-ai-language-questionanswering-authoring` package to manage Question Answering projects.

## Prerequisites

1. A Language (Question Answering) resource in Azure.
2. Python 3.9+.
3. Install the package (editable from repo root):
   `pip install -e .` (from the package root) or install dependencies listed in `sdk_packaging.toml`.

## Environment Variables

Set the following before running samples:

* `AZURE_QUESTIONANSWERING_ENDPOINT` - The endpoint of your resource.
* `AZURE_QUESTIONANSWERING_KEY` - A key for the resource.
* `AZURE_QUESTIONANSWERING_PROJECT` - (Only for export/import samples) existing project name.

Example (PowerShell):
```powershell
$env:AZURE_QUESTIONANSWERING_ENDPOINT="https://<your-resource>.cognitiveservices.azure.com/"
$env:AZURE_QUESTIONANSWERING_KEY="<api-key>"
$env:AZURE_QUESTIONANSWERING_PROJECT="myProject"
```

## Samples

Synchronous samples in `authoring/`:

* `sample_create_and_deploy_project.py` - Create a project, add a source, deploy it.
* `sample_export_import_project.py` - Export a project and re-import as a new one.
* `sample_update_knowledge_sources.py` - Add sources, QnAs, and synonyms.

Asynchronous samples in `authoring/async_samples/` mirror the sync versions.

## Running

From this samples directory:

```powershell
python authoring/sample_create_and_deploy_project.py
```

Or async:

```powershell
python authoring/async_samples/sample_create_and_deploy_project_async.py
```

## Notes

* Long-running operations return pollers; `.result()` waits for completion (or `await` for async).
* Clean up test projects you create to avoid clutter.
* For larger exports (excel/tsv), the export sample code writes files to `./ExportedProject`.
