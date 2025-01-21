# Release History

## 2.0.0 (2025-01-20)

### Features Added

  - Client `ServiceNetworkingMgmtClient` added method `send_request`
  - Client `ServiceNetworkingMgmtClient` added operation group `security_policies_interface`
  - Model `Association` added property `properties`
  - Model `AssociationUpdate` added property `properties`
  - Model `Frontend` added property `properties`
  - Model `TrafficController` added property `properties`
  - Model `TrafficControllerUpdate` added property `properties`
  - Added model `AssociationProperties`
  - Added model `AssociationUpdateProperties`
  - Added model `FrontendProperties`
  - Added enum `PolicyType`
  - Added model `SecurityPolicy`
  - Added model `SecurityPolicyConfigurations`
  - Added model `SecurityPolicyProperties`
  - Added model `SecurityPolicyUpdate`
  - Added model `SecurityPolicyUpdateProperties`
  - Added model `TrafficControllerProperties`
  - Added model `TrafficControllerUpdateProperties`
  - Added model `WafPolicy`
  - Added model `WafSecurityPolicy`
  - Added model `SecurityPoliciesInterfaceOperations`
  - Method `Association.__init__` has a new overload `def __init__(self: None, location: str, tags: Optional[Dict[str, str]], properties: Optional[_models.AssociationProperties])`
  - Method `Association.__init__` has a new overload `def __init__(self: None, mapping: Mapping[str, Any])`
  - Method `Association.__init__` has a new overload `def __init__(self: None, location: str, tags: Optional[Dict[str, str]])`
  - Method `Association.__init__` has a new overload `def __init__(self: None, mapping: Mapping[str, Any])`
  - Method `AssociationSubnet.__init__` has a new overload `def __init__(self: None, id: str)`
  - Method `AssociationSubnet.__init__` has a new overload `def __init__(self: None, mapping: Mapping[str, Any])`
  - Method `AssociationUpdate.__init__` has a new overload `def __init__(self: None, tags: Optional[Dict[str, str]], properties: Optional[_models.AssociationUpdateProperties])`
  - Method `AssociationUpdate.__init__` has a new overload `def __init__(self: None, mapping: Mapping[str, Any])`
  - Method `ErrorResponse.__init__` has a new overload `def __init__(self: None, error: Optional[_models.ErrorDetail])`
  - Method `ErrorResponse.__init__` has a new overload `def __init__(self: None, mapping: Mapping[str, Any])`
  - Method `Frontend.__init__` has a new overload `def __init__(self: None, location: str, tags: Optional[Dict[str, str]], properties: Optional[_models.FrontendProperties])`
  - Method `Frontend.__init__` has a new overload `def __init__(self: None, mapping: Mapping[str, Any])`
  - Method `Frontend.__init__` has a new overload `def __init__(self: None, location: str, tags: Optional[Dict[str, str]])`
  - Method `Frontend.__init__` has a new overload `def __init__(self: None, mapping: Mapping[str, Any])`
  - Method `FrontendUpdate.__init__` has a new overload `def __init__(self: None, tags: Optional[Dict[str, str]])`
  - Method `FrontendUpdate.__init__` has a new overload `def __init__(self: None, mapping: Mapping[str, Any])`
  - Method `Operation.__init__` has a new overload `def __init__(self: None, display: Optional[_models.OperationDisplay])`
  - Method `Operation.__init__` has a new overload `def __init__(self: None, mapping: Mapping[str, Any])`
  - Method `ResourceId.__init__` has a new overload `def __init__(self: None, id: str)`
  - Method `ResourceId.__init__` has a new overload `def __init__(self: None, mapping: Mapping[str, Any])`
  - Method `SystemData.__init__` has a new overload `def __init__(self: None, created_by: Optional[str], created_by_type: Optional[Union[str, _models.CreatedByType]], created_at: Optional[datetime], last_modified_by: Optional[str], last_modified_by_type: Optional[Union[str, _models.CreatedByType]], last_modified_at: Optional[datetime])`
  - Method `SystemData.__init__` has a new overload `def __init__(self: None, mapping: Mapping[str, Any])`
  - Method `TrackedResource.__init__` has a new overload `def __init__(self: None, location: str, tags: Optional[Dict[str, str]])`
  - Method `TrackedResource.__init__` has a new overload `def __init__(self: None, mapping: Mapping[str, Any])`
  - Method `TrafficController.__init__` has a new overload `def __init__(self: None, location: str, tags: Optional[Dict[str, str]], properties: Optional[_models.TrafficControllerProperties])`
  - Method `TrafficController.__init__` has a new overload `def __init__(self: None, mapping: Mapping[str, Any])`
  - Method `TrafficController.__init__` has a new overload `def __init__(self: None, location: str, tags: Optional[Dict[str, str]])`
  - Method `TrafficController.__init__` has a new overload `def __init__(self: None, mapping: Mapping[str, Any])`
  - Method `TrafficControllerUpdate.__init__` has a new overload `def __init__(self: None, tags: Optional[Dict[str, str]], properties: Optional[_models.TrafficControllerUpdateProperties])`
  - Method `TrafficControllerUpdate.__init__` has a new overload `def __init__(self: None, mapping: Mapping[str, Any])`
  - Method `AssociationProperties.__init__` has a new overload `def __init__(self: None, association_type: Union[str, _models.AssociationType], subnet: Optional[_models.AssociationSubnet])`
  - Method `AssociationProperties.__init__` has a new overload `def __init__(self: None, mapping: Mapping[str, Any])`
  - Method `AssociationUpdateProperties.__init__` has a new overload `def __init__(self: None, association_type: Optional[Union[str, _models.AssociationType]], subnet: Optional[_models.AssociationSubnet])`
  - Method `AssociationUpdateProperties.__init__` has a new overload `def __init__(self: None, mapping: Mapping[str, Any])`
  - Method `SecurityPolicy.__init__` has a new overload `def __init__(self: None, location: str, tags: Optional[Dict[str, str]], properties: Optional[_models.SecurityPolicyProperties])`
  - Method `SecurityPolicy.__init__` has a new overload `def __init__(self: None, mapping: Mapping[str, Any])`
  - Method `SecurityPolicy.__init__` has a new overload `def __init__(self: None, location: str, tags: Optional[Dict[str, str]])`
  - Method `SecurityPolicy.__init__` has a new overload `def __init__(self: None, mapping: Mapping[str, Any])`
  - Method `SecurityPolicyConfigurations.__init__` has a new overload `def __init__(self: None, waf_security_policy: Optional[_models.WafSecurityPolicy])`
  - Method `SecurityPolicyConfigurations.__init__` has a new overload `def __init__(self: None, mapping: Mapping[str, Any])`
  - Method `SecurityPolicyProperties.__init__` has a new overload `def __init__(self: None, waf_policy: Optional[_models.WafPolicy])`
  - Method `SecurityPolicyProperties.__init__` has a new overload `def __init__(self: None, mapping: Mapping[str, Any])`
  - Method `SecurityPolicyUpdate.__init__` has a new overload `def __init__(self: None, tags: Optional[Dict[str, str]], properties: Optional[_models.SecurityPolicyUpdateProperties])`
  - Method `SecurityPolicyUpdate.__init__` has a new overload `def __init__(self: None, mapping: Mapping[str, Any])`
  - Method `SecurityPolicyUpdateProperties.__init__` has a new overload `def __init__(self: None, waf_policy: Optional[_models.WafPolicy])`
  - Method `SecurityPolicyUpdateProperties.__init__` has a new overload `def __init__(self: None, mapping: Mapping[str, Any])`
  - Method `TrafficControllerProperties.__init__` has a new overload `def __init__(self: None, security_policy_configurations: Optional[_models.SecurityPolicyConfigurations])`
  - Method `TrafficControllerProperties.__init__` has a new overload `def __init__(self: None, mapping: Mapping[str, Any])`
  - Method `TrafficControllerUpdateProperties.__init__` has a new overload `def __init__(self: None, security_policy_configurations: Optional[_models.SecurityPolicyConfigurations])`
  - Method `TrafficControllerUpdateProperties.__init__` has a new overload `def __init__(self: None, mapping: Mapping[str, Any])`
  - Method `WafPolicy.__init__` has a new overload `def __init__(self: None, id: str)`
  - Method `WafPolicy.__init__` has a new overload `def __init__(self: None, mapping: Mapping[str, Any])`
  - Method `WafSecurityPolicy.__init__` has a new overload `def __init__(self: None, id: str)`
  - Method `WafSecurityPolicy.__init__` has a new overload `def __init__(self: None, mapping: Mapping[str, Any])`
  - Method `AssociationsInterfaceOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, traffic_controller_name: str, association_name: str, resource: IO[bytes], content_type: str)`
  - Method `AssociationsInterfaceOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, traffic_controller_name: str, association_name: str, resource: JSON, content_type: str)`
  - Method `AssociationsInterfaceOperations.update` has a new overload `def update(self: None, resource_group_name: str, traffic_controller_name: str, association_name: str, properties: IO[bytes], content_type: str)`
  - Method `AssociationsInterfaceOperations.update` has a new overload `def update(self: None, resource_group_name: str, traffic_controller_name: str, association_name: str, properties: JSON, content_type: str)`
  - Method `FrontendsInterfaceOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, traffic_controller_name: str, frontend_name: str, resource: IO[bytes], content_type: str)`
  - Method `FrontendsInterfaceOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, traffic_controller_name: str, frontend_name: str, resource: JSON, content_type: str)`
  - Method `FrontendsInterfaceOperations.update` has a new overload `def update(self: None, resource_group_name: str, traffic_controller_name: str, frontend_name: str, properties: IO[bytes], content_type: str)`
  - Method `FrontendsInterfaceOperations.update` has a new overload `def update(self: None, resource_group_name: str, traffic_controller_name: str, frontend_name: str, properties: JSON, content_type: str)`
  - Method `TrafficControllerInterfaceOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, traffic_controller_name: str, resource: IO[bytes], content_type: str)`
  - Method `TrafficControllerInterfaceOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, traffic_controller_name: str, resource: JSON, content_type: str)`
  - Method `TrafficControllerInterfaceOperations.update` has a new overload `def update(self: None, resource_group_name: str, traffic_controller_name: str, properties: IO[bytes], content_type: str)`
  - Method `TrafficControllerInterfaceOperations.update` has a new overload `def update(self: None, resource_group_name: str, traffic_controller_name: str, properties: JSON, content_type: str)`
  - Method `SecurityPoliciesInterfaceOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, traffic_controller_name: str, security_policy_name: str, resource: SecurityPolicy, content_type: str)`
  - Method `SecurityPoliciesInterfaceOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, traffic_controller_name: str, security_policy_name: str, resource: JSON, content_type: str)`
  - Method `SecurityPoliciesInterfaceOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, traffic_controller_name: str, security_policy_name: str, resource: IO[bytes], content_type: str)`
  - Method `SecurityPoliciesInterfaceOperations.update` has a new overload `def update(self: None, resource_group_name: str, traffic_controller_name: str, security_policy_name: str, properties: SecurityPolicyUpdate, content_type: str)`
  - Method `SecurityPoliciesInterfaceOperations.update` has a new overload `def update(self: None, resource_group_name: str, traffic_controller_name: str, security_policy_name: str, properties: JSON, content_type: str)`
  - Method `SecurityPoliciesInterfaceOperations.update` has a new overload `def update(self: None, resource_group_name: str, traffic_controller_name: str, security_policy_name: str, properties: IO[bytes], content_type: str)`

