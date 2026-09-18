# Release History

## 10.0.0b1 (2026-05-28)

### Features Added

  - Client `DataFactoryManagementClient` added method `send_request`
  - Model `ChangeDataCaptureResource` added property `system_data`
  - Model `CredentialResource` added property `system_data`
  - Model `DataFlowResource` added property `system_data`
  - Model `DatasetResource` added property `system_data`
  - Model `Factory` added property `system_data`
  - Model `GlobalParameterResource` added property `system_data`
  - Model `IntegrationRuntimeResource` added property `system_data`
  - Model `LinkedServiceResource` added property `system_data`
  - Model `ManagedPrivateEndpointResource` added property `system_data`
  - Model `ManagedVirtualNetworkResource` added property `system_data`
  - Model `PipelineResource` added property `system_data`
  - Model `PrivateEndpointConnectionResource` added property `system_data`
  - Model `TriggerResource` added property `system_data`
  - Added enum `CreatedByType`
  - Added model `ProxyResource`

### Breaking Changes

  - This version introduces new hybrid models which have dual dictionary and model nature. Please follow https://aka.ms/azsdk/python/migrate/hybrid-models for migration.
  - For the method breakings, please refer to https://aka.ms/azsdk/python/migrate/operations for migration.
  - Model `AmazonMWSLinkedService` moved instance variable `endpoint`, `marketplace_id`, `seller_id`, `mws_auth_token`, `access_key_id`, `secret_key`, `use_encrypted_endpoints`, `use_host_verification`, `use_peer_verification` and `encrypted_credential` under property `type_properties` whose type is `AmazonMWSLinkedServiceTypeProperties`
  - Model `AmazonMWSObjectDataset` moved instance variable `table_name` under property `type_properties` whose type is `GenericDatasetTypeProperties`
  - Model `AmazonRdsForOracleLinkedService` moved instance variable `connection_string`, `server`, `authentication_type`, `username`, `password`, `encryption_client`, `encryption_types_client`, `crypto_checksum_client`, `crypto_checksum_types_client`, `initial_lob_fetch_size`, `fetch_size`, `statement_cache_size`, `initialization_string`, `enable_bulk_load`, `support_v1_data_types`, `fetch_tswtz_as_timestamp` and `encrypted_credential` under property `type_properties` whose type is `AmazonRdsForLinkedServiceTypeProperties`
  - Model `AmazonRdsForOracleTableDataset` moved instance variable `schema_type_properties_schema` and `table` under property `type_properties` whose type is `AmazonRdsForOracleTableDatasetTypeProperties`
  - Model `AmazonRdsForSqlServerLinkedService` moved instance variable `server`, `database`, `encrypt`, `trust_server_certificate`, `host_name_in_certificate`, `application_intent`, `connect_timeout`, `connect_retry_count`, `connect_retry_interval`, `load_balance_timeout`, `command_timeout`, `integrated_security`, `failover_partner`, `max_pool_size`, `min_pool_size`, `multiple_active_result_sets`, `multi_subnet_failover`, `packet_size`, `pooling`, `connection_string`, `authentication_type`, `user_name`, `password`, `encrypted_credential` and `always_encrypted_settings` under property `type_properties` whose type is `AmazonRdsForSqlServerLinkedServiceTypeProperties`
  - Model `AmazonRdsForSqlServerTableDataset` moved instance variable `schema_type_properties_schema` and `table` under property `type_properties` whose type is `AmazonRdsForSqlServerTableDatasetTypeProperties`
  - Model `AmazonRedshiftLinkedService` moved instance variable `server`, `username`, `password`, `database`, `port` and `encrypted_credential` under property `type_properties` whose type is `AmazonRedshiftLinkedServiceTypeProperties`
  - Model `AmazonRedshiftTableDataset` moved instance variable `table_name`, `table` and `schema_type_properties_schema` under property `type_properties` whose type is `AmazonRedshiftTableDatasetTypeProperties`
  - Model `AmazonS3CompatibleLinkedService` moved instance variable `access_key_id`, `secret_access_key`, `service_url`, `force_path_style` and `encrypted_credential` under property `type_properties` whose type is `AmazonS3CompatibleLinkedServiceTypeProperties`
  - Model `AmazonS3Dataset` moved instance variable `bucket_name`, `key`, `prefix`, `version`, `modified_datetime_start`, `modified_datetime_end`, `format` and `compression` under property `type_properties` whose type is `AmazonS3DatasetTypeProperties`
  - Model `AmazonS3LinkedService` moved instance variable `authentication_type`, `access_key_id`, `secret_access_key`, `service_url`, `session_token` and `encrypted_credential` under property `type_properties` whose type is `AmazonS3LinkedServiceTypeProperties`
  - Model `AppFiguresLinkedService` moved instance variable `user_name`, `password` and `client_key` under property `type_properties` whose type is `AppFiguresLinkedServiceTypeProperties`
  - Model `AppendVariableActivity` moved instance variable `variable_name` and `value` under property `type_properties` whose type is `AppendVariableActivityTypeProperties`
  - Model `AsanaLinkedService` moved instance variable `api_token` and `encrypted_credential` under property `type_properties` whose type is `AsanaLinkedServiceTypeProperties`
  - Model `AvroDataset` moved instance variable `location`, `avro_compression_codec` and `avro_compression_level` under property `type_properties` whose type is `AvroDatasetTypeProperties`
  - Model `AzPowerShellSetup` moved instance variable `version` under property `type_properties` whose type is `AzPowerShellSetupTypeProperties`
  - Model `AzureBatchLinkedService` moved instance variable `account_name`, `access_key`, `batch_uri`, `pool_name`, `linked_service_name`, `encrypted_credential` and `credential` under property `type_properties` whose type is `AzureBatchLinkedServiceTypeProperties`
  - Model `AzureBlobDataset` moved instance variable `folder_path`, `table_root_location`, `file_name`, `modified_datetime_start`, `modified_datetime_end`, `format` and `compression` under property `type_properties` whose type is `AzureBlobDatasetTypeProperties`
  - Model `AzureBlobFSDataset` moved instance variable `folder_path`, `file_name`, `format` and `compression` under property `type_properties` whose type is `AzureBlobFSDatasetTypeProperties`
  - Model `AzureBlobFSLinkedService` moved instance variable `url`, `account_key`, `service_principal_id`, `service_principal_key`, `tenant`, `azure_cloud_type`, `encrypted_credential`, `credential`, `service_principal_credential_type`, `service_principal_credential`, `sas_uri` and `sas_token` under property `type_properties` whose type is `AzureBlobFSLinkedServiceTypeProperties`
  - Model `AzureBlobStorageLinkedService` moved instance variable `connection_string`, `account_key`, `sas_uri`, `sas_token`, `service_endpoint`, `service_principal_id`, `service_principal_key`, `tenant`, `azure_cloud_type`, `account_kind`, `encrypted_credential`, `credential`, `authentication_type` and `container_uri` under property `type_properties` whose type is `AzureBlobStorageLinkedServiceTypeProperties`
  - Model `AzureDataExplorerCommandActivity` moved instance variable `command` and `command_timeout` under property `type_properties` whose type is `AzureDataExplorerCommandActivityTypeProperties`
  - Model `AzureDataExplorerLinkedService` moved instance variable `endpoint`, `service_principal_id`, `service_principal_key`, `database`, `tenant` and `credential` under property `type_properties` whose type is `AzureDataExplorerLinkedServiceTypeProperties`
  - Model `AzureDataExplorerTableDataset` moved instance variable `table` under property `type_properties` whose type is `AzureDataExplorerDatasetTypeProperties`
  - Model `AzureDataLakeAnalyticsLinkedService` moved instance variable `account_name`, `service_principal_id`, `service_principal_key`, `tenant`, `subscription_id`, `resource_group_name`, `data_lake_analytics_uri` and `encrypted_credential` under property `type_properties` whose type is `AzureDataLakeAnalyticsLinkedServiceTypeProperties`
  - Model `AzureDataLakeStoreDataset` moved instance variable `folder_path`, `file_name`, `format` and `compression` under property `type_properties` whose type is `AzureDataLakeStoreDatasetTypeProperties`
  - Model `AzureDataLakeStoreLinkedService` moved instance variable `data_lake_store_uri`, `service_principal_id`, `service_principal_key`, `tenant`, `azure_cloud_type`, `account_name`, `subscription_id`, `resource_group_name`, `encrypted_credential` and `credential` under property `type_properties` whose type is `AzureDataLakeStoreLinkedServiceTypeProperties`
  - Model `AzureDatabricksDeltaLakeDataset` moved instance variable `table` and `database` under property `type_properties` whose type is `AzureDatabricksDeltaLakeDatasetTypeProperties`
  - Model `AzureDatabricksDeltaLakeLinkedService` moved instance variable `domain`, `access_token`, `cluster_id`, `encrypted_credential`, `credential` and `workspace_resource_id` under property `type_properties` whose type is `AzureDatabricksDetltaLakeLinkedServiceTypeProperties`
  - Model `AzureDatabricksLinkedService` moved instance variable `domain`, `access_token`, `authentication`, `workspace_resource_id`, `existing_cluster_id`, `instance_pool_id`, `new_cluster_version`, `new_cluster_num_of_worker`, `new_cluster_node_type`, `new_cluster_spark_conf`, `new_cluster_spark_env_vars`, `new_cluster_custom_tags`, `new_cluster_log_destination`, `new_cluster_driver_node_type`, `new_cluster_init_scripts`, `new_cluster_enable_elastic_disk`, `encrypted_credential`, `policy_id`, `credential` and `data_security_mode` under property `type_properties` whose type is `AzureDatabricksLinkedServiceTypeProperties`
  - Model `AzureFileStorageLinkedService` moved instance variable `host`, `user_id`, `password`, `connection_string`, `account_key`, `sas_uri`, `sas_token`, `file_share`, `snapshot`, `encrypted_credential`, `service_endpoint` and `credential` under property `type_properties` whose type is `AzureFileStorageLinkedServiceTypeProperties`
  - Model `AzureFunctionActivity` moved instance variable `method`, `function_name`, `headers` and `body` under property `type_properties` whose type is `AzureFunctionActivityTypeProperties`
  - Model `AzureFunctionLinkedService` moved instance variable `function_app_url`, `function_key`, `encrypted_credential`, `credential`, `resource_id` and `authentication` under property `type_properties` whose type is `AzureFunctionLinkedServiceTypeProperties`
  - Model `AzureKeyVaultLinkedService` moved instance variable `base_url` and `credential` under property `type_properties` whose type is `AzureKeyVaultLinkedServiceTypeProperties`
  - Model `AzureMLBatchExecutionActivity` moved instance variable `global_parameters`, `web_service_outputs` and `web_service_inputs` under property `type_properties` whose type is `AzureMLBatchExecutionActivityTypeProperties`
  - Model `AzureMLExecutePipelineActivity` moved instance variable `ml_pipeline_id`, `ml_pipeline_endpoint_id`, `version`, `experiment_name`, `ml_pipeline_parameters`, `data_path_assignments`, `ml_parent_run_id` and `continue_on_step_failure` under property `type_properties` whose type is `AzureMLExecutePipelineActivityTypeProperties`
  - Model `AzureMLLinkedService` moved instance variable `ml_endpoint`, `api_key`, `update_resource_endpoint`, `service_principal_id`, `service_principal_key`, `tenant`, `encrypted_credential` and `authentication` under property `type_properties` whose type is `AzureMLLinkedServiceTypeProperties`
  - Model `AzureMLServiceLinkedService` moved instance variable `subscription_id`, `resource_group_name`, `ml_workspace_name`, `authentication`, `service_principal_id`, `service_principal_key`, `tenant` and `encrypted_credential` under property `type_properties` whose type is `AzureMLServiceLinkedServiceTypeProperties`
  - Model `AzureMLUpdateResourceActivity` moved instance variable `trained_model_name`, `trained_model_linked_service_name` and `trained_model_file_path` under property `type_properties` whose type is `AzureMLUpdateResourceActivityTypeProperties`
  - Model `AzureMariaDBLinkedService` moved instance variable `connection_string`, `pwd` and `encrypted_credential` under property `type_properties` whose type is `AzureMariaDBLinkedServiceTypeProperties`
  - Model `AzureMariaDBTableDataset` moved instance variable `table_name` under property `type_properties` whose type is `GenericDatasetTypeProperties`
  - Model `AzureMySqlLinkedService` moved instance variable `connection_string`, `password` and `encrypted_credential` under property `type_properties` whose type is `AzureMySqlLinkedServiceTypeProperties`
  - Model `AzureMySqlTableDataset` moved instance variable `table_name` and `table` under property `type_properties` whose type is `AzureMySqlTableDatasetTypeProperties`
  - Model `AzurePostgreSqlLinkedService` moved instance variable `connection_string`, `server`, `port`, `username`, `database`, `ssl_mode`, `timeout`, `command_timeout`, `trust_server_certificate`, `read_buffer_size`, `timezone`, `encoding`, `password`, `encrypted_credential`, `service_principal_id`, `service_principal_key`, `service_principal_credential_type`, `service_principal_embedded_cert`, `service_principal_embedded_cert_password`, `tenant`, `azure_cloud_type` and `credential` under property `type_properties` whose type is `AzurePostgreSqlLinkedServiceTypeProperties`
  - Model `AzurePostgreSqlSinkUpsertSettings` renamed its instance variable `keys` to `keys_property`
  - Model `AzurePostgreSqlTableDataset` moved instance variable `table_name`, `table` and `schema_type_properties_schema` under property `type_properties` whose type is `AzurePostgreSqlTableDatasetTypeProperties`
  - Model `AzureSearchIndexDataset` moved instance variable `index_name` under property `type_properties` whose type is `AzureSearchIndexDatasetTypeProperties`
  - Model `AzureSearchLinkedService` moved instance variable `url`, `key` and `encrypted_credential` under property `type_properties` whose type is `AzureSearchLinkedServiceTypeProperties`
  - Model `AzureSqlDWLinkedService` moved instance variable `server`, `database`, `encrypt`, `trust_server_certificate`, `host_name_in_certificate`, `application_intent`, `connect_timeout`, `connect_retry_count`, `connect_retry_interval`, `load_balance_timeout`, `command_timeout`, `integrated_security`, `failover_partner`, `max_pool_size`, `min_pool_size`, `multiple_active_result_sets`, `multi_subnet_failover`, `packet_size`, `pooling`, `connection_string`, `authentication_type`, `user_name`, `password`, `service_principal_id`, `service_principal_key`, `service_principal_credential_type`, `service_principal_credential`, `tenant`, `azure_cloud_type`, `encrypted_credential` and `credential` under property `type_properties` whose type is `AzureSqlDWLinkedServiceTypeProperties`
  - Model `AzureSqlDWTableDataset` moved instance variable `table_name`, `schema_type_properties_schema` and `table` under property `type_properties` whose type is `AzureSqlDWTableDatasetTypeProperties`
  - Model `AzureSqlDatabaseLinkedService` moved instance variable `server`, `database`, `encrypt`, `trust_server_certificate`, `host_name_in_certificate`, `application_intent`, `connect_timeout`, `connect_retry_count`, `connect_retry_interval`, `load_balance_timeout`, `command_timeout`, `integrated_security`, `failover_partner`, `max_pool_size`, `min_pool_size`, `multiple_active_result_sets`, `multi_subnet_failover`, `packet_size`, `pooling`, `connection_string`, `authentication_type`, `user_name`, `password`, `service_principal_id`, `service_principal_key`, `service_principal_credential_type`, `service_principal_credential`, `tenant`, `azure_cloud_type`, `encrypted_credential`, `always_encrypted_settings` and `credential` under property `type_properties` whose type is `AzureSqlDatabaseLinkedServiceTypeProperties`
  - Model `AzureSqlMILinkedService` moved instance variable `server`, `database`, `encrypt`, `trust_server_certificate`, `host_name_in_certificate`, `application_intent`, `connect_timeout`, `connect_retry_count`, `connect_retry_interval`, `load_balance_timeout`, `command_timeout`, `integrated_security`, `failover_partner`, `max_pool_size`, `min_pool_size`, `multiple_active_result_sets`, `multi_subnet_failover`, `packet_size`, `pooling`, `connection_string`, `authentication_type`, `user_name`, `password`, `service_principal_id`, `service_principal_key`, `service_principal_credential_type`, `service_principal_credential`, `tenant`, `azure_cloud_type`, `encrypted_credential`, `always_encrypted_settings` and `credential` under property `type_properties` whose type is `AzureSqlMILinkedServiceTypeProperties`
  - Model `AzureSqlMITableDataset` moved instance variable `table_name`, `schema_type_properties_schema` and `table` under property `type_properties` whose type is `AzureSqlMITableDatasetTypeProperties`
  - Model `AzureSqlTableDataset` moved instance variable `table_name`, `schema_type_properties_schema` and `table` under property `type_properties` whose type is `AzureSqlTableDatasetTypeProperties`
  - Model `AzureStorageLinkedService` moved instance variable `connection_string`, `account_key`, `sas_uri`, `sas_token` and `encrypted_credential` under property `type_properties` whose type is `AzureStorageLinkedServiceTypeProperties`
  - Model `AzureSynapseArtifactsLinkedService` moved instance variable `endpoint`, `authentication` and `workspace_resource_id` under property `type_properties` whose type is `AzureSynapseArtifactsLinkedServiceTypeProperties`
  - Model `AzureTableDataset` moved instance variable `table_name` under property `type_properties` whose type is `AzureTableDatasetTypeProperties`
  - Model `AzureTableStorageLinkedService` moved instance variable `connection_string`, `account_key`, `sas_uri`, `sas_token`, `encrypted_credential`, `service_endpoint` and `credential` under property `type_properties` whose type is `AzureTableStorageLinkedServiceTypeProperties`
  - Model `BinaryDataset` moved instance variable `location` and `compression` under property `type_properties` whose type is `BinaryDatasetTypeProperties`
  - Model `BlobEventsTrigger` moved instance variable `blob_path_begins_with`, `blob_path_ends_with`, `ignore_empty_blobs`, `events` and `scope` under property `type_properties` whose type is `BlobEventsTriggerTypeProperties`
  - Model `BlobTrigger` moved instance variable `folder_path`, `max_concurrency` and `linked_service` under property `type_properties` whose type is `BlobTriggerTypeProperties`
  - Model `CassandraLinkedService` moved instance variable `host`, `authentication_type`, `port`, `username`, `password` and `encrypted_credential` under property `type_properties` whose type is `CassandraLinkedServiceTypeProperties`
  - Model `CassandraTableDataset` moved instance variable `table_name` and `keyspace` under property `type_properties` whose type is `CassandraTableDatasetTypeProperties`
  - Model `ChainingTrigger` moved instance variable `depends_on` and `run_dimension` under property `type_properties` whose type is `ChainingTriggerTypeProperties`
  - Model `ChangeDataCaptureResource` moved instance variable `folder`, `description`, `source_connections_info`, `target_connections_info`, `policy`, `allow_v_net_override` and `status` under property `properties` whose type is `ChangeDataCapture`
  - Model `CloudError` moved instance variable `code`, `message`, `target` and `details` under property `error` whose type is `CloudErrorBody`
  - Model `CmdkeySetup` moved instance variable `target_name`, `user_name` and `password` under property `type_properties` whose type is `CmdkeySetupTypeProperties`
  - Model `CommonDataServiceForAppsEntityDataset` moved instance variable `entity_name` under property `type_properties` whose type is `CommonDataServiceForAppsEntityDatasetTypeProperties`
  - Model `CommonDataServiceForAppsLinkedService` moved instance variable `deployment_type`, `host_name`, `port`, `service_uri`, `organization_name`, `authentication_type`, `domain`, `username`, `password`, `service_principal_id`, `service_principal_credential_type`, `service_principal_credential` and `encrypted_credential` under property `type_properties` whose type is `CommonDataServiceForAppsLinkedServiceTypeProperties`
  - Model `ComponentSetup` moved instance variable `component_name` and `license_key` under property `type_properties` whose type is `LicensedComponentSetupTypeProperties`
  - Model `ConcurLinkedService` moved instance variable `connection_properties`, `client_id`, `username`, `password`, `use_encrypted_endpoints`, `use_host_verification`, `use_peer_verification` and `encrypted_credential` under property `type_properties` whose type is `ConcurLinkedServiceTypeProperties`
  - Model `ConcurObjectDataset` moved instance variable `table_name` under property `type_properties` whose type is `GenericDatasetTypeProperties`
  - Model `CopyActivity` moved instance variable `source`, `sink`, `translator`, `enable_staging`, `staging_settings`, `parallel_copies`, `data_integration_units`, `enable_skip_incompatible_row`, `redirect_incompatible_row_settings`, `log_storage_settings`, `log_settings`, `preserve_rules`, `preserve`, `validate_data_consistency` and `skip_error_file` under property `type_properties` whose type is `CopyActivityTypeProperties`
  - Model `CosmosDbLinkedService` moved instance variable `connection_string`, `account_endpoint`, `database`, `account_key`, `service_principal_id`, `service_principal_credential_type`, `service_principal_credential`, `tenant`, `azure_cloud_type`, `connection_mode`, `encrypted_credential` and `credential` under property `type_properties` whose type is `CosmosDbLinkedServiceTypeProperties`
  - Model `CosmosDbMongoDbApiCollectionDataset` moved instance variable `collection` under property `type_properties` whose type is `CosmosDbMongoDbApiCollectionDatasetTypeProperties`
  - Model `CosmosDbMongoDbApiLinkedService` moved instance variable `is_server_version_above32`, `connection_string` and `database` under property `type_properties` whose type is `CosmosDbMongoDbApiLinkedServiceTypeProperties`
  - Model `CosmosDbSqlApiCollectionDataset` moved instance variable `collection_name` under property `type_properties` whose type is `CosmosDbSqlApiCollectionDatasetTypeProperties`
  - Model `CouchbaseLinkedService` moved instance variable `connection_string`, `cred_string` and `encrypted_credential` under property `type_properties` whose type is `CouchbaseLinkedServiceTypeProperties`
  - Model `CouchbaseTableDataset` moved instance variable `table_name` under property `type_properties` whose type is `GenericDatasetTypeProperties`
  - Model `CustomActivity` moved instance variable `command`, `resource_linked_service`, `folder_path`, `reference_objects`, `extended_properties`, `retention_time_in_days` and `auto_user_specification` under property `type_properties` whose type is `CustomActivityTypeProperties`
  - Model `CustomEventsTrigger` moved instance variable `subject_begins_with`, `subject_ends_with`, `events` and `scope` under property `type_properties` whose type is `CustomEventsTriggerTypeProperties`
  - Model `DataLakeAnalyticsUSQLActivity` moved instance variable `script_path`, `script_linked_service`, `degree_of_parallelism`, `priority`, `parameters`, `runtime_version` and `compilation_mode` under property `type_properties` whose type is `DataLakeAnalyticsUSQLActivityTypeProperties`
  - Model `DatabricksJobActivity` moved instance variable `job_id` and `job_parameters` under property `type_properties` whose type is `DatabricksJobActivityTypeProperties`
  - Model `DatabricksNotebookActivity` moved instance variable `notebook_path`, `base_parameters` and `libraries` under property `type_properties` whose type is `DatabricksNotebookActivityTypeProperties`
  - Model `DatabricksSparkJarActivity` moved instance variable `main_class_name`, `parameters` and `libraries` under property `type_properties` whose type is `DatabricksSparkJarActivityTypeProperties`
  - Model `DatabricksSparkPythonActivity` moved instance variable `python_file`, `parameters` and `libraries` under property `type_properties` whose type is `DatabricksSparkPythonActivityTypeProperties`
  - Model `DataworldLinkedService` moved instance variable `api_token` and `encrypted_credential` under property `type_properties` whose type is `DataworldLinkedServiceTypeProperties`
  - Model `Db2LinkedService` moved instance variable `connection_string`, `server`, `database`, `authentication_type`, `username`, `password`, `package_collection`, `certificate_common_name` and `encrypted_credential` under property `type_properties` whose type is `Db2LinkedServiceTypeProperties`
  - Model `Db2TableDataset` moved instance variable `table_name`, `schema_type_properties_schema` and `table` under property `type_properties` whose type is `Db2TableDatasetTypeProperties`
  - Model `DeleteActivity` moved instance variable `recursive`, `max_concurrent_connections`, `enable_logging`, `log_storage_settings`, `dataset` and `store_settings` under property `type_properties` whose type is `DeleteActivityTypeProperties`
  - Model `DelimitedTextDataset` moved instance variable `location`, `column_delimiter`, `row_delimiter`, `encoding_name`, `compression_codec`, `compression_level`, `quote_char`, `escape_char`, `first_row_as_header` and `null_value` under property `type_properties` whose type is `DelimitedTextDatasetTypeProperties`
  - Model `DocumentDbCollectionDataset` moved instance variable `collection_name` under property `type_properties` whose type is `DocumentDbCollectionDatasetTypeProperties`
  - Model `DrillLinkedService` moved instance variable `connection_string`, `pwd` and `encrypted_credential` under property `type_properties` whose type is `DrillLinkedServiceTypeProperties`
  - Model `DrillTableDataset` moved instance variable `table_name`, `table` and `schema_type_properties_schema` under property `type_properties` whose type is `DrillDatasetTypeProperties`
  - Model `DynamicsAXLinkedService` moved instance variable `url`, `service_principal_id`, `service_principal_key`, `tenant`, `aad_resource_id` and `encrypted_credential` under property `type_properties` whose type is `DynamicsAXLinkedServiceTypeProperties`
  - Model `DynamicsAXResourceDataset` moved instance variable `path` under property `type_properties` whose type is `DynamicsAXResourceDatasetTypeProperties`
  - Model `DynamicsCrmEntityDataset` moved instance variable `entity_name` under property `type_properties` whose type is `DynamicsCrmEntityDatasetTypeProperties`
  - Model `DynamicsCrmLinkedService` moved instance variable `deployment_type`, `host_name`, `port`, `service_uri`, `organization_name`, `authentication_type`, `domain`, `username`, `password`, `service_principal_id`, `service_principal_credential_type`, `service_principal_credential`, `credential` and `encrypted_credential` under property `type_properties` whose type is `DynamicsCrmLinkedServiceTypeProperties`
  - Model `DynamicsEntityDataset` moved instance variable `entity_name` under property `type_properties` whose type is `DynamicsEntityDatasetTypeProperties`
  - Model `DynamicsLinkedService` moved instance variable `deployment_type`, `host_name`, `port`, `service_uri`, `organization_name`, `authentication_type`, `domain`, `username`, `password`, `service_principal_id`, `service_principal_credential_type`, `service_principal_credential`, `encrypted_credential` and `credential` under property `type_properties` whose type is `DynamicsLinkedServiceTypeProperties`
  - Model `EloquaLinkedService` moved instance variable `endpoint`, `username`, `password`, `use_encrypted_endpoints`, `use_host_verification`, `use_peer_verification` and `encrypted_credential` under property `type_properties` whose type is `EloquaLinkedServiceTypeProperties`
  - Model `EloquaObjectDataset` moved instance variable `table_name` under property `type_properties` whose type is `GenericDatasetTypeProperties`
  - Model `EnvironmentVariableSetup` moved instance variable `variable_name` and `variable_value` under property `type_properties` whose type is `EnvironmentVariableSetupTypeProperties`
  - Model `ExcelDataset` moved instance variable `location`, `sheet_name`, `sheet_index`, `range`, `first_row_as_header`, `compression` and `null_value` under property `type_properties` whose type is `ExcelDatasetTypeProperties`
  - Model `ExecuteDataFlowActivity` moved instance variable `data_flow`, `staging`, `integration_runtime`, `continuation_settings`, `compute`, `trace_level`, `continue_on_error`, `run_concurrently` and `source_staging_concurrency` under property `type_properties` whose type is `ExecuteDataFlowActivityTypeProperties`
  - Model `ExecutePipelineActivity` moved instance variable `pipeline`, `parameters` and `wait_on_completion` under property `type_properties` whose type is `ExecutePipelineActivityTypeProperties`
  - Model `ExecuteSSISPackageActivity` moved instance variable `package_location`, `runtime`, `logging_level`, `environment_path`, `execution_credential`, `connect_via`, `project_parameters`, `package_parameters`, `project_connection_managers`, `package_connection_managers`, `property_overrides` and `log_location` under property `type_properties` whose type is `ExecuteSSISPackageActivityTypeProperties`
  - Model `ExecuteWranglingDataflowActivity` moved instance variable `data_flow`, `staging`, `integration_runtime`, `continuation_settings`, `compute`, `trace_level`, `continue_on_error`, `run_concurrently`, `source_staging_concurrency`, `sinks` and `queries` under property `type_properties` whose type is `ExecutePowerQueryActivityTypeProperties`
  - Model `FactoryUpdateParameters` moved instance variable `public_network_access` under property `properties` whose type is `FactoryUpdateProperties`
  - Model `FailActivity` moved instance variable `message` and `error_code` under property `type_properties` whose type is `FailActivityTypeProperties`
  - Model `FileServerLinkedService` moved instance variable `host`, `user_id`, `password` and `encrypted_credential` under property `type_properties` whose type is `FileServerLinkedServiceTypeProperties`
  - Model `FileShareDataset` moved instance variable `folder_path`, `file_name`, `modified_datetime_start`, `modified_datetime_end`, `format`, `file_filter` and `compression` under property `type_properties` whose type is `FileShareDatasetTypeProperties`
  - Model `FilterActivity` moved instance variable `items` and `condition` under property `type_properties` whose type is `FilterActivityTypeProperties`
  - Model `Flowlet` moved instance variable `sources`, `sinks`, `transformations`, `script` and `script_lines` under property `type_properties` whose type is `FlowletTypeProperties`
  - Model `ForEachActivity` moved instance variable `is_sequential`, `batch_count`, `items` and `activities` under property `type_properties` whose type is `ForEachActivityTypeProperties`
  - Model `FtpServerLinkedService` moved instance variable `host`, `port`, `authentication_type`, `user_name`, `password`, `encrypted_credential`, `enable_ssl` and `enable_server_certificate_validation` under property `type_properties` whose type is `FtpServerLinkedServiceTypeProperties`
  - Model `GetMetadataActivity` moved instance variable `dataset`, `field_list`, `store_settings` and `format_settings` under property `type_properties` whose type is `GetMetadataActivityTypeProperties`
  - Model `GoogleAdWordsLinkedService` moved instance variable `connection_properties`, `client_customer_id`, `developer_token`, `authentication_type`, `refresh_token`, `client_id`, `client_secret`, `email`, `key_file_path`, `trusted_cert_path`, `use_system_trust_store`, `private_key`, `login_customer_id`, `google_ads_api_version`, `support_legacy_data_types` and `encrypted_credential` under property `type_properties` whose type is `GoogleAdWordsLinkedServiceTypeProperties`
  - Model `GoogleAdWordsObjectDataset` moved instance variable `table_name` under property `type_properties` whose type is `GenericDatasetTypeProperties`
  - Model `GoogleBigQueryLinkedService` moved instance variable `project`, `additional_projects`, `request_google_drive_scope`, `authentication_type`, `refresh_token`, `client_id`, `client_secret`, `email`, `key_file_path`, `trusted_cert_path`, `use_system_trust_store` and `encrypted_credential` under property `type_properties` whose type is `GoogleBigQueryLinkedServiceTypeProperties`
  - Model `GoogleBigQueryObjectDataset` moved instance variable `table_name`, `table` and `dataset` under property `type_properties` whose type is `GoogleBigQueryDatasetTypeProperties`
  - Model `GoogleBigQueryV2LinkedService` moved instance variable `project_id`, `authentication_type`, `client_id`, `client_secret`, `refresh_token`, `key_file_content` and `encrypted_credential` under property `type_properties` whose type is `GoogleBigQueryV2LinkedServiceTypeProperties`
  - Model `GoogleBigQueryV2ObjectDataset` moved instance variable `table` and `dataset` under property `type_properties` whose type is `GoogleBigQueryV2DatasetTypeProperties`
  - Model `GoogleCloudStorageLinkedService` moved instance variable `access_key_id`, `secret_access_key`, `service_url` and `encrypted_credential` under property `type_properties` whose type is `GoogleCloudStorageLinkedServiceTypeProperties`
  - Model `GoogleSheetsLinkedService` moved instance variable `api_token` and `encrypted_credential` under property `type_properties` whose type is `GoogleSheetsLinkedServiceTypeProperties`
  - Model `GreenplumLinkedService` moved instance variable `connection_string`, `pwd`, `encrypted_credential`, `authentication_type`, `host`, `port`, `username`, `database`, `ssl_mode`, `connection_timeout` and `command_timeout` under property `type_properties` whose type is `GreenplumLinkedServiceTypeProperties`
  - Model `GreenplumTableDataset` moved instance variable `table_name`, `table` and `schema_type_properties_schema` under property `type_properties` whose type is `GreenplumDatasetTypeProperties`
  - Model `HBaseLinkedService` moved instance variable `host`, `port`, `http_path`, `authentication_type`, `username`, `password`, `enable_ssl`, `trusted_cert_path`, `allow_host_name_cn_mismatch`, `allow_self_signed_server_cert` and `encrypted_credential` under property `type_properties` whose type is `HBaseLinkedServiceTypeProperties`
  - Model `HBaseObjectDataset` moved instance variable `table_name` under property `type_properties` whose type is `GenericDatasetTypeProperties`
  - Model `HDInsightHiveActivity` moved instance variable `storage_linked_services`, `arguments`, `get_debug_info`, `script_path`, `script_linked_service`, `defines`, `variables` and `query_timeout` under property `type_properties` whose type is `HDInsightHiveActivityTypeProperties`
  - Model `HDInsightLinkedService` moved instance variable `cluster_uri`, `cluster_auth_type`, `user_name`, `password`, `linked_service_name`, `hcatalog_linked_service_name`, `encrypted_credential`, `is_esp_enabled`, `file_system` and `credential` under property `type_properties` whose type is `HDInsightLinkedServiceTypeProperties`
  - Model `HDInsightMapReduceActivity` moved instance variable `storage_linked_services`, `arguments`, `get_debug_info`, `class_name`, `jar_file_path`, `jar_linked_service`, `jar_libs` and `defines` under property `type_properties` whose type is `HDInsightMapReduceActivityTypeProperties`
  - Model `HDInsightOnDemandLinkedService` moved instance variable `cluster_size`, `time_to_live`, `version_type_properties_version`, `linked_service_name`, `host_subscription_id`, `service_principal_id`, `service_principal_key`, `tenant`, `cluster_resource_group`, `cluster_resource_group_auth_type`, `cluster_name_prefix`, `cluster_user_name`, `cluster_password`, `cluster_ssh_user_name`, `cluster_ssh_password`, `additional_linked_service_names`, `hcatalog_linked_service_name`, `cluster_type`, `spark_version`, `core_configuration`, `h_base_configuration`, `hdfs_configuration`, `hive_configuration`, `map_reduce_configuration`, `oozie_configuration`, `storm_configuration`, `yarn_configuration`, `encrypted_credential`, `head_node_size`, `data_node_size`, `zookeeper_node_size`, `script_actions`, `virtual_network_id`, `subnet_name` and `credential` under property `type_properties` whose type is `HDInsightOnDemandLinkedServiceTypeProperties`
  - Model `HDInsightPigActivity` moved instance variable `storage_linked_services`, `arguments`, `get_debug_info`, `script_path`, `script_linked_service` and `defines` under property `type_properties` whose type is `HDInsightPigActivityTypeProperties`
  - Model `HDInsightSparkActivity` moved instance variable `root_path`, `entry_file_path`, `arguments`, `get_debug_info`, `spark_job_linked_service`, `class_name`, `proxy_user` and `spark_config` under property `type_properties` whose type is `HDInsightSparkActivityTypeProperties`
  - Model `HDInsightStreamingActivity` moved instance variable `storage_linked_services`, `arguments`, `get_debug_info`, `mapper`, `reducer`, `input`, `output`, `file_paths`, `file_linked_service`, `combiner`, `command_environment` and `defines` under property `type_properties` whose type is `HDInsightStreamingActivityTypeProperties`
  - Model `HdfsLinkedService` moved instance variable `url`, `authentication_type`, `encrypted_credential`, `user_name` and `password` under property `type_properties` whose type is `HdfsLinkedServiceTypeProperties`
  - Model `HiveLinkedService` moved instance variable `host`, `port`, `server_type`, `thrift_transport_protocol`, `authentication_type`, `service_discovery_mode`, `zoo_keeper_name_space`, `use_native_query`, `username`, `password`, `http_path`, `enable_ssl`, `enable_server_certificate_validation`, `trusted_cert_path`, `use_system_trust_store`, `allow_host_name_cn_mismatch`, `allow_self_signed_server_cert` and `encrypted_credential` under property `type_properties` whose type is `HiveLinkedServiceTypeProperties`
  - Model `HiveObjectDataset` moved instance variable `table_name`, `table` and `schema_type_properties_schema` under property `type_properties` whose type is `HiveDatasetTypeProperties`
  - Model `HttpDataset` moved instance variable `relative_url`, `request_method`, `request_body`, `additional_headers`, `format` and `compression` under property `type_properties` whose type is `HttpDatasetTypeProperties`
  - Model `HttpLinkedService` moved instance variable `url`, `authentication_type`, `user_name`, `password`, `auth_headers`, `embedded_cert_data`, `cert_thumbprint`, `encrypted_credential` and `enable_server_certificate_validation` under property `type_properties` whose type is `HttpLinkedServiceTypeProperties`
  - Model `HubspotLinkedService` moved instance variable `client_id`, `client_secret`, `access_token`, `refresh_token`, `use_encrypted_endpoints`, `use_host_verification`, `use_peer_verification` and `encrypted_credential` under property `type_properties` whose type is `HubspotLinkedServiceTypeProperties`
  - Model `HubspotObjectDataset` moved instance variable `table_name` under property `type_properties` whose type is `GenericDatasetTypeProperties`
  - Model `IcebergDataset` moved instance variable `location` under property `type_properties` whose type is `IcebergDatasetTypeProperties`
  - Model `IfConditionActivity` moved instance variable `expression`, `if_true_activities` and `if_false_activities` under property `type_properties` whose type is `IfConditionActivityTypeProperties`
  - Model `ImpalaLinkedService` moved instance variable `host`, `port`, `authentication_type`, `username`, `password`, `thrift_transport_protocol`, `enable_ssl`, `enable_server_certificate_validation`, `trusted_cert_path`, `use_system_trust_store`, `allow_host_name_cn_mismatch`, `allow_self_signed_server_cert` and `encrypted_credential` under property `type_properties` whose type is `ImpalaLinkedServiceTypeProperties`
  - Model `ImpalaObjectDataset` moved instance variable `table_name`, `table` and `schema_type_properties_schema` under property `type_properties` whose type is `ImpalaDatasetTypeProperties`
  - Model `InformixLinkedService` moved instance variable `connection_string`, `authentication_type`, `credential`, `user_name`, `password` and `encrypted_credential` under property `type_properties` whose type is `InformixLinkedServiceTypeProperties`
  - Model `InformixTableDataset` moved instance variable `table_name` under property `type_properties` whose type is `InformixTableDatasetTypeProperties`
  - Model `JiraLinkedService` moved instance variable `host`, `port`, `username`, `password`, `use_encrypted_endpoints`, `use_host_verification`, `use_peer_verification` and `encrypted_credential` under property `type_properties` whose type is `JiraLinkedServiceTypeProperties`
  - Model `JiraObjectDataset` moved instance variable `table_name`, `schema_type_properties_schema` and `table` under property `type_properties` whose type is `JiraTableDatasetTypeProperties`
  - Model `JsonDataset` moved instance variable `location`, `encoding_name` and `compression` under property `type_properties` whose type is `JsonDatasetTypeProperties`
  - Model `LakeHouseLinkedService` moved instance variable `workspace_id`, `artifact_id`, `authentication_type`, `service_principal_id`, `service_principal_key`, `tenant`, `encrypted_credential`, `service_principal_credential_type`, `service_principal_credential` and `credential` under property `type_properties` whose type is `LakeHouseLinkedServiceTypeProperties`
  - Model `LakeHouseTableDataset` moved instance variable `schema_type_properties_schema` and `table` under property `type_properties` whose type is `LakeHouseTableDatasetTypeProperties`
  - Model `LookupActivity` moved instance variable `source`, `dataset`, `first_row_only` and `treat_decimal_as_string` under property `type_properties` whose type is `LookupActivityTypeProperties`
  - Model `MagentoLinkedService` moved instance variable `host`, `access_token`, `use_encrypted_endpoints`, `use_host_verification`, `use_peer_verification` and `encrypted_credential` under property `type_properties` whose type is `MagentoLinkedServiceTypeProperties`
  - Model `MagentoObjectDataset` moved instance variable `table_name` under property `type_properties` whose type is `GenericDatasetTypeProperties`
  - Model `ManagedIdentityCredential` moved instance variable `resource_id` under property `type_properties` whose type is `ManagedIdentityTypeProperties`
  - Model `ManagedIntegrationRuntime` moved instance variable `compute_properties`, `ssis_properties`, `customer_virtual_network` and `interactive_query` under property `type_properties` whose type is `ManagedIntegrationRuntimeTypeProperties`
  - Model `ManagedIntegrationRuntimeStatus` moved instance variable `create_time`, `nodes`, `other_errors` and `last_operation` under property `type_properties` whose type is `ManagedIntegrationRuntimeStatusTypeProperties`
  - Model `MappingDataFlow` moved instance variable `sources`, `sinks`, `transformations`, `script` and `script_lines` under property `type_properties` whose type is `MappingDataFlowTypeProperties`
  - Model `MariaDBLinkedService` moved instance variable `driver_version`, `connection_string`, `server`, `port`, `username`, `database`, `ssl_mode`, `use_system_trust_store`, `password` and `encrypted_credential` under property `type_properties` whose type is `MariaDBLinkedServiceTypeProperties`
  - Model `MariaDBTableDataset` moved instance variable `table_name` under property `type_properties` whose type is `GenericDatasetTypeProperties`
  - Model `MarketoLinkedService` moved instance variable `endpoint`, `client_id`, `client_secret`, `use_encrypted_endpoints`, `use_host_verification`, `use_peer_verification` and `encrypted_credential` under property `type_properties` whose type is `MarketoLinkedServiceTypeProperties`
  - Model `MarketoObjectDataset` moved instance variable `table_name` under property `type_properties` whose type is `GenericDatasetTypeProperties`
  - Model `MicrosoftAccessLinkedService` moved instance variable `connection_string`, `authentication_type`, `credential`, `user_name`, `password` and `encrypted_credential` under property `type_properties` whose type is `MicrosoftAccessLinkedServiceTypeProperties`
  - Model `MicrosoftAccessTableDataset` moved instance variable `table_name` under property `type_properties` whose type is `MicrosoftAccessTableDatasetTypeProperties`
  - Model `MongoDbAtlasCollectionDataset` moved instance variable `collection` under property `type_properties` whose type is `MongoDbAtlasCollectionDatasetTypeProperties`
  - Model `MongoDbAtlasLinkedService` moved instance variable `connection_string`, `database` and `driver_version` under property `type_properties` whose type is `MongoDbAtlasLinkedServiceTypeProperties`
  - Model `MongoDbCollectionDataset` moved instance variable `collection_name` under property `type_properties` whose type is `MongoDbCollectionDatasetTypeProperties`
  - Model `MongoDbLinkedService` moved instance variable `server`, `authentication_type`, `database_name`, `username`, `password`, `auth_source`, `port`, `enable_ssl`, `allow_self_signed_server_cert` and `encrypted_credential` under property `type_properties` whose type is `MongoDbLinkedServiceTypeProperties`
  - Model `MongoDbV2CollectionDataset` moved instance variable `collection` under property `type_properties` whose type is `MongoDbV2CollectionDatasetTypeProperties`
  - Model `MongoDbV2LinkedService` moved instance variable `connection_string` and `database` under property `type_properties` whose type is `MongoDbV2LinkedServiceTypeProperties`
  - Model `MySqlLinkedService` moved instance variable `driver_version`, `connection_string`, `server`, `port`, `username`, `database`, `ssl_mode`, `use_system_trust_store`, `password`, `encrypted_credential`, `allow_zero_date_time`, `connection_timeout`, `convert_zero_date_time`, `guid_format`, `ssl_cert`, `ssl_key` and `treat_tiny_as_boolean` under property `type_properties` whose type is `MySqlLinkedServiceTypeProperties`
  - Model `MySqlTableDataset` moved instance variable `table_name` under property `type_properties` whose type is `MySqlTableDatasetTypeProperties`
  - Model `NetezzaLinkedService` moved instance variable `connection_string`, `server`, `port`, `uid`, `database`, `security_level`, `pwd` and `encrypted_credential` under property `type_properties` whose type is `NetezzaLinkedServiceTypeProperties`
  - Model `NetezzaTableDataset` moved instance variable `table_name`, `table` and `schema_type_properties_schema` under property `type_properties` whose type is `NetezzaTableDatasetTypeProperties`
  - Model `ODataLinkedService` moved instance variable `url`, `authentication_type`, `user_name`, `password`, `auth_headers`, `tenant`, `service_principal_id`, `azure_cloud_type`, `aad_resource_id`, `aad_service_principal_credential_type`, `service_principal_key`, `service_principal_embedded_cert`, `service_principal_embedded_cert_password` and `encrypted_credential` under property `type_properties` whose type is `ODataLinkedServiceTypeProperties`
  - Model `ODataResourceDataset` moved instance variable `path` under property `type_properties` whose type is `ODataResourceDatasetTypeProperties`
  - Model `OdbcLinkedService` moved instance variable `connection_string`, `authentication_type`, `credential`, `user_name`, `password` and `encrypted_credential` under property `type_properties` whose type is `OdbcLinkedServiceTypeProperties`
  - Model `OdbcTableDataset` moved instance variable `table_name` under property `type_properties` whose type is `OdbcTableDatasetTypeProperties`
  - Model `Office365Dataset` moved instance variable `table_name` and `predicate` under property `type_properties` whose type is `Office365DatasetTypeProperties`
  - Model `Office365LinkedService` moved instance variable `office365_tenant_id`, `service_principal_tenant_id`, `service_principal_id`, `service_principal_key`, `service_principal_credential_type`, `service_principal_embedded_cert`, `service_principal_embedded_cert_password` and `encrypted_credential` under property `type_properties` whose type is `Office365LinkedServiceTypeProperties`
  - Model `OracleCloudStorageLinkedService` moved instance variable `access_key_id`, `secret_access_key`, `service_url` and `encrypted_credential` under property `type_properties` whose type is `OracleCloudStorageLinkedServiceTypeProperties`
  - Model `OracleLinkedService` moved instance variable `connection_string`, `server`, `authentication_type`, `username`, `password`, `encryption_client`, `encryption_types_client`, `crypto_checksum_client`, `crypto_checksum_types_client`, `initial_lob_fetch_size`, `fetch_size`, `statement_cache_size`, `initialization_string`, `enable_bulk_load`, `support_v1_data_types`, `fetch_tswtz_as_timestamp` and `encrypted_credential` under property `type_properties` whose type is `OracleLinkedServiceTypeProperties`
  - Model `OracleServiceCloudLinkedService` moved instance variable `host`, `username`, `password`, `use_encrypted_endpoints`, `use_host_verification`, `use_peer_verification` and `encrypted_credential` under property `type_properties` whose type is `OracleServiceCloudLinkedServiceTypeProperties`
  - Model `OracleServiceCloudObjectDataset` moved instance variable `table_name` under property `type_properties` whose type is `GenericDatasetTypeProperties`
  - Model `OracleTableDataset` moved instance variable `table_name`, `schema_type_properties_schema` and `table` under property `type_properties` whose type is `OracleTableDatasetTypeProperties`
  - Model `OrcDataset` moved instance variable `location` and `orc_compression_codec` under property `type_properties` whose type is `OrcDatasetTypeProperties`
  - Model `ParquetDataset` moved instance variable `location` and `compression_codec` under property `type_properties` whose type is `ParquetDatasetTypeProperties`
  - Model `PaypalLinkedService` moved instance variable `host`, `client_id`, `client_secret`, `use_encrypted_endpoints`, `use_host_verification`, `use_peer_verification` and `encrypted_credential` under property `type_properties` whose type is `PaypalLinkedServiceTypeProperties`
  - Model `PaypalObjectDataset` moved instance variable `table_name` under property `type_properties` whose type is `GenericDatasetTypeProperties`
  - Model `PhoenixLinkedService` moved instance variable `host`, `port`, `http_path`, `authentication_type`, `username`, `password`, `enable_ssl`, `trusted_cert_path`, `use_system_trust_store`, `allow_host_name_cn_mismatch`, `allow_self_signed_server_cert` and `encrypted_credential` under property `type_properties` whose type is `PhoenixLinkedServiceTypeProperties`
  - Model `PhoenixObjectDataset` moved instance variable `table_name`, `table` and `schema_type_properties_schema` under property `type_properties` whose type is `PhoenixDatasetTypeProperties`
  - Model `PipelineResource` moved instance variable `description`, `activities`, `parameters`, `variables`, `concurrency`, `annotations`, `run_dimensions`, `folder` and `policy` under property `properties` whose type is `Pipeline`
  - Model `PostgreSqlLinkedService` moved instance variable `connection_string`, `password` and `encrypted_credential` under property `type_properties` whose type is `PostgreSqlLinkedServiceTypeProperties`
  - Model `PostgreSqlTableDataset` moved instance variable `table_name`, `table` and `schema_type_properties_schema` under property `type_properties` whose type is `PostgreSqlTableDatasetTypeProperties`
  - Model `PostgreSqlV2LinkedService` moved instance variable `server`, `port`, `username`, `database`, `authentication_type`, `ssl_mode`, `schema`, `pooling`, `connection_timeout`, `command_timeout`, `trust_server_certificate`, `ssl_certificate`, `ssl_key`, `ssl_password`, `read_buffer_size`, `log_parameters`, `timezone`, `encoding`, `password` and `encrypted_credential` under property `type_properties` whose type is `PostgreSqlV2LinkedServiceTypeProperties`
  - Model `PostgreSqlV2TableDataset` moved instance variable `table` and `schema_type_properties_schema` under property `type_properties` whose type is `PostgreSqlV2TableDatasetTypeProperties`
  - Model `PrestoLinkedService` moved instance variable `host`, `server_version`, `catalog`, `port`, `authentication_type`, `username`, `password`, `enable_ssl`, `enable_server_certificate_validation`, `trusted_cert_path`, `use_system_trust_store`, `allow_host_name_cn_mismatch`, `allow_self_signed_server_cert`, `time_zone_id` and `encrypted_credential` under property `type_properties` whose type is `PrestoLinkedServiceTypeProperties`
  - Model `PrestoObjectDataset` moved instance variable `table_name`, `table` and `schema_type_properties_schema` under property `type_properties` whose type is `PrestoDatasetTypeProperties`
  - Model `QuickBooksLinkedService` moved instance variable `connection_properties`, `endpoint`, `company_id`, `consumer_key`, `consumer_secret`, `access_token`, `access_token_secret`, `refresh_token`, `use_encrypted_endpoints` and `encrypted_credential` under property `type_properties` whose type is `QuickBooksLinkedServiceTypeProperties`
  - Model `QuickBooksObjectDataset` moved instance variable `table_name` under property `type_properties` whose type is `GenericDatasetTypeProperties`
  - Model `QuickbaseLinkedService` moved instance variable `url`, `user_token` and `encrypted_credential` under property `type_properties` whose type is `QuickbaseLinkedServiceTypeProperties`
  - Model `RelationalTableDataset` moved instance variable `table_name` under property `type_properties` whose type is `RelationalTableDatasetTypeProperties`
  - Model `RerunTumblingWindowTrigger` moved instance variable `parent_trigger`, `requested_start_time`, `requested_end_time` and `rerun_concurrency` under property `type_properties` whose type is `RerunTumblingWindowTriggerTypeProperties`
  - Model `Resource` moved instance variable `location`, `tags` and `e_tag` under property `system_data` whose type is `SystemData`
  - Model `ResponsysLinkedService` moved instance variable `endpoint`, `client_id`, `client_secret`, `use_encrypted_endpoints`, `use_host_verification`, `use_peer_verification` and `encrypted_credential` under property `type_properties` whose type is `ResponsysLinkedServiceTypeProperties`
  - Model `ResponsysObjectDataset` moved instance variable `table_name` under property `type_properties` whose type is `GenericDatasetTypeProperties`
  - Model `RestResourceDataset` moved instance variable `relative_url`, `request_method`, `request_body`, `additional_headers` and `pagination_rules` under property `type_properties` whose type is `RestResourceDatasetTypeProperties`
  - Model `RestServiceLinkedService` moved instance variable `url`, `enable_server_certificate_validation`, `authentication_type`, `user_name`, `password`, `auth_headers`, `service_principal_id`, `service_principal_key`, `tenant`, `azure_cloud_type`, `aad_resource_id`, `encrypted_credential`, `credential`, `client_id`, `client_secret`, `token_endpoint`, `resource`, `scope`, `service_principal_credential_type`, `service_principal_embedded_cert` and `service_principal_embedded_cert_password` under property `type_properties` whose type is `RestServiceLinkedServiceTypeProperties`
  - Model `RunQueryFilter` renamed its instance variable `values` to `values_property`
  - Model `SSISLogLocation` moved instance variable `access_credential` and `log_refresh_interval` under property `type_properties` whose type is `SSISLogLocationTypeProperties`
  - Model `SSISPackageLocation` moved instance variable `package_password`, `access_credential`, `configuration_path`, `configuration_access_credential`, `package_name`, `package_content`, `package_last_modified_date` and `child_packages` under property `type_properties` whose type is `SSISPackageLocationTypeProperties`
  - Model `SalesforceLinkedService` moved instance variable `environment_url`, `username`, `password`, `security_token`, `api_version` and `encrypted_credential` under property `type_properties` whose type is `SalesforceLinkedServiceTypeProperties`
  - Model `SalesforceMarketingCloudLinkedService` moved instance variable `connection_properties`, `client_id`, `client_secret`, `use_encrypted_endpoints`, `use_host_verification`, `use_peer_verification` and `encrypted_credential` under property `type_properties` whose type is `SalesforceMarketingCloudLinkedServiceTypeProperties`
  - Model `SalesforceMarketingCloudObjectDataset` moved instance variable `table_name` under property `type_properties` whose type is `GenericDatasetTypeProperties`
  - Model `SalesforceObjectDataset` moved instance variable `object_api_name` under property `type_properties` whose type is `SalesforceObjectDatasetTypeProperties`
  - Model `SalesforceServiceCloudLinkedService` moved instance variable `environment_url`, `username`, `password`, `security_token`, `api_version`, `extended_properties` and `encrypted_credential` under property `type_properties` whose type is `SalesforceServiceCloudLinkedServiceTypeProperties`
  - Model `SalesforceServiceCloudObjectDataset` moved instance variable `object_api_name` under property `type_properties` whose type is `SalesforceServiceCloudObjectDatasetTypeProperties`
  - Model `SalesforceServiceCloudV2LinkedService` moved instance variable `environment_url`, `authentication_type`, `client_id`, `client_secret`, `api_version` and `encrypted_credential` under property `type_properties` whose type is `SalesforceServiceCloudV2LinkedServiceTypeProperties`
  - Model `SalesforceServiceCloudV2ObjectDataset` moved instance variable `object_api_name` and `report_id` under property `type_properties` whose type is `SalesforceServiceCloudV2ObjectDatasetTypeProperties`
  - Model `SalesforceV2LinkedService` moved instance variable `environment_url`, `authentication_type`, `client_id`, `client_secret`, `api_version` and `encrypted_credential` under property `type_properties` whose type is `SalesforceV2LinkedServiceTypeProperties`
  - Model `SalesforceV2ObjectDataset` moved instance variable `object_api_name` and `report_id` under property `type_properties` whose type is `SalesforceV2ObjectDatasetTypeProperties`
  - Model `SapBWLinkedService` moved instance variable `server`, `system_number`, `client_id`, `user_name`, `password` and `encrypted_credential` under property `type_properties` whose type is `SapBWLinkedServiceTypeProperties`
  - Model `SapCloudForCustomerLinkedService` moved instance variable `url`, `username`, `password` and `encrypted_credential` under property `type_properties` whose type is `SapCloudForCustomerLinkedServiceTypeProperties`
  - Model `SapCloudForCustomerResourceDataset` moved instance variable `path` under property `type_properties` whose type is `SapCloudForCustomerResourceDatasetTypeProperties`
  - Model `SapEccLinkedService` moved instance variable `url`, `username`, `password` and `encrypted_credential` under property `type_properties` whose type is `SapEccLinkedServiceTypeProperties`
  - Model `SapEccResourceDataset` moved instance variable `path` under property `type_properties` whose type is `SapEccResourceDatasetTypeProperties`
  - Model `SapHanaLinkedService` moved instance variable `connection_string`, `server`, `authentication_type`, `user_name`, `password` and `encrypted_credential` under property `type_properties` whose type is `SapHanaLinkedServiceProperties`
  - Model `SapHanaTableDataset` moved instance variable `schema_type_properties_schema` and `table` under property `type_properties` whose type is `SapHanaTableDatasetTypeProperties`
  - Model `SapOdpLinkedService` moved instance variable `server`, `system_number`, `client_id`, `language`, `system_id`, `user_name`, `password`, `message_server`, `message_server_service`, `snc_mode`, `snc_my_name`, `snc_partner_name`, `snc_library_path`, `snc_qop`, `x509_certificate_path`, `logon_group`, `subscriber_name` and `encrypted_credential` under property `type_properties` whose type is `SapOdpLinkedServiceTypeProperties`
  - Model `SapOdpResourceDataset` moved instance variable `context` and `object_name` under property `type_properties` whose type is `SapOdpResourceDatasetTypeProperties`
  - Model `SapOpenHubLinkedService` moved instance variable `server`, `system_number`, `client_id`, `language`, `system_id`, `user_name`, `password`, `message_server`, `message_server_service`, `logon_group` and `encrypted_credential` under property `type_properties` whose type is `SapOpenHubLinkedServiceTypeProperties`
  - Model `SapOpenHubTableDataset` moved instance variable `open_hub_destination_name`, `exclude_last_request` and `base_request_id` under property `type_properties` whose type is `SapOpenHubTableDatasetTypeProperties`
  - Model `SapTableLinkedService` moved instance variable `server`, `system_number`, `client_id`, `language`, `system_id`, `user_name`, `password`, `message_server`, `message_server_service`, `snc_mode`, `snc_my_name`, `snc_partner_name`, `snc_library_path`, `snc_qop`, `logon_group` and `encrypted_credential` under property `type_properties` whose type is `SapTableLinkedServiceTypeProperties`
  - Model `SapTableResourceDataset` moved instance variable `table_name` under property `type_properties` whose type is `SapTableResourceDatasetTypeProperties`
  - Model `ScheduleTrigger` moved instance variable `recurrence` under property `type_properties` whose type is `ScheduleTriggerTypeProperties`
  - Model `ScriptActivity` moved instance variable `script_block_execution_timeout`, `scripts`, `log_settings`, `return_multistatement_result` and `treat_decimal_as_string` under property `type_properties` whose type is `ScriptActivityTypeProperties`
  - Model `SelfHostedIntegrationRuntime` moved instance variable `linked_info` and `self_contained_interactive_authoring_enabled` under property `type_properties` whose type is `SelfHostedIntegrationRuntimeTypeProperties`
  - Model `SelfHostedIntegrationRuntimeStatus` moved instance variable `create_time`, `task_queue_id`, `internal_channel_encryption`, `version`, `nodes`, `scheduled_update_date`, `update_delay_offset`, `local_time_zone_offset`, `capabilities`, `service_urls`, `auto_update`, `version_status`, `links`, `pushed_version`, `latest_version`, `auto_update_eta` and `self_contained_interactive_authoring_enabled` under property `type_properties` whose type is `SelfHostedIntegrationRuntimeStatusTypeProperties`
  - Model `ServiceNowLinkedService` moved instance variable `endpoint`, `authentication_type`, `username`, `password`, `client_id`, `client_secret`, `use_encrypted_endpoints`, `use_host_verification`, `use_peer_verification` and `encrypted_credential` under property `type_properties` whose type is `ServiceNowLinkedServiceTypeProperties`
  - Model `ServiceNowObjectDataset` moved instance variable `table_name` under property `type_properties` whose type is `GenericDatasetTypeProperties`
  - Model `ServiceNowV2LinkedService` moved instance variable `endpoint`, `authentication_type`, `username`, `password`, `client_id`, `client_secret`, `grant_type` and `encrypted_credential` under property `type_properties` whose type is `ServiceNowV2LinkedServiceTypeProperties`
  - Model `ServiceNowV2ObjectDataset` moved instance variable `table_name` and `value_type` under property `type_properties` whose type is `ServiceNowV2DatasetTypeProperties`
  - Model `ServicePrincipalCredential` moved instance variable `service_principal_id`, `service_principal_key` and `tenant` under property `type_properties` whose type is `ServicePrincipalCredentialTypeProperties`
  - Model `SetVariableActivity` moved instance variable `variable_name`, `value` and `set_system_variable` under property `type_properties` whose type is `SetVariableActivityTypeProperties`
  - Model `SftpServerLinkedService` moved instance variable `host`, `port`, `authentication_type`, `user_name`, `password`, `encrypted_credential`, `private_key_path`, `private_key_content`, `pass_phrase`, `skip_host_key_validation` and `host_key_fingerprint` under property `type_properties` whose type is `SftpServerLinkedServiceTypeProperties`
  - Model `SharePointOnlineListLinkedService` moved instance variable `site_url`, `tenant_id`, `service_principal_id`, `service_principal_key`, `service_principal_credential_type`, `service_principal_embedded_cert`, `service_principal_embedded_cert_password` and `encrypted_credential` under property `type_properties` whose type is `SharePointOnlineListLinkedServiceTypeProperties`
  - Model `SharePointOnlineListResourceDataset` moved instance variable `list_name` under property `type_properties` whose type is `SharePointOnlineListDatasetTypeProperties`
  - Model `ShopifyLinkedService` moved instance variable `host`, `access_token`, `use_encrypted_endpoints`, `use_host_verification`, `use_peer_verification` and `encrypted_credential` under property `type_properties` whose type is `ShopifyLinkedServiceTypeProperties`
  - Model `ShopifyObjectDataset` moved instance variable `table_name` under property `type_properties` whose type is `GenericDatasetTypeProperties`
  - Model `SmartsheetLinkedService` moved instance variable `api_token` and `encrypted_credential` under property `type_properties` whose type is `SmartsheetLinkedServiceTypeProperties`
  - Model `SnowflakeDataset` moved instance variable `schema_type_properties_schema` and `table` under property `type_properties` whose type is `SnowflakeDatasetTypeProperties`
  - Model `SnowflakeLinkedService` moved instance variable `connection_string`, `password` and `encrypted_credential` under property `type_properties` whose type is `SnowflakeLinkedServiceTypeProperties`
  - Model `SnowflakeV2Dataset` moved instance variable `schema_type_properties_schema` and `table` under property `type_properties` whose type is `SnowflakeDatasetTypeProperties`
  - Model `SnowflakeV2LinkedService` moved instance variable `account_identifier`, `user`, `password`, `database`, `warehouse`, `authentication_type`, `client_id`, `client_secret`, `tenant_id`, `scope`, `private_key`, `private_key_passphrase`, `role`, `host`, `schema`, `encrypted_credential` and `use_utc_timestamps` under property `type_properties` whose type is `SnowflakeLinkedV2ServiceTypeProperties`
  - Model `SparkLinkedService` moved instance variable `host`, `port`, `server_type`, `thrift_transport_protocol`, `authentication_type`, `username`, `password`, `http_path`, `enable_ssl`, `enable_server_certificate_validation`, `trusted_cert_path`, `use_system_trust_store`, `allow_host_name_cn_mismatch`, `allow_self_signed_server_cert` and `encrypted_credential` under property `type_properties` whose type is `SparkLinkedServiceTypeProperties`
  - Model `SparkObjectDataset` moved instance variable `table_name`, `table` and `schema_type_properties_schema` under property `type_properties` whose type is `SparkDatasetTypeProperties`
  - Model `SqlDWUpsertSettings` renamed its instance variable `keys` to `keys_property`
  - Model `SqlServerLinkedService` moved instance variable `server`, `database`, `encrypt`, `trust_server_certificate`, `host_name_in_certificate`, `application_intent`, `connect_timeout`, `connect_retry_count`, `connect_retry_interval`, `load_balance_timeout`, `command_timeout`, `integrated_security`, `failover_partner`, `max_pool_size`, `min_pool_size`, `multiple_active_result_sets`, `multi_subnet_failover`, `packet_size`, `pooling`, `connection_string`, `authentication_type`, `user_name`, `password`, `encrypted_credential`, `always_encrypted_settings` and `credential` under property `type_properties` whose type is `SqlServerLinkedServiceTypeProperties`
  - Model `SqlServerStoredProcedureActivity` moved instance variable `stored_procedure_name` and `stored_procedure_parameters` under property `type_properties` whose type is `SqlServerStoredProcedureActivityTypeProperties`
  - Model `SqlServerTableDataset` moved instance variable `table_name`, `schema_type_properties_schema` and `table` under property `type_properties` whose type is `SqlServerTableDatasetTypeProperties`
  - Model `SqlUpsertSettings` renamed its instance variable `keys` to `keys_property`
  - Model `SquareLinkedService` moved instance variable `connection_properties`, `host`, `client_id`, `client_secret`, `redirect_uri`, `use_encrypted_endpoints`, `use_host_verification`, `use_peer_verification` and `encrypted_credential` under property `type_properties` whose type is `SquareLinkedServiceTypeProperties`
  - Model `SquareObjectDataset` moved instance variable `table_name` under property `type_properties` whose type is `GenericDatasetTypeProperties`
  - Model `SwitchActivity` moved instance variable `on`, `cases` and `default_activities` under property `type_properties` whose type is `SwitchActivityTypeProperties`
  - Model `SybaseLinkedService` moved instance variable `server`, `database`, `schema`, `authentication_type`, `username`, `password` and `encrypted_credential` under property `type_properties` whose type is `SybaseLinkedServiceTypeProperties`
  - Model `SybaseTableDataset` moved instance variable `table_name` under property `type_properties` whose type is `SybaseTableDatasetTypeProperties`
  - Model `SynapseNotebookActivity` moved instance variable `notebook`, `spark_pool`, `parameters`, `executor_size`, `conf`, `driver_size`, `num_executors`, `configuration_type`, `target_spark_configuration` and `spark_config` under property `type_properties` whose type is `SynapseNotebookActivityTypeProperties`
  - Model `SynapseSparkJobDefinitionActivity` moved instance variable `spark_job`, `arguments`, `file`, `scan_folder`, `class_name`, `files`, `python_code_reference`, `files_v2`, `target_big_data_pool`, `executor_size`, `conf`, `driver_size`, `num_executors`, `configuration_type`, `target_spark_configuration` and `spark_config` under property `type_properties` whose type is `SynapseSparkJobActivityTypeProperties`
  - Model `TeamDeskLinkedService` moved instance variable `authentication_type`, `url`, `user_name`, `password`, `api_token` and `encrypted_credential` under property `type_properties` whose type is `TeamDeskLinkedServiceTypeProperties`
  - Model `TeradataLinkedService` moved instance variable `connection_string`, `server`, `authentication_type`, `username`, `password`, `ssl_mode`, `port_number`, `https_port_number`, `use_data_encryption`, `character_set`, `max_resp_size` and `encrypted_credential` under property `type_properties` whose type is `TeradataLinkedServiceTypeProperties`
  - Model `TeradataTableDataset` moved instance variable `database` and `table` under property `type_properties` whose type is `TeradataTableDatasetTypeProperties`
  - Model `TumblingWindowTrigger` moved instance variable `frequency`, `interval`, `start_time`, `end_time`, `delay`, `max_concurrency`, `retry_policy` and `depends_on` under property `type_properties` whose type is `TumblingWindowTriggerTypeProperties`
  - Model `TwilioLinkedService` moved instance variable `user_name` and `password` under property `type_properties` whose type is `TwilioLinkedServiceTypeProperties`
  - Model `UntilActivity` moved instance variable `expression`, `timeout` and `activities` under property `type_properties` whose type is `UntilActivityTypeProperties`
  - Model `ValidationActivity` moved instance variable `timeout`, `sleep`, `minimum_size`, `child_items` and `dataset` under property `type_properties` whose type is `ValidationActivityTypeProperties`
  - Model `VerticaLinkedService` moved instance variable `connection_string`, `server`, `port`, `uid`, `database`, `pwd` and `encrypted_credential` under property `type_properties` whose type is `VerticaLinkedServiceTypeProperties`
  - Model `VerticaTableDataset` moved instance variable `table_name`, `table` and `schema_type_properties_schema` under property `type_properties` whose type is `VerticaDatasetTypeProperties`
  - Model `WaitActivity` moved instance variable `wait_time_in_seconds` under property `type_properties` whose type is `WaitActivityTypeProperties`
  - Model `WarehouseLinkedService` moved instance variable `artifact_id`, `endpoint`, `workspace_id`, `authentication_type`, `service_principal_id`, `service_principal_key`, `tenant`, `encrypted_credential`, `service_principal_credential_type`, `service_principal_credential` and `credential` under property `type_properties` whose type is `WarehouseLinkedServiceTypeProperties`
  - Model `WarehouseTableDataset` moved instance variable `schema_type_properties_schema` and `table` under property `type_properties` whose type is `WarehouseTableDatasetTypeProperties`
  - Model `WebActivity` moved instance variable `method`, `url`, `headers`, `body`, `authentication`, `disable_cert_validation`, `http_request_timeout`, `turn_off_async`, `datasets`, `linked_services` and `connect_via` under property `type_properties` whose type is `WebActivityTypeProperties`
  - Model `WebHookActivity` moved instance variable `method`, `url`, `timeout`, `headers`, `body`, `authentication` and `report_status_on_call_back` under property `type_properties` whose type is `WebHookActivityTypeProperties`
  - Model `WebTableDataset` moved instance variable `index` and `path` under property `type_properties` whose type is `WebTableDatasetTypeProperties`
  - Model `WranglingDataFlow` moved instance variable `sources`, `script` and `document_locale` under property `type_properties` whose type is `PowerQueryTypeProperties`
  - Model `XeroLinkedService` moved instance variable `connection_properties`, `host`, `consumer_key`, `private_key`, `use_encrypted_endpoints`, `use_host_verification`, `use_peer_verification` and `encrypted_credential` under property `type_properties` whose type is `XeroLinkedServiceTypeProperties`
  - Model `XeroObjectDataset` moved instance variable `table_name` under property `type_properties` whose type is `GenericDatasetTypeProperties`
  - Model `XmlDataset` moved instance variable `location`, `encoding_name`, `null_value` and `compression` under property `type_properties` whose type is `XmlDatasetTypeProperties`
  - Model `ZendeskLinkedService` moved instance variable `authentication_type`, `url`, `user_name`, `password`, `api_token` and `encrypted_credential` under property `type_properties` whose type is `ZendeskLinkedServiceTypeProperties`
  - Model `ZohoLinkedService` moved instance variable `connection_properties`, `endpoint`, `access_token`, `use_encrypted_endpoints`, `use_host_verification`, `use_peer_verification` and `encrypted_credential` under property `type_properties` whose type is `ZohoLinkedServiceTypeProperties`
  - Model `ZohoObjectDataset` moved instance variable `table_name` under property `type_properties` whose type is `GenericDatasetTypeProperties`
  - Method `ChangeDataCaptureOperations.create_or_update` replaced positional_or_keyword parameter `if_match` to keyword_only parameter `etag`/`match_condition`
  - Method `ChangeDataCaptureOperations.get` replaced positional_or_keyword parameter `if_none_match` to keyword_only parameter `etag`/`match_condition`
  - Method `CredentialOperationsOperations.create_or_update` replaced positional_or_keyword parameter `if_match` to keyword_only parameter `etag`/`match_condition`
  - Method `CredentialOperationsOperations.get` replaced positional_or_keyword parameter `if_none_match` to keyword_only parameter `etag`/`match_condition`
  - Method `DataFlowsOperations.create_or_update` replaced positional_or_keyword parameter `if_match` to keyword_only parameter `etag`/`match_condition`
  - Method `DataFlowsOperations.get` replaced positional_or_keyword parameter `if_none_match` to keyword_only parameter `etag`/`match_condition`
  - Method `DatasetsOperations.create_or_update` replaced positional_or_keyword parameter `if_match` to keyword_only parameter `etag`/`match_condition`
  - Method `DatasetsOperations.get` replaced positional_or_keyword parameter `if_none_match` to keyword_only parameter `etag`/`match_condition`
  - Method `FactoriesOperations.create_or_update` replaced positional_or_keyword parameter `if_match` to keyword_only parameter `etag`/`match_condition`
  - Method `FactoriesOperations.get` replaced positional_or_keyword parameter `if_none_match` to keyword_only parameter `etag`/`match_condition`
  - Method `IntegrationRuntimesOperations.create_or_update` replaced positional_or_keyword parameter `if_match` to keyword_only parameter `etag`/`match_condition`
  - Method `IntegrationRuntimesOperations.get` replaced positional_or_keyword parameter `if_none_match` to keyword_only parameter `etag`/`match_condition`
  - Method `LinkedServicesOperations.create_or_update` replaced positional_or_keyword parameter `if_match` to keyword_only parameter `etag`/`match_condition`
  - Method `LinkedServicesOperations.get` replaced positional_or_keyword parameter `if_none_match` to keyword_only parameter `etag`/`match_condition`
  - Method `ManagedPrivateEndpointsOperations.create_or_update` replaced positional_or_keyword parameter `if_match` to keyword_only parameter `etag`/`match_condition`
  - Method `ManagedPrivateEndpointsOperations.get` replaced positional_or_keyword parameter `if_none_match` to keyword_only parameter `etag`/`match_condition`
  - Method `ManagedVirtualNetworksOperations.create_or_update` replaced positional_or_keyword parameter `if_match` to keyword_only parameter `etag`/`match_condition`
  - Method `ManagedVirtualNetworksOperations.get` replaced positional_or_keyword parameter `if_none_match` to keyword_only parameter `etag`/`match_condition`
  - Method `PipelineRunsOperations.cancel` changed its parameter `is_recursive` from `positional_or_keyword` to `keyword_only`
  - Method `PipelinesOperations.create_or_update` replaced positional_or_keyword parameter `if_match` to keyword_only parameter `etag`/`match_condition`
  - Method `PipelinesOperations.create_run` changed its parameter `reference_pipeline_run_id`/`is_recovery`/`start_activity_name`/`start_from_failure` from `positional_or_keyword` to `keyword_only`
  - Method `PipelinesOperations.get` replaced positional_or_keyword parameter `if_none_match` to keyword_only parameter `etag`/`match_condition`
  - Method `PrivateEndpointConnectionOperations.create_or_update` replaced positional_or_keyword parameter `if_match` to keyword_only parameter `etag`/`match_condition`
  - Method `PrivateEndpointConnectionOperations.get` replaced positional_or_keyword parameter `if_none_match` to keyword_only parameter `etag`/`match_condition`
  - Method `TriggersOperations.create_or_update` replaced positional_or_keyword parameter `if_match` to keyword_only parameter `etag`/`match_condition`
  - Method `TriggersOperations.get` replaced positional_or_keyword parameter `if_none_match` to keyword_only parameter `etag`/`match_condition`

