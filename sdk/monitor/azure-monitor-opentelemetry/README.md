# Azure Monitor Opentelemetry Distro client library for Python

The Azure Monitor Distro of [Opentelemetry Python][ot_sdk_python] provides multiple installable components available for an Opentelemetry Azure Monitor monitoring solution. It allows you to instrument your Python applications to capture and report telemetry to Azure Monitor via the Azure monitor exporters.

This distro automatically installs the following libraries:

* [Azure Monitor OpenTelemetry exporters][azure_monitor_opentelemetry_exporters]
* A subset of OpenTelemetry [instrumentations][ot_instrumentations] that are officially supported as listed below.

## Officially supported instrumentations

OpenTelemetry instrumentations allow automatic collection of requests sent from underlying instrumented libraries. The following is a list of OpenTelemetry instrumentations that come bundled in with the Azure monitor distro. These instrumentations are enabled by default. See the [Usage](#usage) section below for how to opt-out of these instrumentations.

| Instrumentation | Supported library Name | Supported versions |
| --------------- | ---------------------- | ------------------ |
| [Azure Core Tracing OpenTelemetry][azure_core_tracing_opentelemetry_plugin] | `azure_sdk` | |
| [OpenTelemetry Django Instrumentation][ot_instrumentation_django] | [django][pypi_django] | [link][ot_instrumentation_django_version]
| [OpenTelemetry FastApi Instrumentation][ot_instrumentation_fastapi] | [fastapi][pypi_fastapi] | [link][ot_instrumentation_fastapi_version]
| [OpenTelemetry Flask Instrumentation][ot_instrumentation_flask] | [flask][pypi_flask] | [link][ot_instrumentation_flask_version]
| [OpenTelemetry Psycopg2 Instrumentation][ot_instrumentation_psycopg2] | [psycopg2][pypi_psycopg2] | [link][ot_instrumentation_psycopg2_version]
| [OpenTelemetry Requests Instrumentation][ot_instrumentation_requests] | [requests][pypi_requests] | [link][ot_instrumentation_requests_version]
| [OpenTelemetry UrlLib Instrumentation][ot_instrumentation_urllib] | [urllib][pypi_urllib] | All
| [OpenTelemetry UrlLib3 Instrumentation][ot_instrumentation_urllib3] | [urllib3][pypi_urllib3] | [link][ot_instrumentation_urllib3_version]

If you would like to add support for another OpenTelemetry instrumentation, please submit a feature [request][distro_feature_request]. In the meantime, you can use the OpenTelemetry instrumentation manually via it's own APIs (i.e. `instrument()`) in your code. See [this][samples_manual] for an example.

## Key concepts

This package bundles a series of OpenTelemetry and Azure Monitor components to enable the collection and sending of telemetry to Azure Monitor. For MANUAL instrumentation, use the `configure_azure_monitor` function. AUTOMATIC instrumentation is not yet supported.

The [Azure Monitor OpenTelemetry exporters][azure_monitor_opentelemetry_exporters] are the main components in accomplishing this. You will be able to use the exporters and their APIs directly through this package. Please go the exporter documentation to understand how OpenTelemetry and Azure Monitor components work in enabling telemetry collection and exporting.

Currently, all instrumentations available in OpenTelemetry are in a beta state, meaning they are not stable and may have breaking changes in the future. Efforts are being made in pushing these to a more stable state.

## Getting started

### Prerequisites

To use this package, you must have:

* Azure subscription - [Create a free account][azure_sub]
* Azure Monitor - [How to use application insights][application_insights_namespace]
* Opentelemetry SDK - [Opentelemetry SDK for Python][ot_sdk_python]
* Python 3.7 or later - [Install Python][python]

### Install the package

Install the Azure Monitor Opentelemetry Distro with [pip][pip]:

```Bash
pip install azure-monitor-opentelemetry
```

### Usage

You can use `configure_azure_monitor` to set up instrumentation for your app to Azure Monitor. `configure_azure_monitor` supports the following optional arguments. All pass-in parameters take priority over any related environment variables.

| Parameter | Description | Environment Variable |
|-------------------|----------------------------------------------------|----------------------|
| `connection_string` | The [connection string][connection_string_doc] for your Application Insights resource. The connection string will be automatically populated from the `APPLICATIONINSIGHTS_CONNECTION_STRING` environment variable if not explicitly passed in. | `APPLICATIONINSIGHTS_CONNECTION_STRING` |
| `logger_name` | The name of the [Python logger][python_logger] under which telemetry is collected. | `N/A` |
| `instrumentation_options` | A nested dictionary that determines which instrumentations to enable or disable. Instrumentations are referred to by their [Library Names](#officially-supported-instrumentations). For example, `{"azure_sdk": {"enabled": False}, "flask": {"enabled": False}, "django": {"enabled": True}}` will disable Azure Core Tracing and the Flask instrumentation but leave Django and the other default instrumentations enabled. The `OTEL_PYTHON_DISABLED_INSTRUMENTATIONS` environment variable explained below can also be used to disable instrumentations. | `N/A` |


You can configure further with [OpenTelemetry environment variables][ot_env_vars] such as:
| Environment Variable | Description |
|-------------|----------------------|
| [OTEL_SERVICE_NAME][opentelemetry_spec_service_name], [OTEL_RESOURCE_ATTRIBUTES][opentelemetry_spec_resource_attributes] | Specifies the OpenTelemetry [resource][opentelemetry_spec_resource] associated with your application. |
| `OTEL_LOGS_EXPORTER` | If set to `None`, disables collection and export of logging telemetry. |
| `OTEL_METRICS_EXPORTER` | If set to `None`, disables collection and export of metric telemetry. |
| `OTEL_TRACES_EXPORTER` | If set to `None`, disables collection and export of distributed tracing telemetry. |
| `OTEL_BLRP_SCHEDULE_DELAY` | Specifies the logging export interval in milliseconds. Defaults to 5000. |
| `OTEL_BSP_SCHEDULE_DELAY` | Specifies the distributed tracing export interval in milliseconds. Defaults to 5000. |
| `OTEL_TRACES_SAMPLER_ARG` | Specifies the ratio of distributed tracing telemetry to be [sampled][application_insights_sampling]. Accepted values are in the range [0,1]. Defaults to 1.0, meaning no telemetry is sampled out. |
| `OTEL_PYTHON_DISABLED_INSTRUMENTATIONS` | Specifies which of the supported instrumentations to disable. Disabled instrumentations will not be instrumented as part of `configure_azure_monitor`. However, they can still be manually instrumented with `instrument()` directly. Accepts a comma-separated list of lowercase [Library Names](#officially-supported-instrumentations). For example, set to `"psycopg2,fastapi"` to disable the Psycopg2 and FastAPI instrumentations. Defaults to an empty list, enabling all supported instrumentations. |

#### Azure monitor OpenTelemetry Exporter configurations

You can pass Azure monitor OpenTelemetry exporter configuration parameters directly into `configure_azure_monitor`. See additional [configuration related to exporting here][exporter_configuration_docs].

```python
...
configure_azure_monitor(
   connection_string="<your-connection-string>",
   disable_offline_storage=True, 
)
...
```

### Examples

Samples are available [here][samples] to demonstrate how to utilize the above configuration options.

## Troubleshooting

The exporter raises exceptions defined in [Azure Core](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/README.md#azure-core-library-exceptions).

## Next steps

Check out the [documentation][azure_monitor_enable_docs] for more.

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

### Additional documentation

* [Azure Portal][azure_portal]
* [Official Azure monitor docs][azure_monitor_enable_docs]
* [OpenTelemetry Python Official Docs][ot_python_docs]

<!-- LINKS -->
[azure_core_tracing_opentelemetry_plugin]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/core/azure-core-tracing-opentelemetry
[azure_core_tracing_opentelemetry_plugin_sample]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/monitor/azure-monitor-opentelemetry/samples/tracing/azure_core.py
[azure_monitor_enable_docs]: https://learn.microsoft.com/azure/azure-monitor/app/opentelemetry-enable?tabs=python
[azure_monitor_opentelemetry_exporters]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/monitor/azure-monitor-opentelemetry-exporter#microsoft-opentelemetry-exporter-for-azure-monitor
[azure_portal]: https://portal.azure.com
[azure_sub]: https://azure.microsoft.com/free/
[application_insights_namespace]: https://learn.microsoft.com/azure/azure-monitor/app/app-insights-overview
[application_insights_sampling]: https://learn.microsoft.com/azure/azure-monitor/app/sampling
[connection_string_doc]: https://learn.microsoft.com/azure/azure-monitor/app/sdk-connection-string
[distro_feature_request]: https://github.com/Azure/azure-sdk-for-python/issues/new
[exporter_configuration_docs]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/monitor/azure-monitor-opentelemetry-exporter#configuration
[ot_env_vars]: https://opentelemetry.io/docs/reference/specification/sdk-environment-variables/
[ot_instrumentations]: https://github.com/open-telemetry/opentelemetry-python-contrib/tree/main/instrumentation
[ot_metric_reader]: https://github.com/open-telemetry/opentelemetry-specification/blob/main/specification/metrics/sdk.md#metricreader
[ot_python_docs]: https://opentelemetry.io/docs/instrumentation/python/
[ot_sdk_python]: https://github.com/open-telemetry/opentelemetry-python
[ot_sdk_python_metric_reader]: https://opentelemetry-python.readthedocs.io/en/stable/sdk/metrics.export.html#opentelemetry.sdk.metrics.export.MetricReader
[ot_sdk_python_view_examples]: https://github.com/open-telemetry/opentelemetry-python/tree/main/docs/examples/metrics/views
[ot_instrumentation_django]: https://github.com/open-telemetry/opentelemetry-python-contrib/tree/main/instrumentation/opentelemetry-instrumentation-django
[ot_instrumentation_django_version]: https://github.com/open-telemetry/opentelemetry-python-contrib/blob/main/instrumentation/opentelemetry-instrumentation-django/src/opentelemetry/instrumentation/django/package.py#L16
[ot_instrumentation_fastapi]: https://github.com/open-telemetry/opentelemetry-python-contrib/tree/main/instrumentation/opentelemetry-instrumentation-fastapi
[ot_instrumentation_fastapi_version]: https://github.com/open-telemetry/opentelemetry-python-contrib/blob/main/instrumentation/opentelemetry-instrumentation-fastapi/src/opentelemetry/instrumentation/fastapi/package.py#L16
[ot_instrumentation_flask]: https://github.com/open-telemetry/opentelemetry-python-contrib/tree/main/instrumentation/opentelemetry-instrumentation-flask
[ot_instrumentation_flask_version]: https://github.com/open-telemetry/opentelemetry-python-contrib/blob/main/instrumentation/opentelemetry-instrumentation-flask/src/opentelemetry/instrumentation/flask/package.py#L16
[ot_instrumentation_psycopg2]: https://github.com/open-telemetry/opentelemetry-python-contrib/tree/main/instrumentation/opentelemetry-instrumentation-psycopg2
[ot_instrumentation_psycopg2_version]: https://github.com/open-telemetry/opentelemetry-python-contrib/blob/main/instrumentation/opentelemetry-instrumentation-psycopg2/src/opentelemetry/instrumentation/psycopg2/package.py#L16
[ot_instrumentation_requests]: https://github.com/open-telemetry/opentelemetry-python-contrib/tree/main/instrumentation/opentelemetry-instrumentation-requests
[ot_instrumentation_requests_version]: https://github.com/open-telemetry/opentelemetry-python-contrib/blob/main/instrumentation/opentelemetry-instrumentation-requests/src/opentelemetry/instrumentation/requests/package.py#L16
[ot_instrumentation_urllib]: https://github.com/open-telemetry/opentelemetry-python-contrib/tree/main/instrumentation/opentelemetry-instrumentation-urllib3
[ot_instrumentation_urllib3]: https://github.com/open-telemetry/opentelemetry-python-contrib/tree/main/instrumentation/opentelemetry-instrumentation-urllib3
[ot_instrumentation_urllib3_version]: https://github.com/open-telemetry/opentelemetry-python-contrib/blob/main/instrumentation/opentelemetry-instrumentation-urllib3/src/opentelemetry/instrumentation/urllib3/package.py#L16
[opentelemetry_spec_resource]: https://github.com/open-telemetry/opentelemetry-specification/blob/main/specification/resource/sdk.md#resource-sdk
[opentelemetry_spec_resource_attributes]: https://github.com/open-telemetry/opentelemetry-specification/blob/main/specification/resource/sdk.md#specifying-resource-information-via-an-environment-variable
[opentelemetry_spec_service_name]: https://github.com/open-telemetry/opentelemetry-specification/tree/main/specification/resource/semantic_conventions#semantic-attributes-with-sdk-provided-default-value
[opentelemetry_spec_view]: https://github.com/open-telemetry/opentelemetry-specification/blob/main/specification/metrics/sdk.md#view
[pip]: https://pypi.org/project/pip/
[pypi_django]: https://pypi.org/project/Django/
[pypi_fastapi]: https://pypi.org/project/fastapi/
[pypi_flask]: https://pypi.org/project/Flask/
[pypi_psycopg2]: https://pypi.org/project/psycopg2/
[pypi_requests]: https://pypi.org/project/requests/
[pypi_urllib]: https://docs.python.org/3/library/urllib.html
[pypi_urllib3]: https://pypi.org/project/urllib3/
[python]: https://www.python.org/downloads/
[python_logger]: https://docs.python.org/3/library/logging.html#logger-objects
[python_logging_level]: https://docs.python.org/3/library/logging.html#levels
[samples]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/monitor/azure-monitor-opentelemetry/samples
[samples_manual]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/monitor/azure-monitor-opentelemetry/samples/tracing/manual.py
