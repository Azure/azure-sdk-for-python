# Release History

## 0.25.0 (2020-12-14)

**Features**

  - Model ManagedInstanceUpdate has a new parameter identity
  - Model ManagedInstanceUpdate has a new parameter private_endpoint_connections
  - Model ManagedInstanceUpdate has a new parameter zone_redundant
  - Model ManagedInstance has a new parameter private_endpoint_connections
  - Model ManagedInstance has a new parameter zone_redundant
  - Added operation ManagedInstancesOperations.list_by_managed_instance
  - Added operation DatabasesOperations.import_method
  - Added operation DatabasesOperations.import_database
  - Added operation DatabasesOperations.list_inaccessible_by_server
  - Added operation group ServerDevOpsAuditSettingsOperations

**Breaking changes**

  - Removed operation ServersOperations.import_database
  - Removed operation group ManagedDatabaseRestoreDetailsOperations
  - Removed operation group ImportExportOperations

## 0.24.0 (2020-11-04)

**Features**

  - Model DataMaskingRule has a new parameter data_masking_rule_id
  - Model SyncAgent has a new parameter sync_agent_name
  - Model SyncGroup has a new parameter private_endpoint_name
  - Model SyncMember has a new parameter private_endpoint_name
  - Model ElasticPoolUpdate has a new parameter maintenance_configuration_id
  - Model Database has a new parameter storage_account_type
  - Model Database has a new parameter high_availability_replica_count
  - Model Database has a new parameter maintenance_configuration_id
  - Model Database has a new parameter secondary_type
  - Model DatabaseUpdate has a new parameter storage_account_type
  - Model DatabaseUpdate has a new parameter high_availability_replica_count
  - Model DatabaseUpdate has a new parameter maintenance_configuration_id
  - Model DatabaseUpdate has a new parameter secondary_type
  - Model RecommendedElasticPoolMetric has a new parameter date_time_property
  - Model ElasticPool has a new parameter maintenance_configuration_id
  - Added operation ManagedBackupShortTermRetentionPoliciesOperations.create_or_update
  - Added operation ManagedBackupShortTermRetentionPoliciesOperations.update
  - Added operation JobAgentsOperations.create_or_update
  - Added operation JobAgentsOperations.delete
  - Added operation JobAgentsOperations.update
  - Added operation RestorePointsOperations.create
  - Added operation ServerCommunicationLinksOperations.create_or_update
  - Added operation JobExecutionsOperations.create_or_update
  - Added operation JobExecutionsOperations.create
  - Added operation BackupShortTermRetentionPoliciesOperations.create_or_update
  - Added operation BackupShortTermRetentionPoliciesOperations.update
  - Added operation SyncGroupsOperations.refresh_hub_schema
  - Added operation SyncGroupsOperations.delete
  - Added operation SyncGroupsOperations.create_or_update
  - Added operation SyncGroupsOperations.update
  - Added operation ReplicationLinksOperations.failover
  - Added operation ReplicationLinksOperations.unlink
  - Added operation ReplicationLinksOperations.failover_allow_data_loss
  - Added operation SyncAgentsOperations.create_or_update
  - Added operation SyncAgentsOperations.delete
  - Added operation ManagedDatabasesOperations.create_or_update
  - Added operation ManagedDatabasesOperations.delete
  - Added operation ManagedDatabasesOperations.complete_restore
  - Added operation ManagedDatabasesOperations.update
  - Added operation WorkloadGroupsOperations.create_or_update
  - Added operation WorkloadGroupsOperations.delete
  - Added operation LongTermRetentionBackupsOperations.delete
  - Added operation LongTermRetentionBackupsOperations.delete_by_resource_group
  - Added operation ElasticPoolsOperations.failover
  - Added operation ElasticPoolsOperations.delete
  - Added operation ElasticPoolsOperations.create_or_update
  - Added operation ElasticPoolsOperations.update
  - Added operation ServerSecurityAlertPoliciesOperations.create_or_update
  - Added operation InstancePoolsOperations.create_or_update
  - Added operation InstancePoolsOperations.delete
  - Added operation InstancePoolsOperations.update
  - Added operation VirtualClustersOperations.delete
  - Added operation VirtualClustersOperations.update
  - Added operation ManagedInstanceAdministratorsOperations.create_or_update
  - Added operation ManagedInstanceAdministratorsOperations.delete
  - Added operation ServerKeysOperations.create_or_update
  - Added operation ServerKeysOperations.delete
  - Added operation EncryptionProtectorsOperations.create_or_update
  - Added operation EncryptionProtectorsOperations.revalidate
  - Added operation BackupLongTermRetentionPoliciesOperations.create_or_update
  - Added operation ManagedServerSecurityAlertPoliciesOperations.create_or_update
  - Added operation ManagedRestorableDroppedDatabaseBackupShortTermRetentionPoliciesOperations.create_or_update
  - Added operation ManagedRestorableDroppedDatabaseBackupShortTermRetentionPoliciesOperations.update
  - Added operation ServerAzureADAdministratorsOperations.create_or_update
  - Added operation ServerAzureADAdministratorsOperations.delete
  - Added operation ManagedInstanceLongTermRetentionPoliciesOperations.create_or_update
  - Added operation ExtendedServerBlobAuditingPoliciesOperations.create_or_update
  - Added operation PrivateEndpointConnectionsOperations.create_or_update
  - Added operation PrivateEndpointConnectionsOperations.delete
  - Added operation LongTermRetentionManagedInstanceBackupsOperations.delete
  - Added operation LongTermRetentionManagedInstanceBackupsOperations.delete_by_resource_group
  - Added operation ManagedInstancesOperations.failover
  - Added operation ManagedInstancesOperations.delete
  - Added operation ManagedInstancesOperations.create_or_update
  - Added operation ManagedInstancesOperations.update
  - Added operation SyncMembersOperations.create_or_update
  - Added operation SyncMembersOperations.delete
  - Added operation SyncMembersOperations.refresh_member_schema
  - Added operation SyncMembersOperations.update
  - Added operation ServerDnsAliasesOperations.create_or_update
  - Added operation ServerDnsAliasesOperations.delete
  - Added operation ServerDnsAliasesOperations.acquire
  - Added operation ServersOperations.create_or_update
  - Added operation ServersOperations.delete
  - Added operation ServersOperations.import_database
  - Added operation ServersOperations.update
  - Added operation ManagedDatabaseVulnerabilityAssessmentScansOperations.initiate_scan
  - Added operation WorkloadClassifiersOperations.create_or_update
  - Added operation WorkloadClassifiersOperations.delete
  - Added operation DatabaseVulnerabilityAssessmentScansOperations.initiate_scan
  - Added operation ServerBlobAuditingPoliciesOperations.create_or_update
  - Added operation DatabasesOperations.export
  - Added operation DatabasesOperations.upgrade_data_warehouse
  - Added operation DatabasesOperations.failover
  - Added operation DatabasesOperations.pause
  - Added operation DatabasesOperations.update
  - Added operation DatabasesOperations.resume
  - Added operation DatabasesOperations.create_or_update
  - Added operation DatabasesOperations.delete
  - Added operation ManagedInstanceEncryptionProtectorsOperations.create_or_update
  - Added operation ManagedInstanceEncryptionProtectorsOperations.revalidate
  - Added operation ManagedInstanceKeysOperations.create_or_update
  - Added operation ManagedInstanceKeysOperations.delete
  - Added operation ServerAzureADOnlyAuthenticationsOperations.create_or_update
  - Added operation ServerAzureADOnlyAuthenticationsOperations.delete
  - Added operation VirtualNetworkRulesOperations.create_or_update
  - Added operation VirtualNetworkRulesOperations.delete
  - Added operation TdeCertificatesOperations.create
  - Added operation ManagedInstanceTdeCertificatesOperations.create
  - Added operation FailoverGroupsOperations.force_failover_allow_data_loss
  - Added operation FailoverGroupsOperations.failover
  - Added operation FailoverGroupsOperations.update
  - Added operation FailoverGroupsOperations.create_or_update
  - Added operation FailoverGroupsOperations.delete
  - Added operation InstanceFailoverGroupsOperations.failover
  - Added operation InstanceFailoverGroupsOperations.force_failover_allow_data_loss
  - Added operation InstanceFailoverGroupsOperations.delete
  - Added operation InstanceFailoverGroupsOperations.create_or_update
  - Added operation group DatabaseOperations
  - Added operation group ManagedInstanceAzureADOnlyAuthenticationsOperations
  - Added operation group ManagedInstanceOperations
  - Added operation group ElasticPoolOperations
  - Added operation group ImportExportOperations
  - Added operation group ServerTrustGroupsOperations

