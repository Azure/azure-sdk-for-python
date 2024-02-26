# Release History

## 1.0.0b8 (Unreleased)

### Features Added
- Connections LIST operation now supports returning data connections via new optional flag: include_data_connections.
- Connections have read-only support for 3 new connection types: gen 2, data lake, and azure blob.

### Breaking Changes

- MAJOR: `~azure.ai.resources.entities.AIResource` entity renamed to `~azure.ai.resources.entities.AIHub`.
  This includes all field names that reference this entity as well. Ex: inputs named `ai_resource_name` renamed to `ai_hub_name`.

### Bugs Fixed
- Connections docstrings now discuss scope field.

### Other Changes

## 1.0.0b7 (2024-02-07)

### Other Changes

- Bug fixes

## 1.0.0b6 (2024-02-06)

### Other Changes

- Bug fixes

## 1.0.0b5 (2024-02-01)

### Other Changes

- Duplicate cleanup

## 1.0.0b4 (2024-02-01)

### Other Changes

- Use openai v1 environment variable

## 1.0.0b3 (2024-01-30)

### Features Added

- AzureOpenAIConnection.set_current_environment supports openai 1.0 and above.

### Other Changes

- Support for Python 3.12

## 1.0.0b2 (2023-11-30)

### Other Changes

- Dependency improvements.

## 1.0.0b1 (2023-11-10)

### Features Added

- First preview.
