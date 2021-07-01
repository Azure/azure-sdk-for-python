[![Build Status](https://dev.azure.com/azure-sdk/public/_apis/build/status/azure-sdk-for-python.client?branchName=main)](https://dev.azure.com/azure-sdk/public/_build/latest?definitionId=46?branchName=main)

# Azure Cognitive Language Services Question Answering client library for Python

Question Answering is a cloud-based API service that lets you create a conversational question-and-answer layer over your existing data. Use it to build a knowledge base by extracting questions and answers from your semi-structured content, including FAQ, manuals, and documents. Answer users’ questions with the best answers from the QnAs in your knowledge base—automatically. Your knowledge base gets smarter, too, as it continually learns from user behavior.

[Source code][questionanswering_client_src] | [Package (PyPI)][questionanswering_pypi_package] | [API reference documentation][questionanswering_refdocs] | [Product documentation][questionanswering_docs] | [Samples][questionanswering_samples]

## Getting started

### Prerequisites

* Python 2.7, or 3.6 or later is required to use this package.
* An [Azure subscription][azure_subscription]
* An existing Question Answering resource

> Note: the new unified Cognitive Language Services are not currently available for deployment.

### Install the package

Install the Azure QuestionAnswering client library for Python with [pip][pip_link]:

```bash
pip install azure-ai-language-questionanswering --pre
```

### Authenticate the client

In order to interact with the Question Answering service, you'll need to create an instance of the [`QuestionAnsweringClient`][questionanswering_client_class] class. You will need an **endpoint**, and an **API key** instantiate a client object. For more information regarding authenticating with Cognitive Services, see [Authenticate requests to Azure Cognitive Services][cognitive_auth].

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

endpoint = "https://myaccount.api.cognitive.microsoft.com"
credential = AzureKeyCredential("{api-key}")

client = QuestionAnsweringClient(endpoint, credential)
```
Or an asynchronous client:
```python
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.questionanswering.aio import QuestionAnsweringClient

endpoint = "https://myaccount.api.cognitive.microsoft.com"
credential = AzureKeyCredential("{api-key}")

client = QuestionAnsweringClient(endpoint, credential)
```

## Key concepts

### QuestionAnsweringClient

The [`QuestionAnsweringClient`][questionanswering_client_class] is the primary interface for asking questions using a knowledge base with your own information, or text input using pre-trained models. 
For asynchronous operations, an async `QuestionAnsweringClient` is in the `azure.ai.language.questionanswering.aio` namespace.

## Examples

The `azure-ai-language-questionanswering` client library provides both synchronous and asynchronous APIs.

The following examples show common scenarios using the `client` [created above](#create-questionansweringclient).

### Ask a question

The only input required to a ask a question using a knowledgebase is just the question itself:

```python
from azure.ai.lanuage import questionanswering as qna

params = qna.models.KnowledgebaseQueryParameters(
    question="How long should my Surface battery last?"
)

output = client.query_knowledgebase(
    project_name="FAQ",
    knowledgebase_query_parameters=params
)
for answer in output.answers:
    print("({}) {}".format(answer.confidence_score, answer.answer))
    print("Source: {}".format(answer.source))

```

You can set additional properties on `KnowledgebaseQueryParameters` to limit the number of answers, specify a minimum confidence score, and more.

### Ask a follow-up question

If your knowledgebase is configured for [chit-chat][questionanswering_docs_chat], you can ask a follow-up question provided the previous question-answering ID and, optionally, the exact question the user asked:

```python
params = qna.models.KnowledgebaseQueryParameters(
    question="How long should charging take?"
    context=qna.models.KnowledgebaseAnswerRequestContext(
        previous_user_query="How long should my Surface battery last?",
        previous_qna_id=previous_asnwer.id
    )
)

output = client.query_knowledgebase(
    project_name="FAQ",
    knowledgebase_query_parameters=params
)
for answer in output.answers:
    print("({}) {}".format(answer.confidence_score, answer.answer))
    print("Source: {}".format(answer.source))

```

## Optional Configuration
Optional keyword arguments can be passed in at the client and per-operation level. The azure-core [reference documentation][azure_core_ref_docs] describes available configurations for retries, logging, transport protocols, and more.


### Retry Policy configuration

Use the following keyword arguments when instantiating a client to configure the retry policy:

* __retry_total__ (int): Total number of retries to allow. Takes precedence over other counts.
Pass in `retry_total=0` if you do not want to retry on requests. Defaults to 10.
* __retry_connect__ (int): How many connection-related errors to retry on. Defaults to 3.
* __retry_read__ (int): How many times to retry on read errors. Defaults to 3.
* __retry_status__ (int): How many times to retry on bad status codes. Defaults to 3.
* __retry_to_secondary__ (bool): Whether the request should be retried to secondary, if able.
This should only be enabled of RA-GRS accounts are used and potentially stale data can be handled.
Defaults to `False`.

### Other client / per-operation configuration

Other optional configuration keyword arguments that can be specified on the client or per-operation.

**Client keyword arguments:**

* __connection_timeout__ (int): Optionally sets the connect and read timeout value, in seconds.
* __transport__ (Any): User-provided transport to send the HTTP request.

**Per-operation keyword arguments:**

* __raw_response_hook__ (callable): The given callback uses the response returned from the service.
* __raw_request_hook__ (callable): The given callback uses the request before being sent to service.
* __client_request_id__ (str): Optional user specified identification of the request.
* __user_agent__ (str): Appends the custom value to the user-agent header to be sent with the request.
* __logging_enable__ (bool): Enables logging at the DEBUG level. Defaults to False. Can also be passed in at
the client level to enable it for all requests.
* __headers__ (dict): Pass in custom headers as key, value pairs. E.g. `headers={'CustomValue': value}`

## Troubleshooting

### General
Azure QuestionAnswering clients raise exceptions defined in [Azure Core][azure_core_readme].
When you interact with the Cognitive Language Services Question Answering client library using the .Python SDK, errors returned by the service correspond to the same HTTP status codes returned for [REST API][questionanswering_rest_docs] requests.

For example, if you submit a question to a non-existant knowledge base, a `400` error is returned indicating "Bad Request".

```python
from azure.core.exceptions import HttpResponseError

try:
    client.query_knowledgebase(
        project_name="invalid-knowledgebase",
        knowledgebase_query_parameters=params
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
headers, can be enabled on a client with the `logging_enable` argument:
```python
import sys
import logging
from azure.ai.language.questionanswering import QuestionAnsweringClient

# Create a logger for the 'azure' SDK
logger = logging.getLogger('azure')
logger.setLevel(logging.DEBUG)

# Configure a console output
handler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(handler)

# This client will log detailed information about its HTTP sessions, at DEBUG level
client = QuestionAnsweringClient(
    endpoint,
    credential,
    logging_enable=True
)
```

Similarly, `logging_enable` can enable detailed logging for a single operation,
even when it is not enabled for the client:
```python
client.query_knowledgebase(
    project_name="FAQ",
    knowledgebase_query_parameters=params,
    logging_enable=True
)
```

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
[azure_core_ref_docs]: https://azuresdkdocs.blob.core.windows.net/$web/python/azure-core/latest/azure.core.html
[azure_core_readme]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/README.md
[pip_link]:https://pypi.org/project/pip/
[questionanswering_client_class]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/cognitivelanguage/azure-ai-language-questionanswering/azure/ai/language/questionanswering/_question_answering_client.py#L27
[questionanswering_client_src]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-questionanswering/
[questionanswering_docs]: https://azure.microsoft.com/services/cognitive-services/qna-maker/
[questionanswering_docs_chat]: https://docs.microsoft.com/azure/cognitive-services/qnamaker/how-to/chit-chat-knowledge-base
[questionanswering_docs_demos]: https://azure.microsoft.com/services/cognitive-services/qna-maker/#demo
[questionanswering_docs_features]: https://azure.microsoft.com/services/cognitive-services/qna-maker/#features
[questionanswering_pypi_package]: https://pypi.org/project/azure-ai-language-questionanswering/
[questionanswering_refdocs]: https://docs.microsoft.com/python/api/overview/azure/ai-language-questionanswering-readme-pre?view=azure-python-preview
[questionanswering_rest_docs]: https://docs.microsoft.com/rest/api/cognitiveservices-qnamaker/
[questionanswering_samples]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-questionanswering/samples/README.md

![Impressions](https://azure-sdk-impressions.azurewebsites.net/api/impressions/azure-sdk-for-python%2Fsdk%2Ftemplate%2Fazure-template%2FREADME.png)