**Breaking changes**

  - Operation SyncGroupsOperations.list_logs has a new signature
  - Operation JobCredentialsOperations.create_or_update has a new signature
  - Operation JobCredentialsOperations.create_or_update has a new signature
  - Operation JobTargetGroupsOperations.create_or_update has a new signature
  - Operation JobsOperations.create_or_update has a new signature
  - Operation JobsOperations.create_or_update has a new signature
  - Operation DatabasesOperations.rename has a new signature
  - Parameter database_id of model JobAgent is now required
  - Parameter server_key_type of model ManagedInstanceKey is now required
  - Parameter password of model JobCredential is now required
  - Parameter username of model JobCredential is now required
  - Parameter read_write_endpoint of model InstanceFailoverGroup is now required
  - Parameter partner_regions of model InstanceFailoverGroup is now required
  - Parameter managed_instance_pairs of model InstanceFailoverGroup is now required
  - Parameter column_name of model DataMaskingRule is now required
  - Parameter schema_name of model DataMaskingRule is now required
  - Parameter table_name of model DataMaskingRule is now required
  - Parameter start_ip_address of model FirewallRule is now required
  - Parameter end_ip_address of model FirewallRule is now required
  - Parameter members of model JobTargetGroup is now required
  - Parameter max_resource_percent of model WorkloadGroup is now required
  - Parameter min_resource_percent of model WorkloadGroup is now required
  - Parameter min_resource_percent_per_request of model WorkloadGroup is now required
  - Parameter baseline_results of model DatabaseVulnerabilityAssessmentRuleBaseline is now required
  - Parameter action of model JobStep is now required
  - Parameter target_group of model JobStep is now required
  - Parameter credential of model JobStep is now required
  - Parameter private_blob of model TdeCertificate is now required
  - Parameter server_key_type of model EncryptionProtector is now required
  - Parameter administrator_type of model ManagedInstanceAdministrator is now required
  - Parameter sid of model ManagedInstanceAdministrator is now required
  - Parameter login of model ManagedInstanceAdministrator is now required
  - Parameter storage_container_path of model ManagedInstanceVulnerabilityAssessment is now required
  - Parameter partner_server of model ServerCommunicationLink is now required
  - Parameter member_name of model WorkloadClassifier is now required
  - Parameter storage_container_path of model ServerVulnerabilityAssessment is now required
  - Parameter virtual_network_subnet_id of model VirtualNetworkRule is now required
  - Parameter server_key_type of model ServerKey is now required
  - Parameter azure_ad_only_authentication of model ServerAzureADOnlyAuthentication is now required
  - Parameter administrator_type of model ServerAzureADAdministrator is now required
  - Parameter sid of model ServerAzureADAdministrator is now required
  - Parameter login of model ServerAzureADAdministrator is now required
  - Parameter server_key_type of model ManagedInstanceEncryptionProtector is now required
  - Parameter read_write_endpoint of model FailoverGroup is now required
  - Parameter partner_servers of model FailoverGroup is now required
  - Parameter license_type of model InstancePool is now required
  - Parameter v_cores of model InstancePool is now required
  - Parameter subnet_id of model InstancePool is now required
  - Parameter state of model ManagedServerSecurityAlertPolicy is now required
  - Parameter state of model ServerSecurityAlertPolicy is now required
  - Parameter state of model ManagedDatabaseSecurityAlertPolicy is now required
  - Parameter masking_function of model DataMaskingRule is now required
  - Parameter state of model DatabaseSecurityAlertPolicy is now required
  - Parameter state of model ExtendedServerBlobAuditingPolicy is now required
  - Parameter state of model ServerBlobAuditingPolicy is now required
  - Parameter state of model ExtendedDatabaseBlobAuditingPolicy is now required
  - Parameter data_masking_state of model DataMaskingPolicy is now required
  - Parameter state of model DatabaseBlobAuditingPolicy is now required
  - Parameter connection_type of model ServerConnectionPolicy is now required
  - Operation WorkloadGroupsOperations.list_by_database has a new signature
  - Operation WorkloadGroupsOperations.get has a new signature
  - Operation WorkloadClassifiersOperations.list_by_workload_group has a new signature
  - Operation WorkloadClassifiersOperations.get has a new signature
  - Operation VirtualNetworkRulesOperations.list_by_server has a new signature
  - Operation VirtualNetworkRulesOperations.get has a new signature
  - Operation VirtualClustersOperations.list_by_resource_group has a new signature
  - Operation VirtualClustersOperations.get has a new signature
  - Operation UsagesOperations.list_by_instance_pool has a new signature
  - Operation SyncMembersOperations.list_member_schemas has a new signature
  - Operation SyncMembersOperations.list_by_sync_group has a new signature
  - Operation SyncMembersOperations.get has a new signature
  - Operation SyncGroupsOperations.trigger_sync has a new signature
  - Operation SyncGroupsOperations.list_sync_database_ids has a new signature
  - Operation SyncGroupsOperations.list_logs has a new signature
  - Operation SyncGroupsOperations.list_hub_schemas has a new signature
  - Operation SyncGroupsOperations.list_by_database has a new signature
  - Operation SyncGroupsOperations.get has a new signature
  - Operation SyncGroupsOperations.cancel_sync has a new signature
  - Operation SyncAgentsOperations.list_linked_databases has a new signature
  - Operation SyncAgentsOperations.list_by_server has a new signature
  - Operation SyncAgentsOperations.get has a new signature
  - Operation SyncAgentsOperations.generate_key has a new signature
  - Operation SubscriptionUsagesOperations.list_by_location has a new signature
  - Operation SubscriptionUsagesOperations.get has a new signature
  - Operation ServiceTierAdvisorsOperations.list_by_database has a new signature
  - Operation ServiceTierAdvisorsOperations.get has a new signature
  - Operation ServiceObjectivesOperations.list_by_server has a new signature
  - Operation ServiceObjectivesOperations.get has a new signature
  - Operation ServersOperations.list_by_resource_group has a new signature
  - Operation ServersOperations.get has a new signature
  - Operation ServerVulnerabilityAssessmentsOperations.list_by_server has a new signature
  - Operation ServerUsagesOperations.list_by_server has a new signature
  - Operation ServerSecurityAlertPoliciesOperations.list_by_server has a new signature
  - Operation ServerKeysOperations.list_by_server has a new signature
  - Operation ServerKeysOperations.get has a new signature
  - Operation ServerDnsAliasesOperations.list_by_server has a new signature
  - Operation ServerDnsAliasesOperations.get has a new signature
  - Operation ServerCommunicationLinksOperations.list_by_server has a new signature
  - Operation ServerCommunicationLinksOperations.get has a new signature
  - Operation ServerCommunicationLinksOperations.delete has a new signature
  - Operation ServerBlobAuditingPoliciesOperations.list_by_server has a new signature
  - Operation ServerBlobAuditingPoliciesOperations.get has a new signature
  - Operation ServerAzureADOnlyAuthenticationsOperations.list_by_server has a new signature
  - Operation ServerAzureADAdministratorsOperations.list_by_server has a new signature
  - Operation ServerAutomaticTuningOperations.get has a new signature
  - Operation SensitivityLabelsOperations.list_recommended_by_database has a new signature
  - Operation SensitivityLabelsOperations.list_current_by_database has a new signature
  - Operation SensitivityLabelsOperations.get has a new signature
  - Operation SensitivityLabelsOperations.enable_recommendation has a new signature
  - Operation SensitivityLabelsOperations.disable_recommendation has a new signature
  - Operation SensitivityLabelsOperations.delete has a new signature
  - Operation SensitivityLabelsOperations.create_or_update has a new signature
  - Operation RestorePointsOperations.list_by_database has a new signature
  - Operation RestorePointsOperations.get has a new signature
  - Operation RestorePointsOperations.delete has a new signature
  - Operation RestorableDroppedManagedDatabasesOperations.list_by_instance has a new signature
  - Operation RestorableDroppedManagedDatabasesOperations.get has a new signature
  - Operation RestorableDroppedDatabasesOperations.list_by_server has a new signature
  - Operation RestorableDroppedDatabasesOperations.get has a new signature
  - Operation ReplicationLinksOperations.list_by_database has a new signature
  - Operation ReplicationLinksOperations.get has a new signature
  - Operation ReplicationLinksOperations.delete has a new signature
  - Operation RecoverableManagedDatabasesOperations.list_by_instance has a new signature
  - Operation RecoverableManagedDatabasesOperations.get has a new signature
  - Operation RecoverableDatabasesOperations.list_by_server has a new signature
  - Operation RecoverableDatabasesOperations.get has a new signature
  - Operation RecommendedElasticPoolsOperations.list_metrics has a new signature
  - Operation RecommendedElasticPoolsOperations.list_by_server has a new signature
  - Operation RecommendedElasticPoolsOperations.get has a new signature
  - Operation PrivateLinkResourcesOperations.list_by_server has a new signature
  - Operation PrivateLinkResourcesOperations.get has a new signature
  - Operation PrivateEndpointConnectionsOperations.list_by_server has a new signature
  - Operation PrivateEndpointConnectionsOperations.get has a new signature
  - Operation ManagedServerSecurityAlertPoliciesOperations.list_by_instance has a new signature
  - Operation ManagedRestorableDroppedDatabaseBackupShortTermRetentionPoliciesOperations.list_by_restorable_dropped_database has a new signature
  - Operation ManagedInstancesOperations.list_by_resource_group has a new signature
  - Operation ManagedInstancesOperations.list_by_instance_pool has a new signature
  - Operation ManagedInstancesOperations.get has a new signature
  - Operation ManagedInstanceVulnerabilityAssessmentsOperations.list_by_instance has a new signature
  - Operation ManagedInstanceLongTermRetentionPoliciesOperations.list_by_database has a new signature
  - Operation ManagedInstanceKeysOperations.list_by_instance has a new signature
  - Operation ManagedInstanceKeysOperations.get has a new signature
  - Operation ManagedInstanceEncryptionProtectorsOperations.list_by_instance has a new signature
  - Operation ManagedInstanceAdministratorsOperations.list_by_instance has a new signature
  - Operation ManagedInstanceAdministratorsOperations.get has a new signature
  - Operation ManagedDatabasesOperations.list_inaccessible_by_instance has a new signature
  - Operation ManagedDatabasesOperations.list_by_instance has a new signature
  - Operation ManagedDatabasesOperations.get has a new signature
  - Operation ManagedDatabaseVulnerabilityAssessmentsOperations.list_by_database has a new signature
  - Operation ManagedDatabaseVulnerabilityAssessmentScansOperations.get has a new signature
  - Operation ManagedDatabaseVulnerabilityAssessmentScansOperations.get has a new signature
  - Operation ManagedDatabaseVulnerabilityAssessmentRuleBaselinesOperations.get has a new signature
  - Operation ManagedDatabaseVulnerabilityAssessmentRuleBaselinesOperations.get has a new signature
  - Operation ManagedDatabaseVulnerabilityAssessmentRuleBaselinesOperations.delete has a new signature
  - Operation ManagedDatabaseVulnerabilityAssessmentRuleBaselinesOperations.delete has a new signature
  - Operation ManagedDatabaseSensitivityLabelsOperations.list_recommended_by_database has a new signature
  - Operation ManagedDatabaseSensitivityLabelsOperations.list_current_by_database has a new signature
  - Operation ManagedDatabaseSensitivityLabelsOperations.get has a new signature
  - Operation ManagedDatabaseSensitivityLabelsOperations.enable_recommendation has a new signature
  - Operation ManagedDatabaseSensitivityLabelsOperations.disable_recommendation has a new signature
  - Operation ManagedDatabaseSensitivityLabelsOperations.delete has a new signature
  - Operation ManagedDatabaseSensitivityLabelsOperations.create_or_update has a new signature
  - Operation ManagedDatabaseSecurityAlertPoliciesOperations.list_by_database has a new signature
  - Operation ManagedBackupShortTermRetentionPoliciesOperations.list_by_database has a new signature
  - Operation LongTermRetentionManagedInstanceBackupsOperations.list_by_resource_group_location has a new signature
  - Operation LongTermRetentionManagedInstanceBackupsOperations.list_by_resource_group_instance has a new signature
  - Operation LongTermRetentionManagedInstanceBackupsOperations.list_by_resource_group_database has a new signature
  - Operation LongTermRetentionManagedInstanceBackupsOperations.list_by_location has a new signature
  - Operation LongTermRetentionManagedInstanceBackupsOperations.list_by_instance has a new signature
  - Operation LongTermRetentionManagedInstanceBackupsOperations.list_by_database has a new signature
  - Operation LongTermRetentionManagedInstanceBackupsOperations.get_by_resource_group has a new signature
  - Operation LongTermRetentionManagedInstanceBackupsOperations.get has a new signature
  - Operation LongTermRetentionBackupsOperations.list_by_server has a new signature
  - Operation LongTermRetentionBackupsOperations.list_by_resource_group_server has a new signature
  - Operation LongTermRetentionBackupsOperations.list_by_resource_group_location has a new signature
  - Operation LongTermRetentionBackupsOperations.list_by_resource_group_database has a new signature
  - Operation LongTermRetentionBackupsOperations.list_by_location has a new signature
  - Operation LongTermRetentionBackupsOperations.list_by_database has a new signature
  - Operation LongTermRetentionBackupsOperations.get_by_resource_group has a new signature
  - Operation LongTermRetentionBackupsOperations.get has a new signature
  - Operation JobsOperations.list_by_agent has a new signature
  - Operation JobsOperations.get has a new signature
  - Operation JobsOperations.delete has a new signature
  - Operation JobVersionsOperations.list_by_job has a new signature
  - Operation JobVersionsOperations.get has a new signature
  - Operation JobTargetGroupsOperations.list_by_agent has a new signature
  - Operation JobTargetGroupsOperations.get has a new signature
  - Operation JobTargetGroupsOperations.delete has a new signature
  - Operation JobTargetGroupsOperations.create_or_update has a new signature
  - Operation JobTargetExecutionsOperations.list_by_step has a new signature
  - Operation JobTargetExecutionsOperations.list_by_job_execution has a new signature
  - Operation JobTargetExecutionsOperations.get has a new signature
  - Operation JobStepsOperations.list_by_version has a new signature
  - Operation JobStepsOperations.list_by_job has a new signature
  - Operation JobStepsOperations.get_by_version has a new signature
  - Operation JobStepsOperations.get has a new signature
  - Operation JobStepsOperations.delete has a new signature
  - Operation JobStepsOperations.create_or_update has a new signature
  - Operation JobStepExecutionsOperations.list_by_job_execution has a new signature
  - Operation JobStepExecutionsOperations.get has a new signature
  - Operation JobExecutionsOperations.list_by_job has a new signature
  - Operation JobExecutionsOperations.list_by_agent has a new signature
  - Operation JobExecutionsOperations.get has a new signature
  - Operation JobExecutionsOperations.cancel has a new signature
  - Operation JobCredentialsOperations.list_by_agent has a new signature
  - Operation JobCredentialsOperations.get has a new signature
  - Operation JobCredentialsOperations.delete has a new signature
  - Operation JobAgentsOperations.list_by_server has a new signature
  - Operation JobAgentsOperations.get has a new signature
  - Operation InstancePoolsOperations.list_by_resource_group has a new signature
  - Operation InstancePoolsOperations.get has a new signature
  - Operation GeoBackupPoliciesOperations.list_by_database has a new signature
  - Operation FirewallRulesOperations.list_by_server has a new signature
  - Operation FirewallRulesOperations.get has a new signature
  - Operation FirewallRulesOperations.delete has a new signature
  - Operation ExtendedServerBlobAuditingPoliciesOperations.list_by_server has a new signature
  - Operation ExtendedServerBlobAuditingPoliciesOperations.get has a new signature
  - Operation ExtendedDatabaseBlobAuditingPoliciesOperations.list_by_database has a new signature
  - Operation ExtendedDatabaseBlobAuditingPoliciesOperations.get has a new signature
  - Operation ExtendedDatabaseBlobAuditingPoliciesOperations.create_or_update has a new signature
  - Operation EncryptionProtectorsOperations.list_by_server has a new signature
  - Operation ElasticPoolsOperations.list_metrics has a new signature
  - Operation ElasticPoolsOperations.list_metric_definitions has a new signature
  - Operation ElasticPoolsOperations.list_by_server has a new signature
  - Operation ElasticPoolsOperations.get has a new signature
  - Operation ElasticPoolDatabaseActivitiesOperations.list_by_elastic_pool has a new signature
  - Operation ElasticPoolActivitiesOperations.list_by_elastic_pool has a new signature
  - Operation DatabasesOperations.rename has a new signature
  - Operation DatabasesOperations.list_metrics has a new signature
  - Operation DatabasesOperations.list_metric_definitions has a new signature
  - Operation DatabasesOperations.list_by_server has a new signature
  - Operation DatabasesOperations.list_by_elastic_pool has a new signature
  - Operation DatabasesOperations.get has a new signature
  - Operation DatabaseVulnerabilityAssessmentsOperations.list_by_database has a new signature
  - Operation DatabaseVulnerabilityAssessmentRuleBaselinesOperations.get has a new signature
  - Operation DatabaseVulnerabilityAssessmentRuleBaselinesOperations.get has a new signature
  - Operation DatabaseVulnerabilityAssessmentRuleBaselinesOperations.delete has a new signature
  - Operation DatabaseVulnerabilityAssessmentRuleBaselinesOperations.delete has a new signature
  - Operation DatabaseUsagesOperations.list_by_database has a new signature
  - Operation DatabaseBlobAuditingPoliciesOperations.list_by_database has a new signature
  - Operation DatabaseBlobAuditingPoliciesOperations.get has a new signature
  - Operation DatabaseBlobAuditingPoliciesOperations.create_or_update has a new signature
  - Operation DatabaseAutomaticTuningOperations.get has a new signature
  - Operation DataMaskingRulesOperations.list_by_database has a new signature
  - Operation DataMaskingRulesOperations.create_or_update has a new signature
  - Operation DataMaskingPoliciesOperations.get has a new signature
  - Operation CapabilitiesOperations.list_by_location has a new signature
  - Operation BackupShortTermRetentionPoliciesOperations.list_by_database has a new signature
  - Operation BackupLongTermRetentionPoliciesOperations.list_by_database has a new signature
  - Operation ManagedBackupShortTermRetentionPoliciesOperations.get has a new signature
  - Operation TransparentDataEncryptionsOperations.create_or_update has a new signature
  - Operation TransparentDataEncryptionsOperations.get has a new signature
  - Operation TransparentDataEncryptionActivitiesOperations.list_by_configuration has a new signature
  - Operation DatabaseVulnerabilityAssessmentsOperations.create_or_update has a new signature
  - Operation DatabaseVulnerabilityAssessmentsOperations.delete has a new signature
  - Operation DatabaseVulnerabilityAssessmentsOperations.get has a new signature
  - Operation ServerAutomaticTuningOperations.update has a new signature
  - Operation BackupShortTermRetentionPoliciesOperations.get has a new signature
  - Operation FirewallRulesOperations.create_or_update has a new signature
  - Operation ManagedInstanceVulnerabilityAssessmentsOperations.create_or_update has a new signature
  - Operation ManagedInstanceVulnerabilityAssessmentsOperations.delete has a new signature
  - Operation ManagedInstanceVulnerabilityAssessmentsOperations.get has a new signature
  - Operation ManagedDatabaseVulnerabilityAssessmentRuleBaselinesOperations.create_or_update has a new signature
  - Operation ServerSecurityAlertPoliciesOperations.get has a new signature
  - Operation InstancePoolsOperations.list has a new signature
  - Operation ManagedDatabaseRestoreDetailsOperations.get has a new signature
  - Operation ManagedDatabaseSecurityAlertPoliciesOperations.create_or_update has a new signature
  - Operation ManagedDatabaseSecurityAlertPoliciesOperations.get has a new signature
  - Operation GeoBackupPoliciesOperations.create_or_update has a new signature
  - Operation GeoBackupPoliciesOperations.get has a new signature
  - Operation VirtualClustersOperations.list has a new signature
  - Operation DatabaseVulnerabilityAssessmentRuleBaselinesOperations.create_or_update has a new signature
  - Operation EncryptionProtectorsOperations.get has a new signature
  - Operation BackupLongTermRetentionPoliciesOperations.get has a new signature
  - Operation DatabaseThreatDetectionPoliciesOperations.create_or_update has a new signature
  - Operation DatabaseThreatDetectionPoliciesOperations.get has a new signature
  - Operation DataMaskingPoliciesOperations.create_or_update has a new signature
  - Operation ManagedServerSecurityAlertPoliciesOperations.get has a new signature
  - Operation ManagedRestorableDroppedDatabaseBackupShortTermRetentionPoliciesOperations.get has a new signature
  - Operation ServerAzureADAdministratorsOperations.get has a new signature
  - Operation ServerVulnerabilityAssessmentsOperations.create_or_update has a new signature
  - Operation ServerVulnerabilityAssessmentsOperations.delete has a new signature
  - Operation ServerVulnerabilityAssessmentsOperations.get has a new signature
  - Operation ManagedInstanceLongTermRetentionPoliciesOperations.get has a new signature
  - Operation ManagedDatabaseVulnerabilityAssessmentsOperations.create_or_update has a new signature
  - Operation ManagedDatabaseVulnerabilityAssessmentsOperations.delete has a new signature
  - Operation ManagedDatabaseVulnerabilityAssessmentsOperations.get has a new signature
  - Operation ManagedInstancesOperations.list has a new signature
  - Operation ServersOperations.check_name_availability has a new signature
  - Operation ServersOperations.list has a new signature
  - Operation DatabaseAutomaticTuningOperations.update has a new signature
  - Operation ManagedDatabaseVulnerabilityAssessmentScansOperations.export has a new signature
  - Operation ManagedDatabaseVulnerabilityAssessmentScansOperations.list_by_database has a new signature
  - Operation DatabaseVulnerabilityAssessmentScansOperations.export has a new signature
  - Operation DatabaseVulnerabilityAssessmentScansOperations.list_by_database has a new signature
  - Operation DatabaseVulnerabilityAssessmentScansOperations.get has a new signature
  - Operation ManagedInstanceEncryptionProtectorsOperations.get has a new signature
  - Operation ServerConnectionPoliciesOperations.create_or_update has a new signature
  - Operation ServerConnectionPoliciesOperations.get has a new signature
  - Operation Operations.list has a new signature
  - Operation ServerAzureADOnlyAuthenticationsOperations.get has a new signature
  - Model BackupShortTermRetentionPolicy no longer has parameter diff_backup_interval_in_hours
  - Model DataMaskingRule no longer has parameter id_properties_id
  - Model SyncAgent no longer has parameter name_properties_name
  - Model Database no longer has parameter read_replica_count
  - Model DatabaseUpdate no longer has parameter read_replica_count
  - Model RecommendedElasticPoolMetric no longer has parameter date_time
  - Removed operation ManagedBackupShortTermRetentionPoliciesOperations.begin_create_or_update
  - Removed operation ManagedBackupShortTermRetentionPoliciesOperations.begin_update
  - Removed operation JobAgentsOperations.begin_create_or_update
  - Removed operation JobAgentsOperations.begin_update
  - Removed operation JobAgentsOperations.begin_delete
  - Removed operation RestorePointsOperations.begin_create
  - Removed operation ServerCommunicationLinksOperations.begin_create_or_update
  - Removed operation JobExecutionsOperations.begin_create_or_update
  - Removed operation JobExecutionsOperations.begin_create
  - Removed operation BackupShortTermRetentionPoliciesOperations.begin_create_or_update
  - Removed operation BackupShortTermRetentionPoliciesOperations.begin_update
  - Removed operation SyncGroupsOperations.begin_create_or_update
  - Removed operation SyncGroupsOperations.begin_refresh_hub_schema
  - Removed operation SyncGroupsOperations.begin_update
  - Removed operation SyncGroupsOperations.begin_delete
  - Removed operation ReplicationLinksOperations.begin_failover_allow_data_loss
  - Removed operation ReplicationLinksOperations.begin_failover
  - Removed operation ReplicationLinksOperations.begin_unlink
  - Removed operation SyncAgentsOperations.begin_create_or_update
  - Removed operation SyncAgentsOperations.begin_delete
  - Removed operation ManagedDatabasesOperations.begin_create_or_update
  - Removed operation ManagedDatabasesOperations.begin_complete_restore
  - Removed operation ManagedDatabasesOperations.begin_update
  - Removed operation ManagedDatabasesOperations.begin_delete
  - Removed operation WorkloadGroupsOperations.begin_create_or_update
  - Removed operation WorkloadGroupsOperations.begin_delete
  - Removed operation LongTermRetentionBackupsOperations.begin_delete_by_resource_group
  - Removed operation LongTermRetentionBackupsOperations.begin_delete
  - Removed operation ElasticPoolsOperations.begin_create_or_update
  - Removed operation ElasticPoolsOperations.begin_failover
  - Removed operation ElasticPoolsOperations.begin_update
  - Removed operation ElasticPoolsOperations.begin_delete
  - Removed operation ServerSecurityAlertPoliciesOperations.begin_create_or_update
  - Removed operation InstancePoolsOperations.begin_create_or_update
  - Removed operation InstancePoolsOperations.begin_update
  - Removed operation InstancePoolsOperations.begin_delete
  - Removed operation VirtualClustersOperations.begin_update
  - Removed operation VirtualClustersOperations.begin_delete
  - Removed operation ManagedInstanceAdministratorsOperations.begin_create_or_update
  - Removed operation ManagedInstanceAdministratorsOperations.begin_delete
  - Removed operation ServerKeysOperations.begin_create_or_update
  - Removed operation ServerKeysOperations.begin_delete
  - Removed operation EncryptionProtectorsOperations.begin_revalidate
  - Removed operation EncryptionProtectorsOperations.begin_create_or_update
  - Removed operation BackupLongTermRetentionPoliciesOperations.begin_create_or_update
  - Removed operation ManagedServerSecurityAlertPoliciesOperations.begin_create_or_update
  - Removed operation ManagedRestorableDroppedDatabaseBackupShortTermRetentionPoliciesOperations.begin_create_or_update
  - Removed operation ManagedRestorableDroppedDatabaseBackupShortTermRetentionPoliciesOperations.begin_update
  - Removed operation ServerAzureADAdministratorsOperations.begin_create_or_update
  - Removed operation ServerAzureADAdministratorsOperations.begin_delete
  - Removed operation ManagedInstanceLongTermRetentionPoliciesOperations.begin_create_or_update
  - Removed operation ExtendedServerBlobAuditingPoliciesOperations.begin_create_or_update
  - Removed operation PrivateEndpointConnectionsOperations.begin_create_or_update
  - Removed operation PrivateEndpointConnectionsOperations.begin_delete
  - Removed operation LongTermRetentionManagedInstanceBackupsOperations.begin_delete_by_resource_group
  - Removed operation LongTermRetentionManagedInstanceBackupsOperations.begin_delete
  - Removed operation ManagedInstancesOperations.begin_create_or_update
  - Removed operation ManagedInstancesOperations.begin_failover
  - Removed operation ManagedInstancesOperations.begin_update
  - Removed operation ManagedInstancesOperations.begin_delete
  - Removed operation SyncMembersOperations.begin_refresh_member_schema
  - Removed operation SyncMembersOperations.begin_create_or_update
  - Removed operation SyncMembersOperations.begin_update
  - Removed operation SyncMembersOperations.begin_delete
  - Removed operation ServerDnsAliasesOperations.begin_acquire
  - Removed operation ServerDnsAliasesOperations.begin_create_or_update
  - Removed operation ServerDnsAliasesOperations.begin_delete
  - Removed operation ServersOperations.begin_create_or_update
  - Removed operation ServersOperations.begin_update
  - Removed operation ServersOperations.begin_delete
  - Removed operation ManagedDatabaseVulnerabilityAssessmentScansOperations.begin_initiate_scan
  - Removed operation WorkloadClassifiersOperations.begin_create_or_update
  - Removed operation WorkloadClassifiersOperations.begin_delete
  - Removed operation DatabaseVulnerabilityAssessmentScansOperations.begin_initiate_scan
  - Removed operation ServerBlobAuditingPoliciesOperations.begin_create_or_update
  - Removed operation DatabasesOperations.begin_create_or_update
  - Removed operation DatabasesOperations.begin_delete
  - Removed operation DatabasesOperations.begin_create_import_operation
  - Removed operation DatabasesOperations.begin_failover
  - Removed operation DatabasesOperations.begin_export
  - Removed operation DatabasesOperations.begin_import_method
  - Removed operation DatabasesOperations.begin_pause
  - Removed operation DatabasesOperations.begin_update
  - Removed operation DatabasesOperations.begin_upgrade_data_warehouse
  - Removed operation DatabasesOperations.begin_resume
  - Removed operation ManagedInstanceEncryptionProtectorsOperations.begin_revalidate
  - Removed operation ManagedInstanceEncryptionProtectorsOperations.begin_create_or_update
  - Removed operation ManagedInstanceKeysOperations.begin_create_or_update
  - Removed operation ManagedInstanceKeysOperations.begin_delete
  - Removed operation ServerAzureADOnlyAuthenticationsOperations.begin_create_or_update
  - Removed operation ServerAzureADOnlyAuthenticationsOperations.begin_delete
  - Removed operation VirtualNetworkRulesOperations.begin_create_or_update
  - Removed operation VirtualNetworkRulesOperations.begin_delete
  - Removed operation TdeCertificatesOperations.begin_create
  - Removed operation ManagedInstanceTdeCertificatesOperations.begin_create
  - Removed operation FailoverGroupsOperations.begin_create_or_update
  - Removed operation FailoverGroupsOperations.begin_delete
  - Removed operation FailoverGroupsOperations.begin_failover
  - Removed operation FailoverGroupsOperations.begin_update
  - Removed operation FailoverGroupsOperations.begin_force_failover_allow_data_loss
  - Removed operation InstanceFailoverGroupsOperations.begin_create_or_update
  - Removed operation InstanceFailoverGroupsOperations.begin_failover
  - Removed operation InstanceFailoverGroupsOperations.begin_force_failover_allow_data_loss
  - Removed operation InstanceFailoverGroupsOperations.begin_delete
  - Removed operation group ManagedInstanceOperationsOperations
  - Removed operation group DatabaseOperationsOperations
  - Removed operation group ElasticPoolOperationsOperations
  