### Other Changes

  - Deleted model `ChangeDataCaptureListResponse`/`CredentialListResponse`/`DataFlowListResponse`/`DatasetListResponse`/`FactoryListResponse`/`GlobalParameterListResponse`/`IntegrationRuntimeListResponse`/`IntegrationRuntimeStatusListResponse`/`LinkedServiceListResponse`/`ManagedPrivateEndpointListResponse`/`ManagedVirtualNetworkListResponse`/`OperationListResponse`/`PipelineListResponse`/`PrivateEndpointConnectionListResponse`/`QueryDataFlowDebugSessionsResponse`/`TriggerListResponse` which actually were not used by SDK users
  - Deleted model `CopyTranslator`/`GetDataFactoryOperationStatusResponse`/`TabularTranslator`/`TypeConversionSettings`/`AdditionalColumns`/`DatasetDataElement`/`DatasetSchemaDataElement`/`OutputColumn`/`StoredProcedureParameter` which actually were not used by SDK users
  - Deleted enum `AmazonRdsForOraclePartitionOption`/`AvroCompressionCodec`/`CompressionCodec`/`CopyBehaviorType`/`DatasetCompressionLevel`/`DynamicsAuthenticationType`/`DynamicsDeploymentType`/`HdiNodeTypes`/`JsonFormatFilePattern`/`JsonWriteFilePattern`/`NetezzaPartitionOption`/`OraclePartitionOption`/`OrcCompressionCodec`/`SalesforceSourceReadBehavior`/`SapHanaPartitionOption`/`SapTablePartitionOption`/`ServicePrincipalCredentialType`/`SqlPartitionOption`/`StoredProcedureParameterType`/`TeradataPartitionOption`/`ScriptType`/`SqlDWWriteBehaviorEnum`/`SqlWriteBehaviorEnum` which actually were not used by SDK users

