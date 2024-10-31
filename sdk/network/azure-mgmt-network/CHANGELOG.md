# Release History

## 28.0.0 (2024-10-31)

### Features Added

  - Client `NetworkManagementClient` added operation group `application_gateways`
  - Client `NetworkManagementClient` added operation group `application_gateway_private_link_resources`
  - Client `NetworkManagementClient` added operation group `application_gateway_private_endpoint_connections`
  - Client `NetworkManagementClient` added operation group `application_gateway_waf_dynamic_manifests_default`
  - Client `NetworkManagementClient` added operation group `application_gateway_waf_dynamic_manifests`
  - Client `NetworkManagementClient` added operation group `application_security_groups`
  - Client `NetworkManagementClient` added operation group `available_delegations`
  - Client `NetworkManagementClient` added operation group `available_resource_group_delegations`
  - Client `NetworkManagementClient` added operation group `available_service_aliases`
  - Client `NetworkManagementClient` added operation group `azure_firewalls`
  - Client `NetworkManagementClient` added operation group `azure_firewall_fqdn_tags`
  - Client `NetworkManagementClient` added operation group `web_categories`
  - Client `NetworkManagementClient` added operation group `bastion_hosts`
  - Client `NetworkManagementClient` added operation group `network_interfaces`
  - Client `NetworkManagementClient` added operation group `public_ip_addresses`
  - Client `NetworkManagementClient` added operation group `vip_swap`
  - Client `NetworkManagementClient` added operation group `custom_ip_prefixes`
  - Client `NetworkManagementClient` added operation group `ddos_custom_policies`
  - Client `NetworkManagementClient` added operation group `ddos_protection_plans`
  - Client `NetworkManagementClient` added operation group `dscp_configuration`
  - Client `NetworkManagementClient` added operation group `available_endpoint_services`
  - Client `NetworkManagementClient` added operation group `express_route_circuit_authorizations`
  - Client `NetworkManagementClient` added operation group `express_route_circuit_peerings`
  - Client `NetworkManagementClient` added operation group `express_route_circuit_connections`
  - Client `NetworkManagementClient` added operation group `peer_express_route_circuit_connections`
  - Client `NetworkManagementClient` added operation group `express_route_circuits`
  - Client `NetworkManagementClient` added operation group `express_route_service_providers`
  - Client `NetworkManagementClient` added operation group `express_route_cross_connections`
  - Client `NetworkManagementClient` added operation group `express_route_cross_connection_peerings`
  - Client `NetworkManagementClient` added operation group `express_route_ports_locations`
  - Client `NetworkManagementClient` added operation group `express_route_ports`
  - Client `NetworkManagementClient` added operation group `express_route_links`
  - Client `NetworkManagementClient` added operation group `express_route_port_authorizations`
  - Client `NetworkManagementClient` added operation group `express_route_provider_ports_location`
  - Client `NetworkManagementClient` added operation group `firewall_policies`
  - Client `NetworkManagementClient` added operation group `firewall_policy_rule_collection_groups`
  - Client `NetworkManagementClient` added operation group `firewall_policy_idps_signatures`
  - Client `NetworkManagementClient` added operation group `firewall_policy_idps_signatures_overrides`
  - Client `NetworkManagementClient` added operation group `firewall_policy_idps_signatures_filter_values`
  - Client `NetworkManagementClient` added operation group `firewall_policy_drafts`
  - Client `NetworkManagementClient` added operation group `firewall_policy_deployments`
  - Client `NetworkManagementClient` added operation group `firewall_policy_rule_collection_group_drafts`
  - Client `NetworkManagementClient` added operation group `ip_allocations`
  - Client `NetworkManagementClient` added operation group `ip_groups`
  - Client `NetworkManagementClient` added operation group `load_balancers`
  - Client `NetworkManagementClient` added operation group `load_balancer_backend_address_pools`
  - Client `NetworkManagementClient` added operation group `load_balancer_frontend_ip_configurations`
  - Client `NetworkManagementClient` added operation group `inbound_nat_rules`
  - Client `NetworkManagementClient` added operation group `load_balancer_load_balancing_rules`
  - Client `NetworkManagementClient` added operation group `load_balancer_outbound_rules`
  - Client `NetworkManagementClient` added operation group `load_balancer_network_interfaces`
  - Client `NetworkManagementClient` added operation group `load_balancer_probes`
  - Client `NetworkManagementClient` added operation group `nat_gateways`
  - Client `NetworkManagementClient` added operation group `network_interface_ip_configurations`
  - Client `NetworkManagementClient` added operation group `network_interface_load_balancers`
  - Client `NetworkManagementClient` added operation group `network_interface_tap_configurations`
  - Client `NetworkManagementClient` added operation group `network_managers`
  - Client `NetworkManagementClient` added operation group `network_manager_commits`
  - Client `NetworkManagementClient` added operation group `network_manager_deployment_status`
  - Client `NetworkManagementClient` added operation group `subscription_network_manager_connections`
  - Client `NetworkManagementClient` added operation group `management_group_network_manager_connections`
  - Client `NetworkManagementClient` added operation group `connectivity_configurations`
  - Client `NetworkManagementClient` added operation group `network_groups`
  - Client `NetworkManagementClient` added operation group `static_members`
  - Client `NetworkManagementClient` added operation group `scope_connections`
  - Client `NetworkManagementClient` added operation group `security_admin_configurations`
  - Client `NetworkManagementClient` added operation group `admin_rule_collections`
  - Client `NetworkManagementClient` added operation group `admin_rules`
  - Client `NetworkManagementClient` added operation group `security_user_configurations`
  - Client `NetworkManagementClient` added operation group `security_user_rule_collections`
  - Client `NetworkManagementClient` added operation group `security_user_rules`
  - Client `NetworkManagementClient` added operation group `network_manager_routing_configurations`
  - Client `NetworkManagementClient` added operation group `routing_rule_collections`
  - Client `NetworkManagementClient` added operation group `routing_rules`
  - Client `NetworkManagementClient` added operation group `network_profiles`
  - Client `NetworkManagementClient` added operation group `network_security_groups`
  - Client `NetworkManagementClient` added operation group `security_rules`
  - Client `NetworkManagementClient` added operation group `default_security_rules`
  - Client `NetworkManagementClient` added operation group `network_virtual_appliances`
  - Client `NetworkManagementClient` added operation group `virtual_appliance_sites`
  - Client `NetworkManagementClient` added operation group `virtual_appliance_skus`
  - Client `NetworkManagementClient` added operation group `inbound_security_rule`
  - Client `NetworkManagementClient` added operation group `network_watchers`
  - Client `NetworkManagementClient` added operation group `packet_captures`
  - Client `NetworkManagementClient` added operation group `connection_monitors`
  - Client `NetworkManagementClient` added operation group `flow_logs`
  - Client `NetworkManagementClient` added operation group `operations`
  - Client `NetworkManagementClient` added operation group `private_endpoints`
  - Client `NetworkManagementClient` added operation group `available_private_endpoint_types`
  - Client `NetworkManagementClient` added operation group `private_dns_zone_groups`
  - Client `NetworkManagementClient` added operation group `private_link_services`
  - Client `NetworkManagementClient` added operation group `public_ip_prefixes`
  - Client `NetworkManagementClient` added operation group `route_filters`
  - Client `NetworkManagementClient` added operation group `route_filter_rules`
  - Client `NetworkManagementClient` added operation group `route_tables`
  - Client `NetworkManagementClient` added operation group `routes`
  - Client `NetworkManagementClient` added operation group `security_partner_providers`
  - Client `NetworkManagementClient` added operation group `bgp_service_communities`
  - Client `NetworkManagementClient` added operation group `service_endpoint_policies`
  - Client `NetworkManagementClient` added operation group `service_endpoint_policy_definitions`
  - Client `NetworkManagementClient` added operation group `service_tags`
  - Client `NetworkManagementClient` added operation group `service_tag_information`
  - Client `NetworkManagementClient` added operation group `usages`
  - Client `NetworkManagementClient` added operation group `virtual_networks`
  - Client `NetworkManagementClient` added operation group `subnets`
  - Client `NetworkManagementClient` added operation group `resource_navigation_links`
  - Client `NetworkManagementClient` added operation group `service_association_links`
  - Client `NetworkManagementClient` added operation group `virtual_network_peerings`
  - Client `NetworkManagementClient` added operation group `virtual_network_gateways`
  - Client `NetworkManagementClient` added operation group `virtual_network_gateway_connections`
  - Client `NetworkManagementClient` added operation group `local_network_gateways`
  - Client `NetworkManagementClient` added operation group `virtual_network_gateway_nat_rules`
  - Client `NetworkManagementClient` added operation group `virtual_network_taps`
  - Client `NetworkManagementClient` added operation group `virtual_routers`
  - Client `NetworkManagementClient` added operation group `virtual_router_peerings`
  - Client `NetworkManagementClient` added operation group `virtual_wans`
  - Client `NetworkManagementClient` added operation group `vpn_sites`
  - Client `NetworkManagementClient` added operation group `vpn_site_links`
  - Client `NetworkManagementClient` added operation group `vpn_sites_configuration`
  - Client `NetworkManagementClient` added operation group `vpn_server_configurations`
  - Client `NetworkManagementClient` added operation group `configuration_policy_groups`
  - Client `NetworkManagementClient` added operation group `virtual_hubs`
  - Client `NetworkManagementClient` added operation group `route_maps`
  - Client `NetworkManagementClient` added operation group `hub_virtual_network_connections`
  - Client `NetworkManagementClient` added operation group `vpn_gateways`
  - Client `NetworkManagementClient` added operation group `vpn_link_connections`
  - Client `NetworkManagementClient` added operation group `vpn_connections`
  - Client `NetworkManagementClient` added operation group `vpn_site_link_connections`
  - Client `NetworkManagementClient` added operation group `nat_rules`
  - Client `NetworkManagementClient` added operation group `p2_svpn_gateways`
  - Client `NetworkManagementClient` added operation group `vpn_server_configurations_associated_with_virtual_wan`
  - Client `NetworkManagementClient` added operation group `virtual_hub_route_table_v2_s`
  - Client `NetworkManagementClient` added operation group `express_route_gateways`
  - Client `NetworkManagementClient` added operation group `express_route_connections`
  - Client `NetworkManagementClient` added operation group `network_virtual_appliance_connections`
  - Client `NetworkManagementClient` added operation group `virtual_hub_bgp_connection`
  - Client `NetworkManagementClient` added operation group `virtual_hub_bgp_connections`
  - Client `NetworkManagementClient` added operation group `virtual_hub_ip_configuration`
  - Client `NetworkManagementClient` added operation group `hub_route_tables`
  - Client `NetworkManagementClient` added operation group `routing_intent`
  - Client `NetworkManagementClient` added operation group `web_application_firewall_policies`
  - Model `NetworkManagementClient` added property `url`
  - Method `NetworkManagementClient.begin_delete_bastion_shareable_link` has a new overload `def begin_delete_bastion_shareable_link(self: None, resource_group_name: str, bastion_host_name: str, bsl_request: BastionShareableLinkListRequest, content_type: str)`
  - Method `NetworkManagementClient.begin_delete_bastion_shareable_link` has a new overload `def begin_delete_bastion_shareable_link(self: None, resource_group_name: str, bastion_host_name: str, bsl_request: IO[bytes], content_type: str)`
  - Method `NetworkManagementClient.begin_delete_bastion_shareable_link_by_token` has a new overload `def begin_delete_bastion_shareable_link_by_token(self: None, resource_group_name: str, bastion_host_name: str, bsl_token_request: BastionShareableLinkTokenListRequest, content_type: str)`
  - Method `NetworkManagementClient.begin_delete_bastion_shareable_link_by_token` has a new overload `def begin_delete_bastion_shareable_link_by_token(self: None, resource_group_name: str, bastion_host_name: str, bsl_token_request: IO[bytes], content_type: str)`
  - Method `NetworkManagementClient.begin_generatevirtualwanvpnserverconfigurationvpnprofile` has a new overload `def begin_generatevirtualwanvpnserverconfigurationvpnprofile(self: None, resource_group_name: str, virtual_wan_name: str, vpn_client_params: VirtualWanVpnProfileParameters, content_type: str)`
  - Method `NetworkManagementClient.begin_generatevirtualwanvpnserverconfigurationvpnprofile` has a new overload `def begin_generatevirtualwanvpnserverconfigurationvpnprofile(self: None, resource_group_name: str, virtual_wan_name: str, vpn_client_params: IO[bytes], content_type: str)`
  - Method `NetworkManagementClient.begin_put_bastion_shareable_link` has a new overload `def begin_put_bastion_shareable_link(self: None, resource_group_name: str, bastion_host_name: str, bsl_request: BastionShareableLinkListRequest, content_type: str)`
  - Method `NetworkManagementClient.begin_put_bastion_shareable_link` has a new overload `def begin_put_bastion_shareable_link(self: None, resource_group_name: str, bastion_host_name: str, bsl_request: IO[bytes], content_type: str)`
  - Method `NetworkManagementClient.disconnect_active_sessions` has a new overload `def disconnect_active_sessions(self: None, resource_group_name: str, bastion_host_name: str, session_ids: SessionIds, content_type: str)`
  - Method `NetworkManagementClient.disconnect_active_sessions` has a new overload `def disconnect_active_sessions(self: None, resource_group_name: str, bastion_host_name: str, session_ids: IO[bytes], content_type: str)`
  - Method `NetworkManagementClient.get_bastion_shareable_link` has a new overload `def get_bastion_shareable_link(self: None, resource_group_name: str, bastion_host_name: str, bsl_request: BastionShareableLinkListRequest, content_type: str)`
  - Method `NetworkManagementClient.get_bastion_shareable_link` has a new overload `def get_bastion_shareable_link(self: None, resource_group_name: str, bastion_host_name: str, bsl_request: IO[bytes], content_type: str)`
  - Method `NetworkManagementClient.list_active_connectivity_configurations` has a new overload `def list_active_connectivity_configurations(self: None, resource_group_name: str, network_manager_name: str, parameters: ActiveConfigurationParameter, top: Optional[int], content_type: str)`
  - Method `NetworkManagementClient.list_active_connectivity_configurations` has a new overload `def list_active_connectivity_configurations(self: None, resource_group_name: str, network_manager_name: str, parameters: IO[bytes], top: Optional[int], content_type: str)`
  - Method `NetworkManagementClient.list_active_security_admin_rules` has a new overload `def list_active_security_admin_rules(self: None, resource_group_name: str, network_manager_name: str, parameters: ActiveConfigurationParameter, top: Optional[int], content_type: str)`
  - Method `NetworkManagementClient.list_active_security_admin_rules` has a new overload `def list_active_security_admin_rules(self: None, resource_group_name: str, network_manager_name: str, parameters: IO[bytes], top: Optional[int], content_type: str)`
  - Method `NetworkManagementClient.list_network_manager_effective_connectivity_configurations` has a new overload `def list_network_manager_effective_connectivity_configurations(self: None, resource_group_name: str, virtual_network_name: str, parameters: QueryRequestOptions, top: Optional[int], content_type: str)`
  - Method `NetworkManagementClient.list_network_manager_effective_connectivity_configurations` has a new overload `def list_network_manager_effective_connectivity_configurations(self: None, resource_group_name: str, virtual_network_name: str, parameters: IO[bytes], top: Optional[int], content_type: str)`
  - Method `NetworkManagementClient.list_network_manager_effective_security_admin_rules` has a new overload `def list_network_manager_effective_security_admin_rules(self: None, resource_group_name: str, virtual_network_name: str, parameters: QueryRequestOptions, top: Optional[int], content_type: str)`
  - Method `NetworkManagementClient.list_network_manager_effective_security_admin_rules` has a new overload `def list_network_manager_effective_security_admin_rules(self: None, resource_group_name: str, virtual_network_name: str, parameters: IO[bytes], top: Optional[int], content_type: str)`
  - Method `AdminRuleCollectionsOperations.create_or_update` has a new overload `def create_or_update(self: None, resource_group_name: str, network_manager_name: str, configuration_name: str, rule_collection_name: str, rule_collection: AdminRuleCollection, content_type: str)`
  - Method `AdminRuleCollectionsOperations.create_or_update` has a new overload `def create_or_update(self: None, resource_group_name: str, network_manager_name: str, configuration_name: str, rule_collection_name: str, rule_collection: IO[bytes], content_type: str)`
  - Method `AdminRulesOperations.create_or_update` has a new overload `def create_or_update(self: None, resource_group_name: str, network_manager_name: str, configuration_name: str, rule_collection_name: str, rule_name: str, admin_rule: BaseAdminRule, content_type: str)`
  - Method `AdminRulesOperations.create_or_update` has a new overload `def create_or_update(self: None, resource_group_name: str, network_manager_name: str, configuration_name: str, rule_collection_name: str, rule_name: str, admin_rule: IO[bytes], content_type: str)`
  - Method `ApplicationGatewayPrivateEndpointConnectionsOperations.begin_update` has a new overload `def begin_update(self: None, resource_group_name: str, application_gateway_name: str, connection_name: str, parameters: ApplicationGatewayPrivateEndpointConnection, content_type: str)`
  - Method `ApplicationGatewayPrivateEndpointConnectionsOperations.begin_update` has a new overload `def begin_update(self: None, resource_group_name: str, application_gateway_name: str, connection_name: str, parameters: IO[bytes], content_type: str)`
  - Method `ApplicationGatewaysOperations.begin_backend_health_on_demand` has a new overload `def begin_backend_health_on_demand(self: None, resource_group_name: str, application_gateway_name: str, probe_request: ApplicationGatewayOnDemandProbe, expand: Optional[str], content_type: str)`
  - Method `ApplicationGatewaysOperations.begin_backend_health_on_demand` has a new overload `def begin_backend_health_on_demand(self: None, resource_group_name: str, application_gateway_name: str, probe_request: IO[bytes], expand: Optional[str], content_type: str)`
  - Method `ApplicationGatewaysOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, application_gateway_name: str, parameters: ApplicationGateway, content_type: str)`
  - Method `ApplicationGatewaysOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, application_gateway_name: str, parameters: IO[bytes], content_type: str)`
  - Method `ApplicationGatewaysOperations.update_tags` has a new overload `def update_tags(self: None, resource_group_name: str, application_gateway_name: str, parameters: TagsObject, content_type: str)`
  - Method `ApplicationGatewaysOperations.update_tags` has a new overload `def update_tags(self: None, resource_group_name: str, application_gateway_name: str, parameters: IO[bytes], content_type: str)`
  - Method `ApplicationSecurityGroupsOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, application_security_group_name: str, parameters: ApplicationSecurityGroup, content_type: str)`
  - Method `ApplicationSecurityGroupsOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, application_security_group_name: str, parameters: IO[bytes], content_type: str)`
  - Method `ApplicationSecurityGroupsOperations.update_tags` has a new overload `def update_tags(self: None, resource_group_name: str, application_security_group_name: str, parameters: TagsObject, content_type: str)`
  - Method `ApplicationSecurityGroupsOperations.update_tags` has a new overload `def update_tags(self: None, resource_group_name: str, application_security_group_name: str, parameters: IO[bytes], content_type: str)`
  - Method `AzureFirewallsOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, azure_firewall_name: str, parameters: AzureFirewall, content_type: str)`
  - Method `AzureFirewallsOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, azure_firewall_name: str, parameters: IO[bytes], content_type: str)`
  - Method `AzureFirewallsOperations.begin_packet_capture` has a new overload `def begin_packet_capture(self: None, resource_group_name: str, azure_firewall_name: str, parameters: FirewallPacketCaptureParameters, content_type: str)`
  - Method `AzureFirewallsOperations.begin_packet_capture` has a new overload `def begin_packet_capture(self: None, resource_group_name: str, azure_firewall_name: str, parameters: IO[bytes], content_type: str)`
  - Method `AzureFirewallsOperations.begin_update_tags` has a new overload `def begin_update_tags(self: None, resource_group_name: str, azure_firewall_name: str, parameters: TagsObject, content_type: str)`
  - Method `AzureFirewallsOperations.begin_update_tags` has a new overload `def begin_update_tags(self: None, resource_group_name: str, azure_firewall_name: str, parameters: IO[bytes], content_type: str)`
  - Method `BastionHostsOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, bastion_host_name: str, parameters: BastionHost, content_type: str)`
  - Method `BastionHostsOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, bastion_host_name: str, parameters: IO[bytes], content_type: str)`
  - Method `BastionHostsOperations.begin_update_tags` has a new overload `def begin_update_tags(self: None, resource_group_name: str, bastion_host_name: str, parameters: TagsObject, content_type: str)`
  - Method `BastionHostsOperations.begin_update_tags` has a new overload `def begin_update_tags(self: None, resource_group_name: str, bastion_host_name: str, parameters: IO[bytes], content_type: str)`
  - Method `ConfigurationPolicyGroupsOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, vpn_server_configuration_name: str, configuration_policy_group_name: str, vpn_server_configuration_policy_group_parameters: VpnServerConfigurationPolicyGroup, content_type: str)`
  - Method `ConfigurationPolicyGroupsOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, vpn_server_configuration_name: str, configuration_policy_group_name: str, vpn_server_configuration_policy_group_parameters: IO[bytes], content_type: str)`
  - Method `ConnectionMonitorsOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, network_watcher_name: str, connection_monitor_name: str, parameters: ConnectionMonitor, migrate: Optional[str], content_type: str)`
  - Method `ConnectionMonitorsOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, network_watcher_name: str, connection_monitor_name: str, parameters: IO[bytes], migrate: Optional[str], content_type: str)`
  - Method `ConnectionMonitorsOperations.update_tags` has a new overload `def update_tags(self: None, resource_group_name: str, network_watcher_name: str, connection_monitor_name: str, parameters: TagsObject, content_type: str)`
  - Method `ConnectionMonitorsOperations.update_tags` has a new overload `def update_tags(self: None, resource_group_name: str, network_watcher_name: str, connection_monitor_name: str, parameters: IO[bytes], content_type: str)`
  - Method `ConnectivityConfigurationsOperations.create_or_update` has a new overload `def create_or_update(self: None, resource_group_name: str, network_manager_name: str, configuration_name: str, connectivity_configuration: ConnectivityConfiguration, content_type: str)`
  - Method `ConnectivityConfigurationsOperations.create_or_update` has a new overload `def create_or_update(self: None, resource_group_name: str, network_manager_name: str, configuration_name: str, connectivity_configuration: IO[bytes], content_type: str)`
  - Method `CustomIPPrefixesOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, custom_ip_prefix_name: str, parameters: CustomIpPrefix, content_type: str)`
  - Method `CustomIPPrefixesOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, custom_ip_prefix_name: str, parameters: IO[bytes], content_type: str)`
  - Method `CustomIPPrefixesOperations.update_tags` has a new overload `def update_tags(self: None, resource_group_name: str, custom_ip_prefix_name: str, parameters: TagsObject, content_type: str)`
  - Method `CustomIPPrefixesOperations.update_tags` has a new overload `def update_tags(self: None, resource_group_name: str, custom_ip_prefix_name: str, parameters: IO[bytes], content_type: str)`
  - Method `DdosCustomPoliciesOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, ddos_custom_policy_name: str, parameters: DdosCustomPolicy, content_type: str)`
  - Method `DdosCustomPoliciesOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, ddos_custom_policy_name: str, parameters: IO[bytes], content_type: str)`
  - Method `DdosCustomPoliciesOperations.update_tags` has a new overload `def update_tags(self: None, resource_group_name: str, ddos_custom_policy_name: str, parameters: TagsObject, content_type: str)`
  - Method `DdosCustomPoliciesOperations.update_tags` has a new overload `def update_tags(self: None, resource_group_name: str, ddos_custom_policy_name: str, parameters: IO[bytes], content_type: str)`
  - Method `DdosProtectionPlansOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, ddos_protection_plan_name: str, parameters: DdosProtectionPlan, content_type: str)`
  - Method `DdosProtectionPlansOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, ddos_protection_plan_name: str, parameters: IO[bytes], content_type: str)`
  - Method `DdosProtectionPlansOperations.update_tags` has a new overload `def update_tags(self: None, resource_group_name: str, ddos_protection_plan_name: str, parameters: TagsObject, content_type: str)`
  - Method `DdosProtectionPlansOperations.update_tags` has a new overload `def update_tags(self: None, resource_group_name: str, ddos_protection_plan_name: str, parameters: IO[bytes], content_type: str)`
  - Method `DscpConfigurationOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, dscp_configuration_name: str, parameters: DscpConfiguration, content_type: str)`
  - Method `DscpConfigurationOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, dscp_configuration_name: str, parameters: IO[bytes], content_type: str)`
  - Method `ExpressRouteCircuitAuthorizationsOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, circuit_name: str, authorization_name: str, authorization_parameters: ExpressRouteCircuitAuthorization, content_type: str)`
  - Method `ExpressRouteCircuitAuthorizationsOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, circuit_name: str, authorization_name: str, authorization_parameters: IO[bytes], content_type: str)`
  - Method `ExpressRouteCircuitConnectionsOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, circuit_name: str, peering_name: str, connection_name: str, express_route_circuit_connection_parameters: ExpressRouteCircuitConnection, content_type: str)`
  - Method `ExpressRouteCircuitConnectionsOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, circuit_name: str, peering_name: str, connection_name: str, express_route_circuit_connection_parameters: IO[bytes], content_type: str)`
  - Method `ExpressRouteCircuitPeeringsOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, circuit_name: str, peering_name: str, peering_parameters: ExpressRouteCircuitPeering, content_type: str)`
  - Method `ExpressRouteCircuitPeeringsOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, circuit_name: str, peering_name: str, peering_parameters: IO[bytes], content_type: str)`
  - Method `ExpressRouteCircuitsOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, circuit_name: str, parameters: ExpressRouteCircuit, content_type: str)`
  - Method `ExpressRouteCircuitsOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, circuit_name: str, parameters: IO[bytes], content_type: str)`
  - Method `ExpressRouteCircuitsOperations.update_tags` has a new overload `def update_tags(self: None, resource_group_name: str, circuit_name: str, parameters: TagsObject, content_type: str)`
  - Method `ExpressRouteCircuitsOperations.update_tags` has a new overload `def update_tags(self: None, resource_group_name: str, circuit_name: str, parameters: IO[bytes], content_type: str)`
  - Method `ExpressRouteConnectionsOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, express_route_gateway_name: str, connection_name: str, put_express_route_connection_parameters: ExpressRouteConnection, content_type: str)`
  - Method `ExpressRouteConnectionsOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, express_route_gateway_name: str, connection_name: str, put_express_route_connection_parameters: IO[bytes], content_type: str)`
  - Method `ExpressRouteCrossConnectionPeeringsOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, cross_connection_name: str, peering_name: str, peering_parameters: ExpressRouteCrossConnectionPeering, content_type: str)`
  - Method `ExpressRouteCrossConnectionPeeringsOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, cross_connection_name: str, peering_name: str, peering_parameters: IO[bytes], content_type: str)`
  - Method `ExpressRouteCrossConnectionsOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, cross_connection_name: str, parameters: ExpressRouteCrossConnection, content_type: str)`
  - Method `ExpressRouteCrossConnectionsOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, cross_connection_name: str, parameters: IO[bytes], content_type: str)`
  - Method `ExpressRouteCrossConnectionsOperations.update_tags` has a new overload `def update_tags(self: None, resource_group_name: str, cross_connection_name: str, cross_connection_parameters: TagsObject, content_type: str)`
  - Method `ExpressRouteCrossConnectionsOperations.update_tags` has a new overload `def update_tags(self: None, resource_group_name: str, cross_connection_name: str, cross_connection_parameters: IO[bytes], content_type: str)`
  - Method `ExpressRouteGatewaysOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, express_route_gateway_name: str, put_express_route_gateway_parameters: ExpressRouteGateway, content_type: str)`
  - Method `ExpressRouteGatewaysOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, express_route_gateway_name: str, put_express_route_gateway_parameters: IO[bytes], content_type: str)`
  - Method `ExpressRouteGatewaysOperations.begin_update_tags` has a new overload `def begin_update_tags(self: None, resource_group_name: str, express_route_gateway_name: str, express_route_gateway_parameters: TagsObject, content_type: str)`
  - Method `ExpressRouteGatewaysOperations.begin_update_tags` has a new overload `def begin_update_tags(self: None, resource_group_name: str, express_route_gateway_name: str, express_route_gateway_parameters: IO[bytes], content_type: str)`
  - Method `ExpressRoutePortAuthorizationsOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, express_route_port_name: str, authorization_name: str, authorization_parameters: ExpressRoutePortAuthorization, content_type: str)`
  - Method `ExpressRoutePortAuthorizationsOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, express_route_port_name: str, authorization_name: str, authorization_parameters: IO[bytes], content_type: str)`
  - Method `ExpressRoutePortsOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, express_route_port_name: str, parameters: ExpressRoutePort, content_type: str)`
  - Method `ExpressRoutePortsOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, express_route_port_name: str, parameters: IO[bytes], content_type: str)`
  - Method `ExpressRoutePortsOperations.generate_loa` has a new overload `def generate_loa(self: None, resource_group_name: str, express_route_port_name: str, request: GenerateExpressRoutePortsLOARequest, content_type: str)`
  - Method `ExpressRoutePortsOperations.generate_loa` has a new overload `def generate_loa(self: None, resource_group_name: str, express_route_port_name: str, request: IO[bytes], content_type: str)`
  - Method `ExpressRoutePortsOperations.update_tags` has a new overload `def update_tags(self: None, resource_group_name: str, express_route_port_name: str, parameters: TagsObject, content_type: str)`
  - Method `ExpressRoutePortsOperations.update_tags` has a new overload `def update_tags(self: None, resource_group_name: str, express_route_port_name: str, parameters: IO[bytes], content_type: str)`
  - Method `FirewallPoliciesOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, firewall_policy_name: str, parameters: FirewallPolicy, content_type: str)`
  - Method `FirewallPoliciesOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, firewall_policy_name: str, parameters: IO[bytes], content_type: str)`
  - Method `FirewallPoliciesOperations.update_tags` has a new overload `def update_tags(self: None, resource_group_name: str, firewall_policy_name: str, parameters: TagsObject, content_type: str)`
  - Method `FirewallPoliciesOperations.update_tags` has a new overload `def update_tags(self: None, resource_group_name: str, firewall_policy_name: str, parameters: IO[bytes], content_type: str)`
  - Method `FirewallPolicyDraftsOperations.create_or_update` has a new overload `def create_or_update(self: None, resource_group_name: str, firewall_policy_name: str, parameters: FirewallPolicyDraft, content_type: str)`
  - Method `FirewallPolicyDraftsOperations.create_or_update` has a new overload `def create_or_update(self: None, resource_group_name: str, firewall_policy_name: str, parameters: IO[bytes], content_type: str)`
  - Method `FirewallPolicyIdpsSignaturesFilterValuesOperations.list` has a new overload `def list(self: None, resource_group_name: str, firewall_policy_name: str, parameters: SignatureOverridesFilterValuesQuery, content_type: str)`
  - Method `FirewallPolicyIdpsSignaturesFilterValuesOperations.list` has a new overload `def list(self: None, resource_group_name: str, firewall_policy_name: str, parameters: IO[bytes], content_type: str)`
  - Method `FirewallPolicyIdpsSignaturesOperations.list` has a new overload `def list(self: None, resource_group_name: str, firewall_policy_name: str, parameters: IDPSQueryObject, content_type: str)`
  - Method `FirewallPolicyIdpsSignaturesOperations.list` has a new overload `def list(self: None, resource_group_name: str, firewall_policy_name: str, parameters: IO[bytes], content_type: str)`
  - Method `FirewallPolicyIdpsSignaturesOverridesOperations.patch` has a new overload `def patch(self: None, resource_group_name: str, firewall_policy_name: str, parameters: SignaturesOverrides, content_type: str)`
  - Method `FirewallPolicyIdpsSignaturesOverridesOperations.patch` has a new overload `def patch(self: None, resource_group_name: str, firewall_policy_name: str, parameters: IO[bytes], content_type: str)`
  - Method `FirewallPolicyIdpsSignaturesOverridesOperations.put` has a new overload `def put(self: None, resource_group_name: str, firewall_policy_name: str, parameters: SignaturesOverrides, content_type: str)`
  - Method `FirewallPolicyIdpsSignaturesOverridesOperations.put` has a new overload `def put(self: None, resource_group_name: str, firewall_policy_name: str, parameters: IO[bytes], content_type: str)`
  - Method `FirewallPolicyRuleCollectionGroupDraftsOperations.create_or_update` has a new overload `def create_or_update(self: None, resource_group_name: str, firewall_policy_name: str, rule_collection_group_name: str, parameters: FirewallPolicyRuleCollectionGroupDraft, content_type: str)`
  - Method `FirewallPolicyRuleCollectionGroupDraftsOperations.create_or_update` has a new overload `def create_or_update(self: None, resource_group_name: str, firewall_policy_name: str, rule_collection_group_name: str, parameters: IO[bytes], content_type: str)`
  - Method `FirewallPolicyRuleCollectionGroupsOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, firewall_policy_name: str, rule_collection_group_name: str, parameters: FirewallPolicyRuleCollectionGroup, content_type: str)`
  - Method `FirewallPolicyRuleCollectionGroupsOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, firewall_policy_name: str, rule_collection_group_name: str, parameters: IO[bytes], content_type: str)`
  - Method `FlowLogsOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, network_watcher_name: str, flow_log_name: str, parameters: FlowLog, content_type: str)`
  - Method `FlowLogsOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, network_watcher_name: str, flow_log_name: str, parameters: IO[bytes], content_type: str)`
  - Method `FlowLogsOperations.update_tags` has a new overload `def update_tags(self: None, resource_group_name: str, network_watcher_name: str, flow_log_name: str, parameters: TagsObject, content_type: str)`
  - Method `FlowLogsOperations.update_tags` has a new overload `def update_tags(self: None, resource_group_name: str, network_watcher_name: str, flow_log_name: str, parameters: IO[bytes], content_type: str)`
  - Method `HubRouteTablesOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, virtual_hub_name: str, route_table_name: str, route_table_parameters: HubRouteTable, content_type: str)`
  - Method `HubRouteTablesOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, virtual_hub_name: str, route_table_name: str, route_table_parameters: IO[bytes], content_type: str)`
  - Method `HubVirtualNetworkConnectionsOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, virtual_hub_name: str, connection_name: str, hub_virtual_network_connection_parameters: HubVirtualNetworkConnection, content_type: str)`
  - Method `HubVirtualNetworkConnectionsOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, virtual_hub_name: str, connection_name: str, hub_virtual_network_connection_parameters: IO[bytes], content_type: str)`
  - Method `InboundNatRulesOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, load_balancer_name: str, inbound_nat_rule_name: str, inbound_nat_rule_parameters: InboundNatRule, content_type: str)`
  - Method `InboundNatRulesOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, load_balancer_name: str, inbound_nat_rule_name: str, inbound_nat_rule_parameters: IO[bytes], content_type: str)`
  - Method `InboundSecurityRuleOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, network_virtual_appliance_name: str, rule_collection_name: str, parameters: InboundSecurityRule, content_type: str)`
  - Method `InboundSecurityRuleOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, network_virtual_appliance_name: str, rule_collection_name: str, parameters: IO[bytes], content_type: str)`
  - Method `IpAllocationsOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, ip_allocation_name: str, parameters: IpAllocation, content_type: str)`
  - Method `IpAllocationsOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, ip_allocation_name: str, parameters: IO[bytes], content_type: str)`
  - Method `IpAllocationsOperations.update_tags` has a new overload `def update_tags(self: None, resource_group_name: str, ip_allocation_name: str, parameters: TagsObject, content_type: str)`
  - Method `IpAllocationsOperations.update_tags` has a new overload `def update_tags(self: None, resource_group_name: str, ip_allocation_name: str, parameters: IO[bytes], content_type: str)`
  - Method `IpGroupsOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, ip_groups_name: str, parameters: IpGroup, content_type: str)`
  - Method `IpGroupsOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, ip_groups_name: str, parameters: IO[bytes], content_type: str)`
  - Method `IpGroupsOperations.update_groups` has a new overload `def update_groups(self: None, resource_group_name: str, ip_groups_name: str, parameters: TagsObject, content_type: str)`
  - Method `IpGroupsOperations.update_groups` has a new overload `def update_groups(self: None, resource_group_name: str, ip_groups_name: str, parameters: IO[bytes], content_type: str)`
  - Method `LoadBalancerBackendAddressPoolsOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, load_balancer_name: str, backend_address_pool_name: str, parameters: BackendAddressPool, content_type: str)`
  - Method `LoadBalancerBackendAddressPoolsOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, load_balancer_name: str, backend_address_pool_name: str, parameters: IO[bytes], content_type: str)`
  - Method `LoadBalancersOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, load_balancer_name: str, parameters: LoadBalancer, content_type: str)`
  - Method `LoadBalancersOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, load_balancer_name: str, parameters: IO[bytes], content_type: str)`
  - Method `LoadBalancersOperations.begin_list_inbound_nat_rule_port_mappings` has a new overload `def begin_list_inbound_nat_rule_port_mappings(self: None, group_name: str, load_balancer_name: str, backend_pool_name: str, parameters: QueryInboundNatRulePortMappingRequest, content_type: str)`
  - Method `LoadBalancersOperations.begin_list_inbound_nat_rule_port_mappings` has a new overload `def begin_list_inbound_nat_rule_port_mappings(self: None, group_name: str, load_balancer_name: str, backend_pool_name: str, parameters: IO[bytes], content_type: str)`
  - Method `LoadBalancersOperations.begin_swap_public_ip_addresses` has a new overload `def begin_swap_public_ip_addresses(self: None, location: str, parameters: LoadBalancerVipSwapRequest, content_type: str)`
  - Method `LoadBalancersOperations.begin_swap_public_ip_addresses` has a new overload `def begin_swap_public_ip_addresses(self: None, location: str, parameters: IO[bytes], content_type: str)`
  - Method `LoadBalancersOperations.migrate_to_ip_based` has a new overload `def migrate_to_ip_based(self: None, group_name: str, load_balancer_name: str, parameters: Optional[MigrateLoadBalancerToIpBasedRequest], content_type: str)`
  - Method `LoadBalancersOperations.migrate_to_ip_based` has a new overload `def migrate_to_ip_based(self: None, group_name: str, load_balancer_name: str, parameters: Optional[IO[bytes]], content_type: str)`
  - Method `LoadBalancersOperations.update_tags` has a new overload `def update_tags(self: None, resource_group_name: str, load_balancer_name: str, parameters: TagsObject, content_type: str)`
  - Method `LoadBalancersOperations.update_tags` has a new overload `def update_tags(self: None, resource_group_name: str, load_balancer_name: str, parameters: IO[bytes], content_type: str)`
  - Method `LocalNetworkGatewaysOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, local_network_gateway_name: str, parameters: LocalNetworkGateway, content_type: str)`
  - Method `LocalNetworkGatewaysOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, local_network_gateway_name: str, parameters: IO[bytes], content_type: str)`
  - Method `LocalNetworkGatewaysOperations.update_tags` has a new overload `def update_tags(self: None, resource_group_name: str, local_network_gateway_name: str, parameters: TagsObject, content_type: str)`
  - Method `LocalNetworkGatewaysOperations.update_tags` has a new overload `def update_tags(self: None, resource_group_name: str, local_network_gateway_name: str, parameters: IO[bytes], content_type: str)`
  - Method `ManagementGroupNetworkManagerConnectionsOperations.create_or_update` has a new overload `def create_or_update(self: None, management_group_id: str, network_manager_connection_name: str, parameters: NetworkManagerConnection, content_type: str)`
  - Method `ManagementGroupNetworkManagerConnectionsOperations.create_or_update` has a new overload `def create_or_update(self: None, management_group_id: str, network_manager_connection_name: str, parameters: IO[bytes], content_type: str)`
  - Method `NatGatewaysOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, nat_gateway_name: str, parameters: NatGateway, content_type: str)`
  - Method `NatGatewaysOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, nat_gateway_name: str, parameters: IO[bytes], content_type: str)`
  - Method `NatGatewaysOperations.update_tags` has a new overload `def update_tags(self: None, resource_group_name: str, nat_gateway_name: str, parameters: TagsObject, content_type: str)`
  - Method `NatGatewaysOperations.update_tags` has a new overload `def update_tags(self: None, resource_group_name: str, nat_gateway_name: str, parameters: IO[bytes], content_type: str)`
  - Method `NatRulesOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, gateway_name: str, nat_rule_name: str, nat_rule_parameters: VpnGatewayNatRule, content_type: str)`
  - Method `NatRulesOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, gateway_name: str, nat_rule_name: str, nat_rule_parameters: IO[bytes], content_type: str)`
  - Method `NetworkGroupsOperations.create_or_update` has a new overload `def create_or_update(self: None, resource_group_name: str, network_manager_name: str, network_group_name: str, parameters: NetworkGroup, if_match: Optional[str], content_type: str)`
  - Method `NetworkGroupsOperations.create_or_update` has a new overload `def create_or_update(self: None, resource_group_name: str, network_manager_name: str, network_group_name: str, parameters: IO[bytes], if_match: Optional[str], content_type: str)`
  - Method `NetworkInterfaceTapConfigurationsOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, network_interface_name: str, tap_configuration_name: str, tap_configuration_parameters: NetworkInterfaceTapConfiguration, content_type: str)`
  - Method `NetworkInterfaceTapConfigurationsOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, network_interface_name: str, tap_configuration_name: str, tap_configuration_parameters: IO[bytes], content_type: str)`
  - Method `NetworkInterfacesOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, network_interface_name: str, parameters: NetworkInterface, content_type: str)`
  - Method `NetworkInterfacesOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, network_interface_name: str, parameters: IO[bytes], content_type: str)`
  - Method `NetworkInterfacesOperations.update_tags` has a new overload `def update_tags(self: None, resource_group_name: str, network_interface_name: str, parameters: TagsObject, content_type: str)`
  - Method `NetworkInterfacesOperations.update_tags` has a new overload `def update_tags(self: None, resource_group_name: str, network_interface_name: str, parameters: IO[bytes], content_type: str)`
  - Method `NetworkManagementClientOperationsMixin.begin_delete_bastion_shareable_link` has a new overload `def begin_delete_bastion_shareable_link(self: None, resource_group_name: str, bastion_host_name: str, bsl_request: BastionShareableLinkListRequest, content_type: str)`
  - Method `NetworkManagementClientOperationsMixin.begin_delete_bastion_shareable_link` has a new overload `def begin_delete_bastion_shareable_link(self: None, resource_group_name: str, bastion_host_name: str, bsl_request: IO[bytes], content_type: str)`
  - Method `NetworkManagementClientOperationsMixin.begin_delete_bastion_shareable_link_by_token` has a new overload `def begin_delete_bastion_shareable_link_by_token(self: None, resource_group_name: str, bastion_host_name: str, bsl_token_request: BastionShareableLinkTokenListRequest, content_type: str)`
  - Method `NetworkManagementClientOperationsMixin.begin_delete_bastion_shareable_link_by_token` has a new overload `def begin_delete_bastion_shareable_link_by_token(self: None, resource_group_name: str, bastion_host_name: str, bsl_token_request: IO[bytes], content_type: str)`
  - Method `NetworkManagementClientOperationsMixin.begin_generatevirtualwanvpnserverconfigurationvpnprofile` has a new overload `def begin_generatevirtualwanvpnserverconfigurationvpnprofile(self: None, resource_group_name: str, virtual_wan_name: str, vpn_client_params: VirtualWanVpnProfileParameters, content_type: str)`
  - Method `NetworkManagementClientOperationsMixin.begin_generatevirtualwanvpnserverconfigurationvpnprofile` has a new overload `def begin_generatevirtualwanvpnserverconfigurationvpnprofile(self: None, resource_group_name: str, virtual_wan_name: str, vpn_client_params: IO[bytes], content_type: str)`
  - Method `NetworkManagementClientOperationsMixin.begin_put_bastion_shareable_link` has a new overload `def begin_put_bastion_shareable_link(self: None, resource_group_name: str, bastion_host_name: str, bsl_request: BastionShareableLinkListRequest, content_type: str)`
  - Method `NetworkManagementClientOperationsMixin.begin_put_bastion_shareable_link` has a new overload `def begin_put_bastion_shareable_link(self: None, resource_group_name: str, bastion_host_name: str, bsl_request: IO[bytes], content_type: str)`
  - Method `NetworkManagementClientOperationsMixin.disconnect_active_sessions` has a new overload `def disconnect_active_sessions(self: None, resource_group_name: str, bastion_host_name: str, session_ids: SessionIds, content_type: str)`
  - Method `NetworkManagementClientOperationsMixin.disconnect_active_sessions` has a new overload `def disconnect_active_sessions(self: None, resource_group_name: str, bastion_host_name: str, session_ids: IO[bytes], content_type: str)`
  - Method `NetworkManagementClientOperationsMixin.get_bastion_shareable_link` has a new overload `def get_bastion_shareable_link(self: None, resource_group_name: str, bastion_host_name: str, bsl_request: BastionShareableLinkListRequest, content_type: str)`
  - Method `NetworkManagementClientOperationsMixin.get_bastion_shareable_link` has a new overload `def get_bastion_shareable_link(self: None, resource_group_name: str, bastion_host_name: str, bsl_request: IO[bytes], content_type: str)`
  - Method `NetworkManagementClientOperationsMixin.list_active_connectivity_configurations` has a new overload `def list_active_connectivity_configurations(self: None, resource_group_name: str, network_manager_name: str, parameters: ActiveConfigurationParameter, top: Optional[int], content_type: str)`
  - Method `NetworkManagementClientOperationsMixin.list_active_connectivity_configurations` has a new overload `def list_active_connectivity_configurations(self: None, resource_group_name: str, network_manager_name: str, parameters: IO[bytes], top: Optional[int], content_type: str)`
  - Method `NetworkManagementClientOperationsMixin.list_active_security_admin_rules` has a new overload `def list_active_security_admin_rules(self: None, resource_group_name: str, network_manager_name: str, parameters: ActiveConfigurationParameter, top: Optional[int], content_type: str)`
  - Method `NetworkManagementClientOperationsMixin.list_active_security_admin_rules` has a new overload `def list_active_security_admin_rules(self: None, resource_group_name: str, network_manager_name: str, parameters: IO[bytes], top: Optional[int], content_type: str)`
  - Method `NetworkManagementClientOperationsMixin.list_network_manager_effective_connectivity_configurations` has a new overload `def list_network_manager_effective_connectivity_configurations(self: None, resource_group_name: str, virtual_network_name: str, parameters: QueryRequestOptions, top: Optional[int], content_type: str)`
  - Method `NetworkManagementClientOperationsMixin.list_network_manager_effective_connectivity_configurations` has a new overload `def list_network_manager_effective_connectivity_configurations(self: None, resource_group_name: str, virtual_network_name: str, parameters: IO[bytes], top: Optional[int], content_type: str)`
  - Method `NetworkManagementClientOperationsMixin.list_network_manager_effective_security_admin_rules` has a new overload `def list_network_manager_effective_security_admin_rules(self: None, resource_group_name: str, virtual_network_name: str, parameters: QueryRequestOptions, top: Optional[int], content_type: str)`
  - Method `NetworkManagementClientOperationsMixin.list_network_manager_effective_security_admin_rules` has a new overload `def list_network_manager_effective_security_admin_rules(self: None, resource_group_name: str, virtual_network_name: str, parameters: IO[bytes], top: Optional[int], content_type: str)`
  - Method `NetworkManagerCommitsOperations.begin_post` has a new overload `def begin_post(self: None, resource_group_name: str, network_manager_name: str, parameters: NetworkManagerCommit, content_type: str)`
  - Method `NetworkManagerCommitsOperations.begin_post` has a new overload `def begin_post(self: None, resource_group_name: str, network_manager_name: str, parameters: IO[bytes], content_type: str)`
  - Method `NetworkManagerDeploymentStatusOperations.list` has a new overload `def list(self: None, resource_group_name: str, network_manager_name: str, parameters: NetworkManagerDeploymentStatusParameter, top: Optional[int], content_type: str)`
  - Method `NetworkManagerDeploymentStatusOperations.list` has a new overload `def list(self: None, resource_group_name: str, network_manager_name: str, parameters: IO[bytes], top: Optional[int], content_type: str)`
  - Method `NetworkManagerRoutingConfigurationsOperations.create_or_update` has a new overload `def create_or_update(self: None, resource_group_name: str, network_manager_name: str, configuration_name: str, routing_configuration: NetworkManagerRoutingConfiguration, content_type: str)`
  - Method `NetworkManagerRoutingConfigurationsOperations.create_or_update` has a new overload `def create_or_update(self: None, resource_group_name: str, network_manager_name: str, configuration_name: str, routing_configuration: IO[bytes], content_type: str)`
  - Method `NetworkManagersOperations.create_or_update` has a new overload `def create_or_update(self: None, resource_group_name: str, network_manager_name: str, parameters: NetworkManager, content_type: str)`
  - Method `NetworkManagersOperations.create_or_update` has a new overload `def create_or_update(self: None, resource_group_name: str, network_manager_name: str, parameters: IO[bytes], content_type: str)`
  - Method `NetworkManagersOperations.patch` has a new overload `def patch(self: None, resource_group_name: str, network_manager_name: str, parameters: PatchObject, content_type: str)`
  - Method `NetworkManagersOperations.patch` has a new overload `def patch(self: None, resource_group_name: str, network_manager_name: str, parameters: IO[bytes], content_type: str)`
  - Method `NetworkProfilesOperations.create_or_update` has a new overload `def create_or_update(self: None, resource_group_name: str, network_profile_name: str, parameters: NetworkProfile, content_type: str)`
  - Method `NetworkProfilesOperations.create_or_update` has a new overload `def create_or_update(self: None, resource_group_name: str, network_profile_name: str, parameters: IO[bytes], content_type: str)`
  - Method `NetworkProfilesOperations.update_tags` has a new overload `def update_tags(self: None, resource_group_name: str, network_profile_name: str, parameters: TagsObject, content_type: str)`
  - Method `NetworkProfilesOperations.update_tags` has a new overload `def update_tags(self: None, resource_group_name: str, network_profile_name: str, parameters: IO[bytes], content_type: str)`
  - Method `NetworkSecurityGroupsOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, network_security_group_name: str, parameters: NetworkSecurityGroup, content_type: str)`
  - Method `NetworkSecurityGroupsOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, network_security_group_name: str, parameters: IO[bytes], content_type: str)`
  - Method `NetworkSecurityGroupsOperations.update_tags` has a new overload `def update_tags(self: None, resource_group_name: str, network_security_group_name: str, parameters: TagsObject, content_type: str)`
  - Method `NetworkSecurityGroupsOperations.update_tags` has a new overload `def update_tags(self: None, resource_group_name: str, network_security_group_name: str, parameters: IO[bytes], content_type: str)`
  - Method `NetworkVirtualApplianceConnectionsOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, network_virtual_appliance_name: str, connection_name: str, network_virtual_appliance_connection_parameters: NetworkVirtualApplianceConnection, content_type: str)`
  - Method `NetworkVirtualApplianceConnectionsOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, network_virtual_appliance_name: str, connection_name: str, network_virtual_appliance_connection_parameters: IO[bytes], content_type: str)`
  - Method `NetworkVirtualAppliancesOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, network_virtual_appliance_name: str, parameters: NetworkVirtualAppliance, content_type: str)`
  - Method `NetworkVirtualAppliancesOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, network_virtual_appliance_name: str, parameters: IO[bytes], content_type: str)`
  - Method `NetworkVirtualAppliancesOperations.begin_restart` has a new overload `def begin_restart(self: None, resource_group_name: str, network_virtual_appliance_name: str, network_virtual_appliance_instance_ids: Optional[NetworkVirtualApplianceInstanceIds], content_type: str)`
  - Method `NetworkVirtualAppliancesOperations.begin_restart` has a new overload `def begin_restart(self: None, resource_group_name: str, network_virtual_appliance_name: str, network_virtual_appliance_instance_ids: Optional[IO[bytes]], content_type: str)`
  - Method `NetworkVirtualAppliancesOperations.update_tags` has a new overload `def update_tags(self: None, resource_group_name: str, network_virtual_appliance_name: str, parameters: TagsObject, content_type: str)`
  - Method `NetworkVirtualAppliancesOperations.update_tags` has a new overload `def update_tags(self: None, resource_group_name: str, network_virtual_appliance_name: str, parameters: IO[bytes], content_type: str)`
  - Method `NetworkWatchersOperations.begin_check_connectivity` has a new overload `def begin_check_connectivity(self: None, resource_group_name: str, network_watcher_name: str, parameters: ConnectivityParameters, content_type: str)`
  - Method `NetworkWatchersOperations.begin_check_connectivity` has a new overload `def begin_check_connectivity(self: None, resource_group_name: str, network_watcher_name: str, parameters: IO[bytes], content_type: str)`
  - Method `NetworkWatchersOperations.begin_get_azure_reachability_report` has a new overload `def begin_get_azure_reachability_report(self: None, resource_group_name: str, network_watcher_name: str, parameters: AzureReachabilityReportParameters, content_type: str)`
  - Method `NetworkWatchersOperations.begin_get_azure_reachability_report` has a new overload `def begin_get_azure_reachability_report(self: None, resource_group_name: str, network_watcher_name: str, parameters: IO[bytes], content_type: str)`
  - Method `NetworkWatchersOperations.begin_get_flow_log_status` has a new overload `def begin_get_flow_log_status(self: None, resource_group_name: str, network_watcher_name: str, parameters: FlowLogStatusParameters, content_type: str)`
  - Method `NetworkWatchersOperations.begin_get_flow_log_status` has a new overload `def begin_get_flow_log_status(self: None, resource_group_name: str, network_watcher_name: str, parameters: IO[bytes], content_type: str)`
  - Method `NetworkWatchersOperations.begin_get_network_configuration_diagnostic` has a new overload `def begin_get_network_configuration_diagnostic(self: None, resource_group_name: str, network_watcher_name: str, parameters: NetworkConfigurationDiagnosticParameters, content_type: str)`
  - Method `NetworkWatchersOperations.begin_get_network_configuration_diagnostic` has a new overload `def begin_get_network_configuration_diagnostic(self: None, resource_group_name: str, network_watcher_name: str, parameters: IO[bytes], content_type: str)`
  - Method `NetworkWatchersOperations.begin_get_next_hop` has a new overload `def begin_get_next_hop(self: None, resource_group_name: str, network_watcher_name: str, parameters: NextHopParameters, content_type: str)`
  - Method `NetworkWatchersOperations.begin_get_next_hop` has a new overload `def begin_get_next_hop(self: None, resource_group_name: str, network_watcher_name: str, parameters: IO[bytes], content_type: str)`
  - Method `NetworkWatchersOperations.begin_get_troubleshooting` has a new overload `def begin_get_troubleshooting(self: None, resource_group_name: str, network_watcher_name: str, parameters: TroubleshootingParameters, content_type: str)`
  - Method `NetworkWatchersOperations.begin_get_troubleshooting` has a new overload `def begin_get_troubleshooting(self: None, resource_group_name: str, network_watcher_name: str, parameters: IO[bytes], content_type: str)`
  - Method `NetworkWatchersOperations.begin_get_troubleshooting_result` has a new overload `def begin_get_troubleshooting_result(self: None, resource_group_name: str, network_watcher_name: str, parameters: QueryTroubleshootingParameters, content_type: str)`
  - Method `NetworkWatchersOperations.begin_get_troubleshooting_result` has a new overload `def begin_get_troubleshooting_result(self: None, resource_group_name: str, network_watcher_name: str, parameters: IO[bytes], content_type: str)`
  - Method `NetworkWatchersOperations.begin_get_vm_security_rules` has a new overload `def begin_get_vm_security_rules(self: None, resource_group_name: str, network_watcher_name: str, parameters: SecurityGroupViewParameters, content_type: str)`
  - Method `NetworkWatchersOperations.begin_get_vm_security_rules` has a new overload `def begin_get_vm_security_rules(self: None, resource_group_name: str, network_watcher_name: str, parameters: IO[bytes], content_type: str)`
  - Method `NetworkWatchersOperations.begin_list_available_providers` has a new overload `def begin_list_available_providers(self: None, resource_group_name: str, network_watcher_name: str, parameters: AvailableProvidersListParameters, content_type: str)`
  - Method `NetworkWatchersOperations.begin_list_available_providers` has a new overload `def begin_list_available_providers(self: None, resource_group_name: str, network_watcher_name: str, parameters: IO[bytes], content_type: str)`
  - Method `NetworkWatchersOperations.begin_set_flow_log_configuration` has a new overload `def begin_set_flow_log_configuration(self: None, resource_group_name: str, network_watcher_name: str, parameters: FlowLogInformation, content_type: str)`
  - Method `NetworkWatchersOperations.begin_set_flow_log_configuration` has a new overload `def begin_set_flow_log_configuration(self: None, resource_group_name: str, network_watcher_name: str, parameters: IO[bytes], content_type: str)`
  - Method `NetworkWatchersOperations.begin_verify_ip_flow` has a new overload `def begin_verify_ip_flow(self: None, resource_group_name: str, network_watcher_name: str, parameters: VerificationIPFlowParameters, content_type: str)`
  - Method `NetworkWatchersOperations.begin_verify_ip_flow` has a new overload `def begin_verify_ip_flow(self: None, resource_group_name: str, network_watcher_name: str, parameters: IO[bytes], content_type: str)`
  - Method `NetworkWatchersOperations.create_or_update` has a new overload `def create_or_update(self: None, resource_group_name: str, network_watcher_name: str, parameters: NetworkWatcher, content_type: str)`
  - Method `NetworkWatchersOperations.create_or_update` has a new overload `def create_or_update(self: None, resource_group_name: str, network_watcher_name: str, parameters: IO[bytes], content_type: str)`
  - Method `NetworkWatchersOperations.get_topology` has a new overload `def get_topology(self: None, resource_group_name: str, network_watcher_name: str, parameters: TopologyParameters, content_type: str)`
  - Method `NetworkWatchersOperations.get_topology` has a new overload `def get_topology(self: None, resource_group_name: str, network_watcher_name: str, parameters: IO[bytes], content_type: str)`
  - Method `NetworkWatchersOperations.update_tags` has a new overload `def update_tags(self: None, resource_group_name: str, network_watcher_name: str, parameters: TagsObject, content_type: str)`
  - Method `NetworkWatchersOperations.update_tags` has a new overload `def update_tags(self: None, resource_group_name: str, network_watcher_name: str, parameters: IO[bytes], content_type: str)`
  - Method `P2SVpnGatewaysOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, gateway_name: str, p2_s_vpn_gateway_parameters: P2SVpnGateway, content_type: str)`
  - Method `P2SVpnGatewaysOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, gateway_name: str, p2_s_vpn_gateway_parameters: IO[bytes], content_type: str)`
  - Method `P2SVpnGatewaysOperations.begin_disconnect_p2_s_vpn_connections` has a new overload `def begin_disconnect_p2_s_vpn_connections(self: None, resource_group_name: str, p2_s_vpn_gateway_name: str, request: P2SVpnConnectionRequest, content_type: str)`
  - Method `P2SVpnGatewaysOperations.begin_disconnect_p2_s_vpn_connections` has a new overload `def begin_disconnect_p2_s_vpn_connections(self: None, resource_group_name: str, p2_s_vpn_gateway_name: str, request: IO[bytes], content_type: str)`
  - Method `P2SVpnGatewaysOperations.begin_generate_vpn_profile` has a new overload `def begin_generate_vpn_profile(self: None, resource_group_name: str, gateway_name: str, parameters: P2SVpnProfileParameters, content_type: str)`
  - Method `P2SVpnGatewaysOperations.begin_generate_vpn_profile` has a new overload `def begin_generate_vpn_profile(self: None, resource_group_name: str, gateway_name: str, parameters: IO[bytes], content_type: str)`
  - Method `P2SVpnGatewaysOperations.begin_get_p2_s_vpn_connection_health_detailed` has a new overload `def begin_get_p2_s_vpn_connection_health_detailed(self: None, resource_group_name: str, gateway_name: str, request: P2SVpnConnectionHealthRequest, content_type: str)`
  - Method `P2SVpnGatewaysOperations.begin_get_p2_s_vpn_connection_health_detailed` has a new overload `def begin_get_p2_s_vpn_connection_health_detailed(self: None, resource_group_name: str, gateway_name: str, request: IO[bytes], content_type: str)`
  - Method `P2SVpnGatewaysOperations.begin_update_tags` has a new overload `def begin_update_tags(self: None, resource_group_name: str, gateway_name: str, p2_s_vpn_gateway_parameters: TagsObject, content_type: str)`
  - Method `P2SVpnGatewaysOperations.begin_update_tags` has a new overload `def begin_update_tags(self: None, resource_group_name: str, gateway_name: str, p2_s_vpn_gateway_parameters: IO[bytes], content_type: str)`
  - Method `PacketCapturesOperations.begin_create` has a new overload `def begin_create(self: None, resource_group_name: str, network_watcher_name: str, packet_capture_name: str, parameters: PacketCapture, content_type: str)`
  - Method `PacketCapturesOperations.begin_create` has a new overload `def begin_create(self: None, resource_group_name: str, network_watcher_name: str, packet_capture_name: str, parameters: IO[bytes], content_type: str)`
  - Method `PrivateDnsZoneGroupsOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, private_endpoint_name: str, private_dns_zone_group_name: str, parameters: PrivateDnsZoneGroup, content_type: str)`
  - Method `PrivateDnsZoneGroupsOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, private_endpoint_name: str, private_dns_zone_group_name: str, parameters: IO[bytes], content_type: str)`
  - Method `PrivateEndpointsOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, private_endpoint_name: str, parameters: PrivateEndpoint, content_type: str)`
  - Method `PrivateEndpointsOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, private_endpoint_name: str, parameters: IO[bytes], content_type: str)`
  - Method `PrivateLinkServicesOperations.begin_check_private_link_service_visibility` has a new overload `def begin_check_private_link_service_visibility(self: None, location: str, parameters: CheckPrivateLinkServiceVisibilityRequest, content_type: str)`
  - Method `PrivateLinkServicesOperations.begin_check_private_link_service_visibility` has a new overload `def begin_check_private_link_service_visibility(self: None, location: str, parameters: IO[bytes], content_type: str)`
  - Method `PrivateLinkServicesOperations.begin_check_private_link_service_visibility_by_resource_group` has a new overload `def begin_check_private_link_service_visibility_by_resource_group(self: None, location: str, resource_group_name: str, parameters: CheckPrivateLinkServiceVisibilityRequest, content_type: str)`
  - Method `PrivateLinkServicesOperations.begin_check_private_link_service_visibility_by_resource_group` has a new overload `def begin_check_private_link_service_visibility_by_resource_group(self: None, location: str, resource_group_name: str, parameters: IO[bytes], content_type: str)`
  - Method `PrivateLinkServicesOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, service_name: str, parameters: PrivateLinkService, content_type: str)`
  - Method `PrivateLinkServicesOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, service_name: str, parameters: IO[bytes], content_type: str)`
  - Method `PrivateLinkServicesOperations.update_private_endpoint_connection` has a new overload `def update_private_endpoint_connection(self: None, resource_group_name: str, service_name: str, pe_connection_name: str, parameters: PrivateEndpointConnection, content_type: str)`
  - Method `PrivateLinkServicesOperations.update_private_endpoint_connection` has a new overload `def update_private_endpoint_connection(self: None, resource_group_name: str, service_name: str, pe_connection_name: str, parameters: IO[bytes], content_type: str)`
  - Method `PublicIPAddressesOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, public_ip_address_name: str, parameters: PublicIPAddress, content_type: str)`
  - Method `PublicIPAddressesOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, public_ip_address_name: str, parameters: IO[bytes], content_type: str)`
  - Method `PublicIPAddressesOperations.update_tags` has a new overload `def update_tags(self: None, resource_group_name: str, public_ip_address_name: str, parameters: TagsObject, content_type: str)`
  - Method `PublicIPAddressesOperations.update_tags` has a new overload `def update_tags(self: None, resource_group_name: str, public_ip_address_name: str, parameters: IO[bytes], content_type: str)`
  - Method `PublicIPPrefixesOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, public_ip_prefix_name: str, parameters: PublicIPPrefix, content_type: str)`
  - Method `PublicIPPrefixesOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, public_ip_prefix_name: str, parameters: IO[bytes], content_type: str)`
  - Method `PublicIPPrefixesOperations.update_tags` has a new overload `def update_tags(self: None, resource_group_name: str, public_ip_prefix_name: str, parameters: TagsObject, content_type: str)`
  - Method `PublicIPPrefixesOperations.update_tags` has a new overload `def update_tags(self: None, resource_group_name: str, public_ip_prefix_name: str, parameters: IO[bytes], content_type: str)`
  - Method `RouteFilterRulesOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, route_filter_name: str, rule_name: str, route_filter_rule_parameters: RouteFilterRule, content_type: str)`
  - Method `RouteFilterRulesOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, route_filter_name: str, rule_name: str, route_filter_rule_parameters: IO[bytes], content_type: str)`
  - Method `RouteFiltersOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, route_filter_name: str, route_filter_parameters: RouteFilter, content_type: str)`
  - Method `RouteFiltersOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, route_filter_name: str, route_filter_parameters: IO[bytes], content_type: str)`
  - Method `RouteFiltersOperations.update_tags` has a new overload `def update_tags(self: None, resource_group_name: str, route_filter_name: str, parameters: TagsObject, content_type: str)`
  - Method `RouteFiltersOperations.update_tags` has a new overload `def update_tags(self: None, resource_group_name: str, route_filter_name: str, parameters: IO[bytes], content_type: str)`
  - Method `RouteMapsOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, virtual_hub_name: str, route_map_name: str, route_map_parameters: RouteMap, content_type: str)`
  - Method `RouteMapsOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, virtual_hub_name: str, route_map_name: str, route_map_parameters: IO[bytes], content_type: str)`
  - Method `RouteTablesOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, route_table_name: str, parameters: RouteTable, content_type: str)`
  - Method `RouteTablesOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, route_table_name: str, parameters: IO[bytes], content_type: str)`
  - Method `RouteTablesOperations.update_tags` has a new overload `def update_tags(self: None, resource_group_name: str, route_table_name: str, parameters: TagsObject, content_type: str)`
  - Method `RouteTablesOperations.update_tags` has a new overload `def update_tags(self: None, resource_group_name: str, route_table_name: str, parameters: IO[bytes], content_type: str)`
  - Method `RoutesOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, route_table_name: str, route_name: str, route_parameters: Route, content_type: str)`
  - Method `RoutesOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, route_table_name: str, route_name: str, route_parameters: IO[bytes], content_type: str)`
  - Method `RoutingIntentOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, virtual_hub_name: str, routing_intent_name: str, routing_intent_parameters: RoutingIntent, content_type: str)`
  - Method `RoutingIntentOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, virtual_hub_name: str, routing_intent_name: str, routing_intent_parameters: IO[bytes], content_type: str)`
  - Method `RoutingRuleCollectionsOperations.create_or_update` has a new overload `def create_or_update(self: None, resource_group_name: str, network_manager_name: str, configuration_name: str, rule_collection_name: str, rule_collection: RoutingRuleCollection, content_type: str)`
  - Method `RoutingRuleCollectionsOperations.create_or_update` has a new overload `def create_or_update(self: None, resource_group_name: str, network_manager_name: str, configuration_name: str, rule_collection_name: str, rule_collection: IO[bytes], content_type: str)`
  - Method `RoutingRulesOperations.create_or_update` has a new overload `def create_or_update(self: None, resource_group_name: str, network_manager_name: str, configuration_name: str, rule_collection_name: str, rule_name: str, routing_rule: RoutingRule, content_type: str)`
  - Method `RoutingRulesOperations.create_or_update` has a new overload `def create_or_update(self: None, resource_group_name: str, network_manager_name: str, configuration_name: str, rule_collection_name: str, rule_name: str, routing_rule: IO[bytes], content_type: str)`
  - Method `ScopeConnectionsOperations.create_or_update` has a new overload `def create_or_update(self: None, resource_group_name: str, network_manager_name: str, scope_connection_name: str, parameters: ScopeConnection, content_type: str)`
  - Method `ScopeConnectionsOperations.create_or_update` has a new overload `def create_or_update(self: None, resource_group_name: str, network_manager_name: str, scope_connection_name: str, parameters: IO[bytes], content_type: str)`
  - Method `SecurityAdminConfigurationsOperations.create_or_update` has a new overload `def create_or_update(self: None, resource_group_name: str, network_manager_name: str, configuration_name: str, security_admin_configuration: SecurityAdminConfiguration, content_type: str)`
  - Method `SecurityAdminConfigurationsOperations.create_or_update` has a new overload `def create_or_update(self: None, resource_group_name: str, network_manager_name: str, configuration_name: str, security_admin_configuration: IO[bytes], content_type: str)`
  - Method `SecurityPartnerProvidersOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, security_partner_provider_name: str, parameters: SecurityPartnerProvider, content_type: str)`
  - Method `SecurityPartnerProvidersOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, security_partner_provider_name: str, parameters: IO[bytes], content_type: str)`
  - Method `SecurityPartnerProvidersOperations.update_tags` has a new overload `def update_tags(self: None, resource_group_name: str, security_partner_provider_name: str, parameters: TagsObject, content_type: str)`
  - Method `SecurityPartnerProvidersOperations.update_tags` has a new overload `def update_tags(self: None, resource_group_name: str, security_partner_provider_name: str, parameters: IO[bytes], content_type: str)`
  - Method `SecurityRulesOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, network_security_group_name: str, security_rule_name: str, security_rule_parameters: SecurityRule, content_type: str)`
  - Method `SecurityRulesOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, network_security_group_name: str, security_rule_name: str, security_rule_parameters: IO[bytes], content_type: str)`
  - Method `SecurityUserConfigurationsOperations.create_or_update` has a new overload `def create_or_update(self: None, resource_group_name: str, network_manager_name: str, configuration_name: str, security_user_configuration: SecurityUserConfiguration, content_type: str)`
  - Method `SecurityUserConfigurationsOperations.create_or_update` has a new overload `def create_or_update(self: None, resource_group_name: str, network_manager_name: str, configuration_name: str, security_user_configuration: IO[bytes], content_type: str)`
  - Method `SecurityUserRuleCollectionsOperations.create_or_update` has a new overload `def create_or_update(self: None, resource_group_name: str, network_manager_name: str, configuration_name: str, rule_collection_name: str, security_user_rule_collection: SecurityUserRuleCollection, content_type: str)`
  - Method `SecurityUserRuleCollectionsOperations.create_or_update` has a new overload `def create_or_update(self: None, resource_group_name: str, network_manager_name: str, configuration_name: str, rule_collection_name: str, security_user_rule_collection: IO[bytes], content_type: str)`
  - Method `SecurityUserRulesOperations.create_or_update` has a new overload `def create_or_update(self: None, resource_group_name: str, network_manager_name: str, configuration_name: str, rule_collection_name: str, rule_name: str, security_user_rule: SecurityUserRule, content_type: str)`
  - Method `SecurityUserRulesOperations.create_or_update` has a new overload `def create_or_update(self: None, resource_group_name: str, network_manager_name: str, configuration_name: str, rule_collection_name: str, rule_name: str, security_user_rule: IO[bytes], content_type: str)`
  - Method `ServiceEndpointPoliciesOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, service_endpoint_policy_name: str, parameters: ServiceEndpointPolicy, content_type: str)`
  - Method `ServiceEndpointPoliciesOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, service_endpoint_policy_name: str, parameters: IO[bytes], content_type: str)`
  - Method `ServiceEndpointPoliciesOperations.update_tags` has a new overload `def update_tags(self: None, resource_group_name: str, service_endpoint_policy_name: str, parameters: TagsObject, content_type: str)`
  - Method `ServiceEndpointPoliciesOperations.update_tags` has a new overload `def update_tags(self: None, resource_group_name: str, service_endpoint_policy_name: str, parameters: IO[bytes], content_type: str)`
  - Method `ServiceEndpointPolicyDefinitionsOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, service_endpoint_policy_name: str, service_endpoint_policy_definition_name: str, service_endpoint_policy_definitions: ServiceEndpointPolicyDefinition, content_type: str)`
  - Method `ServiceEndpointPolicyDefinitionsOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, service_endpoint_policy_name: str, service_endpoint_policy_definition_name: str, service_endpoint_policy_definitions: IO[bytes], content_type: str)`
  - Method `StaticMembersOperations.create_or_update` has a new overload `def create_or_update(self: None, resource_group_name: str, network_manager_name: str, network_group_name: str, static_member_name: str, parameters: StaticMember, content_type: str)`
  - Method `StaticMembersOperations.create_or_update` has a new overload `def create_or_update(self: None, resource_group_name: str, network_manager_name: str, network_group_name: str, static_member_name: str, parameters: IO[bytes], content_type: str)`
  - Method `SubnetsOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, virtual_network_name: str, subnet_name: str, subnet_parameters: Subnet, content_type: str)`
  - Method `SubnetsOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, virtual_network_name: str, subnet_name: str, subnet_parameters: IO[bytes], content_type: str)`
  - Method `SubnetsOperations.begin_prepare_network_policies` has a new overload `def begin_prepare_network_policies(self: None, resource_group_name: str, virtual_network_name: str, subnet_name: str, prepare_network_policies_request_parameters: PrepareNetworkPoliciesRequest, content_type: str)`
  - Method `SubnetsOperations.begin_prepare_network_policies` has a new overload `def begin_prepare_network_policies(self: None, resource_group_name: str, virtual_network_name: str, subnet_name: str, prepare_network_policies_request_parameters: IO[bytes], content_type: str)`
  - Method `SubnetsOperations.begin_unprepare_network_policies` has a new overload `def begin_unprepare_network_policies(self: None, resource_group_name: str, virtual_network_name: str, subnet_name: str, unprepare_network_policies_request_parameters: UnprepareNetworkPoliciesRequest, content_type: str)`
  - Method `SubnetsOperations.begin_unprepare_network_policies` has a new overload `def begin_unprepare_network_policies(self: None, resource_group_name: str, virtual_network_name: str, subnet_name: str, unprepare_network_policies_request_parameters: IO[bytes], content_type: str)`
  - Method `SubscriptionNetworkManagerConnectionsOperations.create_or_update` has a new overload `def create_or_update(self: None, network_manager_connection_name: str, parameters: NetworkManagerConnection, content_type: str)`
  - Method `SubscriptionNetworkManagerConnectionsOperations.create_or_update` has a new overload `def create_or_update(self: None, network_manager_connection_name: str, parameters: IO[bytes], content_type: str)`
  - Method `VipSwapOperations.begin_create` has a new overload `def begin_create(self: None, group_name: str, resource_name: str, parameters: SwapResource, content_type: str)`
  - Method `VipSwapOperations.begin_create` has a new overload `def begin_create(self: None, group_name: str, resource_name: str, parameters: IO[bytes], content_type: str)`
  - Method `VirtualApplianceSitesOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, network_virtual_appliance_name: str, site_name: str, parameters: VirtualApplianceSite, content_type: str)`
  - Method `VirtualApplianceSitesOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, network_virtual_appliance_name: str, site_name: str, parameters: IO[bytes], content_type: str)`
  - Method `VirtualHubBgpConnectionOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, virtual_hub_name: str, connection_name: str, parameters: BgpConnection, content_type: str)`
  - Method `VirtualHubBgpConnectionOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, virtual_hub_name: str, connection_name: str, parameters: IO[bytes], content_type: str)`
  - Method `VirtualHubIpConfigurationOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, virtual_hub_name: str, ip_config_name: str, parameters: HubIpConfiguration, content_type: str)`
  - Method `VirtualHubIpConfigurationOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, virtual_hub_name: str, ip_config_name: str, parameters: IO[bytes], content_type: str)`
  - Method `VirtualHubRouteTableV2SOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, virtual_hub_name: str, route_table_name: str, virtual_hub_route_table_v2_parameters: VirtualHubRouteTableV2, content_type: str)`
  - Method `VirtualHubRouteTableV2SOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, virtual_hub_name: str, route_table_name: str, virtual_hub_route_table_v2_parameters: IO[bytes], content_type: str)`
  - Method `VirtualHubsOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, virtual_hub_name: str, virtual_hub_parameters: VirtualHub, content_type: str)`
  - Method `VirtualHubsOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, virtual_hub_name: str, virtual_hub_parameters: IO[bytes], content_type: str)`
  - Method `VirtualHubsOperations.begin_get_effective_virtual_hub_routes` has a new overload `def begin_get_effective_virtual_hub_routes(self: None, resource_group_name: str, virtual_hub_name: str, effective_routes_parameters: Optional[EffectiveRoutesParameters], content_type: str)`
  - Method `VirtualHubsOperations.begin_get_effective_virtual_hub_routes` has a new overload `def begin_get_effective_virtual_hub_routes(self: None, resource_group_name: str, virtual_hub_name: str, effective_routes_parameters: Optional[IO[bytes]], content_type: str)`
  - Method `VirtualHubsOperations.begin_get_inbound_routes` has a new overload `def begin_get_inbound_routes(self: None, resource_group_name: str, virtual_hub_name: str, get_inbound_routes_parameters: GetInboundRoutesParameters, content_type: str)`
  - Method `VirtualHubsOperations.begin_get_inbound_routes` has a new overload `def begin_get_inbound_routes(self: None, resource_group_name: str, virtual_hub_name: str, get_inbound_routes_parameters: IO[bytes], content_type: str)`
  - Method `VirtualHubsOperations.begin_get_outbound_routes` has a new overload `def begin_get_outbound_routes(self: None, resource_group_name: str, virtual_hub_name: str, get_outbound_routes_parameters: GetOutboundRoutesParameters, content_type: str)`
  - Method `VirtualHubsOperations.begin_get_outbound_routes` has a new overload `def begin_get_outbound_routes(self: None, resource_group_name: str, virtual_hub_name: str, get_outbound_routes_parameters: IO[bytes], content_type: str)`
  - Method `VirtualHubsOperations.update_tags` has a new overload `def update_tags(self: None, resource_group_name: str, virtual_hub_name: str, virtual_hub_parameters: TagsObject, content_type: str)`
  - Method `VirtualHubsOperations.update_tags` has a new overload `def update_tags(self: None, resource_group_name: str, virtual_hub_name: str, virtual_hub_parameters: IO[bytes], content_type: str)`
  - Method `VirtualNetworkGatewayConnectionsOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, virtual_network_gateway_connection_name: str, parameters: VirtualNetworkGatewayConnection, content_type: str)`
  - Method `VirtualNetworkGatewayConnectionsOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, virtual_network_gateway_connection_name: str, parameters: IO[bytes], content_type: str)`
  - Method `VirtualNetworkGatewayConnectionsOperations.begin_reset_shared_key` has a new overload `def begin_reset_shared_key(self: None, resource_group_name: str, virtual_network_gateway_connection_name: str, parameters: ConnectionResetSharedKey, content_type: str)`
  - Method `VirtualNetworkGatewayConnectionsOperations.begin_reset_shared_key` has a new overload `def begin_reset_shared_key(self: None, resource_group_name: str, virtual_network_gateway_connection_name: str, parameters: IO[bytes], content_type: str)`
  - Method `VirtualNetworkGatewayConnectionsOperations.begin_set_shared_key` has a new overload `def begin_set_shared_key(self: None, resource_group_name: str, virtual_network_gateway_connection_name: str, parameters: ConnectionSharedKey, content_type: str)`
  - Method `VirtualNetworkGatewayConnectionsOperations.begin_set_shared_key` has a new overload `def begin_set_shared_key(self: None, resource_group_name: str, virtual_network_gateway_connection_name: str, parameters: IO[bytes], content_type: str)`
  - Method `VirtualNetworkGatewayConnectionsOperations.begin_start_packet_capture` has a new overload `def begin_start_packet_capture(self: None, resource_group_name: str, virtual_network_gateway_connection_name: str, parameters: Optional[VpnPacketCaptureStartParameters], content_type: str)`
  - Method `VirtualNetworkGatewayConnectionsOperations.begin_start_packet_capture` has a new overload `def begin_start_packet_capture(self: None, resource_group_name: str, virtual_network_gateway_connection_name: str, parameters: Optional[IO[bytes]], content_type: str)`
  - Method `VirtualNetworkGatewayConnectionsOperations.begin_stop_packet_capture` has a new overload `def begin_stop_packet_capture(self: None, resource_group_name: str, virtual_network_gateway_connection_name: str, parameters: VpnPacketCaptureStopParameters, content_type: str)`
  - Method `VirtualNetworkGatewayConnectionsOperations.begin_stop_packet_capture` has a new overload `def begin_stop_packet_capture(self: None, resource_group_name: str, virtual_network_gateway_connection_name: str, parameters: IO[bytes], content_type: str)`
  - Method `VirtualNetworkGatewayConnectionsOperations.begin_update_tags` has a new overload `def begin_update_tags(self: None, resource_group_name: str, virtual_network_gateway_connection_name: str, parameters: TagsObject, content_type: str)`
  - Method `VirtualNetworkGatewayConnectionsOperations.begin_update_tags` has a new overload `def begin_update_tags(self: None, resource_group_name: str, virtual_network_gateway_connection_name: str, parameters: IO[bytes], content_type: str)`
  - Method `VirtualNetworkGatewayNatRulesOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, virtual_network_gateway_name: str, nat_rule_name: str, nat_rule_parameters: VirtualNetworkGatewayNatRule, content_type: str)`
  - Method `VirtualNetworkGatewayNatRulesOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, virtual_network_gateway_name: str, nat_rule_name: str, nat_rule_parameters: IO[bytes], content_type: str)`
  - Method `VirtualNetworkGatewaysOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, virtual_network_gateway_name: str, parameters: VirtualNetworkGateway, content_type: str)`
  - Method `VirtualNetworkGatewaysOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, virtual_network_gateway_name: str, parameters: IO[bytes], content_type: str)`
  - Method `VirtualNetworkGatewaysOperations.begin_disconnect_virtual_network_gateway_vpn_connections` has a new overload `def begin_disconnect_virtual_network_gateway_vpn_connections(self: None, resource_group_name: str, virtual_network_gateway_name: str, request: P2SVpnConnectionRequest, content_type: str)`
  - Method `VirtualNetworkGatewaysOperations.begin_disconnect_virtual_network_gateway_vpn_connections` has a new overload `def begin_disconnect_virtual_network_gateway_vpn_connections(self: None, resource_group_name: str, virtual_network_gateway_name: str, request: IO[bytes], content_type: str)`
  - Method `VirtualNetworkGatewaysOperations.begin_generate_vpn_profile` has a new overload `def begin_generate_vpn_profile(self: None, resource_group_name: str, virtual_network_gateway_name: str, parameters: VpnClientParameters, content_type: str)`
  - Method `VirtualNetworkGatewaysOperations.begin_generate_vpn_profile` has a new overload `def begin_generate_vpn_profile(self: None, resource_group_name: str, virtual_network_gateway_name: str, parameters: IO[bytes], content_type: str)`
  - Method `VirtualNetworkGatewaysOperations.begin_generatevpnclientpackage` has a new overload `def begin_generatevpnclientpackage(self: None, resource_group_name: str, virtual_network_gateway_name: str, parameters: VpnClientParameters, content_type: str)`
  - Method `VirtualNetworkGatewaysOperations.begin_generatevpnclientpackage` has a new overload `def begin_generatevpnclientpackage(self: None, resource_group_name: str, virtual_network_gateway_name: str, parameters: IO[bytes], content_type: str)`
  - Method `VirtualNetworkGatewaysOperations.begin_set_vpnclient_ipsec_parameters` has a new overload `def begin_set_vpnclient_ipsec_parameters(self: None, resource_group_name: str, virtual_network_gateway_name: str, vpnclient_ipsec_params: VpnClientIPsecParameters, content_type: str)`
  - Method `VirtualNetworkGatewaysOperations.begin_set_vpnclient_ipsec_parameters` has a new overload `def begin_set_vpnclient_ipsec_parameters(self: None, resource_group_name: str, virtual_network_gateway_name: str, vpnclient_ipsec_params: IO[bytes], content_type: str)`
  - Method `VirtualNetworkGatewaysOperations.begin_start_packet_capture` has a new overload `def begin_start_packet_capture(self: None, resource_group_name: str, virtual_network_gateway_name: str, parameters: Optional[VpnPacketCaptureStartParameters], content_type: str)`
  - Method `VirtualNetworkGatewaysOperations.begin_start_packet_capture` has a new overload `def begin_start_packet_capture(self: None, resource_group_name: str, virtual_network_gateway_name: str, parameters: Optional[IO[bytes]], content_type: str)`
  - Method `VirtualNetworkGatewaysOperations.begin_stop_packet_capture` has a new overload `def begin_stop_packet_capture(self: None, resource_group_name: str, virtual_network_gateway_name: str, parameters: VpnPacketCaptureStopParameters, content_type: str)`
  - Method `VirtualNetworkGatewaysOperations.begin_stop_packet_capture` has a new overload `def begin_stop_packet_capture(self: None, resource_group_name: str, virtual_network_gateway_name: str, parameters: IO[bytes], content_type: str)`
  - Method `VirtualNetworkGatewaysOperations.begin_update_tags` has a new overload `def begin_update_tags(self: None, resource_group_name: str, virtual_network_gateway_name: str, parameters: TagsObject, content_type: str)`
  - Method `VirtualNetworkGatewaysOperations.begin_update_tags` has a new overload `def begin_update_tags(self: None, resource_group_name: str, virtual_network_gateway_name: str, parameters: IO[bytes], content_type: str)`
  - Method `VirtualNetworkGatewaysOperations.vpn_device_configuration_script` has a new overload `def vpn_device_configuration_script(self: None, resource_group_name: str, virtual_network_gateway_connection_name: str, parameters: VpnDeviceScriptParameters, content_type: str)`
  - Method `VirtualNetworkGatewaysOperations.vpn_device_configuration_script` has a new overload `def vpn_device_configuration_script(self: None, resource_group_name: str, virtual_network_gateway_connection_name: str, parameters: IO[bytes], content_type: str)`
  - Method `VirtualNetworkPeeringsOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, virtual_network_name: str, virtual_network_peering_name: str, virtual_network_peering_parameters: VirtualNetworkPeering, sync_remote_address_space: Optional[Union[str, SyncRemoteAddressSpace]], content_type: str)`
  - Method `VirtualNetworkPeeringsOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, virtual_network_name: str, virtual_network_peering_name: str, virtual_network_peering_parameters: IO[bytes], sync_remote_address_space: Optional[Union[str, SyncRemoteAddressSpace]], content_type: str)`
  - Method `VirtualNetworkTapsOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, tap_name: str, parameters: VirtualNetworkTap, content_type: str)`
  - Method `VirtualNetworkTapsOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, tap_name: str, parameters: IO[bytes], content_type: str)`
  - Method `VirtualNetworkTapsOperations.update_tags` has a new overload `def update_tags(self: None, resource_group_name: str, tap_name: str, tap_parameters: TagsObject, content_type: str)`
  - Method `VirtualNetworkTapsOperations.update_tags` has a new overload `def update_tags(self: None, resource_group_name: str, tap_name: str, tap_parameters: IO[bytes], content_type: str)`
  - Method `VirtualNetworksOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, virtual_network_name: str, parameters: VirtualNetwork, content_type: str)`
  - Method `VirtualNetworksOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, virtual_network_name: str, parameters: IO[bytes], content_type: str)`
  - Method `VirtualNetworksOperations.update_tags` has a new overload `def update_tags(self: None, resource_group_name: str, virtual_network_name: str, parameters: TagsObject, content_type: str)`
  - Method `VirtualNetworksOperations.update_tags` has a new overload `def update_tags(self: None, resource_group_name: str, virtual_network_name: str, parameters: IO[bytes], content_type: str)`
  - Method `VirtualRouterPeeringsOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, virtual_router_name: str, peering_name: str, parameters: VirtualRouterPeering, content_type: str)`
  - Method `VirtualRouterPeeringsOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, virtual_router_name: str, peering_name: str, parameters: IO[bytes], content_type: str)`
  - Method `VirtualRoutersOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, virtual_router_name: str, parameters: VirtualRouter, content_type: str)`
  - Method `VirtualRoutersOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, virtual_router_name: str, parameters: IO[bytes], content_type: str)`
  - Method `VirtualWansOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, virtual_wan_name: str, wan_parameters: VirtualWAN, content_type: str)`
  - Method `VirtualWansOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, virtual_wan_name: str, wan_parameters: IO[bytes], content_type: str)`
  - Method `VirtualWansOperations.update_tags` has a new overload `def update_tags(self: None, resource_group_name: str, virtual_wan_name: str, wan_parameters: TagsObject, content_type: str)`
  - Method `VirtualWansOperations.update_tags` has a new overload `def update_tags(self: None, resource_group_name: str, virtual_wan_name: str, wan_parameters: IO[bytes], content_type: str)`
  - Method `VpnConnectionsOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, gateway_name: str, connection_name: str, vpn_connection_parameters: VpnConnection, content_type: str)`
  - Method `VpnConnectionsOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, gateway_name: str, connection_name: str, vpn_connection_parameters: IO[bytes], content_type: str)`
  - Method `VpnConnectionsOperations.begin_start_packet_capture` has a new overload `def begin_start_packet_capture(self: None, resource_group_name: str, gateway_name: str, vpn_connection_name: str, parameters: Optional[VpnConnectionPacketCaptureStartParameters], content_type: str)`
  - Method `VpnConnectionsOperations.begin_start_packet_capture` has a new overload `def begin_start_packet_capture(self: None, resource_group_name: str, gateway_name: str, vpn_connection_name: str, parameters: Optional[IO[bytes]], content_type: str)`
  - Method `VpnConnectionsOperations.begin_stop_packet_capture` has a new overload `def begin_stop_packet_capture(self: None, resource_group_name: str, gateway_name: str, vpn_connection_name: str, parameters: Optional[VpnConnectionPacketCaptureStopParameters], content_type: str)`
  - Method `VpnConnectionsOperations.begin_stop_packet_capture` has a new overload `def begin_stop_packet_capture(self: None, resource_group_name: str, gateway_name: str, vpn_connection_name: str, parameters: Optional[IO[bytes]], content_type: str)`
  - Method `VpnGatewaysOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, gateway_name: str, vpn_gateway_parameters: VpnGateway, content_type: str)`
  - Method `VpnGatewaysOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, gateway_name: str, vpn_gateway_parameters: IO[bytes], content_type: str)`
  - Method `VpnGatewaysOperations.begin_start_packet_capture` has a new overload `def begin_start_packet_capture(self: None, resource_group_name: str, gateway_name: str, parameters: Optional[VpnGatewayPacketCaptureStartParameters], content_type: str)`
  - Method `VpnGatewaysOperations.begin_start_packet_capture` has a new overload `def begin_start_packet_capture(self: None, resource_group_name: str, gateway_name: str, parameters: Optional[IO[bytes]], content_type: str)`
  - Method `VpnGatewaysOperations.begin_stop_packet_capture` has a new overload `def begin_stop_packet_capture(self: None, resource_group_name: str, gateway_name: str, parameters: Optional[VpnGatewayPacketCaptureStopParameters], content_type: str)`
  - Method `VpnGatewaysOperations.begin_stop_packet_capture` has a new overload `def begin_stop_packet_capture(self: None, resource_group_name: str, gateway_name: str, parameters: Optional[IO[bytes]], content_type: str)`
  - Method `VpnGatewaysOperations.begin_update_tags` has a new overload `def begin_update_tags(self: None, resource_group_name: str, gateway_name: str, vpn_gateway_parameters: TagsObject, content_type: str)`
  - Method `VpnGatewaysOperations.begin_update_tags` has a new overload `def begin_update_tags(self: None, resource_group_name: str, gateway_name: str, vpn_gateway_parameters: IO[bytes], content_type: str)`
  - Method `VpnLinkConnectionsOperations.begin_set_or_init_default_shared_key` has a new overload `def begin_set_or_init_default_shared_key(self: None, resource_group_name: str, gateway_name: str, connection_name: str, link_connection_name: str, connection_shared_key_parameters: ConnectionSharedKeyResult, content_type: str)`
  - Method `VpnLinkConnectionsOperations.begin_set_or_init_default_shared_key` has a new overload `def begin_set_or_init_default_shared_key(self: None, resource_group_name: str, gateway_name: str, connection_name: str, link_connection_name: str, connection_shared_key_parameters: IO[bytes], content_type: str)`
  - Method `VpnServerConfigurationsOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, vpn_server_configuration_name: str, vpn_server_configuration_parameters: VpnServerConfiguration, content_type: str)`
  - Method `VpnServerConfigurationsOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, vpn_server_configuration_name: str, vpn_server_configuration_parameters: IO[bytes], content_type: str)`
  - Method `VpnServerConfigurationsOperations.update_tags` has a new overload `def update_tags(self: None, resource_group_name: str, vpn_server_configuration_name: str, vpn_server_configuration_parameters: TagsObject, content_type: str)`
  - Method `VpnServerConfigurationsOperations.update_tags` has a new overload `def update_tags(self: None, resource_group_name: str, vpn_server_configuration_name: str, vpn_server_configuration_parameters: IO[bytes], content_type: str)`
  - Method `VpnSitesConfigurationOperations.begin_download` has a new overload `def begin_download(self: None, resource_group_name: str, virtual_wan_name: str, request: GetVpnSitesConfigurationRequest, content_type: str)`
  - Method `VpnSitesConfigurationOperations.begin_download` has a new overload `def begin_download(self: None, resource_group_name: str, virtual_wan_name: str, request: IO[bytes], content_type: str)`
  - Method `VpnSitesOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, vpn_site_name: str, vpn_site_parameters: VpnSite, content_type: str)`
  - Method `VpnSitesOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, vpn_site_name: str, vpn_site_parameters: IO[bytes], content_type: str)`
  - Method `VpnSitesOperations.update_tags` has a new overload `def update_tags(self: None, resource_group_name: str, vpn_site_name: str, vpn_site_parameters: TagsObject, content_type: str)`
  - Method `VpnSitesOperations.update_tags` has a new overload `def update_tags(self: None, resource_group_name: str, vpn_site_name: str, vpn_site_parameters: IO[bytes], content_type: str)`
  - Method `WebApplicationFirewallPoliciesOperations.create_or_update` has a new overload `def create_or_update(self: None, resource_group_name: str, policy_name: str, parameters: WebApplicationFirewallPolicy, content_type: str)`
  - Method `WebApplicationFirewallPoliciesOperations.create_or_update` has a new overload `def create_or_update(self: None, resource_group_name: str, policy_name: str, parameters: IO[bytes], content_type: str)`

