# encoding: utf-8
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.

require_relative 'spec_helper'

include MsRestAzure
include Azure::ARM::Storage

describe StorageAccounts do

  before(:each) do
    @resource_helper = ResourceHelper.new
    @storage_client = @resource_helper.storage_client
    @resource_client = @resource_helper.resource_client
    @client = @storage_client.storage_accounts
    @resource_group = @resource_helper.create_resource_group
    @storage_type = 'Microsoft.Storage/storageAccounts'
    @account_type = 'Standard_LRS'
    @account_location = 'westus'
  end

  after(:each) do
    @resource_helper.delete_resource_group(@resource_group.name)
  end

  it 'create storage account' do
    name = 'storage56e236d65ef043378'
    props = Models::StorageAccountPropertiesCreateParameters.new
    props.account_type = @account_type

    params = Models::StorageAccountCreateParameters.new
    params.properties = props
    params.location = @account_location

    result = @client.create(@resource_group.name, name, params).value!
    expect(result.response.status).to eq(200)
    expect(result.body).not_to be_nil
    expect(result.body.location).to eq('westus')
    expect(result.body.properties).to be_a(Models::StorageAccountProperties)
    expect(result.body.properties.account_type).to eq(props.account_type)
  end

  it 'list storage accounts' do
    result = @client.list.value!
    expect(result.body.value).not_to be_nil
    expect(result.body.value).to be_a(Array)
  end

  it 'list storage accounts by resource group' do
    result = @client.list_by_resource_group(@resource_group.name).value!
    expect(result.body).not_to be_nil
    expect(result.body.value).to be_a(Array)
  end

  it 'should send true if name is available' do
    acc_name = Models::StorageAccountCheckNameAvailabilityParameters.new
    acc_name.name = 'storage4db9202c66274d529'
    acc_name.type = @storage_type

    result = @client.check_name_availability(acc_name).value!
    expect(result.body).not_to be_nil
    expect(result.body.name_available).to be_truthy
  end

  it 'should get storage account properties' do
    storage = create_storage_account('storage8acbcd443ca040968')

    result = @client.get_properties(@resource_group.name, storage).value!

    expect(result.body).not_to be_nil
    expect(result.body.location).to eq('westus')
    expect(result.body.name).to eq(storage)
    expect(result.body.type).to eq(@storage_type)
    expect(result.body.properties).to be_a(Models::StorageAccountProperties)
    expect(result.body.properties.account_type).to eq(@account_type)
  end

  it 'should regenerate storage account keys' do
    storage = create_storage_account('storagec38683a7fd6445a68')

    params = Models::StorageAccountRegenerateKeyParameters.new
    params.key_name = 'key1'

    storage_keys1 = @client.regenerate_key(@resource_group.name, storage, params).value!
    expect(storage_keys1.body.key1).not_to be_nil
    expect(storage_keys1.body.key2).not_to be_nil

    params.key_name = 'key2'
    storage_keys2 = @client.regenerate_key(@resource_group.name, storage, params).value!
    expect(storage_keys2.body.key1).to eq(storage_keys1.body.key1)
    expect(storage_keys2.body.key2).not_to eq(storage_keys1.body.key2)
  end

  it 'should get storage account keys' do
    storage = create_storage_account('storage8cfc02401d3d40129')

    result = @client.list_keys(@resource_group.name, storage).value!
    expect(result.body.key1).not_to be_nil
    expect(result.body.key2).not_to be_nil
  end

  it 'should update storage' do
    storage = create_storage_account('storage3b8b8f628a1c4d868')

    params = Models::StorageAccountUpdateParameters.new
    params.tags = { 'tag1' => 'val1' }

    result = @client.update(@resource_group.name, storage, params).value!
    expect(result.body).not_to be_nil
    expect(result.body.tags).not_to be_nil
    expect(result.body.tags['tag1']).to eq('val1')
  end

  it 'should delete storage' do
    storage = create_storage_account('storage92a0dc05385c4eef9')

    result = @client.delete(@resource_group.name, storage).value!
    expect(result.response.status).to eq(200)
  end

  def create_storage_account(acc_name)
    name = acc_name

    props = Models::StorageAccountPropertiesCreateParameters.new
    props.account_type = @account_type

    params = Models::StorageAccountCreateParameters.new
    params.properties = props
    params.location = @account_location

    @client.create(@resource_group.name, name, params).value!.body

    name
  end
end
