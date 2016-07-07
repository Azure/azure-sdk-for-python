# encoding: utf-8
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.

require_relative 'spec_helper'

include MsRestAzure
include Azure::ARM::Resources

describe 'Providers' do

  before(:each) do
    @registered_providers = []
    @unregistered_providers = []
    @resource_helper = ResourceHelper.new()
    @client = @resource_helper.resource_client.providers
  end

  after(:each) do
    @registered_providers.each do |namespace|
      begin
        @client.unregister(namespace).value!
      rescue Exception
      end
    end

    @unregistered_providers.each do |namespace|
      begin
        @client.register(namespace).value!
      rescue Exception
      end
    end
  end

  it 'should list providers' do
    result = @client.list_async().value!
    expect(result.body.value).not_to be_nil
    expect(result.body.value).to be_a(Array)

    while !result.body.next_link.nil? && !result.body.next_link.empty?  do
      result = @client.list_next_async(result.body.next_link).value!
      expect(result.body.value).not_to be_nil
      expect(result.body.value).to be_a(Array)
    end
  end

  it 'should list providers with top restriction parameter' do
    result = @client.list_async(1).value!
    expect(result.body.value).not_to be_nil
    expect(result.body.value).to be_a(Array)

    while !result.body.next_link.nil? && !result.body.next_link.empty?  do
      result = @client.list_next(result.body.next_link).value!
      expect(result.body.value).not_to be_nil
      expect(result.body.value).to be_a(Array)
    end
  end

  it 'should register provider' do
    providers = @client.list_async().value!.body.value
    targetProvider = providers.detect do |item|
      item.registration_state == 'NotRegistered' || item.registration_state == 'Unregistered'
    end
    @registered_providers.push(targetProvider.namespace)

    result = @client.register_async(targetProvider.namespace).value!

    expect(result.response.status).to eq(200)
    expect(result.body.namespace).to eq(targetProvider.namespace)
    expect(result.body.registration_state).not_to eq('NotRegistered')
  end

  it 'should raise an error when attempting register provider with nil parameter' do
    expect{@client.register(nil)}.to raise_error(ArgumentError)
  end

  it 'should unregister provider' do
    providers = @client.list_async().value!.body.value
    targetProvider = providers.detect {|item| item.registration_state == 'Registered' }
    @unregistered_providers.push(targetProvider.namespace)

    result = @client.unregister_async(targetProvider.namespace).value!

    expect(result.response.status).to eq(200)
    expect(result.body.namespace).to eq(targetProvider.namespace)
    expect(result.body.registration_state).not_to eq('Registered')
  end

  it 'should raise an error when attempting unregister provider with nil parameter' do
    expect{@client.unregister(nil)}.to raise_error(ArgumentError)
  end

  it 'should get provider' do
    providers = @client.list_async().value!.body.value

    result = @client.get_async(providers[0].namespace).value!

    expect(result.body).not_to be_nil
    expect(result.body.namespace).to eq(providers[0].namespace)
  end

  it 'should raise error when attempting get provider with nil parameter' do
    expect{@client.get(nil)}.to raise_error(ArgumentError)
  end

end
