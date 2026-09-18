# Release History

## 1.0.0b2 (2026-08-27)

### Features Added

  - Client `TerraformMgmtClient` added parameter `cloud_setting` in method `__init__`
  - Model `BaseExportModel` added property `exclude_azure_resource`
  - Model `BaseExportModel` added property `exclude_terraform_resource`
  - Model `BaseExportModel` added property `include_extensions`
  - Model `BaseExportModel` added property `include_managed_resource`
  - Model `BaseExportModel` added property `include_role_assignment`
  - Model `ExportQuery` added property `authorization_scope_filter`
  - Model `ExportQuery` added property `exclude_azure_resource`
  - Model `ExportQuery` added property `exclude_terraform_resource`
  - Model `ExportQuery` added property `include_extensions`
  - Model `ExportQuery` added property `include_managed_resource`
  - Model `ExportQuery` added property `include_resource_group`
  - Model `ExportQuery` added property `include_role_assignment`
  - Model `ExportQuery` added property `table`
  - Model `ExportResource` added property `exclude_azure_resource`
  - Model `ExportResource` added property `exclude_terraform_resource`
  - Model `ExportResource` added property `include_extensions`
  - Model `ExportResource` added property `include_managed_resource`
  - Model `ExportResource` added property `include_resource_group`
  - Model `ExportResource` added property `include_role_assignment`
  - Model `ExportResource` added property `recursive`
  - Model `ExportResourceGroup` added property `exclude_azure_resource`
  - Model `ExportResourceGroup` added property `exclude_terraform_resource`
  - Model `ExportResourceGroup` added property `include_extensions`
  - Model `ExportResourceGroup` added property `include_managed_resource`
  - Model `ExportResourceGroup` added property `include_role_assignment`
  - Model `ExportResult` added property `import_property`
  - Model `TerraformOperationStatus` added property `id`
  - Added enum `AuthorizationScopeFilter`
  - Added enum `AzureExtensionResourceType`

## 1.0.0b1 (2024-11-21)

### Other Changes

  - Initial version
