# Release History

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
