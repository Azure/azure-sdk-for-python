

# Azure Core Tracing OpenCensus client library for Python

## Getting started

Install the opencensus python for Python with [pip](https://pypi.org/project/pip/):

```bash
pip install azure-core-tracing-opencensus --pre
```

Now you can use opencensus for Python as usual with any SDKs that is compatible
with azure-core tracing. This includes (not exhaustive list), azure-storage-blob, azure-keyvault-secrets, azure-eventhub, etc.

## Key concepts

* You don't need to pass any context, SDK will get it for you
* The opencensus threading plugin is installed with this package

## Examples

There is no explicit context to pass, you just create your usual opencensus and tracer and
call any SDK code that is compatible with azure-core tracing. This is an example
using Azure Monitor exporter, but you can use any exporter (Zipkin, etc.).

```python
from opencensus.ext.azure.trace_exporter import AzureExporter

from opencensus.trace.tracer import Tracer
from opencensus.trace.samplers import AlwaysOnSampler

from azure.storage.blob import BlobServiceClient

exporter = AzureExporter(
    instrumentation_key="uuid of the instrumentation key (see your Azure Monitor account)"
)

tracer = Tracer(exporter=exporter, sampler=AlwaysOnSampler())
with tracer.span(name="MyApplication") as span:
    client = BlobServiceClient.from_connection_string('connectionstring')
    client.delete_container('my_container')  # Call will be traced
```


## Troubleshooting

This client raises exceptions defined in [Azure Core](https://docs.microsoft.com/python/api/azure-core/azure.core.exceptions?view=azure-python).


## Next steps

More documentation on OpenCensus configuration can be found on the [OpenCensus website](https://opencensus.io)


## Contributing
This project welcomes contributions and suggestions.  Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit https://cla.microsoft.com.

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/). For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.
