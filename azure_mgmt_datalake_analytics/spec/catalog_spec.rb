# encoding: utf-8
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.

require_relative 'spec_helper'

include MsRestAzure
include Azure::ARM::Resources
include Azure::ARM::DataLakeAnalytics

describe 'DataLakeAnalyticsClient Catalog' do
  before(:each) do
    @resource_helper = ResourceHelper.new
    @resource_group = @resource_helper.create_resource_group
    @dl_store_acc = @resource_helper.create_datalake_store_account('dlstoreacc')
    @dl_analysis_acc = @resource_helper.create_datalake_analysis_account('dlanalyticsacc', 'dlstoreacc')
    @client = @resource_helper.dla_cat_client.catalog
  end

  after(:each) do
    @resource_helper.delete_resource_group(@resource_group.name)
  end

  it 'should get catalog default database' do
    u_sql_database = @client.get_database(@dl_analysis_acc.name, 'master')
    expect(u_sql_database).to be_an_instance_of(Catalog::Models::USqlDatabase)
    expect(u_sql_database.name).to eq('master')
  end
end