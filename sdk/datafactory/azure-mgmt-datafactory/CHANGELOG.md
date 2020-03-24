# Release History

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
