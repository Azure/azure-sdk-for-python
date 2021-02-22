# Microsoft Opentelemetry exporter for Azure Monitor

[![Gitter chat](https://img.shields.io/gitter/room/Microsoft/azure-monitor-python)](https://gitter.im/Azure/azure-sdk-for-python)

The exporter for Azure Monitor allows you to export tracing data utilizing the OpenTelemetry SDK and send telemetry data to Azure Monitor for applications written in Python.

[Source code](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/monitor/azure-monitor-opentelemetry-exporter) | [Package (PyPi)][pypi] | [API reference documentation][api_docs] | [Product documentation][product_docs] || [Samples](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/monitor/azure-monitor-opentelemetry-exporter/samples) | [Changelog](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/monitor/azure-monitor-opentelemetry-exporter/CHANGELOG.md)

## Getting started

### Install the package

Install the Microsoft Opentelemetry exporter for Azure Monitor with [pip][pip]:

```Bash
pip install azure-monitor-opentelemetry-exporter --pre
```

### Prerequisites:
To use this package, you must have:
* Azure subscription - [Create a free account][azure_sub]
* Azure Monitor - [How to use application insights][application_insights_namespace]
* Opentelemetry SDK - [Opentelemtry SDK for Python][ot_sdk_python]
* Python 3.5 or later - [Install Python][python]

### Authenticate the client

Interaction with Azure monitor exporter starts with an instance of the `AzureMonitorTraceExporter` class. You will need a **connection_string** to instantiate the object.
Please find the samples linked below for demonstration as to how to authenticate using a connection string.

#### [Create Exporter from connection string][sample_authenticate_client_connstr]

```Python
from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter
exporter = AzureMonitorTraceExporter.from_connection_string(
    connection_string = os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"]
)
```

You can also instantiate the exporter directly via the constructor. In this case, the connection string will be automatically populated from the `APPLICATIONINSIGHTS_CONNECTION_STRING` environment variable.

```python
from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter
exporter = AzureMonitorTraceExporter()
```

## Key concepts

Some of the key concepts for the Azure monitor exporter include:

* [Opentelemetry][opentelemtry_spec]: Opentelemetry is a set of libraries used to collect and export telemetry data (metrics, logs, and traces) for analysis in order to understand your software's performance and behavior.

* [Instrumentation][instrumentation_library]: The ability to call the opentelemetry API directly by any application is facilitated by instrumentaton. A library that enables OpenTelemetry observability for another library is called an Instrumentation Library.

* [Trace][trace_concept]: Trace refers to distributed tracing. It can be thought of as a directed acyclic graph (DAG) of Spans, where the edges between Spans are defined as parent/child relationship.

* [Tracer Provider][tracer_provider]: Provides a `Tracer` for use by the given instrumentation library.

* [Span Processor][span_processor]: A span processor allows hooks for SDK's `Span` start and end method invocations. Follow the link for more information.

* [Sampling][sampler_ref]: Sampling is a mechanism to control the noise and overhead introduced by OpenTelemetry by reducing the number of samples of traces collected and sent to the backend.

* [AzureMonitorTraceExporter][client_reference]: This is the class that is initialized to send tracing related telemetry to Azure Monitor.

For more information about these resources, see [What is Azure Monitor?][product_docs].

## Examples

The following sections provide several code snippets covering some of the most common tasks, including:

* [Exporting a custom span](#export-hello-world-trace)
* [Using an instrumentation to track a library](#instrumentation-with-requests-library)

### Export Hello World Trace

```Python
import os
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchExportSpanProcessor
from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter

exporter = AzureMonitorTraceExporter.from_connection_string(
    connection_string = os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING "]
)

trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)
span_processor = BatchExportSpanProcessor(exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

with tracer.start_as_current_span("hello"):
    print("Hello, World!")
```

### Instrumentation with requests library

OpenTelemetry also supports several instrumentations which allows to instrument with third party libraries.

This example shows how to instrument with the [requests](https://pypi.org/project/requests/) library.

* Install the requests integration package using pip install opentelemetry-instrumentation-requests.

```Python
import os
import requests
from opentelemetry import trace
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchExportSpanProcessor

from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter

trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)

# This line causes your calls made with the requests library to be tracked.
RequestsInstrumentor().instrument()
span_processor = BatchExportSpanProcessor(
    AzureMonitorTraceExporter.from_connection_string(
        os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING "]
    )
)
trace.get_tracer_provider().add_span_processor(span_processor)

RequestsInstrumentor().instrument()

# This request will be traced
response = requests.get(url="https://azure.microsoft.com/")
```

## Troubleshooting

The exporter raises exceptions defined in [Azure Core](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/core/azure-core/README.md#azure-core-library-exceptions).

## Next steps

### More sample code

Please find further examples in the [samples](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/monitor/azure-monitor-opentelemetry-exporter/samples) directory demonstrating common scenarios.

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
[api_docs]: https://azuresdkdocs.blob.core.windows.net/$web/python/azure-opentelemetry-exporter-azuremonitor/1.0.0b2/index.html
[product_docs]: https://docs.microsoft.com/azure/azure-monitor/overview
[azure_portal]: https://portal.azure.com
[azure_sub]: https://azure.microsoft.com/free/
[cloud_shell]: https://docs.microsoft.com/azure/cloud-shell/overview
[cloud_shell_bash]: https://shell.azure.com/bash
[pip]: https://pypi.org/project/pip/
[pypi]: https://pypi.org/project/azure-opentelemetry-exporter-azuremonitor
[python]: https://www.python.org/downloads/
[venv]: https://docs.python.org/3/library/venv.html
[virtualenv]: https://virtualenv.pypa.io
[ot_sdk_python]: https://github.com/open-telemetry/opentelemetry-python
[application_insights_namespace]: https://docs.microsoft.com/azure/azure-monitor/app/app-insights-overview#how-do-i-use-application-insights
[trace_concept]: https://github.com/open-telemetry/opentelemetry-specification/blob/master/specification/overview.md#trace
[client_reference]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/monitor/azure-monitor-opentelemetry-exporter/azure/monitor/opentelemetry/exporter/export/trace/_exporter.py#L30
[opentelemtry_spec]: https://opentelemetry.io/
[instrumentation_library]: https://github.com/open-telemetry/opentelemetry-specification/blob/master/specification/overview.md#instrumentation-libraries
[tracer_provider]: https://opentelemetry-python.readthedocs.io/en/stable/api/trace.html?highlight=TracerProvider#opentelemetry.trace.TracerProvider
[span_processor]: https://opentelemetry-python.readthedocs.io/en/stable/_modules/opentelemetry/sdk/trace.html?highlight=SpanProcessor#
[sampler_ref]: https://github.com/open-telemetry/opentelemetry-specification/blob/master/specification/trace/sdk.md#sampling

[sample_authenticate_client_connstr]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/monitor/azure-monitor-opentelemetry-exporter/samples/traces/sample_trace.py
