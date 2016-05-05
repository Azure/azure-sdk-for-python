# encoding: utf-8
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.

require File.join(File.dirname(__FILE__), '../../vcr_helper')
require 'azure_mgmt_resources'
require 'ms_rest_azure'

include MsRest
include MsRestAzure
include Azure::ARM::Resources

class ResourceHelper
  GOOD_TEMPLATE_URI = 'https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/101-documentdb-account-create/azuredeploy.json'
  attr_accessor :resource_client

  def initialize
    tenant_id = ENV['AZURE_TENANT_ID']
    client_id = ENV['AZURE_CLIENT_ID']
    secret = ENV['AZURE_CLIENT_SECRET']
    subscription_id = ENV['AZURE_SUBSCRIPTION_ID']

    token_provider = ApplicationTokenProvider.new(tenant_id, client_id, secret)
    credentials = TokenCredentials.new(token_provider)

    @resource_client = ResourceManagementClient.new(credentials)
    @resource_client.subscription_id = subscription_id
    @resource_client.long_running_operation_retry_timeout = ENV.fetch('RETRY_TIMEOUT', 30).to_i
  end

  def create_resource_group
    resource_group_name = 'RubySDKTest_azure_mgmt_resources'
    params = Azure::ARM::Resources::Models::ResourceGroup.new()
    params.location = 'westus'

    @resource_client.resource_groups.create_or_update(resource_group_name, params).value!.body
  end

  def delete_resource_group(name)
    @resource_client.resource_groups.delete(name).value!
  end

  def create_deployment(resource_group_name)
    deployment_name = 'Deployment_test'
    params = build_deployment_params
    @resource_client.deployments.create_or_update(resource_group_name, deployment_name, params).value!.body
  end

  def wait_for_deployment(resource_group_name, deployment_name, params)
    tries = 0
    loop do
      begin
        @resource_client.deployments.validate(resource_group_name, deployment_name, params).value!
        break
      rescue Exception
        tries += 1
        sleep(1)
      end

      if tries > 10
        break
      end
    end
  end

  def build_deployment_params()
    params = Models::Deployment.new
    params.properties = Models::DeploymentProperties.new
    template_link = Models::TemplateLink.new
    template_link.uri = GOOD_TEMPLATE_URI
    params.properties.template_link = template_link
    params.properties.mode = Models::DeploymentMode::Incremental
    params.properties.parameters = {
        'databaseAccountName'=> { 'value' => 'mydocs-test'}
    }

    params
  end

  def begin_create_deployment(resource_group_name)
    deployment_name = 'Deployment_test'
    params = build_deployment_params
    @resource_client.deployments.begin_create_or_update(resource_group_name, deployment_name, params).value!.body
  end
end
