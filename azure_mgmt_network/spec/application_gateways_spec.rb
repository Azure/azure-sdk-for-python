# encoding: utf-8
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.

require_relative 'spec_helper'

include MsRestAzure
include Azure::ARM::Resources
include Azure::ARM::Network

describe ApplicationGateways do

  before(:all) do
    skip('application gateways aren\'t properly supported yet')

    @client = NETWORK_CLIENT.application_gateways
    @location = 'westus'
    @resource_group = create_resource_group
  end
  after(:all) do
    delete_resource_group(@resource_group.name) unless @resource_group.nil?
  end

  it 'should list all the application gateways in a subscription' do
    result = @client.list_all.value!
    expect(result.response.status).to eq(200)
    expect(result.body).not_to be_nil
    expect(result.body.value).to be_a(Array)
    while !result.body.next_link.nil? && !result.body.next_link.empty? do
      result = @client.list_all_next(result.body.next_link).value!
      expect(result.body.value).not_to be_nil
      expect(result.body.value).to be_a(Array)
    end
  end

  it 'should list all the application gateways in a resource group' do
    result = @client.list(@resource_group.name).value!
    expect(result.response.status).to eq(200)
    expect(result.body).not_to be_nil
    expect(result.body.value).to be_a(Array)
    while !result.body.next_link.nil? && !result.body.next_link.empty? do
      result = @client.list_next(result.body.next_link).value!
      expect(result.body.value).not_to be_nil
      expect(result.body.value).to be_a(Array)
    end
  end


  example 'application gateway api' do
    skip('no long running tasks should be performed') unless RUN_LONG_TASKS
    # create application gateway
    params = build_application_gateway_params
    result = @client.create_or_update(@resource_group.name, params.name, params).value!
    expect(result.response.status).to eq(200)
    expect(result.body).not_to be_nil
    expect(result.body.name).to eq(params.name)
    # get application gateway
    application_gateway = result.body
    result = @client.get(@resource_group.name, application_gateway.name).value!
    expect(result.response.status).to eq(200)
    expect(result.body).not_to be_nil
    expect(result.body.name).to eq(application_gateway.name)
    # start application gateway
    result = @client.start(@resource_group.name, application_gateway.name).value!
    expect(result.response.status).to eq(200)
    # stop application gateway
    result = @client.stop(@resource_group.name, application_gateway.name).value!
    expect(result.response.status).to eq(200)
    # delete application gateway
    result = @client.delete(@resource_group.name, application_gateway.name).value!
    expect(result.response.status).to eq(200)
  end

  def build_application_gateway_params
    vnet = create_virtual_network(@resource_group.name)
    subnet = create_subnet(vnet, @resource_group, NETWORK_CLIENT.subnets)
    application_gateway_name = get_random_name('app_gateway')
    params = Models::ApplicationGateway.new
    params.name = application_gateway_name
    params.location = @location
    props = Models::ApplicationGatewayPropertiesFormat.new
    params.properties = props
    sku = Models::ApplicationGatewaySku.new
    props.sku = sku
    sku.name = 'Standard_Small'
    sku.tier = 'Standard'
    sku.capacity = 2
    ip_configuration = Models::ApplicationGatewayIpConfiguration.new
    props.gateway_ip_configurations = [ip_configuration]
    ip_configuration.name = get_random_name('ip_config')
    ip_config_props = Models::ApplicationGatewayIpConfigurationPropertiesFormat.new
    ip_configuration.properties = ip_config_props
    ip_config_props.subnet = subnet
    frontend_ip_config = Models::ApplicationGatewayFrontendIpConfiguration.new
    props.frontend_ip_configurations = [frontend_ip_config]
    frontend_ip_config_name = get_random_name('frontend_ip_config')
    frontend_ip_config.name = frontend_ip_config_name
    frontend_ip_config.id = get_child_app_gw_resource_id(NETWORK_CLIENT.subscription_id, @resource_group.name, application_gateway_name, 'frontendIPConfigurations', frontend_ip_config_name)
    frontend_ip_config_props = Models::ApplicationGatewayFrontendIpConfigurationPropertiesFormat.new
    frontend_ip_config.properties = frontend_ip_config_props
    frontend_ip_config_props.private_ipallocation_method = 'Dynamic'
    frontend_ip_config_props.subnet = subnet
    frontend_port = Models::ApplicationGatewayFrontendPort.new
    props.frontend_ports = [frontend_port]
    frontend_port_name = get_random_name('frontend_port')
    frontend_port.name = frontend_port_name
    frontend_port_props = Models::ApplicationGatewayFrontendPortPropertiesFormat.new
    frontend_port.properties = frontend_port_props
    frontend_port.id = get_child_app_gw_resource_id(NETWORK_CLIENT.subscription_id, @resource_group.name, application_gateway_name, 'frontendPorts', frontend_port_name)
    frontend_port_props.port = 80
    backend_address_pool = Models::ApplicationGatewayBackendAddressPool.new
    props.backend_address_pools = [backend_address_pool]
    backend_address_pool_name = get_random_name('backend_address_pool')
    backend_address_pool.name = backend_address_pool_name
    backend_address_pool.id = get_child_app_gw_resource_id(NETWORK_CLIENT.subscription_id, @resource_group.name, application_gateway_name, 'backendAddressPools', backend_address_pool_name)
    backend_address_pool_props = Models::ApplicationGatewayBackendAddressPoolPropertiesFormat.new
    backend_address_pool.properties = backend_address_pool_props
    backend_address = Models::ApplicationGatewayBackendAddress.new
    backend_address_pool_props.backend_addresses = [backend_address]
    backend_address.ip_address = '104.42.6.202'
    backend_http_set = Models::ApplicationGatewayBackendHttpSettings.new
    props.backend_http_settings_collection = [backend_http_set]
    backend_http_set_name = get_random_name('backend_http_set')
    backend_http_set.name = backend_http_set_name
    backend_http_set.id = get_child_app_gw_resource_id(NETWORK_CLIENT.subscription_id, @resource_group.name, application_gateway_name, 'backendHttpSettingsCollection', backend_http_set_name)
    backend_http_set_props = Models::ApplicationGatewayBackendHttpSettingsPropertiesFormat.new
    backend_http_set.properties = backend_http_set_props
    backend_http_set_props.port = 80
    backend_http_set_props.protocol = 'Http'
    backend_http_set_props.cookie_based_affinity = 'Disabled'
    http_listener = Models::ApplicationGatewayHttpListener.new
    props.http_listeners = [http_listener]
    http_listener_name = get_random_name('http_listener')
    http_listener.name = http_listener_name
    http_listener.id = get_child_app_gw_resource_id(NETWORK_CLIENT.subscription_id, @resource_group.name, application_gateway_name, 'httpListeners', http_listener_name)
    http_listener_props = Models::ApplicationGatewayHttpListenerPropertiesFormat.new
    http_listener.properties = http_listener_props
    http_listener_props.frontend_port = frontend_port
    http_listener_props.frontend_ip_configuration = frontend_ip_config
    http_listener_props.protocol = 'Http'
    request_routing_rule = Models::ApplicationGatewayRequestRoutingRule.new
    props.request_routing_rules = [request_routing_rule]
    request_routing_rule.name = get_random_name('request_route_rule')
    request_routing_rule_props = Models::ApplicationGatewayRequestRoutingRulePropertiesFormat.new
    request_routing_rule.properties = request_routing_rule_props
    request_routing_rule_props.rule_type = 'Basic'
    request_routing_rule_props.http_listener = http_listener
    request_routing_rule_props.backend_address_pool = backend_address_pool
    request_routing_rule_props.backend_http_settings = backend_http_set
    params
  end

 def get_child_app_gw_resource_id(subscriptionId, resourceGroupName, appGwname, childResourceType, childResourceName)
      "/subscriptions/#{subscriptionId}/resourceGroups/#{resourceGroupName}/providers/Microsoft.Network/applicationGateways/#{appGwname}/#{childResourceType}/#{childResourceName}"
 end

end