# Release History

## 1.0.0rc1 (2021-12-23)

**Features**

  - Model Operation has a new parameter is_data_action
  - Model Transformation has a new parameter valid_streaming_units
  - Model AzureSqlReferenceInputDataSource has a new parameter refresh_type
  - Model AzureSqlReferenceInputDataSource has a new parameter database
  - Model AzureSqlReferenceInputDataSource has a new parameter refresh_rate
  - Model AzureSqlReferenceInputDataSource has a new parameter full_snapshot_query
  - Model AzureSqlReferenceInputDataSource has a new parameter delta_snapshot_query
  - Model AzureSqlReferenceInputDataSource has a new parameter table
  - Model AzureSqlReferenceInputDataSource has a new parameter server
  - Model AzureSqlReferenceInputDataSource has a new parameter user
  - Model AzureSqlReferenceInputDataSource has a new parameter password
  - Model PrivateEndpoint has a new parameter created_date
  - Model PrivateEndpoint has a new parameter manual_private_link_service_connections
  - Model Cluster has a new parameter provisioning_state
  - Model Cluster has a new parameter cluster_id
  - Model Cluster has a new parameter capacity_allocated
  - Model Cluster has a new parameter capacity_assigned
  - Model Cluster has a new parameter created_date
  - Added operation StreamingJobsOperations.begin_scale

**Breaking changes**

  - Model StreamingJob no longer has parameter externals
  - Model AzureSqlReferenceInputDataSource no longer has parameter properties
  - Model PrivateEndpoint no longer has parameter properties
  - Model FunctionProperties no longer has parameter inputs
  - Model FunctionProperties no longer has parameter binding
  - Model FunctionProperties no longer has parameter output
  - Model Cluster no longer has parameter properties

## 1.0.0rc1 (2020-09-18)

  - Initial Release
