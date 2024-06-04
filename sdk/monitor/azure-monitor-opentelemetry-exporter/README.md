# Microsoft OpenTelemetry exporter for Azure Monitor

The exporter for Azure Monitor allows Python applications to export data from the OpenTelemetry SDK to Azure Monitor. The exporter is intended for users who require advanced configuration or have more complicated telemetry needs that require all of distributed tracing, logging and metrics. If you have simpler configuration requirements, we recommend using the [Azure Monitor OpenTelemetry Distro](https://learn.microsoft.com/azure/azure-monitor/app/opentelemetry-enable?tabs=python) instead for a simpler one-line setup.

Prior to using this SDK, please read and understand [Data Collection Basics](https://learn.microsoft.com/azure/azure-monitor/app/opentelemetry-overview?tabs=python), especially the section on [telemetry types](https://learn.microsoft.com/azure/azure-monitor/app/opentelemetry-overview?tabs=python#telemetry-types). OpenTelemetry terminology differs from Application Insights terminology so it is important to understand the way the telemetry types map to each other.

[Source code](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/monitor/azure-monitor-opentelemetry-exporter) | [Package (PyPi)][pypi] | [API reference documentation][api_docs] | [Product documentation][product_docs] | [Samples][exporter_samples] | [Changelog](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-opentelemetry-exporter/CHANGELOG.md)

## Getting started

### Install the package

Install the Microsoft OpenTelemetry exporter for Azure Monitor with [pip][pip]:

```Bash
pip install azure-monitor-opentelemetry-exporter --pre
```

### Prerequisites

To use this package, you must have:

* Azure subscription - [Create a free account][azure_sub]
* Azure Monitor - [How to use application insights][application_insights_namespace]
* OpenTelemetry SDK - [OpenTelemetry SDK for Python][ot_sdk_python]
* Python 3.8 or later - [Install Python][python]

### Instantiate the client

Interaction with Azure monitor exporter starts with an instance of the `AzureMonitorTraceExporter` class for distributed tracing, `AzureMonitorLogExporter` for logging and `AzureMonitorMetricExporter` for metrics. You will need a **connection_string** to instantiate the object.
Please find the samples linked below for demonstration as to how to construct the exporter using a connection string.

#### Logging (experimental)

NOTE: The logging signal for the `AzureMonitorLogExporter` is currently in an EXPERIMENTAL state. Possible breaking changes may ensue in the future.

```python
from azure.monitor.opentelemetry.exporter import AzureMonitorLogExporter
exporter = AzureMonitorLogExporter(
    connection_string=os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"]
)
```

#### Metrics

```python
from azure.monitor.opentelemetry.exporter import AzureMonitorMetricExporter
exporter = AzureMonitorMetricExporter(
    connection_string=os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"]
)
```

#### Tracing

```python
from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter
exporter = AzureMonitorTraceExporter(
    connection_string=os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"]
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

* [OpenTelemetry][opentelemetry_spec]: OpenTelemetry is a set of libraries used to collect and export telemetry data (metrics, logs, and traces) for analysis in order to understand your software's performance and behavior.

* [Instrumentation][instrumentation_library]: The ability to call the OpenTelemetry API directly by any application is facilitated by instrumentation. A library that enables OpenTelemetry observability for another library is called an instrumentation Library.

* [Log][log_concept]: Log refers to capturing of logging, exception and events.

* [LogRecord][log_record]: Represents a log record emitted from a supported logging library.

* [Logger][logger]: Converts a `LogRecord` into a readable `LogData`, and will be pushed through the SDK to be exported.

* [Logger Provider][logger_provider]: Provides a `Logger` for the given instrumentation library.

* [LogRecordProcessor][log_record_processor]: Interface to hook the log record emitting action.

* [LoggingHandler][logging_handler]: A handler class which writes logging records in OpenTelemetry format from the standard Python `logging` library.

* [AzureMonitorLogExporter][log_reference]: This is the class that is initialized to send logging related telemetry to Azure Monitor.

* [Metric][metric_concept]: `Metric` refers to recording raw measurements with predefined aggregation and sets of attributes for a period in time.

* [Measurement][measurement]: Represents a data point recorded at a point in time.

* [Instrument][instrument]: Instruments are used to report `Measurement`s.

* [Meter][meter]: The `Meter` is responsible for creating `Instruments`.

* [Meter Provider][meter_provider]: Provides a `Meter` for the given instrumentation library.

* [Metric Reader][metric_reader]: An SDK implementation object that provides the common configurable aspects of the OpenTelemetry Metrics SDK such as collection, flushing and shutdown.

* [AzureMonitorMetricExporter][metric_reference]: This is the class that is initialized to send metric related telemetry to Azure Monitor.

* [Trace][trace_concept]: Trace refers to distributed tracing. A distributed trace is a set of events, triggered as a result of a single logical operation, consolidated across various components of an application. In particular, a Trace can be thought of as a directed acyclic graph (DAG) of Spans, where the edges between Spans are defined as parent/child relationship.

* [Span][span]: Represents a single operation within a `Trace`. Can be nested to form a trace tree. Each trace contains a root span, which typically describes the entire operation and, optionally, one ore more sub-spans for its sub-operations.

* [Tracer][tracer]: Responsible for creating `Span`s.

* [Tracer Provider][tracer_provider]: Provides a `Tracer` for use by the given instrumentation library.

* [Span Processor][span_processor]: A span processor allows hooks for SDK's `Span` start and end method invocations. Follow the link for more information.

* [AzureMonitorTraceExporter][trace_reference]: This is the class that is initialized to send tracing related telemetry to Azure Monitor.

* [Sampling][sampler_ref]: Sampling is a mechanism to control the noise and overhead introduced by OpenTelemetry by reducing the number of samples of traces collected and sent to the backend.

* ApplicationInsightsSampler: Application Insights specific sampler used for consistent sampling across Application Insights SDKs and OpenTelemetry-based SDKs sending data to Application Insights. This sampler MUST be used whenever `AzureMonitorTraceExporter` is used.

For more information about these resources, see [What is Azure Monitor?][product_docs].

## Configuration

All configuration options can be passed through the constructors of exporters through `kwargs`. Below is a list of configurable options.

* `connection_string`: The connection string used for your Application Insights resource.
* `disable_offline_storage`: Boolean value to determine whether to disable storing failed telemetry records for retry. Defaults to `False`.
* `storage_directory`: Storage directory in which to store retry files. Defaults to `<tempfile.gettempdir()>/Microsoft/AzureMonitor/opentelemetry-python-<your-instrumentation-key>`.
* `credential`: Token credential, such as ManagedIdentityCredential or ClientSecretCredential, used for [Azure Active Directory (AAD) authentication][aad_for_ai_docs]. Defaults to None. See [samples][exporter_samples] for examples.

## Examples

### Logging (experimental)

NOTE: The logging signal for the `AzureMonitorLogExporter` is currently in an EXPERIMENTAL state. Possible breaking changes may ensue in the future.

The following sections provide several code snippets covering some of the most common tasks, including:

* [Exporting a log record](#export-hello-world-log)
* [Exporting correlated log record](#export-correlated-log)
* [Exporting log record with custom properties](#export-custom-properties-log)
* [Exporting an exceptions log record](#export-exceptions-log)

Review the [OpenTelemetry Logging SDK][ot_logging_sdk] to learn how to use OpenTelemetry components to collect logs.

When integrating the `AzureMonitorLogExporter`, it's **strongly advised to utilize a named logger** rather
than the root logger.
This recommendation stems from the exporter's dependency on `azure-core` for constructing and dispatching requests.
Since `azure-core` itself uses a Python logger, attaching the handler to the root logger would
inadvertently capture and export these internal log messages as well.
This triggers a recursive loop of logging and exporting, leading to an unnecessary proliferation of log data.
To avoid this, configure a named logger for your application's logging needs or set up your logging handler to filter out logs originating from the SDK library.

#### Export Hello World Log

```python
"""
An example to show an application using Opentelemetry logging sdk. Logging calls to the standard Python
logging library are tracked and telemetry is exported to application insights with the AzureMonitorLogExporter.
"""
import os
import logging

from opentelemetry._logs import set_logger_provider
from opentelemetry.sdk._logs import (
    LoggerProvider,
    LoggingHandler,
)
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor

from azure.monitor.opentelemetry.exporter import AzureMonitorLogExporter

logger_provider = LoggerProvider()
set_logger_provider(logger_provider)

exporter = AzureMonitorLogExporter(
    connection_string=os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"]
)

logger_provider.add_log_record_processor(BatchLogRecordProcessor(exporter))

# Attach LoggingHandler to namespaced logger
handler = LoggingHandler()
logger = logging.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.NOTSET)

logger.warning("Hello World!")

# Telemetry records are flushed automatically upon application exit
# If you would like to flush records manually yourself, you can call force_flush()
logger_provider.force_flush()
```

#### Export Correlated Log

```python
"""
An example showing how to include context correlation information in logging telemetry.
"""
import os
import logging

from opentelemetry import trace
from opentelemetry._logs import set_logger_provider
from opentelemetry.sdk._logs import (
    LoggerProvider,
    LoggingHandler,
)
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.trace import TracerProvider

from azure.monitor.opentelemetry.exporter import AzureMonitorLogExporter

trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)
logger_provider = LoggerProvider()
set_logger_provider(logger_provider)

