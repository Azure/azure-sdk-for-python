# Release History

## 1.0.0b4.post1 (2023-08-15)

This package is no longer being maintained. Use the [azure-schemaregistry-avroencoder](https://pypi.org/project/azure-schemaregistry-avroencoder/) package instead.

For migration instructions, see the [migration guide](https://aka.ms/azsdk/python/migrate/sr-avroserializer-to-avroencoder).

## 1.0.0b4 (2021-11-11)

### Features Added

- Async version of `AvroSerializer` has been added under `azure.schemaregistry.serializer.avroserializer.aio`.
- Depends on `azure-schemaregistry>=1.0.0,<2.0.0`.

### Breaking Changes

- `SchemaParseError`, `SchemaSerializationError`, and `SchemaDeserializationError` have been introduced under `azure.schemaregistry.serializer.avroserializer.exceptions` and will be raised for corresponding operations.
  - `SchemaParseError` and `SchemaSerializationError` may be raised for errors when calling `serialize` on `AvroSerializer`.
  - `SchemaParseError` and `SchemaDeserializationError` may be raised for errors when calling `deserialize` on `AvroSerializer`.

## 1.0.0b3 (2021-10-06)

### Features Added

- `auto_register_schemas` keyword argument has been added to `AvroSerializer`, which will allow for automatically registering schemas passed in to the `serialize`, when set to `True`, otherwise `False` by default.
- `value` parameter in `serialize` on `AvroSerializer` takes type `Mapping` rather than `Dict`.
- Depends on `azure-schemaregistry==1.0.0b3`.

### Breaking Changes

- `SchemaRegistryAvroSerializer` has been renamed `AvroSerializer`.
- `schema_registry` parameter in the `AvroSerializer` constructor has been renamed `client`.
- `schema_group` parameter in the `AvroSerializer` constructor has been renamed `group_name`.
- `data` parameter in the `serialize` and `deserialize` methods on `AvroSerializer` has been renamed `value`.
- `schema` parameter in the `serialize` method on `AvroSerializer` no longer accepts argument of type `bytes`.
- `AvroSerializer` constructor no longer takes in the `codec` keyword argument.
- The following positional arguments are now required keyword arguments:
  - `client` and `group_name` in `AvroSerializer` constructor
  - `schema` in `serialize` on `AvroSerializer`

## 1.0.0b2 (2021-08-18)

This version and all future versions will require Python 2.7 or Python 3.6+, Python 3.5 is no longer supported.

### Features Added

- Depends on `azure-schemaregistry==1.0.0b2` which supports client-level caching.

## 1.0.0b1 (2020-09-09)

Version 1.0.0b1 is the first preview of our efforts to create a user-friendly and Pythonic client library for Azure Schema Registry Avro Serializer.

**New features**

- `SchemaRegistryAvroSerializer` is the top-level client class that provides the functionality to encode and decode avro data utilizing the avro library. It will automatically register schema and retrieve schema from Azure Schema Registry Service. It provides two methods:
  - `serialize`: Serialize dict data into bytes according to the given schema and register schema if needed.
  - `deserialize`: Deserialize bytes data into dict data by automatically retrieving schema from the service.
