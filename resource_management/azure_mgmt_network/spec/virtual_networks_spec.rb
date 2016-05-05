# encoding: utf-8
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.

require_relative 'spec_helper'

include MsRestAzure
include Azure::ARM::Resources
include Azure::ARM::Network

describe 'Virtual Networks' do
  before(:each) do
    @resource_helper = ResourceHelper.new()
    @client = @resource_helper.network_client.virtual_networks
    @resource_group = @resource_helper.create_resource_group
    @location = 'westus'
  end

  after(:each) do
    @resource_helper.delete_resource_group(@resource_group.name)
  end

  it 'should create virtual network' do
    virtualNetworkName = "vnet7384"
    params = @resource_helper.build_virtual_network_params(@location)
    result = @client.create_or_update(@resource_group.name, virtualNetworkName, params).value!

    expect(result.response.status).to eq(200)
    expect(result.body).not_to be_nil
    expect(result.body.location).to eq(params.location)
    expect(result.body.name).to eq(virtualNetworkName)
  end

  it 'should get virtual network' do
    vnet = @resource_helper.create_virtual_network(@resource_group.name)
    result = @client.get(@resource_group.name, vnet.name).value!
    expect(result.response.status).to eq(200)
    expect(result.body).not_to be_nil
    expect(result.body.name).to eq(vnet.name)
  end

  it 'should list all virtual networks' do
    result = @client.list_all.value!
    expect(result.body.value).not_to be_nil
    expect(result.body.value).to be_a(Array)

    while !result.body.next_link.nil? && !result.body.next_link.empty? do
      result = @client.list_next(result.body.next_link).value!
      expect(result.body.value).not_to be_nil
      expect(result.body.value).to be_a(Array)
    end
  end

  it 'should list all virtual networks in resource group' do
    result = @client.list(@resource_group.name).value!
    expect(result.body.value).not_to be_nil
    expect(result.body.value).to be_a(Array)

    while !result.body.next_link.nil? && !result.body.next_link.empty? do
      result = @client.list_next(result.body.next_link).value!
      expect(result.body.value).not_to be_nil
      expect(result.body.value).to be_a(Array)
    end
  end

  it 'should list all Virtual Networks in a subscription' do
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

  it 'should delete virtual network' do
    vnet = @resource_helper.create_virtual_network(@resource_group.name)
    result = @client.delete(@resource_group.name, vnet.name).value!
    expect(result.response.status).to eq(200)
  end
end
