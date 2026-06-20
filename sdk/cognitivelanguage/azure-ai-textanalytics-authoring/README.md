[![Build Status](https://dev.azure.com/azure-sdk/public/_apis/build/status/azure-sdk-for-python.client?branchName=main)](https://dev.azure.com/azure-sdk/public/_build/latest?definitionId=46?branchName=main)

# Azure Text Authoring client library for Python

**Text Authoring** is part of Azure AI Language. It provides APIs and SDKs to **create, manage, train, evaluate, and deploy** text projects and models (for example, custom single/multi-label classification). With the `TextAuthoringClient`, you can automate much of what you’d otherwise do in Language Studio, including:

- **Project management**: Create, update, export, and import projects.  
- **Training jobs**: Start, monitor, and cancel model training jobs.  
- **Evaluation**: Retrieve model evaluation summaries and document-level results.  
- **Deployments**: Create, update, swap, and delete deployments.  
- **Snapshots**: Load a trained model snapshot back into a project.  
- **Resource assignment**: Assign or unassign Azure resources to a deployment.  

[Source code][text_authoring_client_src]
| [Package (PyPI)][text_authoring_pypi_package]
| [API reference][api_reference_authoring]
| [Samples][text_authoring_samples]
| [Product docs][text_authoring_docs]
| [REST API docs][text_authoring_restdocs]

---

## Getting started

### Prerequisites

- Python 3.7 or later  
- An [Azure subscription][azure_subscription]  
- An Azure AI [Language resource][language_resource]

### Install the package

Install the Azure Text Authoring client library for Python with [pip][pip_link]:

```bash
pip install azure-ai-textanalytics-authoring
```

> Note: This version of the client library defaults to the 2025-05-15-preview version of the service.

This table shows the relationship between SDK versions and supported API versions of the service

| SDK version  | Supported API version of service  |
| ------------ | --------------------------------- |
| 1.0.0b1 - Latest preview release | 2023-04-01, 2024-11-15-preview, 2025-05-15-preview (default) |

### Authenticate the client

To interact with the Text Authoring service, you'll need to create an instance of the `TextAuthoringClient`. You will need an **endpoint** and an **API key** to instantiate a client object. For more information regarding authenticating with Cognitive Services, see [Authenticate requests to Azure Cognitive Services][cognitive_auth].

#### Get an API key

You can get the **endpoint** and **API key** from your Cognitive Services resource in the [Azure Portal][azure_portal].

Alternatively, use the [Azure CLI][azure_cli] command shown below to get the API key from the Cognitive Service resource:

```powershell
az cognitiveservices account keys list --resource-group <resource-group-name> --name <resource-name>
```

#### Create a TextAuthoringClient with an Azure Active Directory Credential

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
from azure.ai.textanalytics.authoring import TextAuthoringClient
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()
client = TextAuthoringClient(
    endpoint="https://<my-custom-subdomain>.cognitiveservices.azure.com/",
    credential=credential,
)
```

#### Create a TextAuthoringClient using AzureKeyCredential

Once you've determined your **endpoint** and **API key**, you can instantiate a `TextAuthoringClient`:

```python
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics.authoring import TextAuthoringClient

endpoint = "https://<my-custom-subdomain>.cognitiveservices.azure.com/"
credential = AzureKeyCredential("<api-key>")
client = TextAuthoringClient(endpoint, credential)
```

## Key concepts

### TextAuthoringClient

The `TextAuthoringClient` is the primary entry point for interacting with the Text Authoring service.  
It provides top-level APIs to **manage projects** (create, delete, list) and retrieve **project-scoped clients**.

You can call `get_project_client(project_name)` to obtain a `TextAuthoringProjectClient`, which exposes operations specific to a given project.

For asynchronous operations, an async version of the client is available in the `azure.ai.textanalytics.authoring.aio` namespace.

### TextAuthoringProjectClient

The `TextAuthoringProjectClient` is a **project-scoped client** returned by `TextAuthoringClient.get_project_client(project_name)`.  

It organizes project functionality into operation groups:

- **deployment** → [`DeploymentOperations`]: manage deployments (create, update, delete, swap).  
- **exported_model** → [`ExportedModelOperations`]: handle exported model operations.  
- **project** → [`ProjectOperations`]: manage project-level operations (train, import/export, cancel jobs, assign resources).  
- **trained_model** → [`TrainedModelOperations`]: interact with trained models (evaluation, snapshots, delete models).  

This separation ensures you can focus on project-level actions while still using the main `TextAuthoringClient` for higher-level management.

## Examples

The `azure-ai-textanalytics-authoring` client library provides both **synchronous** and **asynchronous** APIs.

The following examples show common **Text Authoring** scenarios using the `TextAuthoringClient` or `TextAuthoringProjectClient` (created above).

### Create a Text Project

```python
import os
from azure.identity import DefaultAzureCredential
from azure.ai.textanalytics.authoring import TextAuthoringClient
from azure.ai.textanalytics.authoring.models import (
    CreateProjectOptions,
    ProjectKind,
)


def sample_text_create_project():
    # settings
    endpoint = os.environ["AZURE_TEXT_ENDPOINT"]
    project_name = os.environ.get("PROJECT_NAME", "<project-name>")
    language_tag = os.environ.get("LANGUAGE_TAG", "<language-tag>")  # e.g., "en"
    storage_container = os.environ.get("STORAGE_INPUT_CONTAINER_NAME", "<storage-container-name>")
    description = os.environ.get("DESCRIPTION", "<description>")

    # create a client with AAD
    credential = DefaultAzureCredential()
    client = TextAuthoringClient(endpoint, credential=credential)

    # build project definition (Custom Multi-Label Classification)
    body = CreateProjectOptions(
        project_kind=ProjectKind.CUSTOM_MULTI_LABEL_CLASSIFICATION,
        storage_input_container_name=storage_container,
        project_name=project_name,
        language=language_tag,
        description=description,
        multilingual=True,
    )

    # create project
    result = client.create_project(project_name=project_name, body=body)

    # print project details (direct attribute access; no getattr)
    print("=== Create Text Authoring Project Result ===")
    print(f"Project Name: {result.project_name}")
    print(f"Language: {result.language}")
    print(f"Kind: {result.project_kind}")
    print(f"Multilingual: {result.multilingual}")
    print(f"Description: {result.description}")
    print(f"Storage Input Container: {result.storage_input_container_name}")
```

### Import a Project

```python
import os
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import HttpResponseError
from azure.ai.textanalytics.authoring import TextAuthoringClient
from azure.ai.textanalytics.authoring.models import (
    CreateProjectOptions,
    ExportedProject,
    ProjectSettings,
    ExportedCustomSingleLabelClassificationProjectAsset,
    ExportedCustomSingleLabelClassificationDocument,
    ExportedDocumentClass,
    ExportedClass,
    ProjectKind,
    StringIndexType,
)


def sample_import_project():
    # settings
    endpoint = os.environ["AZURE_TEXT_ENDPOINT"]
    project_name = os.environ.get("PROJECT_NAME", "<project-name>")
    language_tag = os.environ.get("LANGUAGE_TAG", "<language-tag>")  # e.g., "en"
    storage_container = os.environ.get("STORAGE_INPUT_CONTAINER_NAME", "<storage-container-name>")
    doc1_path = os.environ.get("DOC1_PATH", "<doc1-path>")  # e.g., "01.txt"
    doc2_path = os.environ.get("DOC2_PATH", "<doc2-path>")  # e.g., "02.txt"

    # create a client with AAD
    credential = DefaultAzureCredential()
    client = TextAuthoringClient(endpoint, credential=credential)

    # project-scoped client
    project_client = client.get_project_client(project_name)

    # ---------- Arrange metadata (project definition) ----------
    project_metadata = CreateProjectOptions(
        project_kind=ProjectKind.CUSTOM_SINGLE_LABEL_CLASSIFICATION,
        storage_input_container_name=storage_container,
        project_name=project_name,
        language=language_tag,
        description="Sample project imported via Python SDK.",
        multilingual=False,
        settings=ProjectSettings(),
    )

    # ---------- Arrange assets (classes + labeled documents) ----------
    project_assets = ExportedCustomSingleLabelClassificationProjectAsset(
        classes=[
            ExportedClass(category="ClassA"),
            ExportedClass(category="ClassB"),
            ExportedClass(category="ClassC"),
        ],
        documents=[
            ExportedCustomSingleLabelClassificationDocument(
                class_property=ExportedDocumentClass(category="ClassA"),
                location=doc1_path,
                language=language_tag,
            ),
            ExportedCustomSingleLabelClassificationDocument(
                class_property=ExportedDocumentClass(category="ClassB"),
                location=doc2_path,
                language=language_tag,
            ),
        ],
    )

    exported_project = ExportedProject(
        project_file_version="2022-05-01",
        string_index_type=StringIndexType.UTF16_CODE_UNIT,
        metadata=project_metadata,
        assets=project_assets,
    )

    # ---------- Import (LRO) with error handling ----------
    poller = project_client.project.begin_import(body=exported_project)
    try:
        poller.result()  # completes with None; raises on failure
        print("Import completed.")
        print(f"done: {poller.done()}")
        print(f"status: {poller.status()}")
    except HttpResponseError as e:
        msg = getattr(getattr(e, "error", None), "message", str(e))
        print(f"Operation failed: {msg}")
```

### Train a Model

```python
import os
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import HttpResponseError
from azure.ai.textanalytics.authoring import TextAuthoringClient
from azure.ai.textanalytics.authoring.models import (
    TrainingJobDetails,
    EvaluationDetails,
    EvaluationKind,
)


def sample_train_project():
    # settings
    endpoint = os.environ["AZURE_TEXT_ENDPOINT"]
    project_name = os.environ.get("PROJECT_NAME", "<project-name>")
    model_label = os.environ.get("MODEL_LABEL", "<model-label>")
    training_config_version = os.environ.get("TRAINING_CONFIG_VERSION", "<training-config-version>")

    # create a client with AAD
    credential = DefaultAzureCredential()
    client = TextAuthoringClient(endpoint, credential=credential)

    # project-scoped client
    project_client = client.get_project_client(project_name)

    # build training job details (80/20 split by percentage)
    training_job_details = TrainingJobDetails(
        model_label=model_label,
        training_config_version=training_config_version,
        evaluation_options=EvaluationDetails(
            kind=EvaluationKind.PERCENTAGE,
            testing_split_percentage=20,
            training_split_percentage=80,
        ),
    )

    # begin training (LRO) and handle success/error
    poller = project_client.project.begin_train(body=training_job_details)
    try:
        poller.result()  # completes with None; raises on failure
        print("Train completed.")
        print(f"done: {poller.done()}")
        print(f"status: {poller.status()}")
    except HttpResponseError as e:
        msg = getattr(getattr(e, "error", None), "message", str(e))
        print(f"Operation failed: {msg}")
```

## Optional Configuration

Optional keyword arguments can be passed in at the client and per-operation level. The azure-core [reference documentation][azure_core_ref_docs] describes available configurations for retries, logging, transport protocols, and more.

## Troubleshooting

### General

The Text Authoring client will raise exceptions defined in [Azure Core][azure_core_exceptions].  
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
from azure.ai.textanalytics.authoring import TextAuthoringClient

# Configure logger
logger = logging.getLogger("azure")
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(handler)

endpoint = "https://<endpoint>.cognitiveservices.azure.com/"
credential = DefaultAzureCredential()

# This client will log detailed HTTP information
client = TextAuthoringClient(endpoint, credential, logging_enable=True)
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

See the [Sample README][text_authoring_samples] for additional examples that demonstrate common Text Authoring workflows such as:

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
[text_authoring_client_src]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-textanalytics-authoring
[text_authoring_pypi_package]: https://pypi.org/project/azure-ai-textanalytics-authoring/
[text_authoring_samples]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-textanalytics-authoring/samples/README.md
[text_authoring_docs]: https://learn.microsoft.com/azure/ai-services/language-service/custom-text-classification/overview
[api_reference_authoring]: https://azuresdkdocs.z19.web.core.windows.net/python/azure-ai-textanalytics-authoring/latest/azure.ai.textanalytics.authoring.html
[text_authoring_restdocs]: https://learn.microsoft.com/rest/api/language/analyze-text-authoring/text-authoring-project?view=rest-language-analyze-text-authoring-2023-04-01
[azure_language_portal]: https://language.cognitive.azure.com/home
[cognitive_authentication_aad]: https://learn.microsoft.com/azure/cognitive-services/authentication#authenticate-with-azure-active-directory
[azure_identity_credentials]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity#credentials
[custom_subdomain]: https://learn.microsoft.com/azure/cognitive-services/authentication#create-a-resource-with-a-custom-subdomain
[install_azure_identity]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity#install-the-package
[register_aad_app]: https://learn.microsoft.com/azure/cognitive-services/authentication#assign-a-role-to-a-service-principal
[grant_role_access]: https://learn.microsoft.com/azure/cognitive-services/authentication#assign-a-role-to-a-service-principal
[default_azure_credential]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity#defaultazurecredential