## 0.23.0 (2020-10-29)

**Features**

  - Model Database has a new parameter secondary_type
  - Model Database has a new parameter maintenance_configuration_id
  - Model Database has a new parameter high_availability_replica_count
  - Model DatabaseUpdate has a new parameter secondary_type
  - Model DatabaseUpdate has a new parameter maintenance_configuration_id
  - Model DatabaseUpdate has a new parameter high_availability_replica_count
  - Model ElasticPoolUpdate has a new parameter maintenance_configuration_id
  - Model ElasticPool has a new parameter maintenance_configuration_id

**Breaking changes**

  - Model Database no longer has parameter read_replica_count
  - Model DatabaseUpdate no longer has parameter read_replica_count
  - Removed operation DatabasesOperations.list_inaccessible_by_server
  
## 0.22.0 (2020-10-09)

**Features**

  - Model BackupShortTermRetentionPolicy has a new parameter diff_backup_interval_in_hours
  - Model ManagedInstance has a new parameter provisioning_state
  - Model ManagedInstanceUpdate has a new parameter provisioning_state
  - Added operation group ServerAzureADOnlyAuthenticationsOperations

**Breaking changes**

  - Operation BackupShortTermRetentionPoliciesOperations.create_or_update has a new signature
  - Operation BackupShortTermRetentionPoliciesOperations.update has a new signature
  - Removed operation ServerAzureADAdministratorsOperations.disable_azure_ad_only_authentication
  
