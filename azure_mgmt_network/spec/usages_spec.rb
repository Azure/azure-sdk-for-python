# encoding: utf-8
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.

require_relative 'spec_helper'

include MsRestAzure
include Azure::ARM::Network

describe 'Usages' do
  before(:each) do
    @resource_helper = ResourceHelper.new()
    @location = 'westus'
    @client = @resource_helper.network_client.usages
  end

  it 'should list compute usages for subscription' do
    result = @client.list_async(@location).value!
    expect(result.response.status).to eq(200)
    expect(result.body).not_to be_nil
    expect(result.body.value).to be_a(Array)
  end
end
