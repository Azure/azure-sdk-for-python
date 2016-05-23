# encoding: utf-8
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.

require_relative 'spec_helper'

include MsRestAzure
include Azure::ARM::Resources

describe 'Tags' do
  let(:tag_name) { 'testtagname' }
  let(:tag_value) { 'testtagvalue' }

  before(:each) do
    @resource_help = ResourceHelper.new()
    @client = @resource_help.resource_client.tags
    @tag = @client.create_or_update_async(tag_name).value!
  end

  after(:each) do
    result = @client.delete_async(tag_name).value!
    expect(result.response.status).to eq(200)
  end

  it 'should create and delete tag' do
    result = @tag

    expect(result.body).not_to be_nil
    expect(result.body.id).not_to be_nil
    expect(result.body.tag_name).to eq(tag_name)
    expect(result.body.values).to be_a(Array)
    expect(result.body.count).to be_a(Models::TagCount)
  end

  it 'should create and delete tag with value' do
    tag = @tag.body
    result = @client.create_or_update_value_async(tag.tag_name, tag_value).value!

    expect(result.body).not_to be_nil
    expect(result.body.id).not_to be_nil
    expect(result.body.tag_value).to eq(tag_value)
    expect(result.body.count).to be_a(Models::TagCount)

    result = @client.delete_value_async(tag.tag_name, tag_value).value!
    expect(result.response.status).to eq(200)
  end

  it 'should list tags' do
    result = @client.list_async().value!
    expect(result.body.value).not_to be_nil
    expect(result.body.value).to be_a(Array)

    while !result.body.next_link.nil? && !result.body.next_link.empty?  do
      result = @client.list_next(result.body.next_link).value!
      expect(result.body.value).not_to be_nil
      expect(result.body.value).to be_a(Array)
    end
  end
end

describe 'Tag raises' do
  before(:each) do
    @resource_help = ResourceHelper.new()
    @client = @resource_help.resource_client.tags
  end

  it 'an exception creating value for not existing tag' do
    tag_name = 'unknown_tag_name'
    tag_value = 'unknown_tag_value'
    expect {@client.create_or_update_value(tag_name, tag_value).value!}.to raise_error(MsRestAzure::AzureOperationError)
  end
end