## 0.21.0 (2020-09-03)

**Features**

  - Model DatabaseUpdate has a new parameter storage_account_type
  - Model Database has a new parameter storage_account_type
  - Model BackupShortTermRetentionPolicy has a new parameter diff_backup_interval_in_hours
  - Model ManagedInstance has a new parameter storage_account_type
  - Model ManagedInstance has a new parameter provisioning_state
  - Model ManagedInstanceUpdate has a new parameter storage_account_type
  - Model ManagedInstanceUpdate has a new parameter provisioning_state
  - Added operation DatabasesOperations.list_inaccessible_by_server
  - Added operation ServersOperations.import_database
  - Added operation group ImportExportOperations
  - Added operation group ServerAzureADOnlyAuthenticationsOperations
  - Added operation group ManagedInstanceAzureADOnlyAuthenticationsOperations

**Breaking changes**

  - Operation BackupShortTermRetentionPoliciesOperations.create_or_update has a new signature
  - Operation BackupShortTermRetentionPoliciesOperations.update has a new signature
  - Removed operation DatabasesOperations.import_method
  - Removed operation DatabasesOperations.create_import_operation
  - Removed operation ServerAzureADAdministratorsOperations.disable_azure_ad_only_authentication

## 0.20.0 (2020-06-22)

**Features**

  - Model ManagedDatabase has a new parameter last_backup_name
  - Model ManagedDatabase has a new parameter auto_complete_restore
  - Model ManagedDatabaseUpdate has a new parameter last_backup_name
  - Model ManagedDatabaseUpdate has a new parameter auto_complete_restore
  - Model ManagedInstanceOperation has a new parameter operation_parameters
  - Model ManagedInstanceOperation has a new parameter operation_steps

