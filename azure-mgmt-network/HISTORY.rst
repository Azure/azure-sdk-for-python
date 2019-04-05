.. :changelog:

Release History
===============

2.6.0 (2019-03-21)
++++++++++++++++++

**Features**

- Model ApplicationGateway has a new parameter firewall_policy
- Model ApplicationGatewayBackendHealthServer has a new parameter health_probe_log
- Model ExpressRouteCircuitPeering has a new parameter peered_connections
- Model ExpressRouteCircuit has a new parameter global_reach_enabled
- Added operation group PeerExpressRouteCircuitConnectionsOperations
- Added operation group WebApplicationFirewallPoliciesOperations

**Bugfixes**

- Fix incorrect operation ApplicationGatewaysOperations.list_available_request_headers
- Fix incorrect operation ApplicationGatewaysOperations.list_available_server_variables
- Fix incorrect operation ApplicationGatewaysOperations.list_available_response_headers

2.6.0rc1 (2019-02-15)
+++++++++++++++++++++

**Features**

- Model AzureFirewall has a new parameter threat_intel_mode
- Model ApplicationGatewayRewriteRule has a new parameter conditions
- Model ApplicationGatewayRewriteRule has a new parameter rule_sequence
- Model ApplicationGatewayAutoscaleConfiguration has a new parameter max_capacity
- Added operation SubnetsOperations.prepare_network_policies

2.5.1 (2019-01-15)
++++++++++++++++++

**Features**

- Add missing ddos_custom_policies operations

2.5.0 (2019-01-04)
++++++++++++++++++

**Features**

- Model PublicIPAddress has a new parameter ddos_settings
- Added operation ApplicationGatewaysOperations.list_available_request_headers
- Added operation ApplicationGatewaysOperations.list_available_server_variables
- Added operation ApplicationGatewaysOperations.list_available_response_headers
- Added operation ApplicationSecurityGroupsOperations.update_tags

2.4.0 (2018-11-27)
++++++++++++++++++

**Features**

- Model ApplicationGatewaySslCertificate has a new parameter key_vault_secret_id
- Model ApplicationGatewayRequestRoutingRule has a new parameter rewrite_rule_set
- Model FlowLogInformation has a new parameter format
- Model ApplicationGateway has a new parameter identity
- Model ApplicationGateway has a new parameter rewrite_rule_sets
- Model TrafficAnalyticsConfigurationProperties has a new parameter traffic_analytics_interval
- Model ApplicationGatewayPathRule has a new parameter rewrite_rule_set
- Model ApplicationGatewayUrlPathMap has a new parameter default_rewrite_rule_set

**Breaking changes**

- Model ApplicationGatewayTrustedRootCertificate no longer has parameter keyvault_secret_id (replaced by key_vault_secret_id)

2.3.0 (2018-11-07)
++++++++++++++++++

**Features**

- Model ApplicationGatewayWebApplicationFirewallConfiguration has a new parameter exclusions
- Model ApplicationGatewayWebApplicationFirewallConfiguration has a new parameter file_upload_limit_in_mb
- Model ApplicationGatewayWebApplicationFirewallConfiguration has a new parameter max_request_body_size_in_kb
- Model ApplicationGatewayHttpListener has a new parameter custom_error_configurations
- Model ExpressRouteCircuit has a new parameter bandwidth_in_gbps
- Model ExpressRouteCircuit has a new parameter stag
- Model ExpressRouteCircuit has a new parameter express_route_port
- Model EvaluatedNetworkSecurityGroup has a new parameter applied_to
- Model NetworkConfigurationDiagnosticResult has a new parameter profile
- Model ApplicationGateway has a new parameter custom_error_configurations
- Added operation group LoadBalancerOutboundRulesOperations
- Added operation group ExpressRouteLinksOperations
- Added operation group ExpressRoutePortsOperations
- Added operation group ExpressRoutePortsLocationsOperations

**Breaking changes**

- Model NetworkConfigurationDiagnosticResult no longer has parameter traffic_query
- Operation NetworkWatchersOperations.get_network_configuration_diagnostic has a new signature (no longer takes target_resource_id, queries, but a NetworkConfigurationDiagnosticParameters instance)

2.2.1 (2018-09-14)
++++++++++++++++++

**Bugfixes**

- Fix unexpected exception with network_profiles.delete

2.2.0 (2018-09-11)
++++++++++++++++++

Default API version is now 2018-08-01

**Features**

