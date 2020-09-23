---
page_type: sample
languages:
  - python
products:
  - azure
  - azure-schema-registry-avro-serializer
urlFragment: schemaregistry-avroserializer-samples
---

# Azure Schema Registry Avro Serializer library for Python Samples

These are code samples that show common scenario operations with the Schema Registry Avro Serializer library.

Several Schema Registry Avro Serializer Python SDK samples are available to you in the SDK's GitHub repository. These samples provide example code for additional scenarios commonly encountered while working with Schema Registry Avro Serializer:

* [avro_serializer.py][avro_serializer_sample] - Examples for common Schema Registry Avro Serializer tasks:
    * Serialize data according to the given schema
    * Deserialize data
* [eventhub_send_integration.py][eventhub_send_integration_sample] - Examples for integration with EventHub in sending tasks:
    * Serialize data with the given schema and send `EventData` to Event Hubs.
* [eventhub_receive_integration.py][eventhub_receive_integration_sample] - Examples for integration with EventHub in receiving tasks:
    * Receive `EventData` from Event Hubs and deserialize the received bytes.

## Prerequisites
- Python 2.7, 3.5 or later.
- **Microsoft Azure Subscription:**  To use Azure services, including Azure Schema Registry, you'll need a subscription.
If you do not have an existing Azure account, you may sign up for a free trial or use your MSDN subscriber benefits when you [create an account](https://account.windowsazure.com/Home/Index).

## Setup

1. Install the Azure Schema Registry Avro Serializer client library and Azure Identity client library for Python with [pip](https://pypi.org/project/pip/):

```bash
pip install azure-schemaregistry-avroserializer azure-identity
```

2. Clone or download this sample repository
3. Open the sample folder in Visual Studio Code or your IDE of choice.

## Running the samples

1. Open a terminal window and `cd` to the directory that the samples are saved in.
2. Set the environment variables specified in the sample file you wish to run.
3. Follow the usage described in the file, e.g. `python avro_serializer.py`

## Next steps

Check out the [API reference documentation][api_reference] to learn more about
what you can do with the Azure Schema Registry Avro Serializer library.

<!-- LINKS -->
[avro_serializer_sample]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/schemaregistry/azure-schemaregistry-avroserializer/samples/avro_serializer.py
[eventhub_send_integration_sample]:  https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/schemaregistry/azure-schemaregistry-avroserializer/samples/eventhub_send_integration.py
[eventhub_receive_integration_sample]:  https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/schemaregistry/azure-schemaregistry-avroserializer/samples/eventhub_receive_integration.py
[api_reference]: https://azuresdkdocs.blob.core.windows.net/$web/python/azure-schemaregistry-avroserializer/latest/index.html
