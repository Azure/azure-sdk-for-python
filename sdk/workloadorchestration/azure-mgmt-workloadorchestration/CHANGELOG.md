# Release History

## 1.0.0b2 (2026-05-19)

### Features Added

  - Client `WorkloadOrchestrationMgmtClient` added parameter `cloud_setting` in method `__init__`
  - Model `ConfigTemplateProperties` added property `unique_identifier`
  - Model `SolutionTemplateProperties` added property `unique_identifier`
  - Added model `ConfigTemplateUpdate`
  - Added model `ConfigTemplateUpdateProperties`
  - Added model `ContextUpdate`
  - Added model `ContextUpdateProperties`
  - Added model `DiagnosticUpdate`
  - Added model `DiagnosticUpdateProperties`
  - Added model `SchemaUpdate`
  - Added model `SchemaUpdateProperties`
  - Added model `SolutionTemplateUpdate`
  - Added model `SolutionTemplateUpdateProperties`
  - Added model `SolutionUpdate`
  - Added model `SolutionUpdateProperties`
  - Added model `TargetUpdate`
  - Added model `TargetUpdateProperties`
  - Model `SchemaReferencesOperations` added method `begin_create_or_update`
  - Model `SchemaReferencesOperations` added method `begin_delete`

### Breaking Changes

  - Method `DynamicSchemaVersionsOperations.begin_create_or_update` inserted a `positional_or_keyword` parameter `dynamic_schema_version_name`
  - Method `DynamicSchemaVersionsOperations.begin_create_or_update` deleted or renamed its parameter `schema_version_name` of kind `positional_or_keyword`
  - Method `DynamicSchemaVersionsOperations.begin_delete` inserted a `positional_or_keyword` parameter `dynamic_schema_version_name`
  - Method `DynamicSchemaVersionsOperations.begin_delete` deleted or renamed its parameter `schema_version_name` of kind `positional_or_keyword`
  - Method `DynamicSchemaVersionsOperations.get` inserted a `positional_or_keyword` parameter `dynamic_schema_version_name`
  - Method `DynamicSchemaVersionsOperations.get` deleted or renamed its parameter `schema_version_name` of kind `positional_or_keyword`
  - Method `DynamicSchemaVersionsOperations.update` inserted a `positional_or_keyword` parameter `dynamic_schema_version_name`
  - Method `DynamicSchemaVersionsOperations.update` deleted or renamed its parameter `schema_version_name` of kind `positional_or_keyword`
  - Method `DynamicSchemaVersionsOperations.get` re-ordered its parameters from `['self', 'resource_group_name', 'schema_name', 'dynamic_schema_name', 'schema_version_name', 'kwargs']` to `['self', 'resource_group_name', 'schema_name', 'dynamic_schema_name', 'dynamic_schema_version_name', 'kwargs']`
  - Method `DynamicSchemaVersionsOperations.begin_create_or_update` re-ordered its parameters from `['self', 'resource_group_name', 'schema_name', 'dynamic_schema_name', 'schema_version_name', 'resource', 'kwargs']` to `['self', 'resource_group_name', 'schema_name', 'dynamic_schema_name', 'dynamic_schema_version_name', 'resource', 'kwargs']`
  - Method `DynamicSchemaVersionsOperations.update` re-ordered its parameters from `['self', 'resource_group_name', 'schema_name', 'dynamic_schema_name', 'schema_version_name', 'properties', 'kwargs']` to `['self', 'resource_group_name', 'schema_name', 'dynamic_schema_name', 'dynamic_schema_version_name', 'properties', 'kwargs']`
  - Method `DynamicSchemaVersionsOperations.begin_delete` re-ordered its parameters from `['self', 'resource_group_name', 'schema_name', 'dynamic_schema_name', 'schema_version_name', 'kwargs']` to `['self', 'resource_group_name', 'schema_name', 'dynamic_schema_name', 'dynamic_schema_version_name', 'kwargs']`

## 1.0.0b1 (2025-08-18)

### Other Changes

  - Initial version