## 9.3.0 (2026-03-10)

### Features Added

  - Model `DataFactoryManagementClient` added parameter `cloud_setting` in method `__init__`
  - Client `DataFactoryManagementClient` added operation group `integration_runtime`
  - Model `AmazonRdsForOracleLinkedService` added property `server`
  - Model `AmazonRdsForOracleLinkedService` added property `authentication_type`
  - Model `AmazonRdsForOracleLinkedService` added property `username`
  - Model `AmazonRdsForOracleLinkedService` added property `encryption_client`
  - Model `AmazonRdsForOracleLinkedService` added property `encryption_types_client`
  - Model `AmazonRdsForOracleLinkedService` added property `crypto_checksum_client`
  - Model `AmazonRdsForOracleLinkedService` added property `crypto_checksum_types_client`
  - Model `AmazonRdsForOracleLinkedService` added property `initial_lob_fetch_size`
  - Model `AmazonRdsForOracleLinkedService` added property `fetch_size`
  - Model `AmazonRdsForOracleLinkedService` added property `statement_cache_size`
  - Model `AmazonRdsForOracleLinkedService` added property `initialization_string`
  - Model `AmazonRdsForOracleLinkedService` added property `enable_bulk_load`
  - Model `AmazonRdsForOracleLinkedService` added property `support_v1_data_types`
  - Model `AmazonRdsForOracleLinkedService` added property `fetch_tswtz_as_timestamp`
  - Model `AmazonRdsForOracleSource` added property `number_precision`
  - Model `AmazonRdsForOracleSource` added property `number_scale`
  - Model `AzureDatabricksLinkedService` added property `data_security_mode`
  - Model `HDInsightLinkedService` added property `cluster_auth_type`
  - Model `HDInsightLinkedService` added property `credential`
  - Model `HDInsightOnDemandLinkedService` added property `cluster_resource_group_auth_type`
  - Model `HiveLinkedService` added property `enable_server_certificate_validation`
  - Model `ImpalaLinkedService` added property `thrift_transport_protocol`
  - Model `ImpalaLinkedService` added property `enable_server_certificate_validation`
  - Model `JiraObjectDataset` added property `schema_type_properties_schema`
  - Model `JiraObjectDataset` added property `table`
  - Model `LakeHouseLinkedService` added property `authentication_type`
  - Model `LakeHouseLinkedService` added property `credential`
  - Model `LookupActivity` added property `treat_decimal_as_string`
  - Model `ManagedIntegrationRuntime` added property `interactive_query`
  - Model `NetezzaLinkedService` added property `server`
  - Model `NetezzaLinkedService` added property `port`
  - Model `NetezzaLinkedService` added property `uid`
  - Model `NetezzaLinkedService` added property `database`
  - Model `NetezzaLinkedService` added property `security_level`
  - Model `Office365LinkedService` added property `service_principal_credential_type`
  - Model `Office365LinkedService` added property `service_principal_embedded_cert`
  - Model `Office365LinkedService` added property `service_principal_embedded_cert_password`
  - Model `OracleSource` added property `number_precision`
  - Model `OracleSource` added property `number_scale`
  - Model `QuickBooksLinkedService` added property `refresh_token`
  - Model `SalesforceV2Source` added property `partition_option`
  - Model `ScriptActivity` added property `treat_decimal_as_string`
  - Model `SnowflakeV2LinkedService` added property `role`
  - Model `SnowflakeV2LinkedService` added property `schema`
  - Model `SnowflakeV2LinkedService` added property `use_utc_timestamps`
  - Model `SparkLinkedService` added property `enable_server_certificate_validation`
  - Model `WarehouseLinkedService` added property `authentication_type`
  - Model `WarehouseLinkedService` added property `credential`
  - Added enum `AmazonRdsForOracleAuthenticationType`
  - Added model `DatabricksJobActivity`
  - Added model `EnableInteractiveQueryRequest`
  - Added model `ErrorAdditionalInfo`
  - Added model `ErrorDetail`
  - Added model `ErrorResponse`
  - Added enum `HDInsightClusterAuthenticationType`
  - Added enum `HDInsightOndemandClusterResourceGroupAuthenticationType`
  - Added enum `ImpalaThriftTransportProtocol`
  - Added enum `InteractiveCapabilityStatus`
  - Added model `InteractiveQueryProperties`
  - Added enum `LakehouseAuthenticationType`
  - Added enum `NetezzaSecurityLevelType`
  - Added enum `WarehouseAuthenticationType`

