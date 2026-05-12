# Release History

## 31.0.0b1 (2026-05-08)

### Features Added

  - Client `NetworkManagementClient` added method `send_request`
  - Added model `CloudError`
  - Added model `DefaultRuleSetPropertyFormat`
  - Added model `ManagedServiceIdentityUserAssignedIdentities`
  - Added model `ProxyResourceWithReadOnlyID`
  - Added model `ProxyResourceWithSettableId`
  - Added model `ReadOnlySubResourceModel`
  - Added model `SecurityPerimeterTrackedResource`
  - Added model `SubResourceModel`
  - Added model `TrackedResourceWithEtag`
  - Added model `TrackedResourceWithOptionalLocation`
  - Added model `TrackedResourceWithSettableIdOptionalLocation`
  - Added model `TrackedResourceWithSettableName`
  - Added model `WritableResource`

### Breaking Changes

  - This version introduces new hybrid models which have dual dictionary and model nature. Please follow https://aka.ms/azsdk/python/migrate/hybrid-models for migration.
  - For the method breakings, please refer to https://aka.ms/azsdk/python/migrate/operations for migration.
  - Method `IpamPoolsOperations.begin_create` replaced positional_or_keyword `if_match` to keyword_only `etag`/`match_condition`
  - Method `IpamPoolsOperations.begin_delete` replaced positional_or_keyword `if_match` to keyword_only `etag`/`match_condition`
  - Method `IpamPoolsOperations.update` replaced positional_or_keyword `if_match` to keyword_only `etag`/`match_condition`
  - Method `NetworkGroupsOperations.create_or_update` replaced positional_or_keyword `if_match` to keyword_only `etag`/`match_condition`
  - Method `VerifierWorkspacesOperations.begin_delete` replaced positional_or_keyword `if_match` to keyword_only `etag`/`match_condition`
  - Method `VerifierWorkspacesOperations.create` replaced positional_or_keyword `if_match` to keyword_only `etag`/`match_condition`
  - Method `VerifierWorkspacesOperations.update` replaced positional_or_keyword `if_match` to keyword_only `etag`/`match_condition`
  - Model `ConnectionMonitorEndpointFilter` renamed its instance variable `items` to `items_property`
  - Model `ExceptionEntry` renamed its instance variable `values` to `values_property`
  - Model `FilterItems` renamed its instance variable `values` to `values_property`
  - Model `ServiceTagsListResult` renamed its instance variable `values` to `values_property`
  - Model `AdminRule` moved instance variable `description`, `protocol`, `sources`, `destinations`, `source_port_ranges`, `destination_port_ranges`, `access`, `priority`, `direction`, `provisioning_state` and `resource_guid` under property `properties` whose type is `AdminPropertiesFormat`
  - Model `AdminRuleCollection` moved instance variable `description`, `applies_to_groups`, `provisioning_state` and `resource_guid` under property `properties` whose type is `AdminRuleCollectionPropertiesFormat`
  - Model `ApplicationGateway` moved instance variable `sku`, `ssl_policy`, `operational_state`, `gateway_ip_configurations`, `authentication_certificates`, `trusted_root_certificates`, `trusted_client_certificates`, `ssl_certificates`, `frontend_ip_configurations`, `frontend_ports`, `probes`, `backend_address_pools`, `backend_http_settings_collection`, `backend_settings_collection`, `http_listeners`, `listeners`, `ssl_profiles`, `url_path_maps`, `request_routing_rules`, `routing_rules`, `rewrite_rule_sets`, `redirect_configurations`, `web_application_firewall_configuration`, `firewall_policy`, `enable_http2`, `enable_fips`, `autoscale_configuration`, `private_link_configurations`, `private_endpoint_connections`, `resource_guid`, `provisioning_state`, `custom_error_configurations`, `force_firewall_policy_association`, `load_distribution_policies`, `entra_jwt_validation_configs`, `global_configuration` and `default_predefined_ssl_policy` under property `properties` whose type is `ApplicationGatewayPropertiesFormat`
  - Model `ApplicationGatewayAuthenticationCertificate` moved instance variable `data` and `provisioning_state` under property `properties` whose type is `ApplicationGatewayAuthenticationCertificatePropertiesFormat`
  - Model `ApplicationGatewayAvailableSslOptions` moved instance variable `predefined_policies`, `default_policy`, `available_cipher_suites` and `available_protocols` under property `properties` whose type is `ApplicationGatewayAvailableSslOptionsPropertiesFormat`
  - Model `ApplicationGatewayBackendAddressPool` moved instance variable `backend_ip_configurations`, `backend_addresses` and `provisioning_state` under property `properties` whose type is `ApplicationGatewayBackendAddressPoolPropertiesFormat`
  - Model `ApplicationGatewayBackendHttpSettings` moved instance variable `port`, `protocol`, `cookie_based_affinity`, `request_timeout`, `probe`, `authentication_certificates`, `trusted_root_certificates`, `connection_draining`, `host_name`, `pick_host_name_from_backend_address`, `affinity_cookie_name`, `probe_enabled`, `path`, `dedicated_backend_connection`, `validate_cert_chain_and_expiry`, `validate_sni`, `sni_name` and `provisioning_state` under property `properties` whose type is `ApplicationGatewayBackendHttpSettingsPropertiesFormat`
  - Model `ApplicationGatewayBackendSettings` moved instance variable `port`, `protocol`, `timeout`, `probe`, `trusted_root_certificates`, `host_name`, `pick_host_name_from_backend_address`, `enable_l4_client_ip_preservation` and `provisioning_state` under property `properties` whose type is `ApplicationGatewayBackendSettingsPropertiesFormat`
  - Model `ApplicationGatewayEntraJWTValidationConfig` moved instance variable `un_authorized_request_action`, `tenant_id`, `client_id`, `audiences` and `provisioning_state` under property `properties` whose type is `ApplicationGatewayEntraJWTValidationConfigPropertiesFormat`
  - Model `ApplicationGatewayFirewallRuleSet` moved instance variable `provisioning_state`, `rule_set_type`, `rule_set_version`, `rule_groups` and `tiers` under property `properties` whose type is `ApplicationGatewayFirewallRuleSetPropertiesFormat`
  - Model `ApplicationGatewayFrontendIPConfiguration` moved instance variable `private_ip_address`, `private_ip_allocation_method`, `subnet`, `public_ip_address`, `private_link_configuration` and `provisioning_state` under property `properties` whose type is `ApplicationGatewayFrontendIPConfigurationPropertiesFormat`
  - Model `ApplicationGatewayFrontendPort` moved instance variable `port` and `provisioning_state` under property `properties` whose type is `ApplicationGatewayFrontendPortPropertiesFormat`
  - Model `ApplicationGatewayHttpListener` moved instance variable `frontend_ip_configuration`, `frontend_port`, `protocol`, `host_name`, `ssl_certificate`, `ssl_profile`, `require_server_name_indication`, `provisioning_state`, `custom_error_configurations`, `firewall_policy` and `host_names` under property `properties` whose type is `ApplicationGatewayHttpListenerPropertiesFormat`
  - Model `ApplicationGatewayIPConfiguration` moved instance variable `subnet` and `provisioning_state` under property `properties` whose type is `ApplicationGatewayIPConfigurationPropertiesFormat`
  - Model `ApplicationGatewayListener` moved instance variable `frontend_ip_configuration`, `frontend_port`, `protocol`, `ssl_certificate`, `ssl_profile`, `provisioning_state` and `host_names` under property `properties` whose type is `ApplicationGatewayListenerPropertiesFormat`
  - Model `ApplicationGatewayLoadDistributionPolicy` moved instance variable `load_distribution_targets`, `load_distribution_algorithm` and `provisioning_state` under property `properties` whose type is `ApplicationGatewayLoadDistributionPolicyPropertiesFormat`
  - Model `ApplicationGatewayLoadDistributionTarget` moved instance variable `weight_per_server` and `backend_address_pool` under property `properties` whose type is `ApplicationGatewayLoadDistributionTargetPropertiesFormat`
  - Model `ApplicationGatewayPathRule` moved instance variable `paths`, `backend_address_pool`, `backend_http_settings`, `redirect_configuration`, `rewrite_rule_set`, `load_distribution_policy`, `provisioning_state` and `firewall_policy` under property `properties` whose type is `ApplicationGatewayPathRulePropertiesFormat`
  - Model `ApplicationGatewayProbe` moved instance variable `protocol`, `host`, `path`, `interval`, `timeout`, `unhealthy_threshold`, `pick_host_name_from_backend_http_settings`, `pick_host_name_from_backend_settings`, `min_servers`, `match`, `enable_probe_proxy_protocol_header`, `provisioning_state` and `port` under property `properties` whose type is `ApplicationGatewayProbePropertiesFormat`
  - Model `ApplicationGatewayRedirectConfiguration` moved instance variable `redirect_type`, `target_listener`, `target_url`, `include_path`, `include_query_string`, `request_routing_rules`, `url_path_maps` and `path_rules` under property `properties` whose type is `ApplicationGatewayRedirectConfigurationPropertiesFormat`
  - Model `ApplicationGatewayRequestRoutingRule` moved instance variable `rule_type`, `priority`, `backend_address_pool`, `backend_http_settings`, `http_listener`, `url_path_map`, `rewrite_rule_set`, `redirect_configuration`, `load_distribution_policy`, `entra_jwt_validation_config` and `provisioning_state` under property `properties` whose type is `ApplicationGatewayRequestRoutingRulePropertiesFormat`
  - Model `ApplicationGatewayRewriteRuleSet` moved instance variable `rewrite_rules` and `provisioning_state` under property `properties` whose type is `ApplicationGatewayRewriteRuleSetPropertiesFormat`
  - Model `ApplicationGatewayRoutingRule` moved instance variable `rule_type`, `priority`, `backend_address_pool`, `backend_settings`, `listener` and `provisioning_state` under property `properties` whose type is `ApplicationGatewayRoutingRulePropertiesFormat`
  - Model `ApplicationGatewaySslCertificate` moved instance variable `data`, `password`, `public_cert_data`, `key_vault_secret_id` and `provisioning_state` under property `properties` whose type is `ApplicationGatewaySslCertificatePropertiesFormat`
  - Model `ApplicationGatewaySslPredefinedPolicy` moved instance variable `cipher_suites` and `min_protocol_version` under property `properties` whose type is `ApplicationGatewaySslPredefinedPolicyPropertiesFormat`
  - Model `ApplicationGatewaySslProfile` moved instance variable `trusted_client_certificates`, `ssl_policy`, `client_auth_configuration` and `provisioning_state` under property `properties` whose type is `ApplicationGatewaySslProfilePropertiesFormat`
  - Model `ApplicationGatewayTrustedClientCertificate` moved instance variable `data`, `validated_cert_data`, `client_cert_issuer_dn` and `provisioning_state` under property `properties` whose type is `ApplicationGatewayTrustedClientCertificatePropertiesFormat`
  - Model `ApplicationGatewayTrustedRootCertificate` moved instance variable `data`, `key_vault_secret_id` and `provisioning_state` under property `properties` whose type is `ApplicationGatewayTrustedRootCertificatePropertiesFormat`
  - Model `ApplicationGatewayUrlPathMap` moved instance variable `default_backend_address_pool`, `default_backend_http_settings`, `default_rewrite_rule_set`, `default_redirect_configuration`, `default_load_distribution_policy`, `path_rules` and `provisioning_state` under property `properties` whose type is `ApplicationGatewayUrlPathMapPropertiesFormat`
  - Model `ApplicationGatewayWafDynamicManifestResult` moved instance variable `available_rule_sets`, `rule_set_type` and `rule_set_version` under property `properties` whose type is `ApplicationGatewayWafDynamicManifestPropertiesResult`
  - Model `ApplicationSecurityGroup` moved instance variable `resource_guid` and `provisioning_state` under property `properties` whose type is `ApplicationSecurityGroupPropertiesFormat`
  - Model `AzureFirewall` moved instance variable `application_rule_collections`, `nat_rule_collections`, `network_rule_collections`, `ip_configurations`, `management_ip_configuration`, `provisioning_state`, `threat_intel_mode`, `virtual_hub`, `firewall_policy`, `hub_ip_addresses`, `ip_groups`, `sku` and `autoscale_configuration` under property `properties` whose type is `AzureFirewallPropertiesFormat`
  - Model `AzureFirewallApplicationRuleCollection` moved instance variable `priority`, `action`, `rules` and `provisioning_state` under property `properties` whose type is `AzureFirewallApplicationRuleCollectionPropertiesFormat`
  - Model `AzureFirewallFqdnTag` moved instance variable `provisioning_state` and `fqdn_tag_name` under property `properties` whose type is `AzureFirewallFqdnTagPropertiesFormat`
  - Model `AzureFirewallIPConfiguration` moved instance variable `private_ip_address`, `subnet`, `public_ip_address` and `provisioning_state` under property `properties` whose type is `AzureFirewallIPConfigurationPropertiesFormat`
  - Model `AzureFirewallNetworkRuleCollection` moved instance variable `priority`, `action`, `rules` and `provisioning_state` under property `properties` whose type is `AzureFirewallNetworkRuleCollectionPropertiesFormat`
  - Model `AzureWebCategory` moved instance variable `group` under property `properties` whose type is `AzureWebCategoryPropertiesFormat`
  - Model `BackendAddressPool` moved instance variable `location`, `tunnel_interfaces`, `load_balancer_backend_addresses`, `backend_ip_configurations`, `load_balancing_rules`, `outbound_rule`, `outbound_rules`, `inbound_nat_rules`, `provisioning_state`, `drain_period_in_seconds`, `virtual_network` and `sync_mode` under property `properties` whose type is `BackendAddressPoolPropertiesFormat`
  - Model `BastionHost` moved instance variable `ip_configurations`, `dns_name`, `virtual_network`, `network_acls`, `provisioning_state`, `scale_units`, `disable_copy_paste`, `enable_file_copy`, `enable_ip_connect`, `enable_shareable_link`, `enable_tunneling`, `enable_kerberos`, `enable_session_recording` and `enable_private_only_bastion` under property `properties` whose type is `BastionHostPropertiesFormat`
  - Model `BastionHostIPConfiguration` moved instance variable `subnet`, `public_ip_address`, `provisioning_state` and `private_ip_allocation_method` under property `properties` whose type is `BastionHostIPConfigurationPropertiesFormat`
  - Model `BgpServiceCommunity` moved instance variable `service_name` and `bgp_communities` under property `properties` whose type is `BgpServiceCommunityPropertiesFormat`
  - Model `ContainerNetworkInterface` moved instance variable `container_network_interface_configuration`, `container`, `ip_configurations` and `provisioning_state` under property `properties` whose type is `ContainerNetworkInterfacePropertiesFormat`
  - Model `ContainerNetworkInterfaceConfiguration` moved instance variable `ip_configurations`, `container_network_interfaces` and `provisioning_state` under property `properties` whose type is `ContainerNetworkInterfaceConfigurationPropertiesFormat`
  - Model `ContainerNetworkInterfaceIpConfiguration` moved instance variable `provisioning_state` under property `properties` whose type is `ContainerNetworkInterfaceIpConfigurationPropertiesFormat`
  - Model `CustomIpPrefix` moved instance variable `asn`, `cidr`, `signed_message`, `authorization_message`, `custom_ip_prefix_parent`, `child_custom_ip_prefixes`, `commissioned_state`, `express_route_advertise`, `geo`, `no_internet_advertise`, `prefix_type`, `public_ip_prefixes`, `resource_guid`, `failed_reason` and `provisioning_state` under property `properties` whose type is `CustomIpPrefixPropertiesFormat`
  - Model `DdosCustomPolicy` moved instance variable `resource_guid`, `provisioning_state`, `detection_rules` and `front_end_ip_configuration` under property `properties` whose type is `DdosCustomPolicyPropertiesFormat`
  - Model `DdosDetectionRule` moved instance variable `provisioning_state`, `detection_mode` and `traffic_detection_rule` under property `properties` whose type is `DdosDetectionRulePropertiesFormat`
  - Model `DdosProtectionPlan` moved instance variable `resource_guid`, `provisioning_state`, `public_ip_addresses` and `virtual_networks` under property `properties` whose type is `DdosProtectionPlanPropertiesFormat`
  - Model `DefaultAdminRule` moved instance variable `description`, `flag`, `protocol`, `sources`, `destinations`, `source_port_ranges`, `destination_port_ranges`, `access`, `priority`, `direction`, `provisioning_state` and `resource_guid` under property `properties` whose type is `DefaultAdminPropertiesFormat`
  - Model `Delegation` moved instance variable `service_name`, `actions` and `provisioning_state` under property `properties` whose type is `ServiceDelegationPropertiesFormat`
  - Model `DscpConfiguration` moved instance variable `markings`, `source_ip_ranges`, `destination_ip_ranges`, `source_port_ranges`, `destination_port_ranges`, `protocol`, `qos_definition_collection`, `qos_collection_id`, `associated_network_interfaces`, `resource_guid` and `provisioning_state` under property `properties` whose type is `DscpConfigurationPropertiesFormat`
  - Model `ExpressRouteCircuit` moved instance variable `allow_classic_operations`, `circuit_provisioning_state`, `service_provider_provisioning_state`, `authorizations`, `peerings`, `service_key`, `service_provider_notes`, `service_provider_properties`, `express_route_port`, `bandwidth_in_gbps`, `stag`, `provisioning_state`, `gateway_manager_etag`, `global_reach_enabled`, `authorization_key`, `authorization_status` and `enable_direct_port_rate_limit` under property `properties` whose type is `ExpressRouteCircuitPropertiesFormat`
  - Model `ExpressRouteCircuitAuthorization` moved instance variable `authorization_key`, `authorization_use_status`, `connection_resource_uri` and `provisioning_state` under property `properties` whose type is `AuthorizationPropertiesFormat`
  - Model `ExpressRouteCircuitConnection` moved instance variable `express_route_circuit_peering`, `peer_express_route_circuit_peering`, `address_prefix`, `authorization_key`, `ipv6_circuit_connection_config`, `circuit_connection_status` and `provisioning_state` under property `properties` whose type is `ExpressRouteCircuitConnectionPropertiesFormat`
  - Model `ExpressRouteCircuitPeering` moved instance variable `peering_type`, `state`, `azure_asn`, `peer_asn`, `primary_peer_address_prefix`, `secondary_peer_address_prefix`, `primary_azure_port`, `secondary_azure_port`, `shared_key`, `vlan_id`, `microsoft_peering_config`, `stats`, `provisioning_state`, `gateway_manager_etag`, `last_modified_by`, `route_filter`, `ipv6_peering_config`, `express_route_connection`, `connections` and `peered_connections` under property `properties` whose type is `ExpressRouteCircuitPeeringPropertiesFormat`
  - Model `ExpressRouteLink` moved instance variable `router_name`, `interface_name`, `patch_panel_id`, `rack_id`, `colo_location`, `connector_type`, `admin_state`, `provisioning_state` and `mac_sec_config` under property `properties` whose type is `ExpressRouteLinkPropertiesFormat`
  - Model `ExpressRoutePort` moved instance variable `peering_location`, `bandwidth_in_gbps`, `provisioned_bandwidth_in_gbps`, `mtu`, `encapsulation`, `ether_type`, `allocation_date`, `links`, `circuits`, `provisioning_state`, `resource_guid` and `billing_type` under property `properties` whose type is `ExpressRoutePortPropertiesFormat`
  - Model `ExpressRoutePortAuthorization` moved instance variable `authorization_key`, `authorization_use_status`, `circuit_resource_uri` and `provisioning_state` under property `properties` whose type is `ExpressRoutePortAuthorizationPropertiesFormat`
  - Model `ExpressRoutePortsLocation` moved instance variable `address`, `contact`, `available_bandwidths` and `provisioning_state` under property `properties` whose type is `ExpressRoutePortsLocationPropertiesFormat`
  - Model `ExpressRouteServiceProvider` moved instance variable `peering_locations`, `bandwidths_offered` and `provisioning_state` under property `properties` whose type is `ExpressRouteServiceProviderPropertiesFormat`
  - Model `FirewallPolicy` moved instance variable `size`, `rule_collection_groups`, `provisioning_state`, `base_policy`, `firewalls`, `child_policies`, `threat_intel_mode`, `threat_intel_whitelist`, `insights`, `snat`, `sql`, `dns_settings`, `explicit_proxy`, `intrusion_detection`, `transport_security` and `sku` under property `properties` whose type is `FirewallPolicyPropertiesFormat`
  - Model `FlowLogInformation` moved instance variable `storage_id`, `enabled_filtering_criteria`, `record_types`, `enabled`, `retention_policy` and `format` under property `properties` whose type is `FlowLogPropertiesFormat`
  - Model `FrontendIPConfiguration` moved instance variable `inbound_nat_rules`, `inbound_nat_pools`, `outbound_rules`, `load_balancing_rules`, `private_ip_address`, `private_ip_allocation_method`, `private_ip_address_version`, `subnet`, `public_ip_address`, `public_ip_prefix`, `gateway_load_balancer` and `provisioning_state` under property `properties` whose type is `FrontendIPConfigurationPropertiesFormat`
  - Model `HubIpConfiguration` moved instance variable `private_ip_address`, `private_ip_allocation_method`, `subnet`, `public_ip_address` and `provisioning_state` under property `properties` whose type is `HubIPConfigurationPropertiesFormat`
  - Model `IPConfiguration` moved instance variable `private_ip_address`, `private_ip_allocation_method`, `subnet`, `public_ip_address` and `provisioning_state` under property `properties` whose type is `IPConfigurationPropertiesFormat`
  - Model `IPConfigurationProfile` moved instance variable `subnet` and `provisioning_state` under property `properties` whose type is `IPConfigurationProfilePropertiesFormat`
  - Model `InboundNatPool` moved instance variable `frontend_ip_configuration`, `protocol`, `frontend_port_range_start`, `frontend_port_range_end`, `backend_port`, `idle_timeout_in_minutes`, `enable_floating_ip`, `enable_tcp_reset` and `provisioning_state` under property `properties` whose type is `InboundNatPoolPropertiesFormat`
  - Model `InboundNatRule` moved instance variable `frontend_ip_configuration`, `backend_ip_configuration`, `protocol`, `frontend_port`, `backend_port`, `idle_timeout_in_minutes`, `enable_floating_ip`, `enable_tcp_reset`, `frontend_port_range_start`, `frontend_port_range_end`, `backend_address_pool` and `provisioning_state` under property `properties` whose type is `InboundNatRulePropertiesFormat`
  - Model `IpAllocation` moved instance variable `subnet`, `virtual_network`, `type_properties_type`, `prefix`, `prefix_length`, `prefix_type`, `ipam_allocation_id` and `allocation_tags` under property `properties` whose type is `IpAllocationPropertiesFormat`
  - Model `IpGroup` moved instance variable `provisioning_state`, `ip_addresses`, `firewalls` and `firewall_policies` under property `properties` whose type is `IpGroupPropertiesFormat`
  - Model `IpamPoolPrefixAllocation` moved instance variable `id` under property `pool` whose type is `IpamPoolPrefixAllocationPool`
  - Model `LoadBalancer` moved instance variable `frontend_ip_configurations`, `backend_address_pools`, `load_balancing_rules`, `probes`, `inbound_nat_rules`, `inbound_nat_pools`, `outbound_rules`, `resource_guid`, `provisioning_state` and `scope` under property `properties` whose type is `LoadBalancerPropertiesFormat`
  - Model `LoadBalancerBackendAddress` moved instance variable `virtual_network`, `subnet`, `ip_address`, `network_interface_ip_configuration`, `load_balancer_frontend_ip_configuration`, `inbound_nat_rules_port_mapping` and `admin_state` under property `properties` whose type is `LoadBalancerBackendAddressPropertiesFormat`
  - Model `LoadBalancingRule` moved instance variable `frontend_ip_configuration`, `backend_address_pool`, `backend_address_pools`, `probe`, `protocol`, `load_distribution`, `frontend_port`, `backend_port`, `idle_timeout_in_minutes`, `enable_floating_ip`, `enable_tcp_reset`, `disable_outbound_snat`, `enable_connection_tracking` and `provisioning_state` under property `properties` whose type is `LoadBalancingRulePropertiesFormat`
  - Model `LocalNetworkGateway` moved instance variable `local_network_address_space`, `gateway_ip_address`, `fqdn`, `bgp_settings`, `resource_guid` and `provisioning_state` under property `properties` whose type is `LocalNetworkGatewayPropertiesFormat`
  - Model `NatGateway` moved instance variable `idle_timeout_in_minutes`, `public_ip_addresses`, `public_ip_addresses_v6`, `public_ip_prefixes`, `public_ip_prefixes_v6`, `subnets`, `source_virtual_network`, `service_gateway`, `resource_guid` and `provisioning_state` under property `properties` whose type is `NatGatewayPropertiesFormat`
  - Model `NetworkInterface` moved instance variable `virtual_machine`, `network_security_group`, `private_endpoint`, `ip_configurations`, `tap_configurations`, `dns_settings`, `mac_address`, `primary`, `vnet_encryption_supported`, `default_outbound_connectivity_enabled`, `enable_accelerated_networking`, `disable_tcp_state_tracking`, `enable_ip_forwarding`, `hosted_workloads`, `dscp_configuration`, `resource_guid`, `provisioning_state`, `workload_type`, `nic_type`, `private_link_service`, `migration_phase`, `auxiliary_mode` and `auxiliary_sku` under property `properties` whose type is `NetworkInterfacePropertiesFormat`
  - Model `NetworkInterfaceIPConfiguration` moved instance variable `gateway_load_balancer`, `virtual_network_taps`, `application_gateway_backend_address_pools`, `load_balancer_backend_address_pools`, `load_balancer_inbound_nat_rules`, `private_ip_address`, `private_ip_address_prefix_length`, `private_ip_allocation_method`, `private_ip_address_version`, `subnet`, `primary`, `public_ip_address`, `application_security_groups`, `provisioning_state` and `private_link_connection_properties` under property `properties` whose type is `NetworkInterfaceIPConfigurationPropertiesFormat`
  - Model `NetworkInterfaceTapConfiguration` moved instance variable `virtual_network_tap` and `provisioning_state` under property `properties` whose type is `NetworkInterfaceTapConfigurationPropertiesFormat`
  - Model `NetworkManagerRoutingConfiguration` moved instance variable `description`, `provisioning_state`, `resource_guid` and `route_table_usage_mode` under property `properties` whose type is `NetworkManagerRoutingConfigurationPropertiesFormat`
  - Model `NetworkProfile` moved instance variable `container_network_interfaces`, `container_network_interface_configurations`, `resource_guid` and `provisioning_state` under property `properties` whose type is `NetworkProfilePropertiesFormat`
  - Model `NetworkSecurityGroup` moved instance variable `flush_connection`, `security_rules`, `default_security_rules`, `network_interfaces`, `subnets`, `flow_logs`, `resource_guid` and `provisioning_state` under property `properties` whose type is `NetworkSecurityGroupPropertiesFormat`
  - Model `NetworkVirtualAppliance` moved instance variable `nva_sku`, `address_prefix`, `boot_strap_configuration_blobs`, `virtual_hub`, `cloud_init_configuration_blobs`, `cloud_init_configuration`, `virtual_appliance_asn`, `ssh_public_key`, `virtual_appliance_nics`, `network_profile`, `additional_nics`, `internet_ingress_public_ips`, `virtual_appliance_sites`, `virtual_appliance_connections`, `inbound_security_rules`, `provisioning_state`, `deployment_type`, `delegation`, `partner_managed_resource`, `nva_interface_configurations` and `private_ip_address` under property `properties` whose type is `NetworkVirtualAppliancePropertiesFormat`
  - Model `NetworkVirtualApplianceSku` moved instance variable `vendor`, `available_versions` and `available_scale_units` under property `properties` whose type is `NetworkVirtualApplianceSkuPropertiesFormat`
  - Model `NetworkWatcher` moved instance variable `provisioning_state` under property `properties` whose type is `NetworkWatcherPropertiesFormat`
  - Model `Operation` moved instance variable `service_specification` under property `properties` whose type is `OperationPropertiesFormat`
  - Model `OutboundRule` moved instance variable `allocated_outbound_ports`, `frontend_ip_configurations`, `backend_address_pool`, `provisioning_state`, `protocol`, `enable_tcp_reset` and `idle_timeout_in_minutes` under property `properties` whose type is `OutboundRulePropertiesFormat`
  - Model `PeerExpressRouteCircuitConnection` moved instance variable `express_route_circuit_peering`, `peer_express_route_circuit_peering`, `address_prefix`, `circuit_connection_status`, `connection_name`, `auth_resource_guid` and `provisioning_state` under property `properties` whose type is `PeerExpressRouteCircuitConnectionPropertiesFormat`
  - Model `PrivateDnsZoneConfig` moved instance variable `private_dns_zone_id` and `record_sets` under property `properties` whose type is `PrivateDnsZonePropertiesFormat`
  - Model `PrivateDnsZoneGroup` moved instance variable `provisioning_state` and `private_dns_zone_configs` under property `properties` whose type is `PrivateDnsZoneGroupPropertiesFormat`
  - Model `Probe` moved instance variable `load_balancing_rules`, `protocol`, `port`, `interval_in_seconds`, `no_healthy_backends_behavior`, `number_of_probes`, `probe_threshold`, `request_path` and `provisioning_state` under property `properties` whose type is `ProbePropertiesFormat`
  - Model `PublicIPAddress` moved instance variable `public_ip_allocation_method`, `public_ip_address_version`, `ip_configuration`, `dns_settings`, `ddos_settings`, `ip_tags`, `ip_address`, `public_ip_prefix`, `idle_timeout_in_minutes`, `resource_guid`, `provisioning_state`, `service_public_ip_address`, `nat_gateway`, `migration_phase`, `linked_public_ip_address` and `delete_option` under property `properties` whose type is `PublicIPAddressPropertiesFormat`
  - Model `PublicIPPrefix` moved instance variable `public_ip_address_version`, `ip_tags`, `prefix_length`, `ip_prefix`, `public_ip_addresses`, `load_balancer_frontend_ip_configuration`, `custom_ip_prefix`, `resource_guid`, `provisioning_state` and `nat_gateway` under property `properties` whose type is `PublicIPPrefixPropertiesFormat`
  - Model `ResourceNavigationLink` moved instance variable `linked_resource_type`, `link` and `provisioning_state` under property `properties` whose type is `ResourceNavigationLinkFormat`
  - Model `Route` moved instance variable `address_prefix`, `next_hop_type`, `next_hop_ip_address`, `provisioning_state` and `has_bgp_override` under property `properties` whose type is `RoutePropertiesFormat`
  - Model `RouteFilter` moved instance variable `rules`, `peerings`, `ipv6_peerings` and `provisioning_state` under property `properties` whose type is `RouteFilterPropertiesFormat`
  - Model `RouteFilterRule` moved instance variable `access`, `route_filter_rule_type`, `communities` and `provisioning_state` under property `properties` whose type is `RouteFilterRulePropertiesFormat`
  - Model `RouteTable` moved instance variable `routes`, `subnets`, `disable_bgp_route_propagation`, `provisioning_state` and `resource_guid` under property `properties` whose type is `RouteTablePropertiesFormat`
  - Model `RoutingRule` moved instance variable `description`, `provisioning_state`, `resource_guid`, `destination` and `next_hop` under property `properties` whose type is `RoutingRulePropertiesFormat`
  - Model `RoutingRuleCollection` moved instance variable `description`, `provisioning_state`, `resource_guid`, `applies_to` and `disable_bgp_route_propagation` under property `properties` whose type is `RoutingRuleCollectionPropertiesFormat`
  - Model `SecurityAdminConfiguration` moved instance variable `description`, `apply_on_network_intent_policy_based_services`, `network_group_address_space_aggregation_option`, `provisioning_state` and `resource_guid` under property `properties` whose type is `SecurityAdminConfigurationPropertiesFormat`
  - Model `SecurityPartnerProvider` moved instance variable `provisioning_state`, `security_provider_name`, `connection_status` and `virtual_hub` under property `properties` whose type is `SecurityPartnerProviderPropertiesFormat`
  - Model `SecurityRule` moved instance variable `description`, `protocol`, `source_port_range`, `destination_port_range`, `source_address_prefix`, `source_address_prefixes`, `source_application_security_groups`, `destination_address_prefix`, `destination_address_prefixes`, `destination_application_security_groups`, `source_port_ranges`, `destination_port_ranges`, `access`, `priority`, `direction` and `provisioning_state` under property `properties` whose type is `SecurityRulePropertiesFormat`
  - Model `SecurityUserConfiguration` moved instance variable `description`, `provisioning_state` and `resource_guid` under property `properties` whose type is `SecurityUserConfigurationPropertiesFormat`
  - Model `SecurityUserRule` moved instance variable `description`, `protocol`, `sources`, `destinations`, `source_port_ranges`, `destination_port_ranges`, `direction`, `provisioning_state` and `resource_guid` under property `properties` whose type is `SecurityUserRulePropertiesFormat`
  - Model `SecurityUserRuleCollection` moved instance variable `description`, `applies_to_groups`, `provisioning_state` and `resource_guid` under property `properties` whose type is `SecurityUserRuleCollectionPropertiesFormat`
  - Model `ServiceAssociationLink` moved instance variable `linked_resource_type`, `link`, `provisioning_state`, `allow_delete` and `locations` under property `properties` whose type is `ServiceAssociationLinkPropertiesFormat`
  - Model `ServiceEndpointPolicy` moved instance variable `service_endpoint_policy_definitions`, `subnets`, `resource_guid`, `provisioning_state`, `service_alias` and `contextual_service_endpoint_policies` under property `properties` whose type is `ServiceEndpointPolicyPropertiesFormat`
  - Model `ServiceEndpointPolicyDefinition` moved instance variable `description`, `service`, `service_resources` and `provisioning_state` under property `properties` whose type is `ServiceEndpointPolicyDefinitionPropertiesFormat`
  - Model `ServiceGateway` moved instance variable `virtual_network`, `route_target_address`, `route_target_address_v6`, `resource_guid` and `provisioning_state` under property `properties` whose type is `ServiceGatewayPropertiesFormat`
  - Model `ServiceGatewayService` moved instance variable `service_type`, `is_default`, `load_balancer_backend_pools` and `public_nat_gateway_id` under property `properties` whose type is `ServiceGatewayServicePropertiesFormat`
  - Model `Subnet` moved instance variable `address_prefix`, `address_prefixes`, `network_security_group`, `route_table`, `nat_gateway`, `service_endpoints`, `service_endpoint_policies`, `private_endpoints`, `ip_configurations`, `ip_configuration_profiles`, `ip_allocations`, `resource_navigation_links`, `service_association_links`, `delegations`, `purpose`, `provisioning_state`, `private_endpoint_network_policies`, `private_link_service_network_policies`, `application_gateway_ip_configurations`, `sharing_scope`, `default_outbound_access`, `ipam_pool_prefix_allocations` and `service_gateway` under property `properties` whose type is `SubnetPropertiesFormat`
  - Model `TroubleshootingParameters` moved instance variable `storage_id` and `storage_path` under property `properties` whose type is `TroubleshootingProperties`
  - Model `VirtualNetwork` moved instance variable `address_space`, `dhcp_options`, `flow_timeout_in_minutes`, `subnets`, `virtual_network_peerings`, `resource_guid`, `provisioning_state`, `enable_ddos_protection`, `enable_vm_protection`, `ddos_protection_plan`, `bgp_communities`, `encryption`, `ip_allocations`, `flow_logs`, `private_endpoint_v_net_policies` and `default_public_nat_gateway` under property `properties` whose type is `VirtualNetworkPropertiesFormat`
  - Model `VirtualNetworkAppliance` moved instance variable `bandwidth_in_gbps`, `ip_configurations`, `provisioning_state`, `resource_guid` and `subnet` under property `properties` whose type is `VirtualNetworkAppliancePropertiesFormat`
  - Model `VirtualNetworkGateway` moved instance variable `auto_scale_configuration`, `ip_configurations`, `gateway_type`, `vpn_type`, `vpn_gateway_generation`, `enable_bgp`, `enable_private_ip_address`, `virtual_network_gateway_migration_status`, `active`, `enable_high_bandwidth_vpn_gateway`, `disable_ip_sec_replay_protection`, `gateway_default_site`, `sku`, `vpn_client_configuration`, `virtual_network_gateway_policy_groups`, `bgp_settings`, `custom_routes`, `resource_guid`, `provisioning_state`, `enable_dns_forwarding`, `inbound_dns_forwarding_endpoint`, `v_net_extended_location_resource_id`, `nat_rules`, `enable_bgp_route_translation_for_nat`, `allow_virtual_wan_traffic`, `allow_remote_vnet_traffic`, `admin_state` and `resiliency_model` under property `properties` whose type is `VirtualNetworkGatewayPropertiesFormat`
  - Model `VirtualNetworkGatewayConnection` moved instance variable `authorization_key`, `virtual_network_gateway1`, `virtual_network_gateway2`, `local_network_gateway2`, `ingress_nat_rules`, `egress_nat_rules`, `connection_type`, `connection_protocol`, `routing_weight`, `dpd_timeout_seconds`, `connection_mode`, `tunnel_properties`, `shared_key`, `connection_status`, `tunnel_connection_status`, `egress_bytes_transferred`, `ingress_bytes_transferred`, `peer`, `enable_bgp`, `gateway_custom_bgp_ip_addresses`, `use_local_azure_ip_address`, `use_policy_based_traffic_selectors`, `ipsec_policies`, `traffic_selector_policies`, `resource_guid`, `provisioning_state`, `express_route_gateway_bypass`, `enable_private_link_fast_path`, `authentication_type` and `certificate_authentication` under property `properties` whose type is `VirtualNetworkGatewayConnectionPropertiesFormat`
  - Model `VirtualNetworkGatewayConnectionListEntity` moved instance variable `authorization_key`, `virtual_network_gateway1`, `virtual_network_gateway2`, `local_network_gateway2`, `connection_type`, `connection_protocol`, `routing_weight`, `connection_mode`, `shared_key`, `connection_status`, `tunnel_connection_status`, `egress_bytes_transferred`, `ingress_bytes_transferred`, `peer`, `enable_bgp`, `gateway_custom_bgp_ip_addresses`, `use_policy_based_traffic_selectors`, `ipsec_policies`, `traffic_selector_policies`, `resource_guid`, `provisioning_state`, `express_route_gateway_bypass` and `enable_private_link_fast_path` under property `properties` whose type is `VirtualNetworkGatewayConnectionListEntityPropertiesFormat`
  - Model `VirtualNetworkGatewayIPConfiguration` moved instance variable `private_ip_allocation_method`, `subnet`, `public_ip_address`, `private_ip_address` and `provisioning_state` under property `properties` whose type is `VirtualNetworkGatewayIPConfigurationPropertiesFormat`
  - Model `VirtualNetworkPeering` moved instance variable `allow_virtual_network_access`, `allow_forwarded_traffic`, `allow_gateway_transit`, `use_remote_gateways`, `remote_virtual_network`, `local_address_space`, `local_virtual_network_address_space`, `remote_address_space`, `remote_virtual_network_address_space`, `remote_bgp_communities`, `remote_virtual_network_encryption`, `peering_state`, `peering_sync_level`, `provisioning_state`, `do_not_verify_remote_gateways`, `resource_guid`, `peer_complete_vnets`, `enable_only_i_pv6_peering`, `local_subnet_names` and `remote_subnet_names` under property `properties` whose type is `VirtualNetworkPeeringPropertiesFormat`
  - Model `VirtualNetworkTap` moved instance variable `network_interface_tap_configurations`, `resource_guid`, `provisioning_state`, `destination_network_interface_ip_configuration`, `destination_load_balancer_front_end_ip_configuration` and `destination_port` under property `properties` whose type is `VirtualNetworkTapPropertiesFormat`
  - Model `VirtualRouter` moved instance variable `virtual_router_asn`, `virtual_router_ips`, `hosted_subnet`, `hosted_gateway`, `peerings` and `provisioning_state` under property `properties` whose type is `VirtualRouterPropertiesFormat`
  - Model `VirtualWAN` moved instance variable `disable_vpn_encryption`, `virtual_hubs`, `vpn_sites`, `allow_branch_to_branch_traffic`, `allow_vnet_to_vnet_traffic`, `office365_local_breakout_category`, `provisioning_state` and `type_properties_type` under property `properties` whose type is `VirtualWanProperties`
  - Model `VpnClientRevokedCertificate` moved instance variable `thumbprint` and `provisioning_state` under property `properties` whose type is `VpnClientRevokedCertificatePropertiesFormat`
  - Model `VpnClientRootCertificate` moved instance variable `public_cert_data` and `provisioning_state` under property `properties` whose type is `VpnClientRootCertificatePropertiesFormat`
  - Model `WebApplicationFirewallPolicy` moved instance variable `policy_settings`, `custom_rules`, `application_gateways`, `provisioning_state`, `resource_state`, `managed_rules`, `http_listeners`, `path_based_rules` and `application_gateway_for_containers` under property `properties` whose type is `WebApplicationFirewallPolicyPropertiesFormat`
  - Model `ActiveConnectivityConfiguration` moved instance variable `description`, `connectivity_topology`, `hubs`, `is_global`, `connectivity_capabilities`, `applies_to_groups`, `provisioning_state`, `delete_existing_peering` and `resource_guid` under property `properties`
  - Model `ActiveDefaultSecurityAdminRule` moved instance variable `description`, `flag`, `protocol`, `sources`, `destinations`, `source_port_ranges`, `destination_port_ranges`, `access`, `priority`, `direction`, `provisioning_state` and `resource_guid` under property `properties`
  - Model `ActiveSecurityAdminRule` moved instance variable `description`, `protocol`, `sources`, `destinations`, `source_port_ranges`, `destination_port_ranges`, `access`, `priority`, `direction`, `provisioning_state` and `resource_guid` under property `properties`
  - Model `ConfigurationGroup` moved instance variable `description`, `member_type`, `provisioning_state` and `resource_guid` under property `properties`
  - Model `ConnectionMonitor` moved instance variable `source`, `destination`, `auto_start`, `monitoring_interval_in_seconds`, `endpoints`, `test_configurations`, `test_groups`, `outputs` and `notes` under property `properties` whose type is `ConnectionMonitorParameters`
  - Model `ConnectionMonitorResult` moved instance variable `source`, `destination`, `auto_start`, `monitoring_interval_in_seconds`, `endpoints`, `test_configurations`, `test_groups`, `outputs`, `notes`, `provisioning_state`, `start_time`, `monitoring_status` and `connection_monitor_type` under property `properties` whose type is `ConnectionMonitorResultProperties`
  - Model `EffectiveConnectivityConfiguration` moved instance variable `description`, `connectivity_topology`, `hubs`, `is_global`, `connectivity_capabilities`, `applies_to_groups`, `provisioning_state`, `delete_existing_peering` and `resource_guid` under property `properties`
  - Model `EffectiveDefaultSecurityAdminRule` moved instance variable `description`, `flag`, `protocol`, `sources`, `destinations`, `source_port_ranges`, `destination_port_ranges`, `access`, `priority`, `direction`, `provisioning_state` and `resource_guid` under property `properties`
  - Model `EffectiveSecurityAdminRule` moved instance variable `description`, `protocol`, `sources`, `destinations`, `source_port_ranges`, `destination_port_ranges`, `access`, `priority`, `direction`, `provisioning_state` and `resource_guid` under property `properties`
  - Model `PacketCapture` moved instance variable `target`, `scope`, `target_type`, `bytes_to_capture_per_packet`, `total_bytes_per_session`, `time_limit_in_seconds`, `storage_location`, `filters`, `continuous_capture` and `capture_settings` under property `properties` whose type is `PacketCaptureParameters`
  - Model `PacketCaptureResult` moved instance variable `target`, `scope`, `target_type`, `bytes_to_capture_per_packet`, `total_bytes_per_session`, `time_limit_in_seconds`, `storage_location`, `filters`, `continuous_capture`, `capture_settings` and `provisioning_state` under property `properties` whose type is `PacketCaptureResultProperties`
  - Deleted or renamed model `AzureAsyncOperationResult`
  - Deleted or renamed model `BastionSessionDeleteResult`
  - Deleted or renamed model `Components1Jq1T4ISchemasManagedserviceidentityPropertiesUserassignedidentitiesAdditionalproperties`
  - Deleted or renamed model `ConnectionMonitorQueryResult`
  - Deleted or renamed model `ConnectionMonitorSourceStatus`
  - Deleted or renamed model `ConnectionState`
  - Deleted or renamed model `ConnectionStateSnapshot`
  - Deleted or renamed model `EvaluationState`
  - Deleted or renamed model `HubVirtualNetworkConnectionStatus`
  - Deleted or renamed model `NetworkOperationStatus`
  - Deleted or renamed model `PatchRouteFilter`
  - Deleted or renamed model `PatchRouteFilterRule`
  - Deleted or renamed model `TrackedResource`
  - Deleted or renamed model `TunnelConnectionStatus`
  - Deleted or renamed model `VpnSiteId`

