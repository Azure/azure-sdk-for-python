# encoding: utf-8
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.

require File.join(File.dirname(__FILE__), '../../vcr_helper')
require 'azure_mgmt_resources'
require 'azure_mgmt_compute'
require 'ms_rest_azure'
require 'azure_mgmt_storage'
require 'azure_mgmt_network'

include MsRest
include MsRestAzure
include Azure::ARM::Compute
include Azure::ARM::Compute::Models
include Azure::ARM::Network
include Azure::ARM::Resources
include Azure::ARM::Storage

class ResourceHelper
  attr_reader :compute_client, :network_client, :resource_client, :storage_client

  def initialize
    tenant_id = ENV['AZURE_TENANT_ID']
    client_id = ENV['AZURE_CLIENT_ID']
    secret = ENV['AZURE_CLIENT_SECRET']
    @subscription_id = ENV['AZURE_SUBSCRIPTION_ID']

    token_provider = ApplicationTokenProvider.new(tenant_id, client_id, secret)
    @credentials = TokenCredentials.new(token_provider)
  end

  def compute_client
    if @compute_client.nil?
      @compute_client = ComputeManagementClient.new(@credentials)
      @compute_client.long_running_operation_retry_timeout = ENV.fetch('RETRY_TIMEOUT', 30).to_i
      @compute_client.subscription_id = @subscription_id
    end
    @compute_client
  end

  def network_client
    if @network_client.nil?
      @network_client = NetworkManagementClient.new(@credentials)
      @network_client.long_running_operation_retry_timeout = ENV.fetch('RETRY_TIMEOUT', 30).to_i
      @network_client.subscription_id = @subscription_id
    end
    @network_client
  end

  def resource_client
    if @resource_client.nil?
      @resource_client = ResourceManagementClient.new(@credentials)
      @resource_client.subscription_id = @subscription_id
      @resource_client.long_running_operation_retry_timeout = ENV.fetch('RETRY_TIMEOUT', 30).to_i
    end
    @resource_client
  end

  def storage_client
    if @storage_client.nil?
      @storage_client = StorageManagementClient.new(@credentials)
      @storage_client.long_running_operation_retry_timeout = ENV.fetch('RETRY_TIMEOUT', 30).to_i
      @storage_client.subscription_id = @subscription_id
    end
    @storage_client
  end

  def create_resource_group
    resource_group_name = 'RubySDKTest_azure_mgmt_compute'
    params = Azure::ARM::Resources::Models::ResourceGroup.new()
    params.location = 'westus'

    resource_client.resource_groups.create_or_update_async(resource_group_name, params).value!.body
  end

  def delete_resource_group(name)
    resource_client.resource_groups.delete(name)
  end

  def create_availability_set(client, resource_group)
    availabilitySetName = 'test-availability-set'
    params = build_availability_set_parameters
    client.create_or_update_async(resource_group.name, availabilitySetName, params).value!.body
  end

  def build_availability_set_parameters
    params = AvailabilitySet.new()
    params.location = 'westus'

    params
  end
end

class String
  def to_b?
    !self.to_i.zero?
  end
end

