# Guide for migrating to azure-ai-language-questionanswering from azure-cognitiveservices-knowledge-qnamaker

This guide is intended to assist in the migration to [azure-ai-language-questionanswering](https://pypi.org/project/azure-ai-language-questionanswering/) from the old one [azure-cognitiveservices-knowledge-qnamaker](https://pypi.org/project/azure-cognitiveservices-knowledge-qnamaker/). It will focus on side-by-side comparisons for similar operations between the two packages.

Familiarity with the `azure-cognitiveservices-knowledge-qnamaker` package is assumed. For those new to the Question Answering client library for Python, please refer to the [README for azure-ai-language-questionanswering][qna_readme] rather than this guide.

## Table of contents
  - [Migration benefits](#migration-benefits)
  - [General changes](#general-changes)
    - [Package and namespaces](#package-and-namespaces)
    - [Runtime Client](#runtime-client)
      - [Authenticating runtime client](#authenticating-runtime-client)
      - [Querying a question](#querying-a-question)
      - [Chatting](#chatting)
    - [Authoring Client](#authoring-client)
      - [Authenticating authoring client](#authenticating-authoring-client)
      - [Creating knowledge base](#creating-knowledge-base)
      - [Updating knowledge base](#updating-knowledge-base)
      - [Exporting knowledge base](#exporting-knowledge-base)
      - [Deleting knowledge base](#deleting-knowledge-base)
  - [Async operations](#async-operations)
  - [Additional Samples](#additional-samples)

## Migration benefits

A natural question to ask when considering whether or not to adopt a new version or library is what the benefits of doing so would be. As Azure has matured and been embraced by a more diverse group of developers, we have been focused on learning the patterns and practices to best support developer productivity and to understand the gaps that the Python client libraries have.

There were several areas of consistent feedback expressed across the Azure client library ecosystem. One of the most important is that the client libraries for different Azure services have not had a consistent approach to organization, naming, and API structure. Additionally, many developers have felt that the learning curve was difficult, and the APIs did not offer a good, approachable, and consistent onboarding story for those learning Azure or exploring a specific Azure service.

To try and improve the development experience across Azure services, a set of uniform [design guidelines][design_guidelines] was created for all languages to drive a consistent experience with established API patterns for all services. A set of [Python-specific guidelines][python_specific_guidelines] was also introduced to ensure that Python clients have a natural and idiomatic feel with respect to the Python ecosystem. Further details are available in the guidelines for those interested.

## General changes

The modern Question Answering client library provides the ability to share in some of the cross-service improvements made to the Azure development experience, such as
- using the new [azure-identity][identity_readme] library to share a single authentication approach between clients
- a unified logging and diagnostics pipeline offering a common view of the activities across each of the client libraries

### Package and namespaces

Package names and the namespace root for the modern Azure Cognitive Services client libraries for Python have changed. Each will follow the pattern `azure.ai.[services]` where the legacy clients followed the pattern `azure.cognitiveservices.[services]`. This provides a quick and accessible means to help understand, at a glance, whether you are using the modern or legacy clients.

In the case of Question Answering, the modern client libraries have packages and namespaces that begin with `azure.ai.language.questionanswering` and were released beginning with version 1. The legacy client libraries have packages and namespaces that begin with `azure.cognitiveservices.knowledge.qnamaker` and a version of 0.3.0 or below.

### Runtime Client

#### Authenticating runtime client

Previously in `azure-cognitiveservices-knowledge-qnamaker` you could create a `QnAMakerClient` by using `CognitiveServicesCredentials` from `msrest.authentication`:

```python
from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.knowledge.qnamaker import QnAMakerClient

client = QnAMakerClient(
    endpoint="https://<my-cognitiveservices-account>.cognitiveservices.azure.com",
    credentials=CognitiveServicesCredentials("API key")
)
```

Now in `azure-ai-language-questionanswering` you can create a `QuestionAnsweringClient` using an [AzureKeyCredential][azure_key_credential] or a token credential from the [azure-identity](https://pypi.org/project/azure-identity/) library:

```python
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.questionanswering import QuestionAnsweringClient

client = QuestionAnsweringClient(
    endpoint="https://<my-cognitiveservices-account>.cognitiveservices.azure.com",
    credential=AzureKeyCredential("API key")
)
```

```python
from azure.identity import DefaultAzureCredential
from azure.ai.language.questionanswering import QuestionAnsweringClient

client = QuestionAnsweringClient(
    endpoint="https://<my-cognitiveservices-account>.cognitiveservices.azure.com",
    credential=DefaultAzureCredential()
)
```

#### Querying a question

In `azure-cognitiveservices-knowledge-qnamaker`, you could query for a question using `QueryDTO`:

```python
from azure.cognitiveservices.knowledge.qnamaker.models import QueryDTO
from azure.cognitiveservices.knowledge.qnamaker import QnAMakerClient

client = QnAMakerClient(endpoint, credentials)

generate_answer_payload = QueryDTO(
    question="How long should my Surface battery last?",
)

response = client.knowledgebase.generate_answer(
    kb_id="<my-knowledge-base-id>",
    generate_answer_payload=generate_answer_payload,
)
best_answers = [a for a in response.answers if a.score > 0.9]
```

In the modern `azure-ai-language-questionanswering`, you use `get_answers`:

```python
from azure.ai.language.questionanswering import QuestionAnsweringClient

client = QuestionAnsweringClient(endpoint=endpoint, credential=credential)

response = client.get_answers(
    question="How long should my Surface battery last?",
    project_name="<my-qna-project-name>",
    deployment_name="<my-qna-deployment-name>"
)
best_answers = [a for a in response.answers if a.confidence_score > 0.9]
```

#### Chatting

Previously in `azure-cognitiveservices-knowledge-qnamaker`, you could chat using `QueryDTO` along with setting the context to have `previous_qna_id`:

```python
from azure.cognitiveservices.knowledge.qnamaker.models import QueryDTO, QueryDTOContext
from azure.cognitiveservices.knowledge.qnamaker import QnAMakerClient

client = QnAMakerClient(endpoint, credentials)

generate_answer_payload = QueryDTO(
    question="How long should my Surface battery last?",
    context=QueryDTOContext(previous_qna_id=1)
)

response = client.knowledgebase.generate_answer(
    kb_id="<my-knowledge-base-id>",
    generate_answer_payload=generate_answer_payload,
)
best_answers = [a for a in response.answers if a.score > 0.9]
```

Now in `azure-ai-language-questionanswering`, you use `KnowledgeBaseAnswerContext`  to set `project_name`, `deployment_name`, and `question` along with setting the `answer_context` to have `previous_qna_id`:


```python
from azure.ai.language.questionanswering import QuestionAnsweringClient
from azure.ai.language.questionanswering.models import KnowledgeBaseAnswerContext

client = QuestionAnsweringClient(endpoint=endpoint, credential=credential)

response = client.get_answers(
    question="How long should my Surface battery last?",
    project_name="<my-qna-project-name>",
    deployment_name="<my-qna-deployment-name>",
    answer_context=KnowledgeBaseAnswerContext(
        previous_qna_id=1
    )
)

best_answers = [a for a in response.answers if a.confidence_score > 0.9]
```

### Authoring Client

#### Authenticating authoring client

Previously in `azure-cognitiveservices-knowledge-qnamaker` you could create a `QnAMakerClient` by using `CognitiveServicesCredentials` from `msrest.authentication`:

```python
from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.knowledge.qnamaker import QnAMakerClient

client = QnAMakerClient(
    endpoint="https://<my-cognitiveservices-account>.cognitiveservices.azure.com",
    credentials=CognitiveServicesCredentials("API key")
)
```

Now in `azure-ai-language-questionanswering` you can create a `AuthoringClient` using an [AzureKeyCredential][azure_key_credential] or a token credential from the [azure-identity](https://pypi.org/project/azure-identity/) library:

```python
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.questionanswering.authoring import AuthoringClient

client = AuthoringClient(
    endpoint="https://<my-cognitiveservices-account>.cognitiveservices.azure.com",
    credential=AzureKeyCredential("API key")
)
```

```python
from azure.identity import DefaultAzureCredential
from azure.ai.language.questionanswering.authoring import AuthoringClient

client = AuthoringClient(
    endpoint="https://<my-cognitiveservices-account>.cognitiveservices.azure.com",
    credential=DefaultAzureCredential()
)
```

#### Creating knowledge base

Previously in `azure-cognitiveservices-knowledge-qnamaker`, you could create a new knowledgebase using a `CreateKbDTO`:

```python
import time
from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.knowledge.qnamaker.models import CreateKbDTO, QnADTO
from azure.cognitiveservices.knowledge.qnamaker import QnAMakerClient

client = QnAMakerClient(
    endpoint="https://<my-cognitiveservices-account>.cognitiveservices.azure.com",
    credentials=CognitiveServicesCredentials("API key")
)

operation = client.knowledgebase.create(
    create_kb_payload=CreateKbDTO(
        name="<knowledgebase-name>",
        qna_list=[
            QnADTO(
                questions=["questions"],
                answer="answer"
            )
        ]
        
    )
)
for i in range(20):
    if operation.operation_state in ["NotStarted", "Running"]:
        print("Waiting for operation: {} to complete.".format(operation.operation_id))
        time.sleep(5)
        operation = client.operations.get_details(operation_id=operation.operation_id)
    else:
        break

if operation.operation_state != "Succeeded":
    raise Exception("Operation {} failed to complete.".format(operation.operation_id))

# Get knowledge base ID from resourceLocation HTTP header
knowledge_base_id = operation.resource_location.replace("/knowledgebases/", "")
print("Created KB with ID: {}".format(knowledge_base_id))
```

Now in `azure-ai-language-questionanswering`, you can create a new Question Answering project by passing a `dict` with the needed project creation properties:

```python
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.questionanswering.authoring import AuthoringClient

client = AuthoringClient(
    endpoint="https://<my-cognitiveservices-account>.cognitiveservices.azure.com",
    credential=AzureKeyCredential("API key")
)

project = client.create_project(
    project_name="<project_name>",
    options={
        "description": "This is the description for a test project",
        "language": "en",
        "multilingualResource": True,
        "settings": {
            "defaultAnswer": "no answer"
        }
    })

print(f"Project name: {project['projectName']}")
print(f"language: {project['language']}")
print(f"description: {project['description']}")
```

#### Updating knowledge base

Previously in `azure-cognitiveservices-knowledge-qnamaker`, you could update your knowledge base using a `UpdateKbOperationDTO`:

```python
import time
from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.knowledge.qnamaker.models import UpdateKbOperationDTO, UpdateKbOperationDTOAdd, QnADTO
from azure.cognitiveservices.knowledge.qnamaker import QnAMakerClient

client = QnAMakerClient(
    endpoint="https://<my-cognitiveservices-account>.cognitiveservices.azure.com",
    credentials=CognitiveServicesCredentials("API key")
)

operation = client.knowledgebase.update(
    kb_id="<knowledgebase-id>",
    update_kb=UpdateKbOperationDTO(
        add=UpdateKbOperationDTOAdd(
            qna_list=[
                QnADTO(
                    questions=["questions"],
                    answer="answer"
                )
            ]
        )   
    )
)
for i in range(20):
    if operation.operation_state in ["NotStarted", "Running"]:
        print("Waiting for operation: {} to complete.".format(operation.operation_id))
        time.sleep(5)
        operation = client.operations.get_details(operation_id=operation.operation_id)
    else:
        break

if operation.operation_state != "Succeeded":
    raise Exception("Operation {} failed to complete.".format(operation.operation_id))

# Get knowledge base ID from resourceLocation HTTP header
knowledge_base_id = operation.resource_location.replace("/knowledgebases/", "")
print("Created KB with ID: {}".format(knowledge_base_id))
```

Now in `azure-ai-language-questionanswering`, you can update your knowledge source using the `begin_update_sources` method:

```python
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.questionanswering.authoring import AuthoringClient

client = AuthoringClient(
    endpoint="https://<my-cognitiveservices-account>.cognitiveservices.azure.com",
    credential=AzureKeyCredential("API key")
)

sources_poller = client.begin_update_sources(
    project_name="<project_name>",
    sources=[{
        "op": "add",
        "value": {
            "displayName": "MicrosoftFAQ",
            "source": "https://www.microsoft.com/en-in/software-download/faq",
            "sourceUri": "https://www.microsoft.com/en-in/software-download/faq",
            "sourceKind": "url",
            "contentStructureKind": "unstructured",
            "refresh": False
        }
    }]
)
sources = sources_poller.result()

for item in sources:
    print(f"source name: {item.get('displayName', 'N/A')}")
    print(f"\tsource: {item['source']}")
    print(f"\tsource uri: {item.get('sourceUri', 'N/A')}")
    print(f"\tsource kind: {item['sourceKind']}")
```

You can also update a project's questions and answers directly as follows:

```python
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.questionanswering.authoring import AuthoringClient

client = AuthoringClient(
    endpoint="https://<my-cognitiveservices-account>.cognitiveservices.azure.com",
    credential=AzureKeyCredential("API key")
)

qna_poller = client.begin_update_qnas(
    project_name="<project_name>",
    qnas=[{
        "op": "add",
        "value": {
            "questions": [
                "What is the easiest way to use Azure services in my Python project?"
            ],
            "answer": "Using the Azure SDKs"
        }
    }]
)

qnas = qna_poller.result()

for item in qnas:
    print(f"qna: {item['id']}")
    print("\tquestions:")
    for question in item["questions"]:
        print(f"\t\t{question}")
    print(f"\tanswer: {item['answer']}")
```

#### Exporting knowledge base

Previously in `azure-cognitiveservices-knowledge-qnamaker`, you could download your knowledge base using the `download` method:

```python
from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.knowledge.qnamaker import QnAMakerClient

client = QnAMakerClient(
    endpoint="https://<my-cognitiveservices-account>.cognitiveservices.azure.com",
    credentials=CognitiveServicesCredentials("API key")
)

data = client.knowledgebase.download(
    kb_id="<knowledgebase-id>",
    environment="Test",
)
print(data.qna_documents)
```

Now you can export your Question Answering project:


```python
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.questionanswering.authoring import AuthoringClient

client = AuthoringClient(
    endpoint="https://<my-cognitiveservices-account>.cognitiveservices.azure.com",
    credential=AzureKeyCredential("API key")
)

export_poller = client.begin_export(
    project_name="<project_name>",
    file_format="json"
)
export_result = export_poller.result()
export_url = export_result["resultUrl"]
```

#### Deleting knowledge base

Previously in `azure-cognitiveservices-knowledge-qnamaker`, you could delete your knowledge base using the `delete` method:

```python
from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.knowledge.qnamaker import QnAMakerClient

client = QnAMakerClient(
    endpoint="https://<my-cognitiveservices-account>.cognitiveservices.azure.com",
    credentials=CognitiveServicesCredentials("API key")
)

client.knowledgebase.delete(
    kb_id="<knowledgebase-id>"
)
```

Now in `azure-ai-language-questionanswering`, you can delete a project using the `begin_delete_project` method:

```python
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.questionanswering.authoring import AuthoringClient

client = AuthoringClient(
    endpoint="https://<my-cognitiveservices-account>.cognitiveservices.azure.com",
    credential=AzureKeyCredential("API key")
)

delete_poller = client.begin_delete_project(
    project_name="<project_name>",
)
delete_poller.result()
```

## Async operations

The modern `azure-ai-language-questionanswering` library includes a complete set of async APIs. To use it, you must first install an async transport, such as [aiohttp][aiohttp]. See [azure-core documentation][azure_core_transport] for more information.

Async operations are available on async clients, which should be closed when they're no longer needed. Each async client is an async context manager and defines an async `close` method. For example:

```python
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.questionanswering.aio import QuestionAnsweringClient

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


## Additional Samples

The new `azure-ai-language-questionanswering` has new capabilities not supported by the old client library, you can
see additional samples [here][qna_samples].

<!--LINKS-->
[qna_readme]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/cognitivelanguage/azure-ai-language-questionanswering/README.md
[design_guidelines]: https://azure.github.io/azure-sdk/python/guidelines/index.html
[python_specific_guidelines]: https://azure.github.io/azure-sdk/python_design.html
[identity_readme]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/identity/azure-identity/README.md
[azure_key_credential]: https://learn.microsoft.com/python/api/azure-core/azure.core.credentials.azurekeycredential?view=azure-python
[aiohttp]: https://pypi.org/project/aiohttp/
[azure_core_transport]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/CLIENT_LIBRARY_DEVELOPER.md#transport
[qna_samples]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-questionanswering/samples