- Model AzureFirewall has a new parameter nat_rule_collections
- Model VirtualHub has a new parameter route_table
- Model VirtualHub has a new parameter virtual_network_connections
- Model VirtualHub has a new parameter p2_svpn_gateway
- Model VirtualHub has a new parameter express_route_gateway
- Model VirtualHub has a new parameter vpn_gateway
- Model VirtualWAN has a new parameter allow_vnet_to_vnet_traffic
- Model VirtualWAN has a new parameter p2_svpn_server_configurations
- Model VirtualWAN has a new parameter office365_local_breakout_category
- Model VirtualWAN has a new parameter allow_branch_to_branch_traffic
- Model VirtualWAN has a new parameter security_provider_name
- Model VpnSite has a new parameter is_security_site
- Model VpnConnection has a new parameter connection_bandwidth
- Model VpnConnection has a new parameter enable_internet_security
- Model VpnConnection has a new parameter vpn_connection_protocol_type
- Model VpnConnection has a new parameter enable_rate_limiting
- Model ServiceEndpointPolicy has a new parameter subnets
- Model AzureFirewallApplicationRule has a new parameter fqdn_tags
- Model AzureFirewallApplicationRule has a new parameter target_fqdns
- Model VpnGateway has a new parameter vpn_gateway_scale_unit
- Model ApplicationGatewayBackendHttpSettings has a new parameter trusted_root_certificates
- Model VirtualNetworkGatewayConnection has a new parameter connection_protocol
- Model ExpressRouteCircuitPeering has a new parameter express_route_connection
- Model Subnet has a new parameter delegations
- Model Subnet has a new parameter address_prefixes
- Model Subnet has a new parameter ip_configuration_profiles
- Model Subnet has a new parameter service_association_links
- Model Subnet has a new parameter interface_endpoints
- Model Subnet has a new parameter purpose
- Model ApplicationGateway has a new parameter trusted_root_certificates
- Model NetworkInterface has a new parameter tap_configurations
- Model NetworkInterface has a new parameter hosted_workloads
- Model NetworkInterface has a new parameter interface_endpoint
- Model VirtualNetworkGatewayConnectionListEntity has a new parameter connection_protocol
- Model HubVirtualNetworkConnection has a new parameter enable_internet_security
- Model NetworkInterfaceIPConfiguration has a new parameter virtual_network_taps
- Added operation VirtualNetworkGatewaysOperations.reset_vpn_client_shared_key
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

- Model VirtualHub no longer has parameter hub_virtual_network_connections
- Model VpnConnection no longer has parameter connection_bandwidth_in_mbps
- Model AzureFirewallApplicationRule no longer has parameter target_urls
- Model VpnGateway no longer has parameter policies
- Model AzureFirewallIPConfiguration no longer has parameter internal_public_ip_address
- Model ApplicationGatewayAutoscaleConfiguration has a new signature
- Renamed virtual_wa_ns to virtual_wans

2.1.0 (2018-08-28)
++++++++++++++++++

Default API version is now 2018-07-01

**Features**

- Model ExpressRouteCircuit has a new parameter allow_global_reach
- Model PublicIPAddress has a new parameter public_ip_prefix
- Model BackendAddressPool has a new parameter outbound_rule (replaces outbound_nat_rule)
- Model FrontendIPConfiguration has a new parameter outbound_rules (replaces outbound_nat_rule)
- Model FrontendIPConfiguration has a new parameter public_ip_prefix
- Model LoadBalancingRule has a new parameter enable_tcp_reset
- Model VirtualNetworkGatewayConnectionListEntity has a new parameter express_route_gateway_bypass
- Model VirtualNetworkGatewayConnection has a new parameter express_route_gateway_bypass
- Model Subnet has a new parameter service_endpoint_policies
- Model InboundNatPool has a new parameter enable_tcp_reset
- Model LoadBalancer has a new parameter outbound_rules (replaces outbound_nat_rule)
- Model InboundNatRule has a new parameter enable_tcp_reset
- Added operation group ServiceEndpointPolicyDefinitionsOperations
- Added operation group ServiceEndpointPoliciesOperations
- Added operation group PublicIPPrefixesOperations

**Breaking changes**

- Model BackendAddressPool no longer has parameter outbound_nat_rule (now outbound_rules)
- Model FrontendIPConfiguration no longer has parameter outbound_nat_rules (now outbound_rules)
- Model LoadBalancer no longer has parameter outbound_nat_rules (now outbound_rules)

2.0.1 (2018-08-07)
++++++++++++++++++

**Bugfixes**

- Fix packet_captures.get_status empty output

2.0.0 (2018-07-27)
++++++++++++++++++

**Features**

- Supports now 2018-06-01 and 2018-04-01. 2018-06-01 is the new default.
- Client class can be used as a context manager to keep the underlying HTTP session open for performance

**Features starting 2018-04-01**