### Other Changes

  - Deleted model `ApplicationGatewayAvailableSslPredefinedPolicies`/`ApplicationGatewayWafDynamicManifestResultList`/`AutoApprovedPrivateLinkServicesResult`/`AvailableDelegationsResult`/`AvailablePrivateEndpointTypesResult`/`AvailableServiceAliasesResult`/`ConnectionSharedKeyResultList`/`ExpressRouteCrossConnectionPeeringList`/`GetServiceGatewayAddressLocationsResult`/`GetServiceGatewayServicesResult`/`IpamPoolList`/`ListHubRouteTablesResult`/`ListHubVirtualNetworkConnectionsResult`/`ListP2SVpnGatewaysResult`/`ListRouteMapsResult`/`ListRoutingIntentResult`/`ListVirtualHubBgpConnectionResults`/`ListVirtualHubIpConfigurationResults`/`ListVirtualHubRouteTableV2SResult`/`ListVirtualHubsResult`/`ListVirtualNetworkGatewayNatRulesResult`/`ListVirtualWANsResult`/`ListVpnConnectionsResult`/`ListVpnGatewayNatRulesResult`/`ListVpnGatewaysResult`/`ListVpnServerConfigurationPolicyGroupsResult`/`ListVpnServerConfigurationsResult`/`ListVpnSiteLinkConnectionsResult`/`ListVpnSiteLinksResult`/`ListVpnSitesResult`/`NetworkVirtualApplianceConnectionList`/`PoolAssociationList`/`StaticCidrList`/`VirtualNetworkDdosProtectionStatusResult`/`VirtualNetworkGatewayListConnectionsResult`/`VirtualNetworkListUsageResult` which actually was not used by SDK users

