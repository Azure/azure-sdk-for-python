# Release History

## 0.21.0 (2025-09-05)

### Features Added

- Add a new Model ServiceNowV2LinkedService
- Model ServiceNowV2ObjectDataset has a new parameter table_name
- Model ServiceNowV2ObjectDataset has a new parameter value_type
- linked service add support Presto server linked service
- Model DynamicsSink has a new parameter bypass_business_logic_execution
- Model DynamicsSink has a new parameter bypass_power_automate_flows
- Model AzurePostgreSqlSink has a new parameter write_method
- Model AzurePostgreSqlSink has a new parameter upsert_settings
- Model SnowflakeV2LinkedService has a new parameter role
- Model SnowflakeV2LinkedService has a new parameter schema
- Model AzurePostgreSqlLinkedService has a new parameter service_principal_embedded_cert
- Model AzurePostgreSqlLinkedService has a new parameter service_principal_embedded_cert_password
- Model ODataLinkedService has a new parameter service_principal_embedded_cert
- Model ODataLinkedService has a new parameter service_principal_embedded_cert_password
- Model Office365LinkedService has a new parameter service_principal_embedded_cert
- Model Office365LinkedService has a new parameter service_principal_embedded_cert_password
- Model RestServiceLinkedService has a new parameter service_principal_embedded_cert
- Model RestServiceLinkedService has a new parameter service_principal_embedded_cert_password
- Model SharePointOnlineListLinkedService has a new parameter service_principal_embedded_cert
- Model SharePointOnlineListLinkedService has a new parameter service_principal_embedded_cert_password
- Model AzureDatabricksLinkedService has a new parameter data_security_mode
- Model AmazonRdsForOracleLinkedService has a new parameter server
- Model AmazonRdsForOracleLinkedService has a new parameter authentication_type
- Model AmazonRdsForOracleLinkedService has a new parameter username
- Model AmazonRdsForOracleLinkedService has a new parameter encryption_client
- Model AmazonRdsForOracleLinkedService has a new parameter encryption_types_client
- Model AmazonRdsForOracleLinkedService has a new parameter crypto_checksum_client
- Model AmazonRdsForOracleLinkedService has a new parameter crypto_checksum_types_client
- Model AmazonRdsForOracleLinkedService has a new parameter initial_lob_fetch_size
- Model AmazonRdsForOracleLinkedService has a new parameter fetch_size
- Model AmazonRdsForOracleLinkedService has a new parameter statement_cache_size
- Model AmazonRdsForOracleLinkedService has a new parameter initialization_string
- Model AmazonRdsForOracleLinkedService has a new parameter enable_bulk_load
- Model AmazonRdsForOracleLinkedService has a new parameter fetch_tswtz_as_timestamp
- Model AmazonRdsForOracleLinkedService has a new parameter support_v1_data_types
- Model FtpServerLinkedService has a new parameter enable_server_certificate_validation
- Model HiveLinkedService has a new parameter enable_server_certificate_validation
- Model HttpLinkedService has a new parameter enable_server_certificate_validation
- Model ImpalaLinkedService has a new parameter enable_server_certificate_validation
- Model RestServiceLinkedService has a new parameter enable_server_certificate_validation
- Model SparkLinkedService has a new parameter enable_server_certificate_validation
- Model QuickBooksLinkedService has a new parameter refresh_token
- Model AmazonRdsForOracleSource has a new parameter number_precision
- Model AmazonRdsForOracleSource has a new parameter number_scale
- Model OracleSource has a new parameter number_precision
- Model OracleSource has a new parameter number_scale
- Model LakeHouseLinkedService has a new parameter authentication_type
- Model LakeHouseLinkedService has a new parameter credential
- Model WarehouseLinkedService has a new parameter authentication_type
- Model WarehouseLinkedService has a new parameter credential
- Model HDInsightLinkedService has a new parameter cluster_auth_type
- Model HDInsightLinkedService has a new parameter credential

### Breaking Changes

- Model LinkedService parameter OracleLinkedService parameter connection_string now is not required
- Model GreenplumLinkedService remove parameter password
- Model ExpressionV2 parameter value change its type from string to object

## 0.20.0 (2025-03-07)

