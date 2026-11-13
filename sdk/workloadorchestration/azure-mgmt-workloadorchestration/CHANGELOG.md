# Release History

## 1.0.0b2 (2026-09-15)

### Features Added

  - Client `WorkloadOrchestrationMgmtClient` added parameter `cloud_setting` in method `__init__`
  - Client `WorkloadOrchestrationMgmtClient` added operation group `config_template_metadatas`
  - Client `WorkloadOrchestrationMgmtClient` added operation group `config_template_schemas`
  - Client `WorkloadOrchestrationMgmtClient` added operation group `hierarchy_configuration_metadata_versions`
  - Client `WorkloadOrchestrationMgmtClient` added operation group `hierarchy_configuration_metadatas`
  - Client `WorkloadOrchestrationMgmtClient` added operation group `solution_deployments`
  - Client `WorkloadOrchestrationMgmtClient` added operation group `solution_metadata_versions`
  - Client `WorkloadOrchestrationMgmtClient` added operation group `solution_metadatas`
  - Client `WorkloadOrchestrationMgmtClient` added operation group `solution_schemas`
  - Model `BulkPublishSolutionParameter` added property `solution_configuration`
  - Model `BulkPublishTargetDetails` added property `solution_configuration`
  - Model `BulkPublishTargetDetails` added property `solution_dependencies`
  - Model `BulkPublishTargetDetails` added property `solution_version_id`
  - Model `ConfigTemplateProperties` added property `unique_identifier`
  - Model `ContextProperties` added property `unique_identifier`
  - Model `DynamicSchemaProperties` added property `display_name`
  - Model `JobProperties` added property `additional_data`
  - Enum `JobType` added member `PUBLISH`
  - Enum `JobType` added member `UNINSTALL`
  - Model `SolutionProperties` added property `display_name`
  - Model `SolutionTemplateProperties` added property `unique_identifier`
  - Model `SolutionTemplateVersionProperties` added property `internal_state`
  - Model `SolutionVersionProperties` added property `current_stage`
  - Model `SolutionVersionProperties` added property `latest_action_triggered_by`
  - Model `SolutionVersionProperties` added property `stages`
  - Enum `State` added member `NOT_APPLICABLE`
  - Added model `AdditionalData`
  - Added model `BulkReviewSolutionParameter`
  - Added model `BulkReviewTargetDetails`
  - Added enum `CMStages`
  - Added enum `ConfigTemplateConfigurationState`
  - Added model `ConfigTemplateMetadata`
  - Added model `ConfigTemplateMetadataProperties`
  - Added model `ConfigTemplateMetadataUpdate`
  - Added model `ConfigTemplateMetadataUpdateProperties`
  - Added model `ConfigTemplateSchema`
  - Added model `ConfigTemplateSchemaProperties`
  - Added model `ConfigTemplateUpdate`
  - Added model `ConfigTemplateUpdateProperties`
  - Added enum `ConfigurationState`
  - Added model `ContextUpdate`
  - Added model `ContextUpdateProperties`
  - Added model `DiagnosticUpdate`
  - Added model `DiagnosticUpdateProperties`
  - Added model `HierarchyConfigurationMetadata`
  - Added model `HierarchyConfigurationMetadataProperties`
  - Added model `HierarchyConfigurationMetadataVersion`
  - Added model `HierarchyConfigurationMetadataVersionProperties`
  - Added model `HierarchyMetadata`
  - Added model `HierarchySelector`
  - Added enum `InternalState`
  - Added model `PublishJobParameter`
  - Added model `PublishJobStepStatistics`
  - Added model `SchemaUpdate`
  - Added model `SchemaUpdateProperties`
  - Added model `SolutionDeployment`
  - Added model `SolutionDeploymentProperties`
  - Added model `SolutionDeploymentUpdate`
  - Added model `SolutionDeploymentUpdateProperties`
  - Added model `SolutionMetadata`
  - Added model `SolutionMetadataProperties`
  - Added model `SolutionMetadataVersion`
  - Added model `SolutionMetadataVersionProperties`
  - Added model `SolutionSchema`
  - Added model `SolutionSchemaProperties`
  - Added model `SolutionTemplateMetadata`
  - Added model `SolutionTemplateMetadataUpdate`
  - Added model `SolutionTemplateUpdate`
  - Added model `SolutionTemplateUpdateProperties`
  - Added model `SolutionUpdate`
  - Added model `SolutionUpdateProperties`
  - Added model `StageMap`
  - Added enum `StateCategory`
  - Added model `TargetMetadata`
  - Added model `TargetUpdate`
  - Added model `TargetUpdateProperties`
  - Added model `UninstallJobParameter`
  - Added model `UninstallJobStepStatistics`
  - Model `ConfigTemplateVersionsOperations` added method `begin_create_or_update`
  - Model `ConfigTemplateVersionsOperations` added method `begin_delete`
  - Model `ConfigTemplatesOperations` added method `begin_link_to_hierarchies`
  - Model `ConfigTemplatesOperations` added method `begin_un_link_from_hierarchies`
  - Model `SchemaReferencesOperations` added method `begin_create_or_update`
  - Model `SchemaReferencesOperations` added method `begin_delete`
  - Model `SolutionTemplateVersionsOperations` added method `begin_bulk_review_solution`
  - Model `SolutionTemplateVersionsOperations` added method `begin_create_or_update`
  - Model `SolutionTemplateVersionsOperations` added method `begin_delete`
  - Model `TargetsOperations` added method `begin_unstage_solution_version`
  - Added operation group `ConfigTemplateMetadatasOperations`
  - Added operation group `ConfigTemplateSchemasOperations`
  - Added operation group `HierarchyConfigurationMetadataVersionsOperations`
  - Added operation group `HierarchyConfigurationMetadatasOperations`
  - Added operation group `SolutionDeploymentsOperations`
  - Added operation group `SolutionMetadataVersionsOperations`
  - Added operation group `SolutionMetadatasOperations`
  - Added operation group `SolutionSchemasOperations`

### Breaking Changes

  - Method `ConfigTemplatesOperations.update` changed type of its parameter `properties` from `ConfigTemplate` to `ConfigTemplateUpdate`
  - Method `ContextsOperations.begin_update` changed type of its parameter `properties` from `Context` to `ContextUpdate`
  - Method `DiagnosticsOperations.begin_update` changed type of its parameter `properties` from `Diagnostic` to `DiagnosticUpdate`
  - Method `SchemasOperations.update` changed type of its parameter `properties` from `Schema` to `SchemaUpdate`
  - Method `SolutionTemplatesOperations.update` changed type of its parameter `properties` from `SolutionTemplate` to `SolutionTemplateUpdate`
  - Method `SolutionsOperations.begin_update` changed type of its parameter `properties` from `Solution` to `SolutionUpdate`
  - Method `TargetsOperations.begin_update` changed type of its parameter `properties` from `Target` to `TargetUpdate`
  - Method `DynamicSchemaVersionsOperations.begin_create_or_update`/`DynamicSchemaVersionsOperations.begin_delete`/`DynamicSchemaVersionsOperations.get`/`DynamicSchemaVersionsOperations.update` renamed their parameter `schema_version_name` to `dynamic_schema_version_name`

## 1.0.0b1 (2025-08-18)

### Other Changes

  - Initial version
