# Release History

## 2.0.0 (2026-07-03)

### Features Added

  - Client `AzureArcDataManagementClient` added method `send_request`
  - Client `AzureArcDataManagementClient` added operation group `sql_server_licenses`
  - Client `AzureArcDataManagementClient` added operation group `postgres_instances`
  - Client `AzureArcDataManagementClient` added operation group `sql_server_esu_licenses`
  - Client `AzureArcDataManagementClient` added operation group `failover_groups`
  - Client `AzureArcDataManagementClient` added operation group `sql_server_availability_groups`
  - Client `AzureArcDataManagementClient` added operation group `active_directory_connectors`
  - Client `AzureArcDataManagementClient` added operation group `sql_server_databases`
  - Enum `ArcSqlServerLicenseType` added member `FABRIC_CAPACITY`
  - Enum `ArcSqlServerLicenseType` added member `LICENSE_ONLY`
  - Enum `ArcSqlServerLicenseType` added member `PAYG`
  - Enum `ArcSqlServerLicenseType` added member `SERVER_CAL`
  - Enum `ConnectionStatus` added member `DISCOVERED`
  - Enum `ConnectionStatus` added member `REGISTERED`
  - Model `DataControllerUpdate` added property `properties`
  - Enum `EditionType` added member `BUSINESS_INTELLIGENCE`
  - Enum `EditionType` added member `STANDARD_DEVELOPER`
  - Enum `EditionType` added member `UNKNOWN`
  - Model `SqlManagedInstanceK8SSpec` added property `security`
  - Model `SqlManagedInstanceK8SSpec` added property `settings`
  - Model `SqlManagedInstanceProperties` added property `active_directory_information`
  - Model `SqlServerInstanceProperties` added property `vm_id`
  - Model `SqlServerInstanceProperties` added property `cores`
  - Model `SqlServerInstanceProperties` added property `discovery_source`
  - Model `SqlServerInstanceProperties` added property `db_master_key_exists`
  - Model `SqlServerInstanceProperties` added property `is_hadr_enabled`
  - Model `SqlServerInstanceProperties` added property `trace_flags`
  - Model `SqlServerInstanceProperties` added property `last_inventory_upload_time`
  - Model `SqlServerInstanceProperties` added property `last_usage_upload_time`
  - Model `SqlServerInstanceProperties` added property `host_type`
  - Model `SqlServerInstanceProperties` added property `always_on_role`
  - Model `SqlServerInstanceProperties` added property `database_mirroring_endpoint`
  - Model `SqlServerInstanceProperties` added property `failover_cluster`
  - Model `SqlServerInstanceProperties` added property `backup_policy`
  - Model `SqlServerInstanceProperties` added property `upgrade_locked_until`
  - Model `SqlServerInstanceProperties` added property `monitoring`
  - Model `SqlServerInstanceProperties` added property `migration`
  - Model `SqlServerInstanceProperties` added property `best_practices_assessment`
  - Model `SqlServerInstanceProperties` added property `client_connection`
  - Model `SqlServerInstanceProperties` added property `service_type`
  - Model `SqlServerInstanceProperties` added property `max_server_memory_mb`
  - Model `SqlServerInstanceProperties` added property `is_microsoft_pki_cert_trust_configured`
  - Model `SqlServerInstanceProperties` added property `is_digi_cert_pki_cert_trust_configured`
  - Model `SqlServerInstanceProperties` added property `authentication`
  - Model `SqlServerInstanceUpdate` added property `properties`
  - Enum `SqlVersion` added member `SQL_SERVER2012`
  - Enum `SqlVersion` added member `SQL_SERVER2014`
  - Enum `SqlVersion` added member `SQL_SERVER2022`
  - Enum `SqlVersion` added member `SQL_SERVER2025`
  - Enum `SqlVersion` added member `UNKNOWN`
  - Added enum `AccountProvisioningMode`
  - Added enum `ActivationState`
  - Added model `ActiveDirectoryConnectorDNSDetails`
  - Added model `ActiveDirectoryConnectorDomainDetails`
  - Added model `ActiveDirectoryConnectorProperties`
  - Added model `ActiveDirectoryConnectorResource`
  - Added model `ActiveDirectoryConnectorSpec`
  - Added model `ActiveDirectoryConnectorStatus`
  - Added model `ActiveDirectoryDomainController`
  - Added model `ActiveDirectoryDomainControllers`
  - Added model `ActiveDirectoryInformation`
  - Added model `AdditionalMigrationJobAttributes`
  - Added enum `AggregationType`
  - Added enum `AlwaysOnRole`
  - Added enum `ArcSqlServerAvailabilityGroupTypeFilter`
  - Added enum `ArcSqlServerAvailabilityMode`
  - Added enum `ArcSqlServerFailoverMode`
  - Added enum `AssessmentStatus`
  - Added model `Authentication`
  - Added enum `AutomatedBackupPreference`
  - Added model `AvailabilityGroupConfigure`
  - Added model `AvailabilityGroupCreateUpdateConfiguration`
  - Added model `AvailabilityGroupCreateUpdateReplicaConfiguration`
  - Added model `AvailabilityGroupInfo`
  - Added model `AvailabilityGroupRetrievalFilters`
  - Added model `AvailabilityGroupState`
  - Added enum `AzureManagedInstanceRole`
  - Added model `BackgroundJob`
  - Added model `BackupPolicy`
  - Added model `BestPracticesAssessment`
  - Added enum `BillingPlan`
  - Added model `ClientConnection`
  - Added enum `ClusterType`
  - Added model `CommonSku`
  - Added enum `ConnectionAuth`
  - Added model `CostOptionSelectedValues`
  - Added model `CostTypeValues`
  - Added model `CronTrigger`
  - Added model `DBMEndpoint`
  - Added model `DataBaseMigration`
  - Added model `DataBaseMigrationAssessment`
  - Added model `DatabaseAssessmentsItem`
  - Added enum `DatabaseCreateMode`
  - Added model `DatabaseMigrationJobsItem`
  - Added enum `DatabaseState`
  - Added model `Databases`
  - Added enum `DbFailover`
  - Added enum `DifferentialBackupHours`
  - Added enum `DiscoverySource`
  - Added model `DiskSizes`
  - Added model `DistributedAvailabilityGroupCreateUpdateAvailabilityGroupCertificateConfiguration`
  - Added model `DistributedAvailabilityGroupCreateUpdateAvailabilityGroupConfiguration`
  - Added model `DistributedAvailabilityGroupCreateUpdateConfiguration`
  - Added enum `DtcSupport`
  - Added enum `EncryptionAlgorithm`
  - Added model `EntraAuthentication`
  - Added model `ErrorAdditionalInfo`
  - Added model `ErrorDetail`
  - Added enum `ExecutionState`
  - Added model `FailoverCluster`
  - Added enum `FailoverGroupPartnerSyncMode`
  - Added model `FailoverGroupProperties`
  - Added model `FailoverGroupResource`
  - Added model `FailoverGroupSpec`
  - Added model `FailoverMiLinkResourceId`
  - Added enum `FailureConditionLevel`
  - Added model `HostIPAddressInformation`
  - Added enum `HostType`
  - Added enum `IdentityType`
  - Added model `ImpactedObjectsInfo`
  - Added model `ImpactedObjectsSuitabilitySummary`
  - Added enum `InitiatedFrom`
  - Added enum `InstanceFailoverGroupRole`
  - Added enum `JobStatus`
  - Added model `K8SActiveDirectory`
  - Added model `K8SActiveDirectoryConnector`
  - Added model `K8SNetworkSettings`
  - Added model `K8SSecurity`
  - Added model `K8SSettings`
  - Added model `K8StransparentDataEncryption`
  - Added model `KeytabInformation`
  - Added enum `LastExecutionStatus`
  - Added enum `LicenseCategory`
  - Added model `ManagedInstanceLinkCreateUpdateConfiguration`
  - Added enum `MiLinkAssessmentCategory`
  - Added model `MiLinkCreateUpdateConfiguration`
  - Added model `Migration`
  - Added model `MigrationAssessment`
  - Added model `MigrationAssessmentSettings`
  - Added enum `MigrationMode`
  - Added enum `MigrationStatus`
  - Added enum `Mode`
  - Added model `Monitoring`
  - Added model `PostgresInstance`
  - Added model `PostgresInstanceProperties`
  - Added model `PostgresInstanceSku`
  - Added model `PostgresInstanceUpdate`
  - Added enum `PrimaryAllowConnections`
  - Added enum `ProvisioningState`
  - Added model `ProxyResource`
  - Added enum `RecommendationStatus`
  - Added enum `RecoveryMode`
  - Added enum `ReplicationPartnerType`
  - Added enum `ResourceUpdateMode`
  - Added enum `Result`
  - Added enum `Role`
  - Added model `Schedule`
  - Added enum `ScopeType`
  - Added enum `SecondaryAllowConnections`
  - Added enum `SeedingMode`
  - Added model `SequencerAction`
  - Added enum `SequencerState`
  - Added model `ServerAssessmentsItem`
  - Added model `ServerAssessmentsPropertiesItemsItem`
  - Added enum `ServiceType`
  - Added model `SkuRecommendationResults`
  - Added model `SkuRecommendationResultsAzureSqlDatabase`
  - Added model `SkuRecommendationResultsAzureSqlDatabaseTargetSku`
  - Added model `SkuRecommendationResultsAzureSqlDatabaseTargetSkuCategory`
  - Added model `SkuRecommendationResultsAzureSqlManagedInstance`
  - Added model `SkuRecommendationResultsAzureSqlManagedInstanceTargetSku`
  - Added model `SkuRecommendationResultsAzureSqlManagedInstanceTargetSkuCategory`
  - Added model `SkuRecommendationResultsAzureSqlVirtualMachine`
  - Added model `SkuRecommendationResultsAzureSqlVirtualMachineTargetSku`
  - Added model `SkuRecommendationResultsAzureSqlVirtualMachineTargetSkuCategory`
  - Added model `SkuRecommendationResultsAzureSqlVirtualMachineTargetSkuVirtualMachineSize`
  - Added model `SkuRecommendationResultsMonthlyCost`
  - Added model `SkuRecommendationResultsMonthlyCostOptionItem`
  - Added model `SkuRecommendationSummary`
  - Added model `SkuRecommendationSummaryTargetSku`
  - Added model `SkuRecommendationSummaryTargetSkuCategory`
  - Added model `SqlAvailabilityGroupDatabaseReplicaResourceProperties`
  - Added model `SqlAvailabilityGroupIpV4AddressesAndMasksPropertiesItem`
  - Added model `SqlAvailabilityGroupReplicaResourceProperties`
  - Added model `SqlAvailabilityGroupStaticIPListenerProperties`
  - Added model `SqlServerAvailabilityGroupResource`
  - Added model `SqlServerAvailabilityGroupResourceProperties`
  - Added model `SqlServerAvailabilityGroupResourcePropertiesDatabases`
  - Added model `SqlServerAvailabilityGroupResourcePropertiesReplicas`
  - Added model `SqlServerAvailabilityGroupUpdate`
  - Added model `SqlServerDatabaseResource`
  - Added model `SqlServerDatabaseResourceProperties`
  - Added model `SqlServerDatabaseResourcePropertiesBackupInformation`
  - Added model `SqlServerDatabaseResourcePropertiesDatabaseOptions`
  - Added model `SqlServerDatabaseUpdate`
  - Added model `SqlServerEsuLicense`
  - Added model `SqlServerEsuLicenseProperties`
  - Added model `SqlServerEsuLicenseUpdate`
  - Added model `SqlServerEsuLicenseUpdateProperties`
  - Added model `SqlServerInstanceBpaColumn`
  - Added enum `SqlServerInstanceBpaColumnType`
  - Added enum `SqlServerInstanceBpaQueryType`
  - Added enum `SqlServerInstanceBpaReportType`
  - Added model `SqlServerInstanceBpaRequest`
  - Added model `SqlServerInstanceJob`
  - Added model `SqlServerInstanceJobStatus`
  - Added model `SqlServerInstanceJobsRequest`
  - Added model `SqlServerInstanceJobsResponse`
  - Added model `SqlServerInstanceJobsStatusRequest`
  - Added model `SqlServerInstanceJobsStatusResponse`
  - Added model `SqlServerInstanceManagedInstanceLinkAssessment`
  - Added model `SqlServerInstanceManagedInstanceLinkAssessmentRequest`
  - Added model `SqlServerInstanceManagedInstanceLinkAssessmentResponse`
  - Added model `SqlServerInstanceMigrationReadinessReportResponse`
  - Added model `SqlServerInstanceRunBestPracticesAssessmentResponse`
  - Added model `SqlServerInstanceRunMigrationAssessmentResponse`
  - Added model `SqlServerInstanceRunMigrationReadinessAssessmentResponse`
  - Added model `SqlServerInstanceRunTargetRecommendationJobRequest`
  - Added model `SqlServerInstanceRunTargetRecommendationJobResponse`
  - Added model `SqlServerInstanceTargetRecommendationReport`
  - Added model `SqlServerInstanceTargetRecommendationReportSection`
  - Added enum `SqlServerInstanceTargetRecommendationReportSectionType`
  - Added model `SqlServerInstanceTargetRecommendationReportsRequest`
  - Added model `SqlServerInstanceTargetRecommendationReportsResponse`
  - Added model `SqlServerInstanceTelemetryColumn`
  - Added enum `SqlServerInstanceTelemetryColumnType`
  - Added model `SqlServerInstanceTelemetryRequest`
  - Added model `SqlServerInstanceUpdateProperties`
  - Added model `SqlServerLicense`
  - Added model `SqlServerLicenseProperties`
  - Added model `SqlServerLicenseUpdate`
  - Added model `SqlServerLicenseUpdateProperties`
  - Added enum `State`
  - Added model `TargetReadiness`
  - Added enum `TargetType`
  - Added enum `Version`
  - Operation group `SqlServerInstancesOperations` added method `begin_get_best_practices_assessment`
  - Operation group `SqlServerInstancesOperations` added method `begin_get_jobs`
  - Operation group `SqlServerInstancesOperations` added method `begin_get_migration_readiness_report`
  - Operation group `SqlServerInstancesOperations` added method `begin_get_target_recommendation_reports`
  - Operation group `SqlServerInstancesOperations` added method `begin_get_telemetry`
  - Operation group `SqlServerInstancesOperations` added method `begin_run_best_practice_assessment`
  - Operation group `SqlServerInstancesOperations` added method `begin_run_managed_instance_link_assessment`
  - Operation group `SqlServerInstancesOperations` added method `begin_run_migration_readiness_assessment`
  - Operation group `SqlServerInstancesOperations` added method `begin_run_target_recommendation_job`
  - Operation group `SqlServerInstancesOperations` added method `get_all_availability_groups`
  - Operation group `SqlServerInstancesOperations` added method `get_jobs_status`
  - Operation group `SqlServerInstancesOperations` added method `post_upgrade`
  - Operation group `SqlServerInstancesOperations` added method `pre_upgrade`
  - Operation group `SqlServerInstancesOperations` added method `run_best_practices_assessment`
  - Operation group `SqlServerInstancesOperations` added method `run_migration_assessment`
  - Added operation group `ActiveDirectoryConnectorsOperations`
  - Added operation group `FailoverGroupsOperations`
  - Added operation group `PostgresInstancesOperations`
  - Added operation group `SqlServerAvailabilityGroupsOperations`
  - Added operation group `SqlServerDatabasesOperations`
  - Added operation group `SqlServerEsuLicensesOperations`
  - Added operation group `SqlServerLicensesOperations`