## 30.2.0 (2026-02-11)

### Features Added

  - Client `NetworkManagementClient` added operation group `service_gateways`
  - Client `NetworkManagementClient` added operation group `virtual_network_appliances`
  - Enum `ActionType` added member `CAPTCHA`
  - Enum `FirewallPolicyIntrusionDetectionProfileType` added member `CORE`
  - Enum `FirewallPolicyIntrusionDetectionProfileType` added member `EMERGING`
  - Enum `FirewallPolicyIntrusionDetectionProfileType` added member `OFF`
  - Model `NatGateway` added property `service_gateway`
  - Model `PolicySettings` added property `captcha_cookie_expiration_in_mins`
  - Model `Subnet` added property `service_gateway`
  - Enum `WebApplicationFirewallAction` added member `CAPTCHA`
  - Added enum `AddressUpdateAction`
  - Added model `GetServiceGatewayAddressLocationsResult`
  - Added model `GetServiceGatewayServicesResult`
  - Added model `RouteTargetAddressPropertiesFormat`
  - Added model `ServiceGateway`
  - Added model `ServiceGatewayAddress`
  - Added model `ServiceGatewayAddressLocation`
  - Added model `ServiceGatewayAddressLocationResponse`
  - Added model `ServiceGatewayListResult`
  - Added model `ServiceGatewayService`
  - Added model `ServiceGatewayServiceRequest`
  - Added model `ServiceGatewaySku`
  - Added enum `ServiceGatewaySkuName`
  - Added enum `ServiceGatewaySkuTier`
  - Added model `ServiceGatewayUpdateAddressLocationsRequest`
  - Added model `ServiceGatewayUpdateServicesRequest`
  - Added enum `ServiceType`
  - Added enum `ServiceUpdateAction`
  - Added enum `UpdateAction`
  - Added model `VirtualNetworkAppliance`
  - Added model `VirtualNetworkApplianceIpConfiguration`
  - Added model `VirtualNetworkApplianceListResult`
  - Added operation group `ServiceGatewaysOperations`
  - Added operation group `VirtualNetworkAppliancesOperations`

