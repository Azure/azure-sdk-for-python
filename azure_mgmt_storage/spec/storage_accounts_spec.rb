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
    params = Models::StorageAccountCreateParameters.new
    params.location = @account_location
    sku = Models::Sku.new
    sku.name = @account_type
    params.sku = sku
    params.kind = Models::Kind::Storage

    result = @client.create_async(@resource_group.name, name, params).value!
    expect(result.response.status).to eq(200)
    expect(result.body).not_to be_nil
    expect(result.body).to be_a(Models::StorageAccount)
    expect(result.body.location).to eq('westus')
    expect(result.body.sku.name).to eq(sku.name)
  end

  it 'list storage accounts' do
    result = @client.list_async.value!
    expect(result.body.value).not_to be_nil
    expect(result.body.value).to be_a(Array)
  end

  it 'list storage accounts by resource group' do
    result = @client.list_by_resource_group_async(@resource_group.name).value!
    expect(result.body).not_to be_nil
    expect(result.body.value).to be_a(Array)
  end

  it 'should send true if name is available' do
    acc_name = Models::StorageAccountCheckNameAvailabilityParameters.new
    acc_name.name = 'storage4db9202c66274d529'
    acc_name.type = @storage_type

    result = @client.check_name_availability_async(acc_name).value!
    expect(result.body).not_to be_nil
    expect(result.body.name_available).to be_truthy
  end

  it 'should get storage account properties' do
    storage = create_storage_account('storage8acbcd443ca040968')

    result = @client.get_properties_async(@resource_group.name, storage).value!

    expect(result.body).not_to be_nil
    expect(result.body).to be_a(Models::StorageAccount)
    expect(result.body.location).to eq('westus')
    expect(result.body.name).to eq(storage)
    expect(result.body.type).to eq(@storage_type)
    expect(result.body.sku.name).to eq(@account_type)
  end

  it 'should regenerate storage account keys' do
    storage = create_storage_account('storagec38683a7fd6445a68')

    params = Models::StorageAccountRegenerateKeyParameters.new
    params.key_name = 'key1'

    storage_keys1 = @client.regenerate_key_async(@resource_group.name, storage, params).value!
    expect(storage_keys1.body.keys[0].value).not_to be_nil
    expect(storage_keys1.body.keys[1].value).not_to be_nil

    params.key_name = 'key2'
    storage_keys2 = @client.regenerate_key_async(@resource_group.name, storage, params).value!
    expect(storage_keys2.body.keys[0].key_name).to eq(storage_keys1.body.keys[0].key_name)
    expect(storage_keys2.body.keys[0].value).to eq(storage_keys1.body.keys[0].value)
    expect(storage_keys2.body.keys[1]).not_to eq(storage_keys1.body.keys[1])
  end

  it 'should get storage account keys' do
    storage = create_storage_account('storage8cfc02401d3d40129')

    result = @client.list_keys_async(@resource_group.name, storage).value!
    expect(result.body.keys[0]).not_to be_nil
    expect(result.body.keys[1]).not_to be_nil
  end

  it 'should update storage' do
    storage = create_storage_account('storage3b8b8f628a1c4d868')

    params = Models::StorageAccountUpdateParameters.new
    params.tags = { 'tag1' => 'val1' }

    result = @client.update_async(@resource_group.name, storage, params).value!
    expect(result.body).not_to be_nil
    expect(result.body.tags).not_to be_nil
    expect(result.body.tags['tag1']).to eq('val1')
  end

  it 'should delete storage' do
    storage = create_storage_account('storage92a0dc05385c4eef9')

    result = @client.delete_async(@resource_group.name, storage).value!
    expect(result.response.status).to eq(200)
  end

  def create_storage_account(acc_name)
    name = acc_name

    params = Models::StorageAccountCreateParameters.new
    sku = Models::Sku.new
    sku.name = @account_type

    params.location = @account_location
    params.sku = sku
    params.kind = Models::Kind::Storage

    @client.create(@resource_group.name, name, params)

    name
  end
end