### Breaking Changes

  - Model `Association` deleted or renamed its instance variable `association_type`
  - Model `Association` deleted or renamed its instance variable `subnet`
  - Model `Association` deleted or renamed its instance variable `provisioning_state`
  - Model `Association` deleted or renamed its instance variable `additional_properties`
  - Model `AssociationSubnet` deleted or renamed its instance variable `additional_properties`
  - Model `AssociationUpdate` deleted or renamed its instance variable `association_type`
  - Model `AssociationUpdate` deleted or renamed its instance variable `subnet`
  - Model `AssociationUpdate` deleted or renamed its instance variable `additional_properties`
  - Model `ErrorAdditionalInfo` deleted or renamed its instance variable `additional_properties`
  - Model `ErrorDetail` deleted or renamed its instance variable `additional_properties`
  - Model `ErrorResponse` deleted or renamed its instance variable `additional_properties`
  - Model `Frontend` deleted or renamed its instance variable `fqdn`
  - Model `Frontend` deleted or renamed its instance variable `provisioning_state`
  - Model `Frontend` deleted or renamed its instance variable `additional_properties`
  - Model `FrontendUpdate` deleted or renamed its instance variable `additional_properties`
  - Model `Operation` deleted or renamed its instance variable `additional_properties`
  - Model `OperationDisplay` deleted or renamed its instance variable `additional_properties`
  - Model `Resource` deleted or renamed its instance variable `additional_properties`
  - Model `ResourceId` deleted or renamed its instance variable `additional_properties`
  - Model `SystemData` deleted or renamed its instance variable `additional_properties`
  - Model `TrackedResource` deleted or renamed its instance variable `additional_properties`
  - Model `TrafficController` deleted or renamed its instance variable `configuration_endpoints`
  - Model `TrafficController` deleted or renamed its instance variable `frontends`
  - Model `TrafficController` deleted or renamed its instance variable `associations`
  - Model `TrafficController` deleted or renamed its instance variable `provisioning_state`
  - Model `TrafficController` deleted or renamed its instance variable `additional_properties`
  - Model `TrafficControllerUpdate` deleted or renamed its instance variable `additional_properties`
  - Deleted or renamed model `AssociationSubnetUpdate`

