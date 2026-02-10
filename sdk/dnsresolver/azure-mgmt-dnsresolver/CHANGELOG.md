# Release History

## 2.0.0b1 (2025-10-23)

### Features Added

  - Model `DnsResolverManagementClient` added parameter `cloud_setting` in method `__init__`
  - Client `DnsResolverManagementClient` added method `send_request`
  - Model `VirtualNetworkDnsForwardingRuleset` added property `properties`
  - Added model `CloudError`
  - Added model `DnsResolverDomainListBulkProperties`
  - Added model `ForwardingRulePatchProperties`
  - Added enum `ManagedDomainList`
  - Added model `VirtualNetworkLinkPatchProperties`
  - Added model `VirtualNetworkLinkSubResourceProperties`

### Breaking Changes

  - This version introduces new hybrid models which have dual dictionary and model nature. And please follow https://aka.ms/azsdk/python/migrate/hybrid-models for migration.
  - For the method breakings, please refer to https://aka.ms/azsdk/python/migrate/operations for migration.
  - Model `DnsResolverDomainListBulk` instance variables `storage_url` and `action` have been moved under property `properties`
  - Model `ForwardingRulePatch` instance variables `target_dns_servers`, `metadata`, and `forwarding_rule_state` have been moved under property `properties`
  - Model `VirtualNetworkDnsForwardingRuleset` instance variable `virtual_network_link` has been moved under property `properties`
  - Model `VirtualNetworkLinkPatch` instance variable `metadata` has been moved under property `properties`
  - Method `DnsForwardingRulesetsOperations.begin_create_or_update` replaced positional_or_keyword parameters `if_match`/`if_none_match` to keyword_only parameters `etag`/`match_condition`
  - Method `DnsForwardingRulesetsOperations.begin_delete` replaced positional_or_keyword parameter `if_match` to keyword_only parameters `etag`/`match_condition`
  - Method `DnsForwardingRulesetsOperations.begin_update` replaced positional_or_keyword parameter `if_match` to keyword_only parameters `etag`/`match_condition`
  - Method `DnsResolverDomainListsOperations.begin_bulk` replaced positional_or_keyword parameters `if_match`/`if_none_match` to keyword_only parameters `etag`/`match_condition`
  - Method `DnsResolverDomainListsOperations.begin_create_or_update` replaced positional_or_keyword parameters `if_match`/`if_none_match` to keyword_only parameters `etag`/`match_condition`
  - Method `DnsResolverDomainListsOperations.begin_delete` replaced positional_or_keyword parameter `if_match` to keyword_only parameters `etag`/`match_condition`
  - Method `DnsResolverDomainListsOperations.begin_update` replaced positional_or_keyword parameter `if_match` to keyword_only parameters `etag`/`match_condition`
  - Method `DnsResolverPoliciesOperations.begin_create_or_update` replaced positional_or_keyword parameters `if_match`/`if_none_match` to keyword_only parameters `etag`/`match_condition`
  - Method `DnsResolverPoliciesOperations.begin_delete` replaced positional_or_keyword parameter `if_match` to keyword_only parameters `etag`/`match_condition`
  - Method `DnsResolverPoliciesOperations.begin_update` replaced positional_or_keyword parameter `if_match` to keyword_only parameters `etag`/`match_condition`
  - Method `DnsResolverPolicyVirtualNetworkLinksOperations.begin_create_or_update` replaced positional_or_keyword parameters `if_match`/`if_none_match` to keyword_only parameters `etag`/`match_condition`
  - Method `DnsResolverPolicyVirtualNetworkLinksOperations.begin_delete` replaced positional_or_keyword parameter `if_match` to keyword_only parameters `etag`/`match_condition`
  - Method `DnsResolverPolicyVirtualNetworkLinksOperations.begin_update` replaced positional_or_keyword parameter `if_match` to keyword_only parameters `etag`/`match_condition`
  - Method `DnsResolversOperations.begin_create_or_update` replaced positional_or_keyword parameters `if_match`/`if_none_match` to keyword_only parameters `etag`/`match_condition`
  - Method `DnsResolversOperations.begin_delete` replaced positional_or_keyword parameter `if_match` to keyword_only parameters `etag`/`match_condition`
  - Method `DnsResolversOperations.begin_update` replaced positional_or_keyword parameter `if_match` to keyword_only parameters `etag`/`match_condition`
  - Method `DnsSecurityRulesOperations.begin_create_or_update` replaced positional_or_keyword parameters `if_match`/`if_none_match` to keyword_only parameters `etag`/`match_condition`
  - Method `DnsSecurityRulesOperations.begin_delete` replaced positional_or_keyword parameter `if_match` to keyword_only parameters `etag`/`match_condition`
  - Method `DnsSecurityRulesOperations.begin_update` replaced positional_or_keyword parameter `if_match` to keyword_only parameters `etag`/`match_condition`
  - Method `ForwardingRulesOperations.create_or_update` replaced positional_or_keyword parameters `if_match`/`if_none_match` to keyword_only parameters `etag`/`match_condition`
  - Method `ForwardingRulesOperations.delete` replaced positional_or_keyword parameter `if_match` to keyword_only parameters `etag`/`match_condition`
  - Method `ForwardingRulesOperations.update` replaced positional_or_keyword parameter `if_match` to keyword_only parameters `etag`/`match_condition`
  - Method `InboundEndpointsOperations.begin_create_or_update` replaced positional_or_keyword parameters `if_match`/`if_none_match` to keyword_only parameters `etag`/`match_condition`
  - Method `InboundEndpointsOperations.begin_delete` replaced positional_or_keyword parameter `if_match` to keyword_only parameters `etag`/`match_condition`
  - Method `InboundEndpointsOperations.begin_update` replaced positional_or_keyword parameter `if_match` to keyword_only parameters `etag`/`match_condition`
  - Method `OutboundEndpointsOperations.begin_create_or_update` replaced positional_or_keyword parameters `if_match`/`if_none_match` to keyword_only parameters `etag`/`match_condition`
  - Method `OutboundEndpointsOperations.begin_delete` replaced positional_or_keyword parameter `if_match` to keyword_only parameters `etag`/`match_condition`
  - Method `OutboundEndpointsOperations.begin_update` replaced positional_or_keyword parameter `if_match` to keyword_only parameters `etag`/`match_condition`
  - Method `VirtualNetworkLinksOperations.begin_create_or_update` replaced positional_or_keyword parameters `if_match`/`if_none_match` to keyword_only parameters `etag`/`match_condition`
  - Method `VirtualNetworkLinksOperations.begin_delete` replaced positional_or_keyword parameter `if_match` to keyword_only parameters `etag`/`match_condition`
  - Method `VirtualNetworkLinksOperations.begin_update` replaced positional_or_keyword parameter `if_match` to keyword_only parameters `etag`/`match_condition`

## 1.1.0 (2025-06-16)

### Features Added

  - Client `DnsResolverManagementClient` added operation group `dns_resolver_policies`
  - Client `DnsResolverManagementClient` added operation group `dns_security_rules`
  - Client `DnsResolverManagementClient` added operation group `dns_resolver_policy_virtual_network_links`
  - Client `DnsResolverManagementClient` added operation group `dns_resolver_domain_lists`
  - Model `ProxyResource` added property `system_data`
  - Model `Resource` added property `system_data`
  - Model `TrackedResource` added property `system_data`
  - Added enum `Action`
  - Added enum `ActionType`
  - Added model `DnsResolverDomainList`
  - Added model `DnsResolverDomainListBulk`
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
  - Added operation group `DnsResolverDomainListsOperations`
  - Added operation group `DnsResolverPoliciesOperations`
  - Added operation group `DnsResolverPolicyVirtualNetworkLinksOperations`
  - Added operation group `DnsSecurityRulesOperations`

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