### Features Added

  - Add a new Model IcebergDataset
  - Add a new Model IcebergSink
  - Add a new Model TeradataSink
  - Model AzureFileStorageLinkedService has a new parameter service_endpoint
  - Model AzureFileStorageLinkedService has a new parameter credential
  - Model AzureTableStorageLinkedService has a new parameter service_endpoint
  - Model AzureTableStorageLinkedService has a new parameter credential
  - Model DynamicsCrmLinkedService has a new properties credential
  - Model DynamicsLinkedService has a new properties domain
  - Model GreenplumLinkedService has a new parameter authentication_type
  - Model GreenplumLinkedService has a new parameter host
  - Model GreenplumLinkedService has a new parameter port
  - Model GreenplumLinkedService has a new parameter username
  - Model GreenplumLinkedService has a new parameter database
  - Model GreenplumLinkedService has a new parameter ssl_mode
  - Model GreenplumLinkedService has a new parameter connection_timeout
  - Model GreenplumLinkedService has a new parameter command_timeout
  - Model GreenplumLinkedService has a new parameter password
  - Model MySqlLinkedService has a new parameter allow_zero_date_time
  - Model MySqlLinkedService has a new parameter connection_timeout
  - Model MySqlLinkedService has a new parameter convert_zero_date_time
  - Model MySqlLinkedService has a new parameter guid_format
  - Model MySqlLinkedService has a new parameter ssl_cert
  - Model MySqlLinkedService has a new parameter ssl_key
  - Model MySqlLinkedService has a new parameter treat_tiny_as_boolean
  - Model OracleLinkedService has a new parameter server
  - Model OracleLinkedService has a new parameter authentication_type
  - Model OracleLinkedService has a new parameter username
  - Model OracleLinkedService has a new parameter encryption_client
  - Model OracleLinkedService has a new parameter encryption_types_client
  - Model OracleLinkedService has a new parameter crypto_checksum_client
  - Model OracleLinkedService has a new parameter crypto_checksum_types_client
  - Model OracleLinkedService has a new parameter initial_lob_fetch_size
  - Model OracleLinkedService has a new parameter fetch_size
  - Model OracleLinkedService has a new parameter statement_cache_size
  - Model OracleLinkedService has a new parameter initialization_string
  - Model OracleLinkedService has a new parameter enable_bulk_load
  - Model OracleLinkedService has a new parameter support_v1_data_types
  - Model OracleLinkedService has a new parameter fetch_tswtz_as_timestamp
  - Model RestServiceLinkedService has a new parameter service_principal_credential_type
  - Model RestServiceLinkedService has a new parameter service_principal_embedded_cert
  - Model RestServiceLinkedService has a new parameter service_principal_embedded_cert_password
  - Model SharePointOnlineListLinkedService has a new parameter service_principal_credential_type
  - Model SharePointOnlineListLinkedService has a new parameter service_principal_embedded_cert
  - Model SharePointOnlineListLinkedService has a new parameter service_principal_embedded_cert_password
  - Model SapTableLinkedService update parameter snc_mode
  - Model SnowflakeV2LinkedService has a new properties host
  - Model SqlServerLinkedService has a new parameter server 
  - Model SqlServerLinkedService has a new parameter database
  - Model SqlServerLinkedService has a new parameter encrypt
  - Model SqlServerLinkedService has a new parameter trust_server_certificate
  - Model SqlServerLinkedService has a new parameter host_name_in_certificate
  - Model SqlServerLinkedService has a new parameter application_intent
  - Model SqlServerLinkedService has a new parameter connect_timeout
  - Model SqlServerLinkedService has a new parameter connect_retry_count
  - Model SqlServerLinkedService has a new parameter connect_retry_interval
  - Model SqlServerLinkedService has a new parameter load_balance_timeout
  - Model SqlServerLinkedService has a new parameter command_timeout
  - Model SqlServerLinkedService has a new parameter integrated_security
  - Model SqlServerLinkedService has a new parameter failover_partner
  - Model SqlServerLinkedService has a new parameter max_pool_size
  - Model SqlServerLinkedService has a new parameter min_pool_size
  - Model SqlServerLinkedService has a new parameter multiple_active_result_sets
  - Model SqlServerLinkedService has a new parameter multi_subnet_failover
  - Model SqlServerLinkedService has a new parameter packet_size
  - Model SqlServerLinkedService has a new parameter pooling
  - Model SqlServerLinkedService has a new parameter authentication_type
  - Model SqlServerLinkedService has a new parameter credential
  - Model AzureSqlDWLinkedService has a new parameter server 
  - Model AzureSqlDWLinkedService has a new parameter database
  - Model AzureSqlDWLinkedService has a new parameter encrypt
  - Model AzureSqlDWLinkedService has a new parameter trust_server_certificate
  - Model AzureSqlDWLinkedService has a new parameter host_name_in_certificate
  - Model AzureSqlDWLinkedService has a new parameter application_intent
  - Model AzureSqlDWLinkedService has a new parameter connect_timeout
  - Model AzureSqlDWLinkedService has a new parameter connect_retry_count
  - Model AzureSqlDWLinkedService has a new parameter connect_retry_interval
  - Model AzureSqlDWLinkedService has a new parameter load_balance_timeout
  - Model AzureSqlDWLinkedService has a new parameter command_timeout
  - Model AzureSqlDWLinkedService has a new parameter integrated_security
  - Model AzureSqlDWLinkedService has a new parameter failover_partner
  - Model AzureSqlDWLinkedService has a new parameter max_pool_size
  - Model AzureSqlDWLinkedService has a new parameter min_pool_size
  - Model AzureSqlDWLinkedService has a new parameter multiple_active_result_sets
  - Model AzureSqlDWLinkedService has a new parameter multi_subnet_failover
  - Model AzureSqlDWLinkedService has a new parameter packet_size
  - Model AzureSqlDWLinkedService has a new parameter pooling
  - Model AzureSqlDWLinkedService has a new parameter authentication_type
  - Model AzureSqlDWLinkedService has a new parameter username
  - Model AzureSqlDWLinkedService has a new parameter service_principal_credential_type
  - Model AzureSqlDWLinkedService has a new parameter service_principal_credential
  - Model AmazonRdsForSqlServerLinkedService has a new parameter server 
  - Model AmazonRdsForSqlServerLinkedService has a new parameter database
  - Model AmazonRdsForSqlServerLinkedService has a new parameter encrypt
  - Model AmazonRdsForSqlServerLinkedService has a new parameter trust_server_certificate
  - Model AmazonRdsForSqlServerLinkedService has a new parameter host_name_in_certificate
  - Model AmazonRdsForSqlServerLinkedService has a new parameter application_intent
  - Model AmazonRdsForSqlServerLinkedService has a new parameter connect_timeout
  - Model AmazonRdsForSqlServerLinkedService has a new parameter connect_retry_count
  - Model AmazonRdsForSqlServerLinkedService has a new parameter connect_retry_interval
  - Model AmazonRdsForSqlServerLinkedService has a new parameter load_balance_timeout
  - Model AmazonRdsForSqlServerLinkedService has a new parameter command_timeout
  - Model AmazonRdsForSqlServerLinkedService has a new parameter integrated_security
  - Model AmazonRdsForSqlServerLinkedService has a new parameter failover_partner
  - Model AmazonRdsForSqlServerLinkedService has a new parameter max_pool_size
  - Model AmazonRdsForSqlServerLinkedService has a new parameter min_pool_size
  - Model AmazonRdsForSqlServerLinkedService has a new parameter multiple_active_result_sets
  - Model AmazonRdsForSqlServerLinkedService has a new parameter multi_subnet_failover
  - Model AmazonRdsForSqlServerLinkedService has a new parameter packet_size
  - Model AmazonRdsForSqlServerLinkedService has a new parameter pooling
  - Model AmazonRdsForSqlServerLinkedService has a new parameter authentication_type
  - Model AzureSqlDatabaseLinkedService has a new parameter server 
  - Model AzureSqlDatabaseLinkedService has a new parameter database
  - Model AzureSqlDatabaseLinkedService has a new parameter encrypt
  - Model AzureSqlDatabaseLinkedService has a new parameter trust_server_certificate
  - Model AzureSqlDatabaseLinkedService has a new parameter host_name_in_certificate
  - Model AzureSqlDatabaseLinkedService has a new parameter application_intent
  - Model AzureSqlDatabaseLinkedService has a new parameter connect_timeout
  - Model AzureSqlDatabaseLinkedService has a new parameter connect_retry_count
  - Model AzureSqlDatabaseLinkedService has a new parameter connect_retry_interval
  - Model AzureSqlDatabaseLinkedService has a new parameter load_balance_timeout
  - Model AzureSqlDatabaseLinkedService has a new parameter command_timeout
  - Model AzureSqlDatabaseLinkedService has a new parameter integrated_security
  - Model AzureSqlDatabaseLinkedService has a new parameter failover_partner
  - Model AzureSqlDatabaseLinkedService has a new parameter max_pool_size
  - Model AzureSqlDatabaseLinkedService has a new parameter min_pool_size
  - Model AzureSqlDatabaseLinkedService has a new parameter multiple_active_result_sets
  - Model AzureSqlDatabaseLinkedService has a new parameter multi_subnet_failover
  - Model AzureSqlDatabaseLinkedService has a new parameter packet_size
  - Model AzureSqlDatabaseLinkedService has a new parameter pooling
  - Model AzureSqlDatabaseLinkedService has a new parameter authentication_type
  - Model AzureSqlDatabaseLinkedService has a new parameter username
  - Model AzureSqlDatabaseLinkedService has a new parameter service_principal_credential_type
  - Model AzureSqlDatabaseLinkedService has a new parameter service_principal_credential
  - Model AzureSqlMILinkedService has a new parameter server 
  - Model AzureSqlMILinkedService has a new parameter database
  - Model AzureSqlMILinkedService has a new parameter encrypt
  - Model AzureSqlMILinkedService has a new parameter trust_server_certificate
  - Model AzureSqlMILinkedService has a new parameter host_name_in_certificate
  - Model AzureSqlMILinkedService has a new parameter application_intent
  - Model AzureSqlMILinkedService has a new parameter connect_timeout
  - Model AzureSqlMILinkedService has a new parameter connect_retry_count
  - Model AzureSqlMILinkedService has a new parameter connect_retry_interval
  - Model AzureSqlMILinkedService has a new parameter load_balance_timeout
  - Model AzureSqlMILinkedService has a new parameter command_timeout
  - Model AzureSqlMILinkedService has a new parameter integrated_security
  - Model AzureSqlMILinkedService has a new parameter failover_partner
  - Model AzureSqlMILinkedService has a new parameter max_pool_size
  - Model AzureSqlMILinkedService has a new parameter min_pool_size
  - Model AzureSqlMILinkedService has a new parameter multiple_active_result_sets
  - Model AzureSqlMILinkedService has a new parameter multi_subnet_failover
  - Model AzureSqlMILinkedService has a new parameter packet_size
  - Model AzureSqlMILinkedService has a new parameter pooling
  - Model AzureSqlMILinkedService has a new parameter authentication_type
  - Model AzureSqlMILinkedService has a new parameter username
  - Model AzureSqlMILinkedService has a new parameter service_principal_credential_type
  - Model AzureSqlMILinkedService has a new parameter service_principal_credential
  - Model TeradataLinkedService a new parameter ssl_mode
  - Model TeradataLinkedService a new parameter port_number
  - Model TeradataLinkedService a new parameter https_port_number
  - Model TeradataLinkedService a new parameter use_data_encryption
  - Model TeradataLinkedService a new parameter character_set
  - Model TeradataLinkedService a new parameter max_resp_size
  - Model VerticaLinkedService a new parameter server
  - Model VerticaLinkedService a new parameter port
  - Model VerticaLinkedService a new parameter uid
  - Model VerticaLinkedService a new parameter database
  - Model LinkedService has a new parameter version
  - Model SynapseNotebookActivity has a new parameter authentication
  - Model SynapseSparkJobDefinitionActivity has a new parameter authentication
  - Model ScriptActivity has a new parameter return_multistatement_result
  - Model ExecuteDataFlowActivity has a new properties continuation_settings
  - Model ExpressionV2 has a new parameter operators
  - Model SalesforceV2Source has a new parameter page_size
  - Model SalesforceV2Source has a new parameter query
  - Model MariaDBLinkedService has a new parameter ssl_mode
  - Model MariaDBLinkedService has a new parameter use_system_trust_store

