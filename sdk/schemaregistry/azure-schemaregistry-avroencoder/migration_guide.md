# Guide for migrating to azure-schemaregistry-avroencoder v1.0.x from azure-schemaregistry-avroserializer v1.0.0b4

This guide is intended to assist in the migration to azure-schemaregistry-avroencoder v1.0.x from azure-schemaregistry-avroserializer v1.0.0b4.

It will focus on side-by-side comparisons for similar operations between the two packages.

Familiarity with the `azure-schemaregistry-avroserializer` v1.0.0b4 package is assumed.
For those new to the Schema Registry Avro Encoder library for Python, please refer to the [README for `azure-schemaregistry-avroencoder`](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/schemaregistry/azure-schemaregistry-avroencoder/README.md) rather than this guide.

## Table of contents

* [Migration benefits](#migration-benefits)
  * [New Features](#new-features)
* [Important changes](#important-changes)
  * [The AvroEncoder](#the-avroencoder)
    * [Encode](#encode)
    * [Decode](#decode)
  * [Content type](#content-type)
    * [Backward Compatibility](#backward-compatibility)
  * [MessageType models](#messagetype-models)
    * [Encoding with EventData](#encoding-with-eventdata)
    * [Decoding with EventData](#decoding-with-eventdata)
* [Additional samples](#additional-samples)

## Migration benefits

A natural question to ask when considering whether or not to adopt a new version or library is what
the benefits of doing so would be. As Azure has matured and been embraced by a more diverse group of developers,
we have been focused on learning the patterns and practices to best support developer productivity and
to understand the gaps that the Python client libraries have.

There were several areas of consistent feedback expressed across the Azure client library ecosystem.
One of the most important is that the client libraries for different Azure services have not had a
consistent approach to organization, naming, and API structure. Additionally, many developers have felt
that the learning curve was difficult, and the APIs did not offer a good, approachable,
and consistent onboarding story for those learning Azure or exploring a specific Azure service.

To try and improve the development experience across Azure services,
a set of uniform [design guidelines](https://azure.github.io/azure-sdk/general_introduction.html) was created
for all languages to drive a consistent experience with established API patterns for all services.
A set of [Python-specific guidelines](https://azure.github.io/azure-sdk/python/guidelines/index.html) was also introduced to ensure
that Python clients have a natural and idiomatic feel with respect to the Python ecosystem.
Further details are available in the guidelines for those interested.

### New Features

We have a variety of new features in the version v1.0.x of the Schema Registry Avro Encoder library.

- `AvroEncoder` sync and async classes provide the functionality to encode and decode content which follows a schema with the RecordSchema format, as defined by the Apache Avro specification. The Apache Avro library is used as the implementation for encoding and decoding.
- Refer to the [CHANGELOG.md](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/schemaregistry/azure-schemaregistry-avroencoder/CHANGELOG.md) for more new features, changes, and bug fixes.

## Important changes

### The AvroEncoder

The `AvroEncoder` has been renamed from the `AvroSerializer` and has the following methods:

* `encode`, which replaces `serialize`
* `decode`, which replaces `deserialize`

#### Encode

The positional parameter `value` has been renamed to `content`. If `value` parameter name was specified when calling `serialize`, it must be updated to `content`.

Using the `AvroSerializer`:

```python
with serializer:
    dict_data_ben = {"name": "Ben", "favorite_number": 7, "favorite_color": "red"}
    payload_ben = serializer.serialize(value=dict_data_ben, schema=SCHEMA_STRING)
    print(payload_ben)  # prints bytes b'<record format indicator><schema ID><Avro-encoded data>``
```

Using the `AvroEncoder`:

```python
with encoder:
    dict_content = {"name": "Ben", "favorite_number": 7, "favorite_color": "red"}
    message_content_ben = encoder.encode(content=dict_content, schema=SCHEMA_STRING)
    print(message_content_ben)  # prints {"content": <Avro-encoded content>, "content_type": "<Avro MIME type>+<Schema ID>"}
```

#### Decode

The positional parameter `value` has been renamed to `content`. If `value` parameter name was specified when calling `deserialize`, it must be updated to `content`.

Using the `AvroSerializer`:

```python
with serializer:
    decoded_value = serializer.deserialize(value=encoded_payload)
```

Using the `AvroEncoder`:

```python
with encoder:
    decoded_content = encoder.decode(content=encoded_content)
```

### Content type

Previously, `encode` returned an Avro-encoded content, with the binary encoded schema ID and record format indicator values prepended to it. Now, `encode` will return a TypedDict of {`content`: `<serialized payload>`, `content_type`: `<Avro MIME type>`+`<schema ID>`} by default.

#### Backward compatibility

In order to decode content that was encoded (or "serialized") by the `AvroSerializer`, use `azure-schemaregistry-avroencoder` v1.0.0b2.
> Note: This backward compatibility was removed starting `azure-schemaregistry-avroencoder` v1.0.0b3.

1. Install `azure-schemaregistry-avroencoder` v1.0.0b2, which automatically detects the preamble.

```pwsh
pip install azure-schemaregistry-avroencoder==1.0.0b2
```

2. Receive and decode events from Event Hubs that were "serialized" by the `AvroSerializer`.

```python
import os
from azure.eventhub import EventHubConsumerClient
from azure.schemaregistry import SchemaRegistryClient
from azure.schemaregistry.encoder.avroencoder import AvroEncoder
from azure.identity import DefaultAzureCredential

token_credential = DefaultAzureCredential()
fully_qualified_namespace = os.environ['SCHEMAREGISTRY_FULLY_QUALIFIED_NAMESPACE']
group_name = os.environ['SCHEMAREGISTRY_GROUP']
eventhub_connection_str = os.environ['EVENT_HUB_CONN_STR']
eventhub_name = os.environ['EVENT_HUB_NAME']

schema_registry_client = SchemaRegistryClient(fully_qualified_namespace, token_credential)
avro_encoder = AvroEncoder(client=schema_registry_client, group_name=group_name)

eventhub_consumer = EventHubConsumerClient.from_connection_string(
    conn_str=eventhub_connection_str,
    consumer_group='$Default',
    eventhub_name=eventhub_name,
)

def on_event(partition_context, event):
    decoded_content = avro_encoder.decode(event)

with eventhub_consumer, avro_encoder:
    eventhub_consumer.receive(on_event=on_event, starting_position="-1")
```

### MessageType models

In order to integrate more easily with messaging libraries, a `MessageType` protocol has been added. It specifies the methods that need to be supported by message models so that the `AvroEncoder` can automatically set/get Avro-encoded content and respective content type on the message.

Message models that currently support the `MessageType` protocol are:

* `azure.eventhub.EventData` from `azure-eventhub>=5.9.0`

#### Encoding with EventData

Previously, the Avro-encoded payload would need to be passed in as the `EventData` body.

```python
with serializer:
    dict_data = {"name": "Ben", "favorite_number": 7, "favorite_color": "red"}
    payload_bytes = serializer.serialize(value=dict_data, schema=SCHEMA_STRING)
    event_data = EventData(body=payload_bytes)  # pass the bytes data to the body of an EventData
```

Now, the `EventData` class can be passed in to the `AvroEncoder` to automatically set the Avro-encoded content and content type on the `EventData` object.

```python
with encoder:
    dict_content = {"name": "Ben", "favorite_number": 7, "favorite_color": "red"}
    event_data = encoder.encode(content=dict_content, schema=SCHEMA_STRING, message_type=EventData)

```

#### Decoding with EventData

Previously, the body on the received EventData would need to be manually constructed then passed to the `AvroSerializer` for decoding.

```python
def on_event(partition_context, event):
    bytes_payload = b"".join(b for b in event.body)
    deserialized_data = avro_serializer.deserialize(value=bytes_payload)
```

Now, the `EventData` can be passed directly to the `AvroEncoder` for automatic decoding.

```python
def on_event(partition_context, event):
    decoded_content = avro_encoder.decode(content=event)
```

## Additional samples

More examples can be found at [Samples for azure-schemaregistry-avroencoder](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/schemaregistry/azure-schemaregistry-avroencoder/samples)