### Breaking Changes

  - Deleted or renamed enum value `FirewallPolicyIntrusionDetectionProfileType.ADVANCED`
  - Deleted or renamed enum value `FirewallPolicyIntrusionDetectionProfileType.BASIC`
  - Deleted or renamed enum value `FirewallPolicyIntrusionDetectionProfileType.STANDARD`

## 30.1.0 (2025-11-19)

### Features Added

  - Added operation PublicIPAddressesOperations.begin_disassociate_cloud_service_reserved_public_ip
  - Added operation PublicIPAddressesOperations.begin_reserve_cloud_service_public_ip_address
  - Model ApplicationGateway has a new parameter entra_jwt_validation_configs
  - Model ApplicationGatewayBackendSettings has a new parameter enable_l4_client_ip_preservation
  - Model ApplicationGatewayClientAuthConfiguration has a new parameter verify_client_auth_mode
  - Model ApplicationGatewayOnDemandProbe has a new parameter enable_probe_proxy_protocol_header
  - Model ApplicationGatewayProbe has a new parameter enable_probe_proxy_protocol_header
  - Model ApplicationGatewayRequestRoutingRule has a new parameter entra_jwt_validation_config
  - Model DdosCustomPolicy has a new parameter detection_rules
  - Model DdosCustomPolicy has a new parameter front_end_ip_configuration
  - Model FlowLog has a new parameter record_types
  - Model FlowLogInformation has a new parameter record_types
  - Model LoadBalancer has a new parameter scope
  - Model NetworkManagerRoutingConfiguration has a new parameter route_table_usage_mode
  - Model PrivateEndpoint has a new parameter ip_version_type
  - Model PrivateLinkService has a new parameter access_mode
  - Model VirtualNetworkGatewayConnection has a new parameter authentication_type
  - Model VirtualNetworkGatewayConnection has a new parameter certificate_authentication

