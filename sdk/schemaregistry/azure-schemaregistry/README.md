# Azure Schema Registry client library for Python

Azure Schema Registry is a schema repository service hosted by Azure Event Hubs, providing schema storage, versioning,
and management. The registry is leveraged by serializers to reduce payload size while describing payload structure with
schema identifiers rather than full schemas.

[Source code][source_code] | [Package (PyPi)][pypi] | [API reference documentation][api_reference] | [Samples][sr_samples] | [Changelog][change_log]

## _Disclaimer_

_Azure SDK Python packages support for Python 2.7 has ended on 01 January 2022. For more information and questions, please refer to https://github.com/Azure/azure-sdk-for-python/issues/20691_

## Getting started

### Install the package

Install the Azure Schema Registry client library for Python with [pip][pip]:

```Bash
pip install azure-schemaregistry
```

### Prerequisites:
To use this package, you must have:
* Azure subscription - [Create a free account][azure_sub]
* [Azure Schema Registry][schemaregistry_service] - [Here is the quickstart guide][quickstart_guide] to create a Schema Registry group using the Azure portal.
* Python 3.6 or later - [Install Python][python]

### Authenticate the client

Interaction with Schema Registry starts with an instance of SchemaRegistryClient class. The client constructor takes the fully qualified namespace and an Azure Active Directory credential:

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
fully_qualified_namespace = '<< FULLY QUALIFIED NAMESPACE OF THE SCHEMA REGISTRY >>'
schema_registry_client = SchemaRegistryClient(fully_qualified_namespace, credential)
```

## Key concepts

- Schema: Schema is the organization or structure for data. More detailed information can be found [here][schemas].

- Schema Group: A logical group of similar schemas based on business criteria, which can hold multiple versions of a schema. More detailed information can be found [here][schema_groups].

- SchemaRegistryClient: `SchemaRegistryClient` provides the API for storing and retrieving schemas in schema registry.

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
fully_qualified_namespace = os.environ['SCHEMA_REGISTRY_FULLY_QUALIFIED_NAMESPACE']
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
fully_qualified_namespace = os.environ['SCHEMA_REGISTRY_FULLY_QUALIFIED_NAMESPACE']
schema_id = 'your-schema-id'

schema_registry_client = SchemaRegistryClient(fully_qualified_namespace=fully_qualified_namespace, credential=token_credential)
with schema_registry_client:
    schema = schema_registry_client.get_schema(schema_id)
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
fully_qualified_namespace = os.environ['SCHEMA_REGISTRY_FULLY_QUALIFIED_NAMESPACE']
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
schema_registry_client = SchemaRegistryClient("your_fully_qualified_namespace", credential, logging_enable=True)
```

Similarly, `logging_enable` can enable detailed logging for a single operation,
even when it isn't enabled for the client:
```py
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
[api_reference]: https://docs.microsoft.com/python/api/overview/azure/schemaregistry-readme
[source_code]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/schemaregistry/azure-schemaregistry
[change_log]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/schemaregistry/azure-schemaregistry/CHANGELOG.md
[schemas]: https://docs.microsoft.com/azure/event-hubs/schema-registry-overview#schemas
[schema_groups]: https://docs.microsoft.com/azure/event-hubs/schema-registry-overview#schema-groups
[schemaregistry_service]: https://aka.ms/schemaregistry
[schemaregistry_avroserializer_pypi]: https://pypi.org/project/azure-schemaregistry-avroserializer/
[token_credential_interface]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/core/azure-core/azure/core/credentials.py
[pypi_azure_identity]: https://pypi.org/project/azure-identity/
[quickstart_guide]: https://docs.microsoft.com/azure/event-hubs/create-schema-registry