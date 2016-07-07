# encoding: utf-8
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.

require 'dotenv'
Dotenv.load(File.join(File.dirname(__FILE__), '.env'))
require 'vcr'

# This will be overridden with dummy values when running in travis-ci
if !ENV['INTEG_RECORDED'].nil? && ENV['INTEG_RECORDED'] == 'true'
  ENV['AZURE_TENANT_ID'] = '11111111-1111-1111-1111-111111111111'
  ENV['AZURE_CLIENT_ID'] = '11111111-1111-1111-1111-111111111111'
  ENV['AZURE_CLIENT_SECRET'] = 'SECRET'
  ENV['AZURE_SUBSCRIPTION_ID'] = '11111111-1111-1111-1111-111111111111'
  ENV['RETRY_TIMEOUT'] = '0'
end

VCR.configure do |config|
  config.default_cassette_options = {:record => :once, :allow_playback_repeats => true }
  config.hook_into :faraday
  config.allow_http_connections_when_no_cassette = true
  config.cassette_library_dir = "spec/vcr_cassettes"
  config.configure_rspec_metadata!

  config.filter_sensitive_data('<AZURE_TENANT_ID>') { ENV['AZURE_TENANT_ID'] }
  config.filter_sensitive_data('<AZURE_CLIENT_ID>') { ENV['AZURE_CLIENT_ID'] }
  config.filter_sensitive_data('<AZURE_CLIENT_SECRET>') { ENV['AZURE_CLIENT_SECRET'] }
  config.filter_sensitive_data('<AZURE_SUBSCRIPTION_ID>') { ENV['AZURE_SUBSCRIPTION_ID'] }

  config.before_record do |interaction|
    interaction.request.headers.delete('authorization')
    interaction.response.body.sub!(/\"access_token\":\".*\"}$/, '"access_token":"<ACCESS_TOKEN>"}')

    # Reduce number of interaction by ignoring 'InProgress' operations
    if interaction.request.uri =~ /^https:\/\/management.azure.com\/subscriptions\/<AZURE_SUBSCRIPTION_ID>\/operationresults\/.*/
      if interaction.response.status.code == 202
        interaction.ignore!
      end
    elsif interaction.request.uri =~ /^https:\/\/management.azure.com\/subscriptions\/<AZURE_SUBSCRIPTION_ID>\/providers\/Microsoft.Storage\/operations\/.*/ then
      if interaction.response.status.code == 202
        interaction.ignore!
      end
    end

    # Override the 'Retry-After' header before recording cassette to speed-up
    if !interaction.response.nil?
      if !interaction.response.headers['Retry-After'].nil?
        interaction.response.headers['Retry-After'] = '1'
      elsif !interaction.response.headers['retry-after'].nil?
        interaction.response.headers['retry-after'] = '1'
      end
    end
  end
end

RSpec.configure do |config|
  config.around(:each) do |example|
    options = example.metadata[:vcr] || {}
    if options[:record] == :skip
      VCR.turned_off(&example)
    else
      name = example.metadata[:description].gsub(/\s+/,'_').gsub(/\./,'/').gsub(/[^\w\/]+/, '_').gsub(/\/$/, '')
      VCR.use_cassette(name, options, &example)
    end
  end
end
