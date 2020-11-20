---
page_type: sample
languages:
  - python
products:
  - microsoft-opentelemetry-exporter-azuremonitor
---

# Microsoft Azure Monitor Opentelemetry Exporter Python Samples

These code samples show common champion scenario operations with the AzureMonitorTraceExporter.

* Trace: [sample_trace.py](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/monitor/microsoft-opentelemetry-exporter-azuremonitor/samples/traces/sample_trace.py)
* Client: [sample_client.py](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/monitor/microsoft-opentelemetry-exporter-azuremonitor/samples/traces/sample_client.py)
* Request: [sample_request.py](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/monitor/microsoft-opentelemetry-exporter-azuremonitor/samples/traces/sample_request.py)
* Server: [sample_server.py](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/monitor/microsoft-opentelemetry-exporter-azuremonitor/samples/traces/sample_server.py)

## Installation

```sh
$ pip install microsoft-opentelemetry-exporter-azuremonitor
```

## Run the Applications

### Trace

* Update `APPLICATIONINSIGHTS_CONNECTION_STRING` environment variable

* Run the sample

```sh
$ # from this directory
$ python trace.py
```

### Request

* Update `APPLICATIONINSIGHTS_CONNECTION_STRING` environment variable

* Run the sample

```sh
$ pip install opentelemetry-instrumentation-requests
$ # from this directory
$ python request.py
```

### Server

* Update `APPLICATIONINSIGHTS_CONNECTION_STRING` environment variable

* Run the sample

```sh
$ pip install opentelemetry-instrumentation-requests
$ pip install opentelemetry-instrumentation-wsgi
$ # from this directory
$ python server.py
```

* Open http://localhost:8080/ 


## Explore the data

After running the applications, data would be available in [Azure](
https://docs.microsoft.com/azure/azure-monitor/app/app-insights-overview#where-do-i-see-my-telemetry)