### Breaking Changes

  - Method `NetworkManagementClient.__init__` deleted or renamed its parameter `api_version` of kind `positional_or_keyword`
  - Method `NetworkManagementClient.__init__` deleted or renamed its parameter `profile` of kind `positional_or_keyword`
  - Method `NetworkManagementClient.begin_delete_bastion_shareable_link` changed from `synchronous` to `asynchronous`
  - Method `NetworkManagementClient.begin_delete_bastion_shareable_link_by_token` changed from `synchronous` to `asynchronous`
  - Method `NetworkManagementClient.begin_generatevirtualwanvpnserverconfigurationvpnprofile` changed from `synchronous` to `asynchronous`
  - Method `NetworkManagementClient.begin_get_active_sessions` changed from `synchronous` to `asynchronous`
  - Method `NetworkManagementClient.begin_put_bastion_shareable_link` changed from `synchronous` to `asynchronous`
  - Method `NetworkManagementClient.check_dns_name_availability` changed from `synchronous` to `asynchronous`
  - Method `NetworkManagementClient.express_route_provider_port` changed from `synchronous` to `asynchronous`
  - Method `NetworkManagementClient.list_active_connectivity_configurations` changed from `synchronous` to `asynchronous`
  - Method `NetworkManagementClient.list_active_security_admin_rules` changed from `synchronous` to `asynchronous`
  - Method `NetworkManagementClient.list_network_manager_effective_connectivity_configurations` changed from `synchronous` to `asynchronous`
  - Method `NetworkManagementClient.list_network_manager_effective_security_admin_rules` changed from `synchronous` to `asynchronous`
  - Method `NetworkManagementClient.supported_security_providers` changed from `synchronous` to `asynchronous`
  - Method `AdminRuleCollectionsOperations.begin_delete` changed from `synchronous` to `asynchronous`
  - Method `AdminRulesOperations.begin_delete` changed from `synchronous` to `asynchronous`
  - Method `ApplicationGatewaysOperations.begin_backend_health` changed from `synchronous` to `asynchronous`
  - Method `ApplicationGatewaysOperations.begin_backend_health_on_demand` changed from `synchronous` to `asynchronous`
  - Method `ApplicationGatewaysOperations.get_ssl_predefined_policy` changed from `synchronous` to `asynchronous`
  - Method `ApplicationGatewaysOperations.list_available_request_headers` changed from `synchronous` to `asynchronous`
  - Method `ApplicationGatewaysOperations.list_available_response_headers` changed from `synchronous` to `asynchronous`
  - Method `ApplicationGatewaysOperations.list_available_server_variables` changed from `synchronous` to `asynchronous`
  - Method `ApplicationGatewaysOperations.list_available_ssl_options` changed from `synchronous` to `asynchronous`
  - Method `ApplicationGatewaysOperations.list_available_waf_rule_sets` changed from `synchronous` to `asynchronous`
  - Method `ApplicationGatewaysOperations.update_tags` changed from `synchronous` to `asynchronous`
  - Method `ApplicationSecurityGroupsOperations.update_tags` changed from `synchronous` to `asynchronous`
  - Method `AzureFirewallsOperations.begin_list_learned_prefixes` changed from `synchronous` to `asynchronous`
  - Method `AzureFirewallsOperations.begin_packet_capture` changed from `synchronous` to `asynchronous`
  - Method `AzureFirewallsOperations.begin_update_tags` changed from `synchronous` to `asynchronous`
  - Method `BastionHostsOperations.begin_update_tags` changed from `synchronous` to `asynchronous`
  - Method `ConnectionMonitorsOperations.begin_create_or_update` changed from `synchronous` to `asynchronous`
  - Method `ConnectionMonitorsOperations.update_tags` changed from `synchronous` to `asynchronous`
  - Method `ConnectivityConfigurationsOperations.begin_delete` changed from `synchronous` to `asynchronous`
  - Method `DdosCustomPoliciesOperations.update_tags` changed from `synchronous` to `asynchronous`
  - Method `DdosProtectionPlansOperations.update_tags` changed from `synchronous` to `asynchronous`
  - Method `ExpressRouteCircuitsOperations.begin_list_arp_table` changed from `synchronous` to `asynchronous`
  - Method `ExpressRouteCircuitsOperations.begin_list_routes_table` changed from `synchronous` to `asynchronous`
  - Method `ExpressRouteCircuitsOperations.begin_list_routes_table_summary` changed from `synchronous` to `asynchronous`
  - Method `ExpressRouteCircuitsOperations.get_peering_stats` changed from `synchronous` to `asynchronous`
  - Method `ExpressRouteCircuitsOperations.get_stats` changed from `synchronous` to `asynchronous`
  - Method `ExpressRouteCircuitsOperations.update_tags` changed from `synchronous` to `asynchronous`
  - Method `ExpressRouteCrossConnectionsOperations.update_tags` changed from `synchronous` to `asynchronous`
  - Method `ExpressRouteGatewaysOperations.begin_update_tags` changed from `synchronous` to `asynchronous`
  - Method `ExpressRoutePortsOperations.generate_loa` changed from `synchronous` to `asynchronous`
  - Method `ExpressRoutePortsOperations.update_tags` changed from `synchronous` to `asynchronous`
  - Method `FirewallPoliciesOperations.update_tags` changed from `synchronous` to `asynchronous`
  - Method `FlowLogsOperations.update_tags` changed from `synchronous` to `asynchronous`
  - Method `HubVirtualNetworkConnectionsOperations.begin_create_or_update` changed from `synchronous` to `asynchronous`
  - Method `HubVirtualNetworkConnectionsOperations.begin_delete` changed from `synchronous` to `asynchronous`
  - Method `InboundSecurityRuleOperations.get` changed from `synchronous` to `asynchronous`
  - Method `LoadBalancerBackendAddressPoolsOperations.begin_create_or_update` changed from `synchronous` to `asynchronous`
  - Method `LoadBalancerBackendAddressPoolsOperations.begin_delete` changed from `synchronous` to `asynchronous`
  - Method `LoadBalancersOperations.begin_list_inbound_nat_rule_port_mappings` changed from `synchronous` to `asynchronous`
  - Method `LoadBalancersOperations.begin_swap_public_ip_addresses` changed from `synchronous` to `asynchronous`
  - Method `LoadBalancersOperations.migrate_to_ip_based` changed from `synchronous` to `asynchronous`
  - Method `LoadBalancersOperations.update_tags` changed from `synchronous` to `asynchronous`
  - Method `LocalNetworkGatewaysOperations.update_tags` changed from `synchronous` to `asynchronous`
  - Method `NetworkGroupsOperations.begin_delete` changed from `synchronous` to `asynchronous`
  - Method `NetworkInterfacesOperations.begin_get_effective_route_table` changed from `synchronous` to `asynchronous`
  - Method `NetworkInterfacesOperations.begin_list_effective_network_security_groups` changed from `synchronous` to `asynchronous`
  - Method `NetworkInterfacesOperations.get_cloud_service_network_interface` changed from `synchronous` to `asynchronous`
  - Method `NetworkInterfacesOperations.get_virtual_machine_scale_set_ip_configuration` changed from `synchronous` to `asynchronous`
  - Method `NetworkInterfacesOperations.update_tags` changed from `synchronous` to `asynchronous`
  - Method `NetworkManagementClientOperationsMixin.begin_delete_bastion_shareable_link` changed from `synchronous` to `asynchronous`
  - Method `NetworkManagementClientOperationsMixin.begin_delete_bastion_shareable_link_by_token` changed from `synchronous` to `asynchronous`
  - Method `NetworkManagementClientOperationsMixin.begin_generatevirtualwanvpnserverconfigurationvpnprofile` changed from `synchronous` to `asynchronous`
  - Method `NetworkManagementClientOperationsMixin.begin_get_active_sessions` changed from `synchronous` to `asynchronous`
  - Method `NetworkManagementClientOperationsMixin.begin_put_bastion_shareable_link` changed from `synchronous` to `asynchronous`
  - Method `NetworkManagementClientOperationsMixin.check_dns_name_availability` changed from `synchronous` to `asynchronous`
  - Method `NetworkManagementClientOperationsMixin.express_route_provider_port` changed from `synchronous` to `asynchronous`
  - Method `NetworkManagementClientOperationsMixin.list_active_connectivity_configurations` changed from `synchronous` to `asynchronous`
  - Method `NetworkManagementClientOperationsMixin.list_active_security_admin_rules` changed from `synchronous` to `asynchronous`
  - Method `NetworkManagementClientOperationsMixin.list_network_manager_effective_connectivity_configurations` changed from `synchronous` to `asynchronous`
  - Method `NetworkManagementClientOperationsMixin.list_network_manager_effective_security_admin_rules` changed from `synchronous` to `asynchronous`
  - Method `NetworkManagementClientOperationsMixin.supported_security_providers` changed from `synchronous` to `asynchronous`
  - Method `NetworkManagerCommitsOperations.begin_post` changed from `synchronous` to `asynchronous`
  - Method `NetworkManagerDeploymentStatusOperations.list` changed from `synchronous` to `asynchronous`
  - Method `NetworkManagersOperations.begin_delete` changed from `synchronous` to `asynchronous`
  - Method `NetworkManagersOperations.patch` changed from `synchronous` to `asynchronous`
  - Method `NetworkSecurityGroupsOperations.update_tags` changed from `synchronous` to `asynchronous`
  - Method `NetworkVirtualAppliancesOperations.begin_restart` changed from `synchronous` to `asynchronous`
  - Method `NetworkWatchersOperations.begin_get_network_configuration_diagnostic` changed from `synchronous` to `asynchronous`
  - Method `P2SVpnGatewaysOperations.begin_disconnect_p2_s_vpn_connections` changed from `synchronous` to `asynchronous`
  - Method `P2SVpnGatewaysOperations.begin_get_p2_s_vpn_connection_health` changed from `synchronous` to `asynchronous`
  - Method `P2SVpnGatewaysOperations.begin_get_p2_s_vpn_connection_health_detailed` changed from `synchronous` to `asynchronous`
  - Method `P2SVpnGatewaysOperations.begin_reset` changed from `synchronous` to `asynchronous`
  - Method `P2SVpnGatewaysOperations.begin_update_tags` changed from `synchronous` to `asynchronous`
  - Method `PrivateLinkServicesOperations.get_private_endpoint_connection` changed from `synchronous` to `asynchronous`
  - Method `PublicIPAddressesOperations.begin_ddos_protection_status` changed from `synchronous` to `asynchronous`
  - Method `PublicIPAddressesOperations.get_cloud_service_public_ip_address` changed from `synchronous` to `asynchronous`
  - Method `PublicIPAddressesOperations.get_virtual_machine_scale_set_public_ip_address` changed from `synchronous` to `asynchronous`
  - Method `PublicIPAddressesOperations.update_tags` changed from `synchronous` to `asynchronous`
  - Method `PublicIPPrefixesOperations.update_tags` changed from `synchronous` to `asynchronous`
  - Method `ResourceNavigationLinksOperations.list` changed from `synchronous` to `asynchronous`
  - Method `RouteFiltersOperations.update_tags` changed from `synchronous` to `asynchronous`
  - Method `RouteTablesOperations.update_tags` changed from `synchronous` to `asynchronous`
  - Method `SecurityAdminConfigurationsOperations.begin_delete` changed from `synchronous` to `asynchronous`
  - Method `SecurityUserConfigurationsOperations.begin_delete` changed from `synchronous` to `asynchronous`
  - Method `ServiceAssociationLinksOperations.list` changed from `synchronous` to `asynchronous`
  - Method `ServiceEndpointPoliciesOperations.update_tags` changed from `synchronous` to `asynchronous`
  - Method `SubnetsOperations.begin_prepare_network_policies` changed from `synchronous` to `asynchronous`
  - Method `SubnetsOperations.begin_unprepare_network_policies` changed from `synchronous` to `asynchronous`
  - Method `VirtualHubBgpConnectionsOperations.begin_list_advertised_routes` changed from `synchronous` to `asynchronous`
  - Method `VirtualHubBgpConnectionsOperations.begin_list_learned_routes` changed from `synchronous` to `asynchronous`
  - Method `VirtualHubsOperations.begin_get_effective_virtual_hub_routes` changed from `synchronous` to `asynchronous`
  - Method `VirtualHubsOperations.begin_get_inbound_routes` changed from `synchronous` to `asynchronous`
  - Method `VirtualHubsOperations.begin_get_outbound_routes` changed from `synchronous` to `asynchronous`
  - Method `VirtualHubsOperations.update_tags` changed from `synchronous` to `asynchronous`
  - Method `VirtualNetworkGatewayConnectionsOperations.begin_get_ike_sas` changed from `synchronous` to `asynchronous`
  - Method `VirtualNetworkGatewayConnectionsOperations.begin_reset_connection` changed from `synchronous` to `asynchronous`
  - Method `VirtualNetworkGatewayConnectionsOperations.begin_start_packet_capture` changed from `synchronous` to `asynchronous`
  - Method `VirtualNetworkGatewayConnectionsOperations.begin_stop_packet_capture` changed from `synchronous` to `asynchronous`
  - Method `VirtualNetworkGatewayConnectionsOperations.begin_update_tags` changed from `synchronous` to `asynchronous`
  - Method `VirtualNetworkGatewaysOperations.begin_disconnect_virtual_network_gateway_vpn_connections` changed from `synchronous` to `asynchronous`
  - Method `VirtualNetworkGatewaysOperations.begin_generate_vpn_profile` changed from `synchronous` to `asynchronous`
  - Method `VirtualNetworkGatewaysOperations.begin_get_advertised_routes` changed from `synchronous` to `asynchronous`
  - Method `VirtualNetworkGatewaysOperations.begin_get_bgp_peer_status` changed from `synchronous` to `asynchronous`
  - Method `VirtualNetworkGatewaysOperations.begin_get_learned_routes` changed from `synchronous` to `asynchronous`
  - Method `VirtualNetworkGatewaysOperations.begin_get_vpn_profile_package_url` changed from `synchronous` to `asynchronous`
  - Method `VirtualNetworkGatewaysOperations.begin_get_vpnclient_connection_health` changed from `synchronous` to `asynchronous`
  - Method `VirtualNetworkGatewaysOperations.begin_get_vpnclient_ipsec_parameters` changed from `synchronous` to `asynchronous`
  - Method `VirtualNetworkGatewaysOperations.begin_reset` changed from `synchronous` to `asynchronous`
  - Method `VirtualNetworkGatewaysOperations.begin_reset_vpn_client_shared_key` changed from `synchronous` to `asynchronous`
  - Method `VirtualNetworkGatewaysOperations.begin_set_vpnclient_ipsec_parameters` changed from `synchronous` to `asynchronous`
  - Method `VirtualNetworkGatewaysOperations.begin_start_packet_capture` changed from `synchronous` to `asynchronous`
  - Method `VirtualNetworkGatewaysOperations.begin_stop_packet_capture` changed from `synchronous` to `asynchronous`
  - Method `VirtualNetworkGatewaysOperations.begin_update_tags` changed from `synchronous` to `asynchronous`
  - Method `VirtualNetworkGatewaysOperations.supported_vpn_devices` changed from `synchronous` to `asynchronous`
  - Method `VirtualNetworkGatewaysOperations.vpn_device_configuration_script` changed from `synchronous` to `asynchronous`
  - Method `VirtualNetworkPeeringsOperations.begin_create_or_update` changed from `synchronous` to `asynchronous`
  - Method `VirtualNetworkTapsOperations.update_tags` changed from `synchronous` to `asynchronous`
  - Method `VirtualNetworksOperations.begin_list_ddos_protection_status` changed from `synchronous` to `asynchronous`
  - Method `VirtualNetworksOperations.check_ip_address_availability` changed from `synchronous` to `asynchronous`
  - Method `VirtualNetworksOperations.update_tags` changed from `synchronous` to `asynchronous`
  - Method `VirtualWansOperations.update_tags` changed from `synchronous` to `asynchronous`
  - Method `VpnConnectionsOperations.begin_start_packet_capture` changed from `synchronous` to `asynchronous`
  - Method `VpnConnectionsOperations.begin_stop_packet_capture` changed from `synchronous` to `asynchronous`
  - Method `VpnGatewaysOperations.begin_reset` changed from `synchronous` to `asynchronous`
  - Method `VpnGatewaysOperations.begin_start_packet_capture` changed from `synchronous` to `asynchronous`
  - Method `VpnGatewaysOperations.begin_stop_packet_capture` changed from `synchronous` to `asynchronous`
  - Method `VpnGatewaysOperations.begin_update_tags` changed from `synchronous` to `asynchronous`
  - Method `VpnLinkConnectionsOperations.begin_get_ike_sas` changed from `synchronous` to `asynchronous`
  - Method `VpnLinkConnectionsOperations.begin_reset_connection` changed from `synchronous` to `asynchronous`
  - Method `VpnLinkConnectionsOperations.begin_set_or_init_default_shared_key` changed from `synchronous` to `asynchronous`
  - Method `VpnLinkConnectionsOperations.get_default_shared_key` changed from `synchronous` to `asynchronous`
  - Method `VpnLinkConnectionsOperations.list_default_shared_key` changed from `synchronous` to `asynchronous`
  - Method `VpnServerConfigurationsOperations.update_tags` changed from `synchronous` to `asynchronous`
  - Method `VpnSitesOperations.update_tags` changed from `synchronous` to `asynchronous`
  - Deleted or renamed model `AccessRuleDirection`
  - Deleted or renamed model `ActiveBaseSecurityUserRule`
  - Deleted or renamed model `ActiveDefaultSecurityUserRule`
  - Deleted or renamed model `ActiveSecurityUserRule`
  - Deleted or renamed model `ApplicationGatewayAutoscaleBounds`
  - Deleted or renamed model `ApplicationRuleCondition`
  - Deleted or renamed model `AssociationAccessMode`
  - Deleted or renamed model `BaseUserRule`
  - Deleted or renamed model `DdosCustomPolicyProtocol`
  - Deleted or renamed model `DdosCustomPolicyTriggerSensitivityOverride`
  - Deleted or renamed model `DdosSettingsProtectionCoverage`
  - Deleted or renamed model `DefaultUserRule`
  - Deleted or renamed model `DeleteExistingNSGs`
  - Deleted or renamed model `EffectiveUserRuleKind`
  - Deleted or renamed model `EffectiveVirtualNetwork`
  - Deleted or renamed model `EffectiveVirtualNetworksParameter`
  - Deleted or renamed model `EndpointService`
  - Deleted or renamed model `ExpressRouteCircuitPeeringType`
  - Deleted or renamed model `FirewallPolicyFilterRule`
  - Deleted or renamed model `FirewallPolicyFilterRuleAction`
  - Deleted or renamed model `FirewallPolicyFilterRuleActionType`
  - Deleted or renamed model `FirewallPolicyNatRule`
  - Deleted or renamed model `FirewallPolicyNatRuleAction`
  - Deleted or renamed model `FirewallPolicyNatRuleActionType`
  - Deleted or renamed model `FirewallPolicyRuleCondition`
  - Deleted or renamed model `FirewallPolicyRuleConditionApplicationProtocol`
  - Deleted or renamed model `FirewallPolicyRuleConditionApplicationProtocolType`
  - Deleted or renamed model `FirewallPolicyRuleConditionNetworkProtocol`
  - Deleted or renamed model `FirewallPolicyRuleConditionType`
  - Deleted or renamed model `FirewallPolicyRuleGroup`
  - Deleted or renamed model `GroupMembersItem`
  - Deleted or renamed model `InterfaceEndpoint`
  - Deleted or renamed model `ListP2SVpnServerConfigurationsResult`
  - Deleted or renamed model `MembershipType`
  - Deleted or renamed model `NatRuleCondition`
  - Deleted or renamed model `NetworkRuleCondition`
  - Deleted or renamed model `NetworkSecurityPerimeter`
  - Deleted or renamed model `NspAccessRule`
  - Deleted or renamed model `NspAssociation`
  - Deleted or renamed model `NspLink`
  - Deleted or renamed model `NspLinkProvisioningState`
  - Deleted or renamed model `NspLinkReference`
  - Deleted or renamed model `NspLinkStatus`
  - Deleted or renamed model `NspProfile`
  - Deleted or renamed model `NspProvisioningState`
  - Deleted or renamed model `OutboundNatRule`
  - Deleted or renamed model `OutboundRulePropertiesFormatProtocol`
  - Deleted or renamed model `P2SVpnServerConfigRadiusClientRootCertificate`
  - Deleted or renamed model `P2SVpnServerConfigRadiusServerRootCertificate`
  - Deleted or renamed model `P2SVpnServerConfigVpnClientRevokedCertificate`
  - Deleted or renamed model `P2SVpnServerConfigVpnClientRootCertificate`
  - Deleted or renamed model `P2SVpnServerConfiguration`
  - Deleted or renamed model `PeerRouteList`
  - Deleted or renamed model `PerimeterAssociableResource`
  - Deleted or renamed model `PerimeterBasedAccessRule`
  - Deleted or renamed model `Policies`
  - Deleted or renamed model `ProtocolCustomSettingsFormat`
  - Deleted or renamed model `ProxyResource`
  - Deleted or renamed model `PublicIpAddressMigrationPhase`
  - Deleted or renamed model `RuleCollection`
  - Deleted or renamed model `SecurityConfiguration`
  - Deleted or renamed model `SecurityType`
  - Deleted or renamed model `SubscriptionId`
  - Deleted or renamed model `UpdateTagsRequest`
  - Deleted or renamed model `UserRule`
  - Deleted or renamed model `UserRuleKind`
  - Deleted or renamed method `AdminRuleCollectionsOperations.delete`
  - Deleted or renamed method `AdminRulesOperations.delete`
  - Deleted or renamed method `ApplicationGatewaysOperations.begin_update_tags`
  - Deleted or renamed method `ApplicationSecurityGroupsOperations.begin_update_tags`
  - Deleted or renamed method `AzureFirewallsOperations.update_tags`
  - Deleted or renamed method `ConnectivityConfigurationsOperations.delete`
  - Deleted or renamed method `DdosCustomPoliciesOperations.begin_update_tags`
  - Deleted or renamed method `DdosProtectionPlansOperations.begin_update_tags`
  - Deleted or renamed method `ExpressRouteCircuitsOperations.begin_update_tags`
  - Deleted or renamed method `ExpressRouteCircuitsOperations.list_arp_table`
  - Deleted or renamed method `ExpressRouteCircuitsOperations.list_routes_table`
  - Deleted or renamed method `ExpressRouteCircuitsOperations.list_stats`
  - Deleted or renamed method `ExpressRouteCrossConnectionsOperations.begin_update_tags`
  - Deleted or renamed method `ExpressRoutePortsOperations.begin_update_tags`
  - Deleted or renamed method `LoadBalancersOperations.begin_update_tags`
  - Deleted or renamed method `LocalNetworkGatewaysOperations.begin_update_tags`
  - Deleted or renamed method `NetworkGroupsOperations.delete`
  - Deleted or renamed method `NetworkInterfacesOperations.begin_update_tags`
  - Deleted or renamed method `NetworkManagerCommitsOperations.post`
  - Deleted or renamed method `NetworkManagersOperations.delete`
  - Deleted or renamed method `NetworkManagersOperations.patch_tags`
  - Deleted or renamed method `NetworkSecurityGroupsOperations.begin_update_tags`
  - Deleted or renamed method `P2SVpnGatewaysOperations.update_tags`
  - Deleted or renamed method `PublicIPAddressesOperations.begin_update_tags`
  - Deleted or renamed method `PublicIPPrefixesOperations.begin_update_tags`
  - Deleted or renamed method `ResourceNavigationLinksOperations.get`
  - Deleted or renamed method `RouteFilterRulesOperations.begin_update`
  - Deleted or renamed method `RouteFiltersOperations.begin_update`
  - Deleted or renamed method `RouteTablesOperations.begin_update_tags`
  - Deleted or renamed method `SecurityAdminConfigurationsOperations.delete`
  - Deleted or renamed method `SecurityUserConfigurationsOperations.delete`
  - Deleted or renamed method `ServiceAssociationLinksOperations.get`
  - Deleted or renamed method `ServiceEndpointPoliciesOperations.begin_update`
  - Deleted or renamed method `VirtualHubsOperations.begin_update_tags`
  - Deleted or renamed method `VirtualNetworkTapsOperations.begin_update_tags`
  - Deleted or renamed method `VirtualNetworksOperations.begin_update_tags`
  - Deleted or renamed method `VirtualNetworksOperations.get_bastion_hosts`
  - Deleted or renamed method `VirtualRouterPeeringsOperations.update`
  - Deleted or renamed method `VirtualRoutersOperations.update`
  - Deleted or renamed method `VirtualWansOperations.begin_update_tags`
  - Deleted or renamed method `VpnGatewaysOperations.update_tags`
  - Deleted or renamed method `VpnServerConfigurationsOperations.begin_update_tags`
  - Deleted or renamed method `VpnSitesOperations.begin_update_tags`
  - Deleted or renamed model `ActiveConnectivityConfigurationsOperations`
  - Deleted or renamed model `ActiveSecurityAdminRulesOperations`
  - Deleted or renamed model `ActiveSecurityUserRulesOperations`
  - Deleted or renamed model `EffectiveConnectivityConfigurationsOperations`
  - Deleted or renamed model `EffectiveVirtualNetworksOperations`
  - Deleted or renamed model `FirewallPolicyRuleGroupsOperations`
  - Deleted or renamed model `InterfaceEndpointsOperations`
  - Deleted or renamed model `NetworkManagerEffectiveSecurityAdminRulesOperations`
  - Deleted or renamed model `NetworkSecurityPerimetersOperations`
  - Deleted or renamed model `NspAccessRulesOperations`
  - Deleted or renamed model `NspAccessRulesReconcileOperations`
  - Deleted or renamed model `NspAssociationReconcileOperations`
  - Deleted or renamed model `NspAssociationsOperations`
  - Deleted or renamed model `NspLinkReferencesOperations`
  - Deleted or renamed model `NspLinksOperations`
  - Deleted or renamed model `NspProfilesOperations`
  - Deleted or renamed model `P2SVpnServerConfigurationsOperations`
  - Deleted or renamed model `PerimeterAssociableResourceTypesOperations`
  - Deleted or renamed model `UserRuleCollectionsOperations`
  - Deleted or renamed model `UserRulesOperations`
  - Deleted or renamed model `VirtualWANsOperations`

