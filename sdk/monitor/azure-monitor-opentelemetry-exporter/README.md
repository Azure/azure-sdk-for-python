# Microsoft Opentelemetry exporter for Azure Monitor

[![Gitter chat](https://img.shields.io/gitter/room/Microsoft/azure-monitor-python)](https://gitter.im/Azure/azure-sdk-for-python)

The exporter for Azure Monitor allows you to export data utilizing the OpenTelemetry SDK and send telemetry data to Azure Monitor for applications written in Python.

[Source code](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/monitor/azure-monitor-opentelemetry-exporter) | [Package (PyPi)][pypi] | [API reference documentation][api_docs] | [Product documentation][product_docs] | [Samples](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/monitor/azure-monitor-opentelemetry-exporter/samples) | [Changelog](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-opentelemetry-exporter/CHANGELOG.md)

## Getting started

### Install the package

Install the Microsoft Opentelemetry exporter for Azure Monitor with [pip][pip]:

```Bash
pip install azure-monitor-opentelemetry-exporter --pre
```

### Prerequisites

To use this package, you must have:

* Azure subscription - [Create a free account][azure_sub]
* Azure Monitor - [How to use application insights][application_insights_namespace]
* Opentelemetry SDK - [Opentelemtry SDK for Python][ot_sdk_python]
* Python 3.6 or later - [Install Python][python]

### Instantiate the client

Interaction with Azure monitor exporter starts with an instance of the `AzureMonitorTraceExporter` class for distributed tracing, `AzureMonitorLogExporter` for logging and `AzureMonitorMetricExporter` for metrics. You will need a **connection_string** to instantiate the object.
Please find the samples linked below for demonstration as to how to construct the exporter using a connection string.

#### Logging

NOTE: The logging signal for the `AzureMonitorLogExporter` is currently in an EXPERIMENTAL state. Possible breaking changes may ensue in the future.

```Python
from azure.monitor.opentelemetry.exporter import AzureMonitorLogExporter
exporter = AzureMonitorLogExporter.from_connection_string(
    conn_str = os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"]
)
```

#### Metrics

```Python
from azure.monitor.opentelemetry.exporter import AzureMonitorMetricExporter
exporter = AzureMonitorMetricExporter.from_connection_string(
    conn_str = os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"]
)

```

#### Tracing

```Python
from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter
exporter = AzureMonitorTraceExporter.from_connection_string(
    conn_str = os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"]
)
```

You can also instantiate the exporter directly via the constructor. In this case, the connection string will be automatically populated from the `APPLICATIONINSIGHTS_CONNECTION_STRING` environment variable.

```python
from azure.monitor.opentelemetry.exporter import AzureMonitorLogExporter
exporter = AzureMonitorLogExporter()
```

```python
from azure.monitor.opentelemetry.exporter import AzureMonitorMetricExporter
exporter = AzureMonitorMetricExporter()
```

```python
from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter
exporter = AzureMonitorTraceExporter()
```

## Key concepts

Some of the key concepts for the Azure monitor exporter include:

* [Opentelemetry][opentelemtry_spec]: Opentelemetry is a set of libraries used to collect and export telemetry data (metrics, logs, and traces) for analysis in order to understand your software's performance and behavior.

* [Instrumentation][instrumentation_library]: The ability to call the opentelemetry API directly by any application is facilitated by instrumentation. A library that enables OpenTelemetry observability for another library is called an instrumentation Library.

* [Log][log_concept]: Log refers to capturing of logging, exception and events.

* [LogRecord][log_record]: Represents a log record emitted from a supported logging library.

* [LogEmitter][log_emitter]: Converts a `LogRecord` into a readable `LogData`, and will be pushed through the SDK to be exported.

* [LogEmitter Provider][log_emitter_provider]: Provides a `LogEmitter` for the given instrumentation library.

* [LogProcessor][log_processor]: Inteface to hook the log record emitting action.

* [LoggingHandler][logging_handler]: A handler class which writes logging records in OpenTelemetry format from the standard Python `logging` library.

* [AzureMonitorLogExporter][log_reference]: This is the class that is initialized to send logging related telemetry to Azure Monitor.

* [Metric][metric_concept]: `Metric` refers to recording raw measurements with predefined aggregation and sets of attributes for a period in time.

* [Measurement][measurement]: Represents a data point recorded at a point in time.

* [Instrument][instrument]: Instruments are used to report `Measurement`s.

* [Meter][meter]: The `Meter` is responsible for creating `Instruments`.

* [Meter Provider][meter_provider]: Provides a `Meter` for the given instrumentation library.

* [Metric Reader][metric_reader]: An SDK implementation object that provides the common configurable aspects of the OpenTelemetry Metrics SDK such as collection, flushing and shutdown.

* [AzureMonitorMetricExporter][metric_reference]: This is the class that is initialized to send metric related telemetry to Azure Monitor.

* [Trace][trace_concept]: Trace refers to distributed tracing. A distributed trace is a set of events, triggered as a result of a single logical operation, consolidated across various components of an application.

* [Span][span]: Represents a single operation within a `Trace`. Can be nested to form a trace tree. Each trace contains a root span, which typically describes the entire operation and, optionally, one ore more sub-spans for its sub-operations.

* [Tracer][tracer]: Responsible for creating `Span`s.

* [Tracer Provider][tracer_provider]: Provides a `Tracer` for use by the given instrumentation library.

* [Span Processor][span_processor]: A span processor allows hooks for SDK's `Span` start and end method invocations. Follow the link for more information.

* [AzureMonitorTraceExporter][trace_reference]: This is the class that is initialized to send tracing related telemetry to Azure Monitor.

* [Sampling][sampler_ref]: Sampling is a mechanism to control the noise and overhead introduced by OpenTelemetry by reducing the number of samples of traces collected and sent to the backend.

For more information about these resources, see [What is Azure Monitor?][product_docs].

## Examples

### Logging

The following sections provide several code snippets covering some of the most common tasks, including:

* [Exporting a log record](#export-hello-world-log)
* [Exporting correlated log record](#export-correlated-log)
* [Exporting log record with custom properties](#export-custom-properties-log)
* [Exporting an exceptions log record](#export-exceptions-log)

#### Export Hello World Log

```Python
import os
import logging

from opentelemetry.sdk._logs import (
    LogEmitterProvider,
    LoggingHandler,
    set_log_emitter_provider,
)
from opentelemetry.sdk._logs.export import BatchLogProcessor

from azure.monitor.opentelemetry.exporter import AzureMonitorLogExporter

log_emitter_provider = LogEmitterProvider()
set_log_emitter_provider(log_emitter_provider)

exporter = AzureMonitorLogExporter.from_connection_string(
    os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"]
)

log_emitter_provider.add_log_processor(BatchLogProcessor(exporter))
handler = LoggingHandler()

# Attach LoggingHandler to root logger
logging.getLogger().addHandler(handler)
logging.getLogger().setLevel(logging.NOTSET)

logger = logging.getLogger(__name__)

logger.warning("Hello World!")
```

#### Export Correlated Log

```Python
import os
import logging

from opentelemetry import trace
from opentelemetry.sdk._logs import (
    LogEmitterProvider,
    LoggingHandler,
    set_log_emitter_provider,
)
from opentelemetry.sdk._logs.export import BatchLogProcessor
from opentelemetry.sdk.trace import TracerProvider

from azure.monitor.opentelemetry.exporter import AzureMonitorLogExporter

trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)
log_emitter_provider = LogEmitterProvider()
set_log_emitter_provider(log_emitter_provider)

exporter = AzureMonitorLogExporter.from_connection_string(
    os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"]
)

log_emitter_provider.add_log_processor(BatchLogProcessor(exporter))
handler = LoggingHandler()

# Attach LoggingHandler to root logger
logging.getLogger().addHandler(handler)
logging.getLogger().setLevel(logging.NOTSET)

logger = logging.getLogger(__name__)

logger.info("INFO: Outside of span")
with tracer.start_as_current_span("foo"):
    logger.warning("WARNING: Inside of span")
logger.error("ERROR: After span")
```

#### Export Custom Properties Log

```Python
import os
import logging

from opentelemetry.sdk._logs import (
    LogEmitterProvider,
    LoggingHandler,
    set_log_emitter_provider,
)
from opentelemetry.sdk._logs.export import BatchLogProcessor

from azure.monitor.opentelemetry.exporter import AzureMonitorLogExporter

log_emitter_provider = LogEmitterProvider()
set_log_emitter_provider(log_emitter_provider)

exporter = AzureMonitorLogExporter.from_connection_string(
    os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"]
)

log_emitter_provider.add_log_processor(BatchLogProcessor(exporter))
handler = LoggingHandler()

# Attach LoggingHandler to root logger
logging.getLogger().addHandler(handler)
logging.getLogger().setLevel(logging.NOTSET)

logger = logging.getLogger(__name__)

# Custom properties
logger.debug("DEBUG: Debug with properties", extra={"debug": "true"})
```

#### Export Exceptions Log

```Python
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""
An example showing how to export exception telemetry using the AzureMonitorLogExporter.
"""
import os
import logging

from opentelemetry.sdk._logs import (
    LogEmitterProvider,
    LoggingHandler,
    get_log_emitter_provider,
    set_log_emitter_provider,
)
from opentelemetry.sdk._logs.export import BatchLogProcessor

from azure.monitor.opentelemetry.exporter import AzureMonitorLogExporter

set_log_emitter_provider(LogEmitterProvider())
exporter = AzureMonitorLogExporter.from_connection_string(
    os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"]
)
get_log_emitter_provider().add_log_processor(BatchLogProcessor(exporter))

# Attach LoggingHandler to namespaced logger
handler = LoggingHandler()
logger = logging.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.NOTSET)

# The following code will generate two pieces of exception telemetry
# that are identical in nature
try:
    val = 1 / 0
    print(val)
except ZeroDivisionError:
    logger.exception("Error: Division by zero")

try:
    val = 1 / 0
    print(val)
except ZeroDivisionError:
    logger.error("Error: Division by zero", stack_info=True, exc_info=True)
```

### Metrics

The following sections provide several code snippets covering some of the most common tasks, including:

* [Using different metric instruments](#metric-instrument-usage)

#### Metric instrument usage

```python
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""
An example to show an application using all instruments in the OpenTelemetry SDK. Metrics created
and recorded using the sdk are tracked and telemetry is exported to application insights with the
AzureMonitorMetricsExporter.
"""
import os
from typing import Iterable

from opentelemetry import metrics
from opentelemetry.metrics import CallbackOptions, Observation
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader

from azure.monitor.opentelemetry.exporter import AzureMonitorMetricExporter

exporter = AzureMonitorMetricExporter.from_connection_string(
    os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"]
)
reader = PeriodicExportingMetricReader(exporter, export_interval_millis=5000)
metrics.set_meter_provider(MeterProvider(metric_readers=[reader]))

# Create a namespaced meter
meter = metrics.get_meter_provider().get_meter("sample")

# Callback functions for observable instruments
def observable_counter_func(options: CallbackOptions) -> Iterable[Observation]:
    yield Observation(1, {})


def observable_up_down_counter_func(
    options: CallbackOptions,
) -> Iterable[Observation]:
    yield Observation(-10, {})


def observable_gauge_func(options: CallbackOptions) -> Iterable[Observation]:
    yield Observation(9, {})

# Counter
counter = meter.create_counter("counter")
counter.add(1)

# Async Counter
observable_counter = meter.create_observable_counter(
    "observable_counter", [observable_counter_func]
)

# UpDownCounter
updown_counter = meter.create_up_down_counter("updown_counter")
updown_counter.add(1)
updown_counter.add(-5)

# Async UpDownCounter
observable_updown_counter = meter.create_observable_up_down_counter(
    "observable_updown_counter", [observable_up_down_counter_func]
)

# Histogram
histogram = meter.create_histogram("histogram")
histogram.record(99.9)

# Async Gauge
gauge = meter.create_observable_gauge("gauge", [observable_gauge_func])

```

### Tracing

The following sections provide several code snippets covering some of the most common tasks, including:

* [Exporting a custom span](#export-hello-world-trace)
* [Using an instrumentation to track a library](#instrumentation-with-requests-library)

#### Export Hello World Trace

```Python
import os
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter

exporter = AzureMonitorTraceExporter.from_connection_string(
    connection_string = os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING "]
)

trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)
span_processor = BatchSpanProcessor(exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

with tracer.start_as_current_span("hello"):
    print("Hello, World!")
```

#### Instrumentation with requests library

OpenTelemetry also supports several instrumentations which allows to instrument with third party libraries.

This example shows how to instrument with the [requests](https://pypi.org/project/requests/) library.

* Install the requests integration package using pip install opentelemetry-instrumentation-requests.

```Python
import os
import requests
from opentelemetry import trace
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter

trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)

# This line causes your calls made with the requests library to be tracked.
RequestsInstrumentor().instrument()
span_processor = BatchSpanProcessor(
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

The exporter raises exceptions defined in [Azure Core](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/README.md#azure-core-library-exceptions).

## Next steps

### More sample code

Please find further examples in the [samples](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/monitor/azure-monitor-opentelemetry-exporter/samples) directory demonstrating common scenarios.

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
[pypi]: https://pypi.org/project/azure-monitor-opentelemetry-exporter/
[python]: https://www.python.org/downloads/
[venv]: https://docs.python.org/3/library/venv.html
[virtualenv]: https://virtualenv.pypa.io
[ot_sdk_python]: https://github.com/open-telemetry/opentelemetry-python
[application_insights_namespace]: https://docs.microsoft.com/azure/azure-monitor/app/app-insights-overview#how-do-i-use-application-insights
[opentelemtry_spec]: https://opentelemetry.io/
[instrumentation_library]: https://github.com/open-telemetry/opentelemetry-specification/blob/master/specification/overview.md#instrumentation-libraries
[log_concept]: https://github.com/open-telemetry/opentelemetry-specification/blob/main/specification/overview.md#log-signal
[log_record]: https://opentelemetry-python.readthedocs.io/en/stable/sdk/logs.html#opentelemetry.sdk._logs.LogRecord
[log_emitter]: https://opentelemetry-python.readthedocs.io/en/stable/sdk/logs.html#opentelemetry.sdk._logs.LogEmitter
[log_emitter_provider]: https://opentelemetry-python.readthedocs.io/en/stable/sdk/logs.html#opentelemetry.sdk._logs.LogEmitterProvider
[log_processor]: https://opentelemetry-python.readthedocs.io/en/stable/sdk/logs.html#opentelemetry.sdk._logs.LogProcessor
[logging_handler]: https://opentelemetry-python.readthedocs.io/en/stable/sdk/logs.html#opentelemetry.sdk._logs.LoggingHandler
[log_reference]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-opentelemetry-exporter/azure/monitor/opentelemetry/exporter/export/logs/_exporter.py
[metric_concept]: https://github.com/open-telemetry/opentelemetry-specification/blob/main/specification/overview.md#metric-signal
[measurement]: https://github.com/open-telemetry/opentelemetry-specification/blob/main/specification/metrics/api.md#measurement
[instrument]: https://github.com/open-telemetry/opentelemetry-specification/blob/main/specification/metrics/api.md#instrument
[meter]: https://github.com/open-telemetry/opentelemetry-specification/blob/main/specification/metrics/api.md#meter
[meter_provider]: https://github.com/open-telemetry/opentelemetry-specification/blob/main/specification/metrics/api.md#meterprovider
[metric_reader]:https://github.com/open-telemetry/opentelemetry-specification/blob/main/specification/metrics/sdk.md#metricreader
[metric_reference]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-opentelemetry-exporter/azure/monitor/opentelemetry/exporter/export/metrics/_exporter.py
[trace_concept]: https://github.com/open-telemetry/opentelemetry-specification/blob/main/specification/overview.md#tracing-signal
[span]: https://opentelemetry-python.readthedocs.io/en/stable/api/trace.html?highlight=TracerProvider#opentelemetry.trace.Span
[tracer]: https://opentelemetry-python.readthedocs.io/en/stable/api/trace.html?highlight=TracerProvider#opentelemetry.trace.Tracer
[tracer_provider]: https://opentelemetry-python.readthedocs.io/en/stable/api/trace.html?highlight=TracerProvider#opentelemetry.trace.TracerProvider
[span_processor]: https://opentelemetry-python.readthedocs.io/en/stable/_modules/opentelemetry/sdk/trace.html?highlight=SpanProcessor#
[trace_reference]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-opentelemetry-exporter/azure/monitor/opentelemetry/exporter/export/trace/_exporter.py
[sampler_ref]: https://github.com/open-telemetry/opentelemetry-specification/blob/master/specification/trace/sdk.md#sampling
