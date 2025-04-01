# Release History

## 2.0.0b1 (2025-04-01)

### Features Added

  - Client `HybridConnectivityMgmtClient` added operation group `generate_aws_template`
  - Client `HybridConnectivityMgmtClient` added operation group `public_cloud_connectors`
  - Client `HybridConnectivityMgmtClient` added operation group `solution_configurations`
  - Client `HybridConnectivityMgmtClient` added operation group `inventory`
  - Client `HybridConnectivityMgmtClient` added operation group `solution_types`
  - Model `ServiceConfigurationResource` added property `properties`
  - Added model `AADProfileProperties`
  - Added model `AwsCloudProfile`
  - Added model `AwsCloudProfileUpdate`
  - Added enum `CloudNativeType`
  - Added model `ExtensionResource`
  - Added model `GenerateAwsTemplateRequest`
  - Added enum `HostType`
  - Added model `IngressProfileProperties`
  - Added model `InventoryProperties`
  - Added model `InventoryResource`
  - Added model `OperationStatusResult`
  - Added model `PublicCloudConnector`
  - Added model `PublicCloudConnectorProperties`
  - Added model `PublicCloudConnectorPropertiesUpdate`
  - Added model `PublicCloudConnectorUpdate`
  - Added model `RelayNamespaceAccessProperties`
  - Added enum `ResourceProvisioningState`
  - Added model `ServiceConfigurationProperties`
  - Added model `ServiceConfigurationPropertiesPatch`
  - Added model `SolutionConfiguration`
  - Added model `SolutionConfigurationProperties`
  - Added model `SolutionConfigurationPropertiesUpdate`
  - Added enum `SolutionConfigurationStatus`
  - Added model `SolutionConfigurationUpdate`
  - Added model `SolutionSettings`
  - Added model `SolutionTypeProperties`
  - Added model `SolutionTypeResource`
  - Added model `SolutionTypeSettings`
  - Added model `SolutionTypeSettingsProperties`
  - Added model `TrackedResource`
  - Added model `TrackedResourceUpdate`
  - Added operation group `GenerateAwsTemplateOperations`
  - Added operation group `InventoryOperations`
  - Added operation group `PublicCloudConnectorsOperations`
  - Added operation group `SolutionConfigurationsOperations`
  - Added operation group `SolutionTypesOperations`

### Breaking Changes

  - Model `EndpointAccessResource` deleted or renamed its instance variable `namespace_name`
  - Model `EndpointAccessResource` deleted or renamed its instance variable `namespace_name_suffix`
  - Model `EndpointAccessResource` deleted or renamed its instance variable `hybrid_connection_name`
  - Model `EndpointAccessResource` deleted or renamed its instance variable `access_key`
  - Model `EndpointAccessResource` deleted or renamed its instance variable `expires_on`
  - Model `EndpointAccessResource` deleted or renamed its instance variable `service_configuration_token`
  - Model `IngressGatewayResource` deleted or renamed its instance variable `hostname`
  - Model `IngressGatewayResource` deleted or renamed its instance variable `server_id`
  - Model `IngressGatewayResource` deleted or renamed its instance variable `tenant_id`
  - Model `IngressGatewayResource` deleted or renamed its instance variable `namespace_name`
  - Model `IngressGatewayResource` deleted or renamed its instance variable `namespace_name_suffix`
  - Model `IngressGatewayResource` deleted or renamed its instance variable `hybrid_connection_name`
  - Model `IngressGatewayResource` deleted or renamed its instance variable `access_key`
  - Model `IngressGatewayResource` deleted or renamed its instance variable `expires_on`
  - Model `IngressGatewayResource` deleted or renamed its instance variable `service_configuration_token`
  - Model `ServiceConfigurationResource` deleted or renamed its instance variable `service_name`
  - Model `ServiceConfigurationResource` deleted or renamed its instance variable `resource_id`
  - Model `ServiceConfigurationResource` deleted or renamed its instance variable `port`
  - Model `ServiceConfigurationResource` deleted or renamed its instance variable `provisioning_state`
  - Model `ServiceConfigurationResourcePatch` deleted or renamed its instance variable `port`
  - Deleted or renamed model `EndpointsList`
  - Deleted or renamed model `ServiceConfigurationList`
  - Parameter `expiresin` of method `EndpointsOperations.list_credentials` is now required
  - Parameter `expiresin`of method `EndpointsOperations.list_ingress_gateway_credentials` is now required

## 1.0.0 (2023-09-20)

### Other Changes

  - First GA

## 1.0.0b1 (2023-09-20)

* Initial Release
