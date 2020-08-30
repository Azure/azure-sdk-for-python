# Azure Schema Registry client library for Python

Azure Schema Registry is a service that provides the ability to store and retrieve different types of schemas such as
Avro, Json, etc.

## Getting started

### Install the package

Install the Azure Service Bus client library for Python with [pip][pip]:

```Bash
pip install azure-schemaregistry
```

### Prerequisites: 
To use this package, you must have:
* Azure subscription - [Create a free account][azure_sub]
* Azure Schema Registry
* Python 2.7, 3.5 or later - [Install Python][python]

## Key concepts

- Schema: Schema is the organization or structure for data.

## Examples

The following sections provide several code snippets covering some of the most common Schema Registry tasks, including:

- [Register a schema](register-a-schema)
- [Get the schema by id](get-the-schema-by-id)
- [Get the id of a schema](get-the-id-of-a-schema)

### Register a schema

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
with schema_registry_client, token_credential:
    schema_properties = schema_registry_client.register_schema(schema_group, schema_name, serilization_type, schema_string)
    schema_id = schema_properties.id
```

### Get the schema by id

```python
import os

from azure.identity import DefaultAzureCredential
from azure.schemaregistry import SchemaRegistryClient

token_credential = DefaultAzureCredential()
endpoint = os.environ['SCHEMA_REGISTRY_ENDPOINT']
schema_id = '<your-schema-id>'

schema_registry_client = SchemaRegistryClient(endpoint=endpoint, credential=token_credential)
with schema_registry_client, token_credential:
    schema = schema_registry_client.get_schema(schema_id)
    schema_content = schema.content
```

### Get the id of a schema

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
with schema_registry_client, token_credential:
    schema_properties = schema_registry_client.get_schema_id(schema_group, schema_name, serialization_type, schema_content)
    schema_id = schema_properties.id
```

## Troubleshooting

### General

Schema Registry clients raise exceptions defined in [Azure Core][azure_core].

### Logging

## Next steps

### More sample code

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

[pip]: https://pypi.org/project/pip/
[python]: https://www.python.org/downloads/
[azure_core]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/core/azure-core/README.md
[azure_sub]: https://azure.microsoft.com/free/