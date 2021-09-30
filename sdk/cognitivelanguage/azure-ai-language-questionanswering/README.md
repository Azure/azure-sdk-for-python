[![Build Status](https://dev.azure.com/azure-sdk/public/_apis/build/status/azure-sdk-for-python.client?branchName=main)](https://dev.azure.com/azure-sdk/public/_build/latest?definitionId=46?branchName=main)

# Azure Cognitive Language Services Question Answering client library for Python

Question Answering is a cloud-based API service that lets you create a conversational question-and-answer layer over your existing data. Use it to build a knowledge base by extracting questions and answers from your semi-structured content, including FAQ, manuals, and documents. Answer users’ questions with the best answers from the QnAs in your knowledge base—automatically. Your knowledge base gets smarter, too, as it continually learns from users' behavior.

[Source code][questionanswering_client_src] | [Package (PyPI)][questionanswering_pypi_package] | [API reference documentation][questionanswering_refdocs] | [Product documentation][questionanswering_docs] | [Samples][questionanswering_samples]

## _Disclaimer_

_Azure SDK Python packages support for Python 2.7 is ending 01 January 2022. For more information and questions, please refer to https://github.com/Azure/azure-sdk-for-python/issues/20691_

## Getting started

### Prerequisites

- Python 2.7, or 3.6 or later is required to use this package.
- An [Azure subscription][azure_subscription]
- An existing Question Answering resource

> Note: the new unified Cognitive Language Services are not currently available for deployment.

### Install the package

Install the Azure QuestionAnswering client library for Python with [pip][pip_link]:

```bash
pip install azure-ai-language-questionanswering
```

### Authenticate the client

In order to interact with the Question Answering service, you'll need to create an instance of the [QuestionAnsweringClient][questionanswering_client_class] class. You will need an **endpoint**, and an **API key** to instantiate a client object. For more information regarding authenticating with Cognitive Services, see [Authenticate requests to Azure Cognitive Services][cognitive_auth].

#### Get an API key

You can get the **endpoint** and an **API key** from the Cognitive Services resource or Question Answering resource in the [Azure Portal][azure_portal].

Alternatively, use the [Azure CLI][azure_cli] command shown below to get the API key from the Question Answering resource.

```powershell
az cognitiveservices account keys list --resource-group <resource-group-name> --name <resource-name>
```

#### Create QuestionAnsweringClient

Once you've determined your **endpoint** and **API key** you can instantiate a `QuestionAnsweringClient`:

```python
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.questionanswering import QuestionAnsweringClient

endpoint = "https://{myaccount}.api.cognitive.microsoft.com"
credential = AzureKeyCredential("{api-key}")

client = QuestionAnsweringClient(endpoint, credential)
```

## Key concepts

### QuestionAnsweringClient

The [QuestionAnsweringClient][questionanswering_client_class] is the primary interface for asking questions using a knowledge base with your own information, or text input using pre-trained models.
For asynchronous operations, an async `QuestionAnsweringClient` is in the `azure.ai.language.questionanswering.aio` namespace.

## Examples

The `azure-ai-language-questionanswering` client library provides both synchronous and asynchronous APIs.

The following examples show common scenarios using the `client` [created above](#create-questionansweringclient).

- [Ask a question](#ask-a-question)
- [Ask a follow-up question](#ask-a-follow-up-question)
- [Asynchronous operations](#asynchronous-operations)

### Ask a question

The only input required to ask a question using a knowledge base is just the question itself:

```python
from azure.ai.language.questionanswering import models as qna

params = qna.QueryKnowledgeBaseOptions(
    question="How long should my Surface battery last?"
)

output = client.query_knowledgebase(
    params,
    project_name="FAQ",
)
for candidate in output.answers:
    print("({}) {}".format(candidate.confidence_score, candidate.answer))
    print("Source: {}".format(candidate.source))

```

You can set additional properties on `QueryKnowledgeBaseOptions` to limit the number of answers, specify a minimum confidence score, and more.

### Ask a follow-up question

If your knowledge base is configured for [chit-chat][questionanswering_docs_chat], the answers from the knowledge base may include suggested [prompts for follow-up questions][questionanswering_refdocs_prompts] to initiate a conversation. You can ask a follow-up question by providing the ID of your chosen answer as the context for the continued conversation:

```python
params = qna.models.QueryKnowledgeBaseOptions(
    question="How long should charging take?"
    context=qna.models.KnowledgeBaseAnswerRequestContext(
        previous_qna_id=previous_answer.id
    )
)

output = client.query_knowledgebase(
    params,
    project_name="FAQ"
)
for candidate in output.answers:
    print("({}) {}".format(candidate.confidence_score, candidate.answer))
    print("Source: {}".format(candidate.source))

```

### Asynchronous operations

The above examples can also be run asynchronously using the client in the `aio` namespace:

```python
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.questionanswering.aio import QuestionAnsweringClient
from azure.ai.language.questionanswering import models as qna

client = QuestionAnsweringClient(endpoint, credential)

params = qna.QueryKnowledgeBaseOptions(
    question="How long should my Surface battery last?"
)

output = await client.query_knowledgebase(
    params,
    project_name="FAQ"
)
```

## Optional Configuration

Optional keyword arguments can be passed in at the client and per-operation level. The azure-core [reference documentation][azure_core_ref_docs] describes available configurations for retries, logging, transport protocols, and more.

## Troubleshooting

### General

Azure QuestionAnswering clients raise exceptions defined in [Azure Core][azure_core_readme].
When you interact with the Cognitive Language Services Question Answering client library using the Python SDK, errors returned by the service correspond to the same HTTP status codes returned for [REST API][questionanswering_rest_docs] requests.

For example, if you submit a question to a non-existant knowledge base, a `400` error is returned indicating "Bad Request".

```python
from azure.core.exceptions import HttpResponseError

try:
    client.query_knowledgebase(
        params,
        project_name="invalid-knowledge-base"
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

See full SDK logging documentation with examples [here][sdk_logging_docs].

## Next steps

- View our [samples][questionanswering_samples].
- Read about the different [features][questionanswering_docs_features] of the Question Answering service.
- Try our service [demos][questionanswering_docs_demos].

## Contributing

See the [CONTRIBUTING.md][contributing] for details on building, testing, and contributing to this library.

This project welcomes contributions and suggestions. Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit [cla.microsoft.com][cla].

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct][code_of_conduct]. For more information see the [Code of Conduct FAQ][coc_faq] or contact [opencode@microsoft.com][coc_contact] with any additional questions or comments.

<!-- LINKS -->

[azure_cli]: https://docs.microsoft.com/cli/azure/
[azure_portal]: https://portal.azure.com/
[azure_subscription]: https://azure.microsoft.com/free/
[cla]: https://cla.microsoft.com
[coc_contact]: mailto:opencode@microsoft.com
[coc_faq]: https://opensource.microsoft.com/codeofconduct/faq/
[code_of_conduct]: https://opensource.microsoft.com/codeofconduct/
[cognitive_auth]: https://docs.microsoft.com/azure/cognitive-services/authentication/
[contributing]: https://github.com/Azure/azure-sdk-for-python/blob/main/CONTRIBUTING.md
[python_logging]: https://docs.python.org/3/library/logging.html
[sdk_logging_docs]: https://docs.microsoft.com/azure/developer/python/azure-sdk-logging
[azure_core_ref_docs]: https://azuresdkdocs.blob.core.windows.net/$web/python/azure-core/latest/azure.core.html
[azure_core_readme]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/README.md
[pip_link]: https://pypi.org/project/pip/
[questionanswering_client_class]: https://azuresdkdocs.blob.core.windows.net/$web/python/azure-ai-language-questionanswering/1.0.0b1/azure.ai.language.questionanswering.html#azure.ai.language.questionanswering.QuestionAnsweringClient
[questionanswering_refdocs_prompts]: https://azuresdkdocs.blob.core.windows.net/$web/python/azure-ai-language-questionanswering/1.0.0b1/azure.ai.language.questionanswering.models.html#azure.ai.language.questionanswering.models.KnowledgeBaseAnswerDialog
[questionanswering_client_src]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-questionanswering/
[questionanswering_docs]: https://azure.microsoft.com/services/cognitive-services/qna-maker/
[questionanswering_docs_chat]: https://docs.microsoft.com/azure/cognitive-services/qnamaker/how-to/chit-chat-knowledge-base
[questionanswering_docs_demos]: https://azure.microsoft.com/services/cognitive-services/qna-maker/#demo
[questionanswering_docs_features]: https://azure.microsoft.com/services/cognitive-services/qna-maker/#features
[questionanswering_pypi_package]: https://pypi.org/project/azure-ai-language-questionanswering/
[questionanswering_refdocs]: https://azuresdkdocs.blob.core.windows.net/$web/python/azure-ai-language-questionanswering/1.0.0b1/azure.ai.language.questionanswering.html
[questionanswering_rest_docs]: https://docs.microsoft.com/rest/api/cognitiveservices-qnamaker/
[questionanswering_samples]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-questionanswering/samples/README.md

![Impressions](https://azure-sdk-impressions.azurewebsites.net/api/impressions/azure-sdk-for-python%2Fsdk%2Ftemplate%2Fazure-template%2FREADME.png)
