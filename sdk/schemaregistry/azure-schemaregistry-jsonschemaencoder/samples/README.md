---
page_type: sample
languages:
  - python
products:
  - azure
  - azure-event-hubs
urlFragment: schemaregistry-jsonschemaencoder-samples
---

# Azure Schema Registry JSON Schema Encoder library for Python Samples

These are code samples that show common scenario operations with the Schema Registry JSON Schema Encoder library.

Several Schema Registry JSON Schema Encoder Python SDK samples are available to you in the SDK's GitHub repository. These samples provide example code for additional scenarios commonly encountered while working with Schema Registry JSON Schema Encoder:

* [encode_and_decode_event_data_message.py][encode_and_decode_event_data_message_sample] ([async version][encode_and_decode_event_data_message_async_sample]) - Examples for common Schema Registry JSON Schema Encoder tasks:
    * Encode content according to the given schema and create EventData object
    * Decode content given an EventData object with encoded content and corresponding content type
* [eventhub_send_integration.py][eventhub_send_integration_sample] ([async version][eventhub_send_integration_async_sample]) - Examples for integration with EventHub in sending tasks:
    * Encode content with the given schema and send `EventData` to Event Hubs.
* [eventhub_receive_integration.py][eventhub_receive_integration_sample] ([async version][eventhub_receive_integration_async_sample]) - Examples for integration with EventHub in receiving tasks:
    * Receive `EventData` from Event Hubs and decode the received bytes.

## Prerequisites
- Python 3.7 or later.
- **Microsoft Azure Subscription:**  To use Azure services, including Azure Schema Registry, you'll need a subscription.
If you do not have an existing Azure account, you may sign up for a free trial or use your MSDN subscriber benefits when you [create an account](https://account.windowsazure.com/Home/Index).

## Setup

1. Install the Azure Schema Registry JSON Schema Encoder client library and Azure Identity client library for Python with [pip](https://pypi.org/project/pip/):

```bash
pip install azure-schemaregistry-jsonschemaencoder azure-identity
```

Additionally, if using with `azure.eventhub.EventData`, install `azure-eventhub>=5.9.0`:

```bash
pip install azure-eventhub>=5.9.0
```

2. Clone or download this sample repository
3. Open the sample folder in Visual Studio Code or your IDE of choice.

## Running the samples

1. Open a terminal window and `cd` to the directory that the samples are saved in.
2. Set the environment variables specified in the sample file you wish to run.
3. Follow the usage described in the file, e.g. `python encode_and_decode_event_data_message.py`

## Next steps

Check out the [API reference documentation][api_reference] to learn more about
what you can do with the Azure Schema Registry JSON Schema Encoder library.

<!-- LINKS -->
[encode_and_decode_event_data_message_sample]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/schemaregistry/azure-schemaregistry-jsonschemaencoder/samples/sync_samples/encode_and_decode_event_data_message.py
[eventhub_send_integration_sample]:  https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/schemaregistry/azure-schemaregistry-jsonschemaencoder/samples/sync_samples/eventhub_send_integration.py
[eventhub_receive_integration_sample]:  https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/schemaregistry/azure-schemaregistry-jsonschemaencoder/samples/sync_samples/eventhub_receive_integration.py
[encode_and_decode_event_data_message_async_sample]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/schemaregistry/azure-schemaregistry-jsonschemaencoder/samples/async_samples/encode_and_decode_event_data_message_async.py
[eventhub_send_integration_async_sample]:  https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/schemaregistry/azure-schemaregistry-jsonschemaencoder/samples/async_samples/eventhub_send_integration_async.py
[eventhub_receive_integration_async_sample]:  https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/schemaregistry/azure-schemaregistry-jsonschemaencoder/samples/async_samples/eventhub_receive_integration_async.py
[api_reference]: https://docs.microsoft.com/python/api/overview/azure/schemaregistry-jsonschemaencoder-readme
