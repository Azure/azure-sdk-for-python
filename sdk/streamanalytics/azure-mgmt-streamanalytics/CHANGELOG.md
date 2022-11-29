# Release History

## 2.0.0b1 (2022-11-11)

### Features Added

  - Added operation SubscriptionsOperations.begin_sample_input
  - Added operation SubscriptionsOperations.begin_test_input
  - Added operation SubscriptionsOperations.begin_test_output
  - Added operation SubscriptionsOperations.begin_test_query
  - Added operation SubscriptionsOperations.compile_query
  - Added operation group SkuOperations
  - Model AzureSqlReferenceInputDataSource has a new parameter authentication_mode
  - Model AzureSynapseDataSourceProperties has a new parameter authentication_mode
  - Model AzureSynapseOutputDataSource has a new parameter authentication_mode
  - Model AzureSynapseOutputDataSourceProperties has a new parameter authentication_mode
  - Model BlobDataSourceProperties has a new parameter authentication_mode
  - Model BlobOutputDataSource has a new parameter blob_path_prefix
  - Model BlobOutputDataSource has a new parameter blob_write_mode
  - Model BlobOutputDataSourceProperties has a new parameter blob_path_prefix
  - Model BlobOutputDataSourceProperties has a new parameter blob_write_mode
  - Model BlobReferenceInputDataSource has a new parameter authentication_mode
  - Model BlobReferenceInputDataSource has a new parameter blob_name
  - Model BlobReferenceInputDataSource has a new parameter delta_path_pattern
  - Model BlobReferenceInputDataSource has a new parameter delta_snapshot_refresh_rate
  - Model BlobReferenceInputDataSource has a new parameter full_snapshot_refresh_rate
  - Model BlobReferenceInputDataSource has a new parameter source_partition_count
  - Model BlobReferenceInputDataSourceProperties has a new parameter authentication_mode
  - Model BlobReferenceInputDataSourceProperties has a new parameter blob_name
  - Model BlobReferenceInputDataSourceProperties has a new parameter delta_path_pattern
  - Model BlobReferenceInputDataSourceProperties has a new parameter delta_snapshot_refresh_rate
  - Model BlobReferenceInputDataSourceProperties has a new parameter full_snapshot_refresh_rate
  - Model BlobReferenceInputDataSourceProperties has a new parameter source_partition_count
  - Model BlobStreamInputDataSource has a new parameter authentication_mode
  - Model BlobStreamInputDataSourceProperties has a new parameter authentication_mode
  - Model Cluster has a new parameter properties
  - Model DocumentDbOutputDataSource has a new parameter authentication_mode
  - Model EventHubDataSourceProperties has a new parameter partition_count
  - Model EventHubOutputDataSource has a new parameter partition_count
  - Model EventHubOutputDataSourceProperties has a new parameter partition_count
  - Model EventHubStreamInputDataSource has a new parameter partition_count
  - Model EventHubStreamInputDataSource has a new parameter prefetch_count
  - Model EventHubStreamInputDataSourceProperties has a new parameter partition_count
  - Model EventHubStreamInputDataSourceProperties has a new parameter prefetch_count
  - Model EventHubV2OutputDataSource has a new parameter partition_count
  - Model EventHubV2StreamInputDataSource has a new parameter partition_count
  - Model EventHubV2StreamInputDataSource has a new parameter prefetch_count
  - Model FunctionProperties has a new parameter binding
  - Model FunctionProperties has a new parameter inputs
  - Model FunctionProperties has a new parameter output
  - Model Identity has a new parameter user_assigned_identities
  - Model InputProperties has a new parameter watermark_settings
  - Model Output has a new parameter last_output_event_timestamps
  - Model Output has a new parameter watermark_settings
  - Model PrivateEndpoint has a new parameter properties
  - Model ReferenceInputProperties has a new parameter watermark_settings
  - Model Sku has a new parameter capacity
  - Model StorageAccount has a new parameter authentication_mode
  - Model StreamInputProperties has a new parameter watermark_settings
  - Model StreamingJob has a new parameter externals
  - Model StreamingJob has a new parameter sku_properties_sku

### Breaking Changes

  - Model AzureSqlReferenceInputDataSource no longer has parameter table
  - Model Cluster no longer has parameter capacity_allocated
  - Model Cluster no longer has parameter capacity_assigned
  - Model Cluster no longer has parameter cluster_id
  - Model Cluster no longer has parameter created_date
  - Model Cluster no longer has parameter provisioning_state
  - Model PrivateEndpoint no longer has parameter created_date
  - Model PrivateEndpoint no longer has parameter manual_private_link_service_connections

## 1.0.0 (2022-01-06)

**Features**

  - Added operation StreamingJobsOperations.begin_scale
  - Model AzureSqlReferenceInputDataSource has a new parameter database
  - Model AzureSqlReferenceInputDataSource has a new parameter delta_snapshot_query
  - Model AzureSqlReferenceInputDataSource has a new parameter full_snapshot_query
  - Model AzureSqlReferenceInputDataSource has a new parameter password
  - Model AzureSqlReferenceInputDataSource has a new parameter refresh_rate
  - Model AzureSqlReferenceInputDataSource has a new parameter refresh_type
  - Model AzureSqlReferenceInputDataSource has a new parameter server
  - Model AzureSqlReferenceInputDataSource has a new parameter table
  - Model AzureSqlReferenceInputDataSource has a new parameter user
  - Model Cluster has a new parameter capacity_allocated
  - Model Cluster has a new parameter capacity_assigned
  - Model Cluster has a new parameter cluster_id
  - Model Cluster has a new parameter created_date
  - Model Cluster has a new parameter provisioning_state
  - Model Operation has a new parameter is_data_action
  - Model PrivateEndpoint has a new parameter created_date
  - Model PrivateEndpoint has a new parameter manual_private_link_service_connections
  - Model Transformation has a new parameter valid_streaming_units

**Breaking changes**

  - Model AzureSqlReferenceInputDataSource no longer has parameter properties
  - Model Cluster no longer has parameter properties
  - Model FunctionProperties no longer has parameter binding
  - Model FunctionProperties no longer has parameter inputs
  - Model FunctionProperties no longer has parameter output
  - Model PrivateEndpoint no longer has parameter properties
  - Model StreamingJob no longer has parameter externals

## 1.0.0rc1 (2020-09-18)

  - Initial Release
