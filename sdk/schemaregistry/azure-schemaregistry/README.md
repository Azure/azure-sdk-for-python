# Azure Schema Registry client library for Python

Azure Schema Registry is a schema repository service hosted by Azure Event Hubs, providing schema storage, versioning,
and management. The registry is leveraged by encoders to reduce payload size while describing payload structure with
schema identifiers rather than full schemas. This package provides:

1. A client library to register and retrieve schemas and their respective properties.

2. An JSON schema-based encoder capable of encoding and decoding payloads containing
Schema Registry schema identifiers, corresponding to JSON schemas used for validation, and encoded content.

[Source code][source_code]
| [Package (PyPi)][pypi]
| [Package (Conda)](https://anaconda.org/microsoft/azure-schemaregistry/)
| [API reference documentation][api_reference]
| [Samples][sr_samples]
| [Changelog][change_log]

## _Disclaimer_

_Azure SDK Python packages support for Python 2.7 has ended on 01 January 2022. For more information and questions, please refer to https://github.com/Azure/azure-sdk-for-python/issues/20691_

## Getting started

### Install the package

Install the Azure Schema Registry client library for Python with [pip][pip]:

```Bash
pip install azure-schemaregistry
```

To use the built-in `jsonschema` validators with the JSON Schema Encoder, install `jsonencoder` extras:

```Bash
pip install azure-schemaregistry[jsonencoder]
```

### Prerequisites:
To use this package, you must have:
* Azure subscription - [Create a free account][azure_sub]
* [Azure Schema Registry][schemaregistry_service] - [Here is the quickstart guide][quickstart_guide] to create a Schema Registry group using the Azure portal.
* Python 3.8 or later - [Install Python][python]

### Authenticate the client

Interaction with Schema Registry starts with an instance of SchemaRegistryClient class. The client constructor takes an Azure Event Hubs fully qualified namespace and an Azure Active Directory credential:

* The fully qualified namespace of the Schema Registry instance should follow the format: `<yournamespace>.servicebus.windows.net`.

* An AAD credential that implements the [TokenCredential][token_credential_interface] protocol should be passed to the constructor. There are implementations of the `TokenCredential` protocol available in the
[azure-identity package][pypi_azure_identity]. To use the credential types provided by `azure-identity`, please install the Azure Identity client library for Python with [pip][pip]:

```Bash
pip install azure-identity
```

* Additionally, to use the async API,  you must first install an async transport, such as [aiohttp](https://pypi.org/project/aiohttp/):

```Bash
pip install aiohttp
```

**Create client using the azure-identity library:**

```python
from azure.schemaregistry import SchemaRegistryClient
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()
# Namespace should be similar to: '<your-eventhub-namespace>.servicebus.windows.net/'
fully_qualified_namespace = os.environ['SCHEMAREGISTRY_FULLY_QUALIFIED_NAMESPACE']
schema_registry_client = SchemaRegistryClient(fully_qualified_namespace, credential)
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

### Client concepts

* Schema: Schema is the organization or structure for data. More detailed information can be found [here][schemas].

* Schema Group: A logical group of similar schemas based on business criteria, which can hold multiple versions of a schema. More detailed information can be found [here][schema_groups].

* SchemaRegistryClient: `SchemaRegistryClient` provides the API for storing and retrieving schemas in schema registry.

### Encoder concepts

* JsonSchemaEncoder: Provides API to encode content to and decode content from Binary Encoding, validate content against a JSON Schema, and cache schemas/schema IDs retrived from the registry using the `SchemaRegistryClient` locally.

* OutboundMessageContent: Protocol defined under `azure.schemaregistry` that allows for `JsonSchemaEncoder.encode` interoperability with certain Azure Messaging SDK message types. Support has been added to:
  * `azure.eventhub.EventData` for `azure-eventhub>=5.9.0`

* InboundMessageContent: Protocol defined under `azure.schemaregistry` that allows for `JsonSchemaEncoder.decode` interoperability with certain Azure Messaging SDK message types. Support has been added to:
  * `azure.eventhub.EventData` for `azure-eventhub>=5.9.0`

#### OutboundMessageContent/InboundMessageContent

If a message type that follows the OutboundMessageContent protocol is provided to the `JsonSchemaEncoder`, it will set the corresponding content and content type properties. If a message type object that follows the InboundMessageContent protocol is provided to the encoder, it will get the corresponding content and content type properties. These are defined as:

* `content`: Binary-encoded, JSON schema-validated payload (in general, format-specific payload)

* `content type`: a string of the format `application/json;serialization=Json+<schema ID>`, where:
  * `application/json;serialization=Json` is the format indicator
  * `<schema ID>` is the hexadecimal representation of GUID, same format and byte order as the string from the Schema Registry service.

If `EventData` is passed in as the message type, the following properties will be set on the `EventData` object:

* The `body` property will be set to the encoded content value.

* The `content_type` property will be set to the content type value.

If message type is not provided, and by default, the encoder will create the following dict:
`{"content": <encoded payload>, "content_type": 'application/json;serialization=Json+<schema ID>'}`

## Examples

The following sections provide several code snippets covering some of the most common Schema Registry and Json Schema Encoder tasks, including:

* [Register a schema](#register-a-schema)
* [Get the schema by id](#get-the-schema-by-id)
* [Get the schema by version](#get-the-schema-by-version)
* [Get the id of a schema](#get-the-id-of-a-schema)

* [Encode](#encode)
* [Decode](#decode)
* [Event Hubs Send Integration](#event-hubs-send-integration)
* [Event Hubs Receive Integration](#event-hubs-receive-integration)

### Register a schema

Use `SchemaRegistryClient.register_schema` method to register a schema.

```python
import os

from azure.identity import DefaultAzureCredential
from azure.schemaregistry import SchemaRegistryClient

token_credential = DefaultAzureCredential()
fully_qualified_namespace = os.environ['SCHEMAREGISTRY_AVRO_FULLY_QUALIFIED_NAMESPACE']
group_name = os.environ['SCHEMA_REGISTRY_GROUP']
name = "your-schema-name"
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
}
"""

schema_registry_client = SchemaRegistryClient(fully_qualified_namespace=fully_qualified_namespace, credential=token_credential)
with schema_registry_client:
    schema_properties = schema_registry_client.register_schema(group_name, name, definition, format)
    id = schema_properties.id
```

### Get the schema by id

Get the schema definition and its properties by schema id.

```python
import os

from azure.identity import DefaultAzureCredential
from azure.schemaregistry import SchemaRegistryClient

token_credential = DefaultAzureCredential()
fully_qualified_namespace = os.environ['SCHEMAREGISTRY_AVRO_FULLY_QUALIFIED_NAMESPACE']
schema_id = 'your-schema-id'

schema_registry_client = SchemaRegistryClient(fully_qualified_namespace=fully_qualified_namespace, credential=token_credential)
with schema_registry_client:
    schema = schema_registry_client.get_schema(schema_id)
    definition = schema.definition
    properties = schema.properties
```

### Get the schema by version

Get the schema definition and its properties by schema version.

```python
import os

from azure.identity import DefaultAzureCredential
from azure.schemaregistry import SchemaRegistryClient

token_credential = DefaultAzureCredential()
fully_qualified_namespace = os.environ['SCHEMAREGISTRY_AVRO_FULLY_QUALIFIED_NAMESPACE']
group_name = os.environ["SCHEMAREGISTRY_GROUP"]
name = "your-schema-name"
version = int("<your schema version>")

schema_registry_client = SchemaRegistryClient(fully_qualified_namespace=fully_qualified_namespace, credential=token_credential)
with schema_registry_client:
    schema = schema_registry_client.get_schema(group_name=group_name, name=name, version=version)
    definition = schema.definition
    properties = schema.properties
```

### Get the id of a schema

Get the schema id of a schema by schema definition and its properties.

```python
import os

from azure.identity import DefaultAzureCredential
from azure.schemaregistry import SchemaRegistryClient

token_credential = DefaultAzureCredential()
fully_qualified_namespace = os.environ['SCHEMAREGISTRY_AVRO_FULLY_QUALIFIED_NAMESPACE']
group_name = os.environ['SCHEMA_REGISTRY_GROUP']
name = "your-schema-name"
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
}
"""

schema_registry_client = SchemaRegistryClient(fully_qualified_namespace=fully_qualified_namespace, credential=token_credential)
with schema_registry_client:
    schema_properties = schema_registry_client.register_schema(group_name, name, definition, format)
    id = schema_properties.id
```

### Encode

Use the `SchemaRegistryClient` to pre-register the schema. Encode and validate the content with the `JsonSchemaEncoder`.

The `encode` method automatically retrieves the schema from the Schema Registry Service, validates against the content, and caches the schema locally.

```python
import os
import json
from azure.schemaregistry import SchemaRegistryClient, SchemaFormat
from azure.schemaregistry.encoder.jsonencoder import JsonSchemaEncoder
from azure.identity import DefaultAzureCredential
from azure.eventhub import EventData

token_credential = DefaultAzureCredential()
fully_qualified_namespace = os.environ['SCHEMAREGISTRY_JSON_FULLY_QUALIFIED_NAMESPACE']
group_name = os.environ['SCHEMAREGISTRY_GROUP']
format = SchemaFormat.JSON
DRAFT2020_12_SCHEMA_IDENTIFIER = "https://json-schema.org/draft/2020-12/schema"

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
name = schema["title"]
definition = json.dumps(schema)

schema_registry_client = SchemaRegistryClient(fully_qualified_namespace, token_credential)
schema_properties = schema_registry_client.register_schema(group_name, name, definition, format)
schema_id = schema_properties.id

# group_name only needed if passing `schema` to encode
encoder = JsonSchemaEncoder(client=schema_registry_client, validate=DRAFT2020_12_SCHEMA_IDENTIFIER, group_name=group_name)

with encoder:
    dict_content = {"name": "Ben", "favorite_number": 7, "favorite_color": "red"}
    event_data = encoder.encode(dict_content, schema_id=schema_id, message_type=EventData)

    # OR

    message_content_dict = encoder.encode(dict_content, schema_id=schema_id)
    event_data = EventData.from_message_content(message_content_dict["content"], message_content_dict["content_type"])

    # OR

    dict_content = {"name": "Ben", "favorite_number": 7, "favorite_color": "red"}
    message_content = encoder.encode(dict_content, schema=definition)  # group_name required in constructor when `schema` is passed
```

### Decode

Decode the content with the `JsonSchemaEncoder`.

The `decode` method automatically retrieves the schema from the Schema Registry Service, validates against the content, and caches the schema locally.

```python
import os
from azure.schemaregistry import SchemaRegistryClient
from azure.schemaregistry.encoder.jsonencoder import JsonSchemaEncoder
from azure.identity import DefaultAzureCredential

token_credential = DefaultAzureCredential()
fully_qualified_namespace = os.environ['SCHEMAREGISTRY_FULLY_QUALIFIED_NAMESPACE']
group_name = os.environ["SCHEMAREGISTRY_GROUP"]
DRAFT2020_12_SCHEMA_IDENTIFIER = "https://json-schema.org/draft/2020-12/schema"

schema_registry_client = SchemaRegistryClient(fully_qualified_namespace, token_credential)
encoder = JsonSchemaEncoder(client=schema_registry_client, validate=DRAFT2020_12_SCHEMA_IDENTIFIER)

with encoder:
    # event_data is an EventData object with encoded body
    decoded_content = encoder.decode(event_data)

    # OR 

    # content_dict is a TypedDict with encoded content and JSON content type 
    decoded_content = encoder.decode(content_dict)
```

### Event Hubs Send Integration

Integration with [Event Hubs][eventhubs_repo] to send an `EventData` object with `body` set to encoded content and corresponding `content_type`.

```python
import os
from azure.eventhub import EventHubProducerClient, EventData
from azure.schemaregistry import SchemaRegistryClient
from azure.schemaregistry.encoder.jsonencoder import JsonSchemaEncoder
from azure.identity import DefaultAzureCredential

token_credential = DefaultAzureCredential()
fully_qualified_namespace = os.environ['SCHEMAREGISTRY_JSON_FULLY_QUALIFIED_NAMESPACE']
group_name = os.environ['SCHEMAREGISTRY_GROUP']
eventhub_connection_str = os.environ['EVENT_HUB_CONN_STR']
eventhub_name = os.environ['EVENT_HUB_NAME']

schema_id = os.environ['PERSON_JSON_SCHEMA_ID']
DRAFT2020_12_SCHEMA_IDENTIFIER = "https://json-schema.org/draft/2020-12/schema"

schema_registry_client = SchemaRegistryClient(fully_qualified_namespace, token_credential)
json_schema_encoder = JsonSchemaEncoder(client=schema_registry_client, validate=DRAFT2020_12_SCHEMA_IDENTIFIER)

eventhub_producer = EventHubProducerClient.from_connection_string(
    conn_str=eventhub_connection_str,
    eventhub_name=eventhub_name
)

with eventhub_producer, json_schema_encoder:
    event_data_batch = eventhub_producer.create_batch()
    dict_content = {"name": "Bob", "favorite_number": 7, "favorite_color": "red"}
    event_data = json_schema_encoder.encode(dict_content, schema_id=schema_id, message_type=EventData)
    event_data_batch.add(event_data)
    eventhub_producer.send_batch(event_data_batch)
```

### Event Hubs Receive Integration

Integration with [Event Hubs][eventhubs_repo] to receive an `EventData` object and decode the encoded `body` value.

```python
import os
from azure.eventhub import EventHubConsumerClient
from azure.schemaregistry import SchemaRegistryClient
from azure.schemaregistry.encoder.jsonencoder import JsonSchemaEncoder
from azure.identity import DefaultAzureCredential

token_credential = DefaultAzureCredential()
fully_qualified_namespace = os.environ['SCHEMAREGISTRY_JSON_FULLY_QUALIFIED_NAMESPACE']
group_name = os.environ['SCHEMAREGISTRY_GROUP']
eventhub_connection_str = os.environ['EVENT_HUB_CONN_STR']
eventhub_name = os.environ['EVENT_HUB_NAME']
DRAFT2020_12_SCHEMA_IDENTIFIER = "https://json-schema.org/draft/2020-12/schema"

schema_registry_client = SchemaRegistryClient(fully_qualified_namespace, token_credential)
json_schema_encoder = JsonSchemaEncoder(client=schema_registry_client, validate=DRAFT2020_12_SCHEMA_IDENTIFIER)

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

Schema Registry clients raise exceptions defined in [Azure Core][azure_core] if errors are encountered when communicating with the Schema Registry service.

Errors when encoding and decoding related to invalid content/content types will be raised as `azure.schemaregistry.encoder.jsonencoder.InvalidContentError`, where `__cause__` will possibly contain an underlying exception.

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
DRAFT2020_12_SCHEMA_IDENTIFIER = "https://json-schema.org/draft/2020-12/schema"
credential = DefaultAzureCredential()
# This client will log detailed information about its HTTP sessions, at DEBUG level
schema_registry_client = SchemaRegistryClient(fully_qualified_namespace, credential, logging_enable=True)
encoder = JsonSchemaEncoder(client=schema_registry_client, validate=DRAFT2020_12_SCHEMA_IDENTIFIER)
```

Similarly, `logging_enable` can enable detailed logging for a single operation,
even when it isn't enabled for the client:

```python
schema_registry_client.get_schema(schema_id, logging_enable=True)
```

## Next steps

### More sample code

Please take a look at the [samples][sr_samples] directory for detailed examples of how to use this library to register and retrieve schema to/from Schema Registry.

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
[pypi]: https://pypi.org/project/azure-schemaregistry
[python]: https://www.python.org/downloads/
[azure_core]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/README.md
[azure_sub]: https://azure.microsoft.com/free/
[python_logging]: https://docs.python.org/3/library/logging.html
[sr_samples]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/schemaregistry/azure-schemaregistry/samples
[api_reference]: https://learn.microsoft.com/python/api/overview/azure/schemaregistry-readme
[source_code]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/schemaregistry/azure-schemaregistry
[change_log]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/schemaregistry/azure-schemaregistry/CHANGELOG.md
[schemas]: https://learn.microsoft.com/azure/event-hubs/schema-registry-overview#schemas
[schema_groups]: https://learn.microsoft.com/azure/event-hubs/schema-registry-overview#schema-groups
[schemaregistry_service]: https://aka.ms/schemaregistry
[token_credential_interface]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/core/azure-core/azure/core/credentials.py
[eventhubs_repo]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/eventhub/azure-eventhub
[pypi_azure_identity]: https://pypi.org/project/azure-identity/
[quickstart_guide]: https://learn.microsoft.com/azure/event-hubs/create-schema-registry