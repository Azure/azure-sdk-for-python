---
page_type: sample
languages:
  - python
products:
  - azure-monitor
---

# Microsoft Azure Monitor Opentelemetry Exporter Trace Python Samples

These code samples show common champion scenario operations with the AzureMonitorTraceExporter.

* Client: [sample_client.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-opentelemetry-exporter/samples/traces/sample_client.py)
* Collector: [sample_collector.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-opentelemetry-exporter/samples/traces/collector/sample_collector.py)
* Jaeger: [sample_jaeger.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-opentelemetry-exporter/samples/traces/sample_jaeger.py)
* Server: [sample_server.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-opentelemetry-exporter/samples/traces/sample_server.py)
* Span Event: [sample_span_event.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-opentelemetry-exporter/samples/traces/sample_span_event.py)
* Trace: [sample_trace.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-opentelemetry-exporter/samples/traces/sample_trace.py)

* Azure AppConfig Add Config Setting: [sample_app_config.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-opentelemetry-exporter/samples/traces/sample_app_config.py)
* Azure Communication Chat Create Client/Thread: [sample_comm_chat.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-opentelemetry-exporter/samples/traces/sample_comm_chat.py)
* Azure Communication Phone Numbers List Purchased Numbers: [sample_comm_phone.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-opentelemetry-exporter/samples/traces/sample_comm_phone.py)
* Azure Communication SMS Send Message: [sample_comm_sms.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-opentelemetry-exporter/samples/traces/sample_comm_sms.py)
* Azure CosmosDb Create Db/Container: [sample_cosmos.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-opentelemetry-exporter/samples/traces/sample_cosmos.py)
* Azure EventHub Send EventData: [sample_event_hub.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-opentelemetry-exporter/samples/traces/sample_event_hub.py)
* Azure EventHub Blob Storage Checkpoint Store: [sample_blob_checkpoint.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-opentelemetry-exporter/samples/traces/sample_blob_checkpoint.py)
* Azure EventGrid Send Event: [sample_event_grid.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-opentelemetry-exporter/samples/traces/sample_event_grid.py)
* Azure Form Recognizer Analyze Document: [sample_form_recognizer.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-opentelemetry-exporter/samples/traces/sample_form_recognizer.py)
* Azure KeyVault Create Certificate: [sample_key_cert.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-opentelemetry-exporter/samples/traces/sample_key_cert.py)
* Azure KeyVault Set Secret: [sample_key_secret.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-opentelemetry-exporter/samples/traces/sample_key_secret.py)
* Azure KeyVault Create Keys: [sample_key_keys.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-opentelemetry-exporter/samples/traces/sample_key_keys.py)
* Azure Service Bus Send: [sample_servicebus_send.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-opentelemetry-exporter/samples/traces/sample_servicebus_send.py)
* Azure Service Bus Receive: [sample_servicebus_receive.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-opentelemetry-exporter/samples/traces/sample_servicebus_receive.py)
* Azure Storage Blob Create Container: [sample_storage_blob.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-opentelemetry-exporter/samples/traces/sample_storage_blob.py)
* Azure Azure Text Analytics Extract Key Phrases: [sample_text_analytics.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-opentelemetry-exporter/samples/traces/sample_text_analytics.py)

## Installation

```sh
$ pip install azure-monitor-opentelemetry-exporter --pre
```

## Run the Applications

### Client

* Update `APPLICATIONINSIGHTS_CONNECTION_STRING` environment variable

* Run the sample

```sh
$ pip install opentelemetry-instrumentation-requests
$ # from this directory
$ python sample_request.py
```

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

### Span Event

* Update `APPLICATIONINSIGHTS_CONNECTION_STRING` environment variable

* Run the sample