## 9.2.0 (2025-04-20)

### Features Added

  - Model AzurePostgreSqlLinkedService has a new parameter azure_cloud_type
  - Model AzurePostgreSqlLinkedService has a new parameter credential
  - Model AzurePostgreSqlLinkedService has a new parameter service_principal_credential_type
  - Model AzurePostgreSqlLinkedService has a new parameter service_principal_embedded_cert
  - Model AzurePostgreSqlLinkedService has a new parameter service_principal_embedded_cert_password
  - Model AzurePostgreSqlLinkedService has a new parameter service_principal_id
  - Model AzurePostgreSqlLinkedService has a new parameter service_principal_key
  - Model AzurePostgreSqlLinkedService has a new parameter tenant
  - Model AzurePostgreSqlSink has a new parameter upsert_settings
  - Model AzurePostgreSqlSink has a new parameter write_method
  - Model CommonDataServiceForAppsSink has a new parameter bypass_business_logic_execution
  - Model CommonDataServiceForAppsSink has a new parameter bypass_power_automate_flows
  - Model DynamicsCrmSink has a new parameter bypass_business_logic_execution
  - Model DynamicsCrmSink has a new parameter bypass_power_automate_flows
  - Model DynamicsSink has a new parameter bypass_business_logic_execution
  - Model DynamicsSink has a new parameter bypass_power_automate_flows
  - Model GreenplumLinkedService has a new parameter authentication_type
  - Model GreenplumLinkedService has a new parameter command_timeout
  - Model GreenplumLinkedService has a new parameter connection_timeout
  - Model GreenplumLinkedService has a new parameter database
  - Model GreenplumLinkedService has a new parameter host
  - Model GreenplumLinkedService has a new parameter port
  - Model GreenplumLinkedService has a new parameter ssl_mode
  - Model GreenplumLinkedService has a new parameter username
  - Model Office365LinkedService has a new parameter service_principal_credential_type
  - Model Office365LinkedService has a new parameter service_principal_embedded_cert
  - Model Office365LinkedService has a new parameter service_principal_embedded_cert_password
  - Model OracleLinkedService has a new parameter authentication_type
  - Model OracleLinkedService has a new parameter crypto_checksum_client
  - Model OracleLinkedService has a new parameter crypto_checksum_types_client
  - Model OracleLinkedService has a new parameter enable_bulk_load
  - Model OracleLinkedService has a new parameter encryption_client
  - Model OracleLinkedService has a new parameter encryption_types_client
  - Model OracleLinkedService has a new parameter fetch_size
  - Model OracleLinkedService has a new parameter fetch_tswtz_as_timestamp
  - Model OracleLinkedService has a new parameter initial_lob_fetch_size
  - Model OracleLinkedService has a new parameter initialization_string
  - Model OracleLinkedService has a new parameter server
  - Model OracleLinkedService has a new parameter statement_cache_size
  - Model OracleLinkedService has a new parameter support_v1_data_types
  - Model OracleLinkedService has a new parameter username
  - Model PrestoLinkedService has a new parameter enable_server_certificate_validation
  - Model ScriptActivity has a new parameter return_multistatement_result
  - Model ServiceNowV2ObjectDataset has a new parameter value_type
  - Model SnowflakeV2LinkedService has a new parameter role
  - Model SnowflakeV2LinkedService has a new parameter schema
  - Model TeradataLinkedService has a new parameter character_set
  - Model TeradataLinkedService has a new parameter https_port_number
  - Model TeradataLinkedService has a new parameter max_resp_size
  - Model TeradataLinkedService has a new parameter port_number
  - Model TeradataLinkedService has a new parameter ssl_mode
  - Model TeradataLinkedService has a new parameter use_data_encryption
  - Model TypeConversionSettings has a new parameter date_format
  - Model TypeConversionSettings has a new parameter time_format

## 9.1.0 (2024-12-16)

### Features Added

  - Model `AzurePostgreSqlLinkedService` added property `server`
  - Model `AzurePostgreSqlLinkedService` added property `port`
  - Model `AzurePostgreSqlLinkedService` added property `username`
  - Model `AzurePostgreSqlLinkedService` added property `database`
  - Model `AzurePostgreSqlLinkedService` added property `ssl_mode`
  - Model `AzurePostgreSqlLinkedService` added property `timeout`
  - Model `AzurePostgreSqlLinkedService` added property `command_timeout`
  - Model `AzurePostgreSqlLinkedService` added property `trust_server_certificate`
  - Model `AzurePostgreSqlLinkedService` added property `read_buffer_size`
  - Model `AzurePostgreSqlLinkedService` added property `timezone`
  - Model `AzurePostgreSqlLinkedService` added property `encoding`
  - Model `MariaDBLinkedService` added property `ssl_mode`
  - Model `MariaDBLinkedService` added property `use_system_trust_store`
  - Model `MySqlLinkedService` added property `allow_zero_date_time`
  - Model `MySqlLinkedService` added property `connection_timeout`
  - Model `MySqlLinkedService` added property `convert_zero_date_time`
  - Model `MySqlLinkedService` added property `guid_format`
  - Model `MySqlLinkedService` added property `ssl_cert`
  - Model `MySqlLinkedService` added property `ssl_key`
  - Model `MySqlLinkedService` added property `treat_tiny_as_boolean`
  - Model `PostgreSqlV2LinkedService` added property `authentication_type`
  - Model `SalesforceV2Source` added property `page_size`
  - Model `ServiceNowV2Source` added property `page_size`
  - Model `SnowflakeV2LinkedService` added property `host`
  - Added model `IcebergDataset`
  - Added model `IcebergSink`
  - Added model `IcebergWriteSettings`

## 9.0.0 (2024-08-19)

### Features Added

  - The model or publicly exposed class 'AmazonMWSLinkedService' had property 'version' added in the __init__ method in the current version
  - The model or publicly exposed class 'AmazonRdsForOracleLinkedService' had property 'version' added in the __init__ method in the current version
  - The model or publicly exposed class 'AmazonRdsForSqlServerLinkedService' had property 'version' added in the __init__ method in the current version
  - The model or publicly exposed class 'AmazonRedshiftLinkedService' had property 'version' added in the __init__ method in the current version
  - The model or publicly exposed class 'AmazonS3CompatibleLinkedService' had property 'version' added in the __init__ method in the current version
  - The model or publicly exposed class 'AmazonS3LinkedService' had property 'version' added in the __init__ method in the current version
  - The model or publicly exposed class 'AppFiguresLinkedService' had property 'version' added in the __init__ method in the current version
  - The model or publicly exposed class 'AsanaLinkedService' had property 'version' added in the __init__ method in the current version
  - The model or publicly exposed class 'AzureBatchLinkedService' had property 'version' added in the __init__ method in the current version
  - The model or publicly exposed class 'AzureBlobFSLinkedService' had property 'version' added in the __init__ method in the current version
  - The model or publicly exposed class 'AzureBlobStorageLinkedService' had property 'version' added in the __init__ method in the current version
  - The model or publicly exposed class 'AzureDataExplorerLinkedService' had property 'version' added in the __init__ method in the current version
  - The model or publicly exposed class 'AzureDataLakeAnalyticsLinkedService' had property 'version' added in the __init__ method in the current version
  - The model or publicly exposed class 'AzureDataLakeStoreLinkedService' had property 'version' added in the __init__ method in the current version
  - The model or publicly exposed class 'AzureDatabricksDeltaLakeLinkedService' had property 'version' added in the __init__ method in the current version
  - The model or publicly exposed class 'AzureDatabricksLinkedService' had property 'version' added in the __init__ method in the current version
  - The model or publicly exposed class 'AzureFileStorageLinkedService' had property 'version' added in the __init__ method in the current version
  - The model or publicly exposed class 'AzureFileStorageLinkedService' had property 'service_endpoint' added in the current version
  - The model or publicly exposed class 'AzureFileStorageLinkedService' had property 'credential' added in the current version
  - The model or publicly exposed class 'AzureFunctionLinkedService' had property 'version' added in the __init__ method in the current version
  - The model or publicly exposed class 'AzureKeyVaultLinkedService' had property 'version' added in the __init__ method in the current version
  - The model or publicly exposed class 'AzureMLLinkedService' had property 'version' added in the __init__ method in the current version
  - The model or publicly exposed class 'AzureMLServiceLinkedService' had property 'version' added in the __init__ method in the current version
  - The model or publicly exposed class 'AzureMariaDBLinkedService' had property 'version' added in the __init__ method in the current version
  - The model or publicly exposed class 'AzureMySqlLinkedService' had property 'version' added in the __init__ method in the current version
  - The model or publicly exposed class 'AzurePostgreSqlLinkedService' had property 'version' added in the __init__ method in the current version
  - The model or publicly exposed class 'AzureSearchLinkedService' had property 'version' added in the __init__ method in the current version
  - The model or publicly exposed class 'AzureSqlDWLinkedService' had property 'version' added in the __init__ method in the current version
  - The model or publicly exposed class 'AzureSqlDatabaseLinkedService' had property 'version' added in the __init__ method in the current version
  - The model or publicly exposed class 'AzureSqlMILinkedService' had property 'version' added in the __init__ method in the current version
  - The model or publicly exposed class 'AzureStorageLinkedService' had property 'version' added in the __init__ method in the current version
  - The model or publicly exposed class 'AzureSynapseArtifactsLinkedService' had property 'version' added in the __init__ method in the current version
  - The model or publicly exposed class 'AzureTableStorageLinkedService' had property 'version' added in the __init__ method in the current version
  - The model or publicly exposed class 'AzureTableStorageLinkedService' had property 'service_endpoint' added in the current version
  - The model or publicly exposed class 'AzureTableStorageLinkedService' had property 'credential' added in the current version
  - The model or publicly exposed class 'CassandraLinkedService' had property 'version' added in the __init__ method in the current version
  - The model or publicly exposed class 'CommonDataServiceForAppsLinkedService' had property 'version' added in the __init__ method in the current version
  - The model or publicly exposed class 'CommonDataServiceForAppsLinkedService' had property 'domain' added in the current version
  - The model or publicly exposed class 'ConcurLinkedService' had property 'version' added in the __init__ method in the current version
  - The model or publicly exposed class 'CosmosDbLinkedService' had property 'version' added in the __init__ method in the current version
  - The model or publicly exposed class 'CosmosDbMongoDbApiLinkedService' had property 'version' added in the __init__ method in the current version
  - The model or publicly exposed class 'CouchbaseLinkedService' had property 'version' added in the __init__ method in the current version
  - The model or publicly exposed class 'CustomDataSourceLinkedService' had property 'version' added in the __init__ method in the current version
  - The model or publicly exposed class 'DataworldLinkedService' had property 'version' added in the __init__ method in the current version
  - The model or publicly exposed class 'Db2LinkedService' had property 'version' added in the __init__ method in the current version
  - The model or publicly exposed class 'DrillLinkedService' had property 'version' added in the __init__ method in the current version
  - The model or publicly exposed class 'DynamicsAXLinkedService' had property 'version' added in the __init__ method in the current version
  - The model or publicly exposed class 'DynamicsAuthenticationType' had property 'ACTIVE_DIRECTORY' added in the current version
  - The model or publicly exposed class 'DynamicsCrmLinkedService' had property 'version' added in the __init__ method in the current version
  - The model or publicly exposed class 'DynamicsCrmLinkedService' had property 'domain' added in the current version
  - The model or publicly exposed class 'DynamicsLinkedService' had property 'version' added in the __init__ method in the current version
  - The model or publicly exposed class 'DynamicsLinkedService' had property 'domain' added in the current version
  - The model or publicly exposed class 'EloquaLinkedService' had property 'version' added in the __init__ method in the current version
  - The model or publicly exposed class 'ExecuteDataFlowActivity' had property 'continuation_settings' added in the current version
  - The model or publicly exposed class 'ExecuteDataFlowActivityTypeProperties' had property 'continuation_settings' added in the current version
  - The model or publicly exposed class 'ExecutePowerQueryActivityTypeProperties' had property 'continuation_settings' added in the __init__ method in the current version
  - The model or publicly exposed class 'ExecuteWranglingDataflowActivity' had property 'continuation_settings' added in the current version
  - The model or publicly exposed class 'FileServerLinkedService' had property 'version' added in the __init__ method in the current version
  - The model or publicly exposed class 'FtpServerLinkedService' had property 'version' added in the __init__ method in the current version
  - The model or publicly exposed class 'GlobalParameterType' had property 'INT' added in the current version
  - The model or publicly exposed class 'GoogleAdWordsLinkedService' had property 'version' added in the __init__ method in the current version
  - The model or publicly exposed class 'GoogleBigQueryLinkedService' had property 'version' added in the __init__ method in the current version
  - The model or publicly exposed class 'GoogleBigQueryV2LinkedService' had property 'version' added in the __init__ method in the current version
  - The model or publicly exposed class 'GoogleCloudStorageLinkedService' had property 'version' added in the __init__ method in the current version
  - The model or publicly exposed class 'GoogleSheetsLinkedService' had property 'version' added in the __init__ method in the current version
  - The model or publicly exposed class 'GreenplumLinkedService' had property 'version' added in the __init__ method in the current version
  - The model or publicly exposed class 'HBaseLinkedService' had property 'version' added in the __init__ method in the current version
  - The model or publicly exposed class 'HDInsightLinkedService' had property 'version' added in the __init__ method in the current version
  - The model or publicly exposed class 'HDInsightOnDemandLinkedService' had property 'version_type_properties_version' added in the current version
  - The model or publicly exposed class 'HdfsLinkedService' had property 'version' added in the __init__ method in the current version
  - The model or publicly exposed class 'HiveLinkedService' had property 'version' added in the __init__ method in the current version
  - The model or publicly exposed class 'HttpLinkedService' had property 'version' added in the __init__ method in the current version
  - The model or publicly exposed class 'HubspotLinkedService' had property 'version' added in the __init__ method in the current version
  - The model or publicly exposed class 'ImpalaLinkedService' had property 'version' added in the __init__ method in the current version
  - The model or publicly exposed class 'InformixLinkedService' had property 'version' added in the __init__ method in the current version
  - The model or publicly exposed class 'JiraLinkedService' had property 'version' added in the __init__ method in the current version
  - The model or publicly exposed class 'LakeHouseLinkedService' had property 'version' added in the __init__ method in the current version
  - The model or publicly exposed class 'LinkedService' had property 'version' added in the current version
  - The model or publicly exposed class 'MagentoLinkedService' had property 'version' added in the __init__ method in the current version
  - The model or publicly exposed class 'MariaDBLinkedService' had property 'version' added in the __init__ method in the current version
  - The model or publicly exposed class 'MarketoLinkedService' had property 'version' added in the __init__ method in the current version
  - The model or publicly exposed class 'MicrosoftAccessLinkedService' had property 'version' added in the __init__ method in the current version
  - The model or publicly exposed class 'MongoDbAtlasLinkedService' had property 'version' added in the __init__ method in the current version
  - The model or publicly exposed class 'MongoDbLinkedService' had property 'version' added in the __init__ method in the current version
  - The model or publicly exposed class 'MongoDbV2LinkedService' had property 'version' added in the __init__ method in the current version
  - The model or publicly exposed class 'MySqlLinkedService' had property 'version' added in the __init__ method in the current version
  - The model or publicly exposed class 'NetezzaLinkedService' had property 'version' added in the __init__ method in the current version
  - The model or publicly exposed class 'NotebookParameterType' had property 'INT' added in the current version
  - The model or publicly exposed class 'ODataLinkedService' had property 'version' added in the __init__ method in the current version
  - The model or publicly exposed class 'OdbcLinkedService' had property 'version' added in the __init__ method in the current version
  - The model or publicly exposed class 'Office365LinkedService' had property 'version' added in the __init__ method in the current version
  - The model or publicly exposed class 'OracleCloudStorageLinkedService' had property 'version' added in the __init__ method in the current version
  - The model or publicly exposed class 'OracleLinkedService' had property 'version' added in the __init__ method in the current version
  - The model or publicly exposed class 'OracleServiceCloudLinkedService' had property 'version' added in the __init__ method in the current version
  - The model or publicly exposed class 'ParameterType' had property 'INT' added in the current version
  - The model or publicly exposed class 'PaypalLinkedService' had property 'version' added in the __init__ method in the current version
  - The model or publicly exposed class 'PhoenixLinkedService' had property 'version' added in the __init__ method in the current version
  - The model or publicly exposed class 'PostgreSqlLinkedService' had property 'version' added in the __init__ method in the current version
  - The model or publicly exposed class 'PostgreSqlV2LinkedService' had property 'version' added in the __init__ method in the current version
  - The model or publicly exposed class 'PrestoLinkedService' had property 'version' added in the __init__ method in the current version
  - The model or publicly exposed class 'QuickBooksLinkedService' had property 'version' added in the __init__ method in the current version
  - The model or publicly exposed class 'QuickbaseLinkedService' had property 'version' added in the __init__ method in the current version
  - The model or publicly exposed class 'ResponsysLinkedService' had property 'version' added in the __init__ method in the current version
  - The model or publicly exposed class 'RestServiceLinkedService' had property 'version' added in the __init__ method in the current version
  - The model or publicly exposed class 'RestServiceLinkedService' had property 'service_principal_credential_type' added in the current version
  - The model or publicly exposed class 'RestServiceLinkedService' had property 'service_principal_embedded_cert' added in the current version
  - The model or publicly exposed class 'RestServiceLinkedService' had property 'service_principal_embedded_cert_password' added in the current version
  - The model or publicly exposed class 'RunQueryFilterOperator' had property 'IN' added in the current version
  - The model or publicly exposed class 'SalesforceLinkedService' had property 'version' added in the __init__ method in the current version
  - The model or publicly exposed class 'SalesforceMarketingCloudLinkedService' had property 'version' added in the __init__ method in the current version
  - The model or publicly exposed class 'SalesforceServiceCloudLinkedService' had property 'version' added in the __init__ method in the current version
  - The model or publicly exposed class 'SalesforceServiceCloudV2LinkedService' had property 'version' added in the __init__ method in the current version
  - The model or publicly exposed class 'SalesforceV2LinkedService' had property 'version' added in the __init__ method in the current version
  - The model or publicly exposed class 'SapBWLinkedService' had property 'version' added in the __init__ method in the current version
  - The model or publicly exposed class 'SapCloudForCustomerLinkedService' had property 'version' added in the __init__ method in the current version
  - The model or publicly exposed class 'SapEccLinkedService' had property 'version' added in the __init__ method in the current version
  - The model or publicly exposed class 'SapHanaLinkedService' had property 'version' added in the __init__ method in the current version
  - The model or publicly exposed class 'SapOdpLinkedService' had property 'version' added in the __init__ method in the current version
  - The model or publicly exposed class 'SapOpenHubLinkedService' had property 'version' added in the __init__ method in the current version
  - The model or publicly exposed class 'SapTableLinkedService' had property 'version' added in the __init__ method in the current version
  - The model or publicly exposed class 'ServiceNowLinkedService' had property 'version' added in the __init__ method in the current version
  - The model or publicly exposed class 'ServiceNowV2LinkedService' had property 'version' added in the __init__ method in the current version
  - The model or publicly exposed class 'SftpServerLinkedService' had property 'version' added in the __init__ method in the current version
  - The model or publicly exposed class 'SharePointOnlineListLinkedService' had property 'version' added in the __init__ method in the current version
  - The model or publicly exposed class 'SharePointOnlineListLinkedService' had property 'service_principal_credential_type' added in the current version
  - The model or publicly exposed class 'SharePointOnlineListLinkedService' had property 'service_principal_embedded_cert' added in the current version
  - The model or publicly exposed class 'SharePointOnlineListLinkedService' had property 'service_principal_embedded_cert_password' added in the current version
  - The model or publicly exposed class 'ShopifyLinkedService' had property 'version' added in the __init__ method in the current version
  - The model or publicly exposed class 'SmartsheetLinkedService' had property 'version' added in the __init__ method in the current version
  - The model or publicly exposed class 'SnowflakeExportCopyCommand' had property 'storage_integration' added in the current version
  - The model or publicly exposed class 'SnowflakeImportCopyCommand' had property 'storage_integration' added in the current version
  - The model or publicly exposed class 'SnowflakeLinkedService' had property 'version' added in the __init__ method in the current version
  - The model or publicly exposed class 'SnowflakeV2LinkedService' had property 'version' added in the __init__ method in the current version
  - The model or publicly exposed class 'SparkLinkedService' had property 'version' added in the __init__ method in the current version
  - The model or publicly exposed class 'SqlServerAuthenticationType' had property 'USER_ASSIGNED_MANAGED_IDENTITY' added in the current version
  - The model or publicly exposed class 'SqlServerLinkedService' had property 'version' added in the __init__ method in the current version
  - The model or publicly exposed class 'SqlServerLinkedService' had property 'credential' added in the current version
  - The model or publicly exposed class 'SqlServerLinkedServiceTypeProperties' had property 'credential' added in the current version
  - The model or publicly exposed class 'SquareLinkedService' had property 'version' added in the __init__ method in the current version
  - The model or publicly exposed class 'StoredProcedureParameterType' had property 'INT' added in the current version
  - The model or publicly exposed class 'SybaseLinkedService' had property 'version' added in the __init__ method in the current version
  - The model or publicly exposed class 'TeamDeskLinkedService' had property 'version' added in the __init__ method in the current version
  - The model or publicly exposed class 'TeradataLinkedService' had property 'version' added in the __init__ method in the current version
  - The model or publicly exposed class 'TwilioLinkedService' had property 'version' added in the __init__ method in the current version
  - The model or publicly exposed class 'VerticaLinkedService' had property 'version' added in the __init__ method in the current version
  - The model or publicly exposed class 'VerticaLinkedService' had property 'server' added in the current version
  - The model or publicly exposed class 'VerticaLinkedService' had property 'port' added in the current version
  - The model or publicly exposed class 'VerticaLinkedService' had property 'uid' added in the current version
  - The model or publicly exposed class 'VerticaLinkedService' had property 'database' added in the current version
  - The model or publicly exposed class 'WarehouseLinkedService' had property 'version' added in the __init__ method in the current version
  - The model or publicly exposed class 'WebLinkedService' had property 'version' added in the __init__ method in the current version
  - The model or publicly exposed class 'XeroLinkedService' had property 'version' added in the __init__ method in the current version
  - The model or publicly exposed class 'ZendeskLinkedService' had property 'version' added in the __init__ method in the current version
  - The model or publicly exposed class 'ZohoLinkedService' had property 'version' added in the __init__ method in the current version
  - The model or publicly exposed class 'AzureStorageLinkedServiceTypeProperties' was added in the current version
  - The model or publicly exposed class 'AzureTableStorageLinkedServiceTypeProperties' was added in the current version
  - The model or publicly exposed class 'ContinuationSettingsReference' was added in the current version

