# Azure AI Language Question Answering Authoring client library for Python

The `azure-ai-language-questionanswering-authoring` package provides **authoring (management) operations** for Azure AI Language Question Answering. It is separated from the runtime Q&A client (`azure-ai-language-questionanswering`) and focuses on creating, updating, importing, exporting, and deploying Question Answering projects, as well as managing knowledge sources, QnAs, and synonyms.

> NOTE: This is a preview (`1.0.0b1`) targeting a preview service API version. APIs, return types (especially long‑running operation (LRO) payloads), and model names may change before GA.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Create the client](#create-the-client)
4. [Common operations](#common-operations)
    * [Create a project](#create-a-project)
    * [List projects](#list-projects)
    * [Update sources (model-based)](#update-sources)
    * [Update QnAs (model-based)](#update-qnas)
    * [Update synonyms](#update-synonyms)
    * [Deploy a project](#deploy-a-project)
    * [Export / Import project](#export--import)
5. [Authentication](#authentication)
6. [Long-running operations (LRO) behavior](#long-running-operations-lro-behavior)
7. [Versioning](#versioning)
8. [Logging](#logging)
9. [Contributing](#contributing)

## Prerequisites

* Python 3.9+.
* An Azure subscription.
* An Azure AI Language resource with Question Answering enabled.

## Installation

```bash
python -m pip install --pre azure-ai-language-questionanswering-authoring
```

## Create the client

Recommended: use Azure Active Directory with `DefaultAzureCredential` (supports managed identity, developer CLI, Visual Studio Code sign-in, environment variables, etc.).

Install the identity dependency if you have not already:

```bash
python -m pip install azure-identity
```

```python
from azure.identity import DefaultAzureCredential
from azure.ai.language.questionanswering.authoring import QuestionAnsweringAuthoringClient

endpoint = "https://<resource-name>.cognitiveservices.azure.com"  # custom subdomain endpoint
credential = DefaultAzureCredential()
client = QuestionAnsweringAuthoringClient(endpoint, credential)
```

## Common operations

### Create a project

```python
metadata = {
    "language": "en",
    "description": "FAQ project",
    "settings": {"defaultAnswer": "no answer"},
    "multilingualResource": True,
}
client.create_project(project_name="FAQ", body=metadata)
```

### List projects

`list_projects` yields dict-like elements. Use key access for stability.

```python
for p in client.list_projects():
    print(p.get("projectName"), p.get("lastModifiedDateTime"))
```

### Update sources

Model-based updates (preferred for type safety). The operation returns an `LROPoller[None]`; `.result()` completes the update with no payload.

```python
from azure.ai.language.questionanswering.authoring import models as qa_models

poller = client.begin_update_sources(
    project_name="FAQ",
    body=[
        qa_models.UpdateSourceRecord(
            op="add",
            value=qa_models.UpdateQnaSourceRecord(
                display_name="ContosoFAQ",
                source="https://contoso.com/faq",
                source_uri="https://contoso.com/faq",
                source_kind="url",
                content_structure_kind="unstructured",
                refresh=False,
            ),
        )
    ],
)
poller.result()  # returns None
```

### Update QnAs

```python
from azure.ai.language.questionanswering.authoring import models as qa_models

poller = client.begin_update_qnas(
    project_name="FAQ",
    body=[
        qa_models.UpdateQnaRecord(
            op="add",
            value=qa_models.QnaRecord(
                id=1,
                answer="You can use the Azure SDKs.",
                source="manual",
                questions=["How do I use Azure services in .NET?"],
            ),
        )
    ],
)
poller.result()  # returns None
```

### Update synonyms

```python
from azure.ai.language.questionanswering.authoring import models as qa_models

client.update_synonyms(
    project_name="FAQ",
    body=qa_models.SynonymAssets(
        value=[
            qa_models.WordAlterations(alterations=["qnamaker", "qna maker"]),
            qa_models.WordAlterations(alterations=["qna", "question and answer"]),
        ]
    ),
)
for group in client.get_synonyms(project_name="FAQ"):
    print("Synonyms group:")
    for alt in group["alterations"]:
        print("  ", alt)
```

### Deploy a project

```python
deploy_poller = client.begin_deploy_project(project_name="FAQ", deployment_name="production")
deploy_poller.result()  # returns None
```

### Export / Import

Current preview LROs for export/import return `None` from `.result()` (no metadata payload). Provide assets manually for import.

```python
# Export (no payload available yet)
export_poller = client.begin_export(project_name="FAQ", format="json")
export_poller.result()  # returns None

# Minimal import assets (one QnA) example
from azure.ai.language.questionanswering.authoring import models as qa_models
assets = qa_models.ImportJobOptions(
    assets=qa_models.Assets(
        qnas=[
            qa_models.ImportQnaRecord(
                id=1,
                answer="Example answer",
                source="https://contoso.com/faq",
                questions=["Example question?"],
            )
        ]
    )
)
import_poller = client.begin_import_method(project_name="FAQ", body=assets, format="json")
import_poller.result()  # returns None
```

## Authentication

You can authenticate with (preferred first):

1. Azure Active Directory credentials via `DefaultAzureCredential` (recommended for production and local dev parity).
2. A resource key using `AzureKeyCredential` (fallback / quick start).

For AAD, use your resource's custom subdomain endpoint (NOT a regional shared endpoint) so the challenge flow can succeed.

Example (resource key fallback):

```python
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.questionanswering.authoring import QuestionAnsweringAuthoringClient

endpoint = "https://<resource-name>.cognitiveservices.azure.com"
key = "<api-key>"
client = QuestionAnsweringAuthoringClient(endpoint, AzureKeyCredential(key))
```

## Long-running operations (LRO) behavior

Preview LROs (`begin_update_*`, `begin_import_method`, `begin_export`, `begin_deploy_project`) return `LROPoller[None]`. The service currently does not project operation metadata in the final result. Plan your code to treat `.result()` as a completion signal only. Future versions may introduce typed results.

## Versioning

This library targets the preview API version `2025-05-15-preview`. Features and models may change; pin a specific package version in production scenarios until GA.

## Logging

Enable basic logging:

```python
import logging
logging.basicConfig(level=logging.INFO)
```
Or enable HTTP-level logging (see `azure-core` docs) by setting environment variable `AZURE_LOG_LEVEL=info`.

## Contributing

This project welcomes contributions and suggestions. Most contributions require
you to agree to a Contributor License Agreement (CLA) declaring that you have
the right to, and actually do, grant us the rights to use your contribution.
For details, visit <https://cla.microsoft.com>.

When you submit a pull request, a CLA-bot will automatically determine whether
you need to provide a CLA and decorate the PR appropriately (e.g., label,
comment). Simply follow the instructions provided by the bot. You will only
need to do this once across all repos using our CLA.

This project has adopted the
[Microsoft Open Source Code of Conduct][code_of_conduct]. For more information,
see the Code of Conduct FAQ or contact <mailto:opencode@microsoft.com> with any
additional questions or comments.

<!-- LINKS -->
[code_of_conduct]: https://opensource.microsoft.com/codeofconduct/
<!-- Removed unused link reference definitions to satisfy markdown lint -->