## 0.19.0 (2020-06-22)

**Features**

  - Model SyncGroup has a new parameter use_private_link_connection
  - Model ManagedInstanceUpdate has a new parameter maintenance_configuration_id
  - Model SyncMember has a new parameter use_private_link_connection
  - Model SyncMember has a new parameter sync_member_azure_database_resource_id
  - Model ManagedInstance has a new parameter maintenance_configuration_id
  - Added operation ExtendedDatabaseBlobAuditingPoliciesOperations.list_by_database
  - Added operation ManagedInstancesOperations.failover
  - Added operation ReplicationLinksOperations.unlink
  - Added operation ExtendedServerBlobAuditingPoliciesOperations.list_by_server

## 0.18.0 (2020-03-23)

**Features**

  - Added operation group ManagedInstanceOperations

## 0.17.0 (2020-03-02)

**Features**

  - Model ManagedInstanceUpdate has a new parameter minimal_tls_version
  - Model ServerAzureADAdministrator has a new parameter azure_ad_only_authentication
  - Model ManagedDatabase has a new parameter long_term_retention_backup_resource_id
  - Model ManagedDatabaseUpdate has a new parameter long_term_retention_backup_resource_id
  - Model SensitivityLabel has a new parameter rank
  - Model ServerUpdate has a new parameter private_endpoint_connections
  - Model ServerUpdate has a new parameter minimal_tls_version
  - Model ServerUpdate has a new parameter public_network_access
  - Model Server has a new parameter private_endpoint_connections
  - Model Server has a new parameter minimal_tls_version
  - Model Server has a new parameter public_network_access
  - Model ManagedInstance has a new parameter minimal_tls_version
  - Added operation ServerAzureADAdministratorsOperations.disable_azure_ad_only_authentication
  - Added operation ManagedDatabasesOperations.list_inaccessible_by_instance
  - Added operation group ManagedInstanceLongTermRetentionPoliciesOperations
  - Added operation group LongTermRetentionManagedInstanceBackupsOperations

