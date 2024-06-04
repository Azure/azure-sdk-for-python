---
page_type: sample
languages:
    - python
products:
    - azure
    - azure-template
urlFragment: azure-template-samples
---

# Azure Monitor OpenTelemetry distro samples

Provide an overview of all the samples and explain how to run them.

For guidance on the samples README, visit the [sample guide](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/sample_guide.md#package-sample-readme).


|**File Name**|**Description**|
|----------------|-------------|
|[logging/correlated_logs.py][correlated_logs] | Produce logs correlated with spans |
|[logging/custom_properties.py][custom_properties] | Add custom propterties to logs |
|[logging/exception_logs.py][exception_logs] | Produce exception logs |
|[logging/logs_with_traces.py][logs_with_traces] | Produce correlated logs inside an instrumented http library's distributed tracing |
|[logging/basic.py][logging_basic] | Produce logs |
|[metrics/attributes.py][attributes] | Add attributes to custom metrics counters |
|[metrics/instruments.py][instruments] | Create observable instruments |
|[metrics/live_metrics.py][live_metrics] | Live metrics feature |
|[tracing/django/sample/manage.py][django] | Instrument a django app |
|[tracing/db_psycopg2.py][db_psycopg2] | Instrument the PsycoPG2 library |
|[tracing/http_fastapi.py][http_fastapi] | Instrument a FastAPI app |
|[tracing/http_flask.py][http_flask] | Instrument a Flask app |
|[tracing/http_requests.py][http_requests] | Instrument the Requests library |
|[tracing/http_urllib.py][http_urllib] | Instrument the URLLib library |
|[tracing/http_urllib3.py][http_urllib3] | Instrument the URLLib library |
|[tracing/instrumentation_options.py][instrumentation_options] | Enable and disable instrumentations |
|[tracing/manually_instrumented.py][manual] | Manually add instrumentation |
|[tracing/sampling.py][sampling] | Sample distributed tracing telemetry |
|[tracing/tracing_simple.py][tracing_simple] | Produce manual spans |

## Prerequisites

* Python 3.7 or later is required to use this package.

## Setup

1. Install the Azure Monitor OpenTelemetry Distro for Python with [pip][pip]:

    ```sh
    pip install azure-monitor-opentelemetry
    ```

2. Clone or download the repository containing this sample code. Alternatively, you can download the sample file directly.

## Running the samples

 Navigate to the directory that the sample(s) are saved in, and follow the usage described in the file. For example, `python logging/simple.py`.

## Next steps

To learn more, see the [Azure Monitor OpenTelemetry Distro documentation][distro_docs] and [OpenTelemetry documentation][otel_docs]

<!-- Links -->
[distro_docs]: https://learn.microsoft.com/azure/azure-monitor/app/opentelemetry-enable?tabs=python
[otel_docs]: https://opentelemetry.io/docs/
[correlated_logs]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/monitor/azure-monitor-opentelemetry/samples/logging/correlated_logs.py
[custom_properties]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/monitor/azure-monitor-opentelemetry/samples/logging/custom_properties.py
[exception_logs]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/monitor/azure-monitor-opentelemetry/samples/logging/exception_logs.py
[logs_with_traces]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/monitor/azure-monitor-opentelemetry/samples/logging/logs_with_traces.py
[logging_basic]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/monitor/azure-monitor-opentelemetry/samples/logging/basic.py
[attributes]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/monitor/azure-monitor-opentelemetry/samples/metrics/attributes.py
[instruments]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/monitor/azure-monitor-opentelemetry/samples/metrics/instruments.py
[instruments]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/monitor/azure-monitor-opentelemetry/samples/metrics/live_metrics.py
[django]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/monitor/azure-monitor-opentelemetry/samples/tracing/django/sample/manage.py
[db_psycopg2]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/monitor/azure-monitor-opentelemetry/samples/tracing/db_psycopg2.py
[http_fastapi]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/monitor/azure-monitor-opentelemetry/samples/tracing/http_fastapi.py
[http_flask]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/monitor/azure-monitor-opentelemetry/samples/tracing/http_flask.py
[http_requests]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/monitor/azure-monitor-opentelemetry/samples/tracing/http_requests.py
[http_urllib]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/monitor/azure-monitor-opentelemetry/samples/tracing/http_urllib.py
[http_urllib3]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/monitor/azure-monitor-opentelemetry/samples/tracing/http_urllib3.py
[instrumentation_options]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/monitor/azure-monitor-opentelemetry/samples/tracing/instrumentation_options.py
[manual]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-opentelemetry/samples/tracing/manually_instrumented.py
[sampling]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/monitor/azure-monitor-opentelemetry/samples/tracing/sampling.py
[tracing_simple]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/monitor/azure-monitor-opentelemetry/samples/tracing/simple.py
[pip]: https://pypi.org/project/pip/
