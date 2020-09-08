# Azure Schema Registry Avro Serializer client library for Python

Azure Schema Registry is a schema repository service hosted by Azure Event Hubs, providing schema storage, versioning,
and management. This package provides an Avro serializer capable of serializing and deserializing payloads containing
Schema Registry schema identifiers and Avro-encoded data.

[Source code][source_code] | [Package (PyPi)][pypi] | [API reference documentation][api_reference] | [Samples][sr_avro_samples] | [Changelog][change_log]

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
* Python 2.7, 3.5 or later - [Install Python][python]

### Authenticate the client
Interaction with Schema Registry Avro Serializer starts with an instance of SchemaRegistryAvroSerializer class. You need the endpoint, AAD credential and schema group name to instantiate the client object. 

**Create client using the azure-identity library:**

```python
from azure.schemaregistry import SchemaRegistryClient
from azure.schemaregistry.serializer.avroserializer import SchemaRegistryAvroSerializer
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()
endpoint = '<< ENDPOINT OF THE SCHEMA REGISTRY >>'
schema_group = '<< GROUP NAME OF THE SCHEMA >>'
schema_registry_client = SchemaRegistryClient(endpoint, credential)
serializer = SchemaRegistryAvroSerializer(schema_registry_client, schema_group)
```

## Key concepts

### SchemaRegistryAvroSerializer

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

### Serialization

```python
import os
from azure.schemaregistry import SchemaRegistryClient
from azure.schemaregistry.serializer.avroserializer import SchemaRegistryAvroSerializer
from azure.identity import DefaultAzureCredential

token_credential = DefaultAzureCredential()
endpoint = os.environ['SCHEMA_REGISTRY_ENDPOINT']
schema_group = "<your-group-name>"

schema_registry_client = SchemaRegistryClient(endpoint, token_credential)
serializer = SchemaRegistryAvroSerializer(schema_registry_client, schema_group)

schema_string = """
{"namespace": "example.avro",
 "type": "record",
 "name": "User",
 "fields": [
     {"name": "name", "type": "string"},
     {"name": "favorite_number",  "type": ["int", "null"]},
     {"name": "favorite_color", "type": ["string", "null"]}
 ]
}"""

with serializer:
    dict_data = {"name": "Ben", "favorite_number": 7, "favorite_color": "red"}
    encoded_bytes = serializer.serialize(dict_data, schema_string)
```

### Deserialization

```python
import os
from azure.schemaregistry import SchemaRegistryClient
from azure.schemaregistry.serializer.avroserializer import SchemaRegistryAvroSerializer
from azure.identity import DefaultAzureCredential

token_credential = DefaultAzureCredential()
endpoint = os.environ['SCHEMA_REGISTRY_ENDPOINT']
schema_group = "<your-group-name>"

schema_registry_client = SchemaRegistryClient(endpoint, token_credential)
serializer = SchemaRegistryAvroSerializer(schema_registry_client, schema_group)

with serializer:
    encoded_bytes = b'<data_encoded_by_azure_schema_registry_avro_serializer>'
    decoded_data = serializer.deserialize(encoded_bytes)
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
from azure.schemaregistry.serializer.avroserializer import SchemaRegistryAvroSerializer
from azure.identity import DefaultAzureCredential

# Create a logger for the SDK
logger = logging.getLogger('azure.schemaregistry')
logger.setLevel(logging.DEBUG)

# Configure a console output
handler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(handler)

credential = DefaultAzureCredential()
schema_registry_client = SchemaRegistryClient("<your-end-point>", credential)
# This client will log detailed information about its HTTP sessions, at DEBUG level
serializer = SchemaRegistryAvroSerializer(schema_registry_client, "<your-group-name>", logging_enable=True)
```

Similarly, `logging_enable` can enable detailed logging for a single operation,
even when it isn't enabled for the client:
```py
serializer.serialie(dict_data, schema_content, logging_enable=True)
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
[azure_core]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/core/azure-core/README.md
[azure_sub]: https://azure.microsoft.com/free/
[python_logging]: https://docs.python.org/3/library/logging.html
[sr_avro_samples]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/schemaregistry/azure-schemaregistry-avroserializer/samples
[api_reference]: https://azuresdkdocs.blob.core.windows.net/$web/python/azure-schemaregistry-avroserializer/latest/index.html
[source_code]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/schemaregistry/azure-schemaregistry-avroserializer
[change_log]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/schemaregistry/azure-schemaregistry-avroserializer/CHANGELOG.md
[schemaregistry_client]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/schemaregistry/azure-schemaregistry
[schemaregistry_service]: https://aka.ms/schemaregistry