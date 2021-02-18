---
page_type: sample
languages:
  - python
products:
  - azure
  - azure-core-tracing-opentelemetry
urlFragment: azure-core-tracing-opentelemetry-samples
---

# Azure Core Tracing Opentelemetry Integration Python Samples

These code samples show using the tracing opentelemetry integration with few services including servicebus, storage and eventgrid. A simple console span exporter is used in this example to export the calls. However, the code to use the azure monitor exporter has also been provided and commented in each sample.

* Trace Storage Calls to create a container: [sample_storage.py][python-sample-storage]
* Trace Eventgrid calls to publish an event : [sample_eventgrid.py][python-sample-eventgrid]
* Trace Servicebus calls to send messages to queue : [sample_servicebus.py][python-sample-servicebus]

It is assumed that the relevant SDKs are installed along with this extension. Below are the relevant packages which can be found in PyPI.

- [azure-storage-blob](https://pypi.org/project/azure-storage-blob/) v12 or greater.
- [azure-servicebus](https://pypi.org/project/azure-servicebus) v7 or greater.
- [azure-eventgrid](https://pypi.org/project/azure-eventgrid) v2.0.0b1 or greater.
- [opentelemtry-sdk](https://pypi.org/project/opentelemetry-sdk/)

[python-sample-storage]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/core/azure-core-tracing-opentelemetry/samples/sample_storage.py
[python-sample-eventgrid]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/core/azure-core-tracing-opentelemetry/samples/sample_eventgrid.py
[python-sample-servicebus]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/core/azure-core-tracing-opentelemetry/samples/sample_servicebus.py
