# Release History

## 1.1.0b2 (2024-10-21)

### Features Added

  - Client `DnsResolverManagementClient` added operation group `dns_resolver_policies`
  - Client `DnsResolverManagementClient` added operation group `dns_security_rules`
  - Client `DnsResolverManagementClient` added operation group `dns_resolver_policy_virtual_network_links`
  - Client `DnsResolverManagementClient` added operation group `dns_resolver_domain_lists`
  - Model `Resource` added property `system_data`
  - Added enum `ActionType`
  - Added enum `BlockResponseCode`
  - Added model `DnsResolverDomainList`
  - Added model `DnsResolverDomainListPatch`
  - Added model `DnsResolverDomainListResult`
  - Added model `DnsResolverPolicy`
  - Added model `DnsResolverPolicyListResult`
  - Added model `DnsResolverPolicyPatch`
  - Added model `DnsResolverPolicyVirtualNetworkLink`
  - Added model `DnsResolverPolicyVirtualNetworkLinkListResult`
  - Added model `DnsResolverPolicyVirtualNetworkLinkPatch`
  - Added model `DnsSecurityRule`
  - Added model `DnsSecurityRuleAction`
  - Added model `DnsSecurityRuleListResult`
  - Added model `DnsSecurityRulePatch`
  - Added enum `DnsSecurityRuleState`
  - Added model `ErrorAdditionalInfo`
  - Added model `ErrorDetail`
  - Added model `ErrorResponse`
  - Added model `DnsResolverDomainListsOperations`
  - Added model `DnsResolverPoliciesOperations`
  - Added model `DnsResolverPolicyVirtualNetworkLinksOperations`
  - Added model `DnsSecurityRulesOperations`

## 1.1.0b1 (2022-12-27)

### Other Changes

  - Added generated samples in github repo
  - Drop support for python<3.7.0

## 1.0.0 (2022-09-15)

### Features Added

  - Model DnsForwardingRulesetPatch has a new parameter dns_resolver_outbound_endpoints

### Breaking Changes

  - Parameter dns_resolver_outbound_endpoints of model DnsForwardingRuleset is now required
  - Parameter domain_name of model ForwardingRule is now required
  - Parameter id of model SubResource is now required
  - Parameter ip_address of model TargetDnsServer is now required
  - Parameter ip_configurations of model InboundEndpoint is now required
  - Parameter subnet of model IpConfiguration is now required
  - Parameter subnet of model OutboundEndpoint is now required
  - Parameter target_dns_servers of model ForwardingRule is now required
  - Parameter virtual_network of model DnsResolver is now required
  - Parameter virtual_network of model VirtualNetworkLink is now required

## 1.0.0b1 (2022-02-21)

* Initial Release