## 0.16.0 (2019-12-17)

**Features**

  - Model ExtendedServerBlobAuditingPolicy has a new parameter
    queue_delay_ms
  - Model EditionCapability has a new parameter read_scale
  - Model EditionCapability has a new parameter
    supported_storage_capabilities
  - Model ServiceObjectiveCapability has a new parameter compute_model
  - Model ServiceObjectiveCapability has a new parameter
    supported_auto_pause_delay
  - Model ServiceObjectiveCapability has a new parameter zone_redundant
  - Model ServiceObjectiveCapability has a new parameter
    supported_min_capacities
  - Model ManagedInstanceVersionCapability has a new parameter
    supported_instance_pool_editions
  - Model DatabaseBlobAuditingPolicy has a new parameter
    queue_delay_ms
  - Model ExtendedDatabaseBlobAuditingPolicy has a new parameter
    queue_delay_ms
  - Model ManagedInstanceVcoresCapability has a new parameter
    supported_storage_sizes
  - Model ManagedInstanceVcoresCapability has a new parameter
    instance_pool_supported
  - Model ManagedInstanceVcoresCapability has a new parameter
    standalone_supported
  - Model ManagedInstanceVcoresCapability has a new parameter
    included_max_size
  - Model ServerBlobAuditingPolicy has a new parameter queue_delay_ms
  - Model ElasticPoolPerformanceLevelCapability has a new parameter
    zone_redundant
  - Added operation group WorkloadGroupsOperations
  - Added operation group WorkloadClassifiersOperations

**Breaking changes**

  - Operation ServerAzureADAdministratorsOperations.create_or_update
    has a new signature
  - Model ManagedInstanceFamilyCapability no longer has parameter
    supported_storage_sizes
  - Model ManagedInstanceFamilyCapability no longer has parameter
    included_max_size

## 0.15.0 (2019-11-12)

**Breaking changes**

  - Operation DatabasesOperations.failover has a new signature
  - Operation ManagedInstanceAdministratorsOperations.get has a new
    signature
  - Operation ManagedInstanceAdministratorsOperations.delete has a new
    signature
  - Operation ManagedInstanceAdministratorsOperations.create_or_update
    has a new signature

## 0.14.0 (2019-10-04)

**Features**

  - Added operation
    ServerBlobAuditingPoliciesOperations.list_by_server
  - Added operation ManagedDatabasesOperations.complete_restore
  - Added operation
    DatabaseBlobAuditingPoliciesOperations.list_by_database
  - Added operation group ManagedDatabaseRestoreDetailsOperations

## 0.13.0 (2019-09-03)

**Features**

  - Model ManagedInstanceUpdate has a new parameter
    source_managed_instance_id
  - Model ManagedInstanceUpdate has a new parameter instance_pool_id
  - Model ManagedInstanceUpdate has a new parameter
    restore_point_in_time
  - Model ManagedInstanceUpdate has a new parameter
    managed_instance_create_mode
  - Model SensitivityLabel has a new parameter is_disabled
  - Model Database has a new parameter paused_date
  - Model Database has a new parameter read_replica_count
  - Model Database has a new parameter resumed_date
  - Model Database has a new parameter auto_pause_delay
  - Model Database has a new parameter min_capacity
  - Model ManagedInstance has a new parameter
    source_managed_instance_id
  - Model ManagedInstance has a new parameter instance_pool_id
  - Model ManagedInstance has a new parameter restore_point_in_time
  - Model ManagedInstance has a new parameter
    managed_instance_create_mode
  - Model DatabaseUpdate has a new parameter paused_date
  - Model DatabaseUpdate has a new parameter read_replica_count
  - Model DatabaseUpdate has a new parameter resumed_date
  - Model DatabaseUpdate has a new parameter auto_pause_delay
  - Model DatabaseUpdate has a new parameter min_capacity
  - Added operation
    ManagedInstanceEncryptionProtectorsOperations.revalidate
  - Added operation
    ManagedDatabaseSensitivityLabelsOperations.enable_recommendation
  - Added operation
    ManagedDatabaseSensitivityLabelsOperations.disable_recommendation
  - Added operation ElasticPoolsOperations.failover
  - Added operation ManagedInstancesOperations.list_by_instance_pool
  - Added operation DatabasesOperations.failover
  - Added operation
    LongTermRetentionBackupsOperations.get_by_resource_group
  - Added operation
    LongTermRetentionBackupsOperations.list_by_resource_group_server
  - Added operation
    LongTermRetentionBackupsOperations.delete_by_resource_group
  - Added operation
    LongTermRetentionBackupsOperations.list_by_resource_group_location
  - Added operation
    LongTermRetentionBackupsOperations.list_by_resource_group_database
  - Added operation SensitivityLabelsOperations.enable_recommendation
  - Added operation SensitivityLabelsOperations.disable_recommendation
  - Added operation EncryptionProtectorsOperations.revalidate
  - Added operation group InstancePoolsOperations
  - Added operation group ManagedInstanceAdministratorsOperations
  - Added operation group UsagesOperations
  - Added operation group PrivateLinkResourcesOperations
  - Added operation group PrivateEndpointConnectionsOperations

**Breaking changes**

  - Operation
    ManagedDatabaseSensitivityLabelsOperations.list_recommended_by_database
    has a new signature
  - Operation
    SensitivityLabelsOperations.list_recommended_by_database has a
    new signature
  - Operation EncryptionProtectorsOperations.create_or_update has a
    new signature

**General breaking changes**

This version uses a next-generation code generator that *might*
introduce breaking changes if from some import. In summary, some modules
were incorrectly visible/importable and have been renamed. This fixed
several issues caused by usage of classes that were not supposed to be
used in the first place.

  - SqlManagementClient cannot be imported from
    `azure.mgmt.sql.sql_management_client` anymore (import from
    `azure.mgmt.sqlmanagement` works like before)
  - SqlManagementClientConfiguration import has been moved from
    `azure.mgmt.sqlmanagement.sql_management_client` to
    `azure.mgmt.sqlmanagement`
  - A model `MyClass` from a "models" sub-module cannot be imported
    anymore using `azure.mgmt.sqlmanagement.models.my_class` (import
    from `azure.mgmt.sqlmanagement.models` works like before)
  - An operation class `MyClassOperations` from an `operations`
    sub-module cannot be imported anymore using
    `azure.mgmt.sqlmanagement.operations.my_class_operations`
    (import from `azure.mgmt.sqlmanagement.operations` works like
    before)

Last but not least, HTTP connection pooling is now enabled by default.
You should always use a client as a context manager, or call close(), or
use no more than one client per process.

## 0.12.0 (2019-03-28)

**Features**

  - Model ManagedDatabase has a new parameter recoverable_database_id
  - Model ManagedDatabase has a new parameter
    restorable_dropped_database_id
  - Model ServerSecurityAlertPolicy has a new parameter creation_time
  - Model ManagedInstanceUpdate has a new parameter
    public_data_endpoint_enabled
  - Model ManagedInstanceUpdate has a new parameter proxy_override
  - Model ManagedInstanceUpdate has a new parameter timezone_id
  - Model ManagedDatabaseUpdate has a new parameter
    recoverable_database_id
  - Model ManagedDatabaseUpdate has a new parameter
    restorable_dropped_database_id
  - Model ManagedInstance has a new parameter
    public_data_endpoint_enabled
  - Model ManagedInstance has a new parameter proxy_override
  - Model ManagedInstance has a new parameter timezone_id
  - Added operation group ManagedServerSecurityAlertPoliciesOperations
  - Added operation group VirtualClustersOperations
  - Added operation group
    ManagedRestorableDroppedDatabaseBackupShortTermRetentionPoliciesOperations
  - Added operation group RestorableDroppedManagedDatabasesOperations
  - Added operation group ManagedDatabaseSensitivityLabelsOperations
  - Added operation group RecoverableManagedDatabasesOperations
  - Added operation group ServerVulnerabilityAssessmentsOperations
  - Added operation group
    ManagedInstanceVulnerabilityAssessmentsOperations
  - Added operation group ManagedDatabaseSecurityAlertPoliciesOperations
  - Added operation group SensitivityLabelsOperations

