# Azure Quantum client library for Python

[Source code](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/quantum/azure-quantum-client) |
[Package (PyPI)](https://pypi.org/project/azure-quantum-client/) |
[API reference documentation]() |
[Product documentation]() |
[Samples](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/quantum/azure-quantum-client/samples)


## Getting started

### Install the package

Install the Azure Quantum client library for Python with [pip](https://pypi.org/project/pip/):

```bash
pip install azure-quantum-client
```

### Prerequisites

* Python 2.7, or 3.5 or later is required to use this package.
* You need an [Azure subscription][azure_sub] and a
[Azure Quantum service][quantum_resource] to use this package.

## Key concepts


## Examples

## Troubleshooting

### General

The Azure Quantum client will raise exceptions defined in [Azure Core][azure_core].

### Logging

This library uses the standard [logging][python_logging] library for logging.
Basic information about HTTP sessions (URLs, headers, etc.) is logged at INFO
level.

Detailed DEBUG level logging, including request/response bodies and unredacted
headers, can be enabled on a client with the `logging_enable` keyword argument:
```python
import sys
import logging
from azure.core.credentials import AzureKeyCredential
from azure.quantum.client import QuantumClient

# Create a logger for the 'azure' SDK
logger = logging.getLogger('azure')
logger.setLevel(logging.DEBUG)

# Configure a console output
handler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(handler)

# This client will log detailed information about its HTTP sessions, at DEBUG level
client = QuantumClient("<service endpoint>", "<workspace_name>", AzureKeyCredential("<api key>"), logging_enable=True)

```

Similarly, `logging_enable` can enable detailed logging for a single operation,
even when it isn't enabled for the client:
```python
```

## Next steps

## Contributing

See our [CONTRIBUTING.md][sdk_contrib] for details on building,
testing, and contributing to this library.

This project welcomes contributions and suggestions.  Most contributions require
you to agree to a Contributor License Agreement (CLA) declaring that you have
the right to, and actually do, grant us the rights to use your contribution. For
details, visit [cla.microsoft.com][cla].

This project has adopted the [Microsoft Open Source Code of Conduct][code_of_conduct].
For more information see the [Code of Conduct FAQ][coc_faq]
or contact [opencode@microsoft.com][coc_contact] with any
additional questions or comments.

## Related projects

* [Microsoft Azure SDK for Python](https://github.com/Azure/azure-sdk-for-python)

<!-- LINKS -->

[azure_cli]: https://docs.microsoft.com/cli/azure
[azure_core]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/core/azure-core/README.md
[azure_sub]: https://azure.microsoft.com/free/
[quantum_resource]: https://docs.microsoft.com/azure/quantum
[azure_portal]: https://portal.azure.com

[sdk_contrib]: https://github.com/Azure/azure-sdk-for-python/blob/master/CONTRIBUTING.md
[python_logging]: https://docs.python.org/3.5/library/logging.html

[cla]: https://cla.microsoft.com
[code_of_conduct]: https://opensource.microsoft.com/codeofconduct/
[coc_faq]: https://opensource.microsoft.com/codeofconduct/faq/
[coc_contact]: mailto:opencode@microsoft.com