- Model FlowLogInformation has a new parameter flow_analytics_configuration
- Model ApplicationGateway has a new parameter enable_fips
- Model ApplicationGateway has a new parameter autoscale_configuration
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

- Operation VirtualNetworkGatewayConnectionsOperations.set_shared_key has a new parameter "id"
- Operation DdosProtectionPlansOperations.create_or_update parameter "parameters" has been flatten to "tags/location"

**Breaking changes starting 2018-06-01**

- The new class VpnConnection introduced in 2018-04-01 renamed "connection_bandwidth" to "connection_bandwidth_in_mbps"

2.0.0rc3 (2018-06-14)
+++++++++++++++++++++

**Bugfixes**

- API version 2018-02-01 enum Probe now supports HTTPS (standard SKU load balancer)
- API version 2015-06-15 adding missing "primary" in NetworkInterfaceIPConfiguration

2.0.0rc2 (2018-04-03)
+++++++++++++++++++++

**Features**

- All clients now support Azure profiles.
- API version 2018-02-01 is now the default
- Express Route Circuit Connection (considered preview)
- Express Route Provider APIs
- GetTopologyOperation supports query parameter
- Feature work for setting Custom IPsec/IKE policy for Virtual Network Gateway point-to-site clients
- DDoS Protection Plans

2.0.0rc1 (2018-03-07)
+++++++++++++++++++++

**General Breaking changes**

This version uses a next-generation code generator that *might* introduce breaking changes.

- Model signatures now use only keyword-argument syntax. All positional arguments must be re-written as keyword-arguments.
  To keep auto-completion in most cases, models are now generated for Python 2 and Python 3. Python 3 uses the "*" syntax for keyword-only arguments.
- Enum types now use the "str" mixin (class AzureEnum(str, Enum)) to improve the behavior when unrecognized enum values are encountered.
  While this is not a breaking change, the distinctions are important, and are documented here:
  https://docs.python.org/3/library/enum.html#others
  At a glance:

  - "is" should not be used at all.
  - "format" will return the string value, where "%s" string formatting will return `NameOfEnum.stringvalue`. Format syntax should be prefered.

- New Long Running Operation:

  - Return type changes from `msrestazure.azure_operation.AzureOperationPoller` to `msrest.polling.LROPoller`. External API is the same.
  - Return type is now **always** a `msrest.polling.LROPoller`, regardless of the optional parameters used.
  - The behavior has changed when using `raw=True`. Instead of returning the initial call result as `ClientRawResponse`,
    without polling, now this returns an LROPoller. After polling, the final resource will be returned as a `ClientRawResponse`.
  - New `polling` parameter. The default behavior is `Polling=True` which will poll using ARM algorithm. When `Polling=False`,
    the response of the initial call will be returned without polling.
  - `polling` parameter accepts instances of subclasses of `msrest.polling.PollingMethod`.
  - `add_done_callback` will no longer raise if called after polling is finished, but will instead execute the callback right away.

**Network Breaking changes**

- Operation network_watcher.get_topology changed method signature

**Features**

- Add API Version 2018-01-01. Not default yet in this version.
- Add ConnectionMonitor operation group (2017-10/11-01)
- Add target_virtual_network / target_subnet to topology_parameter (2017-10/11-01)
- Add idle_timeout_in_minutes / enable_floating_ip to inbound_nat_pool (2017-11-01)

**Bugfixes**

- Fix peer_asn validation rules (2017-10/11-01)

1.7.1 (2017-12-20)
++++++++++++++++++

**Bugfixes**

Fix `SecurityRule` constructor parameters order to respect the one used until 1.5.0.
This indeed introduces a breaking change for users of 1.6.0 and 1.7.0, but this constructor signature change was
not expected, and following semantic versionning all 1.x versions should follow the same signature.

This fixes third party library, like Ansible, that expects (for excellent reasons) this SDK to follow strictly semantic versionning
with regards to breaking changes and have their dependency system asking for `>=1.0;<2.0`

1.7.0 (2017-12-14)
++++++++++++++++++

**Features**

- Add iptag. IpTag is way to restrict the range of IPaddresses to be allocated.
- Default API version is now 2017-11-01

**Bug fixes**

