[![Build Status](https://dev.azure.com/azure-sdk/public/_apis/build/status/azure-sdk-for-python.client?branchName=main)](https://dev.azure.com/azure-sdk/public/_build/latest?definitionId=46?branchName=main)

# Azure Conversation Authoring client library for Python

**Conversation Authoring** is part of the Conversational Language Understanding (CLU) service. It provides APIs and SDKs to **create, manage, train, evaluate, and deploy** conversation projects and models. With the `ConversationAuthoringClient`, you can script everything you’d otherwise do in Language Studio, including:

- **Project management**: Create, update, export, and import projects.  
- **Training jobs**: Start, monitor, and cancel model training jobs.  
- **Evaluation**: Retrieve model evaluation summaries and per-utterance results.  
- **Deployments**: Create, update, swap, and delete deployments.  
- **Snapshots**: Load a trained model snapshot back into a project.  
- **Resource assignment**: Assign or unassign Azure resources to a deployment.  

[Source code][conversation_authoring_client_src]
| [Package (PyPI)][conversation_authoring_pypi_package]
| [API reference documentation][api_reference_authoring]
| [Samples][conversation_authoring_samples]
| [Product documentation][conversation_authoring_docs]
| [REST API documentation][conversation_authoring_restdocs]

## Getting started

### Prerequisites

* Python 3.7 or later is required to use this package.
* An [Azure subscription][azure_subscription]
* A [Language service resource][language_resource]

### Install the package

Install the Azure Conversation Authoring client library for Python with [pip][pip_link]:

```bash
pip install azure-ai-language-conversations-authoring
```

> Note: This version of the client library defaults to the 2025-11-15-preview version of the service

This table shows the relationship between SDK versions and supported API versions of the service

| SDK version  | Supported API version of service  |
| ------------ | --------------------------------- |
| 1.0.0b4 - Latest preview release | 2023-04-01, 2025-11-01, 2025-05-15-preview, 2025-11-15-preview (default) |
| 1.0.0b3 | 2023-04-01, 2025-11-01, 2025-05-15-preview, 2025-11-15-preview (default) |
| 1.0.0b2 | 2023-04-01, 2025-05-15-preview, 2025-11-15-preview (default) |
| 1.0.0b1 | 2023-04-01, 2024-11-15-preview, 2025-05-15-preview (default) |

### Authenticate the client

To interact with the Conversation Authoring service, you'll need to create an instance of the `ConversationAuthoringClient`. You will need an **endpoint** and an **API key** to instantiate a client object. For more information regarding authenticating with Cognitive Services, see [Authenticate requests to Azure Cognitive Services][cognitive_auth].

#### Get an API key

You can get the **endpoint** and **API key** from your Cognitive Services resource in the [Azure Portal][azure_portal].

Alternatively, use the [Azure CLI][azure_cli] command shown below to get the API key from the Cognitive Service resource:

```powershell
az cognitiveservices account keys list --resource-group <resource-group-name> --name <resource-name>
```


#### Create ConversationAuthoringClient

Once you've determined your **endpoint** and **API key**, you can instantiate a `ConversationAuthoringClient`:

```python
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.conversations.authoring import ConversationAuthoringClient

endpoint = "https://<my-custom-subdomain>.cognitiveservices.azure.com/"
credential = AzureKeyCredential("<api-key>")
client = ConversationAuthoringClient(endpoint, credential)
```

#### Create a client with an Azure Active Directory Credential

To use an [Azure Active Directory (AAD) token credential][cognitive_authentication_aad],  
provide an instance of the desired credential type obtained from the [azure-identity][azure_identity_credentials] library.

> Note: Regional endpoints do not support AAD authentication.  
> You must create a [custom subdomain][custom_subdomain] for your resource in order to use this type of authentication.

Authentication with AAD requires some initial setup:

- [Install azure-identity][install_azure_identity]  
- [Register a new AAD application][register_aad_app]  
- [Grant access][grant_role_access] to the Language service by assigning the **Cognitive Services Language Owner** role to your service principal  

After setup, you can choose which type of [credential][azure_identity_credentials] to use.  
As an example, [DefaultAzureCredential][default_azure_credential] can be used to authenticate the client:

Set the values of the client ID, tenant ID, and client secret of the AAD application as environment variables:  
`AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_CLIENT_SECRET`

Use the returned token credential to authenticate the client:

```python
from azure.ai.language.conversations.authoring import ConversationAuthoringClient
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()
client = ConversationAuthoringClient(
    endpoint="https://<my-custom-subdomain>.cognitiveservices.azure.com/",
    credential=credential,
)
```

## Key concepts

### ConversationAuthoringClient

The `ConversationAuthoringClient` is the primary entry point for interacting with the Conversation Authoring service.  
It provides top-level APIs to **manage projects** (create, delete, list) and retrieve **project-scoped clients**.

You can call `get_project_client(project_name)` to obtain a `ConversationAuthoringProjectClient`, which exposes operations specific to a given project.

For asynchronous operations, an async version of the client is available in the `azure.ai.language.conversations.authoring.aio` namespace.

### ConversationAuthoringProjectClient

The `ConversationAuthoringProjectClient` is a **project-scoped client** returned by `ConversationAuthoringClient.get_project_client(project_name)`.  

It organizes project functionality into operation groups:

- **deployment** → [`DeploymentOperations`]: manage deployments (create, update, delete, swap).  
- **exported_model** → [`ExportedModelOperations`]: handle exported model operations.  
- **project** → [`ProjectOperations`]: manage project-level operations (train, import/export, cancel jobs, assign resources).  
- **trained_model** → [`TrainedModelOperations`]: interact with trained models (evaluation, snapshots, delete models).  

This separation ensures you can focus on project-level actions while still using the main `ConversationAuthoringClient` for higher-level management.

## Examples

The `azure-ai-language-conversations-authoring` client library provides both **synchronous** and **asynchronous** APIs.

The following examples show common **Conversation Authoring** scenarios using the `ConversationAuthoringClient` or `ConversationAuthoringProjectClient` (created above).

### Create a Conversation Project

<!-- SNIPPET:sample_create_project.conversation_authoring_create_project -->

```python
import os
from azure.identity import DefaultAzureCredential
from azure.ai.language.conversations.authoring import ConversationAuthoringClient
from azure.ai.language.conversations.authoring.models import (
    CreateProjectOptions,
    ProjectKind,
)


def sample_create_project():
    # settings
    endpoint = os.environ["AZURE_CONVERSATIONS_AUTHORING_ENDPOINT"]
    project_name = os.environ.get("PROJECT_NAME", "<project-name>")

    # create a client with AAD
    credential = DefaultAzureCredential()
    client = ConversationAuthoringClient(endpoint, credential=credential)

    # build project definition
    body = CreateProjectOptions(
        project_kind=ProjectKind.CONVERSATION,
        project_name=project_name,
        language="<language-tag>",  # e.g. "en-us"
        multilingual=True,
        description="Sample project created via Python SDK",
    )

    # create project
    result = client.create_project(project_name=project_name, body=body)

    # print project details (direct attribute access; no getattr)
    print("=== Create Project Result ===")
    print(f"Project Name: {result.project_name}")
    print(f"Language: {result.language}")
    print(f"Kind: {result.project_kind}")
    print(f"Multilingual: {result.multilingual}")
    print(f"Description: {result.description}")
```

<!-- END SNIPPET -->

### Import a Project

<!-- SNIPPET:sample_import_project.conversation_authoring_import_project -->

```python
import os
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import HttpResponseError
from azure.ai.language.conversations.authoring import ConversationAuthoringClient
from azure.ai.language.conversations.authoring.models import (
    ConversationExportedIntent,
    ConversationExportedEntity,
    ConversationExportedUtterance,
    ExportedUtteranceEntityLabel,
    ConversationExportedProjectAsset,
    CreateProjectOptions,
    ProjectKind,
    ProjectSettings,
    ExportedProject,
    ExportedProjectFormat,
)


def sample_import_project():
    # settings
    endpoint = os.environ["AZURE_CONVERSATIONS_AUTHORING_ENDPOINT"]
    project_name = os.environ.get("PROJECT_NAME", "<project-name>")

    # create a client with AAD
    credential = DefaultAzureCredential()
    client = ConversationAuthoringClient(endpoint, credential=credential)
    project_client = client.get_project_client(project_name)

    # ----- Build assets using objects -----
    intents = [
        ConversationExportedIntent(category="<intent-a>"),
        ConversationExportedIntent(category="<intent-b>"),
    ]

    entities = [
        ConversationExportedEntity(
            category="<entity-a>",
            composition_mode="combineComponents",
        )
    ]

    u1 = ConversationExportedUtterance(
        text="<utterance-1>",
        intent="<intent-b>",
        language="<language-tag>",  # e.g., "en-us"
        dataset="Train",
        entities=[ExportedUtteranceEntityLabel(category="<entity-a>", offset=0, length=5)],
    )

    u2 = ConversationExportedUtterance(
        text="<utterance-2>",
        intent="<intent-b>",
        language="<language-tag>",
        dataset="Train",
        entities=[ExportedUtteranceEntityLabel(category="<entity-a>", offset=0, length=5)],
    )

    u3 = ConversationExportedUtterance(
        text="<utterance-3>",
        intent="<intent-b>",
        language="<language-tag>",
        dataset="Train",
        entities=[ExportedUtteranceEntityLabel(category="<entity-a>", offset=0, length=4)],
    )

    assets = ConversationExportedProjectAsset(
        intents=intents,
        entities=entities,
        utterances=[u1, u2, u3],
    )

    metadata = CreateProjectOptions(
        project_kind=ProjectKind.CONVERSATION,
        project_name=project_name,  # required
        language="<language-tag>",  # required (e.g., "en-us")
        settings=ProjectSettings(confidence_threshold=0.0),
        multilingual=False,
        description="",
    )

    exported_project = ExportedProject(
        project_file_version="<project-file-version>",  # e.g., "2025-05-15-preview"
        string_index_type="Utf16CodeUnit",
        metadata=metadata,
        assets=assets,
    )

    # ----- begin import (long-running operation) -----
    poller = project_client.project.begin_import(
        body=exported_project,
        exported_project_format=ExportedProjectFormat.CONVERSATION,
    )

    try:
        poller.result()
        print("Import completed.")
        print(f"done: {poller.done()}")
        print(f"status: {poller.status()}")
    except HttpResponseError as e:
        print(f"Operation failed: {e.message}")
        print(e.error)
```

<!-- END SNIPPET -->

### Train a Model

<!-- SNIPPET:sample_train.conversation_authoring_train -->

```python
import os
from azure.identity import DefaultAzureCredential
from azure.ai.language.conversations.authoring import ConversationAuthoringClient
from azure.ai.language.conversations.authoring.models import (
    TrainingJobDetails,
    TrainingMode,
    EvaluationDetails,
    EvaluationKind,
)


def sample_train():
    # settings
    endpoint = os.environ["AZURE_CONVERSATIONS_AUTHORING_ENDPOINT"]
    project_name = os.environ.get("PROJECT_NAME", "<project-name>")

    # create a client with AAD
    credential = DefaultAzureCredential()
    client = ConversationAuthoringClient(endpoint, credential=credential)
    project_client = client.get_project_client(project_name)

    # build training request
    training_job_details = TrainingJobDetails(
        model_label="<model-label>",
        training_mode=TrainingMode.STANDARD,
        training_config_version="<config-version>",
        evaluation_options=EvaluationDetails(
            kind=EvaluationKind.PERCENTAGE,
            testing_split_percentage=20,
            training_split_percentage=80,
        ),
    )

    # start training job (long-running operation)
    poller = project_client.project.begin_train(body=training_job_details)

    # wait for job completion and get the result (no explicit type variables)
    result = poller.result()

    # print result details
    print("=== Training Result ===")
    print(f"Model Label: {result.model_label}")
    print(f"Training Config Version: {result.training_config_version}")
    print(f"Training Mode: {result.training_mode}")
    print(f"Training Status: {result.training_status}")
    print(f"Data Generation Status: {result.data_generation_status}")
    print(f"Evaluation Status: {result.evaluation_status}")
    print(f"Estimated End: {result.estimated_end_on}")
```

<!-- END SNIPPET -->

## Optional Configuration

Optional keyword arguments can be passed in at the client and per-operation level. The azure-core [reference documentation][azure_core_ref_docs] describes available configurations for retries, logging, transport protocols, and more.

## Troubleshooting

### General

The Conversation Authoring client will raise exceptions defined in [Azure Core][azure_core_exceptions].  
These exceptions provide consistent error handling across Azure SDK libraries.

### Logging

This library uses Python’s built-in [logging][python_logging] module for diagnostic logging.  

- Basic information about HTTP requests (URLs, headers) is logged at **INFO** level.  
- Detailed request/response information (including bodies and unredacted headers) is logged at **DEBUG** level.  

You can enable logging when constructing the client by passing `logging_enable=True`.

```python
import sys
import logging
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.conversations.authoring import ConversationAuthoringClient

# Configure logger
logger = logging.getLogger("azure")
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(handler)

endpoint = "https://<endpoint>.cognitiveservices.azure.com/"
credential = AzureKeyCredential("<api-key>")

# This client will log detailed HTTP information
client = ConversationAuthoringClient(endpoint, credential, logging_enable=True)
```

Similarly, `logging_enable` can enable detailed logging for a single operation, even when it isn't enabled for the client:

```python
result = client.create_project(
    project_name="<project-name>",
    body={...},
    logging_enable=True,
)
```

## Next steps

### More sample code

See the [Sample README][conversation_authoring_samples] for additional examples that demonstrate common Conversation Authoring workflows such as:

- Creating and managing projects  
- Importing and exporting project assets  
- Training models and retrieving evaluation results  
- Deploying and swapping models  
- Assigning or unassigning resources  
- Loading snapshots and managing trained models  

---

## Contributing

See the [CONTRIBUTING.md][contributing] guide for details on building, testing, and contributing to this library.

This project welcomes contributions and suggestions. Most contributions require you to agree to a Contributor License Agreement (CLA), declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit [cla.microsoft.com][cla].

When you submit a pull request, a CLA bot will automatically determine whether you need to provide a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repositories using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct][code_of_conduct].  
For more information, see the [Code of Conduct FAQ][coc_faq] or contact [opencode@microsoft.com][coc_contact] with any additional questions.

---

<!-- LINKS -->
[azure_cli]: https://learn.microsoft.com/cli/azure/
[azure_portal]: https://portal.azure.com/
[azure_subscription]: https://azure.microsoft.com/free/
[language_resource]: https://portal.azure.com/#create/Microsoft.CognitiveServicesTextAnalytics
[cla]: https://cla.microsoft.com
[coc_contact]: mailto:opencode@microsoft.com
[coc_faq]: https://opensource.microsoft.com/codeofconduct/faq/
[code_of_conduct]: https://opensource.microsoft.com/codeofconduct/
[cognitive_auth]: https://learn.microsoft.com/azure/cognitive-services/authentication/
[contributing]: https://github.com/Azure/azure-sdk-for-python/blob/main/CONTRIBUTING.md
[python_logging]: https://docs.python.org/3/library/logging.html
[sdk_logging_docs]: https://learn.microsoft.com/azure/developer/python/azure-sdk-logging
[azure_core_ref_docs]: https://azuresdkdocs.z19.web.core.windows.net/python/azure-core/latest/azure.core.html
[azure_core_exceptions]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/README.md
[pip_link]: https://pypi.org/project/pip/
[conversation_authoring_client_src]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations-authoring
[conversation_authoring_pypi_package]: https://pypi.org/project/azure-ai-language-conversations-authoring/
[conversation_authoring_samples]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations-authoring/samples/README.md
[conversation_authoring_docs]: https://learn.microsoft.com/azure/ai-services/language-service/conversational-language-understanding/overview
[api_reference_authoring]: https://azuresdkdocs.z19.web.core.windows.net/python/azure-ai-language-conversations-authoring/latest/azure.ai.language.conversations.authoring.html
[conversation_authoring_restdocs]: https://learn.microsoft.com/rest/api/language/analyze-conversations-authoring/conversation-authoring-project?view=rest-language-analyze-conversations-authoring-2025-11-01
[azure_language_portal]: https://language.cognitive.azure.com/home
[cognitive_authentication_aad]: https://learn.microsoft.com/azure/cognitive-services/authentication#authenticate-with-azure-active-directory
[azure_identity_credentials]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity#credentials
[custom_subdomain]: https://learn.microsoft.com/azure/cognitive-services/authentication#create-a-resource-with-a-custom-subdomain
[install_azure_identity]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity#install-the-package
[register_aad_app]: https://learn.microsoft.com/azure/cognitive-services/authentication#assign-a-role-to-a-service-principal
[grant_role_access]: https://learn.microsoft.com/azure/cognitive-services/authentication#assign-a-role-to-a-service-principal
[default_azure_credential]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity#defaultazurecredential