### Breaking Changes

  - Model LinkedService parameter PostgreSqlV2LinkedService has a new required properties authentication_type
  - Model LinkedService parameter SapOdpLinkedService update properties sncMode
  - Model LinkedService parameter AzureSqlDWLinkedService parameter connection_string now is not required
  - Model LinkedService parameter SqlServerLinkedService parameter connection_string now is not required
  - Model LinkedService parameter AmazonRdsForSqlServerLinkedService parameter connection_string now is not required
  - Model LinkedService parameter AzureSqlDatabaseLinkedService parameter connection_string now is not required
  - Model LinkedService parameter AzureSqlMILinkedService parameter connection_string now is not required
  - Model SharePointOnlineListLinkedService parameter service_principal_key now is not required

## 0.19.0 (2024-06-04)

### Features Added

  - Model Dataset has a new parameter LakeHouseLocation
  - Model Dataset has a new parameter GoogleBigQueryV2ObjectDataset
  - Model Dataset has a new parameter PostgreSqlV2TableDataset
  - Model Dataset has a new parameter SalesforceServiceCloudV2ObjectDataset
  - Model Dataset has a new parameter SalesforceV2ObjectDataset
  - Model Dataset has a new parameter ServiceNowV2ObjectDataset
  - Model Dataset has a new parameter SnowflakeV2Dataset
  - Model Dataset has a new parameter WarehouseTableDataset
  - Model Pipeline has a new parameter ExpressionV2
  - Model Pipeline has a new parameter GoogleBigQueryV2Source
  - Model Pipeline has a new parameter LakeHouseTableSink
  - Model Pipeline has a new parameter LakeHouseTableSource
  - Model Pipeline has a new parameter LakeHouseWriteSettings
  - Model Pipeline has a new parameter LakeHouseReadSettings
  - Model Pipeline has a new parameter Metadata
  - Model Pipeline has a new parameter MetadataItem
  - Model Pipeline has a new parameter ParquetReadSettingsstate
  - Model Pipeline has a new parameter PostgreSqlV2Source
  - Model Pipeline has a new parameter SalesforceServiceCloudV2Sink
  - Model Pipeline has a new parameter SalesforceServiceCloudV2Source
  - Model Pipeline has a new parameter SalesforceV2Sink
  - Model Pipeline has a new parameter SalesforceV2SourceReadBehavior
  - Model Pipeline has a new parameter SalesforceV2Source
  - Model Pipeline has a new parameter ServiceNowV2Source
  - Model Pipeline has a new parameter SnowflakeV2Sink
  - Model Pipeline has a new parameter SnowflakeV2Source
  - Model Pipeline has a new parameter WarehouseSink
  - Model Pipeline has a new parameter WarehouseSource
  - Model LinkedService add supports GoogleAds
  - Model LinkedService has a new parameter GoogleBigQueryV2LinkedService
  - Model LinkedService has a new parameter LakeHouseLinkedService
  - Model LinkedService has a new parameter PostgreSqlV2LinkedService
  - Model LinkedService has a new parameter SalesforceServiceCloudV2LinkedService
  - Model LinkedService has a new parameter SalesforceV2LinkedService
  - Model LinkedService has a new parameter SalesforceV2LinkedService
  - Model LinkedService has a new parameter SnowflakeV2LinkedService
  - Model LinkedService has a new parameter WarehouseLinkedService
  - Model LinkedService has a new parameter WarehouseLinkedService 

