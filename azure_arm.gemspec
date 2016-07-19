# encoding: utf-8
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.

version = File.read(File.expand_path('../ARM_VERSION', __FILE__)).strip

Gem::Specification.new do |spec|
  spec.name          = 'azure_arm'
  spec.version       = version
  spec.authors       = 'Microsoft Corporation'
  spec.email         = 'azrubyteam@microsoft.com'
  spec.description   = 'Microsoft Azure ARM Client Library for Ruby'
  spec.summary       = 'Official Ruby client library to consume Microsoft Azure ARM services.'
  spec.homepage      = 'http://github.com/azure/azure-sdk-ruby'
  spec.license       = 'MIT'

  spec.required_ruby_version = '>= 1.9.3'

  spec.add_development_dependency 'bundler', '~> 1.9'
  spec.add_development_dependency 'rake', '~> 10'
  spec.add_development_dependency 'rspec', '~> 3'
  spec.add_development_dependency 'dotenv', '~> 2'

  spec.add_runtime_dependency 'azure_mgmt_authorization', version
  spec.add_runtime_dependency 'azure_mgmt_batch', version
  spec.add_runtime_dependency 'azure_mgmt_cdn', version
  spec.add_runtime_dependency 'azure_mgmt_cognitive_services', version
  spec.add_runtime_dependency 'azure_mgmt_commerce', version
  spec.add_runtime_dependency 'azure_mgmt_compute', version
  spec.add_runtime_dependency 'azure_mgmt_datalake_analytics', version
  spec.add_runtime_dependency 'azure_mgmt_datalake_store', version
  spec.add_runtime_dependency 'azure_mgmt_devtestlabs', version
  spec.add_runtime_dependency 'azure_mgmt_dns', version
  spec.add_runtime_dependency 'azure_mgmt_features', version
  spec.add_runtime_dependency 'azure_mgmt_graph', version
  spec.add_runtime_dependency 'azure_mgmt_key_vault', version
  spec.add_runtime_dependency 'azure_mgmt_locks', version
  spec.add_runtime_dependency 'azure_mgmt_logic', version
  spec.add_runtime_dependency 'azure_mgmt_machine_learning', version
  spec.add_runtime_dependency 'azure_mgmt_media_services', version
  spec.add_runtime_dependency 'azure_mgmt_mobile_engagement', version
  spec.add_runtime_dependency 'azure_mgmt_network', version
  spec.add_runtime_dependency 'azure_mgmt_notification_hubs', version
  spec.add_runtime_dependency 'azure_mgmt_policy', version
  spec.add_runtime_dependency 'azure_mgmt_powerbi_embedded', version
  spec.add_runtime_dependency 'azure_mgmt_redis', version
  spec.add_runtime_dependency 'azure_mgmt_resources', version
  spec.add_runtime_dependency 'azure_mgmt_scheduler', version
  spec.add_runtime_dependency 'azure_mgmt_search', version
  spec.add_runtime_dependency 'azure_mgmt_server_management', version
  spec.add_runtime_dependency 'azure_mgmt_service_bus', version
  spec.add_runtime_dependency 'azure_mgmt_sql', version
  spec.add_runtime_dependency 'azure_mgmt_storage', version
  spec.add_runtime_dependency 'azure_mgmt_subscriptions', version
  spec.add_runtime_dependency 'azure_mgmt_traffic_manager', version
  spec.add_runtime_dependency 'azure_mgmt_web', version
end