## 27.0.0 (2024-09-22)

### Features Added

  - Added operation SecurityUserConfigurationsOperations.begin_delete
  - Added operation VpnLinkConnectionsOperations.begin_set_or_init_default_shared_key
  - Added operation VpnLinkConnectionsOperations.get_all_shared_keys
  - Added operation VpnLinkConnectionsOperations.get_default_shared_key
  - Added operation VpnLinkConnectionsOperations.list_default_shared_key
  - Added operation group NetworkManagerRoutingConfigurationsOperations
  - Added operation group RoutingRuleCollectionsOperations
  - Added operation group RoutingRulesOperations
  - Added operation group SecurityUserRuleCollectionsOperations
  - Added operation group SecurityUserRulesOperations
  - Model ApplicationGatewayFirewallRule has a new parameter sensitivity
  - Model AzureFirewall has a new parameter autoscale_configuration
  - Model ConfigurationGroup has a new parameter member_type
  - Model ConnectionSharedKeyResult has a new parameter id
  - Model ConnectionSharedKeyResult has a new parameter name
  - Model ConnectionSharedKeyResult has a new parameter properties
  - Model ConnectionSharedKeyResult has a new parameter type
  - Model FlowLog has a new parameter enabled_filtering_criteria
  - Model FlowLogInformation has a new parameter enabled_filtering_criteria
  - Model ManagedRuleOverride has a new parameter sensitivity
  - Model ManagedRulesDefinition has a new parameter exceptions
  - Model NetworkGroup has a new parameter member_type
  - Model PrivateLinkService has a new parameter destination_ip_address
  - Model VirtualNetwork has a new parameter private_endpoint_v_net_policies
  - Model VirtualNetworkGateway has a new parameter resiliency_model
  - Model WebApplicationFirewallPolicy has a new parameter application_gateway_for_containers