## 0.11.0 (2018-11-08)

**Features**

  - Model ServerBlobAuditingPolicy has a new parameter
    is_azure_monitor_target_enabled
  - Model ExtendedServerBlobAuditingPolicy has a new parameter
    is_azure_monitor_target_enabled
  - Model DatabaseBlobAuditingPolicy has a new parameter
    is_azure_monitor_target_enabled
  - Model ExtendedDatabaseBlobAuditingPolicy has a new parameter
    is_azure_monitor_target_enabled
  - Added operation
    DatabaseVulnerabilityAssessmentsOperations.list_by_database
  - Added operation
    ManagedDatabaseVulnerabilityAssessmentsOperations.list_by_database
  - Added operation group
    ManagedBackupShortTermRetentionPoliciesOperations

## 0.10.0 (2018-10-18)

**Features**

  - Model DatabaseVulnerabilityAssessment has a new parameter
    storage_account_access_key
  - Model ManagedInstanceUpdate has a new parameter dns_zone_partner
  - Model ManagedInstanceUpdate has a new parameter collation
  - Model ManagedInstanceUpdate has a new parameter dns_zone
  - Model ManagedInstance has a new parameter dns_zone_partner
  - Model ManagedInstance has a new parameter collation
  - Model ManagedInstance has a new parameter dns_zone
  - Added operation
    BackupShortTermRetentionPoliciesOperations.list_by_database
  - Added operation group
    ManagedDatabaseVulnerabilityAssessmentsOperations
  - Added operation group ExtendedDatabaseBlobAuditingPoliciesOperations
  - Added operation group TdeCertificatesOperations
  - Added operation group ManagedInstanceKeysOperations
  - Added operation group ServerBlobAuditingPoliciesOperations
  - Added operation group ManagedInstanceEncryptionProtectorsOperations
  - Added operation group ExtendedServerBlobAuditingPoliciesOperations
  - Added operation group ServerSecurityAlertPoliciesOperations
  - Added operation group
    ManagedDatabaseVulnerabilityAssessmentScansOperations
  - Added operation group ManagedInstanceTdeCertificatesOperations
  - Added operation group
    ManagedDatabaseVulnerabilityAssessmentRuleBaselinesOperations

**Breaking changes**

  - Operation
    DatabaseVulnerabilityAssessmentRuleBaselinesOperations.delete has a
    new signature
  - Operation DatabaseVulnerabilityAssessmentRuleBaselinesOperations.get
    has a new signature
  - Operation
    DatabaseVulnerabilityAssessmentRuleBaselinesOperations.create_or_update
    has a new signature

**Note**

  - azure-mgmt-nspkg is not installed anymore on Python 3 (PEP420-based
    namespace package)

## 0.9.1 (2018-05-24)

**Features**

  - Managed instances, databases, and failover groups
  - Vulnerability assessments
  - Backup short term retention policies
  - Elastic Jobs

## 0.9.0 (2018-04-25)

**General Breaking changes**

This version uses a next-generation code generator that *might*
introduce breaking changes.

  - Model signatures now use only keyword-argument syntax. All
    positional arguments must be re-written as keyword-arguments. To
    keep auto-completion in most cases, models are now generated for
    Python 2 and Python 3. Python 3 uses the "*" syntax for
    keyword-only arguments.
  - Enum types now use the "str" mixin (class AzureEnum(str, Enum)) to
    improve the behavior when unrecognized enum values are encountered.
    While this is not a breaking change, the distinctions are important,
    and are documented here:
    <https://docs.python.org/3/library/enum.html#others> At a glance:
      - "is" should not be used at all.
      - "format" will return the string value, where "%s" string
        formatting will return `NameOfEnum.stringvalue`. Format syntax
        should be prefered.
  - New Long Running Operation:
      - Return type changes from
        `msrestazure.azure_operation.AzureOperationPoller` to
        `msrest.polling.LROPoller`. External API is the same.
      - Return type is now **always** a `msrest.polling.LROPoller`,
        regardless of the optional parameters used.
      - The behavior has changed when using `raw=True`. Instead of
        returning the initial call result as `ClientRawResponse`,
        without polling, now this returns an LROPoller. After polling,
        the final resource will be returned as a `ClientRawResponse`.
      - New `polling` parameter. The default behavior is
        `Polling=True` which will poll using ARM algorithm. When
        `Polling=False`, the response of the initial call will be
        returned without polling.
      - `polling` parameter accepts instances of subclasses of
        `msrest.polling.PollingMethod`.
      - `add_done_callback` will no longer raise if called after
        polling is finished, but will instead execute the callback right
        away.

**SQL Breaking changes**

  -   - Database and ElasticPool now use Sku property for scale and
        tier-related properties. We have made this change in order to
        allow future support of autoscale, and to allow for new
        vCore-based editions.
        
          - Database.sku has replaced
            Database.requested_service_objective_name and
            Database.edition. Database scale can be set by setting
            Sku.name to the requested service objective name (e.g. S0,
            P1, or GP_Gen4_1), or by setting Sku.name to the sku name
            (e.g. Standard, Premium, or GP_Gen4) and set Sku.capacity
            to the scale measured in DTU or vCores.
          - Database.current_sku has replaced
            Database.service_level_objetive.
          - Database.current_service_objective_id and
            Database.requested_service_objective_id have been
            removed.
          - ElasticPool.sku has replaced ElasticPool.dtu. Elastic pool
            scale can be set by setting Sku.name to the requested sku
            name (e.g. StandardPool, PremiumPool, or GP_Gen4) and
            setting Sku.capacity to the scale measured in DTU or vCores.
          - ElasticPool.per_database_settings has replaced
            ElasticPool.database_dtu_min and
            ElasticPool.database_dtu_max.

  - Database.max_size_bytes is now an integer instead of string.

  - LocationCapabilities tree has been changed in order to support
    capabilities of new vCore-based database and elastic pool editions.

**Features**

  - Added support for List and Cancel operation on Azure database and
    elastic pool REST API
  - Added Long Term Retention V2 commands, including getting backups,
    deleting backups, setting the V2 policies, and getting the V2
    policies
      - Removed support for managing Vaults used for Long Term Retention
        V1
      - Changed BackupLongTermRetentionPolicy class, removing the Long
        Term Retention V1 properties and adding the Long Term Retention
        V2 properties
      - Removed BackupLongTermRetentionPolicyState

## 0.8.6 (2018-03-22)

**Features**

  - Added support for List and Cancel operation on Azure database and
    elastic pool REST API
  - Added support for Auto-tuning REST API

## 0.8.5 (2018-01-18)

**Features**

  - Added support for renaming databases
  - Added missing database editions and service objectives
  - Added ability to list long term retention vaults & policies

## 0.8.4 (2017-11-14)

**Features**

  - Added support for subscription usages

## 0.8.3 (2017-10-24)

**Features**

  - Added support for database zone redundant property
  - Added support for server dns aliases

## 0.8.2 (2017-10-18)

**Features**

  - Added support for state and migration flag properties for SQL Vnet
    rules

## 0.8.1 (2017-10-04)

**Features**

  - Add database.cancel operation
  - Add database.list_by_database

## 0.8.0 (2017-09-07)

**Disclaimer**

We were using a slightly unorthodox convention for some operation ids.
Some resource operations were "nested" inside others, e.g. blob auditing
policies was nested inside databases as in
client.databases.get_blob_auditing_policies(..) instead of the
flattened ARM standard
client.database_blob_auditing_policies.get(...).

