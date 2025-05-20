# Azure Health Data Services de-identification service client library for Python

This package contains a client library for the de-identification service in Azure Health Data Services which 
enables users to tag, redact, or surrogate health data containing Protected Health Information (PHI).
For more on service functionality and important usage considerations, see [the de-identification service overview][product_documentation].

This library support API versions `2024-11-15` and earlier.

Use the client library for the de-identification service to:
- Discover PHI in unstructured text
- Replace PHI in unstructured text with placeholder values
- Replace PHI in unstructured text with realistic surrogate values
- Manage asynchronous jobs to de-identify documents in Azure Storage

[Source code](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/healthdataaiservices/azure-health-deidentification/azure/health/deidentification)
| [Package (PyPI)](https://pypi.org/project/azure-health-deidentification)
| [API reference documentation](https://learn.microsoft.com/python/api/overview/azure/health-deidentification)
| [Product documentation][product_documentation]
| [Samples][samples]

## Getting started

### Prequisites

- Python 3.9 or later is required to use this package.
- Install [pip][pip].
- You need an [Azure subscription][azure_sub] to use this package.
- [Deploy the de-identification service][deid_quickstart].
- [Configure Azure role-based access control (RBAC)][deid_rbac] for the operations you will perform.

### Install the package

```bash
python -m pip install azure-health-deidentification
```

### Authentication
To authenticate with the de-identification service, install [`azure-identity`][azure_identity_pip]:

```bash
python -m pip install azure.identity
```

You can use [DefaultAzureCredential][default_azure_credential] to automatically find the best credential to use at runtime.

You will need a **service URL** to instantiate a client object. You can find the service URL for a particular resource in the [Azure portal][azure_portal], or using the [Azure CLI][azure_cli]:

```bash
# Get the service URL for the resource
az deidservice show --name "<resource-name>" --resource-group "<resource-group-name>" --query "properties.serviceUrl"
```

Optionally, save the service URL as an environment variable named `AZURE_HEALTH_DEIDENTIFICATION_ENDPOINT` for the sample client initialization code.

Create a client with the endpoint and credential:
<!-- SNIPPET: examples.create_client -->

```python
endpoint = os.environ["AZURE_HEALTH_DEIDENTIFICATION_ENDPOINT"]
credential = DefaultAzureCredential()
client = DeidentificationClient(endpoint, credential)
```

<!-- END SNIPPET -->

## Key concepts

### De-identification operations:
Given an input text, the de-identification service can perform three main operations:
- `Tag` returns the category and location within the text of detected PHI entities.
- `Redact` returns output text where detected PHI entities are replaced with placeholder text. For example `John` replaced with `[name]`.
- `Surrogate` returns output text where detected PHI entities are replaced with realistic replacement values. For example, `My name is John Smith` could become `My name is Tom Jones`.

### Available endpoints
There are two ways to interact with the de-identification service. You can send text directly, or you can create jobs 
to de-identify documents in Azure Storage.

You can de-identify text directly using the `DeidentificationClient`:
<!-- SNIPPET: deidentify_text_surrogate.surrogate -->

```python
body = DeidentificationContent(input_text="Hello, my name is John Smith.")
result: DeidentificationResult = client.deidentify_text(body)
print(f'\nOriginal Text:        "{body.input_text}"')
print(f'Surrogated Text:   "{result.output_text}"')  # Surrogated output: Hello, my name is <synthetic name>.
```

<!-- END SNIPPET -->

To de-identify documents in Azure Storage, see [Tutorial: Configure Azure Storage to de-identify documents][deid_configure_storage]
for prerequisites and configuration options.

To run the sample code below, populate the following environment variables:
- `AZURE_STORAGE_ACCOUNT_LOCATION`: an Azure Storage container endpoint, like `https://<storageaccount>.blob.core.windows.net/<container>`.
- `INPUT_PREFIX`: the prefix of the input document name(s) in the container. For example, providing `folder1` would create a job that would process documents like `https://<storageaccount>.blob.core.windows.net/<container>/folder1/document1.txt`

The client exposes a `begin_deidentify_documents` method that returns a [LROPoller](https://learn.microsoft.com/python/api/azure-core/azure.core.polling.lropoller) instance. You can get the result of the operation by calling `result()`, optionally passing in a `timeout` value in seconds:
<!-- SNIPPET: deidentify_documents.sample -->

```python
endpoint = os.environ["AZURE_HEALTH_DEIDENTIFICATION_ENDPOINT"]
storage_location = os.environ["AZURE_STORAGE_ACCOUNT_LOCATION"]
inputPrefix = os.environ["INPUT_PREFIX"]
outputPrefix = "_output"

credential = DefaultAzureCredential()

client = DeidentificationClient(endpoint, credential)

jobname = f"sample-job-{uuid.uuid4().hex[:8]}"

job = DeidentificationJob(
    source_location=SourceStorageLocation(
        location=storage_location,
        prefix=inputPrefix,
    ),
    target_location=TargetStorageLocation(location=storage_location, prefix=outputPrefix, overwrite=True),
)

finished_job: DeidentificationJob = client.begin_deidentify_documents(jobname, job).result(timeout=60)

print(f"Job Name:   {finished_job.job_name}")
print(f"Job Status: {finished_job.status}")
print(f"File Count: {finished_job.summary.total_count if finished_job.summary is not None else 0}")
```

<!-- END SNIPPET -->

## Examples
The following sections provide code samples covering some of the most common client use cases, including: 

- [Discover PHI in unstructured text](#discover-phi-in-unstructured-text)
- [Replace PHI in unstructured text with placeholder values](#replace-phi-in-unstructured-text-with-placeholder-values)
- [Replace PHI in unstructured text with realistic surrogate values](#replace-phi-in-unstructured-text-with-realistic-surrogate-values)

See the [samples][samples] for code files illustrating common patterns, including creating and managing jobs to de-identify documents in Azure Storage. 

### Discover PHI in unstructured text
When you specify the `TAG` operation, the service will return information about the PHI entities it detects. You can use this information to customize your de-identification workflow:
<!-- SNIPPET: deidentify_text_tag.tag -->

```python
body = DeidentificationContent(
    input_text="Hello, I'm Dr. John Smith.", operation_type=DeidentificationOperationType.TAG
)
result: DeidentificationResult = client.deidentify_text(body)
print(f'\nOriginal Text:    "{body.input_text}"')

if result.tagger_result and result.tagger_result.entities:
    print(f"Tagged Entities:")
    for entity in result.tagger_result.entities:
        print(
            f'\tEntity Text: "{entity.text}", Entity Category: "{entity.category}", Offset: "{entity.offset.code_point}", Length: "{entity.length.code_point}"'
        )
else:
    print("\tNo tagged entities found.")
```

<!-- END SNIPPET -->

### Replace PHI in unstructured text with placeholder values
When you specify the `REDACT` operation, the service will replace the PHI entities it detects with placeholder values. You can learn more about [redaction customization][deid_redact]. 
<!-- SNIPPET: deidentify_text_redact.redact -->

```python
body = DeidentificationContent(
    input_text="It's great to work at Contoso.", operation_type=DeidentificationOperationType.REDACT
)
result: DeidentificationResult = client.deidentify_text(body)
print(f'\nOriginal Text:        "{body.input_text}"')
print(f'Redacted Text:   "{result.output_text}"')  # Redacted output: "It's great to work at [organization]."
```

<!-- END SNIPPET -->

### Replace PHI in unstructured text with realistic surrogate values
The default operation is the `SURROGATE` operation. Using this operation, the service will replace the PHI entities it detects with realistic surrogate values:
<!-- SNIPPET: deidentify_text_surrogate.surrogate -->

```python
body = DeidentificationContent(input_text="Hello, my name is John Smith.")
result: DeidentificationResult = client.deidentify_text(body)
print(f'\nOriginal Text:        "{body.input_text}"')
print(f'Surrogated Text:   "{result.output_text}"')  # Surrogated output: Hello, my name is <synthetic name>.
```

<!-- END SNIPPET -->

### Troubleshooting
The `DeidentificationClient` raises various `AzureError` [exceptions][azure_error]. For example, if you
provide an invalid service URL, an `ServiceRequestError` would be raised with a message indicating the failure cause.
In the following code snippet, the error is handled and displayed:
<!-- SNIPPET: examples.handle_error -->

```python
error_client = DeidentificationClient("https://contoso.deid.azure.com", credential)
body = DeidentificationContent(input_text="Hello, I'm Dr. John Smith.")

try:
    error_client.deidentify_text(body)
except AzureError as e:
    print("\nError: " + e.message)
```

<!-- END SNIPPET -->

If you encounter an error indicating that the service is unable to access source or target storage in a de-identification job:
- Ensure you [assign a managed identity][deid_managed_identity] to your de-identification service
- Ensure you [assign appropriate permissions][deid_rbac] to the managed identity to access the storage account

## Next steps

Find a bug, or have feedback? Raise an issue with the [Health Deidentification][github_issue_label] label.

## Troubleshooting

- **Unable to Access Source or Target Storage**
  - Ensure you create your deid service with a system assigned managed identity
  - Ensure your storage account has given permissions to that managed identity

## Contributing

This project welcomes contributions and suggestions. Most contributions require
you to agree to a Contributor License Agreement (CLA) declaring that you have
the right to, and actually do, grant us the rights to use your contribution.
For details, visit https://cla.microsoft.com.

When you submit a pull request, a CLA-bot will automatically determine whether
you need to provide a CLA and decorate the PR appropriately (e.g., label,
comment). Simply follow the instructions provided by the bot. You will only
need to do this once across all repos using our CLA.

This project has adopted the
[Microsoft Open Source Code of Conduct][code_of_conduct]. For more information,
see the Code of Conduct FAQ or contact opencode@microsoft.com with any
additional questions or comments.

<!-- LINKS -->
[code_of_conduct]: https://opensource.microsoft.com/codeofconduct/
[product_documentation]: https://learn.microsoft.com/azure/healthcare-apis/deidentification/
[azure_identity_pip]: https://pypi.org/project/azure-identity/
[default_azure_credential]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity#defaultazurecredential
[pip]: https://pypi.org/project/pip/
[azure_sub]: https://azure.microsoft.com/free/
[deid_quickstart]: https://learn.microsoft.com/azure/healthcare-apis/deidentification/quickstart
[deid_redact]: https://learn.microsoft.com/azure/healthcare-apis/deidentification/redaction-format
[deid_rbac]: https://learn.microsoft.com/azure/healthcare-apis/deidentification/manage-access-rbac
[deid_managed_identity]: https://learn.microsoft.com/azure/healthcare-apis/deidentification/managed-identities
[deid_configure_storage]: https://learn.microsoft.com/azure/healthcare-apis/deidentification/configure-storage
[azure_cli]: https://learn.microsoft.com/cli/azure/healthcareapis/deidservice?view=azure-cli-latest
[azure_portal]: https://ms.portal.azure.com
[azure_error]: https://learn.microsoft.com/python/api/azure-core/azure.core.exceptions.azureerror
[samples]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/healthdataaiservices/azure-health-deidentification/samples
[github_issue_label]: https://github.com/Azure/azure-sdk-for-python/labels/Health%20Deidentification
