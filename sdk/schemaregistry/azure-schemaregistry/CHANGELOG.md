# Release History

## 1.3.0b4 (Unreleased)

### Features Added

### Breaking Changes

### Bugs Fixed

### Other Changes

## 1.3.0b3 (2023-11-09)

### Features Added

- `V2023_07_01` has been added to `ApiVersion` and set as the default api version.
  - `Protobuf` has been added to supported formats in `SchemaFormat`.

### Other Changes

- Added support for Python 3.12.

## 1.3.0b2 (2023-08-09)

### Features Added

The following features are experimental and may be removed:

- Sync and async `JsonSchemaEncoder` have been added under `azure.schemaregistry.encoder.jsonencoder`.
- `InvalidContentError` and `JsonSchemaDraftIdentifier` have been added under `azure.schemaregistry.encoder.jsonencoder` for use with the `JsonSchemaEncoder`.
- `MessageType`, `MessageContent`, `SchemaContentValidate`, `SchemaEncoder` have been added under `azure.schemaregistry` as protocols to define/for use with the `JsonSchemaEncoder` and future encoder implementations.

## 1.3.0b1 (2023-01-12)

### Features Added

- `V2022_10` has been added to `ApiVersion` and set as the default api version.
  - `Json` and `Custom` have been added to supported formats in `SchemaFormat`.
  - At the time of this release, only Draft 3 of JSON schemas is currently supported by the service.

### Bugs Fixed

- Fixed a bug in sync/async `register_schema` and `get_schema_properties` that did not accept case insensitive strings as an argument to the `format` parameter.

### Other Changes

- Added support for Python 3.11.

## 1.2.0 (2022-10-10)

This version and all future versions will require Python 3.7+, Python 3.6 is no longer supported.

### Features Added

- `group_name`, `name`, and `version` have been added as optional parameters to the `get_schema` method on the sync and async `SchemaRegistryClient`.
- `version` has been added to `SchemaProperties`.

### Other Changes

- Updated azure-core minimum dependency to 1.24.0.
- Added distributed tracing support for sync and async `SchemaRegistryClient`.

## 1.1.0 (2022-05-10)

This version and all future versions will require Python 3.6+. Python 2.7 is no longer supported.

### Features Added

- `group_name` and `name` have been added as instance variables to `SchemaProperties`.

### Other Changes

- Updated azure-core minimum dependency to 1.23.0.

## 1.0.0 (2021-11-10)

**Note:** This is the first stable release of our efforts to create a user-friendly and Pythonic client library for Azure Schema Registry.

### Features Added

- `SchemaRegistryClient` is the top-level client class interacting with the Azure Schema Registry Service. It provides three methods:
  - `register_schema`: Store schema in the service by providing schema group name, schema name, schema definition, and schema format.
  - `get_schema`: Get schema definition and its properties by schema id.
  - `get_schema_properties`: Get schema properties by providing schema group name, schema name, schema definition, and schema format.
- `SchemaProperties` has the following instance variables: `id` and `format`:
  - The type of `format` has been changed from `str` to `SchemaFormat`.
- `Schema` has the following properties: `properties` and `definition`.
- `SchemaFormat` provides the schema format to be stored by the service. Currently, the only supported format is `Avro`.
- `api_version` has been added as a keyword arg to the sync and async `SchemaRegistryClient` constructors.

### Breaking Changes

- `version` instance variable in `SchemaProperties` has been removed.  
- `schema_definition` instance variable in `Schema` has been renamed `definition`.
- `id` parameter in `get_schema` method on sync and async `SchemaRegistryClient` has been renamed `schema_id`.
- `schema_definition` parameter in `register_schema` and `get_schema_properties` methods on sync and async `SchemaRegistryClient` has been renamed `definition`.
- `serializer` namespace has been removed from `azure.schemaregistry`.

## 1.0.0b3 (2021-10-05)

### Breaking Changes

- `get_schema_id` method on sync and async `SchemaRegistryClient` has been renamed `get_schema_properties`.
- `schema_id` parameter in `get_schema` method on sync and async `SchemaRegistryClient` has been renamed `id`.
- `register_schema` and `get_schema_properties` methods on sync and async `SchemaRegistryClient` now take in the following parameters in the given order:
  - `group_name`, which has been renamed from `schema_group`
  - `name`, which has been renamed from `schema_name`
  - `schema_definition`, which has been renamed from `schema_content`
  - `format`, which has been renamed from `serialization_type`
- `endpoint` parameter in `SchemaRegistryClient` constructor has been renamed `fully_qualified_namespace`
- `location` instance variable in `SchemaProperties` has been removed.
- `Schema` and `SchemaProperties` no longer have positional parameters, as they will not be constructed by the user.

### Other Changes

- Updated azure-core dependency to 1.19.0.
- Removed caching support of registered schemas so requests are sent to the service to register schemas, get schema properties, and get schemas.

## 1.0.0b2 (2021-08-17)

This version and all future versions will require Python 2.7 or Python 3.6+, Python 3.5 is no longer supported.

### Features Added

- Support caching of registered schemas and send requests to the service only if the cache does not have the looked-up schema/schema ID.

## 1.0.0b1 (2020-09-09)

Version 1.0.0b1 is the first preview of our efforts to create a user-friendly and Pythonic client library for Azure Schema Registry.

**New features**

- `SchemaRegistryClient` is the top-level client class interacting with the Azure Schema Registry Service. It provides three methods:
  - `register_schema`: Store schema into the service.
  - `get_schema`: Get schema content and its properties by schema id.
  - `get_schema_id`: Get schema id and its properties by schema group, schema name, serialization type and schema content.
