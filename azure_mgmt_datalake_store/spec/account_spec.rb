# encoding: utf-8
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.

require_relative 'spec_helper'

include MsRestAzure
include Azure::ARM::Resources
include Azure::ARM::DataLakeStore::Account

describe 'DataLakeStoreClient Account' do
  before(:each) do
    @resource_helper = ResourceHelper.new
    @resource_group = @resource_helper.create_resource_group
    @client = @resource_helper.dls_acc_client.account

    @datalake_acc_name = 'dlsacc'
  end

  after(:each) do
    @resource_helper.delete_resource_group(@resource_group.name)
  end

  it 'should create update and delete account' do
    # Create
    acc = Models::DataLakeStoreAccount.new
    acc.name = @datalake_acc_name
    acc.location = 'East US 2'
    acc.tags = {
        :testtag1 => :testtag1,
        :testtag2 => :testtag2,
    }
    result = @client.create(@resource_group.name, @datalake_acc_name, acc)
    expect(result).to be_an_instance_of(Models::DataLakeStoreAccount)
    expect(result.name).to eq(@datalake_acc_name)
    expect(result.tags.count).to eq(2)

    # Update
    acc.tags = {
        :testtag1 => :testtag1,
        :testtag2 => :testtag2,
        :testtag3 => :testtag3,
    }
    result = @client.update(@resource_group.name, @datalake_acc_name, acc)
    expect(result).to be_an_instance_of(Models::DataLakeStoreAccount)
    expect(result.name).to eq(@datalake_acc_name)
    expect(result.tags.count).to eq(3)

    # Delete
    result = @client.delete_async(@resource_group.name, @datalake_acc_name).value!
    expect(result.response.status).to eq(200)
  end
end
