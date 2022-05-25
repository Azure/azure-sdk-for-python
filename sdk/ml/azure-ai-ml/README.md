# Azure ML Package client library for Python

We are excited to introduce the public  preview of Azure Machine Learning Python SDK v2. The Python SDK v2 introduces new SDK capabilities like standalone local jobs, reusable components for pipelines and managed online/batch inferencing. Python SDK v2 allows you to move from simple to complex tasks easily and incrementally. This is enabled by using a common object model which brings concept reuse and consistency of actions across various tasks. The SDK v2 shares its foundation with the CLI v2 which is currently in also in public preview.

[Source code][source_code] | [Package (PyPI)][ml_pypi] | [API reference documentation][ml_ref_docs] | [Product documentation][product_documentation] | [Samples][ml_samples]


This package has been tested with Python 3.6, 3.7, 3.8, 3.9 and 3.10.

For a more complete set of Azure libraries, see https://aka.ms/azsdk/python/all

## Getting started

### Prerequisites

- Python 3.6 later is required to use this package.
- You must have an [Azure subscription][azure_subscription].
- An [Azure Machine Learning Workspace][workspace].

### Install the package

Install the Azure ML client library for Python with [pip][pip_link]:

```bash
pip install azure-ai-ml
```

### Authenticate the client

```python
from azure.ai.ml import MLClient
from azure.identity import DefaultAzureCredential

ml_client = MLClient(
    DefaultAzureCredential(), subscription_id, resource_group, workspace
)
```

## Key concepts

Azure Machine Learning Python SDK v2 comes with many new features like standalone local jobs, reusable components for pipelines and managed online/batch inferencing. The SDK v2 brings consistency and ease of use across all assets of the platform. The Python SDK v2 offers the following capabilities:
* Run **Standalone Jobs** - run a discrete ML activity as Job. This job can be run locally or on the cloud. We currently support the following types of jobs:
  * Command - run a command (Python, R, Windows Command, Linux Shell etc.)
  * Sweep - run a hyperparameter sweep on your Command
* Run multiple jobs using our **improved Pipelines**
  * Run a series of commands stitched into a pipeline (**New**)
  * **Components** - run pipelines using reusable components (**New**)
* Use your models for **Managed Online inferencing** (**New**)
* Use your models for Managed **batch inferencing**
* Manage AML resources – workspace, compute, datastores
* Manage AML assets - Datasets, environments, models
* **AutoML** - run standalone AutoML training for various ml-tasks:
  - Classification (Tabular data)
  - Regression (Tabular data)
  - Time Series Forecasting (Tabular data)
  - Image Classification (Multi-class) (**New**)
  - Image Classification (Multi-label) (**New**)
  - Image Object Detection (**New**)
  - Image Instance Segmentation (**New**)
  - NLP Text Classification (Multi-class) (**New**)
  - NLP Text Classification (Multi-label) (**New**)
  - NLP Text Named Entity Recognition (NER) (**New**)

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

## Next steps

- View our [samples][ml_samples].

## Contributing

This project welcomes contributions and suggestions. Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit [cla.microsoft.com][cla].

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct][code_of_conduct]. For more information see the [Code of Conduct FAQ][coc_faq] or contact [opencode@microsoft.com][coc_contact] with any additional questions or comments.

<!-- LINKS -->

[source_code]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/ml/azure-ai-ml
[ml_pypi]: https://pypi.org/project/azure-ai-ml/
[ml_ref_docs]: https://docs.microsoft.com/python/api/azure-ai-ml/?view=azure-ml-py
[ml_samples]: https://github.com/Azure/azureml-examples/tree/sdk-preview/sdk
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
[python_logging]: https://docs.python.org/3/library/logging.html
[cla]: https://cla.microsoft.com
[code_of_conduct]: https://opensource.microsoft.com/codeofconduct/
[coc_faq]: https://opensource.microsoft.com/codeofconduct/faq/
[coc_contact]: mailto:opencode@microsoft.com
