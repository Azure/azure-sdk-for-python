# Azure Schema Registry Avro Serializer client library for Python

Azure Schema Registry is a schema repository service hosted by Azure Event Hubs, providing schema storage, versioning,
and management. This package provides an Avro serializer capable of serializing and deserializing payloads containing
Schema Registry schema identifiers and Avro-encoded data.

[Source code][source_code] | [Package (PyPi)][pypi] | [API reference documentation][api_reference] | [Samples][sr_avro_samples] | [Changelog][change_log]

## _Disclaimer_

_Azure SDK Python packages support for Python 2.7 is ending 01 January 2022. For more information and questions, please refer to https://github.com/Azure/azure-sdk-for-python/issues/20691_

## Getting started

### Install the package

Install the Azure Schema Registry Avro Serializer client library and Azure Identity client library for Python with [pip][pip]:

```Bash
pip install azure-schemaregistry-avroserializer azure-identity
```

### Prerequisites:
To use this package, you must have:
* Azure subscription - [Create a free account][azure_sub]
* [Azure Schema Registry][schemaregistry_service]
* Python 2.7, 3.6 or later - [Install Python][python]

### Authenticate the client
Interaction with the Schema Registry Avro Serializer starts with an instance of AvroSerializer class, which takes the schema group name and the [Schema Registry Client][schemaregistry_client] class. The client constructor takes the Event Hubs fully qualified namespace and and Azure Active Directory credential:

* The fully qualified namespace of the Schema Registry instance should follow the format: `<yournamespace>.servicebus.windows.net`.

* An AAD credential that implements the [TokenCredential][token_credential_interface] protocol should be passed to the constructor. There are implementations of the `TokenCredential` protocol available in the
[azure-identity package][pypi_azure_identity]. To use the credential types provided by `azure-identity`, please install the Azure Identity client library for Python with [pip][pip]:

```Bash
pip install azure-identity
```

