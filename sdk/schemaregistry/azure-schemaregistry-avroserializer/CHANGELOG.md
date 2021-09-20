# Release History

## 1.0.0b3 (Unreleased)

### Features Added

- `auto_register_schemas` keyword argument has been added to `SchemaRegistryAvroSerializer`, which will allow for automatically registering schemas passed in to the `serialize`.

### Breaking Changes

- `schema_registry` parameter in the `SchemaRegistryAvroSerializer` constructor has been renamed `client`.
- `schema_group` parameter in the `SchemaRegistryAvroSerializer` constructor has been renamed `group_name`.
- `data` parameter in the `serialize` and `deserialize` methods on `SchemaRegistryAvroSerializer` has been renamed `value`.
- `schema` parameter in the `serialize` method on `SchemaRegistryAvroSerializer` no longer accepts argument of type `bytes`.
- `SchemaRegistryAvroSerializer` constructor no longer takes in the `codec` keyword argument.
- The following positional arguments are now required keyword arguments:
  - `client` and `group_name` in `SchemaRegistryAvroSerializer` constructor
  - `schema` in `serialize` on `SchemaRegistryAvroSerializer` 

### Bugs Fixed

- `value` parameter in `serialize` on `SchemaRegistryAvroSerializer` takes type `Mapping` rather than `Dict`.

### Other Changes

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
