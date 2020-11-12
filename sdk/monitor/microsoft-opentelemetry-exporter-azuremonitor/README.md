# Microsoft Opentelemtry Exporter for Azure Monitor client library for Python

The Exporter for Azure Monitor allows you to export tracing data utilizing the OpenTelemetry Python Client and send telemetry data to Azure Monitor written in Python.

[Source code](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/monitor/microsoft-opentelemetry-exporter-azuremonitor) | [Package (PyPi)][pypi] | [API reference documentation][api_docs] | [Product documentation][product_docs] | [Samples](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/monitor/microsoft-opentelemetry-exporter-azuremonitor/samples) | [Changelog](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/monitor/microsoft-opentelemetry-exporter-azuremonitor/CHANGELOG.md)

> **NOTE**: This is the preview for the next major version of the [`opentelemetry-azure-monitor-python`](https://github.com/microsoft/opentelemetry-azure-monitor-python).

## Getting started

### Install the package

Install the Microsoft Opentelemetry Exporter Azure Monitor client library for Python with [pip][pip]:

```Bash
pip install microsoft-opentelemetry-exporter-azuremonitor --pre
```

### Prerequisites: 
To use this package, you must have:
* Azure subscription - [Create a free account][azure_sub]
* Azure Monitor - [How to use application insights][application_insights_namespace]
* Opentelemetry SDK - [Opentelemtry SDK for Python][ot_sdk_python]
* Python 3.5 or later - [Install Python][python]

### Authenticate the client

Interaction with Azure monitor exporter starts with an instance of the `AzureMonitorSpanExporter` class. You will need an **instrumentation_key** or a **connection_string** to instantiate the object.
The priority of which value takes on the instrumentation key is:
* Key from explicitly passed in connection string
* Key from explicitly passed in instrumentation key
* Key from connection string in environment variable
* Key from instrumentation key in environment variable
Please find the samples linked below for demonstration as to how to authenticate via either approach.

#### [Create Exporter from connection string][sample_authenticate_client_connstr]

```Python
from microsoft.opentelemetry.exporter.azuremonitor import AzureMonitorSpanExporter
exporter = AzureMonitorSpanExporter(
    connection_string = os.environ["AZURE_MONITOR_CONNECTION_STRING"]
)
```

#### Create Exporter using the instrumentation key:

```Python
from microsoft.opentelemetry.exporter.azuremonitor import AzureMonitorSpanExporter
exporter = AzureMonitorSpanExporter(
    instrumentation_key = os.environ["AZURE_MONITOR_INSTRUMENTATION_KEY"]
)
```

## Key concepts

Some of the key concepts for the Azure monitor exporter include:

* [Opentelemetry][opentelemtry_spec]: Opentelemetry is a tool to instrument, generate, collect, and export telemetry data (metrics, logs, and traces) for analysis in order to understand your software's performance and behavior.

* [Trace][trace_concept]: Trace can be thought of as a directed acyclic graph (DAG) of Spans, where the edges between Spans are defined as parent/child relationship.

* [AzureMonitorSpanExporter][client_reference]: This is the object a user should first initialize to connect the namespace to send trace data.

* [Exporter Options][exporter_options]: Options to configure Azure exporters. Includes connection_string, instrumentation_key, proxies, timeout etc.

For more information about these resources, see [What is Azure Monitor?][product_docs].

## Examples

The following sections provide several code snippets covering some of the most common tasks, including:

* [Export hello world trace data](#export-hello-world-trace)
* [Batch Export Spans](#batch-export-span-processor)


### Export Hello World Trace

```Python
import os
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchExportSpanProcessor
from microsoft.opentelemetry.exporter.azuremonitor import AzureMonitorSpanExporter

# Callback function to add os_type: linux to span properties
def callback_function(envelope):
    envelope.data.base_data.properties["os_type"] = "linux"
    return True

exporter = AzureMonitorSpanExporter(
    connection_string = os.environ["AZURE_MONITOR_CONNECTION_STRING"]
)
exporter.add_telemetry_processor(callback_function)

trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)
span_processor = BatchExportSpanProcessor(exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

with tracer.start_as_current_span("hello"):
    print("Hello, World!")
```

### Batch Export Span Processor

```Python
import os
import requests
from opentelemetry import trace
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchExportSpanProcessor

from microsoft.opentelemetry.exporter.azuremonitor import AzureMonitorSpanExporter

trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)
RequestsInstrumentor().instrument()
span_processor = BatchExportSpanProcessor(
    AzureMonitorSpanExporter(
        connection_string = os.environ["AZURE_MONITOR_CONNECTION_STRING"]
    )
)
trace.get_tracer_provider().add_span_processor(span_processor)
```

## Troubleshooting

### Logging

- Enable by setting `logging_enable=True` when creating the client.

## Next steps

### More sample code

Please find further examples in the [samples](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/monitor/microsoft-opentelemetry-exporter-azuremonitor/samples) directory demonstrating common scenarios.

### Additional documentation

For more extensive documentation on the Azure Monitor service, see the [Azure Monitor documentation][product_docs] on docs.microsoft.com.

For detailed overview of Opentelemetry, visit their [overview](https://github.com/open-telemetry/opentelemetry-specification/blob/master/specification/overview.md) page.

## Contributing

This project welcomes contributions and suggestions.  Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit https://cla.microsoft.com.

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide
a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions
provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

<!-- LINKS -->
[azure_cli]: https://docs.microsoft.com/cli/azure
[api_docs]: https://azuresdkdocs.blob.core.windows.net/$web/python/microsoft-opentelemetry-exporter-azuremonitor/latest/index.html
[product_docs]: https://docs.microsoft.com/azure/azure-monitor/overview
[azure_portal]: https://portal.azure.com
[azure_sub]: https://azure.microsoft.com/free/
[cloud_shell]: https://docs.microsoft.com/azure/cloud-shell/overview
[cloud_shell_bash]: https://shell.azure.com/bash
[pip]: https://pypi.org/project/pip/
[pypi]: https://pypi.org/project/microsoft-opentelemetry-exporter-azuremonitor/#history
[python]: https://www.python.org/downloads/
[venv]: https://docs.python.org/3/library/venv.html
[virtualenv]: https://virtualenv.pypa.io
[ot_sdk_python]: https://github.com/open-telemetry/opentelemetry-python
[application_insights_namespace]: https://docs.microsoft.com/azure/azure-monitor/app/app-insights-overview#how-do-i-use-application-insights
[exporter_options]: https://opentelemetry-azure-monitor-python.readthedocs.io/en/latest/azure_monitor/export/export.options.html?highlight=options
[trace_concept]: https://github.com/open-telemetry/opentelemetry-specification/blob/master/specification/overview.md#trace
[client_reference]: https://opentelemetry-azure-monitor-python.readthedocs.io/en/latest/azure_monitor/export/export.trace.html#module-azure_monitor.export.trace
[opentelemtry_spec]: https://opentelemetry.io/

[sample_authenticate_client_connstr]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/monitor/microsoft-opentelemetry-exporter-azuremonitor/samples/traces/trace.py#L18
