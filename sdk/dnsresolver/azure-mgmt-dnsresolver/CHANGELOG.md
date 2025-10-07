# Release History

## 2.0.0b1 (2025-10-07)

### Features Added

  - Model `VirtualNetworkDnsForwardingRuleset` added property `properties`
  - Added model `CloudError`
  - Added model `DnsResolverDomainListBulkProperties`
  - Added model `ForwardingRulePatchProperties`
  - Added enum `ManagedDomainList`
  - Added model `VirtualNetworkLinkPatchProperties`
  - Added model `VirtualNetworkLinkSubResourceProperties`
  - Model `DnsForwardingRulesetsOperations` added parameter `etag` in method `begin_create_or_update`
  - Model `DnsForwardingRulesetsOperations` added parameter `match_condition` in method `begin_create_or_update`
  - Model `DnsForwardingRulesetsOperations` added parameter `etag` in method `begin_delete`
  - Model `DnsForwardingRulesetsOperations` added parameter `match_condition` in method `begin_delete`
  - Model `DnsForwardingRulesetsOperations` added parameter `etag` in method `begin_update`
  - Model `DnsForwardingRulesetsOperations` added parameter `match_condition` in method `begin_update`
  - Model `DnsResolverDomainListsOperations` added parameter `etag` in method `begin_bulk`
  - Model `DnsResolverDomainListsOperations` added parameter `match_condition` in method `begin_bulk`
  - Model `DnsResolverDomainListsOperations` added parameter `etag` in method `begin_create_or_update`
  - Model `DnsResolverDomainListsOperations` added parameter `match_condition` in method `begin_create_or_update`
  - Model `DnsResolverDomainListsOperations` added parameter `etag` in method `begin_delete`
  - Model `DnsResolverDomainListsOperations` added parameter `match_condition` in method `begin_delete`
  - Model `DnsResolverDomainListsOperations` added parameter `etag` in method `begin_update`
  - Model `DnsResolverDomainListsOperations` added parameter `match_condition` in method `begin_update`
  - Model `DnsResolverPoliciesOperations` added parameter `etag` in method `begin_create_or_update`
  - Model `DnsResolverPoliciesOperations` added parameter `match_condition` in method `begin_create_or_update`
  - Model `DnsResolverPoliciesOperations` added parameter `etag` in method `begin_delete`
  - Model `DnsResolverPoliciesOperations` added parameter `match_condition` in method `begin_delete`
  - Model `DnsResolverPoliciesOperations` added parameter `etag` in method `begin_update`
  - Model `DnsResolverPoliciesOperations` added parameter `match_condition` in method `begin_update`
  - Model `DnsResolverPolicyVirtualNetworkLinksOperations` added parameter `etag` in method `begin_create_or_update`
  - Model `DnsResolverPolicyVirtualNetworkLinksOperations` added parameter `match_condition` in method `begin_create_or_update`
  - Model `DnsResolverPolicyVirtualNetworkLinksOperations` added parameter `etag` in method `begin_delete`
  - Model `DnsResolverPolicyVirtualNetworkLinksOperations` added parameter `match_condition` in method `begin_delete`
  - Model `DnsResolverPolicyVirtualNetworkLinksOperations` added parameter `etag` in method `begin_update`
  - Model `DnsResolverPolicyVirtualNetworkLinksOperations` added parameter `match_condition` in method `begin_update`
  - Model `DnsResolversOperations` added parameter `etag` in method `begin_create_or_update`
  - Model `DnsResolversOperations` added parameter `match_condition` in method `begin_create_or_update`
  - Model `DnsResolversOperations` added parameter `etag` in method `begin_delete`
  - Model `DnsResolversOperations` added parameter `match_condition` in method `begin_delete`
  - Model `DnsResolversOperations` added parameter `etag` in method `begin_update`
  - Model `DnsResolversOperations` added parameter `match_condition` in method `begin_update`
  - Model `DnsSecurityRulesOperations` added parameter `etag` in method `begin_create_or_update`
  - Model `DnsSecurityRulesOperations` added parameter `match_condition` in method `begin_create_or_update`
  - Model `DnsSecurityRulesOperations` added parameter `etag` in method `begin_delete`
  - Model `DnsSecurityRulesOperations` added parameter `match_condition` in method `begin_delete`
  - Model `DnsSecurityRulesOperations` added parameter `etag` in method `begin_update`
  - Model `DnsSecurityRulesOperations` added parameter `match_condition` in method `begin_update`
  - Model `ForwardingRulesOperations` added parameter `etag` in method `create_or_update`
  - Model `ForwardingRulesOperations` added parameter `match_condition` in method `create_or_update`
  - Model `ForwardingRulesOperations` added parameter `etag` in method `delete`
  - Model `ForwardingRulesOperations` added parameter `match_condition` in method `delete`
  - Model `ForwardingRulesOperations` added parameter `etag` in method `update`
  - Model `ForwardingRulesOperations` added parameter `match_condition` in method `update`
  - Model `InboundEndpointsOperations` added parameter `etag` in method `begin_create_or_update`
  - Model `InboundEndpointsOperations` added parameter `match_condition` in method `begin_create_or_update`
  - Model `InboundEndpointsOperations` added parameter `etag` in method `begin_delete`
  - Model `InboundEndpointsOperations` added parameter `match_condition` in method `begin_delete`
  - Model `InboundEndpointsOperations` added parameter `etag` in method `begin_update`
  - Model `InboundEndpointsOperations` added parameter `match_condition` in method `begin_update`
  - Model `OutboundEndpointsOperations` added parameter `etag` in method `begin_create_or_update`
  - Model `OutboundEndpointsOperations` added parameter `match_condition` in method `begin_create_or_update`
  - Model `OutboundEndpointsOperations` added parameter `etag` in method `begin_delete`
  - Model `OutboundEndpointsOperations` added parameter `match_condition` in method `begin_delete`
  - Model `OutboundEndpointsOperations` added parameter `etag` in method `begin_update`
  - Model `OutboundEndpointsOperations` added parameter `match_condition` in method `begin_update`
  - Model `VirtualNetworkLinksOperations` added parameter `etag` in method `begin_create_or_update`
  - Model `VirtualNetworkLinksOperations` added parameter `match_condition` in method `begin_create_or_update`
  - Model `VirtualNetworkLinksOperations` added parameter `etag` in method `begin_delete`
  - Model `VirtualNetworkLinksOperations` added parameter `match_condition` in method `begin_delete`
  - Model `VirtualNetworkLinksOperations` added parameter `etag` in method `begin_update`
  - Model `VirtualNetworkLinksOperations` added parameter `match_condition` in method `begin_update`