* Additionally, to use the async API supported on Python 3.6+, you must first install an async transport, such as [aiohttp](https://pypi.org/project/aiohttp/):

```Bash
pip install aiohttp
```

**Create AvroSerializer using the azure-schemaregistry library:**

```python
from azure.schemaregistry import SchemaRegistryClient
from azure.schemaregistry.serializer.avroserializer import AvroSerializer
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()
# Namespace should be similar to: '<your-eventhub-namespace>.servicebus.windows.net'
fully_qualified_namespace = '<< FULLY QUALIFIED NAMESPACE OF THE SCHEMA REGISTRY >>'
group_name = '<< GROUP NAME OF THE SCHEMA >>'
schema_registry_client = SchemaRegistryClient(fully_qualified_namespace, credential)
serializer = AvroSerializer(client=schema_registry_client, group_name=group_name)
```

## Key concepts

### AvroSerializer

Provides API to serialize to and deserialize from Avro Binary Encoding plus a
header with schema ID. Uses [SchemaRegistryClient][schemaregistry_client] to get schema IDs from schema content or vice versa.

### Message format

The same format is used by schema registry serializers across Azure SDK languages.

Messages are encoded as follows:

- 4 bytes: Format Indicator

  - Currently always zero to indicate format below.

- 32 bytes: Schema ID

  - UTF-8 hexadecimal representation of GUID.
  - 32 hex digits, no hyphens.
  - Same format and byte order as string from Schema Registry service.

- Remaining bytes: Avro payload (in general, format-specific payload)

  - Avro Binary Encoding
  - NOT Avro Object Container File, which includes the schema and defeats the
    purpose of this serialzer to move the schema out of the message payload and
    into the schema registry.


## Examples

The following sections provide several code snippets covering some of the most common Schema Registry tasks, including:

- [Serialization](#serialization)
- [Deserialization](#deserialization)
- [Event Hubs Sending Integration](#event-hubs-sending-integration)
- [Event Hubs Receiving Integration](#event-hubs-receiving-integration)

### Serialization

Use `AvroSerializer.serialize` method to serialize dict data with the given avro schema.
The method would use a schema previously registered to the Schema Registry service and keep the schema cached for future serialization usage. It is also possible to avoid pre-registering the schema to the service and automatically register with the `serialize` method by instantiating the `AvroSerializer` with the keyword argument `auto_register_schemas=True`.

```python
import os
from azure.schemaregistry import SchemaRegistryClient
from azure.schemaregistry.serializer.avroserializer import AvroSerializer
from azure.identity import DefaultAzureCredential

token_credential = DefaultAzureCredential()
fully_qualified_namespace = os.environ['SCHEMAREGISTRY_FULLY_QUALIFIED_NAMESPACE']
group_name = "<your-group-name>"
name = "example.avro.User"
format = "Avro"

definition = """
{"namespace": "example.avro",
 "type": "record",
 "name": "User",
 "fields": [
     {"name": "name", "type": "string"},
     {"name": "favorite_number",  "type": ["int", "null"]},
     {"name": "favorite_color", "type": ["string", "null"]}
 ]
}"""

schema_registry_client = SchemaRegistryClient(fully_qualified_namespace, token_credential)
schema_register_client.register(group_name, name, definition, format)
serializer = AvroSerializer(client=schema_registry_client, group_name=group_name)

with serializer:
    dict_data = {"name": "Ben", "favorite_number": 7, "favorite_color": "red"}
    encoded_bytes = serializer.serialize(dict_data, schema=definition)
```

### Deserialization

Use `AvroSerializer.deserialize` method to deserialize raw bytes into dict data.
The method automatically retrieves the schema from the Schema Registry Service and keeps the schema cached for future deserialization usage.

```python
import os
from azure.schemaregistry import SchemaRegistryClient
from azure.schemaregistry.serializer.avroserializer import AvroSerializer
from azure.identity import DefaultAzureCredential

token_credential = DefaultAzureCredential()
fully_qualified_namespace = os.environ['SCHEMAREGISTRY_FULLY_QUALIFIED_NAMESPACE']
group_name = "<your-group-name>"

schema_registry_client = SchemaRegistryClient(fully_qualified_namespace, token_credential)
serializer = AvroSerializer(client=schema_registry_client, group_name=group_name)

with serializer:
    encoded_bytes = b'<data_encoded_by_azure_schema_registry_avro_serializer>'
    decoded_data = serializer.deserialize(encoded_bytes)
```

### Event Hubs Sending Integration

Integration with [Event Hubs][eventhubs_repo] to send serialized avro dict data as the body of EventData.

```python
import os
from azure.eventhub import EventHubProducerClient, EventData
from azure.schemaregistry import SchemaRegistryClient
from azure.schemaregistry.serializer.avroserializer import AvroSerializer
from azure.identity import DefaultAzureCredential

token_credential = DefaultAzureCredential()
fully_qualified_namespace = os.environ['SCHEMAREGISTRY_FULLY_QUALIFIED_NAMESPACE']
group_name = "<your-group-name>"
eventhub_connection_str = os.environ['EVENT_HUB_CONN_STR']
eventhub_name = os.environ['EVENT_HUB_NAME']

definition = """
{"namespace": "example.avro",
 "type": "record",
 "name": "User",
 "fields": [
     {"name": "name", "type": "string"},
     {"name": "favorite_number",  "type": ["int", "null"]},
     {"name": "favorite_color", "type": ["string", "null"]}
 ]
}"""

schema_registry_client = SchemaRegistryClient(fully_qualified_namespace, token_credential)
avro_serializer = AvroSerializer(client=schema_registry_client, group_name=group_name, auto_register_schemas=True)

eventhub_producer = EventHubProducerClient.from_connection_string(
    conn_str=eventhub_connection_str,
    eventhub_name=eventhub_name
)

with eventhub_producer, avro_serializer:
    event_data_batch = eventhub_producer.create_batch()
    dict_data = {"name": "Bob", "favorite_number": 7, "favorite_color": "red"}
    payload_bytes = avro_serializer.serialize(dict_data, schema=definition)
    event_data_batch.add(EventData(body=payload_bytes))
    eventhub_producer.send_batch(event_data_batch)
```

### Event Hubs Receiving Integration

Integration with [Event Hubs][eventhubs_repo] to receive `EventData` and deserialized raw bytes into avro dict data.

```python
import os
from azure.eventhub import EventHubConsumerClient
from azure.schemaregistry import SchemaRegistryClient
from azure.schemaregistry.serializer.avroserializer import AvroSerializer
from azure.identity import DefaultAzureCredential

token_credential = DefaultAzureCredential()
fully_qualified_namespace = os.environ['SCHEMAREGISTRY_FULLY_QUALIFIED_NAMESPACE']
group_name = "<your-group-name>"
eventhub_connection_str = os.environ['EVENT_HUB_CONN_STR']
eventhub_name = os.environ['EVENT_HUB_NAME']

schema_registry_client = SchemaRegistryClient(fully_qualified_namespace, token_credential)
avro_serializer = AvroSerializer(client=schema_registry_client, group_name=group_name)

eventhub_consumer = EventHubConsumerClient.from_connection_string(
    conn_str=eventhub_connection_str,
    consumer_group='$Default',
    eventhub_name=eventhub_name,
)

def on_event(partition_context, event):
    bytes_payload = b"".join(b for b in event.body)
    deserialized_data = avro_serializer.deserialize(bytes_payload)

with eventhub_consumer, avro_serializer:
    eventhub_consumer.receive(on_event=on_event, starting_position="-1")
```

## Troubleshooting

### General

Azure Schema Registry Avro Serializer raise exceptions defined in [Azure Core][azure_core].

### Logging
This library uses the standard
[logging][python_logging] library for logging.
Basic information about HTTP sessions (URLs, headers, etc.) is logged at INFO
level.

Detailed DEBUG level logging, including request/response bodies and unredacted
headers, can be enabled on a client with the `logging_enable` argument:
```python
import sys
import logging
from azure.schemaregistry import SchemaRegistryClient
from azure.schemaregistry.serializer.avroserializer import AvroSerializer
from azure.identity import DefaultAzureCredential

# Create a logger for the SDK
logger = logging.getLogger('azure.schemaregistry')
logger.setLevel(logging.DEBUG)

# Configure a console output
handler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(handler)

credential = DefaultAzureCredential()
schema_registry_client = SchemaRegistryClient("<your-fully_qualified_namespace>", credential, logging_enable=True)
# This client will log detailed information about its HTTP sessions, at DEBUG level
serializer = AvroSerializer(client=schema_registry_client, group_name="<your-group-name>")
```

Similarly, `logging_enable` can enable detailed logging for a single operation,
even when it isn't enabled for the client:
```py
serializer.serialize(dict_data, schema=schema_definition, logging_enable=True)
```

## Next steps

### More sample code

Please find further examples in the [samples][sr_avro_samples] directory demonstrating common Azure Schema Registry Avro Serializer scenarios.

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

<!-- LINKS -->
[pip]: https://pypi.org/project/pip/
[pypi]: https://pypi.org/project/azure-schemaregistry-avroserializer
[python]: https://www.python.org/downloads/
[azure_core]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/README.md
[azure_sub]: https://azure.microsoft.com/free/
[python_logging]: https://docs.python.org/3/library/logging.html
[sr_avro_samples]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/schemaregistry/azure-schemaregistry-avroserializer/samples
[api_reference]: https://docs.microsoft.com/python/api/overview/azure/schemaregistry-avroserializer-readme
[source_code]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/schemaregistry/azure-schemaregistry-avroserializer
[change_log]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/schemaregistry/azure-schemaregistry-avroserializer/CHANGELOG.md
[schemaregistry_client]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/schemaregistry/azure-schemaregistry
[schemaregistry_service]: https://aka.ms/schemaregistry
[eventhubs_repo]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/eventhub/azure-eventhub
[token_credential_interface]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/core/azure-core/azure/core/credentials.py
[pypi_azure_identity]: https://pypi.org/project/azure-identity/