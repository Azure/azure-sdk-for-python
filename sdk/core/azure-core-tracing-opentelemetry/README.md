

# Azure Core Tracing OpenTelemetry client library for Python

## Getting started

You can enable distributed tracing in Azure client libraries by configuring the OpenTelemetry SDK.
OpenTelemetry is a popular open-source observability framework for generating, capturing, and collecting telemetry data for cloud-native software.

There are two key concepts related to tracing: span and trace. A span represents a single operation in a trace. A span can represent an HTTP request,
a remote procedure call (RPC), a database query, or even the path that your code takes. A trace is a tree of spans showing the path of work through
a system. You can distinguish a trace on its own by a unique 16-byte sequence called a TraceID. For more information on these concepts and how they
relate to OpenTelemetry, see the [OpenTelemetry documentation](https://opentelemetry.io/docs/).

## Tracing with Azure Monitor OpenTelemetry Distro

[Azure Monitor OpenTelemetry Distro](https://learn.microsoft.com/azure/azure-monitor/app/opentelemetry-enable?tabs=python) supports tracing for Azure
SDKs by default. Just install and configure the distro and use Azure clients as usual.

```python

# Enable Azure Monitor OpenTelemetry Distro
# It confiures Azure SDKs to use OpenTelemetry as well
from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry import trace

configure_azure_monitor(
   connection_string="<your-connection-string>"
)

# Use Azure SDKs as usual, here as an example with Storage SDKs
# you may also report your own spans for it.
from azure.storage.blob import BlobServiceClient

tracer = trace.get_tracer(__name__)
with tracer.start_as_current_span(name="MyApplication"):
    client = BlobServiceClient.from_connection_string('connectionstring')
    client.create_container('my_container')  # Call will be traced
```

The Azure Monitor OpenTelemetry Distro can be found in the [`azure-monitor-opentelemetry`](https://pypi.org/project/azure-monitor-opentelemetry) package.

## Tracing with generic OpenTelemetry

Check out your observability provider documentation on how to enable distributed tracing with OpenTelemetry
or follow [OpenTelemetry Python documentation](https://opentelemetry.io/docs/languages/python/) on generic configuration.

In addition to common OpenTelemetry configuration, follow this steps to configure Azure SDKs:

1. Install the Azure Core OpenTelemetry Tracing plugin for Python with [pip](https://pypi.org/project/pip/):

   ```bash
   pip install azure-core-tracing-opentelemetry
   ```

  Now you can use Azure Core OpenTelemetry Tracing plugin for Python as usual with any SDKs that are compatible
  with azure-core tracing. This includes (not exhaustive list), `azure-storage-blob`, `azure-keyvault-secrets`, `azure-eventhub`, etc.

2. Specify which tracing implementation Azure SDK should use in one of the following ways:
   - By setting `AZURE_SDK_TRACING_IMPLEMENTATION` environment variable to `opentelemetry`
     (just make sure you use a fresh version of `azure-core` and `azure-core-tracing-opentelemetry`)

     ```bash
     AZURE_SDK_TRACING_IMPLEMENTATION=opentelemetry
     ```

   - Alternatively, you can set it up in the code:

     ```python
     from azure.core.settings import settings
     settings.tracing_implementation = "opentelemetry"
     ```

This configuration instructs Azure SDK clients to emit spans using global OpenTelemetry instance and
corresponding tracer provider.

There is no need to write any additional code to trace Azure SDK calls or pass trace context explicitly -
Azure SDKs and OpenTelemetry will do it for you.

Here's a full example:

```python

# Declare OpenTelemetry as enabled tracing plugin for Azure SDKs
from azure.core.settings import settings

settings.tracing_implementation = "opentelemetry"

# In the below example, we use a simple console exporter.

# See https://opentelemetry.io/docs/languages/python/ for more details on OpenTelemetry configuration

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter
from opentelemetry.sdk.trace.export import SimpleSpanProcessor

# Simple console exporter
exporter = ConsoleSpanExporter()

trace.set_tracer_provider(TracerProvider())
trace.get_tracer_provider().add_span_processor(
    SimpleSpanProcessor(exporter)
)

# Example with Storage SDKs

from azure.storage.blob import BlobServiceClient

tracer = trace.get_tracer(__name__)
with tracer.start_as_current_span(name="MyApplication"):
    client = BlobServiceClient.from_connection_string('connectionstring')
    client.create_container('my_container')  # Call will be traced
```

## HTTP instrumentation

With the Azure Core OpenTelemetry Tracing plugin enabled, HTTP requests made by Azure SDK clients are typically instrumented via the [`DistributedTracingPolicy`](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/azure/core/pipeline/policies/_distributed_tracing.py) automatically. Since Azure Core handles HTTP instrumentation for Azure service calls, automatic HTTP instrumentation from other libraries such as `opentelemetry-requests-instrumentation` are suppressed to avoid duplicate spans from being created.

## Troubleshooting

This client raises exceptions defined in [Azure Core](https://learn.microsoft.com/python/api/azure-core/azure.core.exceptions?view=azure-python).

## Contributing

This project welcomes contributions and suggestions.  Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit https://cla.microsoft.com.

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/). For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.
