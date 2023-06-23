# Release History

## 1.0.0b1 (Unreleased)

Version 1.0.0b1 is the first preview of our efforts to create a user-friendly and Pythonic client library for Azure Schema Registry JSON Encoder.

### Features Added

- `JsonSchemaEncoder` is the top-level client class that provides the functionality to encode and decode JSON data utilizing the JSON library. It will automatically register schema and retrieve schema from Azure Schema Registry Service. It provides two methods:
  - `encode`: Encode dict content into bytes and add content to message type object to be returned, along with schema ID of provided schema. Optionally, validates content against schema using provided callable.
  - `deserialize`: Deserialize bytes content into dict content. Optionally, validates content against schema using provided callable.

### Other Changes

- The `encode` and `decode` methods on `JsonSchemaEncoder` support the following message models:
  - `azure.eventhub.EventData` in `azure-eventhub>=5.9.0`
