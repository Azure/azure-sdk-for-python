# Release History

## 1.0.0 (Unreleased)

**Note:** This is the first stable release of our efforts to create a user-friendly and Pythonic client library for Azure Schema Registry.

### Features Added

- `SchemaRegistryClient` is the top-level client class interacting with the Azure Schema Registry Service. It provides three methods:
  - `register_schema`: Store schema in the service by providing schema group name, schema name, schema format and schema definition.
  - `get_schema`: Get schema definition and its properties by schema id.
  - `get_schema_properties`: Get schema properties by providing schema group name, schema name, schema format and schema definition.
- `SchemaProperties` has the following instance variables: `id`, `format`, `version`.
- `Schema` has the following properties: `properties` and `schema_definition`.
- `SchemaFormat` provides the schema format to be stored by the service. Currently, the only supported format is `Avro`.
- `api_version` has been added as a keyword arg to the sync and async `SchemaRegistryClient` constructors:
  - currently defaults to and only accepts the string `"2021-10"`

### Breaking Changes

- `version` instance variable in `SchemaProperties` has been removed.  
- `schema_definition` instance variable in `Schema` has been renamed `definition`.
- `id` parameter in `get_schema` method on sync and async `SchemaRegistryClient` has been renamed `schema_id`.
- `name` parameter in `register_schema` and `get_schema_properties` methods on sync and async `SchemaRegistryClient` has been renamed `schema_name`.

### Bugs Fixed

### Other Changes

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
