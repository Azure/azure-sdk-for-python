# Release History

## 1.0.0b3 (Unreleased)

### Features Added

### Breaking Changes

- `auto_register_schemas` keyword in the sync and async `AvroEncoder` constructors has been renamed `auto_register`.
- `SchemaParseError`, `SchemaEncodeError`, and `SchemaDecodeError` have been replaced with `AvroEncodeError` and `InvalidSchemaError`. The errors have been added under the `azure.schemaregistry.encoder.avroencoder` namespace.
- The `exceptions` module in `azure.schemaregistry.encoder.avroencoder` has been removed.
- The `encode` method on the sync and async `AvroEncoder` only allows subtypes of the `MessageType` protocol as values to the `message_type` optional parameter, rather than any callable that has the method signature `(content: bytes, content_type: str, **kwargs: Any)`.

### Other Changes

- This release and future releases will not backward compatibility support for decoding data that was encoded with the AvroSerializer.
- The `encode` and `decode` methods on `AvroEncoder` support the following message models:
  - `azure.eventhub.EventData` in `azure-eventhub==5.9.0b2`

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