```sh
$ # from this directory
$ python sample_span_event.py
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

### Trace

* Update `APPLICATIONINSIGHTS_CONNECTION_STRING` environment variable

* Run the sample

```sh
$ # from this directory
$ python sample_trace.py
```

### Azure AppConfig Add Config Setting

The following sample assumes that you have setup an Azure App Configuration [Store](https://docs.microsoft.com/azure/azure-app-configuration/quickstart-python).

* Update `APPLICATIONINSIGHTS_CONNECTION_STRING` environment variable

* Run the sample

```sh
$ # azure-appconfiguration library
$ pip install azure-appconfiguration
$ # azure sdk core tracing library for opentelemetry
$ pip install azure-core-tracing-opentelemetry
$ # from this directory
$ python sample_app_config.py
```

### Azure Communication Chat Create Client/Thread

The following sample assumes that you have setup an Azure Communication Services [resource](https://docs.microsoft.com/azure/communication-services/quickstarts/create-communication-resource).

* Update `APPLICATIONINSIGHTS_CONNECTION_STRING` environment variable

* Run the sample

```sh
$ # azure-communication-chat library
$ pip install azure-communication-chat
$ # azure-communication-identity library for authentication
$ pip install azure-communication-identity
$ # azure sdk core tracing library for opentelemetry
$ pip install azure-core-tracing-opentelemetry
$ # from this directory
$ python sample_comm_chat.py
```

### Azure Communication Phone Numbers List Purchased Numbers

The following sample assumes that you have setup an Azure Communication Services [resource](https://docs.microsoft.com/azure/communication-services/quickstarts/create-communication-resource).

* Update `APPLICATIONINSIGHTS_CONNECTION_STRING` environment variable

* Run the sample

```sh
$ # azure-communication-phonenumbers library
$ pip install azure-communication-phonenumbers
$ # azure sdk core tracing library for opentelemetry
$ pip install azure-core-tracing-opentelemetry
$ # from this directory
$ python sample_comm_phone.py
```

### Azure Communication SMS Send Message

The following sample assumes that you have setup an Azure Communication Services [resource](https://docs.microsoft.com/azure/communication-services/quickstarts/create-communication-resource).

* Update `APPLICATIONINSIGHTS_CONNECTION_STRING` environment variable

* Run the sample

```sh
$ # azure-communication-sms library
$ pip install azure-communication-sms
$ # azure sdk core tracing library for opentelemetry
$ pip install azure-core-tracing-opentelemetry
$ # from this directory
$ python sample_comm_sms.py
```

### Azure CosmosDb Create Db/Container

The following sample assumes that you have setup Azure CosmosDb [account](https://docs.microsoft.com/azure/cosmos-db/sql/create-cosmosdb-resources-portal).

* Update `APPLICATIONINSIGHTS_CONNECTION_STRING` environment variable
* Update `ACCOUNT_URI` environment variable
* Update `ACCOUNT_KEY` environment variable

* Run the sample

```sh
$ # azure-cosmos library
$ pip install azure-cosmos
$ # azure sdk core tracing library for opentelemetry
$ pip install azure-core-tracing-opentelemetry
$ # from this directory
$ python sample_cosmos.py
```

### Azure EventHub Send EventData

The following sample assumes that you have setup an Azure EventHubs namespace and [EventHub](https://docs.microsoft.com/azure/event-hubs/event-hubs-create).

* Update `APPLICATIONINSIGHTS_CONNECTION_STRING` environment variable
* Update `EVENT_HUB_CONN_STR` environment variable
* Update `EVENT_HUB_NAME` environment variable

* Run the sample

```sh
$ # azure-eventhub library
$ pip install azure-eventhub
$ # azure sdk core tracing library for opentelemetry
$ pip install azure-core-tracing-opentelemetry
$ # from this directory
$ python sample_event_hub.py
```

### Azure EventHub Blob Storage Checkpoint Store

The following sample assumes that you have setup an Azure EventHubs namespace, [EventHub](https://docs.microsoft.com/azure/event-hubs/event-hubs-create) and Azure Blob [storage](https://docs.microsoft.com/azure/storage/blobs/storage-quickstart-blobs-portal).

* Update `APPLICATIONINSIGHTS_CONNECTION_STRING` environment variable
* Update `EVENT_HUB_CONN_STR` environment variable
* Update `EVENT_HUB_NAME` environment variable
* Update `AZURE_STORAGE_CONN_STR` environment variable

* Run the sample

```sh
$ # azure-eventhub-checkpointstoreblob library
$ pip install azure-eventhub-checkpointstoreblob
$ # azure sdk core tracing library for opentelemetry
$ pip install azure-core-tracing-opentelemetry
$ # from this directory
$ python sample_blob_checkpoint.py
```

### Azure EventGrid Send Event

The following sample assumes that you have setup an Azure Event Grid [Topic](https://docs.microsoft.com/azure/event-grid/custom-event-quickstart-portal).

* Update `APPLICATIONINSIGHTS_CONNECTION_STRING` environment variable
* Update `EG_ACCESS_KEY` environment variable
* Update `EG_TOPIC_HOSTNAME` environment variable

* Run the sample

```sh
$ # azure-azure-eventgrid library
$ pip install azure-eventgrid
$ # azure sdk core tracing library for opentelemetry
$ pip install azure-core-tracing-opentelemetry
$ # from this directory
$ python sample_event_grid.py
```

### Azure Form Recognizer Analyze Document

The following sample assumes that you have setup an Azure Form Recognizer [Resource](https://docs.microsoft.com/azure/cognitive-services/cognitive-services-apis-create-account).

* Update `APPLICATIONINSIGHTS_CONNECTION_STRING` environment variable

* Run the sample

```sh
$ # azure-ai-formrecognizer library
$ pip install azure-ai-formrecognizer
$ # azure sdk core tracing library for opentelemetry
$ pip install azure-core-tracing-opentelemetry
$ # from this directory
$ python sample_form_recognizer.py
```

### Azure KeyVault Create Certificate

The following sample assumes that you have setup an Azure Key Vault [resource](https://docs.microsoft.com/azure/key-vault/general/quick-create-portal) and a service [principal](https://docs.microsoft.com/azure/active-directory/develop/howto-create-service-principal-portal) for authentication.

* Update `APPLICATIONINSIGHTS_CONNECTION_STRING` environment variable

* Run the sample

```sh
$ # azure-keyvault-certificates library
$ pip install azure-keyvault-certificates
$ # azure-identity library for authentication
$ pip install azure-identity
$ # azure sdk core tracing library for opentelemetry
$ pip install azure-core-tracing-opentelemetry
$ # from this directory
$ python sample_key_cert.py
```

### Azure KeyVault Set Secret

The following sample assumes that you have setup an Azure Key Vault [resource](https://docs.microsoft.com/azure/key-vault/general/quick-create-portal) and a service [principal](https://docs.microsoft.com/azure/active-directory/develop/howto-create-service-principal-portal) for authentication.

* Update `APPLICATIONINSIGHTS_CONNECTION_STRING` environment variable

* Run the sample

```sh
$ # azure-keyvault-secrets library
$ pip install azure-keyvault-secrets
$ # azure-identity library for authentication
$ pip install azure-identity
$ # azure sdk core tracing library for opentelemetry
$ pip install azure-core-tracing-opentelemetry
$ # from this directory
$ python sample_key_secret.py
```

### Azure KeyVault Create Keys

The following sample assumes that you have setup an Azure Key Vault [resource](https://docs.microsoft.com/azure/key-vault/general/quick-create-portal) and a service [principal](https://docs.microsoft.com/azure/active-directory/develop/howto-create-service-principal-portal) for authentication.

* Update `APPLICATIONINSIGHTS_CONNECTION_STRING` environment variable

* Run the sample

```sh
$ # azure-keyvault-keys library
$ pip install azure-keyvault-keys
$ # azure-identity library for authentication
$ pip install azure-identity
$ # azure sdk core tracing library for opentelemetry
$ pip install azure-core-tracing-opentelemetry
$ # from this directory
$ python sample_key_keys.py
```

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

The following sample assumes that you have setup Azure Blob [storage](https://docs.microsoft.com/azure/storage/blobs/storage-quickstart-blobs-portal).

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
$ python sample_storage_blob.py
```

### Azure Text Analytics Extract Key Phrases

The following sample assumes that you have setup an Azure Cognitive Services [Resource](https://docs.microsoft.com/azure/cognitive-services/cognitive-services-apis-create-account).

* Update `APPLICATIONINSIGHTS_CONNECTION_STRING` environment variable

* Run the sample

```sh
$ # azure-ai-textanalytics library
$ pip install azure-ai-textanalytics
$ # azure sdk core tracing library for opentelemetry
$ pip install azure-core-tracing-opentelemetry
$ # from this directory
$ python sample_text_analytics.py
```

## Explore the data

After running the applications, data would be available in [Azure](
https://docs.microsoft.com/azure/azure-monitor/app/app-insights-overview#where-do-i-see-my-telemetry)
