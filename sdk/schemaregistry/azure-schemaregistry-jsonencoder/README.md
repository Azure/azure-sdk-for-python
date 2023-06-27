# Azure Schema Registry JSON Schema Encoder client library for Python

Azure Schema Registry is a schema repository service hosted by Azure Event Hubs, providing schema storage, versioning,
and management. This package provides an JSON encoder capable of encoding and decoding payloads containing
Schema Registry schema identifiers and corresponding encoded content.

[Source code][source_code] | [Package (PyPi)][pypi] | [API reference documentation][api_reference] | [Samples][sr_json_samples] | [Changelog][change_log]

## _Disclaimer_

_Azure SDK Python packages support for Python 2.7 has ended 01 January 2022. For more information and questions, please refer to https://github.com/Azure/azure-sdk-for-python/issues/20691_

## Getting started

### Install the package

Install the Azure Schema Registry JSON Schema Encoder client library for Python with [pip][pip]:

```Bash
pip install azure-schemaregistry-jsonencoder
```

### Prerequisites:
To use this package, you must have:
* Azure subscription - [Create a free account][azure_sub]
* [Azure Schema Registry][schemaregistry_service] - [Here is the quickstart guide][quickstart_guide] to create a Schema Registry group using the Azure portal.
* Python 3.7 or later - [Install Python][python]

### Authenticate the client
Interaction with the Schema Registry JSON Schema Encoder starts with an instance of JsonSchemaEncoder class, which takes the schema group name and the [Schema Registry Client][schemaregistry_client] class. The client constructor takes the Event Hubs fully qualified namespace and and Azure Active Directory credential:

* The fully qualified namespace of the Schema Registry instance should follow the format: `<yournamespace>.servicebus.windows.net`.

* An AAD credential that implements the [TokenCredential][token_credential_interface] protocol should be passed to the constructor. There are implementations of the `TokenCredential` protocol available in the
[azure-identity package][pypi_azure_identity]. To use the credential types provided by `azure-identity`, please install the Azure Identity client library for Python with [pip][pip]:

```Bash
pip install azure-identity
```

