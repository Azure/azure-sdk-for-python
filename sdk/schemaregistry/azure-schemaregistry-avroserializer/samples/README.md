---
page_type: sample
languages:
  - python
products:
  - azure
  - azure-event-hubs
urlFragment: schemaregistry-avroserializer-samples
---

# Azure Schema Registry Avro serializer library for Python Samples

These are code samples that show common scenario operations with the Schema Registry Avro serializer library.

Several Schema Registry Avro serializer Python SDK samples are available to you in the SDK's GitHub repository. These samples provide example code for additional scenarios commonly encountered while working with Schema Registry Avro serializer:

* [serialize_and_deserialize_event_data_message.py][serialize_and_deserialize_event_data_message_sample] ([async version][serialize_and_deserialize_event_data_message_async_sample]) - Examples for common Schema Registry Avro serializer tasks:
    * Serialize data according to the given schema and create EventData object
    * Deserialize data given an EventData object with serialized data and corresponding content type
* [eventhub_send_integration.py][eventhub_send_integration_sample] ([async version][eventhub_send_integration_async_sample]) - Examples for integration with EventHub in sending tasks:
    * Serialize data with the given schema and send `EventData` to Event Hubs.
* [eventhub_receive_integration.py][eventhub_receive_integration_sample] ([async version][eventhub_receive_integration_async_sample]) - Examples for integration with EventHub in receiving tasks:
    * Receive `EventData` from Event Hubs and deserialize the received bytes.

## Prerequisites
- Python 3.6 or later.
- **Microsoft Azure Subscription:**  To use Azure services, including Azure Schema Registry, you'll need a subscription.
If you do not have an existing Azure account, you may sign up for a free trial or use your MSDN subscriber benefits when you [create an account](https://account.windowsazure.com/Home/Index).

## Setup

1. Install the Azure Schema Registry Avro serializer client library and Azure Identity client library for Python with [pip](https://pypi.org/project/pip/):

```bash
pip install azure-schemaregistry-avroserializer azure-identity
```

Additionally, if using with `azure.eventhub.EventData`, install `azure-eventhub==5.9.0b1`:

```bash
pip install azure-eventhub==5.9.0b1
```

2. Clone or download this sample repository
3. Open the sample folder in Visual Studio Code or your IDE of choice.

## Running the samples

1. Open a terminal window and `cd` to the directory that the samples are saved in.
2. Set the environment variables specified in the sample file you wish to run.
3. Follow the usage described in the file, e.g. `python serialize_and_deserialize_event_data_message.py`

## Next steps

Check out the [API reference documentation][api_reference] to learn more about
what you can do with the Azure Schema Registry Avro serializer library.

<!-- LINKS -->
[serialize_and_deserialize_event_data_message_sample]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/schemaregistry/azure-schemaregistry-avroserializer/samples/sync_samples/serialize_and_deserialize_event_data_message.py
[eventhub_send_integration_sample]:  https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/schemaregistry/azure-schemaregistry-avroserializer/samples/sync_samples/eventhub_send_integration.py
[eventhub_receive_integration_sample]:  https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/schemaregistry/azure-schemaregistry-avroserializer/samples/sync_samples/eventhub_receive_integration.py
[serialize_and_deserialize_event_data_message_async_sample]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/schemaregistry/azure-schemaregistry-avroserializer/samples/async_samples/serialize_and_deserialize_event_data_message_async.py
[eventhub_send_integration_async_sample]:  https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/schemaregistry/azure-schemaregistry-avroserializer/samples/async_samples/eventhub_send_integration_async.py
[eventhub_receive_integration_async_sample]:  https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/schemaregistry/azure-schemaregistry-avroserializer/samples/async_samples/eventhub_receive_integration_async.py
[api_reference]: https://docs.microsoft.com/python/api/overview/azure/schemaregistry-avroserializer-readme
