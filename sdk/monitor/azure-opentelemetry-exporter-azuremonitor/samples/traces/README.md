---
page_type: sample
languages:
  - python
products:
  - azure-opentelemetry-exporter-azuremonitor
---

# Microsoft Azure Monitor Opentelemetry Exporter Python Samples

These code samples show common champion scenario operations with the AzureMonitorTraceExporter.

* Trace: [sample_trace.py](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/monitor/azure-opentelemetry-exporter-azuremonitor/samples/traces/sample_trace.py)
* Client: [sample_client.py](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/monitor/azure-opentelemetry-exporter-azuremonitor/samples/traces/sample_client.py)
* Server: [sample_server.py](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/monitor/azure-opentelemetry-exporter-azuremonitor/samples/traces/sample_server.py)
* Azure Service Bus Send: [sample_servicebus_send.py](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/monitor/azure-opentelemetry-exporter-azuremonitor/samples/traces/sample_servicebus_send.py)
* Azure Service Bus Receive: [sample_servicebus_receive.py](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/monitor/azure-opentelemetry-exporter-azuremonitor/samples/traces/sample_servicebus_receive.py)

## Installation

```sh
$ pip install azure-opentelemetry-exporter-azuremonitor --pre
```

## Run the Applications

### Trace

* Update `APPLICATIONINSIGHTS_CONNECTION_STRING` environment variable

* Run the sample

```sh
$ # from this directory
$ python sample_trace.py
```

### Client

* Update `APPLICATIONINSIGHTS_CONNECTION_STRING` environment variable

* Run the sample

```sh
$ pip install opentelemetry-instrumentation-requests
$ # from this directory
$ python sample_request.py
```

### Server

* Update `APPLICATIONINSIGHTS_CONNECTION_STRING` environment variable

* Run the sample

```sh
$ pip install opentelemetry-instrumentation-requests
$ pip install opentelemetry-instrumentation-flask
$ # from this directory
$ python sample_server.py
```

* Open http://localhost:8080/ 

### Azure Service Bus Send

The following sample assumes that you have setup an Azure Service Bus [namespace](https://docs.microsoft.com/azure/service-bus-messaging/service-bus-quickstart-portal).

* Update `APPLICATIONINSIGHTS_CONNECTION_STRING` environment variable
* Update `SERVICE_BUS_CONN_STR` environment variable
* Update `SERVICE_BUS_QUEUE_NAME` environment variable

* Run the sample

```sh
$ # azure-servicebus library
$ pip install azure-servicebus
$ # azure sdk core tracing library for opentelemetry
$ pip install azure-core-tracing-opentelemetry
$ # from this directory
$ python sample_servicebus_send.py
```

### Azure Service Bus Receive

The following sample assumes that you have setup an Azure Service Bus [namespace](https://docs.microsoft.com/azure/service-bus-messaging/service-bus-quickstart-portal).

* Update `APPLICATIONINSIGHTS_CONNECTION_STRING` environment variable
* Update `SERVICE_BUS_CONN_STR` environment variable
* Update `SERVICE_BUS_QUEUE_NAME` environment variable

* Run the sample

```sh
$ # azure-servicebus library
$ pip install azure-servicebus
$ # azure sdk core tracing library for opentelemetry
$ pip install azure-core-tracing-opentelemetry
$ # from this directory
$ python sample_servicebus_receive.py
```

## Explore the data

After running the applications, data would be available in [Azure](
https://docs.microsoft.com/azure/azure-monitor/app/app-insights-overview#where-do-i-see-my-telemetry)