### Breaking Changes

  - Deleted or renamed client `DnsResolverManagementClient`
  - Model `DnsResolverDomainListBulk` deleted or renamed its instance variable `storage_url`
  - Model `DnsResolverDomainListBulk` deleted or renamed its instance variable `action`
  - Model `ForwardingRulePatch` deleted or renamed its instance variable `target_dns_servers`
  - Model `ForwardingRulePatch` deleted or renamed its instance variable `metadata`
  - Model `ForwardingRulePatch` deleted or renamed its instance variable `forwarding_rule_state`
  - Model `VirtualNetworkDnsForwardingRuleset` deleted or renamed its instance variable `virtual_network_link`
  - Model `VirtualNetworkLinkPatch` deleted or renamed its instance variable `metadata`
  - Method `DnsForwardingRulesetsOperations.begin_create_or_update` deleted or renamed its parameter `if_match` of kind `positional_or_keyword`
  - Method `DnsForwardingRulesetsOperations.begin_create_or_update` deleted or renamed its parameter `if_none_match` of kind `positional_or_keyword`
  - Method `DnsForwardingRulesetsOperations.begin_delete` deleted or renamed its parameter `if_match` of kind `positional_or_keyword`
  - Method `DnsForwardingRulesetsOperations.begin_update` deleted or renamed its parameter `if_match` of kind `positional_or_keyword`
  - Method `DnsResolverDomainListsOperations.begin_bulk` deleted or renamed its parameter `if_match` of kind `positional_or_keyword`
  - Method `DnsResolverDomainListsOperations.begin_bulk` deleted or renamed its parameter `if_none_match` of kind `positional_or_keyword`
  - Method `DnsResolverDomainListsOperations.begin_create_or_update` deleted or renamed its parameter `if_match` of kind `positional_or_keyword`
  - Method `DnsResolverDomainListsOperations.begin_create_or_update` deleted or renamed its parameter `if_none_match` of kind `positional_or_keyword`
  - Method `DnsResolverDomainListsOperations.begin_delete` deleted or renamed its parameter `if_match` of kind `positional_or_keyword`
  - Method `DnsResolverDomainListsOperations.begin_update` deleted or renamed its parameter `if_match` of kind `positional_or_keyword`
  - Method `DnsResolverPoliciesOperations.begin_create_or_update` deleted or renamed its parameter `if_match` of kind `positional_or_keyword`
  - Method `DnsResolverPoliciesOperations.begin_create_or_update` deleted or renamed its parameter `if_none_match` of kind `positional_or_keyword`
  - Method `DnsResolverPoliciesOperations.begin_delete` deleted or renamed its parameter `if_match` of kind `positional_or_keyword`
  - Method `DnsResolverPoliciesOperations.begin_update` deleted or renamed its parameter `if_match` of kind `positional_or_keyword`
  - Method `DnsResolverPolicyVirtualNetworkLinksOperations.begin_create_or_update` deleted or renamed its parameter `if_match` of kind `positional_or_keyword`
  - Method `DnsResolverPolicyVirtualNetworkLinksOperations.begin_create_or_update` deleted or renamed its parameter `if_none_match` of kind `positional_or_keyword`
  - Method `DnsResolverPolicyVirtualNetworkLinksOperations.begin_delete` deleted or renamed its parameter `if_match` of kind `positional_or_keyword`
  - Method `DnsResolverPolicyVirtualNetworkLinksOperations.begin_update` deleted or renamed its parameter `if_match` of kind `positional_or_keyword`
  - Method `DnsResolversOperations.begin_create_or_update` deleted or renamed its parameter `if_match` of kind `positional_or_keyword`
  - Method `DnsResolversOperations.begin_create_or_update` deleted or renamed its parameter `if_none_match` of kind `positional_or_keyword`
  - Method `DnsResolversOperations.begin_delete` deleted or renamed its parameter `if_match` of kind `positional_or_keyword`
  - Method `DnsResolversOperations.begin_update` deleted or renamed its parameter `if_match` of kind `positional_or_keyword`
  - Method `DnsSecurityRulesOperations.begin_create_or_update` deleted or renamed its parameter `if_match` of kind `positional_or_keyword`
  - Method `DnsSecurityRulesOperations.begin_create_or_update` deleted or renamed its parameter `if_none_match` of kind `positional_or_keyword`
  - Method `DnsSecurityRulesOperations.begin_delete` deleted or renamed its parameter `if_match` of kind `positional_or_keyword`
  - Method `DnsSecurityRulesOperations.begin_update` deleted or renamed its parameter `if_match` of kind `positional_or_keyword`
  - Method `ForwardingRulesOperations.create_or_update` deleted or renamed its parameter `if_match` of kind `positional_or_keyword`
  - Method `ForwardingRulesOperations.create_or_update` deleted or renamed its parameter `if_none_match` of kind `positional_or_keyword`
  - Method `ForwardingRulesOperations.delete` deleted or renamed its parameter `if_match` of kind `positional_or_keyword`
  - Method `ForwardingRulesOperations.update` deleted or renamed its parameter `if_match` of kind `positional_or_keyword`
  - Method `InboundEndpointsOperations.begin_create_or_update` deleted or renamed its parameter `if_match` of kind `positional_or_keyword`
  - Method `InboundEndpointsOperations.begin_create_or_update` deleted or renamed its parameter `if_none_match` of kind `positional_or_keyword`
  - Method `InboundEndpointsOperations.begin_delete` deleted or renamed its parameter `if_match` of kind `positional_or_keyword`
  - Method `InboundEndpointsOperations.begin_update` deleted or renamed its parameter `if_match` of kind `positional_or_keyword`
  - Method `OutboundEndpointsOperations.begin_create_or_update` deleted or renamed its parameter `if_match` of kind `positional_or_keyword`
  - Method `OutboundEndpointsOperations.begin_create_or_update` deleted or renamed its parameter `if_none_match` of kind `positional_or_keyword`
  - Method `OutboundEndpointsOperations.begin_delete` deleted or renamed its parameter `if_match` of kind `positional_or_keyword`
  - Method `OutboundEndpointsOperations.begin_update` deleted or renamed its parameter `if_match` of kind `positional_or_keyword`
  - Method `VirtualNetworkLinksOperations.begin_create_or_update` deleted or renamed its parameter `if_match` of kind `positional_or_keyword`
  - Method `VirtualNetworkLinksOperations.begin_create_or_update` deleted or renamed its parameter `if_none_match` of kind `positional_or_keyword`
  - Method `VirtualNetworkLinksOperations.begin_delete` deleted or renamed its parameter `if_match` of kind `positional_or_keyword`
  - Method `VirtualNetworkLinksOperations.begin_update` deleted or renamed its parameter `if_match` of kind `positional_or_keyword`
  - Method `DnsResolverPoliciesOperations.begin_create_or_update` re-ordered its parameters from `['self', 'resource_group_name', 'dns_resolver_policy_name', 'parameters', 'if_match', 'if_none_match', 'kwargs']` to `['self', 'resource_group_name', 'dns_resolver_policy_name', 'parameters', 'etag', 'match_condition', 'kwargs']`
  - Method `DnsSecurityRulesOperations.begin_create_or_update` re-ordered its parameters from `['self', 'resource_group_name', 'dns_resolver_policy_name', 'dns_security_rule_name', 'parameters', 'if_match', 'if_none_match', 'kwargs']` to `['self', 'resource_group_name', 'dns_resolver_policy_name', 'dns_security_rule_name', 'parameters', 'etag', 'match_condition', 'kwargs']`
  - Method `OutboundEndpointsOperations.begin_create_or_update` re-ordered its parameters from `['self', 'resource_group_name', 'dns_resolver_name', 'outbound_endpoint_name', 'parameters', 'if_match', 'if_none_match', 'kwargs']` to `['self', 'resource_group_name', 'dns_resolver_name', 'outbound_endpoint_name', 'parameters', 'etag', 'match_condition', 'kwargs']`
  - Method `DnsResolverPolicyVirtualNetworkLinksOperations.begin_create_or_update` re-ordered its parameters from `['self', 'resource_group_name', 'dns_resolver_policy_name', 'dns_resolver_policy_virtual_network_link_name', 'parameters', 'if_match', 'if_none_match', 'kwargs']` to `['self', 'resource_group_name', 'dns_resolver_policy_name', 'dns_resolver_policy_virtual_network_link_name', 'parameters', 'etag', 'match_condition', 'kwargs']`
  - Method `DnsResolversOperations.begin_create_or_update` re-ordered its parameters from `['self', 'resource_group_name', 'dns_resolver_name', 'parameters', 'if_match', 'if_none_match', 'kwargs']` to `['self', 'resource_group_name', 'dns_resolver_name', 'parameters', 'etag', 'match_condition', 'kwargs']`
  - Method `DnsForwardingRulesetsOperations.begin_create_or_update` re-ordered its parameters from `['self', 'resource_group_name', 'dns_forwarding_ruleset_name', 'parameters', 'if_match', 'if_none_match', 'kwargs']` to `['self', 'resource_group_name', 'dns_forwarding_ruleset_name', 'parameters', 'etag', 'match_condition', 'kwargs']`
  - Method `InboundEndpointsOperations.begin_create_or_update` re-ordered its parameters from `['self', 'resource_group_name', 'dns_resolver_name', 'inbound_endpoint_name', 'parameters', 'if_match', 'if_none_match', 'kwargs']` to `['self', 'resource_group_name', 'dns_resolver_name', 'inbound_endpoint_name', 'parameters', 'etag', 'match_condition', 'kwargs']`
  - Method `VirtualNetworkLinksOperations.begin_create_or_update` re-ordered its parameters from `['self', 'resource_group_name', 'dns_forwarding_ruleset_name', 'virtual_network_link_name', 'parameters', 'if_match', 'if_none_match', 'kwargs']` to `['self', 'resource_group_name', 'dns_forwarding_ruleset_name', 'virtual_network_link_name', 'parameters', 'etag', 'match_condition', 'kwargs']`
  - Method `DnsResolverDomainListsOperations.begin_create_or_update` re-ordered its parameters from `['self', 'resource_group_name', 'dns_resolver_domain_list_name', 'parameters', 'if_match', 'if_none_match', 'kwargs']` to `['self', 'resource_group_name', 'dns_resolver_domain_list_name', 'parameters', 'etag', 'match_condition', 'kwargs']`
  - Method `DnsResolverDomainListsOperations.begin_bulk` re-ordered its parameters from `['self', 'resource_group_name', 'dns_resolver_domain_list_name', 'parameters', 'if_match', 'if_none_match', 'kwargs']` to `['self', 'resource_group_name', 'dns_resolver_domain_list_name', 'parameters', 'etag', 'match_condition', 'kwargs']`
  - Method `ForwardingRulesOperations.create_or_update` re-ordered its parameters from `['self', 'resource_group_name', 'dns_forwarding_ruleset_name', 'forwarding_rule_name', 'parameters', 'if_match', 'if_none_match', 'kwargs']` to `['self', 'resource_group_name', 'dns_forwarding_ruleset_name', 'forwarding_rule_name', 'parameters', 'etag', 'match_condition', 'kwargs']`

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
