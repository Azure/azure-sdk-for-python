# Guide for migrating to azure-ai-language-question-answering from azure-cognitiveservices-knowledge-qnamaker

This guide is intended to assist in the migration to `azure-ai-language-question-answering`. It will focus on side-by-side comparisons for similar operations between the two packages.

Familiarity with the `azure-ai-language-question-answering` package is assumed. For those new to the Key Vault client library for Python, please refer to the [README for `azure-ai-language-question-answering`][qna_readme] rather than this guide.

## Table of contents

* [Migration benefits](#migration-benefits)
* [Important changes](#important-changes)
    - [Separate packages and clients](#separate-packages-and-clients)
    - [Client constructors](#client-constructors)
    - [Async operations](#async-operations)
    - [Query a Knowledge Base](#query-a-knowledge-base)
* [Additional samples](#additional-samples)

## Migration benefits

A natural question to ask when considering whether or not to adopt a new version or library is what the benefits of doing so would be. As Azure has matured and been embraced by a more diverse group of developers, we have been focused on learning the patterns and practices to best support developer productivity and to understand the gaps that the Python client libraries have.

There were several areas of consistent feedback expressed across the Azure client library ecosystem. One of the most important is that the client libraries for different Azure services have not had a consistent approach to organization, naming, and API structure. Additionally, many developers have felt that the learning curve was difficult, and the APIs did not offer a good, approachable, and consistent onboarding story for those learning Azure or exploring a specific Azure service.

To try and improve the development experience across Azure services, a set of uniform [design guidelines][design_guidelines] was created for all languages to drive a consistent experience with established API patterns for all services. A set of [Python-specific guidelines][python_specific_guidelines] was also introduced to ensure that Python clients have a natural and idiomatic feel with respect to the Python ecosystem. Further details are available in the guidelines for those interested.

### Cross Service SDK improvements

The modern Question Answering client library also provides the ability to share in some of the cross-service improvements made to the Azure development experience, such as
- using the new [`azure-identity`][identity_readme] library to share a single authentication approach between clients
- a unified logging and diagnostics pipeline offering a common view of the activities across each of the client libraries

## Important changes

### Client constructors

Across all modern Azure client libraries, clients consistently take an endpoint or connection string along with token credentials. This differs from `QnAMakerClient`, which took an authentication delegate.

#### Authenticating

Previously in `azure-cognitiveservices-knowledge-qnamaker` you could create a `QnAMakerClient` by using `CognitiveServicesCredentials` from `msrest.authentication`:

```python
from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.knowledge.qnamaker import QnAMakerClient

client = QnAMakerClient(
    endpoint="https://<my-cognitiveservices-account>.cognitiveservices.azure.com",
    credentials=CognitiveServicesCredentials("API key")
)
```

Now in `azure-ai-language-questionanswering` you can create a `QuestionAnsweringClient` using an [`AzureKeyCredential`][[azure_key_credential]]:

```python
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.questionanswering import QuestionAnsweringClient

client = QuestionAnsweringClient(
    endpoint="https://<my-cognitiveservices-account>.cognitiveservices.azure.com",
    credential=AzureKeyCredential("API key")
)
```

### Async operations

The modern `azure-ai-language-question-answering` library includes a complete async API supported on Python 3.6+. To use it, you must first install an async transport, such as [aiohttp][aiohttp]. See [azure-core documentation][azure_core_transport] for more information.

Async operations are available on async clients, which should be closed when they're no longer needed. Each async client is an async context manager and defines an async `close` method. For example:

```python
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.questionanswering import QuestionAnsweringClient

endpoint = "https://<my-cognitiveservices-account>.cognitiveservices.azure.com"
credential = AzureKeyCredential("API key")

# call close when the client is no longer needed
client = QuestionAnsweringClient(endpoint=endpoint, credential=credential)
...
await client.close()

# alternatively, use the client as an async context manager
async with QuestionAnsweringClient(endpoint=endpoint, credential=credential) as client:
    ...
```

### Query a Knowledge Base

In `azure-cognitiveservices-knowledge-qnamaker`, you would have to import and create a model
to query a knowledge base.

```python
from azure.cognitiveservices.knowledge.qnamaker.models import QueryDTO

generate_answer_payload = QueryDTO(
    question="How long should my Surface battery last?",
)

response = client.generate_answer(
    kb_id="<my-knowledge-base-id>",
    generate_answer_payload=generate_answer_payload,
)
best_answers = [a for a in response.answers if a.score > 0.9]
```

The modern `azure-ai-language-questionanswering` has overloads for body input.
You can either:

1. Import and create a model and pass it in as a positional parameter
2. Create a JSON dict and pass it in as a positional parameter
3. Pass in arguments directly to the method with keyword arguments.

In this sample, we will show how to pass in the arguments as keyword arguments.

```python
response = client.query_knowledge_base(
    question="How long should my Surface battery last?",
    project_name="<my-qna-project-name>",
    deployment_name="<my-qna-deployment-name>"
)
best_answers = [a for a in response.answers if a.confidence_score > 0.9]
```

## Additional Samples

The new `azure-ai-language-questionanswering` has new capability not supported by the old SDK, you can
see the additional samples [here][qna_samples].

<!--LINKS-->
[qna_readme]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/cognitivelanguage/azure-ai-language-questionanswering/README.md
[design_guidelines]: https://azure.github.io/azure-sdk/python/guidelines/index.html
[python_specific_guidelines]: https://azure.github.io/azure-sdk/python_design.html
[identity_readme]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/identity/azure-identity/README.md
[azure_key_credential]: https://docs.microsoft.com/python/api/azure-core/azure.core.credentials.azurekeycredential?view=azure-python
[aiohttp]: https://pypi.org/project/aiohttp/
[azure_core_transport]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/CLIENT_LIBRARY_DEVELOPER.md#transport
[qna_samples]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-questionanswering/samples