### Breaking Changes

  - The 'GlobalParameterType' enum had its value 'INT_ENUM' deleted or renamed in the current version
  - The model or publicly exposed class 'HDInsightOnDemandLinkedService' had its instance variable 'version' deleted or renamed in the current version
  - The 'NotebookParameterType' enum had its value 'INT_ENUM' deleted or renamed in the current version
  - The 'ParameterType' enum had its value 'INT_ENUM' deleted or renamed in the current version
  - The 'RunQueryFilterOperator' enum had its value 'IN_ENUM' deleted or renamed in the current version
  - The 'StoredProcedureParameterType' enum had its value 'INT_ENUM' deleted or renamed in the current version

## 8.0.0 (2024-06-06)

### Features Added

  - Model DynamicsCrmLinkedService has a new parameter credential
  - Model ExpressionV2 has a new parameter operators
  - Model LakeHouseTableDataset has a new parameter schema_type_properties_schema
  - Model SalesforceServiceCloudV2Source has a new parameter query
  - Model SalesforceV2Source has a new parameter query

### Breaking Changes

  - Model ExpressionV2 no longer has parameter operator

## 7.1.0 (2024-05-08)

### Features Added

  - Model AmazonRdsForSqlServerLinkedService has a new parameter application_intent
  - Model AmazonRdsForSqlServerLinkedService has a new parameter authentication_type
  - Model AmazonRdsForSqlServerLinkedService has a new parameter command_timeout
  - Model AmazonRdsForSqlServerLinkedService has a new parameter connect_retry_count
  - Model AmazonRdsForSqlServerLinkedService has a new parameter connect_retry_interval
  - Model AmazonRdsForSqlServerLinkedService has a new parameter connect_timeout
  - Model AmazonRdsForSqlServerLinkedService has a new parameter database
  - Model AmazonRdsForSqlServerLinkedService has a new parameter encrypt
  - Model AmazonRdsForSqlServerLinkedService has a new parameter failover_partner
  - Model AmazonRdsForSqlServerLinkedService has a new parameter host_name_in_certificate
  - Model AmazonRdsForSqlServerLinkedService has a new parameter integrated_security
  - Model AmazonRdsForSqlServerLinkedService has a new parameter load_balance_timeout
  - Model AmazonRdsForSqlServerLinkedService has a new parameter max_pool_size
  - Model AmazonRdsForSqlServerLinkedService has a new parameter min_pool_size
  - Model AmazonRdsForSqlServerLinkedService has a new parameter multi_subnet_failover
  - Model AmazonRdsForSqlServerLinkedService has a new parameter multiple_active_result_sets
  - Model AmazonRdsForSqlServerLinkedService has a new parameter packet_size
  - Model AmazonRdsForSqlServerLinkedService has a new parameter pooling
  - Model AmazonRdsForSqlServerLinkedService has a new parameter server
  - Model AmazonRdsForSqlServerLinkedService has a new parameter trust_server_certificate
  - Model AzureSqlDWLinkedService has a new parameter application_intent
  - Model AzureSqlDWLinkedService has a new parameter authentication_type
  - Model AzureSqlDWLinkedService has a new parameter command_timeout
  - Model AzureSqlDWLinkedService has a new parameter connect_retry_count
  - Model AzureSqlDWLinkedService has a new parameter connect_retry_interval
  - Model AzureSqlDWLinkedService has a new parameter connect_timeout
  - Model AzureSqlDWLinkedService has a new parameter database
  - Model AzureSqlDWLinkedService has a new parameter encrypt
  - Model AzureSqlDWLinkedService has a new parameter failover_partner
  - Model AzureSqlDWLinkedService has a new parameter host_name_in_certificate
  - Model AzureSqlDWLinkedService has a new parameter integrated_security
  - Model AzureSqlDWLinkedService has a new parameter load_balance_timeout
  - Model AzureSqlDWLinkedService has a new parameter max_pool_size
  - Model AzureSqlDWLinkedService has a new parameter min_pool_size
  - Model AzureSqlDWLinkedService has a new parameter multi_subnet_failover
  - Model AzureSqlDWLinkedService has a new parameter multiple_active_result_sets
  - Model AzureSqlDWLinkedService has a new parameter packet_size
  - Model AzureSqlDWLinkedService has a new parameter pooling
  - Model AzureSqlDWLinkedService has a new parameter server
  - Model AzureSqlDWLinkedService has a new parameter service_principal_credential
  - Model AzureSqlDWLinkedService has a new parameter service_principal_credential_type
  - Model AzureSqlDWLinkedService has a new parameter trust_server_certificate
  - Model AzureSqlDWLinkedService has a new parameter user_name
  - Model AzureSqlDatabaseLinkedService has a new parameter application_intent
  - Model AzureSqlDatabaseLinkedService has a new parameter authentication_type
  - Model AzureSqlDatabaseLinkedService has a new parameter command_timeout
  - Model AzureSqlDatabaseLinkedService has a new parameter connect_retry_count
  - Model AzureSqlDatabaseLinkedService has a new parameter connect_retry_interval
  - Model AzureSqlDatabaseLinkedService has a new parameter connect_timeout
  - Model AzureSqlDatabaseLinkedService has a new parameter database
  - Model AzureSqlDatabaseLinkedService has a new parameter encrypt
  - Model AzureSqlDatabaseLinkedService has a new parameter failover_partner
  - Model AzureSqlDatabaseLinkedService has a new parameter host_name_in_certificate
  - Model AzureSqlDatabaseLinkedService has a new parameter integrated_security
  - Model AzureSqlDatabaseLinkedService has a new parameter load_balance_timeout
  - Model AzureSqlDatabaseLinkedService has a new parameter max_pool_size
  - Model AzureSqlDatabaseLinkedService has a new parameter min_pool_size
  - Model AzureSqlDatabaseLinkedService has a new parameter multi_subnet_failover
  - Model AzureSqlDatabaseLinkedService has a new parameter multiple_active_result_sets
  - Model AzureSqlDatabaseLinkedService has a new parameter packet_size
  - Model AzureSqlDatabaseLinkedService has a new parameter pooling
  - Model AzureSqlDatabaseLinkedService has a new parameter server
  - Model AzureSqlDatabaseLinkedService has a new parameter service_principal_credential
  - Model AzureSqlDatabaseLinkedService has a new parameter service_principal_credential_type
  - Model AzureSqlDatabaseLinkedService has a new parameter trust_server_certificate
  - Model AzureSqlDatabaseLinkedService has a new parameter user_name
  - Model AzureSqlMILinkedService has a new parameter application_intent
  - Model AzureSqlMILinkedService has a new parameter authentication_type
  - Model AzureSqlMILinkedService has a new parameter command_timeout
  - Model AzureSqlMILinkedService has a new parameter connect_retry_count
  - Model AzureSqlMILinkedService has a new parameter connect_retry_interval
  - Model AzureSqlMILinkedService has a new parameter connect_timeout
  - Model AzureSqlMILinkedService has a new parameter database
  - Model AzureSqlMILinkedService has a new parameter encrypt
  - Model AzureSqlMILinkedService has a new parameter failover_partner
  - Model AzureSqlMILinkedService has a new parameter host_name_in_certificate
  - Model AzureSqlMILinkedService has a new parameter integrated_security
  - Model AzureSqlMILinkedService has a new parameter load_balance_timeout
  - Model AzureSqlMILinkedService has a new parameter max_pool_size
  - Model AzureSqlMILinkedService has a new parameter min_pool_size
  - Model AzureSqlMILinkedService has a new parameter multi_subnet_failover
  - Model AzureSqlMILinkedService has a new parameter multiple_active_result_sets
  - Model AzureSqlMILinkedService has a new parameter packet_size
  - Model AzureSqlMILinkedService has a new parameter pooling
  - Model AzureSqlMILinkedService has a new parameter server
  - Model AzureSqlMILinkedService has a new parameter service_principal_credential
  - Model AzureSqlMILinkedService has a new parameter service_principal_credential_type
  - Model AzureSqlMILinkedService has a new parameter trust_server_certificate
  - Model AzureSqlMILinkedService has a new parameter user_name
  - Model ManagedIdentityCredential has a new parameter resource_id
  - Model SqlServerLinkedService has a new parameter application_intent
  - Model SqlServerLinkedService has a new parameter authentication_type
  - Model SqlServerLinkedService has a new parameter command_timeout
  - Model SqlServerLinkedService has a new parameter connect_retry_count
  - Model SqlServerLinkedService has a new parameter connect_retry_interval
  - Model SqlServerLinkedService has a new parameter connect_timeout
  - Model SqlServerLinkedService has a new parameter database
  - Model SqlServerLinkedService has a new parameter encrypt
  - Model SqlServerLinkedService has a new parameter failover_partner
  - Model SqlServerLinkedService has a new parameter host_name_in_certificate
  - Model SqlServerLinkedService has a new parameter integrated_security
  - Model SqlServerLinkedService has a new parameter load_balance_timeout
  - Model SqlServerLinkedService has a new parameter max_pool_size
  - Model SqlServerLinkedService has a new parameter min_pool_size
  - Model SqlServerLinkedService has a new parameter multi_subnet_failover
  - Model SqlServerLinkedService has a new parameter multiple_active_result_sets
  - Model SqlServerLinkedService has a new parameter packet_size
  - Model SqlServerLinkedService has a new parameter pooling
  - Model SqlServerLinkedService has a new parameter server
  - Model SqlServerLinkedService has a new parameter trust_server_certificate

## 7.0.0 (2024-04-22)

### Breaking Changes

  - Model ManagedIdentityCredential no longer has parameter resource_id

## 6.1.0 (2024-03-18)

### Features Added

  - Added model ExpressionV2
  - Added model ExpressionV2Type
  - Added model GoogleBigQueryV2AuthenticationType
  - Added model GoogleBigQueryV2LinkedService
  - Added model GoogleBigQueryV2ObjectDataset
  - Added model GoogleBigQueryV2Source
  - Added model PostgreSqlV2LinkedService
  - Added model PostgreSqlV2Source
  - Added model PostgreSqlV2TableDataset
  - Added model ServiceNowV2AuthenticationType
  - Added model ServiceNowV2LinkedService
  - Added model ServiceNowV2ObjectDataset
  - Added model ServiceNowV2Source

## 6.0.0 (2024-03-04)

### Features Added

  - Model SalesforceServiceCloudV2LinkedService has a new parameter authentication_type
  - Model SalesforceServiceCloudV2Source has a new parameter include_deleted_objects
  - Model SalesforceV2LinkedService has a new parameter authentication_type
  - Model SalesforceV2Source has a new parameter include_deleted_objects

### Breaking Changes

  - Model SalesforceServiceCloudV2Source no longer has parameter read_behavior
  - Model SalesforceV2Source no longer has parameter read_behavior

## 5.0.0 (2024-01-26)

### Features Added

  - Model AzureBlobFSWriteSettings has a new parameter metadata
  - Model AzureBlobStorageWriteSettings has a new parameter metadata
  - Model AzureDataLakeStoreWriteSettings has a new parameter metadata
  - Model AzureFileStorageWriteSettings has a new parameter metadata
  - Model FileServerWriteSettings has a new parameter metadata
  - Model LakeHouseWriteSettings has a new parameter metadata
  - Model MariaDBLinkedService has a new parameter database
  - Model MariaDBLinkedService has a new parameter driver_version
  - Model MariaDBLinkedService has a new parameter password
  - Model MariaDBLinkedService has a new parameter port
  - Model MariaDBLinkedService has a new parameter server
  - Model MariaDBLinkedService has a new parameter username
  - Model MySqlLinkedService has a new parameter database
  - Model MySqlLinkedService has a new parameter driver_version
  - Model MySqlLinkedService has a new parameter port
  - Model MySqlLinkedService has a new parameter server
  - Model MySqlLinkedService has a new parameter ssl_mode
  - Model MySqlLinkedService has a new parameter use_system_trust_store
  - Model MySqlLinkedService has a new parameter username
  - Model SftpWriteSettings has a new parameter metadata
  - Model StoreWriteSettings has a new parameter metadata
  - Model WebActivity has a new parameter http_request_timeout
  - Model WebActivity has a new parameter turn_off_async

### Breaking Changes

  - Model MariaDBLinkedService no longer has parameter pwd

## 4.0.0 (2023-11-20)

### Features Added

  - Added operation group ChangeDataCaptureOperations
  - Model Activity has a new parameter on_inactive_mark_as
  - Model Activity has a new parameter state
  - Model AmazonRdsForSqlServerSource has a new parameter isolation_level
  - Model AppendVariableActivity has a new parameter on_inactive_mark_as
  - Model AppendVariableActivity has a new parameter state
  - Model AzureDataExplorerCommandActivity has a new parameter on_inactive_mark_as
  - Model AzureDataExplorerCommandActivity has a new parameter state
  - Model AzureFunctionActivity has a new parameter on_inactive_mark_as
  - Model AzureFunctionActivity has a new parameter state
  - Model AzureMLBatchExecutionActivity has a new parameter on_inactive_mark_as
  - Model AzureMLBatchExecutionActivity has a new parameter state
  - Model AzureMLExecutePipelineActivity has a new parameter on_inactive_mark_as
  - Model AzureMLExecutePipelineActivity has a new parameter state
  - Model AzureMLServiceLinkedService has a new parameter authentication
  - Model AzureMLUpdateResourceActivity has a new parameter on_inactive_mark_as
  - Model AzureMLUpdateResourceActivity has a new parameter state
  - Model AzureSqlSource has a new parameter isolation_level
  - Model ControlActivity has a new parameter on_inactive_mark_as
  - Model ControlActivity has a new parameter state
  - Model CopyActivity has a new parameter on_inactive_mark_as
  - Model CopyActivity has a new parameter state
  - Model CustomActivity has a new parameter on_inactive_mark_as
  - Model CustomActivity has a new parameter state
  - Model DataLakeAnalyticsUSQLActivity has a new parameter on_inactive_mark_as
  - Model DataLakeAnalyticsUSQLActivity has a new parameter state
  - Model DatabricksNotebookActivity has a new parameter on_inactive_mark_as
  - Model DatabricksNotebookActivity has a new parameter state
  - Model DatabricksSparkJarActivity has a new parameter on_inactive_mark_as
  - Model DatabricksSparkJarActivity has a new parameter state
  - Model DatabricksSparkPythonActivity has a new parameter on_inactive_mark_as
  - Model DatabricksSparkPythonActivity has a new parameter state
  - Model DeleteActivity has a new parameter on_inactive_mark_as
  - Model DeleteActivity has a new parameter state
  - Model ExecuteDataFlowActivity has a new parameter on_inactive_mark_as
  - Model ExecuteDataFlowActivity has a new parameter state
  - Model ExecutePipelineActivity has a new parameter on_inactive_mark_as
  - Model ExecutePipelineActivity has a new parameter state
  - Model ExecuteSSISPackageActivity has a new parameter on_inactive_mark_as
  - Model ExecuteSSISPackageActivity has a new parameter state
  - Model ExecuteWranglingDataflowActivity has a new parameter on_inactive_mark_as
  - Model ExecuteWranglingDataflowActivity has a new parameter state
  - Model ExecutionActivity has a new parameter on_inactive_mark_as
  - Model ExecutionActivity has a new parameter state
  - Model FailActivity has a new parameter on_inactive_mark_as
  - Model FailActivity has a new parameter state
  - Model FilterActivity has a new parameter on_inactive_mark_as
  - Model FilterActivity has a new parameter state
  - Model ForEachActivity has a new parameter on_inactive_mark_as
  - Model ForEachActivity has a new parameter state
  - Model GetMetadataActivity has a new parameter on_inactive_mark_as
  - Model GetMetadataActivity has a new parameter state
  - Model GoogleAdWordsLinkedService has a new parameter google_ads_api_version
  - Model GoogleAdWordsLinkedService has a new parameter login_customer_id
  - Model GoogleAdWordsLinkedService has a new parameter private_key
  - Model GoogleAdWordsLinkedService has a new parameter support_legacy_data_types
  - Model HDInsightHiveActivity has a new parameter on_inactive_mark_as
  - Model HDInsightHiveActivity has a new parameter state
  - Model HDInsightMapReduceActivity has a new parameter on_inactive_mark_as
  - Model HDInsightMapReduceActivity has a new parameter state
  - Model HDInsightPigActivity has a new parameter on_inactive_mark_as
  - Model HDInsightPigActivity has a new parameter state
  - Model HDInsightSparkActivity has a new parameter on_inactive_mark_as
  - Model HDInsightSparkActivity has a new parameter state
  - Model HDInsightStreamingActivity has a new parameter on_inactive_mark_as
  - Model HDInsightStreamingActivity has a new parameter state
  - Model HttpReadSettings has a new parameter additional_columns
  - Model IfConditionActivity has a new parameter on_inactive_mark_as
  - Model IfConditionActivity has a new parameter state
  - Model IntegrationRuntimeDataFlowProperties has a new parameter custom_properties
  - Model LookupActivity has a new parameter on_inactive_mark_as
  - Model LookupActivity has a new parameter state
  - Model MongoDbAtlasLinkedService has a new parameter driver_version
  - Model ParquetSource has a new parameter format_settings
  - Model PipelineExternalComputeScaleProperties has a new parameter number_of_external_nodes
  - Model PipelineExternalComputeScaleProperties has a new parameter number_of_pipeline_nodes
  - Model ScriptActivity has a new parameter on_inactive_mark_as
  - Model ScriptActivity has a new parameter state
  - Model SelfHostedIntegrationRuntime has a new parameter self_contained_interactive_authoring_enabled
  - Model SelfHostedIntegrationRuntimeStatus has a new parameter self_contained_interactive_authoring_enabled
  - Model SetVariableActivity has a new parameter on_inactive_mark_as
  - Model SetVariableActivity has a new parameter policy
  - Model SetVariableActivity has a new parameter set_system_variable
  - Model SetVariableActivity has a new parameter state
  - Model SqlDWSource has a new parameter isolation_level
  - Model SqlMISource has a new parameter isolation_level
  - Model SqlServerSource has a new parameter isolation_level
  - Model SqlServerStoredProcedureActivity has a new parameter on_inactive_mark_as
  - Model SqlServerStoredProcedureActivity has a new parameter state
  - Model SwitchActivity has a new parameter on_inactive_mark_as
  - Model SwitchActivity has a new parameter state
  - Model SynapseNotebookActivity has a new parameter configuration_type
  - Model SynapseNotebookActivity has a new parameter on_inactive_mark_as
  - Model SynapseNotebookActivity has a new parameter spark_config
  - Model SynapseNotebookActivity has a new parameter state
  - Model SynapseNotebookActivity has a new parameter target_spark_configuration
  - Model SynapseSparkJobDefinitionActivity has a new parameter on_inactive_mark_as
  - Model SynapseSparkJobDefinitionActivity has a new parameter state
  - Model UntilActivity has a new parameter on_inactive_mark_as
  - Model UntilActivity has a new parameter state
  - Model ValidationActivity has a new parameter on_inactive_mark_as
  - Model ValidationActivity has a new parameter state
  - Model WaitActivity has a new parameter on_inactive_mark_as
  - Model WaitActivity has a new parameter state
  - Model WebActivity has a new parameter on_inactive_mark_as
  - Model WebActivity has a new parameter state
  - Model WebHookActivity has a new parameter on_inactive_mark_as
  - Model WebHookActivity has a new parameter policy
  - Model WebHookActivity has a new parameter state

### Breaking Changes

  - Model HttpReadSettings no longer has parameter enable_partition_discovery
  - Model HttpReadSettings no longer has parameter partition_root_path

## 3.1.0 (2023-03-20)

