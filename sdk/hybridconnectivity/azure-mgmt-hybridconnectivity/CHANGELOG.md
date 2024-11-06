# Release History

## 2.0.0 (2024-11-18)

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
  - Method `ErrorResponse.__init__` has a new overload `def __init__(self: None, error: Optional[_models.ErrorDetail])`
  - Method `ErrorResponse.__init__` has a new overload `def __init__(self: None, mapping: Mapping[str, Any])`
  - Method `SystemData.__init__` has a new overload `def __init__(self: None, created_by: Optional[str], created_by_type: Optional[Union[str, _models.CreatedByType]], created_at: Optional[datetime], last_modified_by: Optional[str], last_modified_by_type: Optional[Union[str, _models.CreatedByType]], last_modified_at: Optional[datetime])`
  - Method `SystemData.__init__` has a new overload `def __init__(self: None, mapping: Mapping[str, Any])`
  - Method `AwsCloudProfile.__init__` has a new overload `def __init__(self: None, account_id: str, excluded_accounts: Optional[List[str]], is_organizational_account: Optional[bool])`
  - Method `AwsCloudProfile.__init__` has a new overload `def __init__(self: None, mapping: Mapping[str, Any])`
  - Method `GenerateAwsTemplateRequest.__init__` has a new overload `def __init__(self: None, connector_id: str, solution_types: Optional[List[_models.SolutionTypeSettings]])`
  - Method `GenerateAwsTemplateRequest.__init__` has a new overload `def __init__(self: None, mapping: Mapping[str, Any])`
  - Method `InventoryProperties.__init__` has a new overload `def __init__(self: None, cloud_native_type: Optional[Union[str, _models.CloudNativeType]], cloud_native_resource_id: Optional[str], azure_resource_id: Optional[str], status: Optional[Union[str, _models.SolutionConfigurationStatus]], status_details: Optional[str])`
  - Method `InventoryProperties.__init__` has a new overload `def __init__(self: None, mapping: Mapping[str, Any])`
  - Method `InventoryResource.__init__` has a new overload `def __init__(self: None, properties: Optional[_models.InventoryProperties])`
  - Method `InventoryResource.__init__` has a new overload `def __init__(self: None, mapping: Mapping[str, Any])`
  - Method `OperationStatusResult.__init__` has a new overload `def __init__(self: None, status: str, id: Optional[str], name: Optional[str], percent_complete: Optional[float], start_time: Optional[datetime], end_time: Optional[datetime], operations: Optional[List[_models.OperationStatusResult]], error: Optional[_models.ErrorDetail])`
  - Method `OperationStatusResult.__init__` has a new overload `def __init__(self: None, mapping: Mapping[str, Any])`
  - Method `PublicCloudConnector.__init__` has a new overload `def __init__(self: None, location: str, tags: Optional[Dict[str, str]], properties: Optional[_models.PublicCloudConnectorProperties])`
  - Method `PublicCloudConnector.__init__` has a new overload `def __init__(self: None, mapping: Mapping[str, Any])`
  - Method `PublicCloudConnector.__init__` has a new overload `def __init__(self: None, location: str, tags: Optional[Dict[str, str]])`
  - Method `PublicCloudConnector.__init__` has a new overload `def __init__(self: None, mapping: Mapping[str, Any])`
  - Method `PublicCloudConnectorProperties.__init__` has a new overload `def __init__(self: None, aws_cloud_profile: _models.AwsCloudProfile, host_type: Union[str, _models.HostType])`
  - Method `PublicCloudConnectorProperties.__init__` has a new overload `def __init__(self: None, mapping: Mapping[str, Any])`
  - Method `SolutionConfiguration.__init__` has a new overload `def __init__(self: None, properties: Optional[_models.SolutionConfigurationProperties])`
  - Method `SolutionConfiguration.__init__` has a new overload `def __init__(self: None, mapping: Mapping[str, Any])`
  - Method `SolutionConfigurationProperties.__init__` has a new overload `def __init__(self: None, solution_type: str, solution_settings: Optional[_models.SolutionSettings])`
  - Method `SolutionConfigurationProperties.__init__` has a new overload `def __init__(self: None, mapping: Mapping[str, Any])`
  - Method `SolutionTypeProperties.__init__` has a new overload `def __init__(self: None, solution_type: Optional[str], description: Optional[str], supported_azure_regions: Optional[List[str]], solution_settings: Optional[List[_models.SolutionTypeSettingsProperties]])`
  - Method `SolutionTypeProperties.__init__` has a new overload `def __init__(self: None, mapping: Mapping[str, Any])`
  - Method `SolutionTypeResource.__init__` has a new overload `def __init__(self: None, properties: Optional[_models.SolutionTypeProperties])`
  - Method `SolutionTypeResource.__init__` has a new overload `def __init__(self: None, mapping: Mapping[str, Any])`
  - Method `SolutionTypeSettings.__init__` has a new overload `def __init__(self: None, solution_type: str, solution_settings: Optional[_models.SolutionSettings])`
  - Method `SolutionTypeSettings.__init__` has a new overload `def __init__(self: None, mapping: Mapping[str, Any])`
  - Method `SolutionTypeSettingsProperties.__init__` has a new overload `def __init__(self: None, name: str, display_name: str, type: str, description: str, allowed_values: List[str], default_value: str)`
  - Method `SolutionTypeSettingsProperties.__init__` has a new overload `def __init__(self: None, mapping: Mapping[str, Any])`
  - Method `TrackedResource.__init__` has a new overload `def __init__(self: None, location: str, tags: Optional[Dict[str, str]])`
  - Method `TrackedResource.__init__` has a new overload `def __init__(self: None, mapping: Mapping[str, Any])`

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
  - Deleted or renamed model `EndpointsOperations`
  - Deleted or renamed model `Operations`
  - Deleted or renamed model `ServiceConfigurationsOperations`

## 1.0.0 (2023-09-20)

### Other Changes

  - First GA

## 1.0.0b1 (2023-09-20)

* Initial Release
