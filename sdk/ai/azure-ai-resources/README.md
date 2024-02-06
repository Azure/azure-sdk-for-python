# Azure AI Resources Package client library for Python

The Azure AI Resources package is part of the Azure AI SDK for Python and contains functionality for connecting to and managing your Azure AI resources and projects. Within your Azure AI projects it provides control plane operations for creating and managing data, indexes, models and deployments.


[Source code][source_code]
| [Package (PyPI)][ai_pypi]
| [API reference documentation][ai_ref_docs]
| [Product documentation][product_documentation]
| [Samples][generative_samples]

This package has been tested with Python 3.8, 3.9, 3.10, 3.11 and 3.12.

For a more complete set of Azure libraries, see https://aka.ms/azsdk/python/all.

## Getting started

### Prerequisites

- Python 3.7 or later is required to use this package.
- You must have an [Azure subscription][azure_subscription].
- An [Azure Machine Learning Workspace][workspace].
- An [Azure AI Studio project][ai_project].

### Install the package
Install the Azure AI generative package for Python with pip:

```
pip install azure-ai-resources
pip install azure-identity
```
### Authenticate the client

```python
from azure.ai.resources.client import AIClient
from azure.identity import DefaultAzureCredential

ai_client = AIClient(credential=DefaultAzureCredential(), subscription_id='subscription_id',
                     resource_group_name='resource_group', project_name='project_name')
```

## Key concepts
Use this library within your Azure AI projects to provide control plane operations for creating and managing data, indexes, models and deployments.

## Examples

View our [samples repository][generative_samples] on GitHub for examples demonstrating how to use the Azure AI Generative Python SDK.

## Troubleshooting
### General
Azure AI clients raise exceptions defined in Azure Core.

```python
from azure.core.exceptions import HttpResponseError

try:
    ai_client.compute.get("cpu-cluster")
except HttpResponseError as error:
    print("Request failed: {}".format(error.message))
```

### Logging
This library uses the standard logging library for logging. Basic information about HTTP sessions (URLs, headers, etc.) is logged at INFO level.

Detailed DEBUG level logging, including request/response bodies and unredacted headers, can be enabled on a client with the `logging_enable` argument.

See full SDK logging documentation with examples here.

### Telemetry
The Azure AI Generative Python SDK includes a telemetry feature that collects usage and failure data about the SDK and sends it to Microsoft when you use the SDK in a Jupyter Notebook only. <u>Telemetry will not be collected for any use of the Python SDK outside of a Jupyter Notebook.</u>

Telemetry data helps the SDK team understand how the SDK is used so it can be improved and the information about failures helps the team resolve problems and fix bugs. The SDK telemetry feature is enabled by default for Jupyter Notebook usage and cannot be enabled for non-Jupyter scenarios. To opt out of the telemetry feature in a Jupyter scenario, set the environment variable `"AZURE_AI_RESOURCES_ENABLE_LOGGING"` to `"False"`.

## Next steps

View our [samples repository][generative_samples] on GitHub for examples demonstrating how to use the Azure AI Generative Python SDK.

## Contributing

If you encounter any bugs or have suggestions, please file an issue in the [Issues](<https://github.com/Azure/azure-sdk-for-python/issues>) section of the project.

![Impressions](https://azure-sdk-impressions.azurewebsites.net/api/impressions/azure-sdk-for-python%2Fsdk%2Ftemplate%2Fazure-template%2FREADME.png)


<!-- LINKS -->

[source_code]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/ai/azure-ai-resources
[ai_project]: https://aka.ms/azureaistudio
[ai_pypi]: https://pypi.org/project/azure-ai-resources/
[ai_ref_docs]: https://learn.microsoft.com/python/api/azure-ai-resources/?view=azure-python-preview
[generative_samples]: https://github.com/Azure-Samples/azureai-samples
[product_documentation]: https://docs.microsoft.com/azure/machine-learning/
[azure_subscription]: https://azure.microsoft.com/free/
[workspace]: https://docs.microsoft.com/azure/machine-learning/concept-workspace
[python_logging]: https://docs.python.org/3/library/logging.html
[sdk_logging_docs]: https://docs.microsoft.com/azure/developer/python/azure-sdk-logging
[azure_core_readme]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/README.md
[pip_link]: https://pypi.org/project/pip/
[azure_core_ref_docs]: https://aka.ms/azsdk-python-core-policies
[azure_core]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/README.md
[azure_identity]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity
[cla]: https://cla.microsoft.com
[code_of_conduct]: https://opensource.microsoft.com/codeofconduct/
[coc_faq]: https://opensource.microsoft.com/codeofconduct/faq/
[coc_contact]: mailto:opencode@microsoft.com