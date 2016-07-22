# encoding: utf-8
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.

require_relative 'spec_helper'

include MsRestAzure
include Azure::ARM::Resources
include Azure::ARM::Network
include Azure::ARM::Network::Models

describe 'Load balancers' do
  before(:each) do
    @resource_helper = ResourceHelper.new()
    @client = @resource_helper.network_client.load_balancers
    @location = 'westus'
    @resource_group = @resource_helper.create_resource_group
  end
  after(:each) do
    @resource_helper.delete_resource_group(@resource_group.name)
  end

  it 'should create load balancer' do
    params = build_load_balancer_params
    result = @client.create_or_update_async(@resource_group.name, params.name, params).value!
    expect(result.response.status).to eq(201)
    expect(result.body).not_to be_nil
    expect(result.body.name).to eq(params.name)
  end

  it 'should create load balancer with complex parameter structure' do
    #create public ip address Dns Settings
    dns_settings = PublicIPAddressDnsSettings.new

    #create public ip address
    lb_public_ip_name = 'test_public_ip'
    lb_domain_name_label = 'test-domain8564'
    public_ip = PublicIPAddress.new
    public_ip.location = @location
    public_ip.public_ipallocation_method = 'Dynamic'
    public_ip.dns_settings = dns_settings

    dns_settings.domain_name_label = lb_domain_name_label
    public_ip = @resource_helper.network_client.public_ipaddresses.create_or_update(@resource_group.name, lb_public_ip_name, public_ip)

    #create virtual network
    @resource_helper.create_virtual_network(@resource_group.name)

    #create the load balancer
    lb_name = 'test_lb_name'
    frontend_ip_config_name = 'frontend_ip_config_name'
    backend_address_pool_name = 'backend_address_pool_name'
    load_balancing_rule_name = 'load_balancing_rule_name'
    probe_name = 'probe_name'
    inbound_nat_rule1_name = 'inbound_nat_rule8564'
    inbound_nat_rule2_name = 'inbound_nat_rule8675'

    #populate load_balancer create_or_update parameter
    load_balancer = LoadBalancer.new
    load_balancer.location = @location

    frontend_ip_configuration = FrontendIPConfiguration.new
    frontend_ip_configuration.name = frontend_ip_config_name
    frontend_ip_configuration.public_ipaddress = public_ip
    load_balancer.frontend_ipconfigurations = [frontend_ip_configuration]

    backend_address_pool = BackendAddressPool.new
    backend_address_pool.name = backend_address_pool_name
    load_balancer.backend_address_pools = [backend_address_pool]

    load_balancing_rule = LoadBalancingRule.new
    load_balancing_rule.name = load_balancing_rule_name
    frontend_ip_configuration_sub_resource = MsRestAzure::SubResource.new
    frontend_ip_configuration_sub_resource.id =
        get_child_lb_resource_id(@resource_helper.network_client.subscription_id, @resource_group.name,
                                 lb_name, 'FrontendIPConfigurations', frontend_ip_config_name)
    load_balancing_rule.frontend_ipconfiguration = frontend_ip_configuration_sub_resource
    load_balancing_rule.protocol = 'Tcp'
    load_balancing_rule.frontend_port = 80
    load_balancing_rule.backend_port = 80
    load_balancing_rule.enable_floating_ip = false
    load_balancing_rule.idle_timeout_in_minutes = 15
    backend_address_pool_sub_resource = MsRestAzure::SubResource.new
    backend_address_pool_sub_resource.id =
        get_child_lb_resource_id(@resource_helper.network_client.subscription_id, @resource_group.name,
                                 lb_name, 'backendAddressPools', backend_address_pool_name)
    load_balancing_rule.backend_address_pool = backend_address_pool_sub_resource
    probe_sub_resource = MsRestAzure::SubResource.new
    probe_sub_resource.id =
        get_child_lb_resource_id(@resource_helper.network_client.subscription_id, @resource_group.name,
                                 lb_name, 'probes', probe_name)
    load_balancing_rule.probe = probe_sub_resource

    load_balancer.load_balancing_rules = [load_balancing_rule]

    probe = Probe.new
    probe.name = probe_name
    probe.protocol = 'Http'
    probe.port = 80
    probe.request_path = 'healthcheck.aspx'
    probe.interval_in_seconds = 10
    probe.number_of_probes = 2
    load_balancer.probes = [probe]

    inbound_nat_rule1 = InboundNatRule.new
    inbound_nat_rule1.name = inbound_nat_rule1_name
    inbound_nat_rule1.frontend_ipconfiguration = frontend_ip_configuration_sub_resource
    inbound_nat_rule1.protocol = 'Tcp'
    inbound_nat_rule1.frontend_port = 3389
    inbound_nat_rule1.backend_port = 3389
    inbound_nat_rule1.idle_timeout_in_minutes = 15
    inbound_nat_rule1.enable_floating_ip = false

    inbound_nat_rule2 = InboundNatRule.new
    inbound_nat_rule2.name = inbound_nat_rule2_name
    inbound_nat_rule2.frontend_ipconfiguration = frontend_ip_configuration_sub_resource
    inbound_nat_rule2.protocol = 'Tcp'
    inbound_nat_rule2.frontend_port = 3390
    inbound_nat_rule2.backend_port = 3389
    inbound_nat_rule2.idle_timeout_in_minutes = 15
    inbound_nat_rule2.enable_floating_ip = false

    load_balancer.inbound_nat_rules = [inbound_nat_rule1, inbound_nat_rule2]

    #create load balancer
    result = @client.create_or_update_async(@resource_group.name, lb_name, load_balancer).value!
    expect(result.response.status).to eq(201)
    expect(result.body).not_to be_nil
    expect(result.body.name).to eq(lb_name)
  end

  it 'should work with TCP and UDP balance rules' do
    vnet = @resource_helper.create_virtual_network(@resource_group.name)
    subnet = @resource_helper.create_subnet(vnet, @resource_group, @resource_helper.network_client.subnets)
    params = build_load_balancer_params
    frontend_ip_configuration = FrontendIPConfiguration.new
    params.frontend_ipconfigurations = [frontend_ip_configuration]
    ip_config_name = 'frontend_ip_config'
    frontend_ip_configuration.name = ip_config_name
    frontend_ip_configuration.id = get_child_lb_resource_id(@resource_helper.network_client.subscription_id, @resource_group.name, params.name,'frontendIPConfigurations', ip_config_name)
    frontend_ip_configuration.private_ipallocation_method = 'Dynamic'
    frontend_ip_configuration.subnet = subnet
    udp_rule = LoadBalancingRule.new
    udp_rule.name = 'udp_rule'
    udp_rule.frontend_ipconfiguration = frontend_ip_configuration
    udp_rule.protocol = 'Udp'
    udp_rule.frontend_port = 80
    udp_rule.backend_port = 80
    tcp_rule = LoadBalancingRule.new
    tcp_rule.name = 'tcp_rule'
    tcp_rule.frontend_ipconfiguration = frontend_ip_configuration
    tcp_rule.protocol = 'Tcp'
    tcp_rule.frontend_port = 80
    tcp_rule.backend_port = 80
    params.load_balancing_rules = [udp_rule, tcp_rule]
    inbound_udp = InboundNatRule.new
    inbound_tcp = InboundNatRule.new
    params.inbound_nat_rules = [inbound_udp, inbound_tcp]
    inbound_udp.name = 'inbound_udp_rule'
    inbound_tcp.name = 'inbound_tcp_rule'
    inbound_udp.frontend_ipconfiguration = frontend_ip_configuration
    inbound_tcp.frontend_ipconfiguration = frontend_ip_configuration
    inbound_udp.protocol = 'Udp'
    inbound_tcp.protocol = 'Tcp'
    inbound_udp.frontend_port = 32900
    inbound_tcp.frontend_port = 32900
    inbound_udp.backend_port = 32900
    inbound_tcp.backend_port = 32900
    @client.create_or_update(@resource_group.name, params.name, params)
    result = @client.list_all_async.value!
    expect(result.response.status).to eq(200)
  end

  it 'should get load balancer' do
    load_balancer = create_load_balancer
    result = @client.get_async(@resource_group.name, load_balancer.name).value!
    expect(result.response.status).to eq(200)
    expect(result.body).not_to be_nil
    expect(result.body.name).to eq(load_balancer.name)
  end

  it 'should delete load balancer' do
    load_balancer = create_load_balancer
    result = @client.delete_async(@resource_group.name, load_balancer.name).value!
    expect(result.response.status).to eq(200)
  end

  it 'should list loadbalancers in a subscription' do
    result = @client.list_all_async.value!
    expect(result.response.status).to eq(200)
    expect(result.body).not_to be_nil
    expect(result.body.value).to be_a(Array)
    while !result.body.next_link.nil? && !result.body.next_link.empty? do
      result = @client.list_all_next(result.body.next_link)
      expect(result.body.value).not_to be_nil
      expect(result.body.value).to be_a(Array)
    end
  end

  it 'should list loadbalancers in a resource group' do
    result = @client.list_async(@resource_group.name).value!
    expect(result.response.status).to eq(200)
    expect(result.body).not_to be_nil
    expect(result.body.value).to be_a(Array)
    while !result.body.next_link.nil? && !result.body.next_link.empty? do
      result = @client.list_next(result.body.next_link).value!
      expect(result.body.value).not_to be_nil
      expect(result.body.value).to be_a(Array)
    end
  end

  def get_child_lb_resource_id(subscriptionId, resourceGroupName, lbname, childResourceType, childResourceName)
    "/subscriptions/#{subscriptionId}/resourceGroups/#{resourceGroupName}/providers/Microsoft.Network/loadBalancers/#{lbname}/#{childResourceType}/#{childResourceName}"
  end

  def create_load_balancer
    params = build_load_balancer_params
    @client.create_or_update(@resource_group.name, params.name, params)
  end

  def build_load_balancer_params
    params = LoadBalancer.new
    params.location = @location
    params.name = 'load_balancer_test'
    params
  end
end