## 1.1.0 (2025-01-20)

### Features Added

  - Client `ServiceNetworkingMgmtClient` added operation group `security_policies_interface`
  - Model `TrafficController` added property `security_policies`
  - Model `TrafficController` added property `security_policy_configurations`
  - Model `TrafficControllerUpdate` added property `security_policy_configurations`
  - Added enum `PolicyType`
  - Added model `SecurityPolicy`
  - Added model `SecurityPolicyConfigurations`
  - Added model `SecurityPolicyConfigurationsUpdate`
  - Added model `SecurityPolicyListResult`
  - Added model `SecurityPolicyUpdate`
  - Added model `WafPolicy`
  - Added model `WafPolicyUpdate`
  - Added model `WafSecurityPolicy`
  - Added model `WafSecurityPolicyUpdate`
  - Added model `SecurityPoliciesInterfaceOperations`

## 1.1.0b1 (2024-09-29)

### Features Added

  - Client `ServiceNetworkingMgmtClient` added operation group `security_policies_interface`
  - Model `TrafficController` added property `security_policies`
  - Model `TrafficController` added property `security_policy_configurations`
  - Model `TrafficControllerUpdate` added property `security_policy_configurations`
  - Added enum `PolicyType`
  - Added model `SecurityPolicy`
  - Added model `SecurityPolicyConfigurations`
  - Added model `SecurityPolicyConfigurationsUpdate`
  - Added model `SecurityPolicyListResult`
  - Added model `SecurityPolicyUpdate`
  - Added model `WafPolicy`
  - Added model `WafPolicyUpdate`
  - Added model `WafSecurityPolicy`
  - Added model `WafSecurityPolicyUpdate`
  - Added model `SecurityPoliciesInterfaceOperations`

## 1.0.0 (2023-11-20)

### Other Changes

  - First GA

## 1.0.0b2 (2023-05-20)

### Features Added

  - Model AssociationUpdate has a new parameter association_type
  - Model AssociationUpdate has a new parameter subnet
  - Model Frontend has a new parameter fqdn

### Breaking Changes

  - Model AssociationUpdate no longer has parameter properties
  - Model Frontend no longer has parameter ip_address_version
  - Model Frontend no longer has parameter mode
  - Model Frontend no longer has parameter public_ip_address
  - Model FrontendUpdate no longer has parameter properties
  - Model TrafficControllerUpdate no longer has parameter properties

## 1.0.0b1 (2023-01-17)

* Initial Release
