# encoding: utf-8
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.

require File.join(File.dirname(__FILE__), '../../vcr_helper')
require 'azure_mgmt_resources'
require 'azure_mgmt_storage'
require 'ms_rest_azure'

include MsRest
include MsRestAzure
include Azure::ARM::Resources
include Azure::ARM::Storage

class ResourceHelper
  attr_accessor :storage_client
  attr_accessor :resource_client

  def initialize
    tenant_id = ENV['AZURE_TENANT_ID']
    client_id = ENV['AZURE_CLIENT_ID']
    secret = ENV['AZURE_CLIENT_SECRET']
    subscription_id = ENV['AZURE_SUBSCRIPTION_ID']

    token_provider = ApplicationTokenProvider.new(tenant_id, client_id, secret)
    credentials = TokenCredentials.new(token_provider)

    @storage_client = StorageManagementClient.new(credentials)
    @storage_client.long_running_operation_retry_timeout = ENV['RETRY_TIMEOUT'].to_i || 30
    @storage_client.subscription_id = subscription_id

    @resource_client = ResourceManagementClient.new(credentials)
    @resource_client.subscription_id = subscription_id
    @resource_client.long_running_operation_retry_timeout = ENV['RETRY_TIMEOUT'].to_i || 30
  end

  def create_resource_group
    resource_group_name = 'RubySDKTest_azure_mgmt_storage'
    params = Azure::ARM::Resources::Models::ResourceGroup.new
    params.location = 'westus'

    @resource_client.resource_groups.create_or_update(resource_group_name, params)
  end

  def delete_resource_group(name)
    @resource_client.resource_groups.delete(name)
  end
end