## 30.0.0 (2025-10-24)

### Features Added

  - Added operation AzureFirewallsOperations.begin_packet_capture_operation
  - Added operation VirtualNetworkGatewaysOperations.list_radius_secrets
  - Added operation VpnServerConfigurationsOperations.list_radius_secrets
  - Added operation group NetworkSecurityPerimeterServiceTagsOperations
  - Model ApplicationGatewayBackendHttpSettings has a new parameter dedicated_backend_connection
  - Model ApplicationGatewayBackendHttpSettings has a new parameter sni_name
  - Model ApplicationGatewayBackendHttpSettings has a new parameter validate_cert_chain_and_expiry
  - Model ApplicationGatewayBackendHttpSettings has a new parameter validate_sni
  - Model AzureFirewall has a new parameter extended_location
  - Model FirewallPacketCaptureParameters has a new parameter operation
  - Model NetworkVirtualAppliance has a new parameter nva_interface_configurations
  - Model NetworkVirtualAppliance has a new parameter private_ip_address

### Breaking Changes

  - Removed operation group NetworkManagementClientOperationsMixin

## 29.0.0 (2025-05-22)

### Features Added

  - Added operation NetworkVirtualAppliancesOperations.begin_get_boot_diagnostic_logs
  - Added operation NetworkVirtualAppliancesOperations.begin_reimage
  - Added operation VirtualNetworkGatewaysOperations.begin_get_resiliency_information
  - Added operation VirtualNetworkGatewaysOperations.begin_get_routes_information
  - Added operation VirtualNetworkGatewaysOperations.begin_invoke_abort_migration
  - Added operation VirtualNetworkGatewaysOperations.begin_invoke_commit_migration
  - Added operation VirtualNetworkGatewaysOperations.begin_invoke_execute_migration
  - Added operation VirtualNetworkGatewaysOperations.begin_invoke_prepare_migration
  - Added operation group NetworkSecurityPerimeterAccessRulesOperations
  - Added operation group NetworkSecurityPerimeterAssociableResourceTypesOperations
  - Added operation group NetworkSecurityPerimeterAssociationsOperations
  - Added operation group NetworkSecurityPerimeterLinkReferencesOperations
  - Added operation group NetworkSecurityPerimeterLinksOperations
  - Added operation group NetworkSecurityPerimeterLoggingConfigurationsOperations
  - Added operation group NetworkSecurityPerimeterOperationStatusesOperations
  - Added operation group NetworkSecurityPerimeterProfilesOperations
  - Added operation group NetworkSecurityPerimetersOperations
  - Model ActiveConnectivityConfiguration has a new parameter connectivity_capabilities
  - Model ConnectivityConfiguration has a new parameter connectivity_capabilities
  - Model EffectiveConnectivityConfiguration has a new parameter connectivity_capabilities
  - Model ExpressRouteCircuitPeeringConfig has a new parameter advertised_public_prefix_info
  - Model IpamPool has a new parameter etag
  - Model LoadBalancingRule has a new parameter enable_connection_tracking
  - Model ManagedRuleSet has a new parameter computed_disabled_rules
  - Model NatGateway has a new parameter public_ip_addresses_v6
  - Model NatGateway has a new parameter public_ip_prefixes_v6
  - Model NatGateway has a new parameter source_virtual_network
  - Model VerifierWorkspace has a new parameter etag
  - Model VirtualNetwork has a new parameter default_public_nat_gateway
  - Model VirtualNetworkGateway has a new parameter enable_high_bandwidth_vpn_gateway
  - Model VirtualNetworkGateway has a new parameter virtual_network_gateway_migration_status
  - Model VirtualNetworkGatewayConnection has a new parameter tunnel_properties
  - Operation IpamPoolsOperations.begin_create has a new optional parameter if_match
  - Operation IpamPoolsOperations.begin_delete has a new optional parameter if_match
  - Operation IpamPoolsOperations.update has a new optional parameter if_match
  - Operation VerifierWorkspacesOperations.begin_delete has a new optional parameter if_match
  - Operation VerifierWorkspacesOperations.create has a new optional parameter if_match
  - Operation VerifierWorkspacesOperations.update has a new optional parameter if_match

