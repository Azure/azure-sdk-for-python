# Azure AI Language Documents client library for Python

Azure AI Language Documents lets you submit documents stored in Azure Blob Storage for long-running language analysis jobs. You define the input documents, where output artifacts should be written, and one or more analysis tasks such as personally identifiable information (PII) entity recognition.

[Source code][documents_client_src]
| [Package (PyPI)][documents_pypi_package]
| [Package (Conda)](https://anaconda.org/microsoft/azure-ai-language-documents/)
| <!-- [API reference][documents_refdocs] -->
| [Product documentation][documents_docs]
| [Samples][documents_samples]
| [Documents REST API][documents_rest_docs]

> _Python 2.7 is not supported. For details see the Azure SDK for Python end-of-support notice._

## Getting started

### Prerequisites

* Python 3.9 or later.
* An [Azure subscription][azure_subscription].
* An Azure [Language resource][language_service] with a custom domain endpoint if you plan to use Azure Active Directory authentication.
* Azure Blob Storage locations for your source documents and output targets.

### Install the package

Install the Azure AI Language Documents client library for Python with [pip][pip_link]:

```bash
python -m pip install azure-ai-language-documents
```

> This version of the client library targets the service REST API version `2026-05-15-preview`.

### Authenticate the client

To interact with the Documents service, create an instance of `AnalyzeDocumentsClient`<!-- [documents_client_class] -->. The **recommended** approach is to use Azure Active Directory via `DefaultAzureCredential` from the [azure-identity][azure_identity_credentials] library.

> Important: To use Azure AD (AAD) you must use your resource's **custom subdomain** endpoint, for example `https://<my-subdomain>.cognitiveservices.azure.com/`. Regional endpoints do **not** support AAD token authentication.

#### Recommended: `DefaultAzureCredential`

Prerequisites for AAD authentication:

* [Install azure-identity][install_azure_identity]
* [Register an AAD application][register_aad_app]
* [Grant access][grant_role_access] to the Language resource

Set these environment variables only if you’re using a service principal with a client secret:

`AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_CLIENT_SECRET`

Then create the client:

```python
from azure.identity import DefaultAzureCredential 
from azure.ai.language.documents import AnalyzeDocumentsClient

endpoint = "https://<my-subdomain>.cognitiveservices.azure.com/" 
credential = DefaultAzureCredential()

client = AnalyzeDocumentsClient(endpoint, credential)
```


**Why `DefaultAzureCredential`?**

* Eliminates hard-coded secrets
* Works locally, in CI, and in production
* Supports managed identity without code changes
* Centralizes token acquisition and caching

## Key concepts

### `AnalyzeDocumentsClient`

`AnalyzeDocumentsClient` is the primary interface for:

- submitting long-running document analysis jobs with `begin_submit_job`
- checking job status with `get_job_state`
- cancelling jobs with `begin_cancel_job`

For asynchronous operations, use `AnalyzeDocumentsClient` from the `azure.ai.language.documents.aio` namespace.

### Input models

The request body for job submission can be passed either as:

- an `AnalyzeDocumentsJob` model
- a JSON-compatible `dict`

Common related models include:

- `AnalyzeDocumentsJob`
- `MultiLanguageAnalysisInput`
- `MultiLanguageInput`
- `AzureBlobDocumentLocation`
- `AzureContainerDocumentLocation`
- `AzureContainerFolderDocumentLocation`
- `PiiEntityRecognitionAction`
- `PiiTaskParameters`

### Job state

`get_job_state` returns an `AnalyzeDocumentsJobState`, which contains:

- job metadata
- overall job status
- task summary details

## Examples

### `AnalyzeDocumentsClient` usage examples

The `azure-ai-language-documents` client library provides both synchronous and asynchronous APIs.

- [Submit a job](#submit-a-job)
- [Get job state](#get-job-state)
- [Cancel a job](#cancel-a-job)
- [Async usage](#async-usage)
- [Samples](#samples)

#### Submit a job

This example submits a PII analysis job using JSON-compatible dictionary inputs:

<!-- SNIPPET:sample_submit_job.sample_submit_job -->

```python
def sample_submit_job() -> None:
    import os
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.language.documents import AnalyzeDocumentsClient

    endpoint = os.environ["AZURE_LANGUAGE_DOCUMENTS_ENDPOINT"]
    key = os.environ["AZURE_LANGUAGE_KEY"]
    source_location = os.environ["AZURE_LANGUAGE_DOCUMENTS_SOURCE_LOCATION"]
    target_location = os.environ["AZURE_LANGUAGE_DOCUMENTS_TARGET_LOCATION"]

    client = AnalyzeDocumentsClient(endpoint=endpoint, credential=AzureKeyCredential(key))

    with client:
        poller = client.begin_submit_job(
            body={
                "displayName": "Document Analysis Sample",
                "analysisInput": {
                    "documents": [
                        {
                            "language": "en",
                            "id": "1",
                            "source": {"location": source_location},
                            "target": {"location": target_location},
                        }
                    ]
                },
                "tasks": [
                    {
                        "kind": "PiiEntityRecognition",
                        "parameters": {
                            "redactionPolicies": [
                                {
                                    "policyName": "defaultPolicy",
                                    "policyKind": "EntityMask",
                                    "isDefault": True,
                                }
                            ]
                        },
                    }
                ],
            },
        )

        print(f"Initial poller status: {poller.status()}")
        print(f"Operation ID: {poller.details['operation_id']}")

        results = poller.result()

        print(f"Final job ID: {poller.details['job_id']}")
        print(f"Final job status: {poller.details['status']}")

        for tasks in results:
            print(f"Total tasks: {tasks.total}")
            print(f"Completed tasks: {tasks.completed}")
            print(f"Failed tasks: {tasks.failed}")
            print(f"In-progress tasks: {tasks.in_progress}")

            if tasks.items_property:
                for task_result in tasks.items_property:
                    print(f"Task kind: {task_result.kind}")
                    print(f"Task status: {task_result.status}")
```

<!-- END SNIPPET -->

#### Get job state

Use `get_job_state` to retrieve the current state of a submitted job:

<!-- SNIPPET:sample_get_job_state.sample_get_job_state -->

```python
def sample_get_job_state() -> None:
    import os
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.language.documents import AnalyzeDocumentsClient

    endpoint = os.environ["AZURE_LANGUAGE_DOCUMENTS_ENDPOINT"]
    key = os.environ["AZURE_LANGUAGE_KEY"]
    source_location = os.environ["AZURE_LANGUAGE_DOCUMENTS_SOURCE_LOCATION"]
    target_location = os.environ["AZURE_LANGUAGE_DOCUMENTS_TARGET_LOCATION"]

    client = AnalyzeDocumentsClient(endpoint=endpoint, credential=AzureKeyCredential(key))

    with client:
        poller = client.begin_submit_job(
            body={
                "displayName": "Document Analysis Sample",
                "analysisInput": {
                    "documents": [
                        {
                            "language": "en",
                            "id": "1",
                            "source": {"location": source_location},
                            "target": {"location": target_location},
                        }
                    ]
                },
                "tasks": [
                    {
                        "kind": "PiiEntityRecognition",
                        "parameters": {
                            "redactionPolicies": [
                                {
                                    "policyName": "defaultPolicy",
                                    "policyKind": "EntityMask",
                                    "isDefault": True,
                                }
                            ]
                        },
                    }
                ],
            },
        )

        job_id = poller.details["operation_id"]
        response = client.get_job_state(job_id=job_id)

        print(f"Job ID: {response['jobId']}")
        print(f"Status: {response['status']}")
```

<!-- END SNIPPET -->

#### Cancel a job

If you need to cancel a submitted job, use `begin_cancel_job`:

<!-- SNIPPET:sample_cancel_job.sample_cancel_job -->

```python
def sample_cancel_job() -> None:
    import os
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.language.documents import AnalyzeDocumentsClient

    endpoint = os.environ["AZURE_LANGUAGE_DOCUMENTS_ENDPOINT"]
    key = os.environ["AZURE_LANGUAGE_KEY"]
    source_location = os.environ["AZURE_LANGUAGE_DOCUMENTS_SOURCE_LOCATION"]
    target_location = os.environ["AZURE_LANGUAGE_DOCUMENTS_TARGET_LOCATION"]

    client = AnalyzeDocumentsClient(endpoint=endpoint, credential=AzureKeyCredential(key))

    with client:
        submit_poller = client.begin_submit_job(
            body={
                "displayName": "Document Analysis Sample",
                "analysisInput": {
                    "documents": [
                        {
                            "language": "en",
                            "id": "1",
                            "source": {"location": source_location},
                            "target": {"location": target_location},
                        }
                    ]
                },
                "tasks": [
                    {
                        "kind": "PiiEntityRecognition",
                        "parameters": {
                            "redactionPolicies": [
                                {
                                    "policyName": "defaultPolicy",
                                    "policyKind": "EntityMask",
                                    "isDefault": True,
                                }
                            ]
                        },
                    }
                ],
            },
        )

        job_id = submit_poller.details["operation_id"]

        cancel_poller = client.begin_cancel_job(job_id=job_id)
        cancel_poller.result()

        response = client.get_job_state(job_id=job_id)

        print(f"Cancel operation status: {cancel_poller.status()}")
        print(f"Job ID: {response['jobId']}")
        print(f"Job status: {response['status']}")
```

<!-- END SNIPPET -->

#### Async usage

The same patterns are available with the async client in `azure.ai.language.documents.aio`:

<!-- SNIPPET:sample_submit_job_async.sample_submit_job_async -->

```python
import asyncio


async def sample_submit_job() -> None:
    import os
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.language.documents.aio import AnalyzeDocumentsClient

    endpoint = os.environ["AZURE_LANGUAGE_DOCUMENTS_ENDPOINT"]
    key = os.environ["AZURE_LANGUAGE_KEY"]
    source_location = os.environ["AZURE_LANGUAGE_DOCUMENTS_SOURCE_LOCATION"]
    target_location = os.environ["AZURE_LANGUAGE_DOCUMENTS_TARGET_LOCATION"]

    client = AnalyzeDocumentsClient(endpoint=endpoint, credential=AzureKeyCredential(key))

    async with client:
        poller = await client.begin_submit_job(
            body={
                "displayName": "Document Analysis Sample",
                "analysisInput": {
                    "documents": [
                        {
                            "language": "en",
                            "id": "1",
                            "source": {"location": source_location},
                            "target": {"location": target_location},
                        }
                    ]
                },
                "tasks": [
                    {
                        "kind": "PiiEntityRecognition",
                        "parameters": {
                            "redactionPolicies": [
                                {
                                    "policyName": "defaultPolicy",
                                    "policyKind": "EntityMask",
                                    "isDefault": True,
                                }
                            ]
                        },
                    }
                ],
            },
        )

        print(f"Initial poller status: {poller.status()}")
        print(f"Operation ID: {poller.details['operation_id']}")

        results = await poller.result()

        print(f"Final job ID: {poller.details['job_id']}")
        print(f"Final job status: {poller.details['status']}")

        async for tasks in results:
            print(f"Total tasks: {tasks.total}")
            print(f"Completed tasks: {tasks.completed}")
            print(f"Failed tasks: {tasks.failed}")
            print(f"In-progress tasks: {tasks.in_progress}")

            if tasks.items_property:
                for task_result in tasks.items_property:
                    print(f"Task kind: {task_result.kind}")
                    print(f"Task status: {task_result.status}")
```

<!-- END SNIPPET -->

## Samples

The following samples are available in this package:

|**File Name**|**Description**|
|----------------|-------------|
|[sample_submit_job.py][sample_submit_job] and [sample_submit_job_async.py][sample_submit_job_async]|Submit an analyze documents job|
|[sample_get_job_state.py][sample_get_job_state] and [sample_get_job_state_async.py][sample_get_job_state_async]|Submit a job and retrieve its job state|
|[sample_cancel_job.py][sample_cancel_job] and [sample_cancel_job_async.py][sample_cancel_job_async]|Submit a job and cancel it|

## Optional configuration

Optional keyword arguments can be passed at both the client and per-operation level. The azure-core [reference documentation][azure_core_ref_docs] describes available configurations for retries, logging, transport protocols, and more.

## Troubleshooting

### General

Azure AI Language Documents clients raise exceptions defined in [Azure Core][azure_core_readme].

When you interact with the service using the Python SDK, service errors map to the same HTTP status codes returned by the [REST API][documents_rest_docs].

For example:

```python

from azure.core.exceptions import HttpResponseError

try:
    client.get_job_state("invalid-job-id")
except HttpResponseError as error:
    print(f"Query failed: {error.message}")

```

### Logging

This library uses the standard [logging][python_logging] library for logging.

Basic information about HTTP sessions, such as URLs and headers, is logged at INFO level.

Detailed DEBUG logging, including request and response bodies and unredacted headers, can be enabled with the `logging_enable` argument.

See the full SDK logging documentation in the [logging guidance][sdk_logging_docs].

## API usage notes

This library supports both:

* **Strongly typed model inputs** via `AnalyzeDocumentsJob`
* **JSON-compatible dictionary inputs** for direct request construction

## Next steps

* View our [samples][documents_samples].
* Read more about [Azure AI Language][documents_docs].
* Review the [REST API][documents_rest_docs].

## Contributing

See the [CONTRIBUTING.md][contributing] for details on building, testing, and contributing to this library.

This project welcomes contributions and suggestions. Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit [cla.microsoft.com][cla].

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide a CLA and decorate the PR appropriately (for example, label or comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct][code_of_conduct]. For more information see the [Code of Conduct FAQ][coc_faq] or contact [opencode@microsoft.com][coc_contact] with any additional questions or comments.

<!-- LINKS -->

[azure_subscription]: https://azure.microsoft.com/free/
[language_service]: https://ms.portal.azure.com/#create/Microsoft.CognitiveServicesTextAnalytics
[cla]: https://cla.microsoft.com
[coc_contact]: mailto:opencode@microsoft.com
[coc_faq]: https://opensource.microsoft.com/codeofconduct/faq/
[code_of_conduct]: https://opensource.microsoft.com/codeofconduct/
[contributing]: https://github.com/Azure/azure-sdk-for-python/blob/main/CONTRIBUTING.md
[python_logging]: https://docs.python.org/3/library/logging.html
[sdk_logging_docs]: https://learn.microsoft.com/azure/developer/python/azure-sdk-logging
[azure_core_ref_docs]: https://azuresdkdocs.z19.web.core.windows.net/python/azure-core/latest/azure.core.html
[azure_core_readme]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/README.md
[pip_link]: https://pypi.org/project/pip/
[documents_client_class]: https://azuresdkdocs.z19.web.core.windows.net/python/azure-ai-language-documents/latest/azure.ai.language.documents.html#azure.ai.language.documents.AnalyzeDocumentsClient
[documents_client_src]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-documents/
[documents_docs]: https://learn.microsoft.com/azure/ai-services/language-service/
[documents_pypi_package]: https://pypi.org/project/azure-ai-language-documents/
[documents_refdocs]: https://azuresdkdocs.z19.web.core.windows.net/python/azure-ai-language-documents/latest/azure.ai.language.documents.html
[documents_rest_docs]: https://learn.microsoft.com/rest/api/language/
[azure_identity_credentials]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity#credentials
[install_azure_identity]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity#install-the-package
[register_aad_app]: https://learn.microsoft.com/azure/cognitive-services/authentication#assign-a-role-to-a-service-principal
[grant_role_access]: https://learn.microsoft.com/azure/cognitive-services/authentication#assign-a-role-to-a-service-principal
[documents_samples]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-documents/samples/
[sample_submit_job]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-documents/samples/sample_submit_job.py
[sample_submit_job_async]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-documents/samples/async_samples/sample_submit_job_async.py
[sample_get_job_state]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-documents/samples/sample_get_job_state.py
[sample_get_job_state_async]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-documents/samples/async_samples/sample_get_job_state_async.py
[sample_cancel_job]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-documents/samples/sample_cancel_job.py
[sample_cancel_job_async]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-documents/samples/async_samples/sample_cancel_job_async.py