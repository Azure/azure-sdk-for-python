# encoding: utf-8
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.

require_relative 'spec_helper'

include MsRestAzure
include Azure::ARM::Resources

describe 'Resource Provider Operation Details' do
  before(:each) do
    @resource_helper = ResourceHelper.new()
    @client = @resource_helper.resource_client.resource_provider_operation_details
    @resource_api_version = '2015-06-15'
    @providers_client = @resource_helper.resource_client.providers
    @details_client = @resource_helper.resource_client.resource_provider_operation_details
  end

  it 'should list provider operation details' do
    providers = @providers_client.list.value!.body.value

    # Selecting specific provider since not all providers might be registered for current subscription.
    target_provider = providers.detect {|item| item.registration_state == 'Registered' && item.namespace == 'Microsoft.Compute' }

    result = @details_client.list(target_provider.namespace, @resource_api_version).value!
    expect(result.body.value).not_to be_nil
    expect(result.body.value).to be_a(Array)
  end
end
