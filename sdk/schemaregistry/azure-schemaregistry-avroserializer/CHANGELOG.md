# Release History

## 1.0.0b2 (Unreleased)


## 1.0.0b1 (2020-09-09)

Version 1.0.0b1 is the first preview of our efforts to create a user-friendly and Pythonic client library for Azure Schema Registry Avro Serializer.

**New features**

- `SchemaRegistryAvroSerializer` is the top-level client class that provides the functionality to encode and decode avro data utilizing the avro library. It will automatically register schema and retrieve schema from Azure Schema Registry Service. It provides two methods:
  - `serialize`: Serialize dict data into bytes according to the given schema and register schema if needed.
  - `deserialize`: Deserialize bytes data into dict data by automatically retrieving schema from the service.
