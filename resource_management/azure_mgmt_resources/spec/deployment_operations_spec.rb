# encoding: utf-8
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.

require_relative 'spec_helper'

include MsRestAzure
include Azure::ARM::Resources

describe 'Deployment Operations' do
  before(:each) do
    @resource_helper = ResourceHelper.new()
    @client = @resource_helper.resource_client.deployment_operations
    @resource_group = @resource_helper.create_resource_group
    @deployment = @resource_helper.create_deployment(@resource_group.name)
    @resource_helper.wait_for_deployment(@resource_group.name, @deployment.name, @resource_helper.build_deployment_params)
  end

  after(:each) do
    @resource_helper.delete_resource_group(@resource_group.name)
  end

  it 'should get a list of deployment operations' do
    result = @client.list_async(@resource_group.name, @deployment.name).value!
    expect(result.response.status).to eq(200)
    expect(result.body).not_to be_nil
    expect(result.body.value).to be_a(Array)

    while !result.body.next_link.nil? && !result.body.next_link.empty?  do
      result = @client.list_next(result.body.next_link).value!
      expect(result.body.value).not_to be_nil
      expect(result.body.value).to be_a(Array)
    end
  end

  it 'should get a list of deployment operation restricted with top parameter' do
    result = @client.list_async(@resource_group.name, @deployment.name, 1).value!
    expect(result.response.status).to eq(200)
    expect(result.body).not_to be_nil
    expect(result.body.value).to be_a(Array)

    while !result.body.next_link.nil? && !result.body.next_link.empty?  do
      result = @client.list_next_async(result.body.next_link).value!
      expect(result.body.value).not_to be_nil
      expect(result.body.value).to be_a(Array)
    end
  end

  it 'should get a deployment operation' do
    operations = @client.list_async(@resource_group.name, @deployment.name).value!.body.value

    result = @client.get_async(@resource_group.name, @deployment.name, operations[0].operation_id).value!
    expect(result.response.status).to eq(200)
    expect(result.body.operation_id).to eq(operations[0].operation_id)
    expect(result.body.id).not_to be_nil
    expect(result.body.properties).to be_an_instance_of(Models::DeploymentOperationProperties)
  end
end