- Added valid ASN range in ExpressRouteCircuitPeering (#1672)

1.6.0 (2017-11-28)
++++++++++++++++++

**Bug fixes**

- Accept space in location for "usage" (i.e. "west us").
- sourceAddressPrefix, sourceAddressPrefixes and sourceApplicationSecurityGroups
  are mutually exclusive and one only is needed, meaning none of them is required
  by itself. Thus, sourceAddressPrefix is not required anymore.
- destinationAddressPrefix, destinationAddressPrefixes and destinationApplicationSecurityGroups
  are mutually exclusive and one only is needed, meaning none of them is required
  by itself. Thus, destinationAddressPrefix is not required anymore.
- Client now accept unicode string as a valid subscription_id parameter
- Restore missing azure.mgmt.network.__version__

**Features**

- Client now accept a "profile" parameter to define API version per operation group.
- Add update_tags to most of the resources
- Add operations group to list all available rest API operations
- NetworkInterfaces_ListVirtualMachineScaleSetIpConfigurations
- NetworkInterfaces_GetVirtualMachineScaleSetIpConfiguration

1.5.0 (2017-09-26)
++++++++++++++++++

**Features**

- Availability Zones
- Add network_watchers.get_azure_reachability_report
- Add network_watchers.list_available_providers
- Add virtual_network_gateways.supported_vpn_devices
- Add virtual_network_gateways.vpn_device_configuration_script

1.5.0rc1 (2017-09-18)
+++++++++++++++++++++

**Features**

- Add ApiVersion 2017-09-01 (new default)
- Add application_security_groups (ASG) operations group
- Add ASG to network_interface operations
- Add ASG to IP operations
- Add source/destination ASGs to network security rules
- Add DDOS protection and VM protection to vnet operations

**Bug fix**

- check_dns_name_availability now correctly defines "domain_name_label" as required and not optional

1.4.0 (2017-08-23)
++++++++++++++++++

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
  - EffectiveNetworkSecurityRule.destination_address_prefixes attribute
  - SecurityRule.source_port_ranges attribute
  - SecurityRule.destination_port_ranges attribute
  - SecurityRule.source_address_prefixes attribute
  - SecurityRule.destination_address_prefixes attribute

- Added in 2017-08-01 only

  - PublicIPAddress.sku
  - LoadBalancer.sku

**Changes on preview**

  - "available_private_access_services" is renamed "available_endpoint_services"
  - "radius_secret" parsing fix (was unable to work in 1.3.0)


1.3.0 (2017-07-10)
++++++++++++++++++

**Preview features**

- Adding "available_private_access_services" operation group (preview)
- Adding "radius_secret" in Virtual Network Gateway (preview)

**Bug Fixes**

- VMSS Network ApiVersion fix in 2017-06-01 (point to 2017-03-30)

1.2.0 (2017-07-03)
++++++++++++++++++

**Features**

Adding the following features to both 2017-03-01 and 2017-06-01:

- express route ipv6
- VMSS Network (get, list, etc.)
- VMSS Public IP (get, list, etc.)

1.1.0 (2017-06-27)
++++++++++++++++++

**Features**

- Add list_usage in virtual networks (2017-03-01)

- Add ApiVersion 2017-06-01 (new default)

This new ApiVersion is for new Application Gateway features:

  - ApplicationGateway Ssl Policy custom cipher suites support [new properties added to Sslpolicy Property of ApplciationGatewayPropertiesFormat]
  - Get AvailableSslOptions api [new resource ApplicationGatewayAvailableSslOptions and child resource ApplicationGatewayPredefinedPolicy]
  - Redirection support [new child resource ApplicationGatewayRedirectConfiguration for Application Gateway,
    new properties in UrlPathMap, PathRules and RequestRoutingRule]
  - Azure Websites feature support [new properties in ApplicationGatewayBackendHttpSettingsPropertiesFormat,
    ApplicationGatewayProbePropertiesFormat, schema for property ApplicationGatewayProbeHealthResponseMatch]

1.0.0 (2017-05-15)
++++++++++++++++++

- Tag 1.0.0rc3 as stable (same content)

1.0.0rc3 (2017-05-03)
+++++++++++++++++++++

**Features**

- Added check connectivity api to network watcher

1.0.0rc2 (2017-04-18)
+++++++++++++++++++++

**Features**

- Add ApiVersion 2016-12-01 and 2017-03-01
- 2017-03-01 is now default ApiVersion

**Bugfixes**

- Restore access to NetworkWatcher and PacketCapture from 2016-09-01

1.0.0rc1 (2017-04-11)
+++++++++++++++++++++

**Features**

To help customers with sovereign clouds (not general Azure),
this version has official multi ApiVersion support for 2015-06-15 and 2016-09-01

0.30.1 (2017-03-27)
+++++++++++++++++++

* Add NetworkWatcher
* Add PacketCapture
* Add new methods to Virtualk Network Gateway

  * get_bgp_peer_status
  * get_learned_routes
  * get_advertised_routes

0.30.0 (2016-11-01)
+++++++++++++++++++

* Initial preview release. Based on API version 2016-09-01.


0.20.0 (2015-08-31)
+++++++++++++++++++

* Initial preview release. Based on API version 2015-05-01-preview.