* Additionally, to use the async API, you must first install an async transport, such as [aiohttp](https://pypi.org/project/aiohttp/):

```Bash
pip install aiohttp
```

**Create JsonSchemaEncoder using the azure-schemaregistry library:**

```python
import os
from azure.schemaregistry import SchemaRegistryClient
from azure.schemaregistry.encoder.jsonencoder import JsonSchemaEncoder
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()
# Namespace should be similar to: '<your-eventhub-namespace>.servicebus.windows.net'
fully_qualified_namespace = os.environ['SCHEMAREGISTRY_FULLY_QUALIFIED_NAMESPACE']
group_name = os.environ['SCHEMAREGISTRY_GROUP']
schema_registry_client = SchemaRegistryClient(fully_qualified_namespace, credential)
encoder = JsonSchemaEncoder(client=schema_registry_client, group_name=group_name)
```

## Key concepts

### JsonSchemaEncoder

Provides API to encode to and decode from Binary Encoding plus a
content type with schema ID. Uses [SchemaRegistryClient][schemaregistry_client] to get schema IDs from schema content or vice versa.

### Supported message models

Support has been added to certain Azure Messaging SDK model classes for interoperability with the `JsonSchemaEncoder`. These models are subtypes of the `MessageType` protocol defined under the `azure.schemaregistry.encoder.jsonencoder` namespace. Currently, the supported model classes are:

- `azure.eventhub.EventData` for `azure-eventhub>=5.9.0`

### Message format

If a message type that follows the MessageType protocol is provided to the encoder for encoding, it will set the corresponding content and content type properties, where:

- `content`: encoded payload (in general, format-specific payload)
  - Binary Encoding
- `content type`: a string of the format `application/json+<schema ID>`, where:
  - `application/json` is the format indicator
  - `<schema ID>` is the hexadecimal representation of GUID, same format and byte order as the string from the Schema Registry service.

If `EventData` is passed in as the message type, the following properties will be set on the `EventData` object:
 - The `body` property will be set to the content value.
 - The `content_type` property will be set to the content type value.

If message type is not provided, and by default, the encoder will create the following dict:
`{"content": <encoded payload>, "content_type": 'application/json+<schema ID>' }`

## Examples

The following sections provide several code snippets covering some of the most common Schema Registry tasks, including:

- [Encoding](#encoding)
- [Decoding](#decoding)
- [Event Hubs Sending Integration](#event-hubs-sending-integration)
- [Event Hubs Receiving Integration](#event-hubs-receiving-integration)

### Encoding

Use the `JsonSchemaEncoder.encode` method to encode content with the given JSON schema.
The method will use a schema previously registered to the Schema Registry service and keep the schema cached for future encoding usage. In order to avoid pre-registering the schema to the service and automatically register it with the `encode` method, the keyword argument `auto_register=True` should be passed to the `JsonSchemaEncoder` constructor.

```python
import os
from azure.schemaregistry import SchemaRegistryClient
from azure.schemaregistry.encoder.jsonencoder import JsonSchemaEncoder
from azure.identity import DefaultAzureCredential
from azure.eventhub import EventData

token_credential = DefaultAzureCredential()
fully_qualified_namespace = os.environ['SCHEMAREGISTRY_JSON_FULLY_QUALIFIED_NAMESPACE']
group_name = os.environ['SCHEMAREGISTRY_GROUP']
format = "Json"

schema = {
    "$id": "https://example.com/person.schema.json",
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "Person",
    "type": "object",
    "properties": {
        "name": {
            "type": "string",
            "description": "Person's name."
        },
        "favorite_color": {
            "type": "string",
            "description": "Favorite color."
        },
        "favorite_number": {
            "description": "Favorite number.",
            "type": "integer",
        }
    }
}
definition = json.dumps(schema)

schema_registry_client = SchemaRegistryClient(fully_qualified_namespace, token_credential)
schema_registry_client.register_schema(group_name, name, definition, format)
encoder = JsonSchemaEncoder(client=schema_registry_client, group_name=group_name)

with encoder:
    dict_content = {"name": "Ben", "favorite_number": 7, "favorite_color": "red"}
    event_data = encoder.encode(dict_content, schema=definition, message_type=EventData)

    # OR

    message_content_dict = encoder.encode(dict_content, schema=definition)
    event_data = EventData.from_message_content(message_content_dict["content"], message_content_dict["content_type"])
```

### Decoding

Use the `JsonSchemaEncoder.decode` method to decode the encoded content by either:
 - Passing in a message object that is a subtype of the MessageType protocol.
 - Passing in a dict with keys `content`(type bytes) and `content_type` (type string).
The method automatically retrieves the schema from the Schema Registry Service and keeps the schema cached for future decoding usage.

```python
import os
from azure.schemaregistry import SchemaRegistryClient
from azure.schemaregistry.encoder.jsonencoder import JsonSchemaEncoder
from azure.identity import DefaultAzureCredential

token_credential = DefaultAzureCredential()
fully_qualified_namespace = os.environ['SCHEMAREGISTRY_FULLY_QUALIFIED_NAMESPACE']
group_name = "<your-group-name>"

schema_registry_client = SchemaRegistryClient(fully_qualified_namespace, token_credential)
encoder = JsonSchemaEncoder(client=schema_registry_client)

with encoder:
    # event_data is an EventData object with encoded body
    dict_content = {"name": "Ben", "favorite_number": 7, "favorite_color": "red"}
    event_data = encoder.encode(dict_content, schema=definition, message_type=EventData)
    decoded_content = encoder.decode(event_data)

    # OR 

    encoded_bytes = b'<content_encoded_by_azure_schema_registry_json_schema_encoder>'
    content_type = 'application/json+<schema_id_of_corresponding_schema>'
    content_dict = {"content": encoded_bytes, "content_type": content_type}
    decoded_content = encoder.decode(content_dict)
```

### Event Hubs Sending Integration

Integration with [Event Hubs][eventhubs_repo] to send an `EventData` object with `body` set to encoded content and corresponding `content_type`.

```python
import os
from azure.eventhub import EventHubProducerClient, EventData
from azure.schemaregistry import SchemaRegistryClient
from azure.schemaregistry.encoder.jsonencoder import JsonSchemaEncoder
from azure.identity import DefaultAzureCredential

token_credential = DefaultAzureCredential()
fully_qualified_namespace = os.environ['SCHEMAREGISTRY_FULLY_QUALIFIED_NAMESPACE']
group_name = os.environ['SCHEMAREGISTRY_GROUP']
eventhub_connection_str = os.environ['EVENT_HUB_CONN_STR']
eventhub_name = os.environ['EVENT_HUB_NAME']

schema = {
    "$id": "https://example.com/person.schema.json",
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "Person",
    "type": "object",
    "properties": {
        "name": {
            "type": "string",
            "description": "Person's name."
        },
        "favorite_color": {
            "type": "string",
            "description": "Favorite color."
        },
        "favorite_number": {
            "description": "Favorite number.",
            "type": "integer",
        }
    }
}
definition = json.dumps(schema)

schema_registry_client = SchemaRegistryClient(fully_qualified_namespace, token_credential)
json_schema_encoder = JsonSchemaEncoder(client=schema_registry_client, group_name=group_name, auto_register=True)

eventhub_producer = EventHubProducerClient.from_connection_string(
    conn_str=eventhub_connection_str,
    eventhub_name=eventhub_name
)

with eventhub_producer, json_schema_encoder:
    event_data_batch = eventhub_producer.create_batch()
    dict_content = {"name": "Bob", "favorite_number": 7, "favorite_color": "red"}
    event_data = json_schema_encoder.encode(dict_content, schema=definition, message_type=EventData)
    event_data_batch.add(event_data)
    eventhub_producer.send_batch(event_data_batch)
```

### Event Hubs Receiving Integration

Integration with [Event Hubs][eventhubs_repo] to receive an `EventData` object and decode the encoded `body` value.

```python
import os
from azure.eventhub import EventHubConsumerClient
from azure.schemaregistry import SchemaRegistryClient
from azure.schemaregistry.encoder.jsonencoder import JsonSchemaEncoder
from azure.identity import DefaultAzureCredential

token_credential = DefaultAzureCredential()
fully_qualified_namespace = os.environ['SCHEMAREGISTRY_FULLY_QUALIFIED_NAMESPACE']
group_name = os.environ['SCHEMAREGISTRY_GROUP']
eventhub_connection_str = os.environ['EVENT_HUB_CONN_STR']
eventhub_name = os.environ['EVENT_HUB_NAME']

schema_registry_client = SchemaRegistryClient(fully_qualified_namespace, token_credential)
json_schema_encoder = JsonSchemaEncoder(client=schema_registry_client, group_name=group_name)

eventhub_consumer = EventHubConsumerClient.from_connection_string(
    conn_str=eventhub_connection_str,
    consumer_group='$Default',
    eventhub_name=eventhub_name,
)

def on_event(partition_context, event):
    decoded_content = json_schema_encoder.decode(event)

with eventhub_consumer, json_schema_encoder:
    eventhub_consumer.receive(on_event=on_event, starting_position="-1")
```

## Troubleshooting

### General

Azure Schema Registry JSON Schema Encoder raises exceptions defined in [Azure Core][azure_core] if errors are encountered when communicating with the Schema Registry service. Errors related to invalid content/content types and invalid schemas will be raised as `azure.schemaregistry.encoder.jsonencoder.InvalidContentError` and `azure.schemaregistry.encoder.jsonencoder.InvalidSchemaError`, respectively, where `__cause__` will contain the underlying exception raised by the provided `validation`/`schema` callable.

### Logging
This library uses the standard
[logging][python_logging] library for logging.
Basic information about HTTP sessions (URLs, headers, etc.) is logged at INFO
level.

Detailed DEBUG level logging, including request/response bodies and unredacted
headers, can be enabled on a client with the `logging_enable` argument:
```python
import sys
import os
import logging
from azure.schemaregistry import SchemaRegistryClient
from azure.schemaregistry.encoder.jsonencoder import JsonSchemaEncoder
from azure.identity import DefaultAzureCredential

# Create a logger for the SDK
logger = logging.getLogger('azure.schemaregistry')
logger.setLevel(logging.DEBUG)

# Configure a console output
handler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(handler)

fully_qualified_namespace = os.environ['SCHEMAREGISTRY_FULLY_QUALIFIED_NAMESPACE']
group_name = os.environ['SCHEMAREGISTRY_GROUP']
credential = DefaultAzureCredential()
schema_registry_client = SchemaRegistryClient(fully_qualified_namespace, credential, logging_enable=True)
# This client will log detailed information about its HTTP sessions, at DEBUG level
encoder = JsonSchemaEncoder(client=schema_registry_client, group_name=group_name)
```

Similarly, `logging_enable` can enable detailed logging for a single operation,
even when it isn't enabled for the client:
```python
encoder.encode(dict_content, schema=definition, logging_enable=True)
```

## Next steps

### More sample code

Further examples demonstrating common Azure Schema Registry JSON Schema Encoder scenarios are in the [samples][sr_json_samples] directory.

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
[pypi]: https://pypi.org/project/azure-schemaregistry-jsonencoder/
[python]: https://www.python.org/downloads/
[azure_core]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/README.md
[azure_sub]: https://azure.microsoft.com/free/
[python_logging]: https://docs.python.org/3/library/logging.html
[sr_json_samples]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/schemaregistry/azure-schemaregistry-jsonencoder/samples
[api_reference]: https://docs.microsoft.com/python/api/overview/azure/schemaregistry-jsonschemaencoder-readme
[source_code]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/schemaregistry/azure-schemaregistry-jsonencoder
[change_log]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/schemaregistry/azure-schemaregistry-jsonencoder/CHANGELOG.md
[schemaregistry_client]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/schemaregistry/azure-schemaregistry
[schemaregistry_service]: https://aka.ms/schemaregistry
[eventhubs_repo]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/eventhub/azure-eventhub
[token_credential_interface]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/core/azure-core/azure/core/credentials.py
[pypi_azure_identity]: https://pypi.org/project/azure-identity/
[quickstart_guide]: https://docs.microsoft.com/azure/event-hubs/create-schema-registry