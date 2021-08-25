# Release History

## 1.0.0b3 (Unreleased)

### Features Added

### Breaking Changes

### Bugs Fixed

### Other Changes

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
