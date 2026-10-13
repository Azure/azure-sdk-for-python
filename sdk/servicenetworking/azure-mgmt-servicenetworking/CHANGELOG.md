# Release History

## 2.1.0 (2026-08-27)

### Features Added

  - Client `ServiceNetworkingMgmtClient` added parameter `cloud_setting` in method `__init__`
  - Client `ServiceNetworkingMgmtClient` added operation group `private_endpoint_connections_interface`
  - Client `ServiceNetworkingMgmtClient` added operation group `private_link_resources_interface`
  - Model `FrontendProperties` added property `association`
  - Model `FrontendProperties` added property `public_network_access`
  - Model `FrontendProperties` added property `security_policy_configurations`
  - Model `FrontendUpdate` added property `properties`
  - Enum `PolicyType` added member `IP_ACCESS_RULES`
  - Model `SecurityPolicyConfigurations` added property `ip_access_rules_security_policy`
  - Model `SecurityPolicyProperties` added property `ip_access_rules_policy`
  - Model `SecurityPolicyUpdateProperties` added property `ip_access_rules_policy`
  - Model `TrafficControllerProperties` added property `private_endpoint_connections`
  - Added model `FrontendAssociation`
  - Added model `FrontendUpdateProperties`
  - Added model `IpAccessRule`
  - Added enum `IpAccessRuleAction`
  - Added model `IpAccessRulesPolicy`
  - Added model `IpAccessRulesSecurityPolicy`
  - Added model `PrivateEndpointConnection`
  - Added model `PrivateEndpointConnectionProperties`
  - Added model `PrivateEndpointReference`
  - Added model `PrivateLinkResource`
  - Added model `PrivateLinkResourceProperties`
  - Added model `PrivateLinkServiceConnectionState`
  - Added enum `PrivateLinkServiceConnectionStatus`
  - Added model `ProxyResource`
  - Added enum `PublicNetworkAccess`
  - Added operation group `PrivateEndpointConnectionsInterfaceOperations`
  - Added operation group `PrivateLinkResourcesInterfaceOperations`

## 2.1.0b1 (2025-05-12)

### Features Added

  - Model `FrontendProperties` added property `security_policy_configurations`
  - Model `FrontendUpdate` added property `properties`
  - Enum `PolicyType` added member `IP_ACCESS_RULES`
  - Model `SecurityPolicyConfigurations` added property `ip_access_rules_security_policy`
  - Model `SecurityPolicyProperties` added property `ip_access_rules_policy`
  - Model `SecurityPolicyUpdateProperties` added property `ip_access_rules_policy`
  - Added model `FrontendUpdateProperties`
  - Added model `IpAccessRule`
  - Added enum `IpAccessRuleAction`
  - Added model `IpAccessRulesPolicy`
  - Added model `IpAccessRulesSecurityPolicy`

## 2.0.0 (2025-02-05)

### Features Added

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
  - Added operation group `SecurityPoliciesInterfaceOperations`
  
### Breaking Changes

  - Model `Association` deleted or renamed its instance variable `association_type`
  - Model `Association` deleted or renamed its instance variable `subnet`
  - Model `Association` deleted or renamed its instance variable `provisioning_state`
  - Model `AssociationUpdate` deleted or renamed its instance variable `association_type`
  - Model `AssociationUpdate` deleted or renamed its instance variable `subnet`
  - Model `Frontend` deleted or renamed its instance variable `fqdn`
  - Model `Frontend` deleted or renamed its instance variable `provisioning_state`
  - Model `TrafficController` deleted or renamed its instance variable `configuration_endpoints`
  - Model `TrafficController` deleted or renamed its instance variable `frontends`
  - Model `TrafficController` deleted or renamed its instance variable `associations`
  - Model `TrafficController` deleted or renamed its instance variable `provisioning_state`

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
