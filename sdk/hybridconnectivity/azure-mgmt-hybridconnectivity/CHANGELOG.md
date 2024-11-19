# Release History

## 2.0.0 (2024-11-18)

### Features Added

  - Client `HybridConnectivityMgmtClient` added operation group `solution_configurations`
  - Client `HybridConnectivityMgmtClient` added operation group `inventory`
  - Client `HybridConnectivityMgmtClient` added operation group `generate_aws_template`
  - Client `HybridConnectivityMgmtClient` added operation group `public_cloud_connectors`
  - Client `HybridConnectivityMgmtClient` added operation group `solution_types`
  - Added model `AwsCloudProfile`
  - Added model `AwsCloudProfileUpdate`
  - Added model `AzureResourceManagerCommonTypesTrackedResourceUpdate`
  - Added enum `CloudNativeType`
  - Added model `GenerateAwsTemplateRequest`
  - Added enum `HostType`
  - Added model `InventoryProperties`
  - Added model `InventoryResource`
  - Added model `InventoryResourceListResult`
  - Added model `OperationStatusResult`
  - Added model `PublicCloudConnector`
  - Added model `PublicCloudConnectorListResult`
  - Added model `PublicCloudConnectorProperties`
  - Added model `PublicCloudConnectorPropertiesUpdate`
  - Added model `PublicCloudConnectorUpdate`
  - Added enum `ResourceProvisioningState`
  - Added model `SolutionConfiguration`
  - Added model `SolutionConfigurationListResult`
  - Added model `SolutionConfigurationProperties`
  - Added model `SolutionConfigurationPropertiesUpdate`
  - Added enum `SolutionConfigurationStatus`
  - Added model `SolutionConfigurationUpdate`
  - Added enum `SolutionTypeEnum`
  - Added model `SolutionTypePermissions`
  - Added model `SolutionTypeProperties`
  - Added model `SolutionTypeResource`
  - Added model `SolutionTypeResourceListResult`
  - Added model `SolutionTypeSettings`
  - Added model `SolutionTypeSettingsProperties`
  - Added enum `Status`
  - Added model `TestPermissionResult`
  - Added model `TrackedResource`
  - Added operation group `GenerateAwsTemplateOperations`
  - Added operation group `InventoryOperations`
  - Added operation group `PublicCloudConnectorsOperations`
  - Added operation group `SolutionConfigurationsOperations`
  - Added operation group `SolutionTypesOperations`

### Breaking Changes

  - Method `HybridConnectivityMgmtClient.__init__` inserted a `positional_or_keyword` parameter `subscription_id`

## 1.0.0 (2023-09-20)

### Other Changes

  - First GA

## 1.0.0b1 (2023-09-20)

* Initial Release