### Breaking Changes

  - Model ConnectionSharedKeyResult no longer has parameter value

## 26.0.0 (2024-07-21)

### Features Added

  - Added operation InboundSecurityRuleOperations.get
  - Model BastionHost has a new parameter enable_session_recording
  - Model ExpressRouteCircuitAuthorization has a new parameter connection_resource_uri
  - Model FlowLog has a new parameter identity
  - Model FlowLogInformation has a new parameter identity
  - Model Probe has a new parameter no_healthy_backends_behavior
  - Model ServiceEndpointPropertiesFormat has a new parameter network_identifier
  - Model VirtualNetworkGateway has a new parameter identity
  - Operation ExpressRouteCrossConnectionsOperations.list has a new optional parameter filter

### Breaking Changes

  - Model FirewallPacketCaptureParameters no longer has parameter id

## 25.4.0 (2024-05-27)

### Features Added

  - Added operation NetworkVirtualAppliancesOperations.begin_restart
  - Added operation group FirewallPolicyDeploymentsOperations
  - Added operation group FirewallPolicyDraftsOperations
  - Added operation group FirewallPolicyRuleCollectionGroupDraftsOperations
  - Model ApplicationGatewayHeaderConfiguration has a new parameter header_value_matcher
  - Model ApplicationGatewaySku has a new parameter family
  - Model ConnectionMonitorEndpoint has a new parameter location_details
  - Model ConnectionMonitorEndpoint has a new parameter subscription_id
  - Model ExpressRouteCircuit has a new parameter enable_direct_port_rate_limit
  - Model InboundSecurityRule has a new parameter rule_type
  - Model InboundSecurityRules has a new parameter applies_on
  - Model InboundSecurityRules has a new parameter destination_port_ranges
  - Model InboundSecurityRules has a new parameter name
  - Model NetworkInterfaceIPConfiguration has a new parameter private_ip_address_prefix_length
  - Model NetworkVirtualAppliance has a new parameter network_profile
  - Model PacketCapture has a new parameter capture_settings
  - Model PacketCapture has a new parameter continuous_capture
  - Model PacketCaptureParameters has a new parameter capture_settings
  - Model PacketCaptureParameters has a new parameter continuous_capture
  - Model PacketCaptureResult has a new parameter capture_settings
  - Model PacketCaptureResult has a new parameter continuous_capture
  - Model PacketCaptureResultProperties has a new parameter capture_settings
  - Model PacketCaptureResultProperties has a new parameter continuous_capture
  - Model PacketCaptureStorageLocation has a new parameter local_path
  - Model PolicySettings has a new parameter js_challenge_cookie_expiration_in_mins
  - Model Subnet has a new parameter sharing_scope
  - Model VirtualApplianceNicProperties has a new parameter nic_type
  - Model VirtualNetworkPeering has a new parameter enable_only_i_pv6_peering
  - Model VirtualNetworkPeering has a new parameter local_address_space
  - Model VirtualNetworkPeering has a new parameter local_subnet_names
  - Model VirtualNetworkPeering has a new parameter local_virtual_network_address_space
  - Model VirtualNetworkPeering has a new parameter peer_complete_vnets
  - Model VirtualNetworkPeering has a new parameter remote_subnet_names
  - Model VpnSiteLinkConnection has a new parameter dpd_timeout_seconds

