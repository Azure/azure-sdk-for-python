# Release History

## 1.1.0b2 (2025-08-17)

### Features Added

  - Model `Configuration` added property `system_data`
  - Model `Dashboard` added property `system_data`
  - Model `MarkdownPartMetadataSettingsContent` added property `content`
  - Model `MarkdownPartMetadataSettingsContent` added property `title`
  - Model `MarkdownPartMetadataSettingsContent` added property `subtitle`
  - Model `MarkdownPartMetadataSettingsContent` added property `markdown_source`
  - Model `MarkdownPartMetadataSettingsContent` added property `markdown_uri`
  - Model `PatchableDashboard` added property `properties`
  - Model `ProxyResource` added property `system_data`
  - Model `Resource` added property `system_data`
  - Added enum `ActionType`
  - Added model `ConfigurationListResult`
  - Added enum `CreatedByType`
  - Added enum `DashboardPartMetadataType`
  - Added model `DashboardPropertiesWithProvisioningState`
  - Added model `ErrorAdditionalInfo`
  - Added model `ErrorDetail`
  - Added model `Operation`
  - Added model `OperationDisplay`
  - Added model `OperationListResult`
  - Added enum `Origin`
  - Added enum `ResourceProvisioningState`
  - Added model `SystemData`
  - Added model `TrackedResource`

### Breaking Changes

  - Method `DashboardListResult.__init__` removed default value `None` from its parameter `value`
  - Model `MarkdownPartMetadataSettingsContent` deleted or renamed its instance variable `settings`
  - Model `PatchableDashboard` deleted or renamed its instance variable `lenses`
  - Model `PatchableDashboard` deleted or renamed its instance variable `metadata`
  - Method `ViolationsList.__init__` removed default value `None` from its parameter `value`
  - Deleted or renamed model `ConfigurationList`
  - Deleted or renamed model `ConfigurationName`
  - Deleted or renamed model `ErrorDefinition`
  - Deleted or renamed model `MarkdownPartMetadataSettingsContentSettings`
  - Deleted or renamed model `ResourceProviderOperation`
  - Deleted or renamed model `ResourceProviderOperationDisplay`
  - Deleted or renamed model `ResourceProviderOperationList`
  - Method `DashboardsOperations.create_or_update` inserted a `positional_or_keyword` parameter `resource`
  - Method `DashboardsOperations.create_or_update` deleted or renamed its parameter `dashboard` of kind `positional_or_keyword`
  - Method `DashboardsOperations.update` inserted a `positional_or_keyword` parameter `properties`
  - Method `DashboardsOperations.update` deleted or renamed its parameter `dashboard` of kind `positional_or_keyword`
  - Method `TenantConfigurationsOperations.create` inserted a `positional_or_keyword` parameter `resource`
  - Method `TenantConfigurationsOperations.create` deleted or renamed its parameter `tenant_configuration` of kind `positional_or_keyword`
  - Method `TenantConfigurationsOperations.create` re-ordered its parameters from `['self', 'configuration_name', 'tenant_configuration', 'kwargs']` to `['self', 'configuration_name', 'resource', 'kwargs']`
  - Method `DashboardsOperations.create_or_update` re-ordered its parameters from `['self', 'resource_group_name', 'dashboard_name', 'dashboard', 'kwargs']` to `['self', 'resource_group_name', 'dashboard_name', 'resource', 'kwargs']`
  - Method `DashboardsOperations.update` re-ordered its parameters from `['self', 'resource_group_name', 'dashboard_name', 'dashboard', 'kwargs']` to `['self', 'resource_group_name', 'dashboard_name', 'properties', 'kwargs']`

## 1.1.0b1 (2022-11-01)

### Other Changes

  - Added generated samples in github repo
  - Drop support for python<3.7.0

## 1.0.0 (2021-05-21)

**Features**

  - Model MarkdownPartMetadata has a new parameter additional_properties
  - Model DashboardPartMetadata has a new parameter additional_properties

## 1.0.0b1 (2020-12-17)

* Initial Release