### Breaking Changes

  - Model LinkedService parameter MariaDBLinkedService update new properties
  - Model LinkedService parameter MySqlLinkedService update new properties
  - Model LinkedService parameter ServiceNowV2LinkedService update properties
  - Model Pipeline parameter ExecuteDataFlowActivity update new properties computeType
  - Model Pipeline parameter ScriptActivityScriptBlock update properties type

## 0.18.0 (2023-10-30)

### Bugs Fixed

  - Fix runNotebook sessionId from int to string #25210
  - Fix placeholder links causing 404s #26143

### Other Changes

  - Sync expression Support From DataFactory To Synapse #25054

## 0.17.0 (2023-07-28)

### Features Added

  - Added operation group RunNotebookOperations
  - Model Activity has a new parameter on_inactive_mark_as
  - Model Activity has a new parameter state
  - Model AmazonRdsForSqlServerLinkedService has a new parameter always_encrypted_settings
  - Model AmazonRdsForSqlServerSource has a new parameter isolation_level
  - Model AppendVariableActivity has a new parameter on_inactive_mark_as
  - Model AppendVariableActivity has a new parameter state
  - Model AzureBatchLinkedService has a new parameter credential
  - Model AzureBlobFSLinkedService has a new parameter credential
  - Model AzureBlobStorageLinkedService has a new parameter credential
  - Model AzureDataExplorerCommandActivity has a new parameter on_inactive_mark_as
  - Model AzureDataExplorerCommandActivity has a new parameter state
  - Model AzureDataExplorerLinkedService has a new parameter credential
  - Model AzureDataLakeStoreLinkedService has a new parameter credential
  - Model AzureDatabricksDeltaLakeLinkedService has a new parameter credential
  - Model AzureDatabricksLinkedService has a new parameter credential
  - Model AzureFunctionActivity has a new parameter on_inactive_mark_as
  - Model AzureFunctionActivity has a new parameter state
  - Model AzureFunctionLinkedService has a new parameter authentication
  - Model AzureFunctionLinkedService has a new parameter credential
  - Model AzureFunctionLinkedService has a new parameter resource_id
  - Model AzureKeyVaultLinkedService has a new parameter credential
  - Model AzureMLBatchExecutionActivity has a new parameter on_inactive_mark_as
  - Model AzureMLBatchExecutionActivity has a new parameter state
  - Model AzureMLExecutePipelineActivity has a new parameter on_inactive_mark_as
  - Model AzureMLExecutePipelineActivity has a new parameter state
  - Model AzureMLLinkedService has a new parameter authentication
  - Model AzureMLServiceLinkedService has a new parameter authentication
  - Model AzureMLUpdateResourceActivity has a new parameter on_inactive_mark_as
  - Model AzureMLUpdateResourceActivity has a new parameter state
  - Model AzureSqlDWLinkedService has a new parameter credential
  - Model AzureSqlDatabaseLinkedService has a new parameter always_encrypted_settings
  - Model AzureSqlDatabaseLinkedService has a new parameter credential
  - Model AzureSqlMILinkedService has a new parameter always_encrypted_settings
  - Model AzureSqlMILinkedService has a new parameter credential
  - Model AzureSqlSource has a new parameter isolation_level
  - Model ControlActivity has a new parameter on_inactive_mark_as
  - Model ControlActivity has a new parameter state
  - Model CopyActivity has a new parameter on_inactive_mark_as
  - Model CopyActivity has a new parameter state
  - Model CosmosDbLinkedService has a new parameter credential
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
  - Model DynamicsLinkedService has a new parameter credential
  - Model ExecuteDataFlowActivity has a new parameter on_inactive_mark_as
  - Model ExecuteDataFlowActivity has a new parameter state
  - Model ExecutePipelineActivity has a new parameter on_inactive_mark_as
  - Model ExecutePipelineActivity has a new parameter state
  - Model ExecuteSSISPackageActivity has a new parameter on_inactive_mark_as
  - Model ExecuteSSISPackageActivity has a new parameter state
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
  - Model HDInsightHiveActivity has a new parameter on_inactive_mark_as
  - Model HDInsightHiveActivity has a new parameter state
  - Model HDInsightMapReduceActivity has a new parameter on_inactive_mark_as
  - Model HDInsightMapReduceActivity has a new parameter state
  - Model HDInsightOnDemandLinkedService has a new parameter credential
  - Model HDInsightPigActivity has a new parameter on_inactive_mark_as
  - Model HDInsightPigActivity has a new parameter state
  - Model HDInsightSparkActivity has a new parameter on_inactive_mark_as
  - Model HDInsightSparkActivity has a new parameter state
  - Model HDInsightStreamingActivity has a new parameter on_inactive_mark_as
  - Model HDInsightStreamingActivity has a new parameter state
  - Model IfConditionActivity has a new parameter on_inactive_mark_as
  - Model IfConditionActivity has a new parameter state
  - Model LinkConnectionTargetDatabaseTypeProperties has a new parameter action_on_existing_target_table
  - Model LookupActivity has a new parameter on_inactive_mark_as
  - Model LookupActivity has a new parameter state
  - Model MongoDbAtlasLinkedService has a new parameter driver_version
  - Model RestServiceLinkedService has a new parameter credential
  - Model ScriptActivity has a new parameter on_inactive_mark_as
  - Model ScriptActivity has a new parameter state
  - Model SetVariableActivity has a new parameter on_inactive_mark_as
  - Model SetVariableActivity has a new parameter policy
  - Model SetVariableActivity has a new parameter state
  - Model SqlDWSource has a new parameter isolation_level
  - Model SqlMISource has a new parameter isolation_level
  - Model SqlPoolStoredProcedureActivity has a new parameter on_inactive_mark_as
  - Model SqlPoolStoredProcedureActivity has a new parameter state
  - Model SqlServerLinkedService has a new parameter always_encrypted_settings
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
  - Model WebActivityAuthentication has a new parameter credential
  - Model WebActivityAuthentication has a new parameter user_tenant
  - Model WebHookActivity has a new parameter on_inactive_mark_as
  - Model WebHookActivity has a new parameter state