## 25.3.0 (2024-02-22)

### Features Added

  - Model BastionHost has a new parameter zones

## 25.2.0 (2023-12-18)

### Features Added

  - Added operation NetworkManagementClientOperationsMixin.begin_delete_bastion_shareable_link_by_token
  - Added operation NetworkSecurityPerimetersOperations.patch
  - Model ApplicationGatewayListener has a new parameter host_names
  - Model FirewallPolicyIntrusionDetection has a new parameter profile
  - Model NetworkVirtualAppliance has a new parameter internet_ingress_public_ips

## 25.1.0 (2023-09-15)

### Features Added

  - Model BastionHost has a new parameter network_acls
  - Model BastionHost has a new parameter virtual_network
  - Model FirewallPolicy has a new parameter size
  - Model FirewallPolicyRuleCollectionGroup has a new parameter size
  - Model Subnet has a new parameter default_outbound_access
  - Model VirtualNetworkGateway has a new parameter auto_scale_configuration

## 25.0.0 (2023-08-18)

### Features Added

  - Added operation LoadBalancersOperations.migrate_to_ip_based
  - Model BackendAddressPool has a new parameter sync_mode

### Breaking Changes

  - Removed operation group NspLinkReconcileOperations
  - Removed operation group NspLinkReferenceReconcileOperations

