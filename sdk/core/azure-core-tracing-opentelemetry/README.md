

# Azure Core Tracing OpenTelemetry client library for Python

## Getting started

Install the opentelemetry python for Python with [pip](https://pypi.org/project/pip/):

```bash
pip install azure-core-tracing-opentelemetry --pre
```

Now you can use opentelemetry for Python as usual with any SDKs that is compatible
with azure-core tracing. This includes (not exhaustive list), azure-storage-blob, azure-keyvault-secrets, azure-eventhub, etc.

## Key concepts

* You don't need to pass any context, SDK will get it for you

## Examples

There is no explicit context to pass, you just create your usual opentelemetry tracer and
call any SDK code that is compatible with azure-core tracing. This is an example
using Azure Monitor exporter, but you can use any exporter (Zipkin, etc.).

```python
from opentelemetry.ext.azure_monitor import AzureMonitorSpanExporter

from opentelemetry import trace
from opentelemetry.sdk.trace import Tracer

from azure.core.settings import settings
from azure.core.tracing.ext.opentelemetry_span import OpenTelemetrySpan

from azure.storage.blob import BlobServiceClient

# Declare that you want to trace Azure SDK with OpenTelemetry
settings.tracing_implementation = OpenTelemetrySpan

exporter = AzureMonitorSpanExporter(
    instrumentation_key="uuid of the instrumentation key (see your Azure Monitor account)"
)

trace.set_preferred_tracer_implementation(lambda T: Tracer())
tracer = trace.tracer()
tracer.add_span_processor(
    SimpleExportSpanProcessor(exporter)
)

with tracer.start_as_current_span(name="MyApplication"):
    client = BlobServiceClient.from_connection_string('connectionstring')
    client.delete_container('mycontainer')  # Call will be traced
```


## Troubleshooting

This client raises exceptions defined in [Azure Core](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/core/azure-core/docs/exceptions.md).


## Next steps

More documentation on OpenTelemetry configuration can be found on the [OpenTelemetry website](https://opentelemetry.io)


## Contributing
This project welcomes contributions and suggestions.  Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit https://cla.microsoft.com.

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/). For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.
