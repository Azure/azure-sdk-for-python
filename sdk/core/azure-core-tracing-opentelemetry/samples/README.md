---
page_type: sample
languages:
  - python
products:
  - azure
urlFragment: azure-core-tracing-opentelemetry-samples
---

# Azure Core Tracing OpenTelemetry Integration Python Samples

These code samples show using the tracing OpenTelemetry integration with few services including servicebus, storage and eventgrid. A simple console span exporter is used in this example to export the calls. However, the code to use the azure monitor exporter has also been provided and commented in each sample.

* Trace Storage Calls to create a container: [sample_storage.py][python-sample-storage]
* Trace Eventgrid calls to publish an event : [sample_eventgrid.py][python-sample-eventgrid]
* Trace Servicebus calls to send messages to queue : [sample_servicebus.py][python-sample-servicebus]
* Trace Servicebus calls to receive messages from a queue : [sample_receive_sb.py][python-sample-servicebus-receive]
* Trace calls to send data to Eventhub : [sample_eventhubs.py][python-sample-eventhub-send]
* Trace calls to receive data from EventHub : [sample_receive_eh.py][python-sample-eventhub-receive]

It is assumed that the relevant SDKs are installed along with this extension. Below are the relevant packages which can be found in PyPI.

- [azure-storage-blob](https://pypi.org/project/azure-storage-blob/) v12 or greater.
- [azure-servicebus](https://pypi.org/project/azure-servicebus) v7 or greater.
- [azure-eventgrid](https://pypi.org/project/azure-eventgrid) v4 or greater.
- [azure-eventhub](https://pypi.org/project/azure-eventhub/) v5 or greater
- [opentelemetry-sdk](https://pypi.org/project/opentelemetry-sdk/)

[python-sample-storage]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core-tracing-opentelemetry/samples/sample_storage.py
[python-sample-eventgrid]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core-tracing-opentelemetry/samples/sample_eventgrid.py
[python-sample-servicebus]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core-tracing-opentelemetry/samples/sample_servicebus.py
[python-sample-servicebus-receive]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core-tracing-opentelemetry/samples/sample_receive_sb.py
[python-sample-eventhub-send]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core-tracing-opentelemetry/samples/sample_eventhubs.py
[python-sample-eventhub-receive]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core-tracing-opentelemetry/samples/sample_receive_eh.py
