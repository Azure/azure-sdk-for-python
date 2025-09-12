# Azure AI Language Question Answering client library for Python

Question Answering lets you build a conversational Q&A layer over your existing content (FAQ pages, product manuals, documents). You ask a question and receive the best matching answers along with confidence scores. This package targets the inference (runtime) scenario.

> This library contains only the runtime (query) APIs. Authoring/project management samples and APIs have been removed or moved to a separate track. 

## Table of contents
- [Getting started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Install](#install)
  - [Authentication](#authentication)
    - [API key](#api-key)
    - [Azure Active Directory (AAD)](#azure-active-directory-aad)
- [Key concepts](#key-concepts)
- [Examples](#examples)     
  - [Ask a question (knowledge base)](#ask-a-question-knowledge-base)
  - [Ask a follow-up question](#ask-a-follow-up-question)
  - [Alternate input forms (dict / kwargs / model)](#alternate-input-forms-dict--kwargs--model)
- [Optional configuration](#optional-configuration)
- [Troubleshooting](#troubleshooting)
- [Next steps](#next-steps)
- [Contributing](#contributing)
- [License](#license)

## Getting started

### Prerequisites
- Python 3.9 or later.
- An [Azure subscription][azure_sub].
- A Language resource (Question Answering enabled) with an existing project + deployment (e.g. project name `FAQ`, deployment `production`).

### Install

```bash
pip install azure-ai-language-questionanswering
```

### Authentication

#### API key
Get the endpoint and key from the Azure Portal (Language resource) or with Azure CLI:

```powershell
az cognitiveservices account keys list --resource-group <rg> --name <resource-name>
```

Basic client creation:

```python
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.questionanswering import QuestionAnsweringClient
import os

endpoint = os.environ["AZURE_QUESTIONANSWERING_ENDPOINT"]
key      = os.environ["AZURE_QUESTIONANSWERING_KEY"]

client = QuestionAnsweringClient(endpoint, AzureKeyCredential(key))
```

#### Azure Active Directory (AAD)
To use AAD, create a resource with a custom sub‑domain and assign the appropriate Cognitive Services role (e.g. “Cognitive Services Language Reader”) to your service principal.

```python
from azure.identity import DefaultAzureCredential
from azure.ai.language.questionanswering import QuestionAnsweringClient

credential = DefaultAzureCredential()
client = QuestionAnsweringClient(
    endpoint="https://<your-subdomain>.cognitiveservices.azure.com/",
    credential=credential
)
```

Environment variables needed by `DefaultAzureCredential`: `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_CLIENT_SECRET`.

## Key concepts
- `QuestionAnsweringClient`: main entry point for querying a knowledge base.
- Answer object: includes `answer`, `confidence`, optional `short_answer` span, metadata, source, and dialog prompts.
- Context / Follow-up: you can narrow subsequent queries using the `previous_qna_id` (and optionally previous question text).

## Examples      
### Ask a question (knowledge base)

```python
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.questionanswering import QuestionAnsweringClient
import os

client = QuestionAnsweringClient(
    os.environ["AZURE_QUESTIONANSWERING_ENDPOINT"],
    AzureKeyCredential(os.environ["AZURE_QUESTIONANSWERING_KEY"])
)

response = client.get_answers(
    question="How long should my Surface battery last?",
    project_name="FAQ",
    deployment_name="production",
    top=3
)
for candidate in response.answers:
    print(f"({candidate.confidence:.2f}) {candidate.answer} | source={candidate.source}")
```

### Ask a follow-up question

```python
from azure.ai.language.questionanswering import models

first = client.get_answers(
    question="How long should charging take?",
    project_name="FAQ",
    deployment_name="production"
)

best = max(first.answers, key=lambda a: a.confidence)
followup = client.get_answers(
    question="What about battery life while gaming?",
    answer_context=models.KnowledgeBaseAnswerContext(previous_qna_id=best.qna_id),
    project_name="FAQ",
    deployment_name="production"
)
print("Follow-up answers:")
for ans in followup.answers:
    print(f"{ans.confidence:.2f} -> {ans.answer}")
```

### Alternate input forms (dict / kwargs / model)

The convenience layer accepts:
1. Model instance (`AnswersOptions`)
2. Python `dict`
3. Direct keyword arguments

All forms normalize common aliases (e.g. `q`, `question`; `qnaId` or `qna_id`; `confidenceScoreThreshold` → `confidence_threshold`). A default `language` may be injected if not provided.

```python
# kwargs form
client.get_answers(
    project_name="FAQ",
    deployment_name="production",
    question="Ports and connectors",
    top=3,
    confidence_threshold=0.2,
)

# dict form (camelCase aliases also accepted)
client.get_answers(
    {
        "question": "Ports and connectors",
        "top": 3,
        "confidenceScoreThreshold": 0.2
    },
    project_name="FAQ",
    deployment_name="production"
)
```

### Short answer (answer span)
Request short answer spans using `short_answer_options`:

```python
from azure.ai.language.questionanswering import models

resp = client.get_answers(
    question="Ports and connectors",
    project_name="FAQ",
    deployment_name="production",
    short_answer_options=models.ShortAnswerOptions(top=1, confidence_threshold=0.1)
)
for a in resp.answers:
    if a.short_answer:
        print(f"Span: '{a.short_answer.text}' offset={a.short_answer.offset} length={a.short_answer.length}")
```

## Optional configuration
Pass standard `azure-core` options like `logging_enable`, `retry_total`, custom transport, or `user_agent` via client constructor or per call. See [azure-core docs][azure_core_ref_docs].

## Troubleshooting
- Authentication errors: verify endpoint is custom sub‑domain for AAD usage.
- Empty answers: lower `confidence_threshold` or confirm the project deployment is synced.
- Playback test failures (in SDK dev): re‑record after changing request payload shape.

## Next steps
- Explore additional filters (metadata, ranker tuning).
- Integrate with a chat orchestration layer or bot framework.

## Contributing
See [CONTRIBUTING.md][contrib]. Generated files should not be edited directly; enhancements belong in specification or convenience layers.
<!-- LINKS -->
[code_of_conduct]: https://opensource.microsoft.com/codeofconduct/
[authenticate_with_token]: https://docs.microsoft.com/azure/cognitive-services/authentication?tabs=powershell#authenticate-with-an-authentication-token
[azure_identity_credentials]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity#credentials
[azure_identity_pip]: https://pypi.org/project/azure-identity/
[default_azure_credential]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity#defaultazurecredential
[pip]: https://pypi.org/project/pip/
## License
This project is licensed under the [MIT License](https://github.com/Azure/azure-sdk-for-python/blob/main/LICENSE).

---

[azure_sub]: https://azure.microsoft.com/free/
[azure_core_ref_docs]: https://azuresdkdocs.z19.web.core.windows.net/python/azure-core/latest/azure.core.html
[contrib]: https://github.com/Azure/azure-sdk-for-python/blob/main/CONTRIBUTING.md

> Default service API version: `2025-05-15-preview` (this package release `2.0.0b1` is a preview; surface or models can change).

## Service API version

By default the client targets service API version `2025-05-15-preview`.

You can override it (advanced scenario) by passing `api_version=` when creating the client:

```python
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.questionanswering import QuestionAnsweringClient

client = QuestionAnsweringClient(
    endpoint,
    AzureKeyCredential(key),
    api_version="2025-05-15-preview"  # override if future versions become available
)
```

Notes:
- Preview API versions may introduce breaking changes in later updates.
- Using an API version different from the default might not be fully validated by this package’s tests until officially supported.
