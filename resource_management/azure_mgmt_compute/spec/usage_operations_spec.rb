# encoding: utf-8
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.

require_relative 'spec_helper'

include MsRestAzure
include Azure::ARM::Compute

describe UsageOperations do
  before(:each) do
    @resource_helper = ResourceHelper.new
    @client = @resource_helper.compute_client.usage_operations
  end

  it 'should list usages' do
    result = @client.list('westus').value!
    expect(result.response.status).to eq(200)
    expect(result.body).not_to be_nil
    expect(result.body.value).to be_a Array
  end
end