This convention has lead to some inconsistencies, makes some APIs
difficult to find, and is at odds with future APIs. For example if we
wanted to implement listing db audit policies by server, continuing the
current convention would be
client.databases.list_blob_auditing_policies_by_server(..) which
makes much less sense than the ARM standard which would
beclient.database_blob_auditing_policies.list_by_server(...)`.

In order to resolve this and provide a good path moving forward, we have
renamed the inconsistent operations to follow the ARM standard. This is
an unfortunate breaking change, but it's best to do now while the SDK is
still in preview and since most of these operations were only recently
added.

**Breaking changes**

  - client.database.get_backup_long_term_retention_policy ->
    client.backup_long_term_retention_policies.get
  - client.database.create_or_update_backup_long_term_retention_policy
    ->
    client.backup_long_term_retention_policies.create_or_update
  - client.servers.create_backup_long_term_retention_vault ->
    client.backup_long_term_retention_vaults.create_or_update
  - client.servers.get_backup_long_term_retention_vault ->
    client.backup_long_term_retention_vaults.get
  - client.database.list_restore_points ->
    client.restore_points.list_by_database
  - client.servers.create_or_update_connection_policy ->
    client.server_connection_policies.create_or_update
  - client.servers.get_connection_policy ->
    client.server_connection_policies.get
  - client.databases.create_or_update_data_masking_policy ->
    client.data_masking_policies.create_or_update
  - client.databases.get_data_masking_policy ->
    client.data_masking_policies.get
  - client.databases.create_or_update_data_masking_rule ->
    client.data_masking_rules.create_or_update
  - client.databases.get_data_masking_rule ->
    client.data_masking_rules.get
  - client.databases.list_data_masking_rules ->
    client.data_masking_rules.list_by_database
  - client.databases.get_threat_detection_policy ->
    client.database_threat_detection_policies.get
  - client.databases.create_or_update_threat_detection_policy ->
    client.database_threat_detection_policies.create_or_update
  - client.databases.create_or_update_geo_backup_policy ->
    client.geo_backup_policies.create_or_update
  - client.databases.get_geo_backup_policy ->
    client.geo_backup_policies.get
  - client.databases.list_geo_backup_policies ->
    client.geo_backup_policies.list_by_database
  - client.databases.delete_replication_link ->
    client.replication_links.delete
  - client.databases.get_replication_link ->
    client.replication_links.get
  - client.databases.failover_replication_link ->
    client.replication_links.failover
  - client.databases.failover_replication_link_allow_data_loss ->
    client.replication_links.failover_allow_data_loss
  - client.databases.list_replication_links ->
    client.replication_links.list_by_database
  - client.server_azure_ad_administrators.list ->
    client.server_azure_ad_administrators.list_by_server
  - client.servers.get_service_objective ->
    client.service_objectives.get
  - client.servers.list_service_objectives ->
    client.service_objectives.list_by_server
  - client.elastic_pools.list_activity ->
    client.elastic_pool_activities.list_by_elastic_pool
  - client.elastic_pools.list_database_activity ->
    client.elastic_pool_database_activities.list_by_elastic_pool
  - client.elastic_pools.get_database ->
    client.databases.get_by_elastic_pool
  - client.elastic_pools.list_databases ->
    client.databases.list_by_elastic_pool
  - client.recommended_elastic_pools.get_databases ->
    client.databases.get_by_recommended_elastic_pool
  - client.recommended_elastic_pools.list_databases ->
    client.databases.list_by_recommended_elastic_pool
  - client.databases.get_service_tier_advisor ->
    client.service_tier_advisors.get
  - client.databases.list_service_tier_advisors ->
    client.service_tier_advisors.list_by_database
  - client.databases.create_or_update_transparent_data_encryption_configuration
    -> client.transparent_data_encryptions.create_or_update
  - client.databases.get_transparent_data_encryption_configuration
    -> client.transparent_data_encryptions.get
  - client.databases.list_transparent_data_encryption_activity ->
    client.transparent_data_encryption_activities.list_by_configuration
  - client.servers.list_usages ->
    client.server_usages.list_by_server
  - client.databases.list_usages ->
    client.database_usages.list_by_database
  - client.databases.get_blob_auditing_policy ->
    client.database_blob_auditing_policies.get
  - client.databases.create_or_update_blob_auditing_policy ->
    client.database_blob_auditing_policies.create_or_update
  - client.servers.list_encryption_protectors, ->
    client.encryption_protectors.list_by_server
  - client.servers.get_encryption_protector ->
    client.encryption_protectors.get
  - client.servers.create_or_update_encryption_protector ->
    client.encryption_protectors.create_or_update
  - Database blob auditing policy state is required
  - Failover group resource now has required properties defined

**Features**

  - Add SQL DB, server, and pool PATCH operations
  - client.operations.list now returnes a full list of operations and
    not a limited subset (2014-04-01 to 2015-05-01-preview)

**Fixed bugs**

  - Fixed KeyError in server_azure_ad_administrators_operations.get

## 0.7.1 (2017-06-30)

  - Added support for server connection policies
  - Fixed error in
    databases_operations.create_or_update_threat_detection_policy

## 0.7.0 (2017-06-28)

**Features**

  - Backup/Restore related: RecoverableDatabase,
    RestorableDroppedDatabase, BackupLongTermRetentionVault,
    BackupLongTermRetentionPolicy, and GeoBackupPolicy
  - Data Masking rules and policies
  - Server communication links

**Breaking changes**

  - Renamed enum RestorePointTypes to RestorePointType
  - Renamed VnetFirewallRule and related operations to
    VirtualNetworkRule

## 0.6.0 (2017-06-13)

  - Updated Servers api version from 2014-04-01 to 2015-05-01-preview,
    which is SDK compatible and includes support for server managed
    identity
  - Added support for server keys and encryption protectors
  - Added support for check server name availability
  - Added support for virtual network firewall rules
  - Updated server azure ad admin from swagger
  - Minor nonfunctional updates to database blob auditing
  - Breaking changes DatabaseMetrics and ServerMetrics renamed to
    DatabaseUsage and ServerUsage. These were misleadingly named because
    metrics is a different API.
  - Added database metrics and elastic pool metrics

## 0.5.3 (2017-06-01)

  - Update minimal dependency to msrestazure 0.4.8

## 0.5.2 (2017-05-31)

**Features**

  - Added support for server active directory administrator, failover
    groups, and virtual network rules
  - Minor changes to database auditing support

## 0.5.1 (2017-04-28)

**Bugfixes**

  - Fix return exception in import/export

## 0.5.0 (2017-04-19)

**Breaking changes**

  - `SqlManagementClient.list_operations` is now
    `SqlManagementClient.operations.list`

**New features**

  - Added elastic pool capabilities to capabilities API.

**Notes**

  - This wheel package is now built with the azure wheel extension

## 0.4.0 (2017-03-22)

Capabilities and security policy features.

Also renamed several types and operations for improved clarify and
consistency.

Additions:

  - BlobAuditingPolicy APIs (e.g.
    databases.create_or_update_blob_auditing_policy)
  - ThreatDetectionPolicy APIs (e.g.
    databases.create_or_update_threat_detection_policy)
  - databases.list_by_server now supports $expand parameter
  - Capabilities APIs (e.g. capabilities.list_by_location)

Classes and enums renamed:

  - ServerFirewallRule -> FirewallRule
  - DatabaseEditions -> DatabaseEdition
  - ElasticPoolEditions -> ElasticPoolEdition
  - ImportRequestParameters -> ImportRequest
  - ExportRequestParameters -> ExportRequest
  - ImportExportOperationResponse -> ImportExportResponse
  - OperationMode -> ImportOperationMode
  - TransparentDataEncryptionStates -> TransparentDataEncryptionStatus

Classes removed:

  - Unused types: UpgradeHint, Schema, Table, Column

Operations renamed:

  - servers.get_by_resource_group -> servers.get
  - servers.create_or_update_firewall_rule ->
    firewall_rules.create_or_update, and similar for get, list, and
    delete
  - databases.import -> databases.create_import_operation
  - servers.import -> databases.import
  - databases.pause_data_warehouse -> databases.pause
  - databases.resume_data_warehouse -> databases.resume
  - recommended_elastic_pools.list ->
    recommended_elastic_pools.list_by_server

Operations removed:

  - Removed ImportExport operation results APIs since these are handled
    automatically by Azure async pattern.

## 0.3.3 (2017-03-14)

  - Add database blob auditing and threat detection operations

## 0.3.2 (2017-03-08)

  - Add import/export operations
  - Expanded documentation of create modes

## 0.3.1 (2017-03-01)

  - Added ‘filter’ param to list databases

## 0.3.0 (2017-02-27)

**Breaking changes**

  - Enums:
      - createMode renamed to CreateMode
      - Added ReadScale, SampleName, ServerState
  - Added missing Database properties (failover_group_id,
    restore_point_in_time, read_scale, sample_name)
  - Added missing ElasticPoolActivity properties ([requested]()*)
  - Added missing ReplicationLink properties (is_termination_allowed,
    replication_mode)
  - Added missing Server properties ([external_administrator]()*,
    state)
  - Added operations APIs
  - Removed unused Database.upgrade_hint property
  - Removed unused RecommendedDatabaseProperties class
  - Renamed incorrect RecommendedElasticPool.databases_property to
    databases
  - Made firewall rule start/end ip address required
  - Added missing kind property to many resources
  - Many doc clarifications

## 0.2.0 (2016-12-12)

**Breaking changes**

  - Parameters re-ordering (list_database_activity)
  - Flatten create_or_update_firewall_rule from "parameters" to
    "start_ip_address" and "end_ip_address"

## 0.1.0 (2016-11-02)

  - Initial Release
