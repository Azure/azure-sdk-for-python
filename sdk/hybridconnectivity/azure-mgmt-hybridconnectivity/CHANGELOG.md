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
  - Added model `GenerateAwsTemplateOperations`
  - Added model `InventoryOperations`
  - Added model `PublicCloudConnectorsOperations`
  - Added model `SolutionConfigurationsOperations`
  - Added model `SolutionTypesOperations`
  - Method `EndpointsOperations.create_or_update` has a new overload `def create_or_update(self: None, resource_uri: str, endpoint_name: str, endpoint_resource: IO[bytes], content_type: str)`
  - Method `EndpointsOperations.list_credentials` has a new overload `def list_credentials(self: None, resource_uri: str, endpoint_name: str, expiresin: int, list_credentials_request: Optional[IO[bytes]], content_type: str)`
  - Method `EndpointsOperations.list_ingress_gateway_credentials` has a new overload `def list_ingress_gateway_credentials(self: None, resource_uri: str, endpoint_name: str, expiresin: int, list_ingress_gateway_credentials_request: Optional[IO[bytes]], content_type: str)`
  - Method `EndpointsOperations.list_managed_proxy_details` has a new overload `def list_managed_proxy_details(self: None, resource_uri: str, endpoint_name: str, managed_proxy_request: IO[bytes], content_type: str)`
  - Method `EndpointsOperations.update` has a new overload `def update(self: None, resource_uri: str, endpoint_name: str, endpoint_resource: IO[bytes], content_type: str)`
  - Method `ServiceConfigurationsOperations.create_orupdate` has a new overload `def create_orupdate(self: None, resource_uri: str, endpoint_name: str, service_configuration_name: str, service_configuration_resource: IO[bytes], content_type: str)`
  - Method `ServiceConfigurationsOperations.update` has a new overload `def update(self: None, resource_uri: str, endpoint_name: str, service_configuration_name: str, service_configuration_resource: IO[bytes], content_type: str)`
  - Method `GenerateAwsTemplateOperations.post` has a new overload `def post(self: None, generate_aws_template_request: GenerateAwsTemplateRequest, content_type: str)`
  - Method `GenerateAwsTemplateOperations.post` has a new overload `def post(self: None, generate_aws_template_request: IO[bytes], content_type: str)`
  - Method `PublicCloudConnectorsOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, public_cloud_connector: str, resource: PublicCloudConnector, content_type: str)`
  - Method `PublicCloudConnectorsOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, public_cloud_connector: str, resource: IO[bytes], content_type: str)`
  - Method `PublicCloudConnectorsOperations.update` has a new overload `def update(self: None, resource_group_name: str, public_cloud_connector: str, properties: PublicCloudConnectorUpdate, content_type: str)`
  - Method `PublicCloudConnectorsOperations.update` has a new overload `def update(self: None, resource_group_name: str, public_cloud_connector: str, properties: IO[bytes], content_type: str)`
  - Method `SolutionConfigurationsOperations.create_or_update` has a new overload `def create_or_update(self: None, resource_uri: str, solution_configuration: str, resource: SolutionConfiguration, content_type: str)`
  - Method `SolutionConfigurationsOperations.create_or_update` has a new overload `def create_or_update(self: None, resource_uri: str, solution_configuration: str, resource: IO[bytes], content_type: str)`
  - Method `SolutionConfigurationsOperations.update` has a new overload `def update(self: None, resource_uri: str, solution_configuration: str, properties: SolutionConfigurationUpdate, content_type: str)`
  - Method `SolutionConfigurationsOperations.update` has a new overload `def update(self: None, resource_uri: str, solution_configuration: str, properties: IO[bytes], content_type: str)`

### Breaking Changes

  - Method `HybridConnectivityMgmtClient.__init__` inserted a `positional_or_keyword` parameter `subscription_id`

## 1.0.0 (2023-09-20)

### Other Changes

  - First GA

## 1.0.0b1 (2023-09-20)

* Initial Release
