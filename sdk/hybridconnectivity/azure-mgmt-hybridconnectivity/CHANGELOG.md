# Release History

## 2.0.0 (2024-11-15)

### Features Added

  - Client `HybridConnectivityMgmtClient` added method `send_request`
  - Client `HybridConnectivityMgmtClient` added operation group `generate_aws_template`
  - Client `HybridConnectivityMgmtClient` added operation group `public_cloud_connectors`
  - Client `HybridConnectivityMgmtClient` added operation group `solution_configurations`
  - Client `HybridConnectivityMgmtClient` added operation group `inventory`
  - Client `HybridConnectivityMgmtClient` added operation group `solution_types`
  - Model `ErrorAdditionalInfo` added method `info`
  - Model `ErrorAdditionalInfo` added method `type`
  - Model `ErrorDetail` added method `additional_info`
  - Model `ErrorDetail` added method `code`
  - Model `ErrorDetail` added method `details`
  - Model `ErrorDetail` added method `message`
  - Model `ErrorDetail` added method `target`
  - Model `ErrorResponse` added method `error`
  - Model `ProxyResource` added method `id`
  - Model `ProxyResource` added method `name`
  - Model `ProxyResource` added method `system_data`
  - Model `ProxyResource` added method `type`
  - Model `Resource` added method `id`
  - Model `Resource` added method `name`
  - Model `Resource` added method `system_data`
  - Model `Resource` added method `type`
  - Model `SystemData` added method `created_at`
  - Model `SystemData` added method `created_by`
  - Model `SystemData` added method `created_by_type`
  - Model `SystemData` added method `last_modified_at`
  - Model `SystemData` added method `last_modified_by`
  - Model `SystemData` added method `last_modified_by_type`
  - Added model `AwsCloudProfile`
  - Added enum `CloudNativeType`
  - Added model `ExtensionResource`
  - Added model `GenerateAwsTemplateRequest`
  - Added enum `HostType`
  - Added model `InventoryProperties`
  - Added model `InventoryResource`
  - Added model `OperationStatusResult`
  - Added model `PublicCloudConnector`
  - Added model `PublicCloudConnectorProperties`
  - Added enum `ResourceProvisioningState`
  - Added model `SolutionConfiguration`
  - Added model `SolutionConfigurationProperties`
  - Added enum `SolutionConfigurationStatus`
  - Added model `SolutionSettings`
  - Added model `SolutionTypeProperties`
  - Added model `SolutionTypeResource`
  - Added model `SolutionTypeSettings`
  - Added model `SolutionTypeSettingsProperties`
  - Added model `TrackedResource`
    
### Breaking Changes

  - Deleted or renamed client operation group `HybridConnectivityMgmtClient.operations`
  - Deleted or renamed client operation group `HybridConnectivityMgmtClient.endpoints`
  - Deleted or renamed client operation group `HybridConnectivityMgmtClient.service_configurations`
  - Method `HybridConnectivityMgmtClient.__init__` inserted a `positional_or_keyword` parameter `subscription_id`
  - Model `ErrorAdditionalInfo` deleted or renamed its instance variable `additional_properties`
  - Model `ErrorDetail` deleted or renamed its instance variable `additional_properties`
  - Model `ErrorResponse` deleted or renamed its instance variable `additional_properties`
  - Model `ProxyResource` deleted or renamed its instance variable `additional_properties`
  - Model `Resource` deleted or renamed its instance variable `additional_properties`
  - Model `SystemData` deleted or renamed its instance variable `additional_properties`
  - Deleted or renamed model `ActionType`
  - Deleted or renamed model `EndpointAccessResource`
  - Deleted or renamed model `EndpointProperties`
  - Deleted or renamed model `EndpointResource`
  - Deleted or renamed model `EndpointsList`
  - Deleted or renamed model `IngressGatewayResource`
  - Deleted or renamed model `ListCredentialsRequest`
  - Deleted or renamed model `ListIngressGatewayCredentialsRequest`
  - Deleted or renamed model `ManagedProxyRequest`
  - Deleted or renamed model `ManagedProxyResource`
  - Deleted or renamed model `Operation`
  - Deleted or renamed model `OperationDisplay`
  - Deleted or renamed model `Origin`
  - Deleted or renamed model `ProvisioningState`
  - Deleted or renamed model `ServiceConfigurationList`
  - Deleted or renamed model `ServiceConfigurationResource`
  - Deleted or renamed model `ServiceConfigurationResourcePatch`
  - Deleted or renamed model `ServiceName`
  - Deleted or renamed model `Type`
  - Deleted or renamed operation group `EndpointsOperations`
  - Deleted or renamed operation group `Operations`
  - Deleted or renamed operation group `ServiceConfigurationsOperations`

## 1.0.0 (2023-09-20)

### Other Changes

  - First GA

## 1.0.0b1 (2023-09-20)

* Initial Release
