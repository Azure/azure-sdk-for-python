# encoding: utf-8
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.

require_relative 'spec_helper'

include MsRestAzure
include Azure::ARM::Resources
include Azure::ARM::Network

describe 'Public IP Addresses' do
  before(:each) do
    @resource_helper = ResourceHelper.new()
    @client = @resource_helper.network_client.public_ipaddresses
    @resource_group = @resource_helper.create_resource_group
    @location = 'westus'
  end

  after(:each) do
    @resource_helper.delete_resource_group(@resource_group.name)
  end

  it 'should create public ip address' do
    params = @resource_helper.build_public_ip_params(@location)
    public_ip_name = 'ip_name_364384'
    result = @client.create_or_update_async(@resource_group.name, public_ip_name, params).value!
    expect(result.response.status).to eq(200)
    expect(result.body).not_to be_nil
    expect(result.body.name).to eq(public_ip_name)
  end

  it 'should get public ip address' do
    address = @resource_helper.create_public_ip_address(@location, @resource_group)
    result = @client.get_async(@resource_group.name, address.name).value!
    expect(result.response.status).to eq(200)
    expect(result.body).not_to be_nil
    expect(result.body.name).to eq(address.name)
  end

  it 'should list all the public ip addresses in a resource group' do
    result = @client.list_async(@resource_group.name).value!
    expect(result.body.value).not_to be_nil
    expect(result.body.value).to be_a(Array)

    while !result.body.next_link.nil? && !result.body.next_link.empty? do
      result = @client.list_next(result.body.next_link).value!
      expect(result.body.value).not_to be_nil
      expect(result.body.value).to be_a(Array)
    end
  end

  it 'should delete public ip address' do
    address = @resource_helper.create_public_ip_address(@location, @resource_group)
    result = @client.delete_async(@resource_group.name, address.name).value!
    expect(result.response.status).to eq(200)
  end

  it 'should list all the public ip addresses in a subscription' do
    result = @client.list_all_async.value!
    expect(result.response.status).to eq(200)
    expect(result.body).not_to be_nil
    expect(result.body.value).to be_a(Array)
    while !result.body.next_link.nil? && !result.body.next_link.empty? do
      result = @client.list_all_next(result.body.next_link).value!
      expect(result.body.value).not_to be_nil
      expect(result.body.value).to be_a(Array)
    end
  end
end
