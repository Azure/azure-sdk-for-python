# encoding: utf-8
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.

require_relative 'spec_helper'

include MsRestAzure
include Azure::ARM::Resources
include Azure::ARM::DataLakeStore

describe 'DataLakeStoreClient File System' do
  before(:each) do
    @resource_helper = ResourceHelper.new
    @resource_group = @resource_helper.create_resource_group
    @client = @resource_helper.dls_fs_client.file_system

    @datalake_acc_name = 'dlsacc'
    acc = Account::Models::DataLakeStoreAccount.new
    acc.name = @datalake_acc_name
    acc.location = 'East US 2'
    result = @resource_helper.dls_acc_client.account.create_async(@resource_group.name, @datalake_acc_name, acc).value!
    expect(result.body).to be_an_instance_of(Account::Models::DataLakeStoreAccount)
    expect(result.body.name).to eq(@datalake_acc_name)
  end

  after(:each) do
    @resource_helper.delete_resource_group(@resource_group.name)
  end

  it 'should work with file operations' do
    # Create directory
    result = @client.mkdirs(@datalake_acc_name, 'foldername')
    expect(result).to be_an_instance_of(FileSystem::Models::FileOperationResult)
    expect(result.operation_result).to be_truthy

    # Get directory
    result = @client.get_file_status(@datalake_acc_name, 'foldername')
    expect(result).to be_an_instance_of(FileSystem::Models::FileStatusResult)
    expect(result.file_status.type).to eq(FileSystem::Models::FileType::DIRECTORY)
    expect(result.file_status.length).to eq(0)

    # Create empty file inside directory
    result = @client.create_async(@datalake_acc_name, 'foldername/emptyfile.txt').value!
    expect(result.response.status).to eq(201)

    # Get file inside directory
    result = @client.get_file_status(@datalake_acc_name, 'foldername/emptyfile.txt')
    expect(result).to be_an_instance_of(FileSystem::Models::FileStatusResult)
    expect(result.file_status.type).to eq(FileSystem::Models::FileType::FILE)
    expect(result.file_status.length).to eq(0)

    # Create non-empty file inside directory
    result = @client.create_async(@datalake_acc_name, 'foldername/nonemptyfile.txt', 'Hello World!').value!
    expect(result.response.status).to eq(201)

    # Get non-empty file inside directory
    result = @client.get_file_status(@datalake_acc_name, 'foldername/nonemptyfile.txt')
    expect(result).to be_an_instance_of(FileSystem::Models::FileStatusResult)
    expect(result.file_status.type).to eq(FileSystem::Models::FileType::FILE)
    expect(result.file_status.length).to eq(14)

    # Delete folder
    result = @client.delete(@datalake_acc_name, 'foldername', true)
    expect(result).to be_an_instance_of(FileSystem::Models::FileOperationResult)
    expect(result.operation_result).to be_truthy
  end
end
