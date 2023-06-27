Link to previous proposal: https://gist.github.com/swathipil/6473a4c9d834e5d9176d66326c6515cc
Link to Jesse's general cross-language proposal: https://gist.github.com/jsquire/c60aa6229c35d9c35ea7784b23462949
Python SR Json Schema Encoder APIView: 

## Contents
- [Motivation](#motivation)
- [Samples](#samples)
  - [Encode and Send to Event Hubs](#encode-and-send-to-event-hubs)
  - [Receive from Event Hubs and Decode](#receive-from-event-hubs-and-decode)
- [API](#api)
- [Updates](#updates)
- [Alternative Names](#alternative-names)
- [Questions](#questions)

### Motivation

Paraphrasing Jesse:
The service teams wants this feature specifically for the Kafka interoperability/compete story for Event Hubs. It is mostly a marketing "checkbox" feature. Additionally, it will provide a consistent developer experience across different schema formats for Schema Registry SDKs (ex. Avro).

### Samples

#### Encode and Send to Event Hubs
```python
import os
import json
from azure.eventhub import EventHubProducerClient, EventData
from azure.identity import DefaultAzureCredential
from azure.schemaregistry import SchemaRegistryClient
from azure.schemaregistry.encoder.jsonencoder import JsonSchemaEncoder

EVENTHUB_CONNECTION_STR = os.environ['EVENT_HUB_CONN_STR']
EVENTHUB_NAME = os.environ['EVENT_HUB_NAME']

SCHEMAREGISTRY_FULLY_QUALIFIED_NAMESPACE = os.environ['SCHEMAREGISTRY_JSON_FULLY_QUALIFIED_NAMESPACE']
GROUP_NAME = os.environ['SCHEMAREGISTRY_GROUP']

SCHEMA_JSON = {
    "$id": "https://example.com/person.schema.json",
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "Person",
    "type": "object",
    "properties": {
        "name": {
            "type": "string",
            "description": "Person's name."
        },
        "favorite_number": {
            "description": "Favorite number.",
            "type": "integer",
        }
    }
}
SCHEMA_STRING = json.dumps(SCHEMA_JSON)

# example user-defined callable for validation
import jsonschema
def validate_with_jsonschema(content: Mapping[str, Any], schema: Mapping[str, Any]) -> None:
  try:
    jsonschema.Draft4Validator(schema).validate(content)
  except:
    raise MyCustomError(...)
    
# example user-defined callable for schema generation
from genson import SchemaBuilder
def generate_schema_with_genson(content: Mapping[str, Any]) -> Mapping[str, Any]:
  builder = SchemaBuilder()
  try:
    builder.add_object(content)
    return builder.to_schema()
  except:
    raise MyCustomError(...)
    
producer = EventHubProducerClient.from_connection_string(
    conn_str=EVENTHUB_CONNECTION_STR,
    eventhub_name=EVENTHUB_NAME
)
encoder = JsonSchemaEncoder(
    client=SchemaRegistryClient(
        fully_qualified_namespace=SCHEMAREGISTRY_FULLY_QUALIFIED_NAMESPACE,
        credential=DefaultAzureCredential()
    ),
    group_name=GROUP_NAME,
    auto_register=True,
    validate=validate_with_jsonschema,
    generate_schema=generate_schema_with_genson,
)

with producer, encoder:
    event_data_batch = producer.create_batch()
    dict_content = {"name": "Bob", "favorite_number": 7}
    
    # if schema is passed in, then `generate_schema` callable will not be used
    event_data = encoder.encode(content=dict_content, schema=SCHEMA_STRING, message_type=EventData)
    
    # if schema is not passed in, then `generate_schema` will be used
    event_data = encoder.encode(content=dict_content, message_type=EventData)
    
    # if neither are passed in, TypeError will be raised
    
    # encode invalid dict content
    event_data = encoder.encode(  # raises `InvalidContentError`
      content={"name": 5, favorite_number: 7},
      schema=SCHEMA_STRING,
      message_type=EventData
    )
        
    event_data_batch.add(event_data)
    producer.send_batch(event_data_batch)
```

#### Receive from Event Hubs and Decode

```python
import os
from azure.eventhub import EventHubConsumerClient
from azure.identity import DefaultAzureCredential
from azure.schemaregistry import SchemaRegistryClient
from azure.schemaregistry.encoder.jsonencoder import JsonSchemaEncoder

EVENTHUB_CONNECTION_STR = os.environ['EVENT_HUB_CONN_STR']
EVENTHUB_NAME = os.environ['EVENT_HUB_NAME']

SCHEMAREGISTRY_FULLY_QUALIFIED_NAMESPACE = os.environ['SCHEMAREGISTRY_JSON_FULLY_QUALIFIED_NAMESPACE']
GROUP_NAME = os.environ['SCHEMAREGISTRY_GROUP']

# example user-defined callable for validation
import jsonschema
def validate_with_jsonschema(content: Mapping[str, Any], schema: Mapping[str, Any]) -> None:
  try:
    jsonschema.Draft4Validator(schema).validate(content)
  except:
    raise MyCustomError(...)

consumer = EventHubConsumerClient.from_connection_string(
    conn_str=EVENTHUB_CONNECTION_STR,
    consumer_group='$Default',
    eventhub_name=EVENTHUB_NAME,
)
encoder = JsonSchemaEncoder(
    client=SchemaRegistryClient(
        fully_qualified_namespace=SCHEMAREGISTRY_FULLY_QUALIFIED_NAMESPACE,
        credential=DefaultAzureCredential()
    ),
    group_name=GROUP_NAME,
    validate=validate_with_jsonschema,
)

def on_event(partition_context, event):
    print(f"Received event from partition: {partition_context.partition_id}.")
    
    # Internally, schema is retrieved from registry using schema ID in event.content_type. (ex. application/json+{schema_id})
    # Validates content in event.body against retrieved schema if it exists. If invalid, raises
    # azure.schemaregistry.encoder.InvalidContentType error.
    decoded_content = json_encoder.decode(event)

with consumer, encoder:
    consumer.receive(
        on_event=on_event,
        starting_position="-1",
    )
```

### API

```python
# previously JsonEncoder
class JsonSchemaEncoder:
    def __init__(
        self,
        *,
        client: "SchemaRegistryClient",
        group_name: Optional[str] = None,
        auto_register: bool = False,
        validate: Optional[Callable[[Mapping[str, Any], Mapping[str, Any]], None]] = None,
        generate_schema: Optional[Callable[[Mapping[str, Any]], Mapping[str, Any]]] = None, # only used when sending
    ) -> None:
    
    def encode(
        self,
        content: Mapping[str, Any],
        *,
        schema: str,
        message_type: Optional[Type[MessageType]] = None,
        request_options: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Union[MessageType, MessageContent]
    
    def decode(
        self,  # pylint: disable=unused-argument
        message: Union[MessageContent, MessageType],
        *,
        request_options: Dict[str, Any] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
```

### Updates
- Removed all external dependencies
- Adding optional parameters in the constructor for:
  - Validating content against schema.
    - **validate(content: Mapping[str, Any], schema: Mapping[str, Any]) -> None**
  - Generating schema from given content.
    - **generate_schema(content: Mapping[str, Any]) -> Mapping[str, Any])**
- Temporary rename to JsonSchemaEncoder until better alternative found

### Alternative Names
- (current) azure.schemaregistry.encoder.JsonSchemaEncoder
  - con: Potentially misleading - sounds like we're serializing the JSON Schema, not the data.
  - pro: Falls under `encoder` namespace.
- azure.schemaregistry.serializer.JsonSerializer
  - con: Similar to JsonEncoder, which is similar built-in library JSONEncoder
  - con: Namespace (azure.schemaregistry.serializer) does not follow `serializer` convention
- azure.schemaregistry.encoder.JsonSchema
  - .NET is considering this.
- ???

### Questions
1) In the `validate` callable docs, (how) should we enforce draft version validation is consistent with the service?