### Breaking Changes

  - Renamed method `DataControllersOperations.patch_data_controller` to `begin_patch_data_controller`
  - Renamed method `SqlServerInstancesOperations.update` to `begin_update`

### Other Changes

  - Deleted model `ErrorResponseBody`/`OperationListResult`/`PageOfDataControllerResource`/`SqlManagedInstanceListResult`/`SqlManagedInstanceSkuName`/`SqlServerInstanceListResult` which actually were not used by SDK users

## 2.0.0b2 (2026-05-14)

### Other Changes

  - Regenerated with latest code generator tool

## 1.0.1 (2026-05-14)

### Other Changes

  - Regenerated with latest code generator tool

## 2.0.0b1 (2022-11-18)

### Features Added

  - Added operation group ActiveDirectoryConnectorsOperations
  - Added operation group PostgresInstancesOperations
  - Model DataControllerUpdate has a new parameter properties
  - Model ProxyResource has a new parameter system_data
  - Model Resource has a new parameter system_data
  - Model SqlManagedInstanceProperties has a new parameter active_directory_information
  - Model SqlServerInstanceProperties has a new parameter host_type

### Breaking Changes

  - Renamed operation DataControllersOperations.patch_data_controller to DataControllersOperations.begin_patch_data_controller

## 1.0.0 (2021-10-26)

**Features**

  - Model DataControllerProperties has a new parameter logs_dashboard_credential
  - Model DataControllerProperties has a new parameter metrics_dashboard_credential

## 1.0.0b1 (2021-09-15)

* Initial Release
