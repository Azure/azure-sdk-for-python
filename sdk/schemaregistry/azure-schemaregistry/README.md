# Azure Schema Registry client library for Python

Azure Schema Registry is a schema repository service hosted by Azure Event Hubs, providing schema storage, versioning,
and management. The registry is leveraged by serializers to reduce payload size while describing payload structure with
schema identifiers rather than full schemas.

[Source code][source_code] | [Package (PyPi)][pypi] | [API reference documentation][api_reference] | [Samples][sr_samples] | [Changelog][change_log]

## Getting started

### Install the package

Install the Azure Schema Registry client library and Azure Identity client library for Python with [pip][pip]:

```Bash
pip install azure-schemaregistry azure-identity
```

### Prerequisites: 
To use this package, you must have:
* Azure subscription - [Create a free account][azure_sub]
* [Azure Schema Registry][schemaregistry_service]
* Python 2.7, 3.5 or later - [Install Python][python]

### Authenticate the client
Interaction with Schema Registry starts with an instance of SchemaRegistryClient class. You need the endpoint and AAD credential to instantiate the client object. 

**Create client using the azure-identity library:**

```python
from azure.schemaregistry import SchemaRegistryClient
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()
endpoint = '<< ENDPOINT OF THE SCHEMA REGISTRY >>'
schema_registry_client = SchemaRegistryClient(endpoint, credential)
```

## Key concepts

- Schema: Schema is the organization or structure for data.

- SchemaRegistryClient: `SchemaRegistryClient ` provides the API for storing and retrieving schemas in schema registry.

## Examples

The following sections provide several code snippets covering some of the most common Schema Registry tasks, including:

- [Register a schema](#register-a-schema)
- [Get the schema by id](#get-the-schema-by-id)
- [Get the id of a schema](#get-the-id-of-a-schema)

### Register a schema

Use `SchemaRegistryClient.register_schema` method to register a schema.

```python
import os

from azure.identity import DefaultAzureCredential
from azure.schemaregistry import SchemaRegistryClient

token_credential = DefaultAzureCredential()
endpoint = os.environ['SCHEMA_REGISTRY_ENDPOINT']
schema_group = "<your-group-name>"
schema_name = "<your-schema-name>"
serialization_type = "Avro"
schema_content = """
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

schema_registry_client = SchemaRegistryClient(endpoint=endpoint, credential=token_credential)
with schema_registry_client:
    schema_properties = schema_registry_client.register_schema(schema_group, schema_name, serialization_type, schema_content)
    schema_id = schema_properties.schema_id
```

### Get the schema by id

Get the schema content and its properties by schema id.

```python
import os

from azure.identity import DefaultAzureCredential
from azure.schemaregistry import SchemaRegistryClient

token_credential = DefaultAzureCredential()
endpoint = os.environ['SCHEMA_REGISTRY_ENDPOINT']
schema_id = '<your-schema-id>'

schema_registry_client = SchemaRegistryClient(endpoint=endpoint, credential=token_credential)
with schema_registry_client:
    schema = schema_registry_client.get_schema(schema_id)
    schema_content = schema.schema_content
```

### Get the id of a schema

Get the schema id of a schema by schema content and its properties.

```python
import os

from azure.identity import DefaultAzureCredential
from azure.schemaregistry import SchemaRegistryClient

token_credential = DefaultAzureCredential()
endpoint = os.environ['SCHEMA_REGISTRY_ENDPOINT']
schema_group = "<your-group-name>"
schema_name = "<your-schema-name>"
serialization_type = "Avro"
schema_content = """
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

schema_registry_client = SchemaRegistryClient(endpoint=endpoint, credential=token_credential)
with schema_registry_client:
    schema_properties = schema_registry_client.get_schema_id(schema_group, schema_name, serialization_type, schema_content)
    schema_id = schema_properties.schema_id
```

## Troubleshooting

### General

Schema Registry clients raise exceptions defined in [Azure Core][azure_core].

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
from azure.identity import DefaultAzureCredential

# Create a logger for the SDK
logger = logging.getLogger('azure.schemaregistry')
logger.setLevel(logging.DEBUG)

# Configure a console output
handler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(handler)

credential = DefaultAzureCredential()
# This client will log detailed information about its HTTP sessions, at DEBUG level
schema_registry_client = SchemaRegistryClient("you_end_point", credential, logging_enable=True)
```

Similarly, `logging_enable` can enable detailed logging for a single operation,
even when it isn't enabled for the client:
```py
schema_registry_client.get_schema(schema_id, logging_enable=True)
```

## Next steps

### More sample code

Please take a look at the [samples][sr_samples] directory for detailed examples of how to use this library to register and retrieve schema to/from Schema Registry.

### Event Hubs and Avro Serializer

We provide [azure-schemaregistry-avroserializer][schemaregistry_avroserializer_pypi] library as serializer
implementation to serialize/deserialize avro data integrated with `azure-schemaregistry` for automatic schema registration and retrieval.
It integrates nicely with the [EventHubs SDK][eventhubs_repo].
For more information and sample codes, please refer to the [Azure Schema Registry Avro Serializer SDK][schemaregistry_avroserializer_repo].

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
[azure_core]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/core/azure-core/README.md
[azure_sub]: https://azure.microsoft.com/free/
[python_logging]: https://docs.python.org/3/library/logging.html
[sr_samples]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/schemaregistry/azure-schemaregistry/samples
[api_reference]: https://azuresdkdocs.blob.core.windows.net/$web/python/azure-schemaregistry/latest/index.html
[source_code]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/schemaregistry/azure-schemaregistry
[change_log]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/schemaregistry/azure-schemaregistry/CHANGELOG.md
[schemaregistry_service]: https://aka.ms/schemaregistry
[schemaregistry_avroserializer_repo]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/schemaregistry/azure-schemaregistry-avroserializer
[schemaregistry_avroserializer_pypi]: https://pypi.org/project/azure-schemaregistry-avroserializer/
[eventhubs_repo]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/eventhub/azure-eventhub