## 0.16.0 (2023-05-12)

### Bugs Fixed

  - Fix to support IO input  #29615

## 0.15.0 (2023-01-09)

### Features Added

  - Model AzureSynapseArtifactsLinkedService has a new parameter workspace_resource_id
  - Model RestServiceLinkedService has a new parameter auth_headers
  - Model SynapseSparkJobDefinitionActivity has a new parameter configuration_type
  - Model SynapseSparkJobDefinitionActivity has a new parameter files_v2
  - Model SynapseSparkJobDefinitionActivity has a new parameter python_code_reference
  - Model SynapseSparkJobDefinitionActivity has a new parameter scan_folder
  - Model SynapseSparkJobDefinitionActivity has a new parameter spark_config
  - Model SynapseSparkJobDefinitionActivity has a new parameter target_spark_configuration 

### Breaking Changes

  - Parameter export_settings of model SnowflakeSource is now required
  - Renamed operation LinkConnectionOperations.create_or_update_link_connection to LinkConnectionOperations.create_or_update
  - Renamed operation LinkConnectionOperations.delete_link_connection to LinkConnectionOperations.delete
  - Renamed operation LinkConnectionOperations.get_link_connection to LinkConnectionOperations.get
  - Renamed operation LinkConnectionOperations.list_link_connections_by_workspace to LinkConnectionOperations.list_by_workspace

## 0.14.0 (2022-09-19)

### Features Added

  - Upgraded api-version for some operation group

### Other Changes
  
  - Drop support for python3.6

## 0.13.0 (2022-04-21)

### Features

  - Added operation group LinkConnectionOperations

## 0.12.0 (2022-03-07)

### Features Added

- re-generated based on tag package-artifacts-composite-v3

## 0.11.0 (2022-01-11)

### Features Added

- Added `MetastoreOperations`

### Other Changes

- Python 2.7 and 3.6 are no longer supported. Please use Python version 3.7 or later.

## 0.10.0 (2021-11-09)

### Other Changes

- Internal bugfixes (re-generated with latest generator)

## 0.9.0 (2021-10-05)

### Features Added

- re-generated based on tag package-artifacts-composite-v1

## 0.8.0 (2021-08-10)

- Updated API version to "2020-12-01" which is the default API version
- Added `NotebookOperationResultOperations`, `OperationResultOperations`, `OperationStatusOperations`
- Added API version "2021-06-01-preview" support

## 0.7.0 (2021-05-11)

### Bug fixes

- Enable poller when starting a long running operation    #18184

## 0.6.0 (2021-04-06)

### New Features

- Add ADF support

## 0.5.0 (2021-03-09)

### New Features

- Add library operations
- Change create_or_update_sql_script, delete_sql_script, rename_sql_script to long running operations

### Breaking changes

- Stop Python 3.5 support

## 0.4.0 (2020-12-08)

### New Features

- Add Workspace git repo management operations
- Add rename method for data flow, dataset, linked service, notebook, pipeline, spark job definition, sql script operations

## 0.3.0 (2020-09-15)

### New Features

- Add Workspace operations
- Add SqlPools operations
- Add BigDataPools operations
- Add IntegrationRuntimes operations

### Breaking changes

- Migrated most long running operation to polling mechanism (operation now starts with `begin`)

## 0.2.0 (2020-07-01)

* Initial Release
