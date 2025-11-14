# Migration Guide: From Combined Package to Authoring-only Package

This guide helps you migrate from the previous combined `azure-ai-language-questionanswering` package to the new **authoring‑only** package: `azure-ai-language-questionanswering-authoring`.

## 1. Why the Split

The original package contained both:

* Runtime querying (answering questions against a deployed project)
* Authoring management (create / update / import / export / deploy projects, knowledge sources, QnAs, synonyms)

Most users need only one side. After the split:

* `azure-ai-language-questionanswering-authoring` focuses solely on project (authoring) management.
* A dedicated runtime package (or continued combined distribution) may follow separately.

## 2. Package and Client Renames

| Previous (Combined) | New Authoring Package |
|---------------------|-----------------------|
| Install: `azure-ai-language-questionanswering` | Install: `azure-ai-language-questionanswering-authoring` |
| Client: `AuthoringClient` | Client: `QuestionAnsweringAuthoringClient` |
| Async Client: `AuthoringClient` (aio) | Async: `QuestionAnsweringAuthoringClient` (aio) |

Import paths remain under `azure.ai.language.questionanswering.authoring`, but the distribution name and client class changed for clarity.

## 3. Installation

```bash
pip uninstall azure-ai-language-questionanswering -y  # if previously installed
pip install --pre azure-ai-language-questionanswering-authoring
```

From source (repo root):
```bash
pip install -e ./sdk/cognitivelanguage/azure-ai-language-questionanswering-authoring
```

## 4. Quick Code Changes

Old:

```python
from azure.ai.language.questionanswering.authoring import AuthoringClient
client = AuthoringClient(endpoint, AzureKeyCredential(key))
```

New:

```python
from azure.ai.language.questionanswering.authoring import QuestionAnsweringAuthoringClient
client = QuestionAnsweringAuthoringClient(endpoint, AzureKeyCredential(key))
```

Async:

```python
from azure.ai.language.questionanswering.authoring.aio import QuestionAnsweringAuthoringClient
```

 
## 5. Updated / Changed APIs

Key changes from earlier previews or combined forms:

| Area | Before | Now |
|------|--------|-----|
| Deployment poller result | Dict with metadata (assumed) | `None` (completion only) |
| Export poller result | URL payload (assumed) | `None` (no payload yet) |

All other authoring method names (`create_project`, `begin_update_sources`, `begin_update_qnas`, `begin_deploy_project`, `list_projects`, `list_deployments`) remain.

## 6. Long-Running Operations (LRO) Semantics

Current preview LRO pollers return `None` from `.result()`. Treat `.result()` as a completion signal only. Affected operations:

* `begin_update_sources`
* `begin_update_qnas`
* `begin_export`
* `begin_import_assets`
* `begin_deploy_project`

Future versions may introduce typed results; avoid relying on payload shape.

### Example (Import)

```python
from azure.ai.language.questionanswering.authoring import QuestionAnsweringAuthoringClient, models as qa_models
from azure.core.credentials import AzureKeyCredential

client = QuestionAnsweringAuthoringClient(endpoint, AzureKeyCredential(key))
assets = qa_models.ImportJobOptions(
    assets=qa_models.Assets(
        qnas=[
            qa_models.ImportQnaRecord(
                id=1,
                answer="Example",
                source="https://contoso/faq",
                questions=["Example?"],
            )
        ]
    )
)
poller = client.begin_import_assets(project_name="MyProject", body=assets, format="json")
poller.result()  # None (just completion)
```

 
## 7. Authentication Guidance

Preferred: Azure Active Directory with `DefaultAzureCredential`.

```python
from azure.identity import DefaultAzureCredential
from azure.ai.language.questionanswering.authoring import QuestionAnsweringAuthoringClient

endpoint = "https://<resource-name>.cognitiveservices.azure.com"
credential = DefaultAzureCredential()
client = QuestionAnsweringAuthoringClient(endpoint, credential)
```

Fallback (resource key):

```python
from azure.core.credentials import AzureKeyCredential
client = QuestionAnsweringAuthoringClient(endpoint, AzureKeyCredential(key))
```

Ensure you use the custom subdomain endpoint for AAD (not a regional alias) so the challenge flow succeeds.

## 8. Python & Dependencies

* Python >= 3.9
* Core dependencies: `azure-core`, `isodate`, (conditionally) `typing-extensions` (<3.11)

Upgrade from Python 3.8 before installing.

## 9. Environment Variables (Optional Convenience)

| Variable | Purpose |
|----------|---------|
| `AZURE_QUESTIONANSWERING_ENDPOINT` | Resource endpoint |
| `AZURE_QUESTIONANSWERING_KEY` | Key credential (if not using AAD) |
| `AZURE_QUESTIONANSWERING_PROJECT` | Optional: default project name for samples |

 
## 10. Sample & Test Layout

* `samples/` and `async_samples/` now contain **authoring-only** scenarios.
* Runtime question querying samples were removed from this package.
* Live test fixtures trimmed to authoring necessities only.

 
## 11. Backward / Rollback Strategy

If you still need runtime querying before a dedicated runtime package is published, you can temporarily continue using the combined package version you had. Plan to migrate fully once the runtime split is available.

 
## 12. Synonyms, Sources, and QnAs Model-Based Updates

Use model classes instead of raw dictionaries for clarity and forward compatibility:

```python
from azure.ai.language.questionanswering.authoring import models as qa_models
client.begin_update_sources(
    project_name="MyProject",
    sources=[
        qa_models.UpdateSourceRecord(
            op="add",
            value=qa_models.UpdateQnaSourceRecord(
                display_name="FAQSrc",
                source="https://contoso.com/faq",
                source_uri="https://contoso.com/faq",
                source_kind="url",
                content_structure_kind="unstructured",
                refresh=False,
            ),
        )
    ],
).result()
```

 
## 13. Known Preview Limitations

| Limitation | Detail |
|-----------|--------|
| LRO result payloads | All `begin_*` currently return `None` from `.result()` |
| Export artifact access | No direct download URL surfaced yet |
| Metadata evolution | Model names/fields may still change before GA |

## 15. Filing Issues

Provide:

* Old & new package versions
* Code snippet (minimal repro)
* Full stack trace (if exception)

---
Additional runtime migration notes will be added once the runtime package is published.
