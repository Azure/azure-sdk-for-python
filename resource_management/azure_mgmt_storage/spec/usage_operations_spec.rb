# encoding: utf-8
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.

require_relative 'spec_helper'

include MsRestAzure
include Azure::ARM::Storage

describe 'Usage Operations' do
  before(:each) do
    @resource_helper = ResourceHelper.new
    @storage_client = @resource_helper.storage_client
    @client = @storage_client.usage_operations
    @resource_group = @resource_helper.create_resource_group
  end

  after(:each) do
    @resource_helper.delete_resource_group(@resource_group.name)
  end

  it 'list usage operations' do
    result = @client.list.value!
    expect(result.body.value).not_to be_nil
    expect(result.body.value).to be_a(Array)
  end
end
