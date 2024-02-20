

# Azure Core Tracing OpenTelemetry client library for Python

## Getting started

### Install the package

Install the Azure Core OpenTelemetry Tracing plugin for Python with [pip](https://pypi.org/project/pip/):

```bash
pip install azure-core-tracing-opentelemetry
```

Now you can use OpenTelemetry for Python as usual with any SDKs that are compatible
with azure-core tracing. This includes (not exhaustive list), azure-storage-blob, azure-keyvault-secrets, azure-eventhub, etc.

## Key concepts

* You don't need to pass any context, SDK will get it for you
* There are two ways to enable the tracing plugin in code:

  ```python
  from azure.core.settings import settings
  from azure.core.tracing.ext.opentelemetry_span import OpenTelemetrySpan
  settings.tracing_implementation = OpenTelemetrySpan
  ```

  or

  ```python
  from azure.core.settings import settings
  settings.tracing_implementation = "opentelemetry"
  ```

* Alternatively, if you have the latest version of `azure-core` installed, you can also set the following environment variable to enable tracing with OpenTelemetry:

  ```bash
  AZURE_SDK_TRACING_IMPLEMENTATION=opentelemetry
  ```

## Examples

There is no explicit context to pass, you just create your usual opentelemetry tracer and
call any SDK code that is compatible with azure-core tracing. This is an example
using Azure Monitor exporter, but you can use any exporter (Zipkin, etc.).

```python

# Declare OpenTelemetry as enabled tracing plugin for Azure SDKs
from azure.core.settings import settings

settings.tracing_implementation = "opentelemetry"

# In the below example, we use a simple console exporter, uncomment these lines to use
# the OpenTelemetry exporter for Azure Monitor.
# Example of a trace exporter for Azure Monitor, but you can use anything OpenTelemetry supports
# from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter
# exporter = AzureMonitorTraceExporter(
#     connection_string="the connection string used for your Application Insights resource"
# )

# Regular open telemetry usage from here, see https://github.com/open-telemetry/opentelemetry-python
# for details
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter
from opentelemetry.sdk.trace.export import SimpleSpanProcessor

# Simple console exporter
exporter = ConsoleSpanExporter()

trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)
trace.get_tracer_provider().add_span_processor(
    SimpleSpanProcessor(exporter)
)

# Example with Storage SDKs

from azure.storage.blob import BlobServiceClient

with tracer.start_as_current_span(name="MyApplication"):
    client = BlobServiceClient.from_connection_string('connectionstring')
    client.create_container('my_container')  # Call will be traced
```

The Azure Monitor OpenTelemetry Exporter can be found in the [`azure-monitor-opentelemetry-exporter`](https://pypi.org/project/azure-monitor-opentelemetry-exporter/) package.


## HTTP instrumentation

With the Azure Core OpenTelemetry Tracing plugin enabled, HTTP requests made by Azure SDK clients are typically instrumented via the [`DistributedTracingPolicy`](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/azure/core/pipeline/policies/_distributed_tracing.py) automatically. Since Azure Core handles HTTP instrumentation for Azure service calls, automatic HTTP instrumentation from other libraries such as `opentelemetry-requests-instrumentation` are suppressed to avoid duplicate spans from being created.


## Troubleshooting

This client raises exceptions defined in [Azure Core](https://learn.microsoft.com/python/api/azure-core/azure.core.exceptions?view=azure-python).


## Next steps

More documentation on OpenTelemetry configuration can be found on the [OpenTelemetry website](https://opentelemetry.io)


## Contributing

This project welcomes contributions and suggestions.  Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit https://cla.microsoft.com.

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/). For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.
