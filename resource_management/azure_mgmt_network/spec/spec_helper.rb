# encoding: utf-8
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.

require File.join(File.dirname(__FILE__), '../../vcr_helper')
require 'azure_mgmt_network'
require 'azure_mgmt_resources'
require 'ms_rest_azure'

include MsRest
include MsRestAzure
include Azure::ARM::Resources
include Azure::ARM::Network
include Azure::ARM::Network::Models

class ResourceHelper
  attr_reader :network_client, :resource_client

  def initialize
    tenant_id = ENV['AZURE_TENANT_ID']
    client_id = ENV['AZURE_CLIENT_ID']
    secret = ENV['AZURE_CLIENT_SECRET']
    @subscription_id = ENV['AZURE_SUBSCRIPTION_ID']

    token_provider = ApplicationTokenProvider.new(tenant_id, client_id, secret)
    @credentials = TokenCredentials.new(token_provider)
  end

  def resource_client
    if @resource_client.nil?
      @resource_client = ResourceManagementClient.new(@credentials)
      @resource_client.subscription_id = @subscription_id
      @resource_client.long_running_operation_retry_timeout = ENV.fetch('RETRY_TIMEOUT', 30).to_i
    end
    @resource_client
  end

  def network_client
    if @network_client.nil?
      @network_client = NetworkManagementClient.new(@credentials)
      @network_client.long_running_operation_retry_timeout = ENV.fetch('RETRY_TIMEOUT', 30).to_i
      @network_client.subscription_id = @subscription_id
    end
    @network_client
  end

  def create_resource_group
    resource_group_name = 'RubySDKTest_azure_mgmt_network'
    params = Azure::ARM::Resources::Models::ResourceGroup.new()
    params.location = 'westus'

    resource_client.resource_groups.create_or_update(resource_group_name, params).value!.body
  end

  def delete_resource_group(name)
    resource_client.resource_groups.delete(name).value!
  end

  def build_virtual_network_params(location)
    params = VirtualNetwork.new
    props = VirtualNetworkPropertiesFormat.new
    params.location = location
    address_space = AddressSpace.new
    address_space.address_prefixes = ['10.0.0.0/16']
    props.address_space = address_space
    dhcp_options = DhcpOptions.new
    dhcp_options.dns_servers = %w(10.1.1.1 10.1.2.4)
    props.dhcp_options = dhcp_options
    sub2 = Subnet.new
    sub2_prop = SubnetPropertiesFormat.new
    sub2.name = 'subnet1234'
    sub2_prop.address_prefix = '10.0.2.0/24'
    sub2.properties = sub2_prop
    props.subnets = [sub2]
    params.properties = props
    params
  end

  def create_virtual_network(resource_group_name)
    virtualNetworkName = "test_vnet"
    params = build_virtual_network_params('westus')
    network_client.virtual_networks.create_or_update(resource_group_name, virtualNetworkName, params).value!.body
  end

  def create_subnet(virtual_network, resource_group, subnet_client)
    subnet_name = 'subnet4857647'
    params = build_subnet_params
    subnet_client.create_or_update(resource_group.name, virtual_network.name, subnet_name, params).value!.body
  end

  def build_subnet_params
    params = Subnet.new
    prop = SubnetPropertiesFormat.new
    params.properties = prop
    prop.address_prefix = '10.0.1.0/24'
    params
  end

  def create_local_network_gateway(resource_group, location, name = nil)
    params = build_local_network_gateway_params(location)
    params.name = name.nil? ? params.name : name
    network_client.local_network_gateways.create_or_update(resource_group.name, params.name, params).value!.body
  end

  def build_local_network_gateway_params(location)
    params = LocalNetworkGateway.new
    params.location = location
    params.name = 'local_gateway2579'
    props = LocalNetworkGatewayPropertiesFormat.new
    params.properties = props
    props.gateway_ip_address = "192.168.3.7"
    address_space = AddressSpace.new
    props.local_network_address_space = address_space
    address_space.address_prefixes = %w(192.168.0.0/16)
    params
  end

  def create_network_security_group(resource_group, location)
    params = build_network_security_group_params(location)
    network_client.network_security_groups.create_or_update(resource_group.name, params.name, params).value!.body
  end

  def build_network_security_group_params(location)
    network_security_group_name = 'sec73484'
    params = NetworkSecurityGroup.new
    params.name = network_security_group_name
    params.location = location
    params
  end

  def create_virtual_network_gateway(location, resource_group,name = nil)
    params = build_virtual_network_gateway_params(location, resource_group)
    params.name = name || params.name
    network_client.virtual_network_gateways.create_or_update(resource_group.name, params.name, params).value!.body
  end

  def build_virtual_network_gateway_params(location, resource_group)
    params = VirtualNetworkGateway.new
    params.location = location
    params.name = 'vnet_gateway6373'
    props = VirtualNetworkGatewayPropertiesFormat.new
    params.properties = props
    props.enable_bgp = false
    props.gateway_type = 'Vpn'
    props.vpn_type = 'RouteBased'
    ip_config = VirtualNetworkGatewayIpConfiguration.new
    props.ip_configurations = [ip_config]
    ip_config.name = 'ip_config843943'
    ip_config_props = VirtualNetworkGatewayIpConfigurationPropertiesFormat.new
    ip_config.properties = ip_config_props
    ip_config_props.private_ipallocation_method = 'Dynamic'
    vnet = create_virtual_network(resource_group.name)
    public_ip = create_public_ip_address(location, resource_group)
    subnet_params = build_subnet_params
    subnet_params.name = 'GatewaySubnet'
    subnet = network_client.subnets.create_or_update(resource_group.name, vnet.name, subnet_params.name, subnet_params).value!.body
    ip_config_props.public_ipaddress = public_ip
    ip_config_props.subnet = subnet
    params
  end

  def build_public_ip_params(location)
    public_ip = PublicIPAddress.new
    public_ip.location = location
    props = PublicIPAddressPropertiesFormat.new
    props.public_ipallocation_method = 'Dynamic'
    public_ip.properties = props
    domain_name = 'domain734843'
    dns_settings = PublicIPAddressDnsSettings.new
    dns_settings.domain_name_label = domain_name
    props.dns_settings = dns_settings
    public_ip
  end

  def create_public_ip_address(location, resource_group)
    public_ip_address_name = 'ip_name8363'
    params = build_public_ip_params(location)
    network_client.public_ipaddresses.create_or_update(resource_group.name, public_ip_address_name, params).value!.body
  end
end