## 24.0.0 (2023-07-21)

### Breaking Changes

  - Removed `HTTP_STATUS499` from enum `ApplicationGatewayCustomErrorStatusCode`

### Features Added

  - Added enum `AdminState`
  - Model ActiveConnectivityConfiguration has a new parameter resource_guid
  - Model ActiveDefaultSecurityAdminRule has a new parameter resource_guid
  - Model ActiveSecurityAdminRule has a new parameter resource_guid
  - Model AdminRule has a new parameter resource_guid
  - Model AdminRuleCollection has a new parameter resource_guid
  - Model ApplicationGateway has a new parameter default_predefined_ssl_policy
  - Model ConfigurationGroup has a new parameter resource_guid
  - Model ConnectivityConfiguration has a new parameter resource_guid
  - Model DefaultAdminRule has a new parameter resource_guid
  - Model EffectiveConnectivityConfiguration has a new parameter resource_guid
  - Model EffectiveDefaultSecurityAdminRule has a new parameter resource_guid
  - Model EffectiveSecurityAdminRule has a new parameter resource_guid
  - Model NetworkGroup has a new parameter resource_guid
  - Model NetworkManager has a new parameter resource_guid
  - Model SecurityAdminConfiguration has a new parameter resource_guid
  - Model VirtualNetworkGateway has a new parameter admin_state

## 23.1.0 (2023-05-20)

### Features Added

  - Added operation AzureFirewallsOperations.begin_packet_capture
  - Added operation group NetworkVirtualApplianceConnectionsOperations
  - Model ApplicationRule has a new parameter http_headers_to_insert
  - Model BastionHost has a new parameter enable_kerberos
  - Model NetworkInterface has a new parameter auxiliary_sku
  - Model NetworkVirtualAppliance has a new parameter additional_nics
  - Model NetworkVirtualAppliance has a new parameter virtual_appliance_connections
  - Model PolicySettings has a new parameter file_upload_enforcement
  - Model PolicySettings has a new parameter log_scrubbing
  - Model PolicySettings has a new parameter request_body_enforcement
  - Model PolicySettings has a new parameter request_body_inspect_limit_in_kb
  - Model PrivateEndpointConnection has a new parameter private_endpoint_location
  - Model PublicIPAddressDnsSettings has a new parameter domain_name_label_scope
  - Model VirtualApplianceNicProperties has a new parameter instance_name
  - Model WebApplicationFirewallCustomRule has a new parameter group_by_user_session
  - Model WebApplicationFirewallCustomRule has a new parameter rate_limit_duration
  - Model WebApplicationFirewallCustomRule has a new parameter rate_limit_threshold

## 23.0.1 (2023-04-26)

### Bugs Fixed

  - Fix calling failure for those operations which could be called by client directly #30057

## 23.0.0 (2023-03-29)

### Other Changes

  - Initial stable release with our new combined multiapi package. Package size is now 5% of what it used to be.

### Breaking Changes

  - All query and header parameters are now keyword-only
  - Removed api version subfolders. This means you can no longer access any `azure.mgmt.network.v20xx_xx_xx` modules.
  - Removed `.models` method from `NetworkManagementClient`. Instead, import models from `azure.mgmt.network.models`.

## 22.3.0 (2023-03-20)

### Features Added

  - Model ExpressRouteCircuit has a new parameter authorization_status
  - Model NspAccessRule has a new parameter email_addresses
  - Model NspAccessRule has a new parameter phone_numbers
  - Model NspLink has a new parameter remote_perimeter_location
  - Model NspLinkReference has a new parameter remote_perimeter_location
  - Model VirtualNetwork has a new parameter flow_logs
  - Model WebApplicationFirewallCustomRule has a new parameter state
  - Operation VpnGatewaysOperations.begin_reset has a new optional parameter ip_configuration_id

## 23.0.0b2 (2023-02-20)

### Other Changes

  - Continued package size improvements. The whole package is now 5% of the latest stable release

### Breaking Changes

  - Removed api version subfolders. This means you can no longer access any `azure.mgmt.network.v20xx_xx_xx` modules
  - Removed `.models` method from `NetworkManagementClient`

## 23.0.0b1 (2022-12-19)

### Other Changes

  - Preview package with the same multiapi support but much reduced package size.

### Breaking Changes

  - All query and header parameters are now keyword-only
  - Can not individually access each API version's client and operations

## 22.2.0 (2022-12-15)

### Features Added

  - Model BackendAddressPool has a new parameter virtual_network
  - Model NetworkVirtualAppliance has a new parameter delegation
  - Model NetworkVirtualAppliance has a new parameter deployment_type
  - Model NetworkVirtualAppliance has a new parameter partner_managed_resource
  - Model PolicySettings has a new parameter custom_block_response_body
  - Model PolicySettings has a new parameter custom_block_response_status_code

## 22.1.0 (2022-10-24)

### Features Added

  - Added operation group NspLinkReconcileOperations
  - Added operation group NspLinkReferenceReconcileOperations
  - Added operation group NspLinkReferencesOperations
  - Added operation group NspLinksOperations

## 22.0.0 (2022-10-12)

### Features Added

  - Added operation PublicIPAddressesOperations.begin_ddos_protection_status
  - Added operation VirtualHubsOperations.begin_get_inbound_routes
  - Added operation VirtualHubsOperations.begin_get_outbound_routes
  - Added operation VirtualNetworksOperations.begin_list_ddos_protection_status
  - Added operation group ApplicationGatewayWafDynamicManifestsDefaultOperations
  - Added operation group ApplicationGatewayWafDynamicManifestsOperations
  - Added operation group NspAssociationReconcileOperations
  - Added operation group RouteMapsOperations
  - Added operation group VipSwapOperations
  - Model ApplicationGatewayClientAuthConfiguration has a new parameter verify_client_revocation
  - Model ApplicationGatewayFirewallRule has a new parameter action
  - Model ApplicationGatewayFirewallRule has a new parameter rule_id_string
  - Model ApplicationGatewayFirewallRule has a new parameter state
  - Model ApplicationGatewayFirewallRuleSet has a new parameter tiers
  - Model CustomIpPrefix has a new parameter asn
  - Model CustomIpPrefix has a new parameter express_route_advertise
  - Model CustomIpPrefix has a new parameter geo
  - Model CustomIpPrefix has a new parameter prefix_type
  - Model DdosProtectionPlan has a new parameter public_ip_addresses
  - Model DdosSettings has a new parameter ddos_protection_plan
  - Model DdosSettings has a new parameter protection_mode
  - Model ExpressRouteConnection has a new parameter enable_private_link_fast_path
  - Model ExpressRouteGateway has a new parameter allow_non_virtual_wan_traffic
  - Model ExpressRouteLink has a new parameter colo_location
  - Model ExpressRoutePort has a new parameter billing_type
  - Model ManagedRuleOverride has a new parameter action
  - Model NetworkInterface has a new parameter disable_tcp_state_tracking
  - Model NspProfile has a new parameter diagnostic_settings_version
  - Model Probe has a new parameter probe_threshold
  - Model RoutingConfiguration has a new parameter inbound_route_map
  - Model RoutingConfiguration has a new parameter outbound_route_map
  - Model VirtualHub has a new parameter route_maps
  - Model VirtualNetworkGateway has a new parameter allow_remote_vnet_traffic
  - Model VirtualNetworkGateway has a new parameter allow_virtual_wan_traffic
  - Model VirtualNetworkGateway has a new parameter virtual_network_gateway_policy_groups
  - Model VirtualNetworkGatewayConnection has a new parameter enable_private_link_fast_path
  - Model VirtualNetworkGatewayConnectionListEntity has a new parameter enable_private_link_fast_path
  - Model VnetRoute has a new parameter static_routes_config
  - Model VpnClientConfiguration has a new parameter vng_client_connection_configurations

### Breaking Changes

  - Model DdosCustomPolicy no longer has parameter protocol_custom_settings
  - Model DdosCustomPolicy no longer has parameter public_ip_addresses
  - Model DdosSettings no longer has parameter ddos_custom_policy
  - Model DdosSettings no longer has parameter protected_ip
  - Model DdosSettings no longer has parameter protection_coverage
  - Operation NetworkManagementClientOperationsMixin.list_active_connectivity_configurations has a new parameter top
  - Operation NetworkManagementClientOperationsMixin.list_active_security_admin_rules has a new parameter top
  - Operation NetworkManagementClientOperationsMixin.list_network_manager_effective_connectivity_configurations has a new parameter top
  - Operation NetworkManagementClientOperationsMixin.list_network_manager_effective_security_admin_rules has a new parameter top
  - Operation NetworkManagerDeploymentStatusOperations.list has a new parameter top
  - Removed operation NetworkSecurityPerimetersOperations.check_members
  - Removed operation NetworkSecurityPerimetersOperations.query
  - Removed operation group NspAssociationsProxyOperations

## 21.0.1 (2022-08-17)

### Bugs Fixed

  - Add `__version__` to `__init__.py` for package

## 21.0.0 (2022-08-05)

**Features**

  - Added operation AdminRuleCollectionsOperations.begin_delete
  - Added operation AdminRulesOperations.begin_delete
  - Added operation AzureFirewallsOperations.begin_list_learned_prefixes
  - Added operation ConnectivityConfigurationsOperations.begin_delete
  - Added operation NetworkGroupsOperations.begin_delete
  - Added operation NetworkManagementClientOperationsMixin.express_route_provider_port
  - Added operation NetworkManagementClientOperationsMixin.list_active_connectivity_configurations
  - Added operation NetworkManagementClientOperationsMixin.list_active_security_admin_rules
  - Added operation NetworkManagementClientOperationsMixin.list_network_manager_effective_connectivity_configurations
  - Added operation NetworkManagementClientOperationsMixin.list_network_manager_effective_security_admin_rules
  - Added operation NetworkManagerCommitsOperations.begin_post
  - Added operation NetworkManagersOperations.begin_delete
  - Added operation NetworkManagersOperations.patch
  - Added operation NetworkSecurityPerimetersOperations.check_members
  - Added operation NetworkSecurityPerimetersOperations.query
  - Added operation SecurityAdminConfigurationsOperations.begin_delete
  - Added operation group ExpressRouteProviderPortsLocationOperations
  - Added operation group ManagementGroupNetworkManagerConnectionsOperations
  - Added operation group NspAccessRulesReconcileOperations
  - Added operation group NspAssociationsProxyOperations
  - Added operation group ScopeConnectionsOperations
  - Added operation group StaticMembersOperations
  - Added operation group SubscriptionNetworkManagerConnectionsOperations
  - Model ApplicationGatewayRoutingRule has a new parameter priority
  - Model CustomIpPrefix has a new parameter no_internet_advertise
  - Model FirewallPolicy has a new parameter explicit_proxy
  - Model FirewallPolicySNAT has a new parameter auto_learn_private_ranges
  - Model NetworkManagerPropertiesNetworkManagerScopes has a new parameter cross_tenant_scopes
  - Model NetworkSecurityGroup has a new parameter flush_connection
  - Model NetworkSecurityPerimeter has a new parameter perimeter_guid
  - Model PacketCapture has a new parameter scope
  - Model PacketCapture has a new parameter target_type
  - Model PacketCaptureParameters has a new parameter scope
  - Model PacketCaptureParameters has a new parameter target_type
  - Model PacketCaptureResult has a new parameter scope
  - Model PacketCaptureResult has a new parameter target_type
  - Model PacketCaptureResultProperties has a new parameter scope
  - Model PacketCaptureResultProperties has a new parameter target_type
  - Model VirtualHub has a new parameter virtual_router_auto_scale_configuration

**Breaking changes**

  - Model ActiveBaseSecurityAdminRule no longer has parameter configuration_display_name
  - Model ActiveBaseSecurityAdminRule no longer has parameter rule_collection_display_name
  - Model ActiveConnectivityConfiguration no longer has parameter display_name
  - Model ActiveDefaultSecurityAdminRule no longer has parameter configuration_display_name
  - Model ActiveDefaultSecurityAdminRule no longer has parameter display_name
  - Model ActiveDefaultSecurityAdminRule no longer has parameter rule_collection_display_name
  - Model ActiveSecurityAdminRule no longer has parameter configuration_display_name
  - Model ActiveSecurityAdminRule no longer has parameter display_name
  - Model ActiveSecurityAdminRule no longer has parameter rule_collection_display_name
  - Model AdminRule no longer has parameter display_name
  - Model ConfigurationGroup no longer has parameter conditional_membership
  - Model ConfigurationGroup no longer has parameter display_name
  - Model ConfigurationGroup no longer has parameter group_members
  - Model ConfigurationGroup no longer has parameter member_type
  - Model ConnectivityConfiguration no longer has parameter display_name
  - Model DefaultAdminRule no longer has parameter display_name
  - Model EffectiveBaseSecurityAdminRule no longer has parameter configuration_display_name
  - Model EffectiveBaseSecurityAdminRule no longer has parameter rule_collection_display_name
  - Model EffectiveConnectivityConfiguration no longer has parameter display_name
  - Model EffectiveDefaultSecurityAdminRule no longer has parameter configuration_display_name
  - Model EffectiveDefaultSecurityAdminRule no longer has parameter display_name
  - Model EffectiveDefaultSecurityAdminRule no longer has parameter rule_collection_display_name
  - Model EffectiveSecurityAdminRule no longer has parameter configuration_display_name
  - Model EffectiveSecurityAdminRule no longer has parameter display_name
  - Model EffectiveSecurityAdminRule no longer has parameter rule_collection_display_name
  - Model FirewallPolicy no longer has parameter explicit_proxy_settings
  - Model NetworkGroup no longer has parameter conditional_membership
  - Model NetworkGroup no longer has parameter display_name
  - Model NetworkGroup no longer has parameter group_members
  - Model NetworkGroup no longer has parameter member_type
  - Model NetworkManager no longer has parameter display_name
  - Model NetworkSecurityPerimeter no longer has parameter description
  - Model NetworkSecurityPerimeter no longer has parameter display_name
  - Model NetworkSecurityPerimeter no longer has parameter etag
  - Model NspProfile no longer has parameter enabled_log_categories
  - Parameter commit_type of model NetworkManagerCommit is now required
  - Parameter group_connectivity of model ConnectivityGroupItem is now required
  - Parameter network_group_id of model ConnectivityGroupItem is now required
  - Parameter network_group_id of model NetworkManagerSecurityGroupItem is now required
  - Parameter target_locations of model NetworkManagerCommit is now required
  - Removed operation AdminRuleCollectionsOperations.delete
  - Removed operation AdminRulesOperations.delete
  - Removed operation ConnectivityConfigurationsOperations.delete
  - Removed operation NetworkGroupsOperations.delete
  - Removed operation NetworkManagerCommitsOperations.post
  - Removed operation NetworkManagersOperations.delete
  - Removed operation NetworkManagersOperations.patch_tags
  - Removed operation SecurityAdminConfigurationsOperations.delete

## 20.0.0 (2022-05-10)

**Features**

  - Added operation FirewallPoliciesOperations.update_tags
  - Added operation PerimeterAssociableResourceTypesOperations.list
  - Added operation group ConfigurationPolicyGroupsOperations
  - Added operation group ExpressRoutePortAuthorizationsOperations
  - Added operation group NspAccessRulesOperations
  - Added operation group NspAssociationsOperations
  - Added operation group NspProfilesOperations
  - Model ApplicationGateway has a new parameter backend_settings_collection
  - Model ApplicationGateway has a new parameter listeners
  - Model ApplicationGateway has a new parameter routing_rules
  - Model ApplicationGatewayProbe has a new parameter pick_host_name_from_backend_settings
  - Model BackendAddressPool has a new parameter drain_period_in_seconds
  - Model ExpressRouteCircuit has a new parameter authorization_key
  - Model FirewallPolicyIntrusionDetectionConfiguration has a new parameter private_ranges
  - Model LoadBalancerBackendAddress has a new parameter admin_state
  - Model NetworkInterface has a new parameter auxiliary_mode
  - Model P2SConnectionConfiguration has a new parameter configuration_policy_group_associations
  - Model P2SConnectionConfiguration has a new parameter previous_configuration_policy_group_associations
  - Model VirtualHub has a new parameter hub_routing_preference
  - Model VirtualNetworkGatewayConnection has a new parameter gateway_custom_bgp_ip_addresses
  - Model VirtualNetworkGatewayConnectionListEntity has a new parameter gateway_custom_bgp_ip_addresses
  - Model VpnServerConfiguration has a new parameter configuration_policy_groups
  - Model VpnSiteLinkConnection has a new parameter vpn_gateway_custom_bgp_addresses

**Breaking changes**

  - Removed operation PerimeterAssociableResourceTypesOperations.get

## 19.3.0 (2021-11-05)

**Features**

  - Model LoadBalancerBackendAddress has a new parameter inbound_nat_rules_port_mapping
  - Model VpnNatRuleMapping has a new parameter port_range
  - Model OwaspCrsExclusionEntry has a new parameter exclusion_managed_rule_sets
  - Model VirtualNetworkPeering has a new parameter remote_virtual_network_encryption
  - Model NetworkInterface has a new parameter vnet_encryption_supported
  - Model VirtualNetworkGateway has a new parameter disable_ip_sec_replay_protection
  - Model VirtualNetwork has a new parameter encryption
  - Model BackendAddressPool has a new parameter inbound_nat_rules
  - Added operation LoadBalancersOperations.begin_list_inbound_nat_rule_port_mappings
  - Added operation group FirewallPolicyIdpsSignaturesOverridesOperations
  - Added operation group RoutingIntentOperations
  - Added operation group FirewallPolicyIdpsSignaturesOperations
  - Added operation group FirewallPolicyIdpsSignaturesFilterValuesOperations

## 19.2.0 (2021-10-21)

**Features**

  - Added operation group AdminRuleCollectionsOperations
  - Added operation group SecurityUserConfigurationsOperations
  - Added operation group ConnectivityConfigurationsOperations
  - Added operation group ActiveSecurityUserRulesOperations
  - Added operation group NetworkManagerCommitsOperations
  - Added operation group NetworkManagersOperations
  - Added operation group NetworkManagerDeploymentStatusOperations
  - Added operation group ActiveConnectivityConfigurationsOperations
  - Added operation group NetworkManagerEffectiveSecurityAdminRulesOperations
  - Added operation group UserRuleCollectionsOperations
  - Added operation group ActiveSecurityAdminRulesOperations
  - Added operation group UserRulesOperations
  - Added operation group NetworkGroupsOperations
  - Added operation group EffectiveVirtualNetworksOperations
  - Added operation group NetworkSecurityPerimetersOperations
  - Added operation group PerimeterAssociableResourceTypesOperations
  - Added operation group AdminRulesOperations
  - Added operation group SecurityAdminConfigurationsOperations
  - Added operation group EffectiveConnectivityConfigurationsOperations
  - Removed old api-version `2017-08-01`

## 19.1.0 (2021-10-09)

**Features**

  - Model ServiceEndpointPolicy has a new parameter service_alias
  - Model ServiceEndpointPolicy has a new parameter contextual_service_endpoint_policies
  - Model ApplicationGatewayRequestRoutingRule has a new parameter load_distribution_policy
  - Model BgpConnection has a new parameter hub_virtual_network_connection
  - Model BastionHost has a new parameter enable_ip_connect
  - Model BastionHost has a new parameter disable_copy_paste
  - Model BastionHost has a new parameter enable_tunneling
  - Model BastionHost has a new parameter scale_units
  - Model BastionHost has a new parameter enable_file_copy
  - Model BastionHost has a new parameter enable_shareable_link
  - Model DscpConfiguration has a new parameter qos_definition_collection
  - Model ServiceTagInformation has a new parameter service_tag_change_number
  - Model VnetRoute has a new parameter bgp_connections
  - Model VpnGateway has a new parameter enable_bgp_route_translation_for_nat
  - Model ServiceEndpointPolicyDefinition has a new parameter type
  - Model ApplicationGateway has a new parameter global_configuration
  - Model ApplicationGateway has a new parameter load_distribution_policies
  - Model InboundNatRule has a new parameter frontend_port_range_end
  - Model InboundNatRule has a new parameter frontend_port_range_start
  - Model InboundNatRule has a new parameter backend_address_pool
  - Model PrivateEndpoint has a new parameter ip_configurations
  - Model PrivateEndpoint has a new parameter application_security_groups
  - Model PrivateEndpoint has a new parameter custom_network_interface_name
  - Model NetworkVirtualAppliance has a new parameter ssh_public_key
  - Model ApplicationGatewayUrlPathMap has a new parameter default_load_distribution_policy
  - Model FirewallPolicy has a new parameter sql
  - Model FirewallPolicy has a new parameter explicit_proxy_settings
  - Model VirtualHub has a new parameter kind
  - Model ApplicationGatewayPathRule has a new parameter load_distribution_policy
  - Added operation BastionHostsOperations.begin_update_tags
  - Added operation group ServiceTagInformationOperations

## 19.0.0 (2021-05-14)

**Features**

  - Model ApplicationGatewayTrustedClientCertificate has a new parameter validated_cert_data
  - Model ApplicationGatewayTrustedClientCertificate has a new parameter client_cert_issuer_dn
  - Model VirtualNetwork has a new parameter flow_timeout_in_minutes
  - Model FrontendIPConfiguration has a new parameter gateway_load_balancer
  - Model IPAddressAvailabilityResult has a new parameter is_platform_reserved
  - Model CustomIpPrefix has a new parameter custom_ip_prefix_parent
  - Model CustomIpPrefix has a new parameter failed_reason
  - Model CustomIpPrefix has a new parameter child_custom_ip_prefixes
  - Model CustomIpPrefix has a new parameter authorization_message
  - Model CustomIpPrefix has a new parameter signed_message
  - Model VirtualNetworkPeering has a new parameter peering_sync_level
  - Model VirtualNetworkPeering has a new parameter resource_guid
  - Model VirtualNetworkPeering has a new parameter do_not_verify_remote_gateways
  - Model VirtualNetworkPeering has a new parameter type
  - Model VirtualNetworkPeering has a new parameter remote_virtual_network_address_space
  - Model Subnet has a new parameter application_gateway_ip_configurations
  - Model Subnet has a new parameter type
  - Model LoadBalancingRule has a new parameter backend_address_pools
  - Model EffectiveNetworkSecurityGroupAssociation has a new parameter network_manager
  - Model BastionHost has a new parameter sku
  - Model VirtualNetworkGateway has a new parameter extended_location
  - Model VirtualNetworkGateway has a new parameter nat_rules
  - Model VirtualNetworkGateway has a new parameter enable_bgp_route_translation_for_nat
  - Model NetworkInterface has a new parameter workload_type
  - Model NetworkInterface has a new parameter private_link_service
  - Model NetworkInterface has a new parameter nic_type
  - Model NetworkInterface has a new parameter migration_phase
  - Model Delegation has a new parameter type
  - Model PublicIPPrefix has a new parameter nat_gateway
  - Model VirtualNetworkGatewayConnection has a new parameter egress_nat_rules
  - Model VirtualNetworkGatewayConnection has a new parameter ingress_nat_rules
  - Model NetworkInterfaceIPConfiguration has a new parameter gateway_load_balancer
  - Model NetworkInterfaceIPConfiguration has a new parameter type
  - Model AvailablePrivateEndpointType has a new parameter display_name
  - Model PublicIPAddress has a new parameter delete_option
  - Model PublicIPAddress has a new parameter nat_gateway
  - Model PublicIPAddress has a new parameter service_public_ip_address
  - Model PublicIPAddress has a new parameter linked_public_ip_address
  - Model PublicIPAddress has a new parameter migration_phase
  - Model VirtualHub has a new parameter preferred_routing_gateway
  - Model BackendAddressPool has a new parameter tunnel_interfaces
  - Model ServiceTagInformationPropertiesFormat has a new parameter state
  - Added operation LoadBalancersOperations.begin_swap_public_ip_addresses
  - Added operation group VirtualNetworkGatewayNatRulesOperations

**Breaking changes**

  - Operation VirtualNetworkPeeringsOperations.begin_create_or_update has a new signature
  - Model VirtualNetworkGateway no longer has parameter virtual_network_extended_location

## 18.0.0 (2021-03-08)

