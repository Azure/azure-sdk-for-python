# Azure AI Language Question Answering client library for Python

Question Answering is an Azure AI Language capability that lets you build a conversational, question‑and‑answer layer over your existing data. It extracts question/answer pairs from semi‑structured content (FAQ pages, manuals, documents) and uses them to answer user questions with the most relevant answer automatically.

[Source code][questionanswering_client_src]
| [Package (PyPI)][questionanswering_pypi_package]
| [Package (Conda)](https://anaconda.org/microsoft/azure-ai-language-questionanswering/)
| [API reference][questionanswering_refdocs]
| [Product documentation][questionanswering_docs]
| [Samples][questionanswering_samples]
| [Question Answering REST API][questionanswering_rest_docs]

> _Python 2.7 is not supported. For details see the Azure SDK for Python end-of-support notice._

## Getting started

### Prerequisites

* Python 3.9 or later.
* An [Azure subscription][azure_subscription].
* An Azure [Language resource][language_service] (with a custom domain endpoint if you plan to use Azure Active Directory authentication).

### Install the package

```bash
python -m pip install azure-ai-language-questionanswering
```

> This version of the client library targets the service REST API version `2025-05-15-preview`.

### Authenticate the client

You can authenticate with an API key or with an Azure Active Directory (AAD) token credential. For more details, see [Authenticate requests to Azure Cognitive Services][cognitive_auth].

#### API key

Get the endpoint and key from your Language resource in the [Azure Portal][azure_portal] or via the [Azure CLI][azure_cli]:

```powershell
az cognitiveservices account keys list --resource-group <resource-group-name> --name <resource-name>
```

Create a `QuestionAnsweringClient` using the key:

```python
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.questionanswering import QuestionAnsweringClient

endpoint = "https://{my-account}.cognitiveservices.azure.com"  # or your regional endpoint
credential = AzureKeyCredential("<api-key>")

client = QuestionAnsweringClient(endpoint, credential)
```

#### Azure Active Directory

To use AAD, create a custom subdomain for your resource (regional base endpoints do not support AAD), then use a credential from the [azure-identity][azure_identity_credentials] package (for example, `DefaultAzureCredential`). Set the environment variables `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, and `AZURE_CLIENT_SECRET` for a service principal, or ensure a developer login is available for the chained providers.

```python
from azure.ai.language.questionanswering import QuestionAnsweringClient
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()
client = QuestionAnsweringClient(
	endpoint="https://<my-custom-subdomain>.cognitiveservices.azure.com/",
	credential=credential,
)
```

## Key concepts

### QuestionAnsweringClient

`QuestionAnsweringClient` is the primary interface for querying a deployed Question Answering project (knowledge base) or for using the text-based pre-trained question answering capability. Asynchronous operations are provided in the `azure.ai.language.questionanswering.aio` namespace.

> Authoring (project creation, knowledge source management, deployment) has moved to a separate package and is intentionally not covered in this runtime client README.

## Examples

Below are some common usage examples. See the [samples][questionanswering_samples] for more scenarios.

### Ask a question

```python
import os
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.questionanswering import QuestionAnsweringClient
from azure.ai.language.questionanswering import models as qna

endpoint = os.environ["AZURE_QUESTIONANSWERING_ENDPOINT"]
key = os.environ["AZURE_QUESTIONANSWERING_KEY"]

client = QuestionAnsweringClient(endpoint, AzureKeyCredential(key))

options = qna.AnswersOptions(
    question="How long should my Surface battery last?",
    # Optional extra parameters:
    # confidence_threshold=0.2,
    # top=5,
    # short_answer_options=qna.ShortAnswerOptions(top=1)
)
response = client.get_answers(options, project_name="FAQ", deployment_name="production")

for answer in response.answers:
    print(f"({answer.confidence:.2f}) {answer.answer}")
    print(f"Source: {answer.source}")
```

You can also pass optional parameters like `confidence_threshold`, `top`, or `short_answer_options` inside the `AnswersOptions` object.

### Ask a follow-up question

If your project is configured for chit-chat, some answers may include prompts for follow-up questions. Supply the previous answer's `qna_id` as context using `KnowledgeBaseAnswerContext` in the options object.

```python
from azure.ai.language.questionanswering import models as qna

# previous_answer = ... obtain from earlier response above
follow_up_options = qna.AnswersOptions(
    question="How long should charging take?",
    answer_context=qna.KnowledgeBaseAnswerContext(previous_qna_id=previous_answer.qna_id),
)
follow_up = client.get_answers(follow_up_options, project_name="FAQ", deployment_name="production")

for answer in follow_up.answers:
    print(f"({answer.confidence:.2f}) {answer.answer}")
```

### Asynchronous usage

```python
import os
import asyncio
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.questionanswering.aio import QuestionAnsweringClient
from azure.ai.language.questionanswering import models as qna

async def main():
    endpoint = os.environ["AZURE_QUESTIONANSWERING_ENDPOINT"]
    key = os.environ["AZURE_QUESTIONANSWERING_KEY"]
    client = QuestionAnsweringClient(endpoint, AzureKeyCredential(key))
    options = qna.AnswersOptions(question="How long should my Surface battery last?")
    response = await client.get_answers(options, project_name="FAQ", deployment_name="production")
    for answer in response.answers:
        print(f"({answer.confidence:.2f}) {answer.answer}")

asyncio.run(main())
```

> Note: Starting with version `2.0.0b1`, samples and documentation use an explicit `AnswersOptions` object (or `AnswersFromTextOptions` for text) as the first positional argument when calling `get_answers` / `get_answers_from_text`. The older "flattened" parameter form (passing `question=...` directly to `get_answers`) has been removed from samples and may be rejected with a `TypeError` if used incorrectly.

## Optional configuration

You can customize transport options, retries, logging, and more by passing keyword arguments to the client or per operation. See the [azure-core configuration docs][azure_core_ref_docs] for details.

## Troubleshooting

### Exceptions

The client raises exceptions defined in [azure-core][azure_core_readme]. Service errors map to HTTP status codes returned by the REST API. For example, querying a non-existent project may raise `HttpResponseError`.

```python
from azure.core.exceptions import HttpResponseError

try:
	client.get_answers(question="Why?", project_name="invalid", deployment_name="production")
except HttpResponseError as e:
	print(f"Query failed: {e.message}")
```

### Logging

Enable detailed debug logging by setting the environment variable `AZURE_LOG_LEVEL=info` (or `debug`) or by passing `logging_enable=True` when constructing the client / calling an operation. See [SDK logging docs][sdk_logging_docs] for more information.

## Next steps

* Explore the [samples][questionanswering_samples].
* Read the [feature overview][questionanswering_docs_features].
* Try live [demos][questionanswering_docs_demos].

## Contributing

See the [CONTRIBUTING.md][contributing] in the Azure SDK for Python repository for guidance on contributing to this library.

This project welcomes contributions and suggestions. Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit [cla.microsoft.com][cla].

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct][code_of_conduct]. For more information see the [Code of Conduct FAQ][coc_faq] or contact [opencode@microsoft.com][coc_contact].

<!-- LINKS -->
[azure_cli]: https://learn.microsoft.com/cli/azure/
[azure_portal]: https://portal.azure.com/
[azure_subscription]: https://azure.microsoft.com/free/
[language_service]: https://ms.portal.azure.com/#create/Microsoft.CognitiveServicesTextAnalytics
[cla]: https://cla.microsoft.com
[coc_contact]: mailto:opencode@microsoft.com
[coc_faq]: https://opensource.microsoft.com/codeofconduct/faq/
[code_of_conduct]: https://opensource.microsoft.com/codeofconduct/
[cognitive_auth]: https://learn.microsoft.com/azure/cognitive-services/authentication/
[contributing]: https://github.com/Azure/azure-sdk-for-python/blob/main/CONTRIBUTING.md
[python_logging]: https://docs.python.org/3/library/logging.html
[sdk_logging_docs]: https://learn.microsoft.com/azure/developer/python/azure-sdk-logging
[azure_core_ref_docs]: https://azuresdkdocs.z19.web.core.windows.net/python/azure-core/latest/azure.core.html
[azure_core_readme]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/README.md
[questionanswering_client_src]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-questionanswering/
[questionanswering_docs]: https://learn.microsoft.com/azure/ai-services/language-service/question-answering/overview
[questionanswering_docs_demos]: https://learn.microsoft.com/azure/ai-services/language-service/question-answering/quickstart/sdk
[questionanswering_docs_features]: https://learn.microsoft.com/azure/ai-services/language-service/question-answering/overview#key-capabilities
[questionanswering_pypi_package]: https://pypi.org/project/azure-ai-language-questionanswering/
[questionanswering_refdocs]: https://azuresdkdocs.z19.web.core.windows.net/python/azure-ai-language-questionanswering/latest/azure.ai.language.questionanswering.html
[questionanswering_samples]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-questionanswering/samples/README.md
[azure_identity_credentials]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity#credentials
[default_azure_credential]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity#defaultazurecredential
[questionanswering_rest_docs]: https://learn.microsoft.com/rest/api/language/question-answering?view=rest-language-2025-05-15-preview
