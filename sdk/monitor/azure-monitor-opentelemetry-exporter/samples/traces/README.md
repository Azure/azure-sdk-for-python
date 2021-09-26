---
page_type: sample
languages:
  - python
products:
  - azure-monitor
---

# Microsoft Azure Monitor Opentelemetry Exporter Python Samples

These code samples show common champion scenario operations with the AzureMonitorTraceExporter.

* Azure Service Bus Send: [sample_servicebus_send.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-opentelemetry-exporter/samples/traces/sample_servicebus_send.py)
* Azure Service Bus Receive: [sample_servicebus_receive.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-opentelemetry-exporter/samples/traces/sample_servicebus_receive.py)
* Azure Storage Blob Create Container: [sample_storage.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-opentelemetry-exporter/samples/traces/sample_storage.py)
* Client: [sample_client.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-opentelemetry-exporter/samples/traces/sample_client.py)
* Jaeger: [sample_jaeger.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-opentelemetry-exporter/samples/traces/sample_jaeger.py)
* Trace: [sample_trace.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-opentelemetry-exporter/samples/traces/sample_trace.py)
* Server: [sample_server.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-opentelemetry-exporter/samples/traces/sample_server.py)

## Installation

```sh
$ pip install azure-monitor-opentelemetry-exporter --pre
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

### Jaeger

* The Jaeger project provides an all-in-one Docker container with a UI, database, and consumer. Run the following command to start Jaeger:

```sh
$ docker run -p 16686:16686 -p 6831:6831/udp jaegertracing/all-in-one
```

* This command starts Jaeger locally on port 16686 and exposes the Jaeger thrift agent on port 6831. You can visit Jaeger at http://localhost:16686.

* Install the OpenTelemetry Jaeger Exporter

```sh
$ pip install opentelemetry-exporter-jaeger
```

* Update `APPLICATIONINSIGHTS_CONNECTION_STRING` environment variable

* Run the sample

```sh
$ # from this directory
$ python sample_jaeger.py
```

* You should be able to see your traces in the Jaeger backend as well as Azure Monitor application insights backend.

### Collector

* Start the Collector locally to see how the Collector works in practice.

* From the same folder as collector/otel-collector-config.yaml and collector/docker-compose.yml, start the Docker container.

```sh
$ docker-compose up
```

* Install the OpenTelemetry OTLP Exporter

```sh
$ pip install opentelemetry-exporter-otlp
```

* Update `APPLICATIONINSIGHTS_CONNECTION_STRING` environment variable

* Run the sample

```sh
# from collector directory
$ python sample_collector.py
```

* You should be able to see your traces in the Zipkin backend as well as Azure Monitor application insights backend.

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

### Azure Storage Blob Create Container

The following sample assumes that you have setup an Azure Service Bus [namespace](https://docs.microsoft.com/azure/service-bus-messaging/service-bus-quickstart-portal).

* Update `APPLICATIONINSIGHTS_CONNECTION_STRING` environment variable
* Update `AZURE_STORAGE_CONNECTION_STRING` environment variable
* Update `AZURE_STORAGE_BLOB_CONTAINER_NAME` environment variable

* Run the sample

```sh
$ # azure-storage-blob library
$ pip install azure-storage-blob
$ # azure sdk core tracing library for opentelemetry
$ pip install azure-core-tracing-opentelemetry
$ # from this directory
$ python sample_storage.py
```

## Explore the data

After running the applications, data would be available in [Azure](
https://docs.microsoft.com/azure/azure-monitor/app/app-insights-overview#where-do-i-see-my-telemetry)