### Breaking Changes

  - Removed operation ConnectionMonitorsOperations.begin_query
  - Removed operation ConnectionMonitorsOperations.begin_start

## 28.1.0 (2024-12-20)

### Features Added

  - Client `NetworkManagementClient` added operation group `ipam_pools`
  - Client `NetworkManagementClient` added operation group `static_cidrs`
  - Client `NetworkManagementClient` added operation group `reachability_analysis_intents`
  - Client `NetworkManagementClient` added operation group `reachability_analysis_runs`
  - Client `NetworkManagementClient` added operation group `verifier_workspaces`
  - Enum `AddressPrefixType` added member `NETWORK_GROUP`
  - Model `AddressSpace` added property `ipam_pool_prefix_allocations`
  - Model `BastionHost` added property `enable_private_only_bastion`
  - Enum `FirewallPolicyIDPSSignatureDirection` added member `FIVE`
  - Model `NetworkInterface` added property `default_outbound_connectivity_enabled`
  - Enum `ProvisioningState` added member `CANCELED`
  - Enum `ProvisioningState` added member `CREATING`
  - Model `SecurityAdminConfiguration` added property `network_group_address_space_aggregation_option`
  - Model `Subnet` added property `ipam_pool_prefix_allocations`
  - Added enum `AddressSpaceAggregationOption`
  - Added model `CommonErrorAdditionalInfo`
  - Added model `CommonErrorDetail`
  - Added model `CommonErrorResponse`
  - Added model `CommonProxyResource`
  - Added model `CommonResource`
  - Added model `CommonTrackedResource`
  - Added model `ExpressRouteFailoverCircuitResourceDetails`
  - Added model `ExpressRouteFailoverConnectionResourceDetails`
  - Added model `ExpressRouteFailoverRedundantRoute`
  - Added model `ExpressRouteFailoverSingleTestDetails`
  - Added model `ExpressRouteFailoverStopApiParameters`
  - Added model `ExpressRouteFailoverTestDetails`
  - Added model `FailoverConnectionDetails`
  - Added enum `FailoverConnectionStatus`
  - Added enum `FailoverTestStatus`
  - Added enum `FailoverTestStatusForSingleTest`
  - Added enum `FailoverTestType`
  - Added model `IPTraffic`
  - Added model `IntentContent`
  - Added enum `IpType`
  - Added model `IpamPool`
  - Added model `IpamPoolList`
  - Added model `IpamPoolPrefixAllocation`
  - Added model `IpamPoolProperties`
  - Added model `IpamPoolUpdate`
  - Added model `IpamPoolUpdateProperties`
  - Added model `LoadBalancerHealthPerRule`
  - Added model `LoadBalancerHealthPerRulePerBackendAddress`
  - Added enum `NetworkProtocol`
  - Added model `PoolAssociation`
  - Added model `PoolAssociationList`
  - Added model `PoolUsage`
  - Added model `ReachabilityAnalysisIntent`
  - Added model `ReachabilityAnalysisIntentListResult`
  - Added model `ReachabilityAnalysisIntentProperties`
  - Added model `ReachabilityAnalysisRun`
  - Added model `ReachabilityAnalysisRunListResult`
  - Added model `ReachabilityAnalysisRunProperties`
  - Added model `ResourceBasics`
  - Added model `StaticCidr`
  - Added model `StaticCidrList`
  - Added model `StaticCidrProperties`
  - Added model `VerifierWorkspace`
  - Added model `VerifierWorkspaceListResult`
  - Added model `VerifierWorkspaceProperties`
  - Added model `VerifierWorkspaceUpdate`
  - Added model `VerifierWorkspaceUpdateProperties`
  - Operation group `LoadBalancerLoadBalancingRulesOperations` added method `begin_health`
  - Operation group `VirtualNetworkGatewaysOperations` added method `begin_get_failover_all_test_details`
  - Operation group `VirtualNetworkGatewaysOperations` added method `begin_get_failover_single_test_details`
  - Operation group `VirtualNetworkGatewaysOperations` added method `begin_start_express_route_site_failover_simulation`
  - Operation group `VirtualNetworkGatewaysOperations` added method `begin_stop_express_route_site_failover_simulation`
  - Added operation group `IpamPoolsOperations`
  - Added operation group `ReachabilityAnalysisIntentsOperations`
  - Added operation group `ReachabilityAnalysisRunsOperations`
  - Added operation group `StaticCidrsOperations`
  - Added operation group `VerifierWorkspacesOperations`

## 28.0.0 (2024-11-01)

### Breaking Changes

- This package now only targets the latest Api-Version available on Azure and removes APIs of other Api-Version. After this change, the package can have much smaller size. If your application requires a specific and non-latest Api-Version, it's recommended to pin this package to the previous released version; If your application always only use latest Api-Version, please ignore this change.

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
