# encoding: utf-8
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.

require_relative 'spec_helper'

include MsRestAzure
include Azure::ARM::Resources
include Azure::ARM::Network

describe VirtualNetworkGatewayConnections do

  before(:all) do
    skip('gateway connections aren\'t properly supported yet')

    @client = NETWORK_CLIENT.virtual_network_gateway_connections
    @location = 'westus'
    @resource_group = create_resource_group('gateway_test')
    @vnet_gateway = create_virtual_network_gateway(@location, @resource_group, @vnet_gateway_name) if RUN_LONG_TASKS
  end

  before do
    # for every virtual network gateway connection need to be created different localnet and virtualnet pairs
    @localnet_gateway = create_local_network_gateway(@resource_group, @location) if RUN_LONG_TASKS
  end
  after(:all) do
    delete_resource_group(@resource_group.name) unless @resource_group.nil?
  end

  it 'should list virtual network gateway connections' do
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

  it 'should create virtual network gateway connection' do
    skip('no long running tasks should be performed') unless RUN_LONG_TASKS
    params = build_vnet_gateway_conn_params
    result = @client.create_or_update(@resource_group.name, params.name, params).value!
    expect(result.response.status).to eq(200)
    expect(result.body).not_to be_nil
    expect(result.body.name).to eq(params.name)
  end

  it 'should get gateway connection' do
    skip('no long running tasks should be performed') unless RUN_LONG_TASKS
    gateway_connection = create_vnet_gateway_connection
    result = @client.get(@resource_group.name, gateway_connection.name).value!
    expect(result.response.status).to eq(200)
    expect(result.body).not_to be_nil
    expect(result.body.name).to eq(gateway_connection.name)
  end

  it 'should delete gateway connection' do
    skip('no long running tasks should be performed') unless RUN_LONG_TASKS
    conn = create_vnet_gateway_connection
    result = @client.delete(@resource_group.name, conn.name).value!
    expect(result.response.status).to eq(200)
  end

  it 'should set connection shared key' do
    skip('no long running tasks should be performed') unless RUN_LONG_TASKS
    conn = create_vnet_gateway_connection
    shared_key = Models::ConnectionSharedKey.new
    shared_key.value = 'TestSharedKeyValue'
    result = @client.set_shared_key(@resource_group.name, conn.name, shared_key).value!
    expect(result.response.status).to eq(200)
  end

  it 'should get connection shared key' do
    skip('no long running tasks should be performed') unless RUN_LONG_TASKS
    conn = create_vnet_gateway_connection
    result = @client.get_shared_key(@resource_group.name, conn.name).value!
    expect(result.response.status).to eq(200)
  end

  it 'should reset connection shared key' do
    skip('no long running tasks should be performed') unless RUN_LONG_TASKS
    conn = create_vnet_gateway_connection
    reset_shared_key = Models::ConnectionResetSharedKey.new
    reset_shared_key_props = Models::ConnectionResetSharedKeyPropertiesFormat.new
    reset_shared_key.properties = reset_shared_key_props
    reset_shared_key_props.key_length = 50
    result = @client.reset_shared_key(@resource_group.name, conn.name, reset_shared_key).value!
    expect(result.response.status).to eq(200)
  end

  def create_vnet_gateway_connection
    params = build_vnet_gateway_conn_params
    @client.create_or_update(@resource_group.name, params.name, params).value!.body
  end

  def build_vnet_gateway_conn_params
    params = Models::VirtualNetworkGatewayConnection.new
    params.location = @location
    params.name = get_random_name('vnet_conn')
    props = Models::VirtualNetworkGatewayConnectionPropertiesFormat.new
    params.properties = props
    props.virtual_network_gateway1 = @vnet_gateway
    props.local_network_gateway2 = @localnet_gateway
    props.connection_type = 'IPsec'
    props.routing_weight = rand(9)
    props.shared_key = get_random_name('', 3)
    params
  end
end