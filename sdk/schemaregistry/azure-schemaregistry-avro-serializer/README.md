# Azure Schema Registry Avro Serializer library for Python

Azure Schema Registry Avro Serializer provides the ability to serialize and deserialize data according
to the given avro schema. It would automatically register, get and cache the schema.

## Getting started

### Install the package

Install the Azure Service Bus client library for Python with [pip][pip]:

```Bash
pip install azure-schemaregistry-avro-serializer
```

### Prerequisites: 
To use this package, you must have:
* Azure subscription - [Create a free account][azure_sub]
* Azure Schema Registry
* Python 2.7, 3.5 or later - [Install Python][python]

### Authenticate the client
Interaction with Schema Registry Avro Serializer starts with an instance of SchemaRegistryAvroSerializer class. You need the endpoint, AAD credential and schema group name to instantiate the client object. 

**Create client using the azure-identity library:**

```python
from azure.schemaregistry.serializer.avro_serializer import SchemaRegistryAvroSerializer
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()
endpoint = '<< ENDPOINT OF THE SCHEMA REGISTRY >>'
schema_group = '<< GROUP NAME OF THE SCHEMA >>'
schema_registry_client = SchemaRegistryAvroSerializer(endpoint, credential, schema_group)
```

## Key concepts

- Avro: Apache Avro™ is a data serialization system.

## Examples

The following sections provide several code snippets covering some of the most common Schema Registry tasks, including:

- [Serialization](serialization)
- [Deserialization](deserialization)

### Serialization

```python
import os
from azure.schemaregistry.serializer.avro_serializer import SchemaRegistryAvroSerializer
from azure.identity import DefaultAzureCredential

token_credential = DefaultAzureCredential()
endpoint = os.environ['SCHEMA_REGISTRY_ENDPOINT']
schema_group = "<your-group-name>"

serializer = SchemaRegistryAvroSerializer(endpoint, token_credential, schema_group)

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
from azure.schemaregistry.serializer.avro_serializer import SchemaRegistryAvroSerializer
from azure.identity import DefaultAzureCredential

token_credential = DefaultAzureCredential()
endpoint = os.environ['SCHEMA_REGISTRY_ENDPOINT']
schema_group = "<your-group-name>"

serializer = SchemaRegistryAvroSerializer(endpoint, token_credential, schema_group)

with serializer:
    encoded_bytes = b'<data_encoded_by_azure_schema_registry_avro_serializer>'
    decoded_data = serializer.deserialize(encoded_bytes)
```

## Troubleshooting

Azure Schema Registry Avro Serializer raise exceptions defined in [Azure Core][azure_core].

## Next steps

### More sample code

Please find further examples in the [samples](./samples) directory demonstrating common Azure Schema Registry Avro Serializer scenarios.

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