**Features**

  - Model VpnConnection has a new parameter traffic_selector_policies
  - Model VirtualNetworkGateway has a new parameter virtual_network_extended_location
  - Model VirtualNetworkGateway has a new parameter v_net_extended_location_resource_id
  - Model VpnClientConfiguration has a new parameter vpn_authentication_types
  - Model LoadBalancerBackendAddress has a new parameter subnet
  - Model ServiceEndpointPolicy has a new parameter kind
  - Model FirewallPolicy has a new parameter snat
  - Model FirewallPolicy has a new parameter insights
  - Added operation VirtualNetworkGatewayConnectionsOperations.begin_reset_connection
  - Added operation VpnLinkConnectionsOperations.begin_get_ike_sas
  - Added operation VpnLinkConnectionsOperations.begin_reset_connection

**Breaking changes**

  - Model VirtualNetworkGateway no longer has parameter extended_location
  - Model VirtualNetworkGateway no longer has parameter virtual_network_extended_location_resource_id

## 17.1.0 (2021-01-26)

**Features**
  - Model PrivateEndpoint has a new parameter extended_location
  - Model VpnGateway has a new parameter nat_rules
  - Model ExpressRouteConnection has a new parameter express_route_gateway_bypass
  - Model SecurityRule has a new parameter type
  - Model PrivateLinkService has a new parameter extended_location
  - Model Route has a new parameter type
  - Model Route has a new parameter has_bgp_override
  - Model RouteTable has a new parameter resource_guid
  - Model VpnSiteLinkConnection has a new parameter ingress_nat_rules
  - Model VpnSiteLinkConnection has a new parameter vpn_link_connection_mode
  - Model VpnSiteLinkConnection has a new parameter egress_nat_rules
  - Model BackendAddressPool has a new parameter location
  - Model CustomIpPrefix has a new parameter extended_location
  - Added operation ExpressRouteGatewaysOperations.begin_update_tags
  - Added operation VirtualNetworkGatewayConnectionsOperations.begin_get_ike_sas
  - Added operation group NatRulesOperations

## 17.0.0 (2020-11-25)

**Features**

  - Model PublicIPPrefix has a new parameter extended_location
  - Model PublicIPPrefixSku has a new parameter tier
  - Model NatRule has a new parameter translated_fqdn
  - Model NetworkInterface has a new parameter extended_location
  - Model ApplicationRule has a new parameter terminate_tls
  - Model ApplicationRule has a new parameter web_categories
  - Model ApplicationRule has a new parameter target_urls
  - Model VirtualNetworkGatewayConnection has a new parameter connection_mode
  - Model LoadBalancer has a new parameter extended_location
  - Model PublicIPAddress has a new parameter extended_location
  - Model LoadBalancerSku has a new parameter tier
  - Model VirtualNetwork has a new parameter extended_location
  - Model P2SVpnGateway has a new parameter is_routing_preference_internet
  - Model IpGroup has a new parameter firewall_policies
  - Model VpnGateway has a new parameter is_routing_preference_internet
  - Model VirtualNetworkGateway has a new parameter extended_location
  - Model VirtualNetworkGateway has a new parameter virtual_network_extended_location_resource_id
  - Model VirtualNetworkGatewayConnectionListEntity has a new parameter connection_mode
  - Model FirewallPolicy has a new parameter sku
  - Model FirewallPolicy has a new parameter transport_security
  - Model FirewallPolicy has a new parameter identity
  - Model FirewallPolicy has a new parameter intrusion_detection
  - Model VirtualHub has a new parameter allow_branch_to_branch_traffic
  - Model PublicIPAddressSku has a new parameter tier
  - Model ServiceTagsListResult has a new parameter next_link
  - Model LoadBalancerBackendAddress has a new parameter load_balancer_frontend_ip_configuration
  - Added operation NetworkInterfacesOperations.list_cloud_service_network_interfaces
  - Added operation NetworkInterfacesOperations.get_cloud_service_network_interface
  - Added operation NetworkInterfacesOperations.list_cloud_service_role_instance_network_interfaces
  - Added operation PublicIPAddressesOperations.list_cloud_service_role_instance_public_ip_addresses
  - Added operation PublicIPAddressesOperations.list_cloud_service_public_ip_addresses
  - Added operation PublicIPAddressesOperations.get_cloud_service_public_ip_address
  - Added operation group WebCategoriesOperations

**Breaking changes**

  - Operation ConnectionMonitorsOperations.begin_create_or_update has a new signature
  - Model VirtualHub no longer has parameter enable_virtual_router_route_propogation

## 16.0.0 (2020-09-15)

**Features**

  - Model VirtualNetworkPeering has a new parameter remote_bgp_communities
  - Model VirtualHub has a new parameter virtual_router_asn
  - Model VirtualHub has a new parameter routing_state
  - Model VirtualHub has a new parameter ip_configurations
  - Model VirtualHub has a new parameter virtual_router_ips
  - Model VirtualHub has a new parameter enable_virtual_router_route_propogation
  - Model VirtualHub has a new parameter bgp_connections
  - Model FirewallPolicyRule has a new parameter description
  - Model ExpressRouteLinkMacSecConfig has a new parameter sci_state
  - Model VpnGateway has a new parameter ip_configurations
  - Model P2SConnectionConfiguration has a new parameter enable_internet_security
  - Model ConnectionMonitorEndpoint has a new parameter type
  - Model ConnectionMonitorEndpoint has a new parameter coverage_level
  - Model ConnectionMonitorEndpoint has a new parameter scope
  - Model FirewallPolicy has a new parameter rule_collection_groups
  - Model FirewallPolicy has a new parameter dns_settings
  - Model NetworkInterface has a new parameter dscp_configuration
  - Model NetworkVirtualAppliance has a new parameter address_prefix
  - Model NetworkVirtualAppliance has a new parameter cloud_init_configuration_blobs
  - Model NetworkVirtualAppliance has a new parameter boot_strap_configuration_blobs
  - Model NetworkVirtualAppliance has a new parameter cloud_init_configuration
  - Model NetworkVirtualAppliance has a new parameter inbound_security_rules
  - Model NetworkVirtualAppliance has a new parameter nva_sku
  - Model NetworkVirtualAppliance has a new parameter virtual_appliance_sites
  - Model ConnectionMonitorTcpConfiguration has a new parameter destination_port_behavior
  - Model ApplicationGatewayHttpListener has a new parameter ssl_profile
  - Model P2SVpnGateway has a new parameter custom_dns_servers
  - Model ApplicationGateway has a new parameter private_link_configurations
  - Model ApplicationGateway has a new parameter trusted_client_certificates
  - Model ApplicationGateway has a new parameter private_endpoint_connections
  - Model ApplicationGateway has a new parameter ssl_profiles
  - Model HubIPAddresses has a new parameter public_i_ps
  - Model PublicIPPrefix has a new parameter custom_ip_prefix
  - Model ApplicationGatewayFrontendIPConfiguration has a new parameter private_link_configuration
  - Model VpnSite has a new parameter o365_policy
  - Model ConnectivityHop has a new parameter previous_links
  - Model ConnectivityHop has a new parameter previous_hop_ids
  - Model ConnectivityHop has a new parameter links
  - Added operation ExpressRoutePortsOperations.generate_loa
  - Added operation FlowLogsOperations.update_tags
  - Added operation HubVirtualNetworkConnectionsOperations.begin_create_or_update
  - Added operation HubVirtualNetworkConnectionsOperations.begin_delete
  - Added operation VpnGatewaysOperations.begin_stop_packet_capture
  - Added operation VpnGatewaysOperations.begin_start_packet_capture
  - Added operation VpnGatewaysOperations.begin_update_tags
  - Added operation VpnConnectionsOperations.begin_stop_packet_capture
  - Added operation VpnConnectionsOperations.begin_start_packet_capture
  - Added operation PrivateLinkServicesOperations.begin_check_private_link_service_visibility_by_resource_group
  - Added operation PrivateLinkServicesOperations.begin_check_private_link_service_visibility
  - Added operation VirtualHubsOperations.begin_get_effective_virtual_hub_routes
  - Added operation P2SVpnGatewaysOperations.begin_reset
  - Added operation P2SVpnGatewaysOperations.begin_update_tags
  - Added operation group CustomIPPrefixesOperations
  - Added operation group VirtualApplianceSitesOperations
  - Added operation group DscpConfigurationOperations
  - Added operation group VirtualHubIpConfigurationOperations
  - Added operation group VirtualHubBgpConnectionOperations
  - Added operation group InboundSecurityRuleOperations
  - Added operation group VirtualApplianceSkusOperations
  - Added operation group ApplicationGatewayPrivateLinkResourcesOperations
  - Added operation group ApplicationGatewayPrivateEndpointConnectionsOperations
  - Added operation group FirewallPolicyRuleCollectionGroupsOperations
  - Added operation group VirtualHubBgpConnectionsOperations

**Breaking changes**

  - Model VirtualHub no longer has parameter virtual_network_connections
  - Model FirewallPolicyRule no longer has parameter priority
  - Model FirewallPolicy no longer has parameter transport_security
  - Model FirewallPolicy no longer has parameter rule_groups
  - Model FirewallPolicy no longer has parameter intrusion_system_mode
  - Model FirewallPolicy no longer has parameter identity
  - Model NetworkVirtualAppliance no longer has parameter boot_strap_configuration_blob
  - Model NetworkVirtualAppliance no longer has parameter sku
  - Model NetworkVirtualAppliance no longer has parameter cloud_init_configuration_blob
  - Model NatRuleCondition no longer has parameter terminate_tls
  - Model HubIPAddresses no longer has parameter public_ip_addresses
  - Model ApplicationRuleCondition no longer has parameter target_urls
  - Removed operation VpnGatewaysOperations.update_tags
  - Removed operation PrivateLinkServicesOperations.check_private_link_service_visibility_by_resource_group
  - Removed operation PrivateLinkServicesOperations.check_private_link_service_visibility
  - Removed operation P2SVpnGatewaysOperations.update_tags

## 16.0.0b1 (2020-06-17)

This is beta preview version.
For detailed changelog please refer to equivalent stable version 10.2.0 (https://pypi.org/project/azure-mgmt-network/10.2.0/)

This version uses a next-generation code generator that introduces important breaking changes, but also important new features (like unified authentication and async programming).

**General breaking changes**

- Credential system has been completly revamped:

  - `azure.common.credentials` or `msrestazure.azure_active_directory` instances are no longer supported, use the `azure-identity` classes instead: https://pypi.org/project/azure-identity/
  - `credentials` parameter has been renamed `credential`

- The `config` attribute no longer exists on a client, configuration should be passed as kwarg. Example: `MyClient(credential, subscription_id, enable_logging=True)`. For a complete set of
  supported options, see the [parameters accept in init documentation of azure-core](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/CLIENT_LIBRARY_DEVELOPER.md#available-policies)
- You can't import a `version` module anymore, use `__version__` instead
- Operations that used to return a `msrest.polling.LROPoller` now returns a `azure.core.polling.LROPoller` and are prefixed with `begin_`.
- Exceptions tree have been simplified and most exceptions are now `azure.core.exceptions.HttpResponseError` (`CloudError` has been removed).
- Most of the operation kwarg have changed. Some of the most noticeable:

  - `raw` has been removed. Equivalent feature can be found using `cls`, a callback that will give access to internal HTTP response for advanced user
  - For a complete set of
  supported options, see the [parameters accept in Request documentation of azure-core](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/CLIENT_LIBRARY_DEVELOPER.md#available-policies)

**General new features**

- Type annotations support using `typing`. SDKs are mypy ready.
- This client has now stable and official support for async. Check the `aio` namespace of your package to find the async client.
- This client now support natively tracing library like OpenCensus or OpenTelemetry. See this [tracing quickstart](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/core/azure-core-tracing-opentelemetry) for an overview.


## 10.2.0 (2020-04-10)

**Features**

  - Model VpnConnection has a new parameter routing_configuration
  - Model NatRuleCondition has a new parameter terminate_tls
  - Model HubVirtualNetworkConnection has a new parameter routing_configuration
  - Model ExpressRouteConnection has a new parameter routing_configuration
  - Model FirewallPolicy has a new parameter transport_security
  - Model FirewallPolicy has a new parameter identity
  - Model FirewallPolicy has a new parameter threat_intel_whitelist
  - Model ApplicationRuleCondition has a new parameter target_urls
  - Model P2SConnectionConfiguration has a new parameter routing_configuration
  - Model BackendAddressPool has a new parameter load_balancer_backend_addresses
  - Added operation LoadBalancerBackendAddressPoolsOperations.create_or_update
  - Added operation LoadBalancerBackendAddressPoolsOperations.delete
  - Added operation group HubRouteTablesOperations

## 10.1.0 (2020-04-10)

**Features**

  - Model VpnConnection has a new parameter dpd_timeout_seconds
  - Model FirewallPolicy has a new parameter intrusion_system_mode
  - Model Subnet has a new parameter ip_allocations
  - Model ApplicationGateway has a new parameter force_firewall_policy_association
  - Model PrivateEndpoint has a new parameter custom_dns_configs
  - Model VirtualNetworkGatewayConnection has a new parameter dpd_timeout_seconds
  - Model VpnClientConfiguration has a new parameter radius_servers
  - Model VirtualNetwork has a new parameter ip_allocations
  - Model VirtualHub has a new parameter security_partner_provider
  - Model VpnServerConfiguration has a new parameter radius_servers
  - Added operation group PrivateDnsZoneGroupsOperations
  - Added operation group SecurityPartnerProvidersOperations
  - Added operation group IpAllocationsOperations

## 10.0.0 (2020-03-31)

**Features**

  - Model VirtualNetworkGatewayConnection has a new parameter use_local_azure_ip_address
  - Model NetworkRuleCondition has a new parameter source_ip_groups
  - Model NetworkRuleCondition has a new parameter destination_ip_groups
  - Model VirtualNetworkGatewayIPConfiguration has a new parameter private_ip_address
  - Model BgpSettings has a new parameter bgp_peering_addresses
  - Model ExpressRouteCircuitConnection has a new parameter ipv6_circuit_connection_config
  - Model ApplicationGatewayHttpListener has a new parameter host_names
  - Model ApplicationRuleCondition has a new parameter source_ip_groups
  - Model VirtualNetworkGateway has a new parameter enable_private_ip_address
  - Model LocalNetworkGateway has a new parameter fqdn
  - Model VpnSiteLink has a new parameter fqdn
  - Model NetworkSecurityGroup has a new parameter flow_logs
  - Added operation NetworkManagementClientOperationsMixin.put_bastion_shareable_link
  - Added operation NetworkManagementClientOperationsMixin.get_bastion_shareable_link
  - Added operation NetworkManagementClientOperationsMixin.delete_bastion_shareable_link
  - Added operation NetworkManagementClientOperationsMixin.disconnect_active_sessions
  - Added operation NetworkManagementClientOperationsMixin.get_active_sessions
  - Added operation group NetworkVirtualAppliancesOperations

**Breaking changes**

  - Model ApplicationGatewayHttpListener no longer has parameter hostnames

## 9.0.0 (2020-01-17)

**Features**

  - Model AzureFirewall has a new parameter ip_groups
  - Model AzureFirewall has a new parameter
    management_ip_configuration
  - Model ConnectionMonitorResult has a new parameter endpoints
  - Model ConnectionMonitorResult has a new parameter
    connection_monitor_type
  - Model ConnectionMonitorResult has a new parameter
    test_configurations
  - Model ConnectionMonitorResult has a new parameter test_groups
  - Model ConnectionMonitorResult has a new parameter outputs
  - Model ConnectionMonitorResult has a new parameter notes
  - Model AzureFirewallIPConfiguration has a new parameter type
  - Model ConnectionMonitor has a new parameter endpoints
  - Model ConnectionMonitor has a new parameter test_configurations
  - Model ConnectionMonitor has a new parameter test_groups
  - Model ConnectionMonitor has a new parameter outputs
  - Model ConnectionMonitor has a new parameter notes
  - Model DdosSettings has a new parameter protected_ip
  - Model ApplicationGatewayRewriteRuleActionSet has a new parameter
    url_configuration
  - Added operation
    P2sVpnGatewaysOperations.disconnect_p2s_vpn_connections
  - Added operation
    VirtualNetworkGatewaysOperations.disconnect_virtual_network_gateway_vpn_connections
  - Added operation group FlowLogsOperations

**Breaking changes**

  - Operation
    ExpressRouteCircuitAuthorizationsOperations.create_or_update has a
    new signature
  - Model ConnectionMonitorParameters has a new signature

## 8.0.0 (2019-11-12)

**Features**

  - Model PrivateLinkServiceConnectionState has a new parameter
    actions_required
  - Model ConnectivityParameters has a new parameter
    preferred_ip_version

**Breaking changes**

  - Model PrivateLinkServiceConnectionState no longer has parameter
    action_required

## 7.0.0 (2019-10-22)

**Features**

  - Model ApplicationGatewayHttpListener has a new parameter hostnames
  - Model ApplicationGatewayHttpListener has a new parameter
    firewall_policy
  - Model ApplicationGatewayPathRule has a new parameter
    firewall_policy
  - Model P2SVpnGateway has a new parameter
    p2_sconnection_configurations
  - Model VpnServerConfiguration has a new parameter
    vpn_client_root_certificates
  - Model VpnServerConfiguration has a new parameter
    radius_server_root_certificates
  - Model VpnServerConfiguration has a new parameter
    radius_client_root_certificates
  - Model VpnServerConfiguration has a new parameter
    vpn_client_revoked_certificates
  - Model ExpressRouteConnection has a new parameter
    enable_internet_security
  - Model AzureFirewallApplicationRule has a new parameter
    source_ip_groups
  - Model WebApplicationFirewallPolicy has a new parameter
    path_based_rules
  - Model WebApplicationFirewallPolicy has a new parameter
    http_listeners
  - Model PrivateLinkService has a new parameter enable_proxy_protocol
  - Model AzureFirewallNetworkRule has a new parameter
    destination_ip_groups
  - Model AzureFirewallNetworkRule has a new parameter
    source_ip_groups
  - Model AzureFirewallNetworkRule has a new parameter
    destination_fqdns
  - Model VirtualWAN has a new parameter virtual_wan_type
  - Model VirtualHub has a new parameter sku
  - Model VirtualHub has a new parameter virtual_hub_route_table_v2s
  - Model AzureFirewallNatRule has a new parameter translated_fqdn
  - Model AzureFirewallNatRule has a new parameter source_ip_groups
  - Model PrivateEndpointConnection has a new parameter link_identifier
  - Model AzureFirewall has a new parameter additional_properties
  - Added operation RouteFiltersOperations.update_tags
  - Added operation ServiceEndpointPoliciesOperations.update_tags
  - Added operation
    PrivateLinkServicesOperations.get_private_endpoint_connection
  - Added operation
    PrivateLinkServicesOperations.list_private_endpoint_connections
  - Added operation group VirtualHubRouteTableV2sOperations
  - Added operation group IpGroupsOperations

**Breaking changes**

  - Operation AzureFirewallsOperations.update_tags has a new signature
  - Operation
    ExpressRouteCircuitAuthorizationsOperations.create_or_update has a
    new signature
  - Model P2SVpnGateway no longer has parameter
    p2s_connection_configurations
  - Model VpnServerConfiguration no longer has parameter
    vpn_server_config_vpn_client_root_certificates
  - Model VpnServerConfiguration no longer has parameter
    vpn_server_config_radius_client_root_certificates
  - Model VpnServerConfiguration no longer has parameter
    vpn_server_config_vpn_client_revoked_certificates
  - Model VpnServerConfiguration no longer has parameter
    vpn_server_config_radius_server_root_certificates
  - Removed operation RouteFiltersOperations.update
  - Removed operation VirtualRoutersOperations.update
  - Removed operation RouteFilterRulesOperations.update
  - Removed operation VirtualRouterPeeringsOperations.update
  - Removed operation FirewallPoliciesOperations.update_tags
  - Removed operation ServiceEndpointPoliciesOperations.update

## 6.0.0 (2019-10-09)

**Features**

  - Model VirtualNetwork has a new parameter bgp_communities
  - Model VirtualHub has a new parameter azure_firewall
  - Model VirtualHub has a new parameter security_provider_name
  - Model P2SVpnGateway has a new parameter
    p2s_connection_configurations
  - Model P2SVpnGateway has a new parameter vpn_server_configuration
  - Model AzureFirewall has a new parameter sku
  - Model VirtualNetworkGateway has a new parameter
    inbound_dns_forwarding_endpoint
  - Model VirtualNetworkGateway has a new parameter
    enable_dns_forwarding
  - Added operation
    P2sVpnGatewaysOperations.get_p2s_vpn_connection_health_detailed
  - Added operation
    NetworkManagementClientOperationsMixin.generatevirtualwanvpnserverconfigurationvpnprofile
  - Added operation group VpnServerConfigurationsOperations
  - Added operation group
    VpnServerConfigurationsAssociatedWithVirtualWanOperations
  - Added operation group AvailableServiceAliasesOperations

**Breaking changes**

  - Model WebApplicationFirewallPolicy has a new required parameter
    managed_rules
  - Model P2SVpnGateway no longer has parameter
    vpn_client_address_pool
  - Model P2SVpnGateway no longer has parameter custom_routes
  - Model P2SVpnGateway no longer has parameter
    p2_svpn_server_configuration
  - Model VirtualWAN no longer has parameter security_provider_name
  - Model VirtualWAN no longer has parameter
    p2_svpn_server_configurations
  - Model PolicySettings has a new signature

## 5.1.0 (2019-10-03)

**Features**

  - Model VirtualNetworkGateway has a new parameter
    vpn_gateway_generation
  - Model ExpressRoutePort has a new parameter identity
  - Model VirtualNetworkGatewayConnection has a new parameter
    traffic_selector_policies
  - Model ExpressRouteLink has a new parameter mac_sec_config
  - Model VirtualNetworkGatewayConnectionListEntity has a new parameter
    traffic_selector_policies
  - Model NetworkInterfaceIPConfiguration has a new parameter
    private_link_connection_properties
  - Model ApplicationGatewayRequestRoutingRule has a new parameter
    priority
  - Added operation
    VirtualNetworkGatewayConnectionsOperations.stop_packet_capture
  - Added operation
    VirtualNetworkGatewayConnectionsOperations.start_packet_capture
  - Added operation ConnectionMonitorsOperations.update_tags
  - Added operation
    VirtualNetworkGatewaysOperations.stop_packet_capture
  - Added operation
    VirtualNetworkGatewaysOperations.start_packet_capture
  - Added operation group VirtualRoutersOperations
  - Added operation group VirtualRouterPeeringsOperations

## 5.0.0 (2019-08-27)

**Features**

  - Model PrivateLinkServiceIpConfiguration has a new parameter primary
  - Model PrivateLinkServiceIpConfiguration has a new parameter etag
  - Model PrivateLinkServiceIpConfiguration has a new parameter type
  - Model PrivateLinkServiceIpConfiguration has a new parameter id
  - Model AzureFirewall has a new parameter virtual_hub
  - Model AzureFirewall has a new parameter hub_ip_addresses
  - Model AzureFirewall has a new parameter firewall_policy
  - Model PrivateLinkServiceConnection has a new parameter
    provisioning_state
  - Model PrivateLinkServiceConnection has a new parameter etag
  - Model PrivateLinkServiceConnection has a new parameter type
  - Model PublicIPPrefix has a new parameter
    load_balancer_frontend_ip_configuration
  - Model ApplicationGatewayOnDemandProbe has a new parameter
    backend_address_pool
  - Model ApplicationGatewayOnDemandProbe has a new parameter
    backend_http_settings
  - Model PrivateEndpointConnection has a new parameter
    provisioning_state
  - Model PrivateEndpointConnection has a new parameter etag
  - Model PrivateEndpointConnection has a new parameter type
  - Added operation SubnetsOperations.unprepare_network_policies
  - Added operation group FirewallPolicyRuleGroupsOperations
  - Added operation group FirewallPoliciesOperations

**Breaking changes**

  - Model PrivateLinkServiceIpConfiguration no longer has parameter
    public_ip_address
  - Model ApplicationGatewayOnDemandProbe no longer has parameter
    backend_pool_name
  - Model ApplicationGatewayOnDemandProbe no longer has parameter
    backend_http_setting_name

## 4.0.0 (2019-07-19)

**Features**

  - Model Subnet has a new parameter
    private_link_service_network_policies
  - Model Subnet has a new parameter
    private_endpoint_network_policies
  - Model VpnSite has a new parameter vpn_site_links
  - Model LoadBalancingRule has a new parameter type
  - Model BackendAddressPool has a new parameter outbound_rules
  - Model BackendAddressPool has a new parameter type
  - Model InboundNatPool has a new parameter type
  - Model OutboundRule has a new parameter type
  - Model InboundNatRule has a new parameter type
  - Model Probe has a new parameter type
  - Model FrontendIPConfiguration has a new parameter
    private_ip_address_version
  - Model FrontendIPConfiguration has a new parameter type
  - Model AvailablePrivateEndpointType has a new parameter name
  - Model AvailablePrivateEndpointType has a new parameter
    resource_name
  - Model VpnConnection has a new parameter vpn_link_connections
  - Added operation
    AvailablePrivateEndpointTypesOperations.list_by_resource_group
  - Added operation AzureFirewallsOperations.update_tags
  - Added operation
    PrivateLinkServicesOperations.check_private_link_service_visibility_by_resource_group
  - Added operation
    PrivateLinkServicesOperations.list_auto_approved_private_link_services
  - Added operation
    PrivateLinkServicesOperations.check_private_link_service_visibility
  - Added operation
    PrivateLinkServicesOperations.list_auto_approved_private_link_services_by_resource_group
  - Added operation group VpnLinkConnectionsOperations
  - Added operation group VpnSiteLinkConnectionsOperations
  - Added operation group VpnSiteLinksOperations

**Breaking changes**

  - Operation SubnetsOperations.prepare_network_policies has a new
    signature
  - Model PrepareNetworkPoliciesRequest no longer has parameter
    resource_group_name
  - Model AvailablePrivateEndpointType no longer has parameter
    service_name
  - Removed operation group
    AvailableResourceGroupPrivateEndpointTypesOperations

## 3.0.0 (2019-05-24)

**Features**

  - Model NetworkInterface has a new parameter private_endpoint
  - Model ServiceAssociationLink has a new parameter type
  - Model ServiceAssociationLink has a new parameter allow_delete
  - Model ServiceAssociationLink has a new parameter locations
  - Model Subnet has a new parameter private_endpoints
  - Model PatchRouteFilter has a new parameter ipv6_peerings
  - Model ExpressRouteCircuitPeering has a new parameter type
  - Model ApplicationGatewayProbe has a new parameter port
  - Model RouteFilter has a new parameter ipv6_peerings
  - Model ExpressRouteCircuitAuthorization has a new parameter type
  - Model PeerExpressRouteCircuitConnection has a new parameter type
  - Model AzureFirewall has a new parameter zones
  - Model ResourceNavigationLink has a new parameter type
  - Model ExpressRouteCircuitConnection has a new parameter type
  - Model VpnConnection has a new parameter
    use_policy_based_traffic_selectors
  - Model NatGateway has a new parameter zones
  - Model VpnClientConfiguration has a new parameter aad_audience
  - Model VpnClientConfiguration has a new parameter aad_issuer
  - Model VpnClientConfiguration has a new parameter aad_tenant
  - Added operation
    VirtualNetworkGatewaysOperations.get_vpnclient_connection_health
  - Added operation
    P2sVpnGatewaysOperations.get_p2s_vpn_connection_health
  - Added operation VpnGatewaysOperations.reset
  - Added operation group BastionHostsOperations
  - Added operation group NetworkManagementClientOperationsMixin
  - Added operation group PrivateLinkServicesOperations
  - Added operation group
    AvailableResourceGroupPrivateEndpointTypesOperations
  - Added operation group ServiceAssociationLinksOperations
  - Added operation group ResourceNavigationLinksOperations
  - Added operation group ServiceTagsOperations
  - Added operation group PrivateEndpointsOperations
  - Added operation group AvailablePrivateEndpointTypesOperations

**Breaking changes**

  - Model NetworkInterface no longer has parameter interface_endpoint
  - Model Subnet no longer has parameter interface_endpoints
  - Removed operation group InterfaceEndpointsOperations

**General Breaking changes**

This version uses a next-generation code generator that *might*
introduce breaking changes if you were importing from the v20xx_yy_zz
API folders. In summary, some modules were incorrectly
visible/importable and have been renamed. This fixed several issues
caused by usage of classes that were not supposed to be used in the
first place.

  - NetworkManagementClient cannot be imported from
    `azure.mgmt.network.v20xx_yy_zz.network_management_client`
    anymore (import from `azure.mgmt.network.v20xx_yy_zz` works like
    before)
  - NetworkManagementClientConfiguration import has been moved from
    `azure.mgmt.network.v20xx_yy_zz.network_management_client` to
    `azure.mgmt.network.v20xx_yy_zz`
  - A model `MyClass` from a "models" sub-module cannot be imported
    anymore using `azure.mgmt.network.v20xx_yy_zz.models.my_class`
    (import from `azure.mgmt.network.v20xx_yy_zz.models` works like
    before)
  - An operation class `MyClassOperations` from an `operations`
    sub-module cannot be imported anymore using
    `azure.mgmt.network.v20xx_yy_zz.operations.my_class_operations`
    (import from `azure.mgmt.network.v20xx_yy_zz.operations` works
    like before)

Last but not least, HTTP connection pooling is now enabled by default.
You should always use a client as a context manager, or call close(), or
use no more than one client per process.

## 2.7.0 (2019-04-25)

**Features**

  - Model P2SVpnGateway has a new parameter custom_routes
  - Model Subnet has a new parameter nat_gateway
  - Model VpnConnection has a new parameter
    use_local_azure_ip_address
  - Model EffectiveRoute has a new parameter
    disable_bgp_route_propagation
  - Model VirtualNetworkGateway has a new parameter custom_routes
  - Added operation
    ApplicationGatewaysOperations.backend_health_on_demand
  - Added operation DdosProtectionPlansOperations.update_tags
  - Added operation group NatGatewaysOperations

**Bug fixes and preview API updates**

  - Parameter output_blob_sas_url of model
    GetVpnSitesConfigurationRequest is now required
  - Operation VpnSitesConfigurationOperations.download has a new
    signature
  - Model ExpressRouteCircuit no longer has parameter
    allow_global_reach

## 2.6.0 (2019-03-21)

**Features**

  - Model ApplicationGateway has a new parameter firewall_policy
  - Model ApplicationGatewayBackendHealthServer has a new parameter
    health_probe_log
  - Model ExpressRouteCircuitPeering has a new parameter
    peered_connections
  - Model ExpressRouteCircuit has a new parameter global_reach_enabled
  - Added operation group PeerExpressRouteCircuitConnectionsOperations
  - Added operation group WebApplicationFirewallPoliciesOperations

**Bugfixes**

  - Fix incorrect operation
    ApplicationGatewaysOperations.list_available_request_headers
  - Fix incorrect operation
    ApplicationGatewaysOperations.list_available_server_variables
  - Fix incorrect operation
    ApplicationGatewaysOperations.list_available_response_headers

## 2.6.0rc1 (2019-02-15)

**Features**

  - Model AzureFirewall has a new parameter threat_intel_mode
  - Model ApplicationGatewayRewriteRule has a new parameter conditions
  - Model ApplicationGatewayRewriteRule has a new parameter
    rule_sequence
  - Model ApplicationGatewayAutoscaleConfiguration has a new parameter
    max_capacity
  - Added operation SubnetsOperations.prepare_network_policies

## 2.5.1 (2019-01-15)

**Features**

  - Add missing ddos_custom_policies operations

## 2.5.0 (2019-01-04)

**Features**

  - Model PublicIPAddress has a new parameter ddos_settings
  - Added operation
    ApplicationGatewaysOperations.list_available_request_headers
  - Added operation
    ApplicationGatewaysOperations.list_available_server_variables
  - Added operation
    ApplicationGatewaysOperations.list_available_response_headers
  - Added operation ApplicationSecurityGroupsOperations.update_tags

## 2.4.0 (2018-11-27)

**Features**

  - Model ApplicationGatewaySslCertificate has a new parameter
    key_vault_secret_id
  - Model ApplicationGatewayRequestRoutingRule has a new parameter
    rewrite_rule_set
  - Model FlowLogInformation has a new parameter format
  - Model ApplicationGateway has a new parameter identity
  - Model ApplicationGateway has a new parameter rewrite_rule_sets
  - Model TrafficAnalyticsConfigurationProperties has a new parameter
    traffic_analytics_interval
  - Model ApplicationGatewayPathRule has a new parameter
    rewrite_rule_set
  - Model ApplicationGatewayUrlPathMap has a new parameter
    default_rewrite_rule_set

**Breaking changes**

  - Model ApplicationGatewayTrustedRootCertificate no longer has
    parameter keyvault_secret_id (replaced by key_vault_secret_id)

## 2.3.0 (2018-11-07)

**Features**

  - Model ApplicationGatewayWebApplicationFirewallConfiguration has a
    new parameter exclusions
  - Model ApplicationGatewayWebApplicationFirewallConfiguration has a
    new parameter file_upload_limit_in_mb
  - Model ApplicationGatewayWebApplicationFirewallConfiguration has a
    new parameter max_request_body_size_in_kb
  - Model ApplicationGatewayHttpListener has a new parameter
    custom_error_configurations
  - Model ExpressRouteCircuit has a new parameter bandwidth_in_gbps
  - Model ExpressRouteCircuit has a new parameter stag
  - Model ExpressRouteCircuit has a new parameter express_route_port
  - Model EvaluatedNetworkSecurityGroup has a new parameter applied_to
  - Model NetworkConfigurationDiagnosticResult has a new parameter
    profile
  - Model ApplicationGateway has a new parameter
    custom_error_configurations
  - Added operation group LoadBalancerOutboundRulesOperations
  - Added operation group ExpressRouteLinksOperations
  - Added operation group ExpressRoutePortsOperations
  - Added operation group ExpressRoutePortsLocationsOperations

**Breaking changes**

  - Model NetworkConfigurationDiagnosticResult no longer has parameter
    traffic_query
  - Operation
    NetworkWatchersOperations.get_network_configuration_diagnostic
    has a new signature (no longer takes target_resource_id, queries,
    but a NetworkConfigurationDiagnosticParameters instance)

## 2.2.1 (2018-09-14)

**Bugfixes**

  - Fix unexpected exception with network_profiles.delete

## 2.2.0 (2018-09-11)

Default API version is now 2018-08-01

**Features**

  - Model AzureFirewall has a new parameter nat_rule_collections
  - Model VirtualHub has a new parameter route_table
  - Model VirtualHub has a new parameter virtual_network_connections
  - Model VirtualHub has a new parameter p2_svpn_gateway
  - Model VirtualHub has a new parameter express_route_gateway
  - Model VirtualHub has a new parameter vpn_gateway
  - Model VirtualWAN has a new parameter allow_vnet_to_vnet_traffic
  - Model VirtualWAN has a new parameter
    p2_svpn_server_configurations
  - Model VirtualWAN has a new parameter
    office365_local_breakout_category
  - Model VirtualWAN has a new parameter
    allow_branch_to_branch_traffic
  - Model VirtualWAN has a new parameter security_provider_name
  - Model VpnSite has a new parameter is_security_site
  - Model VpnConnection has a new parameter connection_bandwidth
  - Model VpnConnection has a new parameter enable_internet_security
  - Model VpnConnection has a new parameter
    vpn_connection_protocol_type
  - Model VpnConnection has a new parameter enable_rate_limiting
  - Model ServiceEndpointPolicy has a new parameter subnets
  - Model AzureFirewallApplicationRule has a new parameter fqdn_tags
  - Model AzureFirewallApplicationRule has a new parameter target_fqdns
  - Model VpnGateway has a new parameter vpn_gateway_scale_unit
  - Model ApplicationGatewayBackendHttpSettings has a new parameter
    trusted_root_certificates
  - Model VirtualNetworkGatewayConnection has a new parameter
    connection_protocol
  - Model ExpressRouteCircuitPeering has a new parameter
    express_route_connection
  - Model Subnet has a new parameter delegations
  - Model Subnet has a new parameter address_prefixes
  - Model Subnet has a new parameter ip_configuration_profiles
  - Model Subnet has a new parameter service_association_links
  - Model Subnet has a new parameter interface_endpoints
  - Model Subnet has a new parameter purpose
  - Model ApplicationGateway has a new parameter
    trusted_root_certificates
  - Model NetworkInterface has a new parameter tap_configurations
  - Model NetworkInterface has a new parameter hosted_workloads
  - Model NetworkInterface has a new parameter interface_endpoint
  - Model VirtualNetworkGatewayConnectionListEntity has a new parameter
    connection_protocol
  - Model HubVirtualNetworkConnection has a new parameter
    enable_internet_security
  - Model NetworkInterfaceIPConfiguration has a new parameter
    virtual_network_taps
  - Added operation
    VirtualNetworkGatewaysOperations.reset_vpn_client_shared_key
  - Added operation group ExpressRouteConnectionsOperations
  - Added operation group AzureFirewallFqdnTagsOperations
  - Added operation group VirtualNetworkTapsOperations
  - Added operation group NetworkProfilesOperations
  - Added operation group P2sVpnServerConfigurationsOperations
  - Added operation group AvailableDelegationsOperations
  - Added operation group InterfaceEndpointsOperations
  - Added operation group P2sVpnGatewaysOperations
  - Added operation group AvailableResourceGroupDelegationsOperations
  - Added operation group ExpressRouteGatewaysOperations
  - Added operation group NetworkInterfaceTapConfigurationsOperations

**Breaking changes**

  - Model VirtualHub no longer has parameter
    hub_virtual_network_connections
  - Model VpnConnection no longer has parameter
    connection_bandwidth_in_mbps
  - Model AzureFirewallApplicationRule no longer has parameter
    target_urls
  - Model VpnGateway no longer has parameter policies
  - Model AzureFirewallIPConfiguration no longer has parameter
    internal_public_ip_address
  - Model ApplicationGatewayAutoscaleConfiguration has a new signature
  - Renamed virtual_wa_ns to virtual_wans

## 2.1.0 (2018-08-28)

Default API version is now 2018-07-01

**Features**

  - Model ExpressRouteCircuit has a new parameter allow_global_reach
  - Model PublicIPAddress has a new parameter public_ip_prefix
  - Model BackendAddressPool has a new parameter outbound_rule
    (replaces outbound_nat_rule)
  - Model FrontendIPConfiguration has a new parameter outbound_rules
    (replaces outbound_nat_rule)
  - Model FrontendIPConfiguration has a new parameter public_ip_prefix
  - Model LoadBalancingRule has a new parameter enable_tcp_reset
  - Model VirtualNetworkGatewayConnectionListEntity has a new parameter
    express_route_gateway_bypass
  - Model VirtualNetworkGatewayConnection has a new parameter
    express_route_gateway_bypass
  - Model Subnet has a new parameter service_endpoint_policies
  - Model InboundNatPool has a new parameter enable_tcp_reset
  - Model LoadBalancer has a new parameter outbound_rules (replaces
    outbound_nat_rule)
  - Model InboundNatRule has a new parameter enable_tcp_reset
  - Added operation group ServiceEndpointPolicyDefinitionsOperations
  - Added operation group ServiceEndpointPoliciesOperations
  - Added operation group PublicIPPrefixesOperations

**Breaking changes**

  - Model BackendAddressPool no longer has parameter outbound_nat_rule
    (now outbound_rules)
  - Model FrontendIPConfiguration no longer has parameter
    outbound_nat_rules (now outbound_rules)
  - Model LoadBalancer no longer has parameter outbound_nat_rules (now
    outbound_rules)

## 2.0.1 (2018-08-07)

**Bugfixes**

  - Fix packet_captures.get_status empty output

## 2.0.0 (2018-07-27)

**Features**

  - Supports now 2018-06-01 and 2018-04-01. 2018-06-01 is the new
    default.
  - Client class can be used as a context manager to keep the underlying
    HTTP session open for performance

**Features starting 2018-04-01**

  - Model FlowLogInformation has a new parameter
    flow_analytics_configuration
  - Model ApplicationGateway has a new parameter enable_fips
  - Model ApplicationGateway has a new parameter
    autoscale_configuration
  - Model ApplicationGateway has a new parameter zones
  - Model ConnectionSharedKey has a new parameter id
  - Added operation group HubVirtualNetworkConnectionsOperations
  - Added operation group AzureFirewallsOperations
  - Added operation group VirtualHubsOperations
  - Added operation group VpnGatewaysOperations
  - Added operation group VpnSitesOperations
  - Added operation group VirtualWANsOperations
  - Added operation group VpnSitesConfigurationOperations
  - Added operation group VpnConnectionsOperations

**Breaking changes starting 2018-04-01**

  - Operation
    VirtualNetworkGatewayConnectionsOperations.set_shared_key has a
    new parameter "id"
  - Operation DdosProtectionPlansOperations.create_or_update parameter
    "parameters" has been flatten to "tags/location"

**Breaking changes starting 2018-06-01**

  - The new class VpnConnection introduced in 2018-04-01 renamed
    "connection_bandwidth" to "connection_bandwidth_in_mbps"

## 2.0.0rc3 (2018-06-14)

**Bugfixes**

  - API version 2018-02-01 enum Probe now supports HTTPS (standard SKU
    load balancer)
  - API version 2015-06-15 adding missing "primary" in
    NetworkInterfaceIPConfiguration

## 2.0.0rc2 (2018-04-03)

**Features**

  - All clients now support Azure profiles.
  - API version 2018-02-01 is now the default
  - Express Route Circuit Connection (considered preview)
  - Express Route Provider APIs
  - GetTopologyOperation supports query parameter
  - Feature work for setting Custom IPsec/IKE policy for Virtual Network
    Gateway point-to-site clients
  - DDoS Protection Plans

## 2.0.0rc1 (2018-03-07)

**General Breaking changes**

This version uses a next-generation code generator that *might*
introduce breaking changes.

  - Model signatures now use only keyword-argument syntax. All
    positional arguments must be re-written as keyword-arguments. To
    keep auto-completion in most cases, models are now generated for
    Python 2 and Python 3. Python 3 uses the "*" syntax for
    keyword-only arguments.
  - Enum types now use the "str" mixin (class AzureEnum(str, Enum)) to
    improve the behavior when unrecognized enum values are encountered.
    While this is not a breaking change, the distinctions are important,
    and are documented here:
    <https://docs.python.org/3/library/enum.html#others> At a glance:
      - "is" should not be used at all.
      - "format" will return the string value, where "%s" string
        formatting will return `NameOfEnum.stringvalue`. Format syntax
        should be prefered.
  - New Long Running Operation:
      - Return type changes from
        `msrestazure.azure_operation.AzureOperationPoller` to
        `msrest.polling.LROPoller`. External API is the same.
      - Return type is now **always** a `msrest.polling.LROPoller`,
        regardless of the optional parameters used.
      - The behavior has changed when using `raw=True`. Instead of
        returning the initial call result as `ClientRawResponse`,
        without polling, now this returns an LROPoller. After polling,
        the final resource will be returned as a `ClientRawResponse`.
      - New `polling` parameter. The default behavior is
        `Polling=True` which will poll using ARM algorithm. When
        `Polling=False`, the response of the initial call will be
        returned without polling.
      - `polling` parameter accepts instances of subclasses of
        `msrest.polling.PollingMethod`.
      - `add_done_callback` will no longer raise if called after
        polling is finished, but will instead execute the callback right
        away.

**Network Breaking changes**

  - Operation network_watcher.get_topology changed method signature

**Features**

  - Add API Version 2018-01-01. Not default yet in this version.
  - Add ConnectionMonitor operation group (2017-10/11-01)
  - Add target_virtual_network / target_subnet to topology_parameter
    (2017-10/11-01)
  - Add idle_timeout_in_minutes / enable_floating_ip to
    inbound_nat_pool (2017-11-01)

**Bugfixes**

  - Fix peer_asn validation rules (2017-10/11-01)

## 1.7.1 (2017-12-20)

**Bugfixes**

Fix `SecurityRule` constructor parameters order to respect the one
used until 1.5.0. This indeed introduces a breaking change for users of
1.6.0 and 1.7.0, but this constructor signature change was not expected,
and following semantic versionning all 1.x versions should follow the
same signature.

This fixes third party library, like Ansible, that expects (for
excellent reasons) this SDK to follow strictly semantic versionning with
regards to breaking changes and have their dependency system asking for
`>=1.0;<2.0`

## 1.7.0 (2017-12-14)

**Features**

  - Add iptag. IpTag is way to restrict the range of IPaddresses to be
    allocated.
  - Default API version is now 2017-11-01

**Bug fixes**

  - Added valid ASN range in ExpressRouteCircuitPeering (#1672)

## 1.6.0 (2017-11-28)

**Bug fixes**

  - Accept space in location for "usage" (i.e. "west us").
  - sourceAddressPrefix, sourceAddressPrefixes and
    sourceApplicationSecurityGroups are mutually exclusive and one only
    is needed, meaning none of them is required by itself. Thus,
    sourceAddressPrefix is not required anymore.
  - destinationAddressPrefix, destinationAddressPrefixes and
    destinationApplicationSecurityGroups are mutually exclusive and one
    only is needed, meaning none of them is required by itself. Thus,
    destinationAddressPrefix is not required anymore.
  - Client now accept unicode string as a valid subscription_id
    parameter
  - Restore missing azure.mgmt.network.__version__

**Features**

  - Client now accept a "profile" parameter to define API version per
    operation group.
  - Add update_tags to most of the resources
  - Add operations group to list all available rest API operations
  - NetworkInterfaces_ListVirtualMachineScaleSetIpConfigurations
  - NetworkInterfaces_GetVirtualMachineScaleSetIpConfiguration

## 1.5.0 (2017-09-26)

**Features**

  - Availability Zones
  - Add network_watchers.get_azure_reachability_report
  - Add network_watchers.list_available_providers
  - Add virtual_network_gateways.supported_vpn_devices
  - Add virtual_network_gateways.vpn_device_configuration_script

## 1.5.0rc1 (2017-09-18)

**Features**

  - Add ApiVersion 2017-09-01 (new default)
  - Add application_security_groups (ASG) operations group
  - Add ASG to network_interface operations
  - Add ASG to IP operations
  - Add source/destination ASGs to network security rules
  - Add DDOS protection and VM protection to vnet operations

**Bug fix**

  - check_dns_name_availability now correctly defines
    "domain_name_label" as required and not optional

## 1.4.0 (2017-08-23)

**Features**

  - Add ApiVersion 2017-08-01 (new default)
  - Added in both 2017-08-01 and 2017-06-01:
      - virtual_network_gateways.list_connections method
      - default_security_rules operations group
      - inbound_nat_rules operations group
      - load_balancer_backend_address_pools operations group
      - load_balancer_frontend_ip_configurations operations group
      - load_balancer_load_balancing_rules operations group
      - load_balancer_network_interfaces operations group
      - load_balancer_probes operations group
      - network_interface_ip_configurations operations group
      - network_interface_load_balancers operations group
      - EffectiveNetworkSecurityGroup.tag_map attribute
      - EffectiveNetworkSecurityRule.source_port_ranges attribute
      - EffectiveNetworkSecurityRule.destination_port_ranges attribute
      - EffectiveNetworkSecurityRule.source_address_prefixes attribute
      - EffectiveNetworkSecurityRule.destination_address_prefixes
        attribute
      - SecurityRule.source_port_ranges attribute
      - SecurityRule.destination_port_ranges attribute
      - SecurityRule.source_address_prefixes attribute
      - SecurityRule.destination_address_prefixes attribute
  - Added in 2017-08-01 only
      - PublicIPAddress.sku
      - LoadBalancer.sku

**Changes on preview**

>   - "available_private_access_services" is renamed
>     "available_endpoint_services"
>   - "radius_secret" parsing fix (was unable to work in 1.3.0)

## 1.3.0 (2017-07-10)

**Preview features**

  - Adding "available_private_access_services" operation group
    (preview)
  - Adding "radius_secret" in Virtual Network Gateway (preview)

**Bug Fixes**

  - VMSS Network ApiVersion fix in 2017-06-01 (point to 2017-03-30)

## 1.2.0 (2017-07-03)

**Features**

Adding the following features to both 2017-03-01 and 2017-06-01:

  - express route ipv6
  - VMSS Network (get, list, etc.)
  - VMSS Public IP (get, list, etc.)

## 1.1.0 (2017-06-27)

**Features**

  - Add list_usage in virtual networks (2017-03-01)
  - Add ApiVersion 2017-06-01 (new default)

This new ApiVersion is for new Application Gateway features:

>   - ApplicationGateway Ssl Policy custom cipher suites support [new
>     properties added to Sslpolicy Property of
>     ApplciationGatewayPropertiesFormat]
>   - Get AvailableSslOptions api [new resource
>     ApplicationGatewayAvailableSslOptions and child resource
>     ApplicationGatewayPredefinedPolicy]
>   - Redirection support [new child resource
>     ApplicationGatewayRedirectConfiguration for Application Gateway,
>     new properties in UrlPathMap, PathRules and RequestRoutingRule]
>   - Azure Websites feature support [new properties in
>     ApplicationGatewayBackendHttpSettingsPropertiesFormat,
>     ApplicationGatewayProbePropertiesFormat, schema for property
>     ApplicationGatewayProbeHealthResponseMatch]

## 1.0.0 (2017-05-15)

  - Tag 1.0.0rc3 as stable (same content)

## 1.0.0rc3 (2017-05-03)

**Features**

  - Added check connectivity api to network watcher

## 1.0.0rc2 (2017-04-18)

**Features**

  - Add ApiVersion 2016-12-01 and 2017-03-01
  - 2017-03-01 is now default ApiVersion

**Bugfixes**

  - Restore access to NetworkWatcher and PacketCapture from 2016-09-01

## 1.0.0rc1 (2017-04-11)

**Features**

To help customers with sovereign clouds (not general Azure), this
version has official multi ApiVersion support for 2015-06-15 and
2016-09-01

## 0.30.1 (2017-03-27)

  - Add NetworkWatcher
  - Add PacketCapture
  - Add new methods to Virtualk Network Gateway
      - get_bgp_peer_status
      - get_learned_routes
      - get_advertised_routes

## 0.30.0 (2016-11-01)

  - Initial preview release. Based on API version 2016-09-01.

## 0.20.0 (2015-08-31)

  - Initial preview release. Based on API version 2015-05-01-preview.