### Features Added

  - Model AzureBlobFSLinkedService has a new parameter sas_token
  - Model AzureBlobFSLinkedService has a new parameter sas_uri

## 3.0.0 (2023-02-20)

### Features Added

  - Added operation group CredentialOperationsOperations
  - Model AzureBlobStorageLinkedService has a new parameter authentication_type
  - Model AzureBlobStorageLinkedService has a new parameter container_uri
  - Model IntegrationRuntimeComputeProperties has a new parameter copy_compute_scale_properties
  - Model IntegrationRuntimeComputeProperties has a new parameter pipeline_external_compute_scale_properties
  - Model SynapseSparkJobDefinitionActivity has a new parameter configuration_type
  - Model SynapseSparkJobDefinitionActivity has a new parameter scan_folder
  - Model SynapseSparkJobDefinitionActivity has a new parameter spark_config
  - Model SynapseSparkJobDefinitionActivity has a new parameter target_spark_configuration

### Breaking Changes

  - Parameter export_settings of model SnowflakeSource is now required

## 2.10.0 (2022-11-22)

### Features Added

  - Model ScriptActivity has a new parameter script_block_execution_timeout

## 2.9.0 (2022-10-24)

### Features Added

  - Model AzureSynapseArtifactsLinkedService has a new parameter workspace_resource_id
  - Model FactoryGitHubConfiguration has a new parameter disable_publish
  - Model FactoryRepoConfiguration has a new parameter disable_publish
  - Model FactoryVSTSConfiguration has a new parameter disable_publish
  - Model SynapseSparkJobDefinitionActivity has a new parameter files_v2
  - Model SynapseSparkJobDefinitionActivity has a new parameter python_code_reference

## 2.8.1 (2022-10-17)

### Other Changes

  - Changed type of stored_procedure_parameters to json-like object

## 2.8.0 (2022-09-13)

### Features Added

  - Added model AzureSynapseArtifactsLinkedService
  - Added model BigDataPoolParametrizationReference
  - Added model BigDataPoolReferenceType
  - Added model DatasetReferenceType
  - Added model ExpressionType
  - Added model GoogleSheetsLinkedService
  - Added model IntegrationRuntimeReferenceType
  - Added model NotebookParameter
  - Added model NotebookParameterType
  - Added model NotebookReferenceType
  - Added model PipelineReferenceType
  - Added model SparkJobReferenceType
  - Added model SynapseNotebookActivity
  - Added model SynapseNotebookReference
  - Added model SynapseSparkJobDefinitionActivity
  - Added model SynapseSparkJobReference
  - Added model Type

## 2.7.0 (2022-06-15)

**Features**

  - Model RestServiceLinkedService has a new parameter client_id
  - Model RestServiceLinkedService has a new parameter client_secret
  - Model RestServiceLinkedService has a new parameter resource
  - Model RestServiceLinkedService has a new parameter scope
  - Model RestServiceLinkedService has a new parameter token_endpoint

## 2.6.0 (2022-05-27)

**Features**

  - Added operation group GlobalParametersOperations
  - Model DataFlowSink has a new parameter rejected_data_linked_service
  - Model ExecuteDataFlowActivity has a new parameter source_staging_concurrency
  - Model ExecuteDataFlowActivityTypeProperties has a new parameter source_staging_concurrency
  - Model ExecutePowerQueryActivityTypeProperties has a new parameter source_staging_concurrency
  - Model ExecuteWranglingDataflowActivity has a new parameter source_staging_concurrency
  - Model Factory has a new parameter purview_configuration
  - Model PowerQuerySink has a new parameter rejected_data_linked_service

## 2.5.0 (2022-05-12)

**Features**

  - Model PrivateLinkConnectionApprovalRequest has a new parameter private_endpoint

## 2.4.0 (2022-04-15)

**Features**

  - Model ExecutePipelineActivity has a new parameter policy
  - Model WebActivity has a new parameter disable_cert_validation

## 2.3.0 (2022-03-02)

**Features**

  - Added model QuickbaseLinkedService
  - Added model ScriptActivity
  - Added model ScriptActivityLogDestination
  - Added model ScriptActivityParameter
  - Added model ScriptActivityParameterDirection
  - Added model ScriptActivityParameterType
  - Added model ScriptActivityScriptBlock
  - Added model ScriptActivityTypePropertiesLogSettings
  - Added model ScriptType
  - Added model SmartsheetLinkedService
  - Added model TeamDeskAuthenticationType
  - Added model TeamDeskLinkedService
  - Added model ZendeskAuthenticationType
  - Added model ZendeskLinkedService

## 2.2.1 (2022-02-14)

**Fixes**
  - Fix parameter public_network_access mapping type in Model FactoryUpdateParameters

## 2.2.0 (2022-01-06)

**Features**

  - Model AzureBlobFSLinkedService has a new parameter service_principal_credential
  - Model AzureBlobFSLinkedService has a new parameter service_principal_credential_type
  - Model AzureDatabricksDeltaLakeLinkedService has a new parameter credential
  - Model AzureDatabricksDeltaLakeLinkedService has a new parameter workspace_resource_id
  - Model CosmosDbLinkedService has a new parameter credential
  - Model DynamicsLinkedService has a new parameter credential
  - Model GoogleAdWordsLinkedService has a new parameter connection_properties
  - Model LinkedIntegrationRuntimeRbacAuthorization has a new parameter credential

## 2.1.0 (2021-11-20)

**Features**

  - Model PowerQuerySink has a new parameter flowlet
  - Model DatasetCompression has a new parameter level
  - Model SftpReadSettings has a new parameter disable_chunking
  - Model DataFlowSink has a new parameter flowlet
  - Model PowerQuerySource has a new parameter flowlet
  - Model Transformation has a new parameter linked_service
  - Model Transformation has a new parameter dataset
  - Model Transformation has a new parameter flowlet
  - Model DataFlowDebugPackage has a new parameter data_flows
  - Model FtpReadSettings has a new parameter disable_chunking
  - Model MappingDataFlow has a new parameter script_lines
  - Model DataFlowReference has a new parameter parameters
  - Model DataFlowSource has a new parameter flowlet

## 2.0.0 (2021-10-09)

**Features**

  - Model HubspotSource has a new parameter disable_metrics_collection
  - Model SquareSource has a new parameter disable_metrics_collection
  - Model SqlDWSink has a new parameter upsert_settings
  - Model SqlDWSink has a new parameter disable_metrics_collection
  - Model SqlDWSink has a new parameter write_behavior
  - Model SqlDWSink has a new parameter sql_writer_use_table_lock
  - Model GoogleAdWordsSource has a new parameter disable_metrics_collection
  - Model SparkSource has a new parameter disable_metrics_collection
  - Model GoogleCloudStorageReadSettings has a new parameter disable_metrics_collection
  - Model MongoDbV2Source has a new parameter disable_metrics_collection
  - Model CopySource has a new parameter disable_metrics_collection
  - Model BinarySink has a new parameter disable_metrics_collection
  - Model FactoryGitHubConfiguration has a new parameter client_id
  - Model FactoryGitHubConfiguration has a new parameter client_secret
  - Model DrillSource has a new parameter disable_metrics_collection
  - Model OracleCloudStorageReadSettings has a new parameter disable_metrics_collection
  - Model AzureBlobFSSource has a new parameter disable_metrics_collection
  - Model ShopifySource has a new parameter disable_metrics_collection
  - Model AzureBlobStorageLinkedService has a new parameter credential
  - Model StoreReadSettings has a new parameter disable_metrics_collection
  - Model SalesforceMarketingCloudSource has a new parameter disable_metrics_collection
  - Model AzureBlobFSReadSettings has a new parameter disable_metrics_collection
  - Model HiveSource has a new parameter disable_metrics_collection
  - Model VerticaSource has a new parameter disable_metrics_collection
  - Model AzureDataExplorerSource has a new parameter disable_metrics_collection
  - Model SapEccSource has a new parameter disable_metrics_collection
  - Model GreenplumSource has a new parameter disable_metrics_collection
  - Model HDInsightOnDemandLinkedService has a new parameter credential
  - Model AzureDataExplorerSink has a new parameter disable_metrics_collection
  - Model AzureBlobStorageReadSettings has a new parameter disable_metrics_collection
  - Model OrcSink has a new parameter disable_metrics_collection
  - Model HBaseSource has a new parameter disable_metrics_collection
  - Model CopySink has a new parameter disable_metrics_collection
  - Model SapTableSource has a new parameter disable_metrics_collection
  - Model SqlMISink has a new parameter upsert_settings
  - Model SqlMISink has a new parameter disable_metrics_collection
  - Model SqlMISink has a new parameter write_behavior
  - Model SqlMISink has a new parameter sql_writer_use_table_lock
  - Model ZohoSource has a new parameter disable_metrics_collection
  - Model RestSource has a new parameter disable_metrics_collection
  - Model InformixSink has a new parameter disable_metrics_collection
  - Model MicrosoftAccessSink has a new parameter disable_metrics_collection
  - Model DelimitedTextSink has a new parameter disable_metrics_collection
  - Model StoreWriteSettings has a new parameter disable_metrics_collection
  - Model JiraSource has a new parameter disable_metrics_collection
  - Model DocumentDbCollectionSource has a new parameter disable_metrics_collection
  - Model SqlSink has a new parameter upsert_settings
  - Model SqlSink has a new parameter disable_metrics_collection
  - Model SqlSink has a new parameter write_behavior
  - Model SqlSink has a new parameter sql_writer_use_table_lock
  - Model AzureDatabricksLinkedService has a new parameter credential
  - Model SnowflakeSink has a new parameter disable_metrics_collection
  - Model AzureQueueSink has a new parameter disable_metrics_collection
  - Model SalesforceServiceCloudSink has a new parameter disable_metrics_collection
  - Model SapBwSource has a new parameter disable_metrics_collection
  - Model DynamicsAXSource has a new parameter disable_metrics_collection
  - Model SftpWriteSettings has a new parameter disable_metrics_collection
  - Model WebActivityAuthentication has a new parameter credential
  - Model CassandraSource has a new parameter disable_metrics_collection
  - Model HdfsReadSettings has a new parameter disable_metrics_collection
  - Model SqlMISource has a new parameter disable_metrics_collection
  - Model RestServiceLinkedService has a new parameter credential
  - Model Db2Source has a new parameter disable_metrics_collection
  - Model SqlServerLinkedService has a new parameter always_encrypted_settings
  - Model SalesforceSink has a new parameter disable_metrics_collection
  - Model HdfsSource has a new parameter disable_metrics_collection
  - Model ConcurSource has a new parameter disable_metrics_collection
  - Model ParquetSink has a new parameter disable_metrics_collection
  - Model AzureBlobFSLinkedService has a new parameter credential
  - Model MongoDbAtlasSource has a new parameter disable_metrics_collection
  - Model SapHanaSource has a new parameter disable_metrics_collection
  - Model AzureDataLakeStoreWriteSettings has a new parameter disable_metrics_collection
  - Model DocumentDbCollectionSink has a new parameter disable_metrics_collection
  - Model GitHubAccessTokenRequest has a new parameter git_hub_client_secret
  - Model AzureTableSink has a new parameter disable_metrics_collection
  - Model HttpReadSettings has a new parameter disable_metrics_collection
  - Model MongoDbSource has a new parameter disable_metrics_collection
  - Model AzureDataLakeStoreSource has a new parameter disable_metrics_collection
  - Model AzureSqlSource has a new parameter disable_metrics_collection
  - Model OracleServiceCloudSource has a new parameter disable_metrics_collection
  - Model AzureTableSource has a new parameter disable_metrics_collection
  - Model AzureSqlMILinkedService has a new parameter always_encrypted_settings
  - Model AzureSqlMILinkedService has a new parameter credential
  - Model CouchbaseSource has a new parameter disable_metrics_collection
  - Model AzureBatchLinkedService has a new parameter credential
  - Model QuickBooksSource has a new parameter disable_metrics_collection
  - Model CommonDataServiceForAppsSink has a new parameter disable_metrics_collection
  - Model MicrosoftAccessSource has a new parameter disable_metrics_collection
  - Model HttpSource has a new parameter disable_metrics_collection
  - Model BlobSource has a new parameter disable_metrics_collection
  - Model PipelineRunInvokedBy has a new parameter pipeline_name
  - Model PipelineRunInvokedBy has a new parameter pipeline_run_id
  - Model FactoryUpdateParameters has a new parameter public_network_access
  - Model ODataSource has a new parameter disable_metrics_collection
  - Model SapCloudForCustomerSource has a new parameter disable_metrics_collection
  - Model PostgreSqlSource has a new parameter disable_metrics_collection
  - Model AzureFileStorageReadSettings has a new parameter disable_metrics_collection
  - Model TabularSource has a new parameter disable_metrics_collection
  - Model AzurePostgreSqlSource has a new parameter disable_metrics_collection
  - Model AzureBlobFSWriteSettings has a new parameter disable_metrics_collection
  - Model AzureSearchIndexSink has a new parameter disable_metrics_collection
  - Model IntegrationRuntimeVNetProperties has a new parameter subnet_id
  - Model ManagedIntegrationRuntime has a new parameter customer_virtual_network
  - Model WebSource has a new parameter disable_metrics_collection
  - Model DelimitedTextSource has a new parameter disable_metrics_collection
  - Model AmazonS3CompatibleReadSettings has a new parameter disable_metrics_collection
  - Model GoogleBigQuerySource has a new parameter disable_metrics_collection
  - Model OracleSource has a new parameter disable_metrics_collection
  - Model AzureDataLakeStoreSink has a new parameter disable_metrics_collection
  - Model DynamicsSink has a new parameter disable_metrics_collection
  - Model SalesforceSource has a new parameter disable_metrics_collection
  - Model SalesforceServiceCloudSource has a new parameter disable_metrics_collection
  - Model AzureMLLinkedService has a new parameter authentication
  - Model AzureFunctionLinkedService has a new parameter authentication
  - Model AzureFunctionLinkedService has a new parameter resource_id
  - Model AzureFunctionLinkedService has a new parameter credential
  - Model CosmosDbSqlApiSource has a new parameter disable_metrics_collection
  - Model XmlSource has a new parameter disable_metrics_collection
  - Model XeroSource has a new parameter disable_metrics_collection
  - Model ParquetSource has a new parameter disable_metrics_collection
  - Model JsonSink has a new parameter disable_metrics_collection
  - Model MySqlSource has a new parameter disable_metrics_collection
  - Model AzureBlobStorageWriteSettings has a new parameter disable_metrics_collection
  - Model Office365Source has a new parameter disable_metrics_collection
  - Model AzureBlobFSSink has a new parameter disable_metrics_collection
  - Model AzureBlobFSSink has a new parameter metadata
  - Model BlobSink has a new parameter disable_metrics_collection
  - Model BlobSink has a new parameter metadata
  - Model MariaDBSource has a new parameter disable_metrics_collection
  - Model OdbcSource has a new parameter disable_metrics_collection
  - Model DynamicsSource has a new parameter disable_metrics_collection
  - Model ExcelDataset has a new parameter sheet_index
  - Model TeradataSource has a new parameter disable_metrics_collection
  - Model InformixSource has a new parameter disable_metrics_collection
  - Model CosmosDbMongoDbApiLinkedService has a new parameter is_server_version_above32
  - Model DynamicsCrmSink has a new parameter disable_metrics_collection
  - Model AmazonS3ReadSettings has a new parameter disable_metrics_collection
  - Model SqlDWSource has a new parameter disable_metrics_collection
  - Model AzureSqlDWLinkedService has a new parameter credential
  - Model FtpReadSettings has a new parameter disable_metrics_collection
  - Model AzureDatabricksDeltaLakeSource has a new parameter disable_metrics_collection
  - Model EloquaSource has a new parameter disable_metrics_collection
  - Model AzureMySqlSink has a new parameter disable_metrics_collection
  - Model CosmosDbMongoDbApiSource has a new parameter disable_metrics_collection
  - Model AmazonMWSSource has a new parameter disable_metrics_collection
  - Model MarketoSource has a new parameter disable_metrics_collection
  - Model CommonDataServiceForAppsSource has a new parameter disable_metrics_collection
  - Model AvroSource has a new parameter disable_metrics_collection
  - Model AzureSqlSink has a new parameter upsert_settings
  - Model AzureSqlSink has a new parameter disable_metrics_collection
  - Model AzureSqlSink has a new parameter write_behavior
  - Model AzureSqlSink has a new parameter sql_writer_use_table_lock
  - Model AzureFileStorageWriteSettings has a new parameter disable_metrics_collection
  - Model PrestoSource has a new parameter disable_metrics_collection
  - Model BinarySource has a new parameter disable_metrics_collection
  - Model AzureDataExplorerLinkedService has a new parameter credential
  - Model ResponsysSource has a new parameter disable_metrics_collection
  - Model ImpalaSource has a new parameter disable_metrics_collection
  - Model FileServerReadSettings has a new parameter disable_metrics_collection
  - Model SqlServerSink has a new parameter upsert_settings
  - Model SqlServerSink has a new parameter disable_metrics_collection
  - Model SqlServerSink has a new parameter write_behavior
  - Model SqlServerSink has a new parameter sql_writer_use_table_lock
  - Model SapOpenHubSource has a new parameter disable_metrics_collection
  - Model AzurePostgreSqlSink has a new parameter disable_metrics_collection
  - Model FileSystemSource has a new parameter disable_metrics_collection
  - Model OracleSink has a new parameter disable_metrics_collection
  - Model AzureSqlDatabaseLinkedService has a new parameter always_encrypted_settings
  - Model AzureSqlDatabaseLinkedService has a new parameter credential
  - Model PhoenixSource has a new parameter disable_metrics_collection
  - Model AzureMariaDBSource has a new parameter disable_metrics_collection
  - Model OdbcSink has a new parameter disable_metrics_collection
  - Model SharePointOnlineListSource has a new parameter disable_metrics_collection
  - Model FileSystemSink has a new parameter disable_metrics_collection
  - Model RestSink has a new parameter disable_metrics_collection
  - Model DynamicsCrmSource has a new parameter disable_metrics_collection
  - Model AzureDataLakeStoreReadSettings has a new parameter disable_metrics_collection
  - Model OrcSource has a new parameter disable_metrics_collection
  - Model FileServerWriteSettings has a new parameter disable_metrics_collection
  - Model AvroSink has a new parameter disable_metrics_collection
  - Model CosmosDbSqlApiSink has a new parameter disable_metrics_collection
  - Model SapCloudForCustomerSink has a new parameter disable_metrics_collection
  - Model AmazonRedshiftSource has a new parameter disable_metrics_collection
  - Model SybaseSource has a new parameter disable_metrics_collection
  - Model PaypalSource has a new parameter disable_metrics_collection
  - Model AzureKeyVaultLinkedService has a new parameter credential
  - Model SqlServerSource has a new parameter disable_metrics_collection
  - Model IntegrationRuntimeSsisProperties has a new parameter credential
  - Model SftpReadSettings has a new parameter disable_metrics_collection
  - Model SnowflakeSource has a new parameter disable_metrics_collection
  - Model RelationalSource has a new parameter disable_metrics_collection
  - Model IntegrationRuntimeDataFlowProperties has a new parameter cleanup
  - Model ServiceNowSource has a new parameter disable_metrics_collection
  - Model MagentoSource has a new parameter disable_metrics_collection
  - Model NetezzaSource has a new parameter disable_metrics_collection
  - Model AzureDatabricksDeltaLakeSink has a new parameter disable_metrics_collection
  - Model AzureDataLakeStoreLinkedService has a new parameter credential
  - Model AzureMySqlSource has a new parameter disable_metrics_collection
  - Model SqlSource has a new parameter disable_metrics_collection
  - Model CosmosDbMongoDbApiSink has a new parameter disable_metrics_collection
  - Model JsonSource has a new parameter disable_metrics_collection
  - Model ExcelSource has a new parameter disable_metrics_collection
  - Added operation IntegrationRuntimesOperations.list_outbound_network_dependencies_endpoints
  - Added operation group PrivateLinkResourcesOperations
  - Added operation group PrivateEndpointConnectionOperations
  - Added operation group PrivateEndPointConnectionsOperations

**Breaking changes**

  - Parameter type of model MappingDataFlow is now required
  - Parameter type of model DataFlow is now required

## 1.1.0 (2021-03-12)

**Features**

  - Model PipelineResource has a new parameter policy
  - Model ManagedIntegrationRuntime has a new parameter managed_virtual_network
  - Model CustomActivity has a new parameter auto_user_specification
  - Model HttpLinkedService has a new parameter auth_headers
  - Model AzureDatabricksLinkedService has a new parameter workspace_resource_id
  - Model AzureDatabricksLinkedService has a new parameter authentication
  - Model AzureDatabricksLinkedService has a new parameter policy_id
  - Model RestServiceLinkedService has a new parameter auth_headers
  - Model AzureBlobStorageLinkedService has a new parameter account_kind
  - Model AzureMLExecutePipelineActivity has a new parameter version
  - Model AzureMLExecutePipelineActivity has a new parameter ml_pipeline_endpoint_id
  - Model AzureMLExecutePipelineActivity has a new parameter data_path_assignments
  - Model IntegrationRuntimeSsisCatalogInfo has a new parameter dual_standby_pair_name
  - Model WebActivityAuthentication has a new parameter user_tenant
  - Model ODataLinkedService has a new parameter auth_headers
  - Model CosmosDbLinkedService has a new parameter connection_mode
  - Model CosmosDbLinkedService has a new parameter service_principal_credential_type
  - Model CosmosDbLinkedService has a new parameter service_principal_id
  - Model CosmosDbLinkedService has a new parameter tenant
  - Model CosmosDbLinkedService has a new parameter service_principal_credential
  - Model CosmosDbLinkedService has a new parameter azure_cloud_type

## 1.0.0 (2020-12-17)

**Features**

  - Model Factory has a new parameter encryption
  - Model FactoryIdentity has a new parameter user_assigned_identities
  - Model ExecuteDataFlowActivity has a new parameter trace_level
  - Model ExecuteDataFlowActivity has a new parameter continue_on_error
  - Model ExecuteDataFlowActivity has a new parameter run_concurrently

## 1.0.0b1 (2020-11-06)

This is beta preview version.

This version uses a next-generation code generator that introduces important breaking changes, but also important new features (like unified authentication and async programming).

**General breaking changes**

- Credential system has been completly revamped:

  - `azure.common.credentials` or `msrestazure.azure_active_directory` instances are no longer supported, use the `azure-identity` classes instead: https://pypi.org/project/azure-identity/
  - `credentials` parameter has been renamed `credential`