exporter = AzureMonitorLogExporter(
    connection_string=os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"]
)

logger_provider.add_log_record_processor(BatchLogRecordProcessor(exporter))

# Attach LoggingHandler to namespaced logger
handler = LoggingHandler()
logger = logging.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.NOTSET)

logger.info("INFO: Outside of span")
with tracer.start_as_current_span("foo"):
    logger.warning("WARNING: Inside of span")
logger.error("ERROR: After span")
```

#### Export Custom Properties Log

```python
"""
An example showing how to add custom properties to logging telemetry.
"""
import os
import logging

from opentelemetry._logs import set_logger_provider
from opentelemetry.sdk._logs import (
    LoggerProvider,
    LoggingHandler,
)
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor

from azure.monitor.opentelemetry.exporter import AzureMonitorLogExporter

logger_provider = LoggerProvider()
set_logger_provider(logger_provider)

exporter = AzureMonitorLogExporter(
    connection_string=os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"]
)

logger_provider.add_log_record_processor(BatchLogRecordProcessor(exporter))

# Attach LoggingHandler to namespaced logger
handler = LoggingHandler()
logger = logging.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.NOTSET)

# Custom properties
logger.debug("DEBUG: Debug with properties", extra={"debug": "true"})
```

#### Export Exceptions Log

```python
"""
An example showing how to export exception telemetry using the AzureMonitorLogExporter.
"""
import os
import logging

