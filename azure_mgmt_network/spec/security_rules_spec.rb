# encoding: utf-8
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.

require_relative 'spec_helper'

include MsRestAzure
include Azure::ARM::Resources
include Azure::ARM::Network

describe 'Security Rules' do
  before(:each) do
    @resource_helper = ResourceHelper.new()
    @client = @resource_helper.network_client.security_rules
    @location = 'westus'
    @resource_group = @resource_helper.create_resource_group
    @security_group = @resource_helper.create_network_security_group(@resource_group, @location)
  end

  after(:each) do
    @resource_helper.delete_resource_group(@resource_group.name)
  end

  it 'should create security rule' do
    params = build_security_rule_params
    result = @client.create_or_update_async(@resource_group.name, @security_group.name, params.name, params).value!
    expect(result.response.status).to eq(200)
    expect(result.body).not_to be_nil
    expect(result.body.name).to eq(params.name)
  end

  it 'should get security rule' do
    security_rule = create_security_rule
    result = @client.get_async(@resource_group.name, @security_group.name, security_rule.name).value!
    expect(result.response.status).to eq(200)
    expect(result.body).not_to be_nil
    expect(result.body.name).to eq(security_rule.name)
  end

  it 'should delete security rule' do
    security_rule = create_security_rule
    result = @client.delete_async(@resource_group.name, @security_group.name, security_rule.name).value!
    expect(result.response.status).to eq(200)
  end

  it 'should list all the security rules in a network security group' do
    result = @client.list_async(@resource_group.name, @security_group.name).value!
    expect(result.response.status).to eq(200)
    expect(result.body).not_to be_nil
    expect(result.body.value).to be_a(Array)
    while !result.body.next_link.nil? && !result.body.next_link.empty? do
      result = @client.list_all_next(result.body.next_link).value!
      expect(result.body.value).not_to be_nil
      expect(result.body.value).to be_a(Array)
    end
  end

  def create_security_rule
    params = build_security_rule_params
    @client.create_or_update(@resource_group.name, @security_group.name, params.name, params)
  end

  def build_security_rule_params
    params = SecurityRule.new
    params.name = 'sec_rule_7428'
    params.access = 'Deny'
    params.destination_address_prefix = '*'
    params.destination_port_range = '123-3500'
    params.direction = 'Outbound'
    params.priority = 4095
    params.protocol = 'Udp'
    params.source_address_prefix = '*'
    params.source_port_range = '656'
    params
  end
end
