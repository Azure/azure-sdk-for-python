# Release History

## 1.0.1 (Unreleased)

### Features Added

### Breaking Changes

### Bugs Fixed

### Other Changes

## 1.0.0 (2022-05-10)

**Note:** This is the first stable release of our efforts to create a user-friendly Pythonic Avro Encoder library that integrates with the Python client library for Azure Schema Registry.

### Features Added

- `AvroEncoder` sync and async classes provide the functionality to encode and decode content which follows a schema with the RecordSchema format, as defined by the Apache Avro specification. The Apache Avro library is used as the implementation for encoding and decoding.
The encoder will automatically register and retrieve schemas from Azure Schema Registry Service. It provides the following methods:
  - constructor: If `auto_register=True` keyword is passed in, will automatically register schemas passed in to the `encode` method. Otherwise, and by default, will require pre-registering of schemas passed to `encode`. Takes a `group_name` argument that is optional when decoding, but required for encoding.
  - `encode`: Encodes dict content into bytes according to the given schema and registers schema if needed. Returns either a dict of encoded content and corresponding content type or a `MessageType` subtype object, depending on arguments provided.
  - `decode`: Decodes bytes content into dict content by automatically retrieving schema from the service.
- `MessageContent` TypedDict has been introduced with the following required keys:
  - `content`: The bytes content.
  - `content_type`: The string content type, which holds the schema ID and the record format indicator.
- `MessageType` has been introduced with the following methods:
  - `from_message_content`: Class method that creates an object with given bytes content and string content type.
  - `__message_content__`: Returns a `MessageContent` object with content and content type values set to their respective properties on the object.
- Schemas and Schema IDs are cached locally, so that multiple calls with the same schema/schema ID will not trigger multiple service calls.
- The number of hits, misses, and total entries for the schema/schema ID caches will be logged at an info level when a new entry is added.
- `InvalidContentError` has been introduced for errors related to invalid content and content types, where `__cause__` will contain the underlying exception raised by the Avro library.
- `InvalidSchemaError` has been introduced for errors related to invalid schemas, where `__cause__` will contain the underlying exception raised by the Apache Avro library.
- The `encode` and `decode` methods on `AvroEncoder` support the following message models:
  - `azure.eventhub.EventData` in `azure-eventhub>=5.9.0`

### Other Changes

- This package is meant to replace the azure-schemaregistry-avroserializer package, which will no longer be supported.
- `group_name` is now an optional parameter in the sync and async `AvroEncoder` constructors.

## 1.0.0b3 (2022-04-05)

### Breaking Changes

- `auto_register_schemas` keyword in the sync and async `AvroEncoder` constructors has been renamed `auto_register`.
- `SchemaParseError`, `SchemaEncodeError`, and `SchemaDecodeError` have been replaced with `InvalidContentError` and `InvalidSchemaError`. The errors have been added under the `azure.schemaregistry.encoder.avroencoder` namespace.
- The `exceptions` module in `azure.schemaregistry.encoder.avroencoder` has been removed.
- The `encode` method on the sync and async `AvroEncoder` only allows subtypes of the `MessageType` protocol as values to the `message_type` optional parameter, rather than any callable that has the method signature `(content: bytes, content_type: str, **kwargs: Any)`.
- The number of hits/misses, in addition to number of entries, for the schema/schema ID caches will be logged at an info level when a new entry is added.

### Other Changes

- This release and future releases will not have backward compatibility support for decoding data that was encoded with the AvroSerializer.
- The `encode` and `decode` methods on `AvroEncoder` support the following message models:
  - `azure.eventhub.EventData` in `azure-eventhub==5.9.0b3`

## 1.0.0b2 (2022-03-09)

### Features Added

- `request_options` has been added to `encode` and `decode` on `AvroEncoder` as an optional parameter to be passed into client requests.
- The size of the current schema/schema ID caches will be logged at an info level when a new entry has been added.

### Breaking Changes

- `MessageMetadataDict` has been renamed `MessageContent`.
- `data` in `MessageContent` has been renamed `content`.
- The `data` parameter in `encode` and `decode` on the sync and async `AvroEncoder` has been renamed `content`.
- The `from_message_data` method in the `MessageType` protocol has been renamed `from_message_content`. The `data` parameter in `from_message_content` has been renamed `content`.
- The `__message_data__` method in the `MessageType` protocol has been renamed `__message_content__`.

### Other Changes

- This beta release will be backward compatible for decoding data that was encoded with the AvroSerializer.
- The `encode` and `decode` methods on `AvroEncoder` support the following message models:
  - `azure.eventhub.EventData` in `azure-eventhub==5.9.0b2`

## 1.0.0b1 (2022-02-09)

This version and all future versions will require Python 3.6+. Python 2.7 is no longer supported.

### Features Added

- This package is meant to replace the azure-schemaregistry-avroserializer.
- APIs have been updated to allow for encoding directly to and decoding from message type objects, where the data value is the Avro encoded payload.
- The content type of the message will hold the schema ID and record format indicator.

### Other Changes

- This beta release will be backward compatible for decoding data that was encoded with the AvroSerializer.
- The `encode` and `decode` methods on `AvroEncoder` support the following message models:
  - `azure.eventhub.EventData` in `azure-eventhub==5.9.0b1`