from opentelemetry._logs import (
    get_logger_provider,
    set_logger_provider,
)
from opentelemetry.sdk._logs import (
    LoggerProvider,
    LoggingHandler,
)
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor

from azure.monitor.opentelemetry.exporter import AzureMonitorLogExporter

set_logger_provider(LoggerProvider())
exporter = AzureMonitorLogExporter(
    connection_string=os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"]
)
get_logger_provider().add_log_record_processor(BatchLogRecordProcessor(exporter))

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
* [Customizing outputted metrics with views](#metric-custom-views)
* [Recording instruments with attributes](#metric-record-attributes)

Review the [OpenTelemetry Metrics SDK][ot_metrics_sdk] to learn how to use OpenTelemetry components to collect metrics.

#### Metric instrument usage

```python
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

exporter = AzureMonitorMetricExporter(
    connection_string=os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"]
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
up_down_counter = meter.create_up_down_counter("up_down_counter")
up_down_counter.add(1)
up_down_counter.add(-5)

# Async UpDownCounter
observable_up_down_counter = meter.create_observable_up_down_counter(
    "observable_up_down_counter", [observable_up_down_counter_func]
)

# Histogram
histogram = meter.create_histogram("histogram")
histogram.record(99.9)

# Async Gauge
gauge = meter.create_observable_gauge("gauge", [observable_gauge_func])

# Upon application exit, one last collection is made and telemetry records are
# flushed automatically. # If you would like to flush records manually yourself,
# you can call force_flush()
meter_provider.force_flush()
```

#### Metric custom views

```python
"""
This example shows how to customize the metrics that are output by the SDK using Views. Metrics created
and recorded using the sdk are tracked and telemetry is exported to application insights with the
AzureMonitorMetricsExporter.
"""
import os

from opentelemetry import metrics
from opentelemetry.sdk.metrics import Counter, MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.metrics.view import View

from azure.monitor.opentelemetry.exporter import AzureMonitorMetricExporter

exporter = AzureMonitorMetricExporter.from_connection_string(
    os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"]
)
# Create a view matching the counter instrument `my.counter`
# and configure the new name `my.counter.total` for the result metrics stream
change_metric_name_view = View(
    instrument_type=Counter,
    instrument_name="my.counter",
    name="my.counter.total",
)

reader = PeriodicExportingMetricReader(exporter, export_interval_millis=5000)
provider = MeterProvider(
    metric_readers=[
        reader,
    ],
    views=[
        change_metric_name_view,
    ],
)
metrics.set_meter_provider(provider)

meter = metrics.get_meter_provider().get_meter("view-name-change")
my_counter = meter.create_counter("my.counter")
my_counter.add(100)

```

More examples with the metrics `Views` SDK can be found [here](https://github.com/open-telemetry/opentelemetry-python/tree/main/docs/examples/metrics/views).

#### Metric record attributes

```python
"""
An example to show an application using different attributes with instruments in the OpenTelemetry SDK.
Metrics created and recorded using the sdk are tracked and telemetry is exported to application insights
with the AzureMonitorMetricsExporter.
"""
import os

from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader

from azure.monitor.opentelemetry.exporter import AzureMonitorMetricExporter

exporter = AzureMonitorMetricExporter.from_connection_string(
    os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"]
)
reader = PeriodicExportingMetricReader(exporter, export_interval_millis=5000)
metrics.set_meter_provider(MeterProvider(metric_readers=[reader]))

attribute_set1 = {
    "key1": "val1"
}
attribute_set2 = {
    "key2": "val2"
}
large_attribute_set = {}
for i in range(20):
    key = "key{}".format(i)
    val = "val{}".format(i)
    large_attribute_set[key] = val

meter = metrics.get_meter_provider().get_meter("sample")

# Counter
counter = meter.create_counter("attr1_counter")
counter.add(1, attribute_set1)

# Counter2
counter2 = meter.create_counter("attr2_counter")
counter2.add(10, attribute_set1)
counter2.add(30, attribute_set2)

# Counter3
counter3 = meter.create_counter("large_attr_counter")
counter3.add(100, attribute_set1)
counter3.add(200, large_attribute_set)

```

### Tracing

The following sections provide several code snippets covering some of the most common tasks, including:

* [Exporting a custom span](#export-hello-world-trace)
* [Using an instrumentation to track a library](#instrumentation-with-requests-library)
* [Enabling sampling to limit the amount of telemetry sent](#enabling-sampling)

Review the [OpenTelemetry Tracing SDK][ot_tracing_sdk] to learn how to use OpenTelemetry components to collect logs.

#### Export Hello World Trace

```python
"""
An example to show an application using Opentelemetry tracing api and sdk. Custom dependencies are
tracked via spans and telemetry is exported to application insights with the AzureMonitorTraceExporter.
"""
import os
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter

tracer_provider = TracerProvider()
trace.set_tracer_provider(tracer_provider)
tracer = trace.get_tracer(__name__)
# This is the exporter that sends data to Application Insights
exporter = AzureMonitorTraceExporter(
    connection_string=os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"]
)
span_processor = BatchSpanProcessor(exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

with tracer.start_as_current_span("hello"):
    print("Hello, World!")

# Telemetry records are flushed automatically upon application exit
# If you would like to flush records manually yourself, you can call force_flush()
tracer_provider.force_flush()
```

#### Instrumentation with requests library

OpenTelemetry also supports several instrumentations which allows to instrument with third party libraries.

For a list of instrumentations available in OpenTelemetry, visit the contrib [documentation](https://opentelemetry-python-contrib.readthedocs.io/en/latest/).

This example shows how to instrument with the [requests](https://pypi.org/project/requests/) library.

* Install the requests instrumentation package using pip install opentelemetry-instrumentation-requests.

```python
"""
An example to show an application instrumented with the OpenTelemetry requests instrumentation.
Calls made with the requests library will be automatically tracked and telemetry is exported to 
application insights with the AzureMonitorTraceExporter.
See more info on the requests instrumentation here:
https://github.com/open-telemetry/opentelemetry-python-contrib/tree/main/instrumentation/opentelemetry-instrumentation-requests
"""
import os
import requests
from opentelemetry import trace
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter

# This line causes your calls made with the requests library to be tracked.
RequestsInstrumentor().instrument()

trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)
exporter = AzureMonitorTraceExporter(
    connection_string=os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"]
)
span_processor = BatchSpanProcessor(exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

# This request will be traced
response = requests.get(url="https://azure.microsoft.com/")
```

#### Enabling sampling

You can enable sampling to limit the amount of telemetry records you receive. In order to enable correct sampling in Application Insights, use the `ApplicationInsightsSampler` as shown below.

```python
"""
An example to show an application using the ApplicationInsightsSampler to enable sampling for your telemetry.
Specify a sampling rate for the sampler to limit the amount of telemetry records you receive. Custom dependencies
 are tracked via spans and telemetry is exported to application insights with the AzureMonitorTraceExporter.
"""
import os
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from azure.monitor.opentelemetry.exporter import (
    ApplicationInsightsSampler,
    AzureMonitorTraceExporter,
)

# Sampler expects a sample rate of between 0 and 1 inclusive
# A rate of 0.75 means approximately 75% of your telemetry will be sent
sampler = ApplicationInsightsSampler(0.75)
trace.set_tracer_provider(TracerProvider(sampler=sampler))
tracer = trace.get_tracer(__name__)
exporter = AzureMonitorTraceExporter(
    connection_string=os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"]
)
span_processor = BatchSpanProcessor(exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

for i in range(100):
    # Approximately 25% of these spans should be sampled out
    with tracer.start_as_current_span("hello"):
        print("Hello, World!")
```

## Flush/shutdown behavior

For all applications set up with OpenTelemetry SDK and Azure Monitor exporters, telemetry is flushed automatically upon application exit. Note that this does not include when application ends abruptly or crashes due to uncaught exception.

## Troubleshooting

The exporter raises exceptions defined in [Azure Core](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/README.md#azure-core-library-exceptions).

## Next steps

### More sample code

Please find further examples in the [samples][exporter_samples] directory demonstrating common scenarios.

### Additional documentation

For more extensive documentation on the Azure Monitor service, see the [Azure Monitor documentation][product_docs] on docs.microsoft.com.

For detailed overview of OpenTelemetry, visit their [overview](https://github.com/open-telemetry/opentelemetry-specification/blob/master/specification/overview.md) page.

For the official OpenTelemetry Python documentation and how to enable other telemetry scenarios, visit the official OpenTelemetry [website](https://opentelemetry.io/docs/instrumentation/python/).

For more information on the Azure Monitor OpenTelemetry Distro, which is a bundle of useful, pre-assembled components (one of them being this current package) that enable telemetry scenarios with Azure Monitor, visit the [README](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/monitor/azure-monitor-opentelemetry).

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
[aad_for_ai_docs]: https://learn.microsoft.com/azure/azure-monitor/app/azure-ad-authentication?tabs=python
[api_docs]: https://azure.github.io/azure-sdk-for-python/monitor.html#azure-monitor-opentelemetry-exporter
[exporter_samples]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/monitor/azure-monitor-opentelemetry-exporter/samples
[product_docs]: https://docs.microsoft.com/azure/azure-monitor/overview
[azure_sub]: https://azure.microsoft.com/free/
[pip]: https://pypi.org/project/pip/
[pypi]: https://pypi.org/project/azure-monitor-opentelemetry-exporter/
[python]: https://www.python.org/downloads/
[ot_sdk_python]: https://github.com/open-telemetry/opentelemetry-python
[application_insights_namespace]: https://docs.microsoft.com/azure/azure-monitor/app/app-insights-overview#how-do-i-use-application-insights
[opentelemetry_spec]: https://opentelemetry.io/
[instrumentation_library]: https://github.com/open-telemetry/opentelemetry-specification/blob/master/specification/overview.md#instrumentation-libraries
[log_concept]: https://github.com/open-telemetry/opentelemetry-specification/blob/main/specification/overview.md#log-signal
[log_record]: https://opentelemetry-python.readthedocs.io/en/stable/sdk/_logs.html#opentelemetry.sdk._logs.LogRecord
[logger]: https://opentelemetry-python.readthedocs.io/en/stable/sdk/_logs.html#opentelemetry.sdk._logs.Logger
[logger_provider]: https://opentelemetry-python.readthedocs.io/en/stable/sdk/_logs.html#opentelemetry.sdk._logs.LoggerProvider
[log_record_processor]: https://opentelemetry-python.readthedocs.io/en/stable/sdk/_logs.html#opentelemetry.sdk._logs.LogRecordProcessor
[logging_handler]: https://opentelemetry-python.readthedocs.io/en/stable/sdk/_logs.html#opentelemetry.sdk._logs.LoggingHandler
[log_reference]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-opentelemetry-exporter/azure/monitor/opentelemetry/exporter/export/logs/_exporter.py
[ot_logging_sdk]: https://opentelemetry-python.readthedocs.io/en/stable/sdk/_logs.html
[metric_concept]: https://github.com/open-telemetry/opentelemetry-specification/blob/main/specification/overview.md#metric-signal
[measurement]: https://github.com/open-telemetry/opentelemetry-specification/blob/main/specification/metrics/api.md#measurement
[instrument]: https://github.com/open-telemetry/opentelemetry-specification/blob/main/specification/metrics/api.md#instrument
[meter]: https://github.com/open-telemetry/opentelemetry-specification/blob/main/specification/metrics/api.md#meter
[meter_provider]: https://github.com/open-telemetry/opentelemetry-specification/blob/main/specification/metrics/api.md#meterprovider
[metric_reader]:https://github.com/open-telemetry/opentelemetry-specification/blob/main/specification/metrics/sdk.md#metricreader
[metric_reference]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-opentelemetry-exporter/azure/monitor/opentelemetry/exporter/export/metrics/_exporter.py
[ot_metrics_sdk]: https://opentelemetry-python.readthedocs.io/en/stable/sdk/metrics.html
[trace_concept]: https://github.com/open-telemetry/opentelemetry-specification/blob/main/specification/overview.md#tracing-signal
[span]: https://opentelemetry-python.readthedocs.io/en/stable/api/trace.html?highlight=TracerProvider#opentelemetry.trace.Span
[tracer]: https://opentelemetry-python.readthedocs.io/en/stable/api/trace.html?highlight=TracerProvider#opentelemetry.trace.Tracer
[tracer_provider]: https://opentelemetry-python.readthedocs.io/en/stable/api/trace.html?highlight=TracerProvider#opentelemetry.trace.TracerProvider
[span_processor]: https://opentelemetry-python.readthedocs.io/en/stable/_modules/opentelemetry/sdk/trace.html?highlight=SpanProcessor#
[trace_reference]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-opentelemetry-exporter/azure/monitor/opentelemetry/exporter/export/trace/_exporter.py
[ot_tracing_sdk]: https://opentelemetry-python.readthedocs.io/en/stable/sdk/trace.html
[sampler_ref]: https://github.com/open-telemetry/opentelemetry-specification/blob/master/specification/trace/sdk.md#sampling
