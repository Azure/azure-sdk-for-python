# Azure AI Language Question Answering Authoring client library for Python

The `azure-ai-language-questionanswering-authoring` package provides **authoring / management capabilities** for Azure AI Language Question Answering: create and configure projects, add knowledge sources, manage QnA pairs and synonyms, and deploy versions. Runtime (query) operations live in the separate `azure-ai-language-questionanswering` package.

> NOTE: This is a preview (`1.0.0b1`) targeting a preview service API version (`2025-05-15-preview`). APIs, models, and LRO result payloads may change before GA.

[Product documentation][product_docs]

## Getting started

### Prerequisites

- Python 3.9+ (preview requires 3.9 or later)
- An Azure subscription
- An Azure AI Language resource with Question Answering enabled (custom subdomain endpoint recommended for AAD)

### Install the package

```bash
pip install --pre azure-ai-language-questionanswering-authoring
```

Optional (for Azure Active Directory auth):

```bash
pip install azure-identity
```

### Authenticate the client

You can authenticate with:

1. Azure Active Directory via `DefaultAzureCredential` (recommended)
2. A resource key via `AzureKeyCredential` (quick start / local experimentation)

AAD example:
```python
from azure.identity import DefaultAzureCredential
from azure.ai.language.questionanswering.authoring import QuestionAnsweringAuthoringClient

endpoint = "https://<resource-name>.cognitiveservices.azure.com"
credential = DefaultAzureCredential()
client = QuestionAnsweringAuthoringClient(endpoint, credential)
```

Key credential example:
```python
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.questionanswering.authoring import QuestionAnsweringAuthoringClient

client = QuestionAnsweringAuthoringClient(
    endpoint="https://<resource-name>.cognitiveservices.azure.com",
    credential=AzureKeyCredential("<api-key>")
)
```

## Key concepts

- **Project**: A logical container for your knowledge sources, QnA pairs, synonyms, and deployments.
- **Knowledge Source**: A URL/file describing content from which QnA pairs can be extracted.
- **QnA Record**: A question and its answer plus metadata/alternative questions.
- **Synonyms**: Word alteration groups to normalize variations in user questions.
- **Deployment**: A named (e.g., `production`) deployed snapshot of your project used by runtime clients.
- **Long‑running operation (LRO)**: Certain operations (update sources/QnAs, import, export, deploy) return an `LROPoller`. In the current preview these resolve to `None`—treat `.result()` strictly as a completion signal.

## Examples

Below are minimal synchronous examples. More complete samples (including async equivalents) are in the samples directory. Environment variables used by samples: `AZURE_QUESTIONANSWERING_ENDPOINT`, `AZURE_QUESTIONANSWERING_KEY`.

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
```python
for proj in client.list_projects():
    print(proj.get("projectName"), proj.get("lastModifiedDateTime"))
```

### Add / update a knowledge source
```python
from azure.ai.language.questionanswering.authoring.models import UpdateSourceRecord,UpdateQnaSourceRecord 

poller = client.begin_update_sources(
    project_name="FAQ",
    body=[
        UpdateSourceRecord(
            op="add",
            value=UpdateQnaSourceRecord(
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
poller.result()
```

### Add a QnA pair
```python
from azure.ai.language.questionanswering.authoring.models import UpdateQnaRecord,QnaRecord

poller = client.begin_update_qnas(
    project_name="FAQ",
    body=[
        UpdateQnaRecord(
            op="add",
            value=QnaRecord(
                id=1,
                answer="Use the Azure SDKs.",
                source="manual",
                questions=["How do I use Azure services in .NET?"],
            ),
        )
    ],
)
poller.result()
```

### Set synonyms
```python
from azure.ai.language.questionanswering.authoring.models import SynonymAssets,WordAlterations

client.update_synonyms(
    project_name="FAQ",
    body=SynonymAssets(
        value=[
            WordAlterations(alterations=["qnamaker", "qna maker"]),
            WordAlterations(alterations=["qna", "question and answer"]),
        ]
    ),
)
```

### Deploy
```python
client.begin_deploy_project(project_name="FAQ", deployment_name="production").result()
```

### Export / Import
```python
export_poller = client.begin_export(project_name="FAQ", format="json")
export_poller.result()  # current preview returns None

from azure.ai.language.questionanswering.authoring.models import ImportJobOptions,Assets,ImportQnaRecord
assets = ImportJobOptions(
    assets=Assets(
        qnas=[
            ImportQnaRecord(
                id=1,
                answer="Example answer",
                source="https://contoso.com/faq",
                questions=["Example question?"],
            )
        ]
    )
)
client.begin_import_assets(project_name="FAQ", body=assets, format="json").result()
```

## Troubleshooting

### Errors
Service errors raise `HttpResponseError` (or subclasses) from `azure-core`. Check the `.status_code` / `.message` for details.

```python
from azure.core.exceptions import HttpResponseError

try:
    client.list_projects()
except HttpResponseError as e:
    print("Request failed:", e.message)
```

### Logging
Enable basic logging:
```python
import logging
logging.basicConfig(level=logging.INFO)
```
For request/response details set environment variable `AZURE_LOG_LEVEL=info` or pass `logging_enable=True` per operation.

## Next steps

- Explore the full samples
- Learn about Question Answering concepts in [product documentation][product_docs]

## Contributing

See [CONTRIBUTING.md][contributing] for instructions on building, testing, and contributing.

This project welcomes contributions and suggestions. Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit <https://cla.microsoft.com>.

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct][code_of_conduct]. For more information see the [Code of Conduct FAQ][coc_faq] or contact <mailto:opencode@microsoft.com> with any additional questions or comments.

<!-- LINKS -->
[product_docs]: https://learn.microsoft.com/azure/ai-services/language-service/question-answering/overview
[contributing]: https://github.com/Azure/azure-sdk-for-python/blob/main/CONTRIBUTING.md
[code_of_conduct]: https://opensource.microsoft.com/codeofconduct/
[coc_faq]: https://opensource.microsoft.com/codeofconduct/faq/
