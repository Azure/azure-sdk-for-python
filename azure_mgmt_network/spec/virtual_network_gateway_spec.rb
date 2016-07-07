# encoding: utf-8
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.

require_relative 'spec_helper'

include MsRestAzure
include Azure::ARM::Resources
include Azure::ARM::Network

describe VirtualNetworkGateways do

  before(:all) do
    skip('virtual network gateways aren\'t properly supported yet')

    @client = NETWORK_CLIENT.virtual_network_gateways
    @location = 'westus'
    @resource_group = create_resource_group
  end
  after(:all) do
    delete_resource_group(@resource_group.name) unless @resource_group.nil?
  end

  example 'virtual network gateway api' do
    skip('no long running tasks should be performed') unless RUN_LONG_TASKS
    # create virtual network gateway
    params = build_virtual_network_gateway_params(@location, @resource_group)
    result = @client.create_or_update(@resource_group.name, params.name, params).value!
    expect(result.response.status).to eq(200)
    expect(result.body).not_to be_nil
    expect(result.body.name).to eq(params.name)
    virtual_network_gateway = result.body
    # get virtual network gateway
    result = @client.get(@resource_group.name, virtual_network_gateway.name).value!
    expect(result.response.status).to eq(200)
    expect(result.body).not_to be_nil
    expect(result.body.name).to eq(virtual_network_gateway.name)
    # reset virtual network gateway
    result = @client.reset(@resource_group.name, virtual_network_gateway.name, virtual_network_gateway).value!
    expect(result.response.status).to eq(200)
    # delete virtual network gateway
    result = @client.delete(@resource_group.name, virtual_network_gateway.name).value!
    expect(result.response.status).to eq(200)
  end


  it 'should list all the virtual network gateways stored' do
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


end