# encoding: utf-8
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.

require_relative 'spec_helper'

include MsRestAzure
include Azure::ARM::Resources
include Azure::ARM::DataLakeAnalytics

describe 'DataLakeAnalyticsClient Job' do
  before(:each) do
    @resource_helper = ResourceHelper.new
    @resource_group = @resource_helper.create_resource_group
    @dl_store_acc = @resource_helper.create_datalake_store_account('dlstoreacc')
    @dl_analysis_acc = @resource_helper.create_datalake_analysis_account('dlanalyticsacc', 'dlstoreacc')
    @client = @resource_helper.dla_job_client.job
  end

  after(:each) do
    @resource_helper.delete_resource_group(@resource_group.name)
  end

  it 'should create job' do
    job_info = Job::Models::JobInformation.new
    job_info.job_id = '68ef6b80-ec33-4c7e-b204-1e6a77e504a7'
    job_info.name = 'testjob'
    job_info.type = Job::Models::JobType::USql
    prop = Job::Models::JobProperties.new
    prop.type = Job::Models::JobType::USql
    prop.script = 'DROP DATABASE IF EXISTS FOO; CREATE DATABASE FOO; DROP DATABASE IF EXISTS FOO;'
    job_info.properties = prop

    current_job_info = @client.create(@dl_analysis_acc.name, job_info.job_id, job_info)
    expect(current_job_info).to be_an_instance_of(Job::Models::JobInformation)
    expect(current_job_info.job_id).to eq('68ef6b80-ec33-4c7e-b204-1e6a77e504a7')
  end
end