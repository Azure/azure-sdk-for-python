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

Install the Azure Question Answering client library for Python with [pip][pip_link]:

```bash
python -m pip install azure-ai-language-questionanswering
```

> This version of the client library targets the service REST API version `2025-05-15-preview`.

### Authenticate the client

In order to interact with the Question Answering service, you'll create an instance of the [QuestionAnsweringClient][questionanswering_client_class] (or the [AuthoringClient][authoring_client_class] in the separate authoring package). The **recommended** approach is to use Azure Active Directory via `DefaultAzureCredential` from the [azure-identity][azure_identity_credentials] library. This avoids embedding keys, enables managed identity in production, and unifies authentication across Azure SDKs.

> Important: To use Azure AD (AAD) you must use your resource's **custom subdomain** endpoint (for example: `https://<my-subdomain>.cognitiveservices.azure.com/`); legacy regional generic endpoints (e.g., `https://eastus.api.cognitive.microsoft.com`) do **not** support AAD token authentication.

#### Recommended: DefaultAzureCredential

Prerequisites for AAD authentication:

* [Install azure-identity][install_azure_identity]
* [Register an AAD application][register_aad_app]
* [Grant access][grant_role_access] to the Language resource (e.g., assign the "Cognitive Services Language Reader" role, plus writer roles if needed for authoring)

Set these environment variables only if you’re using a service principal with a client secret (otherwise, if you rely on Azure CLI / VS Code login or Managed Identity, you can skip this step):
AZURE_CLIENT_ID, AZURE_TENANT_ID, AZURE_CLIENT_SECRET

Then create the client:

```python
from azure.identity import DefaultAzureCredential
from azure.ai.language.questionanswering import QuestionAnsweringClient

endpoint = "https://<my-subdomain>.cognitiveservices.azure.com/"  # custom subdomain endpoint
credential = DefaultAzureCredential()

client = QuestionAnsweringClient(endpoint, credential)
```

Authoring (if using the separate authoring package):

```python
from azure.identity import DefaultAzureCredential
from azure.ai.language.questionanswering.authoring import AuthoringClient

endpoint = "https://<my-subdomain>.cognitiveservices.azure.com/"
credential = DefaultAzureCredential()

authoring_client = AuthoringClient(endpoint, credential)
```

#### Alternative: API key credential

For quick starts or scripts where you have not yet configured AAD, you can use an API key with `AzureKeyCredential`. You can obtain the key from the Azure Portal, or via the CLI:

```powershell
az cognitiveservices account keys list --resource-group <resource-group-name> --name <resource-name>
```

Then:

```python
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.questionanswering import QuestionAnsweringClient

endpoint = "https://<my-account>.cognitiveservices.azure.com"  # regional or custom subdomain
credential = AzureKeyCredential("<api-key>")

client = QuestionAnsweringClient(endpoint, credential)
```

> Note: You can seamlessly switch between key and AAD auth — no code changes beyond the credential object.

**Why DefaultAzureCredential?**

* Eliminates hard‑coded secrets
* Works locally (developer tools), in CI (service principal / federated), and in production (Managed Identity)
* Centralizes token acquisition & caching
* Supports future auth enhancements without code changes

## Key concepts

### QuestionAnsweringClient

The [QuestionAnsweringClient][questionanswering_client_class] is the primary interface for asking questions using a knowledge base with your own information, or text input using pre-trained models.
For asynchronous operations, an async `QuestionAnsweringClient` is in the `azure.ai.language.questionanswering.aio` namespace.

> Authoring (project creation, knowledge source management, deployment) has moved to a separate package and is intentionally not covered in this runtime client README.

## Examples

### QuestionAnsweringClient usage examples

The `azure-ai-language-questionanswering` client library provides both synchronous and asynchronous APIs.

* [Ask a question](#ask-a-question-options-object)
* [Ask a follow-up question](#follow-up-question-options-object)
* [Asynchronous operations](#async-usage-options-object)

#### Ask a question (options object)

The only input required to ask a question using a knowledge base is just the question itself:

```python
import os
from azure.identity import DefaultAzureCredential
from azure.ai.language.questionanswering import QuestionAnsweringClient
from azure.ai.language.questionanswering.models import AnswersOptions

endpoint = os.environ["AZURE_QUESTIONANSWERING_ENDPOINT"]  # must be a custom subdomain for AAD
client = QuestionAnsweringClient(endpoint, DefaultAzureCredential())

options = AnswersOptions(
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

#### Ask a question (flattened)

For convenience, you can also call `get_answers` directly with keyword parameters:

```python
# Equivalent flattened form - same result as above
response = client.get_answers(
    question="How long should my Surface battery last?",
    project_name="FAQ",
    deployment_name="production",
    # Optional parameters can be passed directly:
    # confidence_threshold=0.2,
    # top=5
)

for answer in response.answers:
    print(f"({answer.confidence:.2f}) {answer.answer}")
    print(f"Source: {answer.source}")
```

#### Follow-up question (options object)

If your knowledge base is configured for [chit-chat][questionanswering_docs_chat], the answers from the knowledge base may include suggested [prompts for follow-up questions][questionanswering_refdocs_prompts] to initiate a conversation. You can ask a follow-up question by providing the ID of your chosen answer as the context for the continued conversation:

```python
from azure.ai.language.questionanswering.models import AnswersOptions, KnowledgeBaseAnswerContext

follow_up_options = AnswersOptions(
    question="How long should charging take?",
    answer_context=KnowledgeBaseAnswerContext(previous_qna_id=previous_answer.qna_id),
)
follow_up = client.get_answers(follow_up_options, project_name="FAQ", deployment_name="production")

for answer in follow_up.answers:
    print(f"({answer.confidence:.2f}) {answer.answer}")
```

#### Follow-up question (flattened)

```python
import os
from azure.identity import DefaultAzureCredential
from azure.ai.language.questionanswering import QuestionAnsweringClient
from azure.ai.language.questionanswering.models import KnowledgeBaseAnswerContext

endpoint = os.environ["AZURE_QUESTIONANSWERING_ENDPOINT"]
client = QuestionAnsweringClient(endpoint, DefaultAzureCredential())

output = client.get_answers(
    question="How long should charging take?",
    answer_context=KnowledgeBaseAnswerContext(previous_qna_id=previous_answer.qna_id),
    project_name="FAQ",
    deployment_name="production"
)
for candidate in output.answers:
    print(f"({candidate.confidence}) {candidate.answer}")
    print(f"Source: {candidate.source}")
```

#### Async usage (options object)

The above examples can also be run asynchronously using the clients in the `aio` namespace:

```python
import os
import asyncio
from azure.identity import DefaultAzureCredential
from azure.ai.language.questionanswering.aio import QuestionAnsweringClient
from azure.ai.language.questionanswering.models import AnswersOptions

async def main():
    endpoint = os.environ["AZURE_QUESTIONANSWERING_ENDPOINT"]
    client = QuestionAnsweringClient(endpoint, DefaultAzureCredential())
    options = AnswersOptions(question="How long should my Surface battery last?")
    response = await client.get_answers(options, project_name="FAQ", deployment_name="production")
    for answer in response.answers:
        print(f"({answer.confidence:.2f}) {answer.answer}")

asyncio.run(main())
```

#### Async usage (flattened)

```python
import os
import asyncio
from azure.identity import DefaultAzureCredential
from azure.ai.language.questionanswering.aio import QuestionAnsweringClient

async def main():
    endpoint = os.environ["AZURE_QUESTIONANSWERING_ENDPOINT"]
    client = QuestionAnsweringClient(endpoint, DefaultAzureCredential())
    output = await client.get_answers(
        question="How long should my Surface battery last?",
        project_name="FAQ",
        deployment_name="production"
    )
    for candidate in output.answers:
        print(f"({candidate.confidence:.2f}) {candidate.answer}")

asyncio.run(main())
```

#### Filtering with metadata (QueryFilters)

You can narrow answers using metadata stored in your knowledge base:

```python
from azure.ai.language.questionanswering.models import (
    AnswersOptions,
    QueryFilters,
    MetadataFilter,
    MetadataRecord
)

# Tuple form (supported)
metadata_filter_tuple = MetadataFilter(metadata=[("product", "surface"), ("locale", "en-US")])

# MetadataRecord form (recommended for static typing)
metadata_filter_records = MetadataFilter(metadata=[
    MetadataRecord(key="product", value="surface"),
    MetadataRecord(key="locale", value="en-US")
])

options = AnswersOptions(
    question="How long should my Surface battery last?",
    filters=QueryFilters(metadata_filter=metadata_filter_tuple),
    confidence_threshold=0.2,
    top=3
)

resp = client.get_answers(options, project_name="FAQ", deployment_name="production")
for ans in resp.answers:
    print(f"{ans.answer} ({ans.confidence:.2f})")

# Note: Passing metadata as a dict (e.g. {'product': 'surface'}) is no longer supported.
```

## Optional Configuration

Optional keyword arguments can be passed in at the client and per-operation level. The azure-core [reference documentation][azure_core_ref_docs] describes available configurations for retries, logging, transport protocols, and more.

## Troubleshooting

### General

Azure Question Answering clients raise exceptions defined in [Azure Core][azure_core_readme].
When you interact with the Cognitive Language Service Question Answering client library using the Python SDK, errors returned by the service correspond to the same HTTP status codes returned for [REST API][questionanswering_rest_docs] requests.

For example, if you submit a question to a non-existent knowledge base, a `400` error is returned indicating "Bad Request".

```python
from azure.core.exceptions import HttpResponseError

try:
    client.get_answers(
        question="Why?",
        project_name="invalid-knowledge-base",
        deployment_name="production"
    )
except HttpResponseError as error:
    print("Query failed: {}".format(error.message))
```

### Logging

This library uses the standard
[logging][python_logging] library for logging.
Basic information about HTTP sessions (URLs, headers, etc.) is logged at INFO
level.

Detailed DEBUG level logging, including request/response bodies and unredacted
headers, can be enabled on a client with the `logging_enable` argument.

See the full SDK logging documentation with examples in the [logging guidance][sdk_logging_docs].

## API Usage Notes

This library supports both explicit options objects (like `AnswersOptions` for `get_answers` and `AnswersFromTextOptions` for `get_answers_from_text`) and flattened keyword parameters for convenience. Both approaches are fully supported and equivalent (and work regardless of whether you use `DefaultAzureCredential` or an API key):

* **Options object approach**: `client.get_answers(AnswersOptions(question="...", top=5), project_name="...", deployment_name="...")`
* **Flattened parameters**: `client.get_answers(question="...", top=5, project_name="...", deployment_name="...")`

Choose whichever style best fits your coding preferences - both produce identical results.

## Next steps

* View our [samples][questionanswering_samples].
* Read about the different [features][questionanswering_docs_features] of the Question Answering service.
* Try our service [demos][questionanswering_docs_demos].

## Contributing

See the [CONTRIBUTING.md][contributing] for details on building, testing, and contributing to this library.

This project welcomes contributions and suggestions. Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit [cla.microsoft.com][cla].

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct][code_of_conduct]. For more information see the [Code of Conduct FAQ][coc_faq] or contact [opencode@microsoft.com][coc_contact] with any additional questions or comments.

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
[pip_link]: https://pypi.org/project/pip/
[questionanswering_client_class]: https://azuresdkdocs.z19.web.core.windows.net/python/azure-ai-language-questionanswering/latest/azure.ai.language.questionanswering.html#azure.ai.language.questionanswering.QuestionAnsweringClient
[authoring_client_class]: https://aka.ms/azsdk/python/questionansweringauthoringclient
[questionanswering_refdocs_prompts]: https://azuresdkdocs.z19.web.core.windows.net/python/azure-ai-language-questionanswering/latest/azure.ai.language.questionanswering.models.html#azure.ai.language.questionanswering.models.KnowledgeBaseAnswerDialog
[questionanswering_client_src]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-questionanswering/
[questionanswering_docs]: https://learn.microsoft.com/azure/ai-services/language-service/question-answering/overview
[questionanswering_docs_chat]: https://learn.microsoft.com/azure/cognitive-services/qnamaker/how-to/chit-chat-knowledge-base
[questionanswering_docs_features]: https://learn.microsoft.com/azure/ai-services/language-service/question-answering/overview#key-capabilities
[questionanswering_pypi_package]: https://pypi.org/project/azure-ai-language-questionanswering/
[questionanswering_refdocs]: https://azuresdkdocs.z19.web.core.windows.net/python/azure-ai-language-questionanswering/latest/azure.ai.language.questionanswering.html
[questionanswering_samples]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-questionanswering/samples/README.md
[azure_identity_credentials]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity#credentials
[install_azure_identity]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity#install-the-package
[register_aad_app]: https://learn.microsoft.com/azure/cognitive-services/authentication#assign-a-role-to-a-service-principal
[grant_role_access]: https://learn.microsoft.com/azure/cognitive-services/authentication#assign-a-role-to-a-service-principal
[questionanswering_rest_docs]: https://learn.microsoft.com/rest/api/language/question-answering/operation-groups?view=rest-language-question-answering-2025-05-15-preview
[questionanswering_docs_demos]: https://learn.microsoft.com/azure/ai-services/language-service/question-answering/overview#try-it
