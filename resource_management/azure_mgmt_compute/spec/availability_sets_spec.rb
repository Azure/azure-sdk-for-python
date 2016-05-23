# encoding: utf-8
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.

require_relative 'spec_helper'

include MsRestAzure
include Azure::ARM::Resources
include Azure::ARM::Compute

describe ComputeManagementClient do
  before(:each) do
    @resource_helper = ResourceHelper.new
    @client = @resource_helper.compute_client.availability_sets
    @resource_group = @resource_helper.create_resource_group
    @resource_identity = 'Microsoft.Compute/availabilitySets'
  end

  after(:each) do
    @resource_helper.delete_resource_group(@resource_group.name)
  end

  it 'should create availability set' do
    availabilitySetName = 'test-availability-set'
    params = @resource_helper.build_availability_set_parameters
    result = @client.create_or_update_async(@resource_group.name, availabilitySetName, params).value!
    expect(result.response.status).to eq(200)
    expect(result.body).not_to be_nil
    expect(result.body.location).to eq(params.location)
    expect(result.body.type).to eq(@resource_identity)
    expect(result.body.name).to eq(availabilitySetName)
  end

  it 'should get availability set' do
    resource = @resource_helper.create_availability_set(@client, @resource_group)

    result = @client.get_async(
        @resource_group.name,
        resource.name,
    ).value!
    expect(result.response.status).to eq(200)
    expect(result.body).not_to be_nil
    expect(result.body.name).to eq(resource.name)
    expect(result.body.type).to eq(@resource_identity)
  end

  it 'should list availability sets' do
    result = @client.list_async(@resource_group.name).value!
    expect(result.body.value).not_to be_nil
    expect(result.body.value).to be_a(Array)
  end

  it 'should delete availability set' do
    resource = @resource_helper.create_availability_set(@client, @resource_group)

    result = @client.delete_async(
        @resource_group.name,
        resource.name
    ).value!
    expect(result.response.status).to eq(200)
  end

  it 'should list available sizes of availability sets' do
    resource = @resource_helper.create_availability_set(@client, @resource_group)
    result = @client.list_available_sizes_async(@resource_group.name, resource.name).value!
    expect(result.response.status).to eq(200)
    expect(result.body.value).not_to be_nil
    expect(result.body.value).to be_a Array
  end
end
