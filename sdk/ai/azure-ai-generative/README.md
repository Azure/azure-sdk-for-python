# Azure Generative AI Package client library for Python

We are excited to introduce the GA of Azure Generative AI Python SDK. The Python SDK introduces new SDK capabilities like <>.

[Source code][source_code]
| [Package (PyPI)][ml_pypi]
| [Package (Conda)][ml_conda]
| [API reference documentation][ml_ref_docs]
| [Product documentation][product_documentation]
| [Samples][ml_samples]


This package has been tested with Python 3.7, 3.8, 3.9 and 3.10.

For a more complete set of Azure libraries, see https://aka.ms/azsdk/python/all

## Getting started

### Prerequisites

- Python 3.7 or later is required to use this package.
- You must have an [Azure subscription][azure_subscription].
- An [Azure Machine Learning Workspace][workspace].

### Install the package

Install the Azure Generative AI client library for Python with [pip][pip_link]:

```bash
pip install azure-ai-generative
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

Azure Generative AI Python SDK offers the following capabilities:
*  

## Examples

- View our [samples][ml_samples].

## Troubleshooting

### General

Azure ML clients raise exceptions defined in [Azure Core][azure_core_readme].

```python
from azure.core.exceptions import HttpResponseError

try:
    ml_client.compute.get("cpu-cluster")
except HttpResponseError as error:
    print("Request failed: {}".format(error.message))
```

### Logging

This library uses the standard
[logging][python_logging] library for logging.
Basic information about HTTP sessions (URLs, headers, etc.) is logged at INFO
level.

Detailed DEBUG level logging, including request/response bodies and unredacted
headers, can be enabled on a client with the `logging_enable` argument.

See full SDK logging documentation with examples [here][sdk_logging_docs].

### Telemetry

The Azure Generative AI Python SDK includes a telemetry feature that collects usage and failure data about the SDK and sends it to Microsoft when you use the SDK in a Jupyter Notebook only.
<u>Telemetry will **not** be collected for any use of the Python SDK outside of a Jupyter Notebook.</u>

Telemetry data helps the SDK team understand how the SDK is used so it can be improved and the information about failures helps the team resolve problems and fix bugs.
The SDK telemetry feature is enabled by default for Jupyter Notebook usage and cannot be enabled for non-Jupyter scenarios. To opt out of the telemetry feature in a Jupyter scenario, pass in `enable_telemetry=False` when constructing your AIClient object.

## Next steps

- View our [samples][ml_samples].

## Contributing

This project welcomes contributions and suggestions. Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit [cla.microsoft.com][cla].

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct][code_of_conduct]. For more information see the [Code of Conduct FAQ][coc_faq] or contact [opencode@microsoft.com][coc_contact] with any additional questions or comments.

<!-- LINKS -->

[source_code]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/ml/azure-ai-ml
[ml_pypi]: https://pypi.org/project/azure-ai-generative/
[ml_conda]: https://anaconda.org/microsoft/azure-ai-generative/
[ml_ref_docs]: <>
[ml_samples]: https://github.com/Azure-Samples/azureai-samples
[product_documentation]: <>
[azure_subscription]: https://azure.microsoft.com/free/
[workspace]: https://docs.microsoft.com/azure/machine-learning/concept-workspace
[python_logging]: https://docs.python.org/3/library/logging.html
[sdk_logging_docs]: https://docs.microsoft.com/azure/developer/python/azure-sdk-logging
[azure_core_readme]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/README.md
[pip_link]: https://pypi.org/project/pip/
[azure_core_ref_docs]: https://aka.ms/azsdk-python-core-policies
[azure_core]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/README.md
[azure_identity]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity
[python_logging]: https://docs.python.org/3/library/logging.html
[cla]: https://cla.microsoft.com
[code_of_conduct]: https://opensource.microsoft.com/codeofconduct/
[coc_faq]: https://opensource.microsoft.com/codeofconduct/faq/
[coc_contact]: mailto:opencode@microsoft.com
