# encoding: utf-8
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.

require_relative 'spec_helper'

include MsRestAzure
include Azure::ARM::Resources
include Azure::ARM::Network

describe 'Local Network Gateways' do
  before(:each) do
    @resource_helper = ResourceHelper.new()
    @client = @resource_helper.network_client.local_network_gateways
    @location = 'westus'
    @resource_group = @resource_helper.create_resource_group
  end

  after(:each) do
    @resource_helper.delete_resource_group(@resource_group.name)
  end

  it 'should create local network gateway' do
    params = @resource_helper.build_local_network_gateway_params(@location)
    result = @client.create_or_update_async(@resource_group.name, params.name, params).value!
    expect(result.response.status).to eq(200)
    expect(result.body).not_to be_nil
    expect(result.body.name).to eq(params.name)
  end

  it 'should get local network gateway' do
    local_network_gateway = @resource_helper.create_local_network_gateway(@resource_group, @location)
    result = @client.get_async(@resource_group.name, local_network_gateway.name).value!
    expect(result.response.status).to eq(200)
    expect(result.body).not_to be_nil
    expect(result.body.name).to eq(local_network_gateway.name)
  end

  it 'should delete local network gateway' do
    local_network_gateway = @resource_helper.create_local_network_gateway(@resource_group, @location)
    result = @client.delete_async(@resource_group.name, local_network_gateway.name).value!
    expect(result.response.status).to eq(200)
  end

  it 'should list all the local network gateways' do
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
end