- The `config` attribute no longer exists on a client, configuration should be passed as kwarg. Example: `MyClient(credential, subscription_id, enable_logging=True)`. For a complete set of
  supported options, see the [parameters accept in init documentation of azure-core](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/CLIENT_LIBRARY_DEVELOPER.md#available-policies)
- You can't import a `version` module anymore, use `__version__` instead
- Operations that used to return a `msrest.polling.LROPoller` now returns a `azure.core.polling.LROPoller` and are prefixed with `begin_`.
- Exceptions tree have been simplified and most exceptions are now `azure.core.exceptions.HttpResponseError` (`CloudError` has been removed).
- Most of the operation kwarg have changed. Some of the most noticeable:

  - `raw` has been removed. Equivalent feature can be found using `cls`, a callback that will give access to internal HTTP response for advanced user
  - For a complete set of
  supported options, see the [parameters accept in Request documentation of azure-core](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/CLIENT_LIBRARY_DEVELOPER.md#available-policies)

**General new features**

- Type annotations support using `typing`. SDKs are mypy ready.
- This client has now stable and official support for async. Check the `aio` namespace of your package to find the async client.
- This client now support natively tracing library like OpenCensus or OpenTelemetry. See this [tracing quickstart](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/core/azure-core-tracing-opentelemetry) for an overview.

## 0.14.0 (2020-10-23)

**Features**

  - Model OrcSink has a new parameter format_settings
  - Model DelimitedTextWriteSettings has a new parameter max_rows_per_file
  - Model DelimitedTextWriteSettings has a new parameter file_name_prefix
  - Model RestSink has a new parameter http_compression_type
  - Model ParquetSink has a new parameter format_settings
  - Model AvroWriteSettings has a new parameter max_rows_per_file
  - Model AvroWriteSettings has a new parameter file_name_prefix

**Breaking changes**

  - Model RestSink no longer has parameter wrap_request_json_in_an_object
  - Model RestSink no longer has parameter compression_type


## 0.13.0 (2020-08-25)

**Features**

  - Model LogStorageSettings has a new parameter enable_reliable_logging
  - Model LogStorageSettings has a new parameter log_level
  - Model HdfsReadSettings has a new parameter delete_files_after_completion
  - Model XmlReadSettings has a new parameter detect_data_type
  - Model XmlReadSettings has a new parameter namespaces
  - Model CosmosDbSqlApiSource has a new parameter detect_datetime
  - Added operation ExposureControlOperations.query_feature_values_by_factory
  - Added operation group ManagedPrivateEndpointsOperations
  - Added operation group ManagedVirtualNetworksOperations

## 0.12.0 (2020-07-29)

**Features**

  - Model SalesforceMarketingCloudLinkedService has a new parameter connection_properties
  - Model ODataLinkedService has a new parameter azure_cloud_type
  - Model SapOpenHubSource has a new parameter custom_rfc_read_table_function_module
  - Model SapOpenHubSource has a new parameter sap_data_column_delimiter
  - Model AzureBlobStorageLinkedService has a new parameter azure_cloud_type
  - Model XeroLinkedService has a new parameter connection_properties
  - Model SapTableSource has a new parameter sap_data_column_delimiter
  - Model AzureSqlDatabaseLinkedService has a new parameter azure_cloud_type
  - Model SapOpenHubLinkedService has a new parameter logon_group
  - Model SapOpenHubLinkedService has a new parameter system_id
  - Model SapOpenHubLinkedService has a new parameter message_server_service
  - Model SapOpenHubLinkedService has a new parameter message_server
  - Model AzureSqlDWLinkedService has a new parameter azure_cloud_type
  - Model AzureDataLakeStoreLinkedService has a new parameter azure_cloud_type
  - Model QuickBooksLinkedService has a new parameter connection_properties
  - Model RestServiceLinkedService has a new parameter azure_cloud_type
  - Model AzureSqlMILinkedService has a new parameter azure_cloud_type
  - Model SquareLinkedService has a new parameter connection_properties
  - Model AzureBlobFSLinkedService has a new parameter azure_cloud_type
  - Model AzureFileStorageLinkedService has a new parameter snapshot
  - Model AzureDatabricksLinkedService has a new parameter new_cluster_log_destination
  - Model ZohoLinkedService has a new parameter connection_properties
  - Added operation TriggerRunsOperations.cancel

## 0.11.0 (2020-06-16)

**Features**

  - Model AzureBlobStorageReadSettings has a new parameter partition_root_path
  - Model AzureBlobStorageReadSettings has a new parameter delete_files_after_completion
  - Model SqlSource has a new parameter partition_option
  - Model SqlSource has a new parameter partition_settings
  - Model JsonSource has a new parameter format_settings
  - Model DynamicsAXSource has a new parameter http_request_timeout
  - Model AzureFileStorageReadSettings has a new parameter partition_root_path
  - Model AzureFileStorageReadSettings has a new parameter prefix
  - Model AzureFileStorageReadSettings has a new parameter delete_files_after_completion
  - Model AzureSqlSource has a new parameter partition_option
  - Model AzureSqlSource has a new parameter partition_settings
  - Model GetMetadataActivity has a new parameter format_settings
  - Model GetMetadataActivity has a new parameter store_settings
  - Model SapCloudForCustomerSink has a new parameter http_request_timeout
  - Model DataFlowSource has a new parameter schema_linked_service
  - Model DataFlowSource has a new parameter linked_service
  - Model SftpReadSettings has a new parameter enable_partition_discovery
  - Model SftpReadSettings has a new parameter partition_root_path
  - Model SftpReadSettings has a new parameter delete_files_after_completion
  - Model FtpReadSettings has a new parameter enable_partition_discovery
  - Model FtpReadSettings has a new parameter partition_root_path
  - Model FtpReadSettings has a new parameter delete_files_after_completion
  - Model IntegrationRuntimeSsisProperties has a new parameter package_stores
  - Model SSISPackageLocation has a new parameter configuration_access_credential
  - Model SqlMISource has a new parameter partition_option
  - Model SqlMISource has a new parameter partition_settings
  - Model SapCloudForCustomerSource has a new parameter http_request_timeout
  - Model AzureDataLakeStoreReadSettings has a new parameter delete_files_after_completion
  - Model AzureDataLakeStoreReadSettings has a new parameter list_before
  - Model AzureDataLakeStoreReadSettings has a new parameter partition_root_path
  - Model AzureDataLakeStoreReadSettings has a new parameter list_after
  - Model AzureBlobFSReadSettings has a new parameter partition_root_path
  - Model AzureBlobFSReadSettings has a new parameter delete_files_after_completion
  - Model SapEccSource has a new parameter http_request_timeout
  - Model DeleteActivity has a new parameter store_settings
  - Model FileServerReadSettings has a new parameter delete_files_after_completion
  - Model FileServerReadSettings has a new parameter partition_root_path
  - Model FileServerReadSettings has a new parameter file_filter
  - Model HttpReadSettings has a new parameter enable_partition_discovery
  - Model HttpReadSettings has a new parameter partition_root_path
  - Model AzureFileStorageLinkedService has a new parameter connection_string
  - Model AzureFileStorageLinkedService has a new parameter file_share
  - Model AzureFileStorageLinkedService has a new parameter account_key
  - Model AzureFileStorageLinkedService has a new parameter sas_uri
  - Model AzureFileStorageLinkedService has a new parameter sas_token
  - Model AmazonS3ReadSettings has a new parameter partition_root_path
  - Model AmazonS3ReadSettings has a new parameter delete_files_after_completion
  - Model GoogleCloudStorageReadSettings has a new parameter partition_root_path
  - Model GoogleCloudStorageReadSettings has a new parameter delete_files_after_completion
  - Model ODataSource has a new parameter http_request_timeout
  - Model SqlDWSource has a new parameter partition_option
  - Model SqlDWSource has a new parameter partition_settings
  - Model BinarySource has a new parameter format_settings
  - Model DataFlowSink has a new parameter schema_linked_service
  - Model DataFlowSink has a new parameter linked_service
  - Model DelimitedTextReadSettings has a new parameter compression_properties
  - Model Factory has a new parameter global_parameters
  - Model SqlServerSource has a new parameter partition_option
  - Model SqlServerSource has a new parameter partition_settings
  - Model HdfsReadSettings has a new parameter partition_root_path

## 0.10.0 (2020-03-10)

**Features**

- Model SqlSource has a new parameter isolation_level
- Model SqlSource has a new parameter additional_columns
- Model SapHanaSource has a new parameter additional_columns
- Model SalesforceMarketingCloudSource has a new parameter additional_columns
- Model Db2Source has a new parameter additional_columns
- Model DynamicsAXSource has a new parameter additional_columns
- Model MicrosoftAccessSource has a new parameter additional_columns
- Model AzureMySqlSource has a new parameter additional_columns
- Model CouchbaseSource has a new parameter additional_columns
- Model CassandraSource has a new parameter additional_columns
- Model NetezzaSource has a new parameter additional_columns
- Model CopyActivity has a new parameter validate_data_consistency
- Model CopyActivity has a new parameter log_storage_settings
- Model CopyActivity has a new parameter skip_error_file
- Model JsonSource has a new parameter additional_columns
- Model AmazonRedshiftSource has a new parameter additional_columns
- Model SapEccSource has a new parameter additional_columns
- Model TabularSource has a new parameter additional_columns
- Model AvroSource has a new parameter additional_columns
- Model DocumentDbCollectionSource has a new parameter additional_columns
- Model SalesforceLinkedService has a new parameter api_version
- Model SybaseSource has a new parameter additional_columns
- Model AzureFileStorageReadSettings has a new parameter file_list_path
- Model SapBwSource has a new parameter additional_columns
- Model MariaDBSource has a new parameter additional_columns
- Model CosmosDbMongoDbApiSource has a new parameter additional_columns
- Model SqlDWSource has a new parameter additional_columns
- Model ConcurSource has a new parameter additional_columns
- Model MongoDbSource has a new parameter additional_columns
- Model AzureSqlSource has a new parameter additional_columns
- Model DynamicsCrmSource has a new parameter additional_columns
- Model JiraSource has a new parameter additional_columns
- Model SftpReadSettings has a new parameter file_list_path
- Model HiveSource has a new parameter additional_columns
- Model OdbcSource has a new parameter additional_columns
- Model SalesforceServiceCloudLinkedService has a new parameter api_version
- Model AzureBlobStorageReadSettings has a new parameter file_list_path
- Model AzureTableSource has a new parameter additional_columns
- Model PaypalSource has a new parameter additional_columns
- Model RelationalSource has a new parameter additional_columns
- Model HBaseSource has a new parameter additional_columns
- Model GoogleCloudStorageReadSettings has a new parameter file_list_path
- Model HubspotSource has a new parameter additional_columns
- Model ResponsysSource has a new parameter additional_columns
- Model CommonDataServiceForAppsSource has a new parameter additional_columns
- Model WebSource has a new parameter additional_columns
- Model Db2LinkedService has a new parameter connection_string
- Model QuickBooksSource has a new parameter additional_columns
- Model FtpReadSettings has a new parameter file_list_path
- Model AzureBlobFSReadSettings has a new parameter file_list_path
- Model SparkSource has a new parameter additional_columns
- Model MagentoSource has a new parameter additional_columns
- Model DrillSource has a new parameter additional_columns
- Model AzureMariaDBSource has a new parameter additional_columns
- Model FileServerReadSettings has a new parameter file_list_path
- Model TeradataSource has a new parameter additional_columns
- Model MarketoSource has a new parameter additional_columns
- Model CosmosDbSqlApiSource has a new parameter additional_columns
- Model AzureDataLakeStoreReadSettings has a new parameter file_list_path
- Model OracleSource has a new parameter additional_columns
- Model VerticaSource has a new parameter additional_columns
- Model PhoenixSource has a new parameter additional_columns
- Model ParquetSource has a new parameter additional_columns
- Model GoogleAdWordsSource has a new parameter additional_columns
- Model SapTableSource has a new parameter additional_columns
- Model FileSystemSource has a new parameter additional_columns
- Model AzureDataLakeStoreWriteSettings has a new parameter expiry_date_time
- Model PrestoSource has a new parameter additional_columns
- Model MongoDbV2Source has a new parameter additional_columns
- Model AzurePostgreSqlSource has a new parameter additional_columns
- Model PostgreSqlSource has a new parameter additional_columns
- Model SquareSource has a new parameter additional_columns
- Model DelimitedTextSource has a new parameter additional_columns
- Model SftpWriteSettings has a new parameter use_temp_file_rename
- Model ZohoSource has a new parameter additional_columns
- Model OracleServiceCloudSource has a new parameter additional_columns
- Model HdfsReadSettings has a new parameter file_list_path
- Model DynamicsSource has a new parameter additional_columns
- Model GoogleBigQuerySource has a new parameter additional_columns
- Model ShopifySource has a new parameter additional_columns
- Model OrcSource has a new parameter additional_columns
- Model AmazonS3ReadSettings has a new parameter file_list_path
- Model EloquaSource has a new parameter additional_columns
- Model ServiceNowSource has a new parameter additional_columns
- Model SalesforceSource has a new parameter additional_columns
- Model ImpalaSource has a new parameter additional_columns
- Model RestSource has a new parameter additional_columns
- Model SqlMISource has a new parameter additional_columns
- Model SapCloudForCustomerSource has a new parameter additional_columns
- Model GreenplumSource has a new parameter additional_columns
- Model SqlServerSource has a new parameter additional_columns
- Model AzureDataExplorerSource has a new parameter additional_columns
- Model SalesforceServiceCloudSource has a new parameter additional_columns
- Model AmazonMWSSource has a new parameter additional_columns
- Model ODataSource has a new parameter additional_columns
- Model SapOpenHubSource has a new parameter additional_columns
- Model InformixSource has a new parameter additional_columns
- Model MySqlSource has a new parameter additional_columns
- Model XeroSource has a new parameter additional_columns
- Added operation TriggersOperations.query_by_factory

**Breaking changes**

- Parameter parent_trigger of model RerunTumblingWindowTrigger is now required
- Operation PipelinesOperations.create_run has a new signature
- Model RerunTumblingWindowTrigger no longer has parameter max_concurrency
- Model RerunTumblingWindowTrigger has a new required parameter rerun_concurrency
- Removed operation group RerunTriggersOperations

## 0.9.0 (2020-02-07)

**Features**

- Model BlobEventsTrigger has a new parameter ignore_empty_blobs
- Model MongoDbV2Source has a new parameter query_timeout
- Model DynamicsCrmLinkedService has a new parameter service_principal_credential_type
- Model DynamicsCrmLinkedService has a new parameter service_principal_id
- Model DynamicsCrmLinkedService has a new parameter service_principal_credential
- Model Office365Source has a new parameter output_columns
- Model DynamicsLinkedService has a new parameter service_principal_credential_type
- Model DynamicsLinkedService has a new parameter service_principal_id
- Model DynamicsLinkedService has a new parameter service_principal_credential
- Model AzureMySqlTableDataset has a new parameter table
- Model HubspotSource has a new parameter query_timeout
- Model TriggerRun has a new parameter dependency_status
- Model TriggerRun has a new parameter run_dimension
- Model DynamicsAXSource has a new parameter query_timeout
- Model DocumentDbCollectionSource has a new parameter query_timeout
- Model AzureSqlSource has a new parameter query_timeout
- Model SapTableSource has a new parameter query_timeout
- Model SybaseSource has a new parameter query_timeout
- Model CommonDataServiceForAppsLinkedService has a new parameter service_principal_credential_type
- Model CommonDataServiceForAppsLinkedService has a new parameter service_principal_id
- Model CommonDataServiceForAppsLinkedService has a new parameter service_principal_credential
- Model HiveSource has a new parameter query_timeout
- Model SapEccSource has a new parameter query_timeout
- Model MySqlSource has a new parameter query_timeout
- Model AzureMySqlSource has a new parameter query_timeout
- Model SparkSource has a new parameter query_timeout
- Model TeradataSource has a new parameter query_timeout
- Model Db2Source has a new parameter query_timeout
- Model AzurePostgreSqlSource has a new parameter query_timeout
- Model DynamicsCrmSink has a new parameter alternate_key_name
- Model MariaDBSource has a new parameter query_timeout
- Model IntegrationRuntimeVNetProperties has a new parameter public_ips
- Model CommonDataServiceForAppsSink has a new parameter alternate_key_name
- Model EloquaSource has a new parameter query_timeout
- Model VerticaSource has a new parameter query_timeout
- Model PhoenixSource has a new parameter query_timeout
- Model PaypalSource has a new parameter query_timeout
- Model PipelineResource has a new parameter run_dimensions
- Model WebActivity has a new parameter connect_via
- Model NetezzaSource has a new parameter query_timeout
- Model XeroSource has a new parameter query_timeout
- Model DrillSource has a new parameter query_timeout
- Model GoogleAdWordsSource has a new parameter query_timeout
- Model ImpalaSource has a new parameter query_timeout
- Model SqlDWSink has a new parameter allow_copy_command
- Model SqlDWSink has a new parameter copy_command_settings
- Model CouchbaseSource has a new parameter query_timeout
- Model DynamicsSink has a new parameter alternate_key_name
- Model Db2LinkedService has a new parameter package_collection
- Model Db2LinkedService has a new parameter certificate_common_name
- Model WebHookActivity has a new parameter report_status_on_call_back
- Model HBaseSource has a new parameter query_timeout
- Model PostgreSqlSource has a new parameter query_timeout
- Model IntegrationRuntimeComputeProperties has a new parameter data_flow_properties
- Model CosmosDbMongoDbApiSource has a new parameter query_timeout
- Model JiraSource has a new parameter query_timeout
- Model AmazonRedshiftSource has a new parameter query_timeout
- Model SqlServerSource has a new parameter query_timeout
- Model SapOpenHubSource has a new parameter query_timeout
- Model MagentoSource has a new parameter query_timeout
- Model CassandraSource has a new parameter query_timeout
- Model SquareSource has a new parameter query_timeout
- Model IntegrationRuntimeSsisProperties has a new parameter express_custom_setup_properties
- Model ShopifySource has a new parameter query_timeout
- Model ResponsysSource has a new parameter query_timeout
- Model MarketoSource has a new parameter query_timeout
- Model SalesforceSource has a new parameter query_timeout
- Model AzureDatabricksLinkedService has a new parameter instance_pool_id
- Model SqlDWSource has a new parameter query_timeout
- Model SalesforceMarketingCloudSource has a new parameter query_timeout
- Model SapCloudForCustomerSource has a new parameter query_timeout
- Model SSISPackageLocation has a new parameter package_last_modified_date
- Model SSISPackageLocation has a new parameter package_content
- Model SSISPackageLocation has a new parameter package_name
- Model SSISPackageLocation has a new parameter child_packages
- Model SapHanaSource has a new parameter partition_settings
- Model SapHanaSource has a new parameter partition_option
- Model SapHanaSource has a new parameter query_timeout
- Model SqlSource has a new parameter query_timeout
- Model PrestoSource has a new parameter query_timeout
- Model ConcurSource has a new parameter query_timeout
- Model GoogleBigQuerySource has a new parameter query_timeout
- Model ServiceNowSource has a new parameter query_timeout
- Model InformixSource has a new parameter query_timeout
- Model AzureTableSource has a new parameter query_timeout
- Model ZohoSource has a new parameter query_timeout
- Model QuickBooksSource has a new parameter query_timeout
- Model OdbcSource has a new parameter query_timeout
- Model AmazonMWSSource has a new parameter query_timeout
- Model OracleServiceCloudSource has a new parameter query_timeout
- Model SqlMISource has a new parameter query_timeout
- Model PipelineRun has a new parameter run_dimensions
- Model SapBwSource has a new parameter query_timeout
- Model GreenplumSource has a new parameter query_timeout
- Model CosmosDbLinkedService has a new parameter database
- Model CosmosDbLinkedService has a new parameter account_endpoint
- Model AzureMariaDBSource has a new parameter query_timeout
- Model AzureBlobStorageReadSettings has a new parameter prefix
- Added operation group DataFlowDebugSessionOperations
- Added operation group DataFlowsOperations

**General Breaking changes**

This version uses a next-generation code generator that might introduce breaking changes for some imports. In summary, some modules were incorrectly visible/importable and have been renamed. This fixed several issues caused by usage of classes that were not supposed to be used in the first place.

- DataFactoryManagementClient cannot be imported from azure.mgmt.datafactory.datafactory_management_client anymore (import from azure.mgmt.datafactory works like before)
- DataFactoryManagementClientConfiguration import has been moved from azure.mgmt.datafactory.datafactory_management_client to azure.mgmt.datafactory
- A model MyClass from a "models" sub-module cannot be imported anymore using azure.mgmt.datafactory.models.my_class (import from azure.mgmt.datafactory.models works like before)
- An operation class MyClassOperations from an operations sub-module cannot be imported anymore using azure.mgmt.datafactory.operations.my_class_operations (import from azure.mgmt.datafactory.operations works like before)

Last but not least, HTTP connection pooling is now enabled by default. You should always use a client as a context manager, or call close(), or use no more than one client per process.

## 0.8.0 (2019-08-30)

**Features**

  - Model HubspotSource has a new parameter max_concurrent_connections
  - Model CouchbaseSource has a new parameter
    max_concurrent_connections
  - Model HttpSource has a new parameter max_concurrent_connections
  - Model AzureDataLakeStoreSource has a new parameter
    max_concurrent_connections
  - Model ConcurSource has a new parameter max_concurrent_connections
  - Model FileShareDataset has a new parameter modified_datetime_start
  - Model FileShareDataset has a new parameter modified_datetime_end
  - Model SalesforceSource has a new parameter
    max_concurrent_connections
  - Model NetezzaSource has a new parameter partition_option
  - Model NetezzaSource has a new parameter max_concurrent_connections
  - Model NetezzaSource has a new parameter partition_settings
  - Model AzureMySqlSource has a new parameter
    max_concurrent_connections
  - Model OdbcSink has a new parameter max_concurrent_connections
  - Model ImpalaObjectDataset has a new parameter
    impala_object_dataset_schema
  - Model ImpalaObjectDataset has a new parameter table
  - Model AzureSqlDWTableDataset has a new parameter
    azure_sql_dw_table_dataset_schema
  - Model AzureSqlDWTableDataset has a new parameter table
  - Model SapEccSource has a new parameter max_concurrent_connections
  - Model CopySource has a new parameter max_concurrent_connections
  - Model ServiceNowSource has a new parameter
    max_concurrent_connections
  - Model Trigger has a new parameter annotations
  - Model CassandraSource has a new parameter
    max_concurrent_connections
  - Model AzureQueueSink has a new parameter
    max_concurrent_connections
  - Model DrillSource has a new parameter max_concurrent_connections
  - Model DocumentDbCollectionSink has a new parameter write_behavior
  - Model DocumentDbCollectionSink has a new parameter
    max_concurrent_connections
  - Model SapHanaLinkedService has a new parameter connection_string
  - Model SalesforceSink has a new parameter
    max_concurrent_connections
  - Model HiveObjectDataset has a new parameter
    hive_object_dataset_schema
  - Model HiveObjectDataset has a new parameter table
  - Model GoogleBigQueryObjectDataset has a new parameter dataset
  - Model GoogleBigQueryObjectDataset has a new parameter table
  - Model FileSystemSource has a new parameter
    max_concurrent_connections
  - Model SqlSink has a new parameter
    stored_procedure_table_type_parameter_name
  - Model SqlSink has a new parameter max_concurrent_connections
  - Model CopySink has a new parameter max_concurrent_connections
  - Model SapCloudForCustomerSource has a new parameter
    max_concurrent_connections
  - Model CopyActivity has a new parameter preserve_rules
  - Model CopyActivity has a new parameter preserve
  - Model AmazonMWSSource has a new parameter
    max_concurrent_connections
  - Model SqlDWSink has a new parameter max_concurrent_connections
  - Model MagentoSource has a new parameter max_concurrent_connections
  - Model BlobEventsTrigger has a new parameter annotations
  - Model DynamicsSink has a new parameter max_concurrent_connections
  - Model AzurePostgreSqlTableDataset has a new parameter table
  - Model AzurePostgreSqlTableDataset has a new parameter
    azure_postgre_sql_table_dataset_schema
  - Model SqlServerTableDataset has a new parameter
    sql_server_table_dataset_schema
  - Model SqlServerTableDataset has a new parameter table
  - Model DocumentDbCollectionSource has a new parameter
    max_concurrent_connections
  - Model AzurePostgreSqlSource has a new parameter
    max_concurrent_connections
  - Model BlobSource has a new parameter max_concurrent_connections
  - Model VerticaTableDataset has a new parameter
    vertica_table_dataset_schema
  - Model VerticaTableDataset has a new parameter table
  - Model PhoenixObjectDataset has a new parameter
    phoenix_object_dataset_schema
  - Model PhoenixObjectDataset has a new parameter table
  - Model AzureSearchIndexSink has a new parameter
    max_concurrent_connections
  - Model MarketoSource has a new parameter max_concurrent_connections
  - Model DynamicsSource has a new parameter
    max_concurrent_connections
  - Model SparkObjectDataset has a new parameter
    spark_object_dataset_schema
  - Model SparkObjectDataset has a new parameter table
  - Model XeroSource has a new parameter max_concurrent_connections
  - Model AmazonRedshiftSource has a new parameter
    max_concurrent_connections
  - Model CustomActivity has a new parameter retention_time_in_days
  - Model WebSource has a new parameter max_concurrent_connections
  - Model GreenplumTableDataset has a new parameter
    greenplum_table_dataset_schema
  - Model GreenplumTableDataset has a new parameter table
  - Model SalesforceMarketingCloudSource has a new parameter
    max_concurrent_connections
  - Model GoogleBigQuerySource has a new parameter
    max_concurrent_connections
  - Model JiraSource has a new parameter max_concurrent_connections
  - Model MongoDbSource has a new parameter max_concurrent_connections
  - Model DrillTableDataset has a new parameter
    drill_table_dataset_schema
  - Model DrillTableDataset has a new parameter table
  - Model ExecuteSSISPackageActivity has a new parameter log_location
  - Model SparkSource has a new parameter max_concurrent_connections
  - Model AzureTableSink has a new parameter
    max_concurrent_connections
  - Model AzureDataLakeStoreSink has a new parameter
    enable_adls_single_file_parallel
  - Model AzureDataLakeStoreSink has a new parameter
    max_concurrent_connections
  - Model PrestoSource has a new parameter max_concurrent_connections
  - Model RelationalSource has a new parameter
    max_concurrent_connections
  - Model TumblingWindowTrigger has a new parameter annotations
  - Model ImpalaSource has a new parameter max_concurrent_connections
  - Model ScheduleTrigger has a new parameter annotations
  - Model QuickBooksSource has a new parameter
    max_concurrent_connections
  - Model PrestoObjectDataset has a new parameter
    presto_object_dataset_schema
  - Model PrestoObjectDataset has a new parameter table
  - Model OracleSink has a new parameter max_concurrent_connections
  - Model HdfsSource has a new parameter max_concurrent_connections
  - Model PhoenixSource has a new parameter max_concurrent_connections
  - Model SapCloudForCustomerSink has a new parameter
    max_concurrent_connections
  - Model SquareSource has a new parameter max_concurrent_connections
  - Model OracleSource has a new parameter partition_option
  - Model OracleSource has a new parameter max_concurrent_connections
  - Model OracleSource has a new parameter partition_settings
  - Model BlobTrigger has a new parameter annotations
  - Model HDInsightOnDemandLinkedService has a new parameter
    virtual_network_id
  - Model HDInsightOnDemandLinkedService has a new parameter
    subnet_name
  - Model AmazonS3LinkedService has a new parameter service_url
  - Model HDInsightLinkedService has a new parameter file_system
  - Model MultiplePipelineTrigger has a new parameter annotations
  - Model HBaseSource has a new parameter max_concurrent_connections
  - Model OracleTableDataset has a new parameter
    oracle_table_dataset_schema
  - Model OracleTableDataset has a new parameter table
  - Model RerunTumblingWindowTrigger has a new parameter annotations
  - Model EloquaSource has a new parameter max_concurrent_connections
  - Model AzureSqlTableDataset has a new parameter
    azure_sql_table_dataset_schema
  - Model AzureSqlTableDataset has a new parameter table
  - Model BlobSink has a new parameter max_concurrent_connections
  - Model HiveSource has a new parameter max_concurrent_connections
  - Model SqlSource has a new parameter max_concurrent_connections
  - Model PaypalSource has a new parameter max_concurrent_connections
  - Model AzureBlobDataset has a new parameter modified_datetime_start
  - Model AzureBlobDataset has a new parameter modified_datetime_end
  - Model VerticaSource has a new parameter max_concurrent_connections
  - Model AmazonS3Dataset has a new parameter modified_datetime_start
  - Model AmazonS3Dataset has a new parameter modified_datetime_end
  - Model PipelineRun has a new parameter run_group_id
  - Model PipelineRun has a new parameter is_latest
  - Model ShopifySource has a new parameter max_concurrent_connections
  - Model MariaDBSource has a new parameter max_concurrent_connections
  - Model TeradataLinkedService has a new parameter connection_string
  - Model ODataLinkedService has a new parameter
    service_principal_embedded_cert
  - Model ODataLinkedService has a new parameter
    aad_service_principal_credential_type
  - Model ODataLinkedService has a new parameter service_principal_key
  - Model ODataLinkedService has a new parameter service_principal_id
  - Model ODataLinkedService has a new parameter aad_resource_id
  - Model ODataLinkedService has a new parameter
    service_principal_embedded_cert_password
  - Model ODataLinkedService has a new parameter tenant
  - Model AzureTableSource has a new parameter
    max_concurrent_connections
  - Model IntegrationRuntimeSsisProperties has a new parameter
    data_proxy_properties
  - Model ZohoSource has a new parameter max_concurrent_connections
  - Model ResponsysSource has a new parameter
    max_concurrent_connections
  - Model FileSystemSink has a new parameter
    max_concurrent_connections
  - Model SqlDWSource has a new parameter max_concurrent_connections
  - Model GreenplumSource has a new parameter
    max_concurrent_connections
  - Model AzureDatabricksLinkedService has a new parameter
    new_cluster_init_scripts
  - Model AzureDatabricksLinkedService has a new parameter
    new_cluster_driver_node_type
  - Model AzureDatabricksLinkedService has a new parameter
    new_cluster_enable_elastic_disk
  - Added operation TriggerRunsOperations.rerun
  - Added operation
    ExposureControlOperations.get_feature_value_by_factory
  - Added model Office365Dataset
  - Added model AzureBlobFSDataset
  - Added model CommonDataServiceForAppsEntityDataset
  - Added model DynamicsCrmEntityDataset
  - Added model AzureSqlMITableDataset
  - Added model HdfsLocation
  - Added model HttpServerLocation
  - Added model SftpLocation
  - Added model FtpServerLocation
  - Added model FileServerLocation
  - Added model AmazonS3Location
  - Added model AzureDataLakeStoreLocation
  - Added model AzureBlobFSLocation
  - Added model AzureBlobStorageLocation
  - Added model DatasetLocation
  - Added model BinaryDataset
  - Added model JsonDataset
  - Added model DelimitedTextDataset
  - Added model ParquetDataset
  - Added model AvroDataset
  - Added model GoogleAdWordsSource
  - Added model OracleServiceCloudSource
  - Added model DynamicsAXSource
  - Added model NetezzaPartitionSettings
  - Added model AzureMariaDBSource
  - Added model AzureBlobFSSource
  - Added model Office365Source
  - Added model MongoDbCursorMethodsProperties
  - Added model CosmosDbMongoDbApiSource
  - Added model MongoDbV2Source
  - Added model TeradataPartitionSettings
  - Added model TeradataSource
  - Added model OraclePartitionSettings
  - Added model AzureDataExplorerSource
  - Added model SqlMISource
  - Added model AzureSqlSource
  - Added model SqlServerSource
  - Added model RestSource
  - Added model SapTablePartitionSettings
  - Added model SapTableSource
  - Added model SapOpenHubSource
  - Added model SapHanaSource
  - Added model SalesforceServiceCloudSource
  - Added model ODataSource
  - Added model SapBwSource
  - Added model SybaseSource
  - Added model PostgreSqlSource
  - Added model MySqlSource
  - Added model OdbcSource
  - Added model Db2Source
  - Added model MicrosoftAccessSource
  - Added model InformixSource
  - Added model CommonDataServiceForAppsSource
  - Added model DynamicsCrmSource
  - Added model HdfsReadSettings
  - Added model HttpReadSettings
  - Added model SftpReadSettings
  - Added model FtpReadSettings
  - Added model FileServerReadSettings
  - Added model AmazonS3ReadSettings
  - Added model AzureDataLakeStoreReadSettings
  - Added model AzureBlobFSReadSettings
  - Added model AzureBlobStorageReadSettings
  - Added model StoreReadSettings
  - Added model BinarySource
  - Added model JsonSource
  - Added model FormatReadSettings
  - Added model DelimitedTextReadSettings
  - Added model DelimitedTextSource
  - Added model ParquetSource
  - Added model AvroSource
  - Added model AzureDataExplorerCommandActivity
  - Added model SSISAccessCredential
  - Added model SSISLogLocation
  - Added model CosmosDbMongoDbApiSink
  - Added model SalesforceServiceCloudSink
  - Added model AzureDataExplorerSink
  - Added model CommonDataServiceForAppsSink
  - Added model DynamicsCrmSink
  - Added model MicrosoftAccessSink
  - Added model InformixSink
  - Added model AzureBlobFSSink
  - Added model SqlMISink
  - Added model AzureSqlSink
  - Added model SqlServerSink
  - Added model FileServerWriteSettings
  - Added model AzureDataLakeStoreWriteSettings
  - Added model AzureBlobFSWriteSettings
  - Added model AzureBlobStorageWriteSettings
  - Added model StoreWriteSettings
  - Added model BinarySink
  - Added model ParquetSink
  - Added model JsonWriteSettings
  - Added model DelimitedTextWriteSettings
  - Added model FormatWriteSettings
  - Added model AvroWriteSettings
  - Added model AvroSink
  - Added model AzureMySqlSink
  - Added model AzurePostgreSqlSink
  - Added model JsonSink
  - Added model DelimitedTextSink
  - Added model WebHookActivity
  - Added model ValidationActivity
  - Added model EntityReference
  - Added model IntegrationRuntimeDataProxyProperties
  - Added model SsisVariable
  - Added model SsisEnvironment
  - Added model SsisParameter
  - Added model SsisPackage
  - Added model SsisEnvironmentReference
  - Added model SsisProject
  - Added model SsisFolder

**Breaking changes**

  - Operation PipelinesOperations.create_run has a new signature
  - Model SSISPackageLocation has a new signature

## 0.7.0 (2019-01-31)

**Features**

  - Model MarketoObjectDataset has a new parameter folder
  - Model MarketoObjectDataset has a new parameter schema
  - Model MarketoObjectDataset has a new parameter table_name
  - Model AzureTableDataset has a new parameter folder
  - Model AzureTableDataset has a new parameter schema
  - Model VerticaTableDataset has a new parameter folder
  - Model VerticaTableDataset has a new parameter schema
  - Model VerticaTableDataset has a new parameter table_name
  - Model VerticaLinkedService has a new parameter pwd
  - Model DocumentDbCollectionDataset has a new parameter folder
  - Model DocumentDbCollectionDataset has a new parameter schema
  - Model HubspotObjectDataset has a new parameter folder
  - Model HubspotObjectDataset has a new parameter schema
  - Model HubspotObjectDataset has a new parameter table_name
  - Model GetMetadataActivity has a new parameter user_properties
  - Model SalesforceObjectDataset has a new parameter folder
  - Model SalesforceObjectDataset has a new parameter schema
  - Model AzureStorageLinkedService has a new parameter account_key
  - Model AzureStorageLinkedService has a new parameter sas_token
  - Model OracleLinkedService has a new parameter password
  - Model ZohoObjectDataset has a new parameter folder
  - Model ZohoObjectDataset has a new parameter schema
  - Model ZohoObjectDataset has a new parameter table_name
  - Model HDInsightHiveActivity has a new parameter variables
  - Model HDInsightHiveActivity has a new parameter query_timeout
  - Model HDInsightHiveActivity has a new parameter user_properties
  - Model AmazonS3Dataset has a new parameter folder
  - Model AmazonS3Dataset has a new parameter schema
  - Model AzureSqlTableDataset has a new parameter folder
  - Model AzureSqlTableDataset has a new parameter schema
  - Model Activity has a new parameter user_properties
  - Model AzurePostgreSqlLinkedService has a new parameter password
  - Model HDInsightMapReduceActivity has a new parameter
    user_properties
  - Model HttpDataset has a new parameter folder
  - Model HttpDataset has a new parameter schema
  - Model MagentoObjectDataset has a new parameter folder
  - Model MagentoObjectDataset has a new parameter schema
  - Model MagentoObjectDataset has a new parameter table_name
  - Model NetezzaLinkedService has a new parameter pwd
  - Model ImpalaObjectDataset has a new parameter folder
  - Model ImpalaObjectDataset has a new parameter schema
  - Model ImpalaObjectDataset has a new parameter table_name
  - Model DrillLinkedService has a new parameter pwd
  - Model XeroObjectDataset has a new parameter folder
  - Model XeroObjectDataset has a new parameter schema
  - Model XeroObjectDataset has a new parameter table_name
  - Model ODataResourceDataset has a new parameter folder
  - Model ODataResourceDataset has a new parameter schema
  - Model MariaDBTableDataset has a new parameter folder
  - Model MariaDBTableDataset has a new parameter schema
  - Model MariaDBTableDataset has a new parameter table_name
  - Model PhoenixObjectDataset has a new parameter folder
  - Model PhoenixObjectDataset has a new parameter schema
  - Model PhoenixObjectDataset has a new parameter table_name
  - Model ShopifyObjectDataset has a new parameter folder
  - Model ShopifyObjectDataset has a new parameter schema
  - Model ShopifyObjectDataset has a new parameter table_name
  - Model DatabricksNotebookActivity has a new parameter libraries
  - Model DatabricksNotebookActivity has a new parameter
    user_properties
  - Model HDInsightStreamingActivity has a new parameter
    user_properties
  - Model MariaDBLinkedService has a new parameter pwd
  - Model OracleTableDataset has a new parameter folder
  - Model OracleTableDataset has a new parameter schema
  - Model AzureDatabricksLinkedService has a new parameter
    new_cluster_spark_env_vars
  - Model AzureDatabricksLinkedService has a new parameter
    new_cluster_custom_tags
  - Model ControlActivity has a new parameter user_properties
  - Model AzurePostgreSqlTableDataset has a new parameter folder
  - Model AzurePostgreSqlTableDataset has a new parameter schema
  - Model AzurePostgreSqlTableDataset has a new parameter table_name
  - Model EloquaObjectDataset has a new parameter folder
  - Model EloquaObjectDataset has a new parameter schema
  - Model EloquaObjectDataset has a new parameter table_name
  - Model ForEachActivity has a new parameter user_properties
  - Model HDInsightPigActivity has a new parameter user_properties
  - Model WaitActivity has a new parameter user_properties
  - Model DrillTableDataset has a new parameter folder
  - Model DrillTableDataset has a new parameter schema
  - Model DrillTableDataset has a new parameter table_name
  - Model ExecutePipelineActivity has a new parameter user_properties
  - Model UntilActivity has a new parameter user_properties
  - Model AzureDataLakeStoreDataset has a new parameter folder
  - Model AzureDataLakeStoreDataset has a new parameter schema
  - Model HDInsightLinkedService has a new parameter is_esp_enabled
  - Model SelfHostedIntegrationRuntimeStatus has a new parameter
    auto_update_eta
  - Model SelfHostedIntegrationRuntimeStatus has a new parameter
    pushed_version
  - Model SelfHostedIntegrationRuntimeStatus has a new parameter
    latest_version
  - Model ServiceNowObjectDataset has a new parameter folder
  - Model ServiceNowObjectDataset has a new parameter schema
  - Model ServiceNowObjectDataset has a new parameter table_name
  - Model WebActivity has a new parameter user_properties
  - Model QuickBooksObjectDataset has a new parameter folder
  - Model QuickBooksObjectDataset has a new parameter schema
  - Model QuickBooksObjectDataset has a new parameter table_name
  - Model CustomDataset has a new parameter folder
  - Model CustomDataset has a new parameter schema
  - Model GreenplumTableDataset has a new parameter folder
  - Model GreenplumTableDataset has a new parameter schema
  - Model GreenplumTableDataset has a new parameter table_name
  - Model JiraObjectDataset has a new parameter folder
  - Model JiraObjectDataset has a new parameter schema
  - Model JiraObjectDataset has a new parameter table_name
  - Model CouchbaseLinkedService has a new parameter cred_string
  - Model PrestoObjectDataset has a new parameter folder
  - Model PrestoObjectDataset has a new parameter schema
  - Model PrestoObjectDataset has a new parameter table_name
  - Model TabularTranslator has a new parameter schema_mapping
  - Model Factory has a new parameter e_tag
  - Model Factory has a new parameter repo_configuration
  - Model AzureSearchIndexDataset has a new parameter folder
  - Model AzureSearchIndexDataset has a new parameter schema
  - Model WebTableDataset has a new parameter folder
  - Model WebTableDataset has a new parameter schema
  - Model FilterActivity has a new parameter user_properties
  - Model PipelineRunInvokedBy has a new parameter invoked_by_type
  - Model Resource has a new parameter e_tag
  - Model RelationalTableDataset has a new parameter folder
  - Model RelationalTableDataset has a new parameter schema
  - Model AzureSqlDWTableDataset has a new parameter folder
  - Model AzureSqlDWTableDataset has a new parameter schema
  - Model Dataset has a new parameter folder
  - Model Dataset has a new parameter schema
  - Model AzureMLBatchExecutionActivity has a new parameter
    user_properties
  - Model CouchbaseTableDataset has a new parameter folder
  - Model CouchbaseTableDataset has a new parameter schema
  - Model CouchbaseTableDataset has a new parameter table_name
  - Model HDInsightSparkActivity has a new parameter user_properties
  - Model AzureSqlDWLinkedService has a new parameter password
  - Model AzureMLUpdateResourceActivity has a new parameter
    user_properties
  - Model SapEccResourceDataset has a new parameter folder
  - Model SapEccResourceDataset has a new parameter schema
  - Model LookupActivity has a new parameter user_properties
  - Model AzureMySqlLinkedService has a new parameter password
  - Model DataLakeAnalyticsUSQLActivity has a new parameter
    user_properties
  - Model CassandraTableDataset has a new parameter folder
  - Model CassandraTableDataset has a new parameter schema
  - Model SquareObjectDataset has a new parameter folder
  - Model SquareObjectDataset has a new parameter schema
  - Model SquareObjectDataset has a new parameter table_name
  - Model HDInsightOnDemandLinkedService has a new parameter
    script_actions
  - Model PaypalObjectDataset has a new parameter folder
  - Model PaypalObjectDataset has a new parameter schema
  - Model PaypalObjectDataset has a new parameter table_name
  - Model PipelineResource has a new parameter variables
  - Model PipelineResource has a new parameter folder
  - Model DynamicsEntityDataset has a new parameter folder
  - Model DynamicsEntityDataset has a new parameter schema
  - Model ActivityPolicy has a new parameter secure_input
  - Model FileShareDataset has a new parameter folder
  - Model FileShareDataset has a new parameter schema
  - Model AzureMySqlTableDataset has a new parameter folder
  - Model AzureMySqlTableDataset has a new parameter schema
  - Model ExecuteSSISPackageActivity has a new parameter
    project_connection_managers
  - Model ExecuteSSISPackageActivity has a new parameter
    user_properties
  - Model ExecuteSSISPackageActivity has a new parameter
    package_connection_managers
  - Model ExecuteSSISPackageActivity has a new parameter
    package_parameters
  - Model ExecuteSSISPackageActivity has a new parameter
    property_overrides
  - Model ExecuteSSISPackageActivity has a new parameter
    project_parameters
  - Model ExecuteSSISPackageActivity has a new parameter
    execution_credential
  - Model HiveObjectDataset has a new parameter folder
  - Model HiveObjectDataset has a new parameter schema
  - Model HiveObjectDataset has a new parameter table_name
  - Model IfConditionActivity has a new parameter user_properties
  - Model CosmosDbLinkedService has a new parameter account_key
  - Model GoogleBigQueryObjectDataset has a new parameter folder
  - Model GoogleBigQueryObjectDataset has a new parameter schema
  - Model GoogleBigQueryObjectDataset has a new parameter table_name
  - Model SqlServerTableDataset has a new parameter folder
  - Model SqlServerTableDataset has a new parameter schema
  - Model SparkObjectDataset has a new parameter folder
  - Model SparkObjectDataset has a new parameter schema
  - Model SparkObjectDataset has a new parameter table_name
  - Model CustomActivity has a new parameter user_properties
  - Model SapCloudForCustomerResourceDataset has a new parameter folder
  - Model SapCloudForCustomerResourceDataset has a new parameter schema
  - Model TumblingWindowTrigger has a new parameter depends_on
  - Model SqlServerStoredProcedureActivity has a new parameter
    user_properties
  - Model ConcurObjectDataset has a new parameter folder
  - Model ConcurObjectDataset has a new parameter schema
  - Model ConcurObjectDataset has a new parameter table_name
  - Model OperationMetricSpecification has a new parameter dimensions
  - Model HBaseObjectDataset has a new parameter folder
  - Model HBaseObjectDataset has a new parameter schema
  - Model HBaseObjectDataset has a new parameter table_name
  - Model AmazonMWSObjectDataset has a new parameter folder
  - Model AmazonMWSObjectDataset has a new parameter schema
  - Model AmazonMWSObjectDataset has a new parameter table_name
  - Model ExecutionActivity has a new parameter user_properties
  - Model AzureBlobDataset has a new parameter folder
  - Model AzureBlobDataset has a new parameter schema
  - Model AzureSqlDatabaseLinkedService has a new parameter password
  - Model MongoDbCollectionDataset has a new parameter folder
  - Model MongoDbCollectionDataset has a new parameter schema
  - Model CopyActivity has a new parameter data_integration_units
  - Model CopyActivity has a new parameter user_properties
  - Model SalesforceMarketingCloudObjectDataset has a new parameter
    folder
  - Model SalesforceMarketingCloudObjectDataset has a new parameter
    schema
  - Model SalesforceMarketingCloudObjectDataset has a new parameter
    table_name
  - Model GreenplumLinkedService has a new parameter pwd
  - Model NetezzaTableDataset has a new parameter folder
  - Model NetezzaTableDataset has a new parameter schema
  - Model NetezzaTableDataset has a new parameter table_name
  - Added operation PipelineRunsOperations.cancel
  - Added operation FactoriesOperations.configure_factory_repo
  - Added operation FactoriesOperations.get_data_plane_access
  - Added operation FactoriesOperations.get_git_hub_access_token
  - Added operation IntegrationRuntimeNodesOperations.get
  - Added operation
    IntegrationRuntimesOperations.create_linked_integration_runtime
  - Added operation IntegrationRuntimesOperations.remove_links
  - Added operation ActivityRunsOperations.query_by_pipeline_run
  - Added operation group RerunTriggersOperations
  - Added operation group TriggerRunsOperations
  - Added operation group IntegrationRuntimeObjectMetadataOperations
  - Added operation group ExposureControlOperations

**Breaking changes**

  - Parameter access_token_secret of model QuickBooksLinkedService is
    now required
  - Parameter access_token of model QuickBooksLinkedService is now
    required
  - Operation DatasetsOperations.get has a new signature
  - Operation FactoriesOperations.create_or_update has a new signature
  - Operation FactoriesOperations.get has a new signature
  - Operation IntegrationRuntimesOperations.get has a new signature
  - Operation LinkedServicesOperations.get has a new signature
  - Operation PipelinesOperations.get has a new signature
  - Operation TriggersOperations.get has a new signature
  - Operation PipelinesOperations.create_run has a new signature
  - Model Db2LinkedService no longer has parameter schema
  - Model QuickBooksLinkedService has a new required parameter
    consumer_key
  - Model QuickBooksLinkedService has a new required parameter
    consumer_secret
  - Model PostgreSqlLinkedService no longer has parameter database
  - Model PostgreSqlLinkedService no longer has parameter username
  - Model PostgreSqlLinkedService no longer has parameter schema
  - Model PostgreSqlLinkedService no longer has parameter server
  - Model PostgreSqlLinkedService has a new required parameter
    connection_string
  - Model TeradataLinkedService no longer has parameter schema
  - Model CopyActivity no longer has parameter
    cloud_data_movement_units
  - Model MySqlLinkedService no longer has parameter database
  - Model MySqlLinkedService no longer has parameter username
  - Model MySqlLinkedService no longer has parameter schema
  - Model MySqlLinkedService no longer has parameter server
  - Model MySqlLinkedService has a new required parameter
    connection_string
  - Removed operation FactoriesOperations.cancel_pipeline_run
  - Removed operation IntegrationRuntimesOperations.remove_node
  - Removed operation TriggersOperations.list_runs
  - Removed operation ActivityRunsOperations.list_by_pipeline_run

## 0.6.0 (2018-03-22)

  - Added new AzureDatabricks LinkedService and DatabricksNotebook
    Activity
  - Added headNodeSize and dataNodeSize properties in HDInsightOnDemand
    LinkedService
  - Added LinkedService, Dataset, CopySource for
    SalesforceMarketingCloud
  - Added support for SecureOutput on all activities
  - Added new BatchCount property on ForEach activity which controls how
    many concurrent activities to run
  - Added DELETE method for Web Activity
  - Added new Filter Activity
  - Added Linked Service Parameters support

## 0.5.0 (2018-02-16)

  - Enable AAD auth via service principal and management service
    identity for Azure SQL DB/DW linked service types
  - Support integration runtime sharing across subscription and data
    factory
  - Enable Azure Key Vault for all compute linked service
  - Add SAP ECC Source
  - GoogleBigQuery support clientId and clientSecret for
    UserAuthentication
  - Add LinkedService, Dataset, CopySource for Vertica and Netezza

## 0.4.0 (2018-02-02)

**Features**

  - Add readBehavior to Salesforce Source
  - Enable Azure Key Vault support for all data store linked services
  - Add license type property to Azure SSIS integration runtime

## 0.3.0 (2017-12-12)

**Features**

  - Add SAP Cloud For Customer Source 
  - Add SAP Cloud For Customer Dataset 
  - Add SAP Cloud For Customer Sink 
  - Support providing a Dynamics password as a SecureString, a secret in
    Azure Key Vault, or as an encrypted credential. 
  - App model for Tumbling Window Trigger 
  - Add LinkedService, Dataset, Source for 26 RFI connectors, including:
    PostgreSQL,Google
    BigQuery,Impala,ServiceNow,Greenplum/Hawq,HBase,Hive ODBC,Spark
    ODBC,HBase Phoenix,MariaDB,Presto,Couchbase,Concur,Zoho CRM,Amazon
    Marketplace Services,PayPal,Square,Shopify,QuickBooks
    Online,Hubspot,Atlassian Jira,Magento,Xero,Drill,Marketo,Eloqua. 
  - Support round tripping of new properties using additionalProperties
    for some types 
  - Add new integration runtime API's: patch integration runtime; patch
    integration runtime node; upgrade integration runtime, get node IP
    address 
  - Add integration runtime naming validation

## 0.2.2 (2017-11-13)

**Features**

  - Added new connectors: AzureMySql, Salesforce and JSONFormat,
    Dynamics Sink
  - Added support providing Salesforce passwords and security tokens as
    SecureString and AzureKeyVaultSecret for Dynamics/Salesforce
  - Added cancel pipeline run api

## 0.2.1 (2017-10-03)

**Features**

  - Add factories.cancel_pipeline_run

## 0.2.0 (2017-09-22)

  - Initial Release
