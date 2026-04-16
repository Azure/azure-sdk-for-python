# Azure AI Language Documents client library for Python

Azure AI Language Documents lets you submit documents stored in Azure Blob Storage for long-running language analysis jobs. You define the input documents, where output artifacts should be written, and one or more analysis tasks such as personally identifiable information (PII) entity recognition.

[Source code][documents_client_src]
| [Package (PyPI)][documents_pypi_package]
| [Package (Conda)](https://anaconda.org/microsoft/azure-ai-language-documents/)
| [API reference][documents_refdocs]
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

> This version of the client library targets the service REST API version `2026-05-01`.

### Authenticate the client

To interact with the Documents service, create an instance of [AnalyzeDocumentsClient][documents_client_class]. The **recommended** approach is to use Azure Active Directory via `DefaultAzureCredential` from the [azure-identity][azure_identity_credentials] library.

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

[`AnalyzeDocumentsClient`][documents_client_class] is the primary interface for submitting document analysis jobs, checking job status, and cancelling submitted jobs.

For asynchronous operations, an async `AnalyzeDocumentsClient` is available in the `azure.ai.language.documents.aio` namespace.

### Input and task model relationships

The request body for job submission is built from these models:

* `AnalyzeDocumentJobsInput` – top-level job definition
* `MultiLanguageAnalysisInput` – collection of documents to analyze
* `MultiLanguageInput` – one input document, including:
  * `source` – input document location
  * `target` – output location
* `DocumentLocation` subtypes – storage-backed document locations:
  * `AzureBlobDocumentLocation`
  * `AzureContainerDocumentLocation`
  * `AzureContainerFolderDocumentLocation`
* `AnalyzeDocumentsLROTask` subtypes – tasks to run for the job, such as:
  * `PiiLROTask`

PII task configuration is provided through `PiiTaskParameters`, including optional `redaction_policies`.

### Results model relationships

`analyze_documents_job_status` returns `AnalyzeDocumentsJobState`, which contains:

* overall job metadata and status
* `tasks`, a `Tasks` object
* `tasks.items_property`, which contains per-task results such as:
  * `PiiEntityRecognitionLROResult`
  * `AbstractiveSummarizationLROResult`

Each task result contains an `AnalyzeDocumentsResult`, which exposes:

* `documents`
* `errors`
* `statistics`
* `model_version`

## Examples

### `AnalyzeDocumentsClient` usage examples

The `azure-ai-language-documents` client library provides both synchronous and asynchronous APIs.

* [Submit a job (model objects)](#submit-a-job-model-objects)
* [Submit a job (JSON body)](#submit-a-job-json-body)
* [Get job status and results](#get-job-status-and-results)
* [Cancel a job](#cancel-a-job)
* [Async usage](#async-usage)

#### Submit a job (model objects)

This example submits a PII analysis job using strongly typed model objects:

```python

import os

from azure.identity import DefaultAzureCredential
from azure.ai.language.documents import AnalyzeDocumentsClient
from azure.ai.language.documents.models import (
    AnalyzeDocumentJobsInput,
    MultiLanguageAnalysisInput,
    MultiLanguageInput,
    AzureBlobDocumentLocation,
    AzureContainerFolderDocumentLocation,
    PiiLROTask,
    PiiTaskParameters,
    CharacterMaskPolicy,
)

endpoint = os.environ["AZURE_LANGUAGE_ENDPOINT"]
client = AnalyzeDocumentsClient(endpoint, DefaultAzureCredential())

job = AnalyzeDocumentJobsInput(
    display_name="sample-documents-job",
    analysis_input=MultiLanguageAnalysisInput(
        documents=[
            MultiLanguageInput(
                id="1",
                source=AzureBlobDocumentLocation(
                    location="https://<storage-account>.blob.core.windows.net/input/invoice-1.txt"
                ),
                target=AzureContainerFolderDocumentLocation(
                    location="https://<storage-account>.blob.core.windows.net/output/pii-results/"
                ),
                language="en",
            )
        ]
    ),
    tasks=[
        PiiLROTask(
            task_name="pii-redaction",
            parameters=PiiTaskParameters(
                redaction_policies=[
                    CharacterMaskPolicy(is_default=True)
                ]
            ),
        )
    ],
    default_language="en",
)

poller = client.begin_analyze_documents_submit_job(job)
poller.result()

print(f"Job completed with status: {poller.status()}")
```

#### Submit a job (JSON body)

You can also submit the request as a JSON-compatible dictionary:

```python
import os

from azure.identity import DefaultAzureCredential
from azure.ai.language.documents import AnalyzeDocumentsClient

endpoint = os.environ["AZURE_LANGUAGE_ENDPOINT"]
client = AnalyzeDocumentsClient(endpoint, DefaultAzureCredential())

body = {
    "displayName": "sample-documents-job",
    "analysisInput": {
        "documents": [
            {
                "id": "1",
                "source": {
                    "kind": "AzureBlob",
                    "location": "https://<storage-account>.blob.core.windows.net/input/invoice-1.txt",
                },
                "target": {
                    "kind": "AzureContainerFolder",
                    "location": "https://<storage-account>.blob.core.windows.net/output/pii-results/",
                },
                "language": "en",
            }
        ]
    },
    "tasks": [
        {
            "kind": "PiiEntityRecognition",
            "taskName": "pii-redaction",
            "parameters": {
                "redactionPolicies": [
                    {
                        "policyKind": "characterMask",
                        "isDefault": True,
                    }
                ]
            },
        }
    ],
    "defaultLanguage": "en",
}

poller = client.begin_analyze_documents_submit_job(body)
poller.result()

print(f"Job completed with status: {poller.status()}")
```

#### Get job status and results

If you have a job ID, use `analyze_documents_job_status` to retrieve the full job state and task results:

```python
from azure.core.exceptions import HttpResponseError

job_id = "<job-id>"

try:
    job_state = client.analyze_documents_job_status(job_id, show_stats=True)

    print(f"Job ID: {job_state.job_id}")
    print(f"Status: {job_state.status}")
    print(f"Created: {job_state.created_date_time}")
    print(f"Updated: {job_state.last_updated_date_time}")

    if job_state.statistics:
        print(f"Documents: {job_state.statistics.documents_count}")
        print(f"Transactions: {job_state.statistics.transactions_count}")

    for task in job_state.tasks.items_property or []:
        print(f"Task kind: {task.kind}")
        print(f"Task status: {task.status}")

        if hasattr(task, "results"):
            print(f"Model version: {task.results.model_version}")
            for document in task.results.documents:
                print(f"Document ID: {document.id}")
                print(f"Source: {document.source.location}")
                for target in document.target:
                    print(f"Target: {target.location}")

except HttpResponseError as error:
    print(f"Request failed: {error.message}")
```

#### Cancel a job

If you need to cancel a submitted job, use `begin_analyze_documents_cancel_job`:

```python

job_id = "<job-id>"

cancel_poller = client.begin_analyze_documents_cancel_job(job_id)
cancel_poller.result()

print(f"Cancellation request completed with status: {cancel_poller.status()}")

```

#### Async usage

The same patterns are available with the async client in `azure.ai.language.documents.aio`:

```python

import os
import asyncio

from azure.identity.aio import DefaultAzureCredential
from azure.ai.language.documents.aio import AnalyzeDocumentsClient
from azure.ai.language.documents.models import (
    AnalyzeDocumentJobsInput,
    MultiLanguageAnalysisInput,
    MultiLanguageInput,
    AzureBlobDocumentLocation,
    AzureContainerFolderDocumentLocation,
    PiiLROTask,
)


async def main():
    credential = DefaultAzureCredential()
    client = AnalyzeDocumentsClient(
        os.environ["AZURE_LANGUAGE_ENDPOINT"],
        credential,
    )

    try:
        job = AnalyzeDocumentJobsInput(
            display_name="async-documents-job",
            analysis_input=MultiLanguageAnalysisInput(
                documents=[
                    MultiLanguageInput(
                        id="1",
                        source=AzureBlobDocumentLocation(
                            location="https://<storage-account>.blob.core.windows.net/input/invoice-1.txt"
                        ),
                        target=AzureContainerFolderDocumentLocation(
                            location="https://<storage-account>.blob.core.windows.net/output/pii-results/"
                        ),
                        language="en",
                    )
                ]
            ),
            tasks=[
                PiiLROTask(task_name="pii-analysis")
            ],
            default_language="en",
        )

        poller = await client.begin_analyze_documents_submit_job(job)
        await poller.result()

        print(f"Job completed with status: {poller.status()}")

    finally:
        await client.close()
        await credential.close()


asyncio.run(main())

```

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
    client.analyze_documents_job_status("invalid-job-id")
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

* **Strongly typed model inputs** via `AnalyzeDocumentJobsInput`
* **JSON-compatible dictionary inputs** for direct request construction

The typed-model approach is recommended for clarity, static analysis, and discoverability.

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
[documents_samples]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-documents/samples/
[documents_rest_docs]: https://learn.microsoft.com/rest/api/language/
[azure_identity_credentials]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity#credentials
[install_azure_identity]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity#install-the-package
[register_aad_app]: https://learn.microsoft.com/azure/cognitive-services/authentication#assign-a-role-to-a-service-principal
[grant_role_access]: https://learn.microsoft.com/azure/cognitive-services/authentication#assign-a-role-to-a-service-principal