# encoding: utf-8
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.

require File.join(File.dirname(__FILE__), '../../vcr_helper')
require 'azure_mgmt_resources'
require 'azure_mgmt_datalake_store'
require 'ms_rest_azure'

include MsRest
include MsRestAzure
include Azure::ARM::Resources
include Azure::ARM::DataLakeStore

class ResourceHelper
  attr_reader :resource_client, :dls_acc_client, :dls_fs_client

  def initialize
    tenant_id = ENV['AZURE_TENANT_ID']
    client_id = ENV['AZURE_CLIENT_ID']
    secret = ENV['AZURE_CLIENT_SECRET']
    @subscription_id = ENV['AZURE_SUBSCRIPTION_ID']

    token_provider = ApplicationTokenProvider.new(tenant_id, client_id, secret)
    @credentials = TokenCredentials.new(token_provider)
  end

  def resource_client
    if @resource_client.nil?
      @resource_client = ResourceManagementClient.new(@credentials)
      @resource_client.subscription_id = @subscription_id
      @resource_client.long_running_operation_retry_timeout = ENV.fetch('RETRY_TIMEOUT', 30).to_i
    end
    @resource_client
  end

  def dls_acc_client
    if @dls_acc_client.nil?
      @dls_acc_client = Account::DataLakeStoreAccountManagementClient.new(@credentials)
      @dls_acc_client.subscription_id = @subscription_id
      @dls_acc_client.long_running_operation_retry_timeout = ENV.fetch('RETRY_TIMEOUT', 30).to_i
    end
    @dls_acc_client
  end

  def dls_fs_client
    if @dls_fs_client.nil?
      @dls_fs_client = FileSystem::DataLakeStoreFileSystemManagementClient.new(@credentials)
      @dls_fs_client.long_running_operation_retry_timeout = ENV.fetch('RETRY_TIMEOUT', 30).to_i
    end
    @dls_fs_client
  end

  def create_resource_group
    resource_group_name = 'RubySDKTest_azure_mgmt_dl_store'
    params = Azure::ARM::Resources::Models::ResourceGroup.new()
    params.location = 'East US 2'

    resource_client.resource_groups.create_or_update(resource_group_name, params)
  end

  def delete_resource_group(name)
    resource_client.resource_groups.delete(name)
  end
end