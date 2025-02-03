# Azure Health Deidentification client library for Python
Azure Health Deidentification is Microsoft's solution to anonymize unstructured health text.

[Source code](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/healthdataaiservices/azure-health-deidentification/azure/health/deidentification)
<!-- TODO: | [Package (PyPI)](https://pypi.org/project/azure-health-deidentification/) -->
<!-- TODO: | [API reference documentation](https://aka.ms/azsdk-python-storage-blob-ref) -->
| [Samples](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/healthdataaiservices/azure-health-deidentification/samples)


## Getting started

### Prerequisites
* Python 3.8 or later is required to use this package. For more details, please read our page on [Azure SDK for Python version support policy](https://github.com/Azure/azure-sdk-for-python/wiki/Azure-SDKs-Python-version-support-policy).
* You must have an [Azure subscription](https://azure.microsoft.com/free/) and an
**Azure Deidentification Service** to use this package.

### Install the package
Install the Azure Health Deidentification client library for Python with [pip](https://pypi.org/project/pip/):

```bash
pip install azure-health-deidentification
```

### Create a Deidentification Service
If you wish to create a new storage account, you can use the
[Azure Portal](https://learn.microsoft.com/azure/storage/common/storage-quickstart-create-account?tabs=azure-portal).

### Create the client
In order to create a Deidentification client you must obtain the **Service URL** from your Azure Deidentification Service

```python
    endpoint = os.environ["AZURE_HEALTH_DEIDENTIFICATION_ENDPOINT"]
    endpoint = endpoint.replace("https://", "")
    print(endpoint)
    # example: fuf4h4bxg5b0d0dr.api.cac001.deid.azure.com

    credential = DefaultAzureCredential()

    client = DeidentificationClient(endpoint, DefaultAzureCredential())
```

### Deidentify a string

```python
    body = DeidentificationContent(input_text="Hello, my name is John Smith.")

    result: DeidentificationResult = client.deidentify(body)
    
    print(f'Original Text:     "{body.input_text}"')
    print(f'Deidentified Text: "{result.output_text}"')
```

## Key concepts
Operation Modes:
- Tag: Will return a structure of offset and length with the PHI category of the related text spans.
- Redact: Will return output text with placeholder stubbed text. ex. `[name]`
- Surrogate: Will return output text with synthetic replacements.
  - `My name is John Smith`
  - `My name is Tom Jones`

## Contributing
This project welcomes contributions and suggestions.  Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit https://cla.microsoft.com.

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/). For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.