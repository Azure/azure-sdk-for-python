# Release History

## 1.0.0b2 (Unreleased)


## 1.0.0b1 (2020-09-09)

Version 1.0.0b1 is the first preview of our efforts to create a user-friendly and Pythonic client library for Azure Schema Registry.

**New features**

- `SchemaRegistryClient` is the top-level client class interacting with the Azure Schema Registry Service. It provides three methods:
  - `register_schema`: Store schema into the service.
  - `get_schema`: Get schema content and its properties by schema id.
  - `get_schema_id`: Get schema id and its properties by schema group, schema name, serialization type and schema content.
