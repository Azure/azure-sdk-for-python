# Azure AI Generative Package client library for Python

The Azure AI Generative package is part of the Azure AI SDK for Python and contains functionality for building, evaluating and deploying Generative AI applications that leverage Azure AI services. The default installation of the package contains capabilities for cloud-connected scenarios, and by installing extras you can also run operations locally (such as building indexes and calculating metrics).

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
pip install azure-ai-generative[index,evaluate,promptflow]
pip install azure-identity
```

## Key concepts

The `[index,evaluate,promptflow]` syntax specifies extra packages that you can optionally remove if you don't need the functionality: 
* `[index]` adds the ability to build indexes on your local development environment
* `[evaluate]` adds the ability to run evaluation and calculate metrics in your local development environment 
* `[promptflow]` adds the ability to develop with prompt flow connected to your Azure AI project

## Usage

### Connecting to Projects
The generative package includes the azure-ai-resources package and uses the `AIClient` for connecting to your project.

First, create an `AI Client`:

```python
from azure.ai.resources.client import AIClient
from azure.identity import DefaultAzureCredential

ai_client = AIClient(
    credential=DefaultAzureCredential(),
    subscription_id='subscription_id',
    resource_group_name='resource_group',
    project_name='project_name'
)
```

### Using the generative package
Azure AI Generative Python SDK offers the following key capabilities.

To build an index locally, import the build_index function:

```python
from azure.ai.generative.index import build_index
```
To run a local evaluation, import the evaluate function:

```python
from azure.ai.generative.evaluate import evaluate
```
To deploy chat functions and prompt flows, import the deploy function:

```python
from azure.ai.resources.entities.deployment import Deployment
```
For sample usage of these, refer to this sample

## Examples

See our [samples repository][generative_samples] for examples of how to use the Azure AI Generative Python SDK.

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

Telemetry data helps the SDK team understand how the SDK is used so it can be improved and the information about failures helps the team resolve problems and fix bugs. The SDK telemetry feature is enabled by default for Jupyter Notebook usage and cannot be enabled for non-Jupyter scenarios. To opt out of the telemetry feature in a Jupyter scenario, set the environment variable `"AZURE_AI_GENERATIVE_ENABLE_LOGGING"` to `"False"`.


## Next steps

See our [samples repository][generative_samples] for examples of how to use the Azure AI Generative Python SDK.

## Contributing

If you encounter any bugs or have suggestions, please file an issue in the [Issues](<https://github.com/Azure/azure-sdk-for-python/issues>) section of the project.

![Impressions](https://azure-sdk-impressions.azurewebsites.net/api/impressions/azure-sdk-for-python%2Fsdk%2Ftemplate%2Fazure-template%2FREADME.png)


<!-- LINKS -->

[source_code]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/ai/azure-ai-generative
[ai_project]: https://aka.ms/azureaistudio
[ai_pypi]: https://pypi.org/project/azure-ai-generative/
[ai_ref_docs]: https://learn.microsoft.com/python/api/azure-ai-generative/?view=azure-python-preview
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