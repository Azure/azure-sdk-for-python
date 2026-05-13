```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.synapse

    class azure.mgmt.synapse.SynapseManagementClient: implements ContextManager 
        azure_ad_only_authentications: AzureADOnlyAuthenticationsOperations
        big_data_pools: BigDataPoolsOperations
        data_masking_policies: DataMaskingPoliciesOperations
        data_masking_rules: DataMaskingRulesOperations
        extended_sql_pool_blob_auditing_policies: ExtendedSqlPoolBlobAuditingPoliciesOperations
        get: GetOperations
        integration_runtime_auth_keys: IntegrationRuntimeAuthKeysOperations
        integration_runtime_connection_infos: IntegrationRuntimeConnectionInfosOperations
        integration_runtime_credentials: IntegrationRuntimeCredentialsOperations
        integration_runtime_monitoring_data: IntegrationRuntimeMonitoringDataOperations
        integration_runtime_node_ip_address: IntegrationRuntimeNodeIpAddressOperations
        integration_runtime_nodes: IntegrationRuntimeNodesOperations
        integration_runtime_object_metadata: IntegrationRuntimeObjectMetadataOperations
        integration_runtime_status: IntegrationRuntimeStatusOperations
        integration_runtimes: IntegrationRuntimesOperations
        ip_firewall_rules: IpFirewallRulesOperations
        keys: KeysOperations
        kusto_operations: KustoOperationsOperations
        kusto_pool_attached_database_configurations: KustoPoolAttachedDatabaseConfigurationsOperations
        kusto_pool_child_resource: KustoPoolChildResourceOperations
        kusto_pool_data_connections: KustoPoolDataConnectionsOperations
        kusto_pool_database_principal_assignments: KustoPoolDatabasePrincipalAssignmentsOperations
        kusto_pool_databases: KustoPoolDatabasesOperations
        kusto_pool_principal_assignments: KustoPoolPrincipalAssignmentsOperations
        kusto_pool_private_link_resources: KustoPoolPrivateLinkResourcesOperations
        kusto_pools: KustoPoolsOperations
        libraries: LibrariesOperations
        library: LibraryOperations
        operations: Operations
        private_endpoint_connections: PrivateEndpointConnectionsOperations
        private_endpoint_connections_private_link_hub: PrivateEndpointConnectionsPrivateLinkHubOperations
        private_link_hub_private_link_resources: PrivateLinkHubPrivateLinkResourcesOperations
        private_link_hubs: PrivateLinkHubsOperations
        private_link_resources: PrivateLinkResourcesOperations
        restorable_dropped_sql_pools: RestorableDroppedSqlPoolsOperations
        spark_configuration: SparkConfigurationOperations
        spark_configurations: SparkConfigurationsOperations
        sql_pool_blob_auditing_policies: SqlPoolBlobAuditingPoliciesOperations
        sql_pool_columns: SqlPoolColumnsOperations
        sql_pool_connection_policies: SqlPoolConnectionPoliciesOperations
        sql_pool_data_warehouse_user_activities: SqlPoolDataWarehouseUserActivitiesOperations
        sql_pool_geo_backup_policies: SqlPoolGeoBackupPoliciesOperations
        sql_pool_maintenance_window_options: SqlPoolMaintenanceWindowOptionsOperations
        sql_pool_maintenance_windows: SqlPoolMaintenanceWindowsOperations
        sql_pool_metadata_sync_configs: SqlPoolMetadataSyncConfigsOperations
        sql_pool_operation_results: SqlPoolOperationResultsOperations
        sql_pool_operations: SqlPoolOperationsOperations
        sql_pool_recommended_sensitivity_labels: SqlPoolRecommendedSensitivityLabelsOperations
        sql_pool_replication_links: SqlPoolReplicationLinksOperations
        sql_pool_restore_points: SqlPoolRestorePointsOperations
        sql_pool_schemas: SqlPoolSchemasOperations
        sql_pool_security_alert_policies: SqlPoolSecurityAlertPoliciesOperations
        sql_pool_sensitivity_labels: SqlPoolSensitivityLabelsOperations
        sql_pool_table_columns: SqlPoolTableColumnsOperations
        sql_pool_tables: SqlPoolTablesOperations
        sql_pool_transparent_data_encryptions: SqlPoolTransparentDataEncryptionsOperations
        sql_pool_usages: SqlPoolUsagesOperations
        sql_pool_vulnerability_assessment_rule_baselines: SqlPoolVulnerabilityAssessmentRuleBaselinesOperations
        sql_pool_vulnerability_assessment_scans: SqlPoolVulnerabilityAssessmentScansOperations
        sql_pool_vulnerability_assessments: SqlPoolVulnerabilityAssessmentsOperations
        sql_pool_workload_classifier: SqlPoolWorkloadClassifierOperations
        sql_pool_workload_group: SqlPoolWorkloadGroupOperations
        sql_pools: SqlPoolsOperations
        workspace_aad_admins: WorkspaceAadAdminsOperations
        workspace_managed_identity_sql_control_settings: WorkspaceManagedIdentitySqlControlSettingsOperations
        workspace_managed_sql_server_blob_auditing_policies: WorkspaceManagedSqlServerBlobAuditingPoliciesOperations
        workspace_managed_sql_server_dedicated_sql_minimal_tls_settings: WorkspaceManagedSqlServerDedicatedSQLMinimalTlsSettingsOperations
        workspace_managed_sql_server_encryption_protector: WorkspaceManagedSqlServerEncryptionProtectorOperations
        workspace_managed_sql_server_extended_blob_auditing_policies: WorkspaceManagedSqlServerExtendedBlobAuditingPoliciesOperations
        workspace_managed_sql_server_recoverable_sql_pools: WorkspaceManagedSqlServerRecoverableSqlPoolsOperations
        workspace_managed_sql_server_security_alert_policy: WorkspaceManagedSqlServerSecurityAlertPolicyOperations
        workspace_managed_sql_server_usages: WorkspaceManagedSqlServerUsagesOperations
        workspace_managed_sql_server_vulnerability_assessments: WorkspaceManagedSqlServerVulnerabilityAssessmentsOperations
        workspace_sql_aad_admins: WorkspaceSqlAadAdminsOperations
        workspaces: WorkspacesOperations

        def __init__(
                self, 
                credential: TokenCredential, 
                subscription_id: str, 
                base_url: str = "https://management.azure.com", 
                *, 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def close(self) -> None: ...


namespace azure.mgmt.synapse.aio

    class azure.mgmt.synapse.aio.SynapseManagementClient: implements AsyncContextManager 
        azure_ad_only_authentications: AzureADOnlyAuthenticationsOperations
        big_data_pools: BigDataPoolsOperations
        data_masking_policies: DataMaskingPoliciesOperations
        data_masking_rules: DataMaskingRulesOperations
        extended_sql_pool_blob_auditing_policies: ExtendedSqlPoolBlobAuditingPoliciesOperations
        get: GetOperations
        integration_runtime_auth_keys: IntegrationRuntimeAuthKeysOperations
        integration_runtime_connection_infos: IntegrationRuntimeConnectionInfosOperations
        integration_runtime_credentials: IntegrationRuntimeCredentialsOperations
        integration_runtime_monitoring_data: IntegrationRuntimeMonitoringDataOperations
        integration_runtime_node_ip_address: IntegrationRuntimeNodeIpAddressOperations
        integration_runtime_nodes: IntegrationRuntimeNodesOperations
        integration_runtime_object_metadata: IntegrationRuntimeObjectMetadataOperations
        integration_runtime_status: IntegrationRuntimeStatusOperations
        integration_runtimes: IntegrationRuntimesOperations
        ip_firewall_rules: IpFirewallRulesOperations
        keys: KeysOperations
        kusto_operations: KustoOperationsOperations
        kusto_pool_attached_database_configurations: KustoPoolAttachedDatabaseConfigurationsOperations
        kusto_pool_child_resource: KustoPoolChildResourceOperations
        kusto_pool_data_connections: KustoPoolDataConnectionsOperations
        kusto_pool_database_principal_assignments: KustoPoolDatabasePrincipalAssignmentsOperations
        kusto_pool_databases: KustoPoolDatabasesOperations
        kusto_pool_principal_assignments: KustoPoolPrincipalAssignmentsOperations
        kusto_pool_private_link_resources: KustoPoolPrivateLinkResourcesOperations
        kusto_pools: KustoPoolsOperations
        libraries: LibrariesOperations
        library: LibraryOperations
        operations: Operations
        private_endpoint_connections: PrivateEndpointConnectionsOperations
        private_endpoint_connections_private_link_hub: PrivateEndpointConnectionsPrivateLinkHubOperations
        private_link_hub_private_link_resources: PrivateLinkHubPrivateLinkResourcesOperations
        private_link_hubs: PrivateLinkHubsOperations
        private_link_resources: PrivateLinkResourcesOperations
        restorable_dropped_sql_pools: RestorableDroppedSqlPoolsOperations
        spark_configuration: SparkConfigurationOperations
        spark_configurations: SparkConfigurationsOperations
        sql_pool_blob_auditing_policies: SqlPoolBlobAuditingPoliciesOperations
        sql_pool_columns: SqlPoolColumnsOperations
        sql_pool_connection_policies: SqlPoolConnectionPoliciesOperations
        sql_pool_data_warehouse_user_activities: SqlPoolDataWarehouseUserActivitiesOperations
        sql_pool_geo_backup_policies: SqlPoolGeoBackupPoliciesOperations
        sql_pool_maintenance_window_options: SqlPoolMaintenanceWindowOptionsOperations
        sql_pool_maintenance_windows: SqlPoolMaintenanceWindowsOperations
        sql_pool_metadata_sync_configs: SqlPoolMetadataSyncConfigsOperations
        sql_pool_operation_results: SqlPoolOperationResultsOperations
        sql_pool_operations: SqlPoolOperationsOperations
        sql_pool_recommended_sensitivity_labels: SqlPoolRecommendedSensitivityLabelsOperations
        sql_pool_replication_links: SqlPoolReplicationLinksOperations
        sql_pool_restore_points: SqlPoolRestorePointsOperations
        sql_pool_schemas: SqlPoolSchemasOperations
        sql_pool_security_alert_policies: SqlPoolSecurityAlertPoliciesOperations
        sql_pool_sensitivity_labels: SqlPoolSensitivityLabelsOperations
        sql_pool_table_columns: SqlPoolTableColumnsOperations
        sql_pool_tables: SqlPoolTablesOperations
        sql_pool_transparent_data_encryptions: SqlPoolTransparentDataEncryptionsOperations
        sql_pool_usages: SqlPoolUsagesOperations
        sql_pool_vulnerability_assessment_rule_baselines: SqlPoolVulnerabilityAssessmentRuleBaselinesOperations
        sql_pool_vulnerability_assessment_scans: SqlPoolVulnerabilityAssessmentScansOperations
        sql_pool_vulnerability_assessments: SqlPoolVulnerabilityAssessmentsOperations
        sql_pool_workload_classifier: SqlPoolWorkloadClassifierOperations
        sql_pool_workload_group: SqlPoolWorkloadGroupOperations
        sql_pools: SqlPoolsOperations
        workspace_aad_admins: WorkspaceAadAdminsOperations
        workspace_managed_identity_sql_control_settings: WorkspaceManagedIdentitySqlControlSettingsOperations
        workspace_managed_sql_server_blob_auditing_policies: WorkspaceManagedSqlServerBlobAuditingPoliciesOperations
        workspace_managed_sql_server_dedicated_sql_minimal_tls_settings: WorkspaceManagedSqlServerDedicatedSQLMinimalTlsSettingsOperations
        workspace_managed_sql_server_encryption_protector: WorkspaceManagedSqlServerEncryptionProtectorOperations
        workspace_managed_sql_server_extended_blob_auditing_policies: WorkspaceManagedSqlServerExtendedBlobAuditingPoliciesOperations
        workspace_managed_sql_server_recoverable_sql_pools: WorkspaceManagedSqlServerRecoverableSqlPoolsOperations
        workspace_managed_sql_server_security_alert_policy: WorkspaceManagedSqlServerSecurityAlertPolicyOperations
        workspace_managed_sql_server_usages: WorkspaceManagedSqlServerUsagesOperations
        workspace_managed_sql_server_vulnerability_assessments: WorkspaceManagedSqlServerVulnerabilityAssessmentsOperations
        workspace_sql_aad_admins: WorkspaceSqlAadAdminsOperations
        workspaces: WorkspacesOperations

        def __init__(
                self, 
                credential: AsyncTokenCredential, 
                subscription_id: str, 
                base_url: str = "https://management.azure.com", 
                *, 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        async def close(self) -> None: ...


namespace azure.mgmt.synapse.aio.operations

    class azure.mgmt.synapse.aio.operations.AzureADOnlyAuthenticationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                azure_ad_only_authentication_name: Union[str, AzureADOnlyAuthenticationName], 
                azure_ad_only_authentication_info: AzureADOnlyAuthentication, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AzureADOnlyAuthentication]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                azure_ad_only_authentication_name: Union[str, AzureADOnlyAuthenticationName], 
                azure_ad_only_authentication_info: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AzureADOnlyAuthentication]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                azure_ad_only_authentication_name: Union[str, AzureADOnlyAuthenticationName], 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AzureADOnlyAuthentication: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[AzureADOnlyAuthentication]: ...


    class azure.mgmt.synapse.aio.operations.BigDataPoolsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                big_data_pool_name: str, 
                big_data_pool_info: BigDataPoolResourceInfo, 
                force: bool = False, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BigDataPoolResourceInfo]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                big_data_pool_name: str, 
                big_data_pool_info: IO, 
                force: bool = False, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BigDataPoolResourceInfo]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                big_data_pool_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[BigDataPoolResourceInfo]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                big_data_pool_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> BigDataPoolResourceInfo: ...

        @distributed_trace
        def list_by_workspace(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[BigDataPoolResourceInfo]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                big_data_pool_name: str, 
                big_data_pool_patch_info: BigDataPoolPatchInfo, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BigDataPoolResourceInfo: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                big_data_pool_name: str, 
                big_data_pool_patch_info: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BigDataPoolResourceInfo: ...


    class azure.mgmt.synapse.aio.operations.DataMaskingPoliciesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                parameters: DataMaskingPolicy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DataMaskingPolicy: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DataMaskingPolicy: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                data_masking_policy_name: str = ..., 
                **kwargs: Any
            ) -> DataMaskingPolicy: ...


    class azure.mgmt.synapse.aio.operations.DataMaskingRulesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                data_masking_rule_name: str, 
                parameters: DataMaskingRule, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DataMaskingRule: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                data_masking_rule_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DataMaskingRule: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                data_masking_rule_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                data_masking_policy_name: str = ..., 
                **kwargs: Any
            ) -> DataMaskingRule: ...

        @distributed_trace
        def list_by_sql_pool(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                data_masking_policy_name: str = ..., 
                **kwargs: Any
            ) -> AsyncIterable[DataMaskingRule]: ...


    class azure.mgmt.synapse.aio.operations.ExtendedSqlPoolBlobAuditingPoliciesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                parameters: ExtendedSqlPoolBlobAuditingPolicy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ExtendedSqlPoolBlobAuditingPolicy: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ExtendedSqlPoolBlobAuditingPolicy: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                *, 
                blob_auditing_policy_name: str = ..., 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ExtendedSqlPoolBlobAuditingPolicy: ...

        @distributed_trace
        def list_by_sql_pool(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[ExtendedSqlPoolBlobAuditingPolicy]: ...


    class azure.mgmt.synapse.aio.operations.GetOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def integration_runtime_enable_interactivequery(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                integration_runtime_name: str, 
                integration_runtime_operation_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> IntegrationRuntimeEnableinteractivequery: ...

        @distributed_trace_async
        async def integration_runtime_start(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                integration_runtime_name: str, 
                integration_runtime_operation_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> IntegrationRuntimeOperationStatus: ...

        @distributed_trace_async
        async def integration_runtime_stop(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                integration_runtime_name: str, 
                integration_runtime_operation_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> IntegrationRuntimeStopOperationStatus: ...


    class azure.mgmt.synapse.aio.operations.IntegrationRuntimeAuthKeysOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                integration_runtime_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> IntegrationRuntimeAuthKeys: ...

        @overload
        async def regenerate(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                integration_runtime_name: str, 
                regenerate_key_parameters: IntegrationRuntimeRegenerateKeyParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> IntegrationRuntimeAuthKeys: ...

        @overload
        async def regenerate(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                integration_runtime_name: str, 
                regenerate_key_parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> IntegrationRuntimeAuthKeys: ...


    class azure.mgmt.synapse.aio.operations.IntegrationRuntimeConnectionInfosOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                integration_runtime_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> IntegrationRuntimeConnectionInfo: ...


    class azure.mgmt.synapse.aio.operations.IntegrationRuntimeCredentialsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def sync(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                integration_runtime_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.synapse.aio.operations.IntegrationRuntimeMonitoringDataOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                integration_runtime_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> IntegrationRuntimeMonitoringData: ...


    class azure.mgmt.synapse.aio.operations.IntegrationRuntimeNodeIpAddressOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                integration_runtime_name: str, 
                node_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> IntegrationRuntimeNodeIpAddress: ...


    class azure.mgmt.synapse.aio.operations.IntegrationRuntimeNodesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                integration_runtime_name: str, 
                node_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                integration_runtime_name: str, 
                node_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> SelfHostedIntegrationRuntimeNode: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                integration_runtime_name: str, 
                node_name: str, 
                update_integration_runtime_node_request: UpdateIntegrationRuntimeNodeRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SelfHostedIntegrationRuntimeNode: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                integration_runtime_name: str, 
                node_name: str, 
                update_integration_runtime_node_request: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SelfHostedIntegrationRuntimeNode: ...


    class azure.mgmt.synapse.aio.operations.IntegrationRuntimeObjectMetadataOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_refresh(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                integration_runtime_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[SsisObjectMetadataStatusResponse]: ...

        @overload
        async def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                integration_runtime_name: str, 
                get_metadata_request: Optional[GetSsisObjectMetadataRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SsisObjectMetadataListResponse: ...

        @overload
        async def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                integration_runtime_name: str, 
                get_metadata_request: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SsisObjectMetadataListResponse: ...


    class azure.mgmt.synapse.aio.operations.IntegrationRuntimeStatusOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                integration_runtime_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> IntegrationRuntimeStatusResponse: ...


    class azure.mgmt.synapse.aio.operations.IntegrationRuntimesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                integration_runtime_name: str, 
                integration_runtime: IntegrationRuntimeResource, 
                if_match: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[IntegrationRuntimeResource]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                integration_runtime_name: str, 
                integration_runtime: IO, 
                if_match: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[IntegrationRuntimeResource]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                integration_runtime_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_disable_interactive_query(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                integration_runtime_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_enable_interactive_query(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                integration_runtime_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_start(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                integration_runtime_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[IntegrationRuntimeStatusResponse]: ...

        @distributed_trace_async
        async def begin_stop(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                integration_runtime_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                integration_runtime_name: str, 
                if_none_match: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Optional[IntegrationRuntimeResource]: ...

        @distributed_trace
        def list_by_workspace(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[IntegrationRuntimeResource]: ...

        @distributed_trace_async
        async def list_outbound_network_dependencies_endpoints(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                integration_runtime_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> IntegrationRuntimeOutboundNetworkDependenciesEndpointsResponse: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                integration_runtime_name: str, 
                update_integration_runtime_request: UpdateIntegrationRuntimeRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> IntegrationRuntimeResource: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                integration_runtime_name: str, 
                update_integration_runtime_request: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> IntegrationRuntimeResource: ...

        @distributed_trace_async
        async def upgrade(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                integration_runtime_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.synapse.aio.operations.IpFirewallRulesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                rule_name: str, 
                ip_firewall_rule_info: IpFirewallRuleInfo, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[IpFirewallRuleInfo]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                rule_name: str, 
                ip_firewall_rule_info: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[IpFirewallRuleInfo]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                rule_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[IpFirewallRuleInfo]: ...

        @overload
        async def begin_replace_all(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                request: ReplaceAllIpFirewallRulesRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ReplaceAllFirewallRulesOperationResponse]: ...

        @overload
        async def begin_replace_all(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                request: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ReplaceAllFirewallRulesOperationResponse]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                rule_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> IpFirewallRuleInfo: ...

        @distributed_trace
        def list_by_workspace(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[IpFirewallRuleInfo]: ...


    class azure.mgmt.synapse.aio.operations.KeysOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                key_name: str, 
                key_properties: Key, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Key: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                key_name: str, 
                key_properties: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Key: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                key_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Optional[Key]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                key_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Key: ...

        @distributed_trace
        def list_by_workspace(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[Key]: ...


    class azure.mgmt.synapse.aio.operations.KustoOperationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[Operation]: ...


    class azure.mgmt.synapse.aio.operations.KustoPoolAttachedDatabaseConfigurationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                workspace_name: str, 
                kusto_pool_name: str, 
                attached_database_configuration_name: str, 
                resource_group_name: str, 
                parameters: AttachedDatabaseConfiguration, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AttachedDatabaseConfiguration]: ...

        @overload
        async def begin_create_or_update(
                self, 
                workspace_name: str, 
                kusto_pool_name: str, 
                attached_database_configuration_name: str, 
                resource_group_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AttachedDatabaseConfiguration]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                workspace_name: str, 
                kusto_pool_name: str, 
                attached_database_configuration_name: str, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                workspace_name: str, 
                kusto_pool_name: str, 
                attached_database_configuration_name: str, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AttachedDatabaseConfiguration: ...

        @distributed_trace
        def list_by_kusto_pool(
                self, 
                workspace_name: str, 
                kusto_pool_name: str, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[AttachedDatabaseConfiguration]: ...


    class azure.mgmt.synapse.aio.operations.KustoPoolChildResourceOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def check_name_availability(
                self, 
                workspace_name: str, 
                kusto_pool_name: str, 
                resource_group_name: str, 
                resource_name: DatabaseCheckNameRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameResult: ...

        @overload
        async def check_name_availability(
                self, 
                workspace_name: str, 
                kusto_pool_name: str, 
                resource_group_name: str, 
                resource_name: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameResult: ...


    class azure.mgmt.synapse.aio.operations.KustoPoolDataConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                kusto_pool_name: str, 
                database_name: str, 
                data_connection_name: str, 
                parameters: DataConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DataConnection]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                kusto_pool_name: str, 
                database_name: str, 
                data_connection_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DataConnection]: ...

        @overload
        async def begin_data_connection_validation(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                kusto_pool_name: str, 
                database_name: str, 
                parameters: DataConnectionValidation, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DataConnectionValidationListResult]: ...

        @overload
        async def begin_data_connection_validation(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                kusto_pool_name: str, 
                database_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DataConnectionValidationListResult]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                kusto_pool_name: str, 
                database_name: str, 
                data_connection_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                kusto_pool_name: str, 
                database_name: str, 
                data_connection_name: str, 
                parameters: DataConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DataConnection]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                kusto_pool_name: str, 
                database_name: str, 
                data_connection_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DataConnection]: ...

        @overload
        async def check_name_availability(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                kusto_pool_name: str, 
                database_name: str, 
                data_connection_name: DataConnectionCheckNameRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameResult: ...

        @overload
        async def check_name_availability(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                kusto_pool_name: str, 
                database_name: str, 
                data_connection_name: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameResult: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                kusto_pool_name: str, 
                database_name: str, 
                data_connection_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> DataConnection: ...

        @distributed_trace
        def list_by_database(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                kusto_pool_name: str, 
                database_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[DataConnection]: ...


    class azure.mgmt.synapse.aio.operations.KustoPoolDatabasePrincipalAssignmentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                workspace_name: str, 
                kusto_pool_name: str, 
                database_name: str, 
                principal_assignment_name: str, 
                resource_group_name: str, 
                parameters: DatabasePrincipalAssignment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DatabasePrincipalAssignment]: ...

        @overload
        async def begin_create_or_update(
                self, 
                workspace_name: str, 
                kusto_pool_name: str, 
                database_name: str, 
                principal_assignment_name: str, 
                resource_group_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DatabasePrincipalAssignment]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                workspace_name: str, 
                kusto_pool_name: str, 
                database_name: str, 
                principal_assignment_name: str, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def check_name_availability(
                self, 
                workspace_name: str, 
                kusto_pool_name: str, 
                database_name: str, 
                resource_group_name: str, 
                principal_assignment_name: DatabasePrincipalAssignmentCheckNameRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameResult: ...

        @overload
        async def check_name_availability(
                self, 
                workspace_name: str, 
                kusto_pool_name: str, 
                database_name: str, 
                resource_group_name: str, 
                principal_assignment_name: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameResult: ...

        @distributed_trace_async
        async def get(
                self, 
                workspace_name: str, 
                kusto_pool_name: str, 
                database_name: str, 
                principal_assignment_name: str, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> DatabasePrincipalAssignment: ...

        @distributed_trace
        def list(
                self, 
                workspace_name: str, 
                kusto_pool_name: str, 
                database_name: str, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[DatabasePrincipalAssignment]: ...


    class azure.mgmt.synapse.aio.operations.KustoPoolDatabasesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                kusto_pool_name: str, 
                database_name: str, 
                parameters: Database, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Database]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                kusto_pool_name: str, 
                database_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Database]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                kusto_pool_name: str, 
                database_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                kusto_pool_name: str, 
                database_name: str, 
                parameters: Database, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Database]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                kusto_pool_name: str, 
                database_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Database]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                kusto_pool_name: str, 
                database_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Database: ...

        @distributed_trace
        def list_by_kusto_pool(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                kusto_pool_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[Database]: ...


    class azure.mgmt.synapse.aio.operations.KustoPoolPrincipalAssignmentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                workspace_name: str, 
                kusto_pool_name: str, 
                principal_assignment_name: str, 
                resource_group_name: str, 
                parameters: ClusterPrincipalAssignment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ClusterPrincipalAssignment]: ...

        @overload
        async def begin_create_or_update(
                self, 
                workspace_name: str, 
                kusto_pool_name: str, 
                principal_assignment_name: str, 
                resource_group_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ClusterPrincipalAssignment]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                workspace_name: str, 
                kusto_pool_name: str, 
                principal_assignment_name: str, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def check_name_availability(
                self, 
                workspace_name: str, 
                kusto_pool_name: str, 
                resource_group_name: str, 
                principal_assignment_name: ClusterPrincipalAssignmentCheckNameRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameResult: ...

        @overload
        async def check_name_availability(
                self, 
                workspace_name: str, 
                kusto_pool_name: str, 
                resource_group_name: str, 
                principal_assignment_name: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameResult: ...

        @distributed_trace_async
        async def get(
                self, 
                workspace_name: str, 
                kusto_pool_name: str, 
                principal_assignment_name: str, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ClusterPrincipalAssignment: ...

        @distributed_trace
        def list(
                self, 
                workspace_name: str, 
                kusto_pool_name: str, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[ClusterPrincipalAssignment]: ...


    class azure.mgmt.synapse.aio.operations.KustoPoolPrivateLinkResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                kusto_pool_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[KustoPoolPrivateLinkResources]: ...


    class azure.mgmt.synapse.aio.operations.KustoPoolsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_add_language_extensions(
                self, 
                workspace_name: str, 
                kusto_pool_name: str, 
                resource_group_name: str, 
                language_extensions_to_add: LanguageExtensionsList, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_add_language_extensions(
                self, 
                workspace_name: str, 
                kusto_pool_name: str, 
                resource_group_name: str, 
                language_extensions_to_add: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_create_or_update(
                self, 
                workspace_name: str, 
                resource_group_name: str, 
                kusto_pool_name: str, 
                parameters: KustoPool, 
                if_match: Optional[str] = None, 
                if_none_match: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[KustoPool]: ...

        @overload
        async def begin_create_or_update(
                self, 
                workspace_name: str, 
                resource_group_name: str, 
                kusto_pool_name: str, 
                parameters: IO, 
                if_match: Optional[str] = None, 
                if_none_match: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[KustoPool]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                workspace_name: str, 
                resource_group_name: str, 
                kusto_pool_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_detach_follower_databases(
                self, 
                workspace_name: str, 
                kusto_pool_name: str, 
                resource_group_name: str, 
                follower_database_to_remove: FollowerDatabaseDefinition, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_detach_follower_databases(
                self, 
                workspace_name: str, 
                kusto_pool_name: str, 
                resource_group_name: str, 
                follower_database_to_remove: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_remove_language_extensions(
                self, 
                workspace_name: str, 
                kusto_pool_name: str, 
                resource_group_name: str, 
                language_extensions_to_remove: LanguageExtensionsList, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_remove_language_extensions(
                self, 
                workspace_name: str, 
                kusto_pool_name: str, 
                resource_group_name: str, 
                language_extensions_to_remove: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_start(
                self, 
                workspace_name: str, 
                kusto_pool_name: str, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_stop(
                self, 
                workspace_name: str, 
                kusto_pool_name: str, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                workspace_name: str, 
                resource_group_name: str, 
                kusto_pool_name: str, 
                parameters: KustoPoolUpdate, 
                if_match: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[KustoPool]: ...

        @overload
        async def begin_update(
                self, 
                workspace_name: str, 
                resource_group_name: str, 
                kusto_pool_name: str, 
                parameters: IO, 
                if_match: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[KustoPool]: ...

        @overload
        async def check_name_availability(
                self, 
                location: str, 
                kusto_pool_name: KustoPoolCheckNameRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameResult: ...

        @overload
        async def check_name_availability(
                self, 
                location: str, 
                kusto_pool_name: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameResult: ...

        @distributed_trace_async
        async def get(
                self, 
                workspace_name: str, 
                kusto_pool_name: str, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> KustoPool: ...

        @distributed_trace_async
        async def list_by_workspace(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> KustoPoolListResult: ...

        @distributed_trace
        def list_follower_databases(
                self, 
                workspace_name: str, 
                kusto_pool_name: str, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[FollowerDatabaseDefinition]: ...

        @distributed_trace
        def list_language_extensions(
                self, 
                workspace_name: str, 
                kusto_pool_name: str, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[LanguageExtension]: ...

        @distributed_trace
        def list_skus(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[SkuDescription]: ...

        @distributed_trace
        def list_skus_by_resource(
                self, 
                workspace_name: str, 
                kusto_pool_name: str, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[AzureResourceSku]: ...


    class azure.mgmt.synapse.aio.operations.LibrariesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_by_workspace(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[LibraryResource]: ...


    class azure.mgmt.synapse.aio.operations.LibraryOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                library_name: str, 
                workspace_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> LibraryResource: ...


    class azure.mgmt.synapse.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def check_name_availability(
                self, 
                request: CheckNameAvailabilityRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResponse: ...

        @overload
        async def check_name_availability(
                self, 
                request: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResponse: ...

        @distributed_trace_async
        async def get_azure_async_header_result(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                operation_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Optional[OperationResource]: ...

        @distributed_trace_async
        async def get_location_header_result(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                operation_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def list(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> List[AvailableRpOperation]: ...


    class azure.mgmt.synapse.aio.operations.PrivateEndpointConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                private_endpoint_connection_name: str, 
                request: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateEndpointConnection]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                private_endpoint_connection_name: str, 
                request: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateEndpointConnection]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                private_endpoint_connection_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationResource]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                private_endpoint_connection_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[PrivateEndpointConnection]: ...


    class azure.mgmt.synapse.aio.operations.PrivateEndpointConnectionsPrivateLinkHubOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                private_link_hub_name: str, 
                private_endpoint_connection_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> PrivateEndpointConnectionForPrivateLinkHub: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                private_link_hub_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[PrivateEndpointConnectionForPrivateLinkHub]: ...


    class azure.mgmt.synapse.aio.operations.PrivateLinkHubPrivateLinkResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                private_link_hub_name: str, 
                private_link_resource_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> PrivateLinkResource: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                private_link_hub_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[PrivateLinkResource]: ...


    class azure.mgmt.synapse.aio.operations.PrivateLinkHubsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                private_link_hub_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                private_link_hub_name: str, 
                private_link_hub_info: PrivateLinkHub, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrivateLinkHub: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                private_link_hub_name: str, 
                private_link_hub_info: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrivateLinkHub: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                private_link_hub_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> PrivateLinkHub: ...

        @distributed_trace
        def list(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[PrivateLinkHub]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[PrivateLinkHub]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                private_link_hub_name: str, 
                private_link_hub_patch_info: PrivateLinkHubPatchInfo, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrivateLinkHub: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                private_link_hub_name: str, 
                private_link_hub_patch_info: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrivateLinkHub: ...


    class azure.mgmt.synapse.aio.operations.PrivateLinkResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                private_link_resource_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> PrivateLinkResource: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[PrivateLinkResource]: ...


    class azure.mgmt.synapse.aio.operations.RestorableDroppedSqlPoolsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                restorable_dropped_sql_pool_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> RestorableDroppedSqlPool: ...

        @distributed_trace
        def list_by_workspace(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[RestorableDroppedSqlPool]: ...


    class azure.mgmt.synapse.aio.operations.SparkConfigurationOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                spark_configuration_name: str, 
                workspace_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> SparkConfigurationResource: ...


    class azure.mgmt.synapse.aio.operations.SparkConfigurationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_by_workspace(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[SparkConfigurationResource]: ...


    class azure.mgmt.synapse.aio.operations.SqlPoolBlobAuditingPoliciesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                parameters: SqlPoolBlobAuditingPolicy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SqlPoolBlobAuditingPolicy: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SqlPoolBlobAuditingPolicy: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                *, 
                blob_auditing_policy_name: str = ..., 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> SqlPoolBlobAuditingPolicy: ...

        @distributed_trace
        def list_by_sql_pool(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[SqlPoolBlobAuditingPolicy]: ...


    class azure.mgmt.synapse.aio.operations.SqlPoolColumnsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                schema_name: str, 
                table_name: str, 
                column_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> SqlPoolColumn: ...


    class azure.mgmt.synapse.aio.operations.SqlPoolConnectionPoliciesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                connection_policy_name: Union[str, ConnectionPolicyName], 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> SqlPoolConnectionPolicy: ...


    class azure.mgmt.synapse.aio.operations.SqlPoolDataWarehouseUserActivitiesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                data_warehouse_user_activity_name: Union[str, DataWarehouseUserActivityName], 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> DataWarehouseUserActivities: ...


    class azure.mgmt.synapse.aio.operations.SqlPoolGeoBackupPoliciesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                geo_backup_policy_name: Union[str, GeoBackupPolicyName], 
                parameters: GeoBackupPolicy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GeoBackupPolicy: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                geo_backup_policy_name: Union[str, GeoBackupPolicyName], 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GeoBackupPolicy: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                geo_backup_policy_name: Union[str, GeoBackupPolicyName], 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> GeoBackupPolicy: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[GeoBackupPolicy]: ...


    class azure.mgmt.synapse.aio.operations.SqlPoolMaintenanceWindowOptionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                maintenance_window_options_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> MaintenanceWindowOptions: ...


    class azure.mgmt.synapse.aio.operations.SqlPoolMaintenanceWindowsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                maintenance_window_name: str, 
                parameters: MaintenanceWindows, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                maintenance_window_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                maintenance_window_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> MaintenanceWindows: ...


    class azure.mgmt.synapse.aio.operations.SqlPoolMetadataSyncConfigsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                metadata_sync_configuration: MetadataSyncConfig, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MetadataSyncConfig: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                metadata_sync_configuration: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MetadataSyncConfig: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> MetadataSyncConfig: ...


    class azure.mgmt.synapse.aio.operations.SqlPoolOperationResultsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_get_location_header_result(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                operation_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[SqlPool]: ...


    class azure.mgmt.synapse.aio.operations.SqlPoolOperationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[SqlPoolOperation]: ...


    class azure.mgmt.synapse.aio.operations.SqlPoolRecommendedSensitivityLabelsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                parameters: RecommendedSensitivityLabelUpdateList, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.synapse.aio.operations.SqlPoolReplicationLinksOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get_by_name(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                link_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ReplicationLink: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[ReplicationLink]: ...


    class azure.mgmt.synapse.aio.operations.SqlPoolRestorePointsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                parameters: CreateSqlPoolRestorePointDefinition, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[RestorePoint]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[RestorePoint]: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                restore_point_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                restore_point_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> RestorePoint: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[RestorePoint]: ...


    class azure.mgmt.synapse.aio.operations.SqlPoolSchemasOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                schema_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> SqlPoolSchema: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                filter: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[SqlPoolSchema]: ...


    class azure.mgmt.synapse.aio.operations.SqlPoolSecurityAlertPoliciesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                security_alert_policy_name: Union[str, SecurityAlertPolicyName], 
                parameters: SqlPoolSecurityAlertPolicy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SqlPoolSecurityAlertPolicy: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                security_alert_policy_name: Union[str, SecurityAlertPolicyName], 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SqlPoolSecurityAlertPolicy: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                security_alert_policy_name: Union[str, SecurityAlertPolicyName], 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> SqlPoolSecurityAlertPolicy: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[SqlPoolSecurityAlertPolicy]: ...


    class azure.mgmt.synapse.aio.operations.SqlPoolSensitivityLabelsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                schema_name: str, 
                table_name: str, 
                column_name: str, 
                parameters: SensitivityLabel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SensitivityLabel: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                schema_name: str, 
                table_name: str, 
                column_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SensitivityLabel: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                schema_name: str, 
                table_name: str, 
                column_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                sensitivity_label_source: str = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def disable_recommendation(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                schema_name: str, 
                table_name: str, 
                column_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                sensitivity_label_source: str = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def enable_recommendation(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                schema_name: str, 
                table_name: str, 
                column_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                sensitivity_label_source: str = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                schema_name: str, 
                table_name: str, 
                column_name: str, 
                sensitivity_label_source: Union[str, SensitivityLabelSource], 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> SensitivityLabel: ...

        @distributed_trace
        def list_current(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                filter: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[SensitivityLabel]: ...

        @distributed_trace
        def list_recommended(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                include_disabled_recommendations: Optional[bool] = None, 
                skip_token: Optional[str] = None, 
                filter: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[SensitivityLabel]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                parameters: SensitivityLabelUpdateList, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.synapse.aio.operations.SqlPoolTableColumnsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_by_table_name(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                schema_name: str, 
                table_name: str, 
                filter: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[SqlPoolColumn]: ...


    class azure.mgmt.synapse.aio.operations.SqlPoolTablesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                schema_name: str, 
                table_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> SqlPoolTable: ...

        @distributed_trace
        def list_by_schema(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                schema_name: str, 
                filter: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[SqlPoolTable]: ...


    class azure.mgmt.synapse.aio.operations.SqlPoolTransparentDataEncryptionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                transparent_data_encryption_name: Union[str, TransparentDataEncryptionName], 
                parameters: TransparentDataEncryption, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TransparentDataEncryption: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                transparent_data_encryption_name: Union[str, TransparentDataEncryptionName], 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TransparentDataEncryption: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                transparent_data_encryption_name: Union[str, TransparentDataEncryptionName], 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> TransparentDataEncryption: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[TransparentDataEncryption]: ...


    class azure.mgmt.synapse.aio.operations.SqlPoolUsagesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[SqlPoolUsage]: ...


    class azure.mgmt.synapse.aio.operations.SqlPoolVulnerabilityAssessmentRuleBaselinesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                vulnerability_assessment_name: Union[str, VulnerabilityAssessmentName], 
                rule_id: str, 
                baseline_name: Union[str, VulnerabilityAssessmentPolicyBaselineName], 
                parameters: SqlPoolVulnerabilityAssessmentRuleBaseline, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SqlPoolVulnerabilityAssessmentRuleBaseline: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                vulnerability_assessment_name: Union[str, VulnerabilityAssessmentName], 
                rule_id: str, 
                baseline_name: Union[str, VulnerabilityAssessmentPolicyBaselineName], 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SqlPoolVulnerabilityAssessmentRuleBaseline: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                vulnerability_assessment_name: Union[str, VulnerabilityAssessmentName], 
                rule_id: str, 
                baseline_name: Union[str, VulnerabilityAssessmentPolicyBaselineName], 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                vulnerability_assessment_name: Union[str, VulnerabilityAssessmentName], 
                rule_id: str, 
                baseline_name: Union[str, VulnerabilityAssessmentPolicyBaselineName], 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> SqlPoolVulnerabilityAssessmentRuleBaseline: ...


    class azure.mgmt.synapse.aio.operations.SqlPoolVulnerabilityAssessmentScansOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_initiate_scan(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                vulnerability_assessment_name: Union[str, VulnerabilityAssessmentName], 
                scan_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def export(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                vulnerability_assessment_name: Union[str, VulnerabilityAssessmentName], 
                scan_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> SqlPoolVulnerabilityAssessmentScansExport: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                vulnerability_assessment_name: Union[str, VulnerabilityAssessmentName], 
                scan_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> VulnerabilityAssessmentScanRecord: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                vulnerability_assessment_name: Union[str, VulnerabilityAssessmentName], 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[VulnerabilityAssessmentScanRecord]: ...


    class azure.mgmt.synapse.aio.operations.SqlPoolVulnerabilityAssessmentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                vulnerability_assessment_name: Union[str, VulnerabilityAssessmentName], 
                parameters: SqlPoolVulnerabilityAssessment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SqlPoolVulnerabilityAssessment: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                vulnerability_assessment_name: Union[str, VulnerabilityAssessmentName], 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SqlPoolVulnerabilityAssessment: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                vulnerability_assessment_name: Union[str, VulnerabilityAssessmentName], 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                vulnerability_assessment_name: Union[str, VulnerabilityAssessmentName], 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> SqlPoolVulnerabilityAssessment: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[SqlPoolVulnerabilityAssessment]: ...


    class azure.mgmt.synapse.aio.operations.SqlPoolWorkloadClassifierOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                workload_group_name: str, 
                workload_classifier_name: str, 
                parameters: WorkloadClassifier, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[WorkloadClassifier]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                workload_group_name: str, 
                workload_classifier_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[WorkloadClassifier]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                workload_group_name: str, 
                workload_classifier_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                workload_group_name: str, 
                workload_classifier_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> WorkloadClassifier: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                workload_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[WorkloadClassifier]: ...


    class azure.mgmt.synapse.aio.operations.SqlPoolWorkloadGroupOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                workload_group_name: str, 
                parameters: WorkloadGroup, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[WorkloadGroup]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                workload_group_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[WorkloadGroup]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                workload_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                workload_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> WorkloadGroup: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[WorkloadGroup]: ...


    class azure.mgmt.synapse.aio.operations.SqlPoolsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                sql_pool_info: SqlPool, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SqlPool]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                sql_pool_info: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SqlPool]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[SqlPool]: ...

        @distributed_trace_async
        async def begin_pause(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[SqlPool]: ...

        @distributed_trace_async
        async def begin_resume(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[SqlPool]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                sql_pool_info: SqlPoolPatchInfo, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SqlPool]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                sql_pool_info: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SqlPool]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> SqlPool: ...

        @distributed_trace
        def list_by_workspace(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[SqlPool]: ...

        @overload
        async def rename(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                parameters: ResourceMoveDefinition, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def rename(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.synapse.aio.operations.WorkspaceAadAdminsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                aad_admin_info: WorkspaceAadAdminInfo, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[WorkspaceAadAdminInfo]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                aad_admin_info: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[WorkspaceAadAdminInfo]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> WorkspaceAadAdminInfo: ...


    class azure.mgmt.synapse.aio.operations.WorkspaceManagedIdentitySqlControlSettingsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                managed_identity_sql_control_settings: ManagedIdentitySqlControlSettingsModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ManagedIdentitySqlControlSettingsModel]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                managed_identity_sql_control_settings: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ManagedIdentitySqlControlSettingsModel]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ManagedIdentitySqlControlSettingsModel: ...


    class azure.mgmt.synapse.aio.operations.WorkspaceManagedSqlServerBlobAuditingPoliciesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                blob_auditing_policy_name: Union[str, BlobAuditingPolicyName], 
                parameters: ServerBlobAuditingPolicy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ServerBlobAuditingPolicy]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                blob_auditing_policy_name: Union[str, BlobAuditingPolicyName], 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ServerBlobAuditingPolicy]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                blob_auditing_policy_name: Union[str, BlobAuditingPolicyName], 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ServerBlobAuditingPolicy: ...

        @distributed_trace
        def list_by_workspace(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[ServerBlobAuditingPolicy]: ...


    class azure.mgmt.synapse.aio.operations.WorkspaceManagedSqlServerDedicatedSQLMinimalTlsSettingsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                dedicated_sq_lminimal_tls_settings_name: Union[str, DedicatedSQLMinimalTlsSettingsName], 
                parameters: DedicatedSQLminimalTlsSettings, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DedicatedSQLminimalTlsSettings]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                dedicated_sq_lminimal_tls_settings_name: Union[str, DedicatedSQLMinimalTlsSettingsName], 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DedicatedSQLminimalTlsSettings]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                dedicated_sq_lminimal_tls_settings_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> DedicatedSQLminimalTlsSettings: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[DedicatedSQLminimalTlsSettings]: ...


    class azure.mgmt.synapse.aio.operations.WorkspaceManagedSqlServerEncryptionProtectorOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                encryption_protector_name: Union[str, EncryptionProtectorName], 
                parameters: EncryptionProtector, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EncryptionProtector]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                encryption_protector_name: Union[str, EncryptionProtectorName], 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EncryptionProtector]: ...

        @distributed_trace_async
        async def begin_revalidate(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                encryption_protector_name: Union[str, EncryptionProtectorName], 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                encryption_protector_name: Union[str, EncryptionProtectorName], 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> EncryptionProtector: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[EncryptionProtector]: ...


    class azure.mgmt.synapse.aio.operations.WorkspaceManagedSqlServerExtendedBlobAuditingPoliciesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                blob_auditing_policy_name: Union[str, BlobAuditingPolicyName], 
                parameters: ExtendedServerBlobAuditingPolicy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ExtendedServerBlobAuditingPolicy]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                blob_auditing_policy_name: Union[str, BlobAuditingPolicyName], 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ExtendedServerBlobAuditingPolicy]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                blob_auditing_policy_name: Union[str, BlobAuditingPolicyName], 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ExtendedServerBlobAuditingPolicy: ...

        @distributed_trace
        def list_by_workspace(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[ExtendedServerBlobAuditingPolicy]: ...


    class azure.mgmt.synapse.aio.operations.WorkspaceManagedSqlServerRecoverableSqlPoolsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> RecoverableSqlPool: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[RecoverableSqlPool]: ...


    class azure.mgmt.synapse.aio.operations.WorkspaceManagedSqlServerSecurityAlertPolicyOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                security_alert_policy_name: Union[str, SecurityAlertPolicyNameAutoGenerated], 
                parameters: ServerSecurityAlertPolicy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ServerSecurityAlertPolicy]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                security_alert_policy_name: Union[str, SecurityAlertPolicyNameAutoGenerated], 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ServerSecurityAlertPolicy]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                security_alert_policy_name: Union[str, SecurityAlertPolicyNameAutoGenerated], 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ServerSecurityAlertPolicy: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[ServerSecurityAlertPolicy]: ...


    class azure.mgmt.synapse.aio.operations.WorkspaceManagedSqlServerUsagesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[ServerUsage]: ...


    class azure.mgmt.synapse.aio.operations.WorkspaceManagedSqlServerVulnerabilityAssessmentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                vulnerability_assessment_name: Union[str, VulnerabilityAssessmentName], 
                parameters: ServerVulnerabilityAssessment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ServerVulnerabilityAssessment: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                vulnerability_assessment_name: Union[str, VulnerabilityAssessmentName], 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ServerVulnerabilityAssessment: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                vulnerability_assessment_name: Union[str, VulnerabilityAssessmentName], 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                vulnerability_assessment_name: Union[str, VulnerabilityAssessmentName], 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ServerVulnerabilityAssessment: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[ServerVulnerabilityAssessment]: ...


    class azure.mgmt.synapse.aio.operations.WorkspaceSqlAadAdminsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                aad_admin_info: WorkspaceAadAdminInfo, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[WorkspaceAadAdminInfo]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                aad_admin_info: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[WorkspaceAadAdminInfo]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> WorkspaceAadAdminInfo: ...


    class azure.mgmt.synapse.aio.operations.WorkspacesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                workspace_info: Workspace, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Workspace]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                workspace_info: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Workspace]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[Workspace]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                workspace_patch_info: WorkspacePatchInfo, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Workspace]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                workspace_patch_info: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Workspace]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Workspace: ...

        @distributed_trace
        def list(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[Workspace]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[Workspace]: ...


namespace azure.mgmt.synapse.models

    class azure.mgmt.synapse.models.ActualState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        DISABLING = "Disabling"
        ENABLED = "Enabled"
        ENABLING = "Enabling"
        UNKNOWN = "Unknown"


    class azure.mgmt.synapse.models.AttachedDatabaseConfiguration(ProxyResource):
        attached_database_names: list[str]
        database_name: str
        default_principals_modification_kind: Union[str, DefaultPrincipalsModificationKind]
        id: str
        kusto_pool_resource_id: str
        location: str
        name: str
        provisioning_state: Union[str, ResourceProvisioningState]
        system_data: SystemData
        table_level_sharing_properties: TableLevelSharingProperties
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                database_name: Optional[str] = ..., 
                default_principals_modification_kind: Optional[Union[str, DefaultPrincipalsModificationKind]] = ..., 
                kusto_pool_resource_id: Optional[str] = ..., 
                location: Optional[str] = ..., 
                table_level_sharing_properties: Optional[TableLevelSharingProperties] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.AttachedDatabaseConfigurationListResult(Model):
        value: list[AttachedDatabaseConfiguration]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[AttachedDatabaseConfiguration]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.AutoPauseProperties(Model):
        delay_in_minutes: int
        enabled: bool

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                delay_in_minutes: Optional[int] = ..., 
                enabled: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.AutoScaleProperties(Model):
        enabled: bool
        max_node_count: int
        min_node_count: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ..., 
                max_node_count: Optional[int] = ..., 
                min_node_count: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.AvailableRpOperation(Model):
        display: AvailableRpOperationDisplayInfo
        is_data_action: str
        name: str
        origin: str
        service_specification: OperationMetaServiceSpecification

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                display: Optional[AvailableRpOperationDisplayInfo] = ..., 
                is_data_action: Optional[str] = ..., 
                name: Optional[str] = ..., 
                origin: Optional[str] = ..., 
                service_specification: Optional[OperationMetaServiceSpecification] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.AvailableRpOperationDisplayInfo(Model):
        description: str
        operation: str
        provider: str
        resource: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                operation: Optional[str] = ..., 
                provider: Optional[str] = ..., 
                resource: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.AzureADOnlyAuthentication(ProxyResource):
        azure_ad_only_authentication: bool
        creation_date: datetime
        id: str
        name: str
        state: Union[str, StateValue]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                azure_ad_only_authentication: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.AzureADOnlyAuthenticationListResult(Model):
        next_link: str
        value: list[AzureADOnlyAuthentication]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.AzureADOnlyAuthenticationName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEFAULT = "default"


    class azure.mgmt.synapse.models.AzureCapacity(Model):
        default: int
        maximum: int
        minimum: int
        scale_type: Union[str, AzureScaleType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                default: int, 
                maximum: int, 
                minimum: int, 
                scale_type: Union[str, AzureScaleType], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.AzureEntityResource(Resource):
        etag: str
        id: str
        name: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.AzureResourceSku(Model):
        capacity: AzureCapacity
        resource_type: str
        sku: AzureSku

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                capacity: Optional[AzureCapacity] = ..., 
                resource_type: Optional[str] = ..., 
                sku: Optional[AzureSku] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.AzureScaleType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTOMATIC = "automatic"
        MANUAL = "manual"
        NONE = "none"


    class azure.mgmt.synapse.models.AzureSku(Model):
        capacity: int
        name: Union[str, SkuName]
        size: Union[str, SkuSize]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                capacity: Optional[int] = ..., 
                name: Union[str, SkuName], 
                size: Union[str, SkuSize], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.BigDataPoolPatchInfo(Model):
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.BigDataPoolResourceInfo(TrackedResource):
        auto_pause: AutoPauseProperties
        auto_scale: AutoScaleProperties
        cache_size: int
        creation_date: datetime
        custom_libraries: list[LibraryInfo]
        default_spark_log_folder: str
        dynamic_executor_allocation: DynamicExecutorAllocation
        id: str
        is_autotune_enabled: bool
        is_compute_isolation_enabled: bool
        last_succeeded_timestamp: datetime
        library_requirements: LibraryRequirements
        location: str
        name: str
        node_count: int
        node_size: Union[str, NodeSize]
        node_size_family: Union[str, NodeSizeFamily]
        provisioning_state: str
        session_level_packages_enabled: bool
        spark_config_properties: SparkConfigProperties
        spark_events_folder: str
        spark_version: str
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                auto_pause: Optional[AutoPauseProperties] = ..., 
                auto_scale: Optional[AutoScaleProperties] = ..., 
                cache_size: Optional[int] = ..., 
                custom_libraries: Optional[List[LibraryInfo]] = ..., 
                default_spark_log_folder: Optional[str] = ..., 
                dynamic_executor_allocation: Optional[DynamicExecutorAllocation] = ..., 
                is_autotune_enabled: Optional[bool] = ..., 
                is_compute_isolation_enabled: Optional[bool] = ..., 
                library_requirements: Optional[LibraryRequirements] = ..., 
                location: str, 
                node_count: Optional[int] = ..., 
                node_size: Optional[Union[str, NodeSize]] = ..., 
                node_size_family: Optional[Union[str, NodeSizeFamily]] = ..., 
                provisioning_state: Optional[str] = ..., 
                session_level_packages_enabled: Optional[bool] = ..., 
                spark_config_properties: Optional[SparkConfigProperties] = ..., 
                spark_events_folder: Optional[str] = ..., 
                spark_version: Optional[str] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.BigDataPoolResourceInfoListResult(Model):
        next_link: str
        value: list[BigDataPoolResourceInfo]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[BigDataPoolResourceInfo]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.BlobAuditingPolicyName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEFAULT = "default"


    class azure.mgmt.synapse.models.BlobAuditingPolicyState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.synapse.models.BlobStorageEventType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MICROSOFT_STORAGE_BLOB_CREATED = "Microsoft.Storage.BlobCreated"
        MICROSOFT_STORAGE_BLOB_RENAMED = "Microsoft.Storage.BlobRenamed"


    class azure.mgmt.synapse.models.CheckNameAvailabilityRequest(Model):
        name: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                type: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.CheckNameAvailabilityResponse(Model):
        available: bool
        message: str
        name: str
        reason: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                available: Optional[bool] = ..., 
                message: Optional[str] = ..., 
                name: Optional[str] = ..., 
                reason: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.CheckNameResult(Model):
        message: str
        name: str
        name_available: bool
        reason: Union[str, Reason]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                message: Optional[str] = ..., 
                name: Optional[str] = ..., 
                name_available: Optional[bool] = ..., 
                reason: Optional[Union[str, Reason]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.ClusterPrincipalAssignment(ProxyResource):
        aad_object_id: str
        id: str
        name: str
        principal_id: str
        principal_name: str
        principal_type: Union[str, PrincipalType]
        provisioning_state: Union[str, ResourceProvisioningState]
        role: Union[str, ClusterPrincipalRole]
        system_data: SystemData
        tenant_id: str
        tenant_name: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                principal_id: Optional[str] = ..., 
                principal_type: Optional[Union[str, PrincipalType]] = ..., 
                role: Optional[Union[str, ClusterPrincipalRole]] = ..., 
                tenant_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.ClusterPrincipalAssignmentCheckNameRequest(Model):
        name: str
        type: str = "Microsoft.Synapse/workspaces/kustoPools/principalAssignments"

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                name: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.ClusterPrincipalAssignmentListResult(Model):
        value: list[ClusterPrincipalAssignment]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[ClusterPrincipalAssignment]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.ClusterPrincipalRole(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALL_DATABASES_ADMIN = "AllDatabasesAdmin"
        ALL_DATABASES_VIEWER = "AllDatabasesViewer"


    class azure.mgmt.synapse.models.CmdkeySetup(CustomSetupBase):
        password: SecretBase
        target_name: JSON
        type: str
        user_name: JSON

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                password: SecretBase, 
                target_name: JSON, 
                user_name: JSON, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.ColumnDataType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BIGINT = "bigint"
        BINARY = "binary"
        BIT = "bit"
        CHAR = "char"
        DATE = "date"
        DATETIME = "datetime"
        DATETIME2 = "datetime2"
        DATETIMEOFFSET = "datetimeoffset"
        DECIMAL = "decimal"
        FLOAT = "float"
        GEOGRAPHY = "geography"
        GEOMETRY = "geometry"
        HIERARCHYID = "hierarchyid"
        IMAGE = "image"
        INT = "int"
        MONEY = "money"
        NCHAR = "nchar"
        NTEXT = "ntext"
        NUMERIC = "numeric"
        NVARCHAR = "nvarchar"
        REAL = "real"
        SMALLDATETIME = "smalldatetime"
        SMALLINT = "smallint"
        SMALLMONEY = "smallmoney"
        SQL_VARIANT = "sql_variant"
        SYSNAME = "sysname"
        TEXT = "text"
        TIME = "time"
        TIMESTAMP = "timestamp"
        TINYINT = "tinyint"
        UNIQUEIDENTIFIER = "uniqueidentifier"
        VARBINARY = "varbinary"
        VARCHAR = "varchar"
        XML = "xml"


    class azure.mgmt.synapse.models.ComponentSetup(CustomSetupBase):
        component_name: str
        license_key: SecretBase
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                component_name: str, 
                license_key: Optional[SecretBase] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.Compression(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        G_ZIP = "GZip"
        NONE = "None"


    class azure.mgmt.synapse.models.ConfigurationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ARTIFACT = "Artifact"
        FILE = "File"


    class azure.mgmt.synapse.models.ConnectionPolicyName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEFAULT = "default"


    class azure.mgmt.synapse.models.CreateMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEFAULT = "Default"
        POINT_IN_TIME_RESTORE = "PointInTimeRestore"
        RECOVERY = "Recovery"
        RESTORE = "Restore"


    class azure.mgmt.synapse.models.CreateSqlPoolRestorePointDefinition(Model):
        restore_point_label: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                restore_point_label: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.synapse.models.CspWorkspaceAdminProperties(Model):
        initial_workspace_admin_object_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                initial_workspace_admin_object_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.CustomSetupBase(Model):
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.CustomerManagedKeyDetails(Model):
        kek_identity: KekIdentityProperties
        key: WorkspaceKeyDetails
        status: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                kek_identity: Optional[KekIdentityProperties] = ..., 
                key: Optional[WorkspaceKeyDetails] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.DataConnection(ProxyResource):
        id: str
        kind: Union[str, DataConnectionKind]
        location: str
        name: str
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.DataConnectionCheckNameRequest(Model):
        name: str
        type: str = "Microsoft.Synapse/workspaces/kustoPools/databases/dataConnections"

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                name: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.DataConnectionKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EVENT_GRID = "EventGrid"
        EVENT_HUB = "EventHub"
        IOT_HUB = "IotHub"


    class azure.mgmt.synapse.models.DataConnectionListResult(Model):
        value: list[DataConnection]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[DataConnection]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.DataConnectionValidation(Model):
        data_connection_name: str
        properties: DataConnection

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                data_connection_name: Optional[str] = ..., 
                properties: Optional[DataConnection] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.DataConnectionValidationListResult(Model):
        value: list[DataConnectionValidationResult]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[DataConnectionValidationResult]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.DataConnectionValidationResult(Model):
        error_message: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                error_message: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.DataFlowComputeType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPUTE_OPTIMIZED = "ComputeOptimized"
        GENERAL = "General"
        MEMORY_OPTIMIZED = "MemoryOptimized"


    class azure.mgmt.synapse.models.DataLakeStorageAccountDetails(Model):
        account_url: str
        create_managed_private_endpoint: bool
        filesystem: str
        resource_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                account_url: Optional[str] = ..., 
                create_managed_private_endpoint: Optional[bool] = ..., 
                filesystem: Optional[str] = ..., 
                resource_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.DataMaskingFunction(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CCN = "CCN"
        DEFAULT = "Default"
        EMAIL = "Email"
        NUMBER = "Number"
        SSN = "SSN"
        TEXT = "Text"


    class azure.mgmt.synapse.models.DataMaskingPolicy(ProxyResource):
        application_principals: str
        data_masking_state: Union[str, DataMaskingState]
        exempt_principals: str
        id: str
        kind: str
        location: str
        managed_by: str
        masking_level: str
        name: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                data_masking_state: Optional[Union[str, DataMaskingState]] = ..., 
                exempt_principals: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.DataMaskingRule(ProxyResource):
        alias_name: str
        column_name: str
        id: str
        id_properties_id: str
        kind: str
        location: str
        masking_function: Union[str, DataMaskingFunction]
        name: str
        number_from: str
        number_to: str
        prefix_size: str
        replacement_string: str
        rule_state: Union[str, DataMaskingRuleState]
        schema_name: str
        suffix_size: str
        table_name: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                alias_name: Optional[str] = ..., 
                column_name: Optional[str] = ..., 
                masking_function: Optional[Union[str, DataMaskingFunction]] = ..., 
                number_from: Optional[str] = ..., 
                number_to: Optional[str] = ..., 
                prefix_size: Optional[str] = ..., 
                replacement_string: Optional[str] = ..., 
                rule_state: Optional[Union[str, DataMaskingRuleState]] = ..., 
                schema_name: Optional[str] = ..., 
                suffix_size: Optional[str] = ..., 
                table_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.DataMaskingRuleListResult(Model):
        value: list[DataMaskingRule]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[DataMaskingRule]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.DataMaskingRuleState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.synapse.models.DataMaskingState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.synapse.models.DataWarehouseUserActivities(ProxyResource):
        active_queries_count: int
        id: str
        name: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.DataWarehouseUserActivityName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CURRENT = "current"


    class azure.mgmt.synapse.models.Database(ProxyResource):
        id: str
        kind: Union[str, Kind]
        location: str
        name: str
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.DatabaseCheckNameRequest(Model):
        name: str
        type: Union[str, Type]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                name: str, 
                type: Union[str, Type], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.DatabaseListResult(Model):
        value: list[Database]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[Database]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.DatabasePrincipalAssignment(ProxyResource):
        aad_object_id: str
        id: str
        name: str
        principal_id: str
        principal_name: str
        principal_type: Union[str, PrincipalType]
        provisioning_state: Union[str, ResourceProvisioningState]
        role: Union[str, DatabasePrincipalRole]
        system_data: SystemData
        tenant_id: str
        tenant_name: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                principal_id: Optional[str] = ..., 
                principal_type: Optional[Union[str, PrincipalType]] = ..., 
                role: Optional[Union[str, DatabasePrincipalRole]] = ..., 
                tenant_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.DatabasePrincipalAssignmentCheckNameRequest(Model):
        name: str
        type: str = "Microsoft.Synapse/workspaces/kustoPools/databases/principalAssignments"

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                name: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.DatabasePrincipalAssignmentListResult(Model):
        value: list[DatabasePrincipalAssignment]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[DatabasePrincipalAssignment]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.DatabasePrincipalRole(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ADMIN = "Admin"
        INGESTOR = "Ingestor"
        MONITOR = "Monitor"
        UNRESTRICTED_VIEWER = "UnrestrictedViewer"
        USER = "User"
        VIEWER = "Viewer"


    class azure.mgmt.synapse.models.DatabaseStatistics(Model):
        size: float

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                size: Optional[float] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.DayOfWeek(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FRIDAY = "Friday"
        MONDAY = "Monday"
        SATURDAY = "Saturday"
        SUNDAY = "Sunday"
        THURSDAY = "Thursday"
        TUESDAY = "Tuesday"
        WEDNESDAY = "Wednesday"


    class azure.mgmt.synapse.models.DedicatedSQLMinimalTlsSettingsName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEFAULT = "default"


    class azure.mgmt.synapse.models.DedicatedSQLminimalTlsSettings(ProxyResource):
        id: str
        location: str
        minimal_tls_version: str
        name: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                minimal_tls_version: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.DedicatedSQLminimalTlsSettingsListResult(Model):
        next_link: str
        value: list[DedicatedSQLminimalTlsSettings]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.DedicatedSQLminimalTlsSettingsPatchInfo(Model):
        minimal_tls_version: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                minimal_tls_version: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.DefaultPrincipalsModificationKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        REPLACE = "Replace"
        UNION = "Union"


    class azure.mgmt.synapse.models.DesiredState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.synapse.models.DynamicExecutorAllocation(Model):
        enabled: bool
        max_executors: int
        min_executors: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ..., 
                max_executors: Optional[int] = ..., 
                min_executors: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.EncryptionDetails(Model):
        cmk: CustomerManagedKeyDetails
        double_encryption_enabled: bool

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                cmk: Optional[CustomerManagedKeyDetails] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.EncryptionProtector(ProxyResource):
        id: str
        kind: str
        location: str
        name: str
        server_key_name: str
        server_key_type: Union[str, ServerKeyType]
        subregion: str
        thumbprint: str
        type: str
        uri: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                server_key_name: Optional[str] = ..., 
                server_key_type: Optional[Union[str, ServerKeyType]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.EncryptionProtectorListResult(Model):
        next_link: str
        value: list[EncryptionProtector]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.EncryptionProtectorName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CURRENT = "current"


    class azure.mgmt.synapse.models.EntityReference(Model):
        reference_name: str
        type: Union[str, IntegrationRuntimeEntityReferenceType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                reference_name: Optional[str] = ..., 
                type: Optional[Union[str, IntegrationRuntimeEntityReferenceType]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.EnvironmentVariableSetup(CustomSetupBase):
        type: str
        variable_name: str
        variable_value: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                variable_name: str, 
                variable_value: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.ErrorAdditionalInfo(Model):
        info: JSON
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.ErrorDetail(Model):
        additional_info: list[ErrorAdditionalInfo]
        code: str
        details: list[ErrorDetail]
        message: str
        target: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.ErrorResponse(Model):
        error: ErrorDetail

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.ErrorResponseAutoGenerated(Model):
        additional_info: list[ErrorAdditionalInfo]
        code: str
        details: list[ErrorResponseAutoGenerated]
        message: str
        target: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.EventGridDataConnection(DataConnection):
        blob_storage_event_type: Union[str, BlobStorageEventType]
        consumer_group: str
        data_format: Union[str, EventGridDataFormat]
        event_hub_resource_id: str
        id: str
        ignore_first_record: bool
        kind: Union[str, DataConnectionKind]
        location: str
        mapping_rule_name: str
        name: str
        provisioning_state: Union[str, ResourceProvisioningState]
        storage_account_resource_id: str
        system_data: SystemData
        table_name: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                blob_storage_event_type: Optional[Union[str, BlobStorageEventType]] = ..., 
                consumer_group: Optional[str] = ..., 
                data_format: Optional[Union[str, EventGridDataFormat]] = ..., 
                event_hub_resource_id: Optional[str] = ..., 
                ignore_first_record: Optional[bool] = ..., 
                location: Optional[str] = ..., 
                mapping_rule_name: Optional[str] = ..., 
                storage_account_resource_id: Optional[str] = ..., 
                table_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.EventGridDataFormat(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APACHEAVRO = "APACHEAVRO"
        AVRO = "AVRO"
        CSV = "CSV"
        JSON = "JSON"
        MULTIJSON = "MULTIJSON"
        ORC = "ORC"
        PARQUET = "PARQUET"
        PSV = "PSV"
        RAW = "RAW"
        SCSV = "SCSV"
        SINGLEJSON = "SINGLEJSON"
        SOHSV = "SOHSV"
        TSV = "TSV"
        TSVE = "TSVE"
        TXT = "TXT"
        W3_CLOGFILE = "W3CLOGFILE"


    class azure.mgmt.synapse.models.EventHubDataConnection(DataConnection):
        compression: Union[str, Compression]
        consumer_group: str
        data_format: Union[str, EventHubDataFormat]
        event_hub_resource_id: str
        event_system_properties: list[str]
        id: str
        kind: Union[str, DataConnectionKind]
        location: str
        managed_identity_resource_id: str
        mapping_rule_name: str
        name: str
        provisioning_state: Union[str, ResourceProvisioningState]
        system_data: SystemData
        table_name: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                compression: Optional[Union[str, Compression]] = ..., 
                consumer_group: Optional[str] = ..., 
                data_format: Optional[Union[str, EventHubDataFormat]] = ..., 
                event_hub_resource_id: Optional[str] = ..., 
                event_system_properties: Optional[List[str]] = ..., 
                location: Optional[str] = ..., 
                managed_identity_resource_id: Optional[str] = ..., 
                mapping_rule_name: Optional[str] = ..., 
                table_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.EventHubDataFormat(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APACHEAVRO = "APACHEAVRO"
        AVRO = "AVRO"
        CSV = "CSV"
        JSON = "JSON"
        MULTIJSON = "MULTIJSON"
        ORC = "ORC"
        PARQUET = "PARQUET"
        PSV = "PSV"
        RAW = "RAW"
        SCSV = "SCSV"
        SINGLEJSON = "SINGLEJSON"
        SOHSV = "SOHSV"
        TSV = "TSV"
        TSVE = "TSVE"
        TXT = "TXT"
        W3_CLOGFILE = "W3CLOGFILE"


    class azure.mgmt.synapse.models.ExtendedServerBlobAuditingPolicy(ProxyResource):
        audit_actions_and_groups: list[str]
        id: str
        is_azure_monitor_target_enabled: bool
        is_devops_audit_enabled: bool
        is_storage_secondary_key_in_use: bool
        name: str
        predicate_expression: str
        queue_delay_ms: int
        retention_days: int
        state: Union[str, BlobAuditingPolicyState]
        storage_account_access_key: str
        storage_account_subscription_id: str
        storage_endpoint: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                audit_actions_and_groups: Optional[List[str]] = ..., 
                is_azure_monitor_target_enabled: Optional[bool] = ..., 
                is_devops_audit_enabled: Optional[bool] = ..., 
                is_storage_secondary_key_in_use: Optional[bool] = ..., 
                predicate_expression: Optional[str] = ..., 
                queue_delay_ms: Optional[int] = ..., 
                retention_days: Optional[int] = ..., 
                state: Optional[Union[str, BlobAuditingPolicyState]] = ..., 
                storage_account_access_key: Optional[str] = ..., 
                storage_account_subscription_id: Optional[str] = ..., 
                storage_endpoint: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.ExtendedServerBlobAuditingPolicyListResult(Model):
        next_link: str
        value: list[ExtendedServerBlobAuditingPolicy]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.ExtendedSqlPoolBlobAuditingPolicy(ProxyResource):
        audit_actions_and_groups: list[str]
        id: str
        is_azure_monitor_target_enabled: bool
        is_storage_secondary_key_in_use: bool
        name: str
        predicate_expression: str
        queue_delay_ms: int
        retention_days: int
        state: Union[str, BlobAuditingPolicyState]
        storage_account_access_key: str
        storage_account_subscription_id: str
        storage_endpoint: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                audit_actions_and_groups: Optional[List[str]] = ..., 
                is_azure_monitor_target_enabled: Optional[bool] = ..., 
                is_storage_secondary_key_in_use: Optional[bool] = ..., 
                predicate_expression: Optional[str] = ..., 
                queue_delay_ms: Optional[int] = ..., 
                retention_days: Optional[int] = ..., 
                state: Optional[Union[str, BlobAuditingPolicyState]] = ..., 
                storage_account_access_key: Optional[str] = ..., 
                storage_account_subscription_id: Optional[str] = ..., 
                storage_endpoint: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.ExtendedSqlPoolBlobAuditingPolicyListResult(Model):
        next_link: str
        value: list[ExtendedSqlPoolBlobAuditingPolicy]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.FollowerDatabaseDefinition(Model):
        attached_database_configuration_name: str
        database_name: str
        kusto_pool_resource_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                attached_database_configuration_name: str, 
                kusto_pool_resource_id: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.FollowerDatabaseListResult(Model):
        value: list[FollowerDatabaseDefinition]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[FollowerDatabaseDefinition]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.GeoBackupPolicy(ProxyResource):
        id: str
        kind: str
        location: str
        name: str
        state: Union[str, GeoBackupPolicyState]
        storage_type: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                state: Union[str, GeoBackupPolicyState], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.GeoBackupPolicyListResult(Model):
        value: list[GeoBackupPolicy]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[GeoBackupPolicy]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.GeoBackupPolicyName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEFAULT = "Default"


    class azure.mgmt.synapse.models.GeoBackupPolicyState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.synapse.models.GetSsisObjectMetadataRequest(Model):
        metadata_path: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                metadata_path: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.IntegrationRuntime(Model):
        additional_properties: dict[str, JSON]
        description: str
        type: Union[str, IntegrationRuntimeType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                additional_properties: Optional[Dict[str, JSON]] = ..., 
                description: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.IntegrationRuntimeAuthKeyName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTH_KEY1 = "authKey1"
        AUTH_KEY2 = "authKey2"


    class azure.mgmt.synapse.models.IntegrationRuntimeAuthKeys(Model):
        auth_key1: str
        auth_key2: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                auth_key1: Optional[str] = ..., 
                auth_key2: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.IntegrationRuntimeAutoUpdate(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        OFF = "Off"
        ON = "On"


    class azure.mgmt.synapse.models.IntegrationRuntimeComputeProperties(Model):
        additional_properties: dict[str, JSON]
        data_flow_properties: IntegrationRuntimeDataFlowProperties
        location: str
        max_parallel_executions_per_node: int
        node_size: str
        number_of_nodes: int
        v_net_properties: IntegrationRuntimeVNetProperties

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                additional_properties: Optional[Dict[str, JSON]] = ..., 
                data_flow_properties: Optional[IntegrationRuntimeDataFlowProperties] = ..., 
                location: Optional[str] = ..., 
                max_parallel_executions_per_node: Optional[int] = ..., 
                node_size: Optional[str] = ..., 
                number_of_nodes: Optional[int] = ..., 
                v_net_properties: Optional[IntegrationRuntimeVNetProperties] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.IntegrationRuntimeConnectionInfo(Model):
        additional_properties: dict[str, JSON]
        host_service_uri: str
        identity_cert_thumbprint: str
        is_identity_cert_exprired: bool
        public_key: str
        service_token: str
        version: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                additional_properties: Optional[Dict[str, JSON]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.IntegrationRuntimeCustomSetupScriptProperties(Model):
        blob_container_uri: str
        sas_token: SecureString

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                blob_container_uri: Optional[str] = ..., 
                sas_token: Optional[SecureString] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.IntegrationRuntimeDataFlowProperties(Model):
        additional_properties: dict[str, JSON]
        cleanup: bool
        compute_type: Union[str, DataFlowComputeType]
        core_count: int
        time_to_live: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                additional_properties: Optional[Dict[str, JSON]] = ..., 
                cleanup: Optional[bool] = ..., 
                compute_type: Optional[Union[str, DataFlowComputeType]] = ..., 
                core_count: Optional[int] = ..., 
                time_to_live: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.IntegrationRuntimeDataProxyProperties(Model):
        connect_via: EntityReference
        path: str
        staging_linked_service: EntityReference

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                connect_via: Optional[EntityReference] = ..., 
                path: Optional[str] = ..., 
                staging_linked_service: Optional[EntityReference] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.IntegrationRuntimeEdition(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ENTERPRISE = "Enterprise"
        STANDARD = "Standard"


    class azure.mgmt.synapse.models.IntegrationRuntimeEnableinteractivequery(Model):
        error: str
        name: str
        properties: JSON
        status: Union[str, WorkspaceStatus]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                error: Optional[str] = ..., 
                name: Optional[str] = ..., 
                properties: Optional[JSON] = ..., 
                status: Optional[Union[str, WorkspaceStatus]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.IntegrationRuntimeEntityReferenceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTEGRATION_RUNTIME_REFERENCE = "IntegrationRuntimeReference"
        LINKED_SERVICE_REFERENCE = "LinkedServiceReference"


    class azure.mgmt.synapse.models.IntegrationRuntimeInternalChannelEncryptionMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NOT_ENCRYPTED = "NotEncrypted"
        NOT_SET = "NotSet"
        SSL_ENCRYPTED = "SslEncrypted"


    class azure.mgmt.synapse.models.IntegrationRuntimeLicenseType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BASE_PRICE = "BasePrice"
        LICENSE_INCLUDED = "LicenseIncluded"


    class azure.mgmt.synapse.models.IntegrationRuntimeListResponse(Model):
        next_link: str
        value: list[IntegrationRuntimeResource]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: List[IntegrationRuntimeResource], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.IntegrationRuntimeMonitoringData(Model):
        name: str
        nodes: list[IntegrationRuntimeNodeMonitoringData]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                nodes: Optional[List[IntegrationRuntimeNodeMonitoringData]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.IntegrationRuntimeNodeIpAddress(Model):
        ip_address: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.IntegrationRuntimeNodeMonitoringData(Model):
        additional_properties: dict[str, JSON]
        available_memory_in_mb: int
        concurrent_jobs_limit: int
        concurrent_jobs_running: int
        cpu_utilization: int
        max_concurrent_jobs: int
        node_name: str
        received_bytes: float
        sent_bytes: float

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                additional_properties: Optional[Dict[str, JSON]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.IntegrationRuntimeOperationStatus(Model):
        error: str
        name: str
        properties: JSON
        status: Union[str, WorkspaceStatus]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                error: Optional[str] = ..., 
                name: Optional[str] = ..., 
                properties: Optional[JSON] = ..., 
                status: Optional[Union[str, WorkspaceStatus]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.IntegrationRuntimeOutboundNetworkDependenciesCategoryEndpoint(Model):
        category: str
        endpoints: list[IntegrationRuntimeOutboundNetworkDependenciesEndpoint]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                category: Optional[str] = ..., 
                endpoints: Optional[List[IntegrationRuntimeOutboundNetworkDependenciesEndpoint]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.IntegrationRuntimeOutboundNetworkDependenciesEndpoint(Model):
        domain_name: str
        endpoint_details: list[IntegrationRuntimeOutboundNetworkDependenciesEndpointDetails]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                domain_name: Optional[str] = ..., 
                endpoint_details: Optional[List[IntegrationRuntimeOutboundNetworkDependenciesEndpointDetails]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.IntegrationRuntimeOutboundNetworkDependenciesEndpointDetails(Model):
        port: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                port: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.IntegrationRuntimeOutboundNetworkDependenciesEndpointsResponse(Model):
        value: list[IntegrationRuntimeOutboundNetworkDependenciesCategoryEndpoint]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[IntegrationRuntimeOutboundNetworkDependenciesCategoryEndpoint]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.IntegrationRuntimeRegenerateKeyParameters(Model):
        key_name: Union[str, IntegrationRuntimeAuthKeyName]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                key_name: Optional[Union[str, IntegrationRuntimeAuthKeyName]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.IntegrationRuntimeResource(SubResource):
        description: str
        etag: str
        id: str
        name: str
        type: str
        type_properties_type: Union[str, IntegrationRuntimeType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.IntegrationRuntimeSsisCatalogInfo(Model):
        additional_properties: dict[str, JSON]
        catalog_admin_password: SecureString
        catalog_admin_user_name: str
        catalog_pricing_tier: Union[str, IntegrationRuntimeSsisCatalogPricingTier]
        catalog_server_endpoint: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                additional_properties: Optional[Dict[str, JSON]] = ..., 
                catalog_admin_password: Optional[SecureString] = ..., 
                catalog_admin_user_name: Optional[str] = ..., 
                catalog_pricing_tier: Optional[Union[str, IntegrationRuntimeSsisCatalogPricingTier]] = ..., 
                catalog_server_endpoint: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.IntegrationRuntimeSsisCatalogPricingTier(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BASIC = "Basic"
        PREMIUM = "Premium"
        PREMIUM_RS = "PremiumRS"
        STANDARD = "Standard"


    class azure.mgmt.synapse.models.IntegrationRuntimeSsisProperties(Model):
        additional_properties: dict[str, JSON]
        catalog_info: IntegrationRuntimeSsisCatalogInfo
        custom_setup_script_properties: IntegrationRuntimeCustomSetupScriptProperties
        data_proxy_properties: IntegrationRuntimeDataProxyProperties
        edition: Union[str, IntegrationRuntimeEdition]
        express_custom_setup_properties: list[CustomSetupBase]
        license_type: Union[str, IntegrationRuntimeLicenseType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                additional_properties: Optional[Dict[str, JSON]] = ..., 
                catalog_info: Optional[IntegrationRuntimeSsisCatalogInfo] = ..., 
                custom_setup_script_properties: Optional[IntegrationRuntimeCustomSetupScriptProperties] = ..., 
                data_proxy_properties: Optional[IntegrationRuntimeDataProxyProperties] = ..., 
                edition: Optional[Union[str, IntegrationRuntimeEdition]] = ..., 
                express_custom_setup_properties: Optional[List[CustomSetupBase]] = ..., 
                license_type: Optional[Union[str, IntegrationRuntimeLicenseType]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.IntegrationRuntimeState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCESS_DENIED = "AccessDenied"
        INITIAL = "Initial"
        LIMITED = "Limited"
        NEED_REGISTRATION = "NeedRegistration"
        OFFLINE = "Offline"
        ONLINE = "Online"
        STARTED = "Started"
        STARTING = "Starting"
        STOPPED = "Stopped"
        STOPPING = "Stopping"


    class azure.mgmt.synapse.models.IntegrationRuntimeStatus(Model):
        additional_properties: dict[str, JSON]
        data_factory_name: str
        state: Union[str, IntegrationRuntimeState]
        type: Union[str, IntegrationRuntimeType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                additional_properties: Optional[Dict[str, JSON]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.IntegrationRuntimeStatusResponse(Model):
        data_factory_name: str
        name: str
        state: Union[str, IntegrationRuntimeState]
        type: Union[str, IntegrationRuntimeType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.IntegrationRuntimeStopOperationStatus(Model):
        error: str
        name: str
        properties: JSON
        status: Union[str, WorkspaceStatus]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                error: Optional[str] = ..., 
                name: Optional[str] = ..., 
                properties: Optional[JSON] = ..., 
                status: Optional[Union[str, WorkspaceStatus]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.IntegrationRuntimeType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MANAGED = "Managed"
        SELF_HOSTED = "SelfHosted"


    class azure.mgmt.synapse.models.IntegrationRuntimeUpdateResult(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAIL = "Fail"
        NONE = "None"
        SUCCEED = "Succeed"


    class azure.mgmt.synapse.models.IntegrationRuntimeVNetProperties(Model):
        additional_properties: dict[str, JSON]
        public_i_ps: list[str]
        subnet: str
        subnet_id: str
        v_net_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                additional_properties: Optional[Dict[str, JSON]] = ..., 
                public_i_ps: Optional[List[str]] = ..., 
                subnet: Optional[str] = ..., 
                subnet_id: Optional[str] = ..., 
                v_net_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.IotHubDataConnection(DataConnection):
        consumer_group: str
        data_format: Union[str, IotHubDataFormat]
        event_system_properties: list[str]
        id: str
        iot_hub_resource_id: str
        kind: Union[str, DataConnectionKind]
        location: str
        mapping_rule_name: str
        name: str
        provisioning_state: Union[str, ResourceProvisioningState]
        shared_access_policy_name: str
        system_data: SystemData
        table_name: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                consumer_group: Optional[str] = ..., 
                data_format: Optional[Union[str, IotHubDataFormat]] = ..., 
                event_system_properties: Optional[List[str]] = ..., 
                iot_hub_resource_id: Optional[str] = ..., 
                location: Optional[str] = ..., 
                mapping_rule_name: Optional[str] = ..., 
                shared_access_policy_name: Optional[str] = ..., 
                table_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.IotHubDataFormat(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APACHEAVRO = "APACHEAVRO"
        AVRO = "AVRO"
        CSV = "CSV"
        JSON = "JSON"
        MULTIJSON = "MULTIJSON"
        ORC = "ORC"
        PARQUET = "PARQUET"
        PSV = "PSV"
        RAW = "RAW"
        SCSV = "SCSV"
        SINGLEJSON = "SINGLEJSON"
        SOHSV = "SOHSV"
        TSV = "TSV"
        TSVE = "TSVE"
        TXT = "TXT"
        W3_CLOGFILE = "W3CLOGFILE"


    class azure.mgmt.synapse.models.IpFirewallRuleInfo(ProxyResource):
        end_ip_address: str
        id: str
        name: str
        provisioning_state: Union[str, ProvisioningState]
        start_ip_address: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                end_ip_address: Optional[str] = ..., 
                start_ip_address: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.IpFirewallRuleInfoListResult(Model):
        next_link: str
        value: list[IpFirewallRuleInfo]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[IpFirewallRuleInfo]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.IpFirewallRuleProperties(Model):
        end_ip_address: str
        provisioning_state: Union[str, ProvisioningState]
        start_ip_address: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                end_ip_address: Optional[str] = ..., 
                start_ip_address: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.KekIdentityProperties(Model):
        use_system_assigned_identity: any
        user_assigned_identity: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                use_system_assigned_identity: Optional[Any] = ..., 
                user_assigned_identity: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.Key(ProxyResource):
        id: str
        is_active_cmk: bool
        key_vault_url: str
        name: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                is_active_cmk: Optional[bool] = ..., 
                key_vault_url: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.KeyInfoListResult(Model):
        next_link: str
        value: list[Key]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[Key]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.Kind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        READ_ONLY_FOLLOWING = "ReadOnlyFollowing"
        READ_WRITE = "ReadWrite"


    class azure.mgmt.synapse.models.KustoPool(TrackedResource):
        data_ingestion_uri: str
        enable_purge: bool
        enable_streaming_ingest: bool
        etag: str
        id: str
        language_extensions: LanguageExtensionsList
        location: str
        name: str
        optimized_autoscale: OptimizedAutoscale
        provisioning_state: Union[str, ResourceProvisioningState]
        sku: AzureSku
        state: Union[str, State]
        state_reason: str
        system_data: SystemData
        tags: dict[str, str]
        type: str
        uri: str
        workspace_uid: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                enable_purge: bool = False, 
                enable_streaming_ingest: bool = False, 
                location: str, 
                optimized_autoscale: Optional[OptimizedAutoscale] = ..., 
                sku: AzureSku, 
                tags: Optional[Dict[str, str]] = ..., 
                workspace_uid: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.KustoPoolCheckNameRequest(Model):
        name: str
        type: str = "Microsoft.Synapse/workspaces/kustoPools"

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                name: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.KustoPoolListResult(Model):
        value: list[KustoPool]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[KustoPool]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.KustoPoolPrivateLinkResources(ProxyResource):
        group_id: str
        id: str
        name: str
        provisioning_state: Union[str, ResourceProvisioningState]
        required_members: list[str]
        required_zone_names: list[str]
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.KustoPoolUpdate(Resource):
        data_ingestion_uri: str
        enable_purge: bool
        enable_streaming_ingest: bool
        id: str
        language_extensions: LanguageExtensionsList
        name: str
        optimized_autoscale: OptimizedAutoscale
        provisioning_state: Union[str, ResourceProvisioningState]
        sku: AzureSku
        state: Union[str, State]
        state_reason: str
        tags: dict[str, str]
        type: str
        uri: str
        workspace_uid: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                enable_purge: bool = False, 
                enable_streaming_ingest: bool = False, 
                optimized_autoscale: Optional[OptimizedAutoscale] = ..., 
                sku: Optional[AzureSku] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                workspace_uid: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.LanguageExtension(Model):
        language_extension_name: Union[str, LanguageExtensionName]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                language_extension_name: Optional[Union[str, LanguageExtensionName]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.LanguageExtensionName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PYTHON = "PYTHON"
        R = "R"


    class azure.mgmt.synapse.models.LanguageExtensionsList(Model):
        value: list[LanguageExtension]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[LanguageExtension]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.LibraryInfo(Model):
        container_name: str
        creator_id: str
        name: str
        path: str
        provisioning_status: str
        type: str
        uploaded_timestamp: datetime

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                container_name: Optional[str] = ..., 
                name: Optional[str] = ..., 
                path: Optional[str] = ..., 
                type: Optional[str] = ..., 
                uploaded_timestamp: Optional[datetime] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.LibraryListResponse(Model):
        next_link: str
        value: list[LibraryResource]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: List[LibraryResource], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.LibraryRequirements(Model):
        content: str
        filename: str
        time: datetime

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                content: Optional[str] = ..., 
                filename: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.LibraryResource(SubResource):
        container_name: str
        creator_id: str
        etag: str
        id: str
        name: str
        name_properties_name: str
        path: str
        provisioning_status: str
        type: str
        type_properties_type: str
        uploaded_timestamp: datetime

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                container_name: Optional[str] = ..., 
                name_properties_name: Optional[str] = ..., 
                path: Optional[str] = ..., 
                type_properties_type: Optional[str] = ..., 
                uploaded_timestamp: Optional[datetime] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.LinkedIntegrationRuntime(Model):
        create_time: datetime
        data_factory_location: str
        data_factory_name: str
        name: str
        subscription_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.LinkedIntegrationRuntimeKeyAuthorization(LinkedIntegrationRuntimeType):
        authorization_type: str
        key: SecureString

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                key: SecureString, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.LinkedIntegrationRuntimeRbacAuthorization(LinkedIntegrationRuntimeType):
        authorization_type: str
        resource_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                resource_id: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.LinkedIntegrationRuntimeType(Model):
        authorization_type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.ListResourceSkusResult(Model):
        value: list[AzureResourceSku]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[AzureResourceSku]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.ListSqlPoolSecurityAlertPolicies(Model):
        next_link: str
        value: list[SqlPoolSecurityAlertPolicy]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.MaintenanceWindowOptions(ProxyResource):
        allow_multiple_maintenance_windows_per_cycle: bool
        default_duration_in_minutes: int
        id: str
        is_enabled: bool
        maintenance_window_cycles: list[MaintenanceWindowTimeRange]
        min_cycles: int
        min_duration_in_minutes: int
        name: str
        time_granularity_in_minutes: int
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                allow_multiple_maintenance_windows_per_cycle: Optional[bool] = ..., 
                default_duration_in_minutes: Optional[int] = ..., 
                is_enabled: Optional[bool] = ..., 
                maintenance_window_cycles: Optional[List[MaintenanceWindowTimeRange]] = ..., 
                min_cycles: Optional[int] = ..., 
                min_duration_in_minutes: Optional[int] = ..., 
                time_granularity_in_minutes: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.MaintenanceWindowTimeRange(Model):
        day_of_week: Union[str, DayOfWeek]
        duration: str
        start_time: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                day_of_week: Optional[Union[str, DayOfWeek]] = ..., 
                duration: Optional[str] = ..., 
                start_time: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.MaintenanceWindows(ProxyResource):
        id: str
        name: str
        time_ranges: list[MaintenanceWindowTimeRange]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                time_ranges: Optional[List[MaintenanceWindowTimeRange]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.ManagedIdentity(Model):
        principal_id: str
        tenant_id: str
        type: Union[str, ResourceIdentityType]
        user_assigned_identities: dict[str, UserAssignedManagedIdentity]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                type: Optional[Union[str, ResourceIdentityType]] = ..., 
                user_assigned_identities: Optional[Dict[str, UserAssignedManagedIdentity]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.ManagedIdentitySqlControlSettingsModel(ProxyResource):
        grant_sql_control_to_managed_identity: ManagedIdentitySqlControlSettingsModelPropertiesGrantSqlControlToManagedIdentity
        id: str
        name: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                grant_sql_control_to_managed_identity: Optional[ManagedIdentitySqlControlSettingsModelPropertiesGrantSqlControlToManagedIdentity] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.ManagedIdentitySqlControlSettingsModelPropertiesGrantSqlControlToManagedIdentity(Model):
        actual_state: Union[str, ActualState]
        desired_state: Union[str, DesiredState]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                desired_state: Optional[Union[str, DesiredState]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.ManagedIntegrationRuntime(IntegrationRuntime):
        additional_properties: dict[str, JSON]
        compute_properties: IntegrationRuntimeComputeProperties
        description: str
        id: str
        reference_name: str
        ssis_properties: IntegrationRuntimeSsisProperties
        state: Union[str, IntegrationRuntimeState]
        type: Union[str, IntegrationRuntimeType]
        type_managed_virtual_network_type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                additional_properties: Optional[Dict[str, JSON]] = ..., 
                compute_properties: Optional[IntegrationRuntimeComputeProperties] = ..., 
                description: Optional[str] = ..., 
                id: Optional[str] = ..., 
                reference_name: Optional[str] = ..., 
                ssis_properties: Optional[IntegrationRuntimeSsisProperties] = ..., 
                type_managed_virtual_network_type: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.ManagedIntegrationRuntimeError(Model):
        additional_properties: dict[str, JSON]
        code: str
        message: str
        parameters: list[str]
        time: datetime

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                additional_properties: Optional[Dict[str, JSON]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.ManagedIntegrationRuntimeNode(Model):
        additional_properties: dict[str, JSON]
        errors: list[ManagedIntegrationRuntimeError]
        node_id: str
        status: Union[str, ManagedIntegrationRuntimeNodeStatus]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                additional_properties: Optional[Dict[str, JSON]] = ..., 
                errors: Optional[List[ManagedIntegrationRuntimeError]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.ManagedIntegrationRuntimeNodeStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVAILABLE = "Available"
        RECYCLING = "Recycling"
        STARTING = "Starting"
        UNAVAILABLE = "Unavailable"


    class azure.mgmt.synapse.models.ManagedIntegrationRuntimeOperationResult(Model):
        activity_id: str
        additional_properties: dict[str, JSON]
        error_code: str
        parameters: list[str]
        result: str
        start_time: datetime
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                additional_properties: Optional[Dict[str, JSON]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.ManagedIntegrationRuntimeStatus(IntegrationRuntimeStatus):
        additional_properties: dict[str, JSON]
        create_time: datetime
        data_factory_name: str
        last_operation: ManagedIntegrationRuntimeOperationResult
        nodes: list[ManagedIntegrationRuntimeNode]
        other_errors: list[ManagedIntegrationRuntimeError]
        state: Union[str, IntegrationRuntimeState]
        type: Union[str, IntegrationRuntimeType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                additional_properties: Optional[Dict[str, JSON]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.ManagedVirtualNetworkSettings(Model):
        allowed_aad_tenant_ids_for_linking: list[str]
        linked_access_check_on_target_resource: bool
        prevent_data_exfiltration: bool

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                allowed_aad_tenant_ids_for_linking: Optional[List[str]] = ..., 
                linked_access_check_on_target_resource: Optional[bool] = ..., 
                prevent_data_exfiltration: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.ManagementOperationState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELLED = "Cancelled"
        CANCEL_IN_PROGRESS = "CancelInProgress"
        FAILED = "Failed"
        IN_PROGRESS = "InProgress"
        PENDING = "Pending"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.synapse.models.MetadataSyncConfig(ProxyResource):
        enabled: bool
        id: str
        name: str
        sync_interval_in_minutes: int
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ..., 
                sync_interval_in_minutes: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.NodeSize(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LARGE = "Large"
        MEDIUM = "Medium"
        NONE = "None"
        SMALL = "Small"
        XXX_LARGE = "XXXLarge"
        XX_LARGE = "XXLarge"
        X_LARGE = "XLarge"


    class azure.mgmt.synapse.models.NodeSizeFamily(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HARDWARE_ACCELERATED_FPGA = "HardwareAcceleratedFPGA"
        HARDWARE_ACCELERATED_GPU = "HardwareAcceleratedGPU"
        MEMORY_OPTIMIZED = "MemoryOptimized"
        NONE = "None"


    class azure.mgmt.synapse.models.Operation(Model):
        display: OperationDisplay
        name: str
        origin: str
        properties: JSON

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                display: Optional[OperationDisplay] = ..., 
                name: Optional[str] = ..., 
                origin: Optional[str] = ..., 
                properties: Optional[JSON] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.OperationDisplay(Model):
        description: str
        operation: str
        provider: str
        resource: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                operation: Optional[str] = ..., 
                provider: Optional[str] = ..., 
                resource: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.OperationListResult(Model):
        next_link: str
        value: list[Operation]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[Operation]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.OperationMetaLogSpecification(Model):
        blob_duration: str
        display_name: str
        name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                blob_duration: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                name: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.OperationMetaMetricDimensionSpecification(Model):
        display_name: str
        name: str
        to_be_exported_for_shoebox: bool

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ..., 
                name: Optional[str] = ..., 
                to_be_exported_for_shoebox: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.OperationMetaMetricSpecification(Model):
        aggregation_type: str
        dimensions: list[OperationMetaMetricDimensionSpecification]
        display_description: str
        display_name: str
        enable_regional_mdm_account: bool
        metric_filter_pattern: str
        name: str
        source_mdm_account: str
        source_mdm_namespace: str
        supports_instance_level_aggregation: bool
        unit: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                aggregation_type: Optional[str] = ..., 
                dimensions: Optional[List[OperationMetaMetricDimensionSpecification]] = ..., 
                display_description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                enable_regional_mdm_account: Optional[bool] = ..., 
                metric_filter_pattern: Optional[str] = ..., 
                name: Optional[str] = ..., 
                source_mdm_account: Optional[str] = ..., 
                source_mdm_namespace: Optional[str] = ..., 
                supports_instance_level_aggregation: Optional[bool] = ..., 
                unit: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.OperationMetaServiceSpecification(Model):
        log_specifications: list[OperationMetaLogSpecification]
        metric_specifications: list[OperationMetaMetricSpecification]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                log_specifications: Optional[List[OperationMetaLogSpecification]] = ..., 
                metric_specifications: Optional[List[OperationMetaMetricSpecification]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.OperationResource(Model):
        end_time: datetime
        error: ErrorDetail
        id: str
        name: str
        percent_complete: float
        properties: JSON
        start_time: datetime
        status: Union[str, OperationStatus]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                end_time: Optional[datetime] = ..., 
                error: Optional[ErrorDetail] = ..., 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                percent_complete: Optional[float] = ..., 
                properties: Optional[JSON] = ..., 
                start_time: Optional[datetime] = ..., 
                status: Optional[Union[str, OperationStatus]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.OperationStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        FAILED = "Failed"
        IN_PROGRESS = "InProgress"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.synapse.models.OptimizedAutoscale(Model):
        is_enabled: bool
        maximum: int
        minimum: int
        version: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                is_enabled: bool, 
                maximum: int, 
                minimum: int, 
                version: int, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.PrincipalType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APP = "App"
        GROUP = "Group"
        USER = "User"


    class azure.mgmt.synapse.models.PrincipalsModificationKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        REPLACE = "Replace"
        UNION = "Union"


    class azure.mgmt.synapse.models.PrivateEndpoint(Model):
        id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.PrivateEndpointConnection(ProxyResource):
        id: str
        name: str
        private_endpoint: PrivateEndpoint
        private_link_service_connection_state: PrivateLinkServiceConnectionState
        provisioning_state: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                private_endpoint: Optional[PrivateEndpoint] = ..., 
                private_link_service_connection_state: Optional[PrivateLinkServiceConnectionState] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.PrivateEndpointConnectionForPrivateLinkHub(PrivateEndpointConnectionForPrivateLinkHubBasicAutoGenerated):
        id: str
        name: str
        properties: PrivateEndpointConnectionProperties
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                properties: Optional[PrivateEndpointConnectionProperties] = ..., 
                type: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.PrivateEndpointConnectionForPrivateLinkHubBasic(Model):
        id: str
        private_endpoint: PrivateEndpoint
        private_link_service_connection_state: PrivateLinkServiceConnectionState
        provisioning_state: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                private_endpoint: Optional[PrivateEndpoint] = ..., 
                private_link_service_connection_state: Optional[PrivateLinkServiceConnectionState] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.PrivateEndpointConnectionForPrivateLinkHubBasicAutoGenerated(Model):
        id: str
        properties: PrivateEndpointConnectionProperties

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                properties: Optional[PrivateEndpointConnectionProperties] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.PrivateEndpointConnectionForPrivateLinkHubResourceCollectionResponse(Model):
        next_link: str
        value: list[PrivateEndpointConnectionForPrivateLinkHub]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[PrivateEndpointConnectionForPrivateLinkHub]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.PrivateEndpointConnectionList(Model):
        next_link: str
        value: list[PrivateEndpointConnection]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.PrivateEndpointConnectionProperties(Model):
        private_endpoint: PrivateEndpoint
        private_link_service_connection_state: PrivateLinkServiceConnectionState
        provisioning_state: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                private_endpoint: Optional[PrivateEndpoint] = ..., 
                private_link_service_connection_state: Optional[PrivateLinkServiceConnectionState] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.PrivateLinkHub(TrackedResource):
        id: str
        location: str
        name: str
        private_endpoint_connections: list[PrivateEndpointConnectionForPrivateLinkHubBasic]
        provisioning_state: str
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                location: str, 
                provisioning_state: Optional[str] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.PrivateLinkHubInfoListResult(Model):
        next_link: str
        value: list[PrivateLinkHub]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[PrivateLinkHub]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.PrivateLinkHubPatchInfo(Model):
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.PrivateLinkResource(ProxyResource):
        id: str
        name: str
        properties: PrivateLinkResourceProperties
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.PrivateLinkResourceListResult(Model):
        next_link: str
        value: list[PrivateLinkResource]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.PrivateLinkResourceProperties(Model):
        group_id: str
        required_members: list[str]
        required_zone_names: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.PrivateLinkResources(Model):
        value: list[KustoPoolPrivateLinkResources]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[KustoPoolPrivateLinkResources]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.PrivateLinkServiceConnectionState(Model):
        actions_required: str
        description: str
        status: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                status: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DELETE_ERROR = "DeleteError"
        DELETING = "Deleting"
        FAILED = "Failed"
        PROVISIONING = "Provisioning"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.synapse.models.ProxyResource(Resource):
        id: str
        name: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.PurviewConfiguration(Model):
        purview_resource_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                purview_resource_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.QueryAggregationFunction(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVG = "avg"
        MAX = "max"
        MIN = "min"
        SUM = "sum"


    class azure.mgmt.synapse.models.QueryExecutionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ABORTED = "aborted"
        ANY = "any"
        EXCEPTION = "exception"
        IRREGULAR = "irregular"
        REGULAR = "regular"


    class azure.mgmt.synapse.models.QueryInterval(Model):
        execution_count: int
        interval_start_time: datetime
        metrics: list[QueryMetric]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.QueryMetric(Model):
        display_name: str
        name: str
        unit: Union[str, QueryMetricUnit]
        value: float

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.QueryMetricUnit(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        KB = "KB"
        MICROSECONDS = "microseconds"
        PERCENTAGE = "percentage"


    class azure.mgmt.synapse.models.QueryObservedMetricType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CPU = "cpu"
        DURATION = "duration"
        EXECUTION_COUNT = "executionCount"
        IO = "io"
        LOGIO = "logio"


    class azure.mgmt.synapse.models.QueryStatistic(Model):
        intervals: list[QueryInterval]
        query_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.ReadOnlyFollowingDatabase(Database):
        attached_database_configuration_name: str
        hot_cache_period: timedelta
        id: str
        kind: Union[str, Kind]
        leader_cluster_resource_id: str
        location: str
        name: str
        principals_modification_kind: Union[str, PrincipalsModificationKind]
        provisioning_state: Union[str, ResourceProvisioningState]
        soft_delete_period: timedelta
        statistics: DatabaseStatistics
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                hot_cache_period: Optional[timedelta] = ..., 
                location: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.ReadWriteDatabase(Database):
        hot_cache_period: timedelta
        id: str
        is_followed: bool
        kind: Union[str, Kind]
        location: str
        name: str
        provisioning_state: Union[str, ResourceProvisioningState]
        soft_delete_period: timedelta
        statistics: DatabaseStatistics
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                hot_cache_period: Optional[timedelta] = ..., 
                location: Optional[str] = ..., 
                soft_delete_period: Optional[timedelta] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.Reason(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALREADY_EXISTS = "AlreadyExists"
        INVALID = "Invalid"


    class azure.mgmt.synapse.models.RecommendedSensitivityLabelUpdate(ProxyResource):
        column: str
        id: str
        name: str
        op: Union[str, RecommendedSensitivityLabelUpdateKind]
        schema: str
        table: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                column: Optional[str] = ..., 
                op: Optional[Union[str, RecommendedSensitivityLabelUpdateKind]] = ..., 
                schema: Optional[str] = ..., 
                table: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.RecommendedSensitivityLabelUpdateKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLE = "disable"
        ENABLE = "enable"


    class azure.mgmt.synapse.models.RecommendedSensitivityLabelUpdateList(Model):
        operations: list[RecommendedSensitivityLabelUpdate]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                operations: Optional[List[RecommendedSensitivityLabelUpdate]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.RecoverableSqlPool(ProxyResource):
        edition: str
        elastic_pool_name: str
        id: str
        last_available_backup_date: datetime
        name: str
        service_level_objective: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.RecoverableSqlPoolListResult(Model):
        next_link: str
        value: list[RecoverableSqlPool]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.ReplaceAllFirewallRulesOperationResponse(Model):
        operation_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                operation_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.ReplaceAllIpFirewallRulesRequest(Model):
        ip_firewall_rules: dict[str, IpFirewallRuleProperties]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                ip_firewall_rules: Optional[Dict[str, IpFirewallRuleProperties]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.ReplicationLink(ProxyResource):
        id: str
        is_termination_allowed: bool
        location: str
        name: str
        partner_database: str
        partner_location: str
        partner_role: Union[str, ReplicationRole]
        partner_server: str
        percent_complete: int
        replication_mode: str
        replication_state: Union[str, ReplicationState]
        role: Union[str, ReplicationRole]
        start_time: datetime
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.ReplicationLinkListResult(Model):
        next_link: str
        value: list[ReplicationLink]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[ReplicationLink]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.ReplicationRole(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COPY = "Copy"
        NON_READABLE_SECONDARY = "NonReadableSecondary"
        PRIMARY = "Primary"
        SECONDARY = "Secondary"
        SOURCE = "Source"


    class azure.mgmt.synapse.models.ReplicationState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CATCH_UP = "CATCH_UP"
        PENDING = "PENDING"
        SEEDING = "SEEDING"
        SUSPENDED = "SUSPENDED"


    class azure.mgmt.synapse.models.Resource(Model):
        id: str
        name: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.ResourceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        SYSTEM_ASSIGNED_USER_ASSIGNED = "SystemAssigned,UserAssigned"


    class azure.mgmt.synapse.models.ResourceMoveDefinition(Model):
        id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                id: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.ResourceProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        MOVING = "Moving"
        RUNNING = "Running"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.synapse.models.RestorableDroppedSqlPool(ProxyResource):
        creation_date: datetime
        database_name: str
        deletion_date: datetime
        earliest_restore_date: datetime
        edition: str
        elastic_pool_name: str
        id: str
        location: str
        max_size_bytes: str
        name: str
        service_level_objective: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.RestorableDroppedSqlPoolListResult(Model):
        value: list[RestorableDroppedSqlPool]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: List[RestorableDroppedSqlPool], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.RestorePoint(ProxyResource):
        earliest_restore_date: datetime
        id: str
        location: str
        name: str
        restore_point_creation_date: datetime
        restore_point_label: str
        restore_point_type: Union[str, RestorePointType]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.RestorePointListResult(Model):
        next_link: str
        value: list[RestorePoint]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.RestorePointType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONTINUOUS = "CONTINUOUS"
        DISCRETE = "DISCRETE"


    class azure.mgmt.synapse.models.SecretBase(Model):
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.SecureString(SecretBase):
        type: str
        value: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.SecurityAlertPolicyName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEFAULT = "default"


    class azure.mgmt.synapse.models.SecurityAlertPolicyNameAutoGenerated(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEFAULT = "Default"


    class azure.mgmt.synapse.models.SecurityAlertPolicyState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"
        NEW = "New"


    class azure.mgmt.synapse.models.SelfHostedIntegrationRuntime(IntegrationRuntime):
        additional_properties: dict[str, JSON]
        description: str
        linked_info: LinkedIntegrationRuntimeType
        type: Union[str, IntegrationRuntimeType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                additional_properties: Optional[Dict[str, JSON]] = ..., 
                description: Optional[str] = ..., 
                linked_info: Optional[LinkedIntegrationRuntimeType] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.SelfHostedIntegrationRuntimeNode(Model):
        additional_properties: dict[str, JSON]
        capabilities: dict[str, str]
        concurrent_jobs_limit: int
        expiry_time: datetime
        host_service_uri: str
        is_active_dispatcher: bool
        last_connect_time: datetime
        last_end_update_time: datetime
        last_start_time: datetime
        last_start_update_time: datetime
        last_stop_time: datetime
        last_update_result: Union[str, IntegrationRuntimeUpdateResult]
        machine_name: str
        max_concurrent_jobs: int
        node_name: str
        register_time: datetime
        status: Union[str, SelfHostedIntegrationRuntimeNodeStatus]
        version: str
        version_status: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                additional_properties: Optional[Dict[str, JSON]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.SelfHostedIntegrationRuntimeNodeStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INITIALIZE_FAILED = "InitializeFailed"
        INITIALIZING = "Initializing"
        LIMITED = "Limited"
        NEED_REGISTRATION = "NeedRegistration"
        OFFLINE = "Offline"
        ONLINE = "Online"
        UPGRADING = "Upgrading"


    class azure.mgmt.synapse.models.SelfHostedIntegrationRuntimeStatus(IntegrationRuntimeStatus):
        additional_properties: dict[str, JSON]
        auto_update: Union[str, IntegrationRuntimeAutoUpdate]
        auto_update_eta: datetime
        capabilities: dict[str, str]
        create_time: datetime
        data_factory_name: str
        internal_channel_encryption: Union[str, IntegrationRuntimeInternalChannelEncryptionMode]
        latest_version: str
        links: list[LinkedIntegrationRuntime]
        local_time_zone_offset: str
        newer_versions: list[str]
        node_communication_channel_encryption_mode: str
        nodes: list[SelfHostedIntegrationRuntimeNode]
        pushed_version: str
        scheduled_update_date: datetime
        service_region: str
        service_urls: list[str]
        state: Union[str, IntegrationRuntimeState]
        task_queue_id: str
        type: Union[str, IntegrationRuntimeType]
        update_delay_offset: str
        version: str
        version_status: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                additional_properties: Optional[Dict[str, JSON]] = ..., 
                links: Optional[List[LinkedIntegrationRuntime]] = ..., 
                newer_versions: Optional[List[str]] = ..., 
                nodes: Optional[List[SelfHostedIntegrationRuntimeNode]] = ..., 
                service_region: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.SensitivityLabel(ProxyResource):
        column_name: str
        id: str
        information_type: str
        information_type_id: str
        is_disabled: bool
        label_id: str
        label_name: str
        managed_by: str
        name: str
        rank: Union[str, SensitivityLabelRank]
        schema_name: str
        table_name: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                information_type: Optional[str] = ..., 
                information_type_id: Optional[str] = ..., 
                label_id: Optional[str] = ..., 
                label_name: Optional[str] = ..., 
                rank: Optional[Union[str, SensitivityLabelRank]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.SensitivityLabelListResult(Model):
        next_link: str
        value: list[SensitivityLabel]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.SensitivityLabelRank(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CRITICAL = "Critical"
        HIGH = "High"
        LOW = "Low"
        MEDIUM = "Medium"
        NONE = "None"


    class azure.mgmt.synapse.models.SensitivityLabelSource(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CURRENT = "current"
        RECOMMENDED = "recommended"


    class azure.mgmt.synapse.models.SensitivityLabelUpdate(ProxyResource):
        column: str
        id: str
        name: str
        op: Union[str, SensitivityLabelUpdateKind]
        schema: str
        sensitivity_label: SensitivityLabel
        table: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                column: Optional[str] = ..., 
                op: Optional[Union[str, SensitivityLabelUpdateKind]] = ..., 
                schema: Optional[str] = ..., 
                sensitivity_label: Optional[SensitivityLabel] = ..., 
                table: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.SensitivityLabelUpdateKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        REMOVE = "remove"
        SET = "set"


    class azure.mgmt.synapse.models.SensitivityLabelUpdateList(Model):
        operations: list[SensitivityLabelUpdate]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                operations: Optional[List[SensitivityLabelUpdate]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.ServerBlobAuditingPolicy(ProxyResource):
        audit_actions_and_groups: list[str]
        id: str
        is_azure_monitor_target_enabled: bool
        is_devops_audit_enabled: bool
        is_storage_secondary_key_in_use: bool
        name: str
        queue_delay_ms: int
        retention_days: int
        state: Union[str, BlobAuditingPolicyState]
        storage_account_access_key: str
        storage_account_subscription_id: str
        storage_endpoint: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                audit_actions_and_groups: Optional[List[str]] = ..., 
                is_azure_monitor_target_enabled: Optional[bool] = ..., 
                is_devops_audit_enabled: Optional[bool] = ..., 
                is_storage_secondary_key_in_use: Optional[bool] = ..., 
                queue_delay_ms: Optional[int] = ..., 
                retention_days: Optional[int] = ..., 
                state: Optional[Union[str, BlobAuditingPolicyState]] = ..., 
                storage_account_access_key: Optional[str] = ..., 
                storage_account_subscription_id: Optional[str] = ..., 
                storage_endpoint: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.ServerBlobAuditingPolicyListResult(Model):
        next_link: str
        value: list[ServerBlobAuditingPolicy]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.ServerKeyType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_KEY_VAULT = "AzureKeyVault"
        SERVICE_MANAGED = "ServiceManaged"


    class azure.mgmt.synapse.models.ServerSecurityAlertPolicy(ProxyResource):
        creation_time: datetime
        disabled_alerts: list[str]
        email_account_admins: bool
        email_addresses: list[str]
        id: str
        name: str
        retention_days: int
        state: Union[str, SecurityAlertPolicyState]
        storage_account_access_key: str
        storage_endpoint: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                disabled_alerts: Optional[List[str]] = ..., 
                email_account_admins: Optional[bool] = ..., 
                email_addresses: Optional[List[str]] = ..., 
                retention_days: Optional[int] = ..., 
                state: Optional[Union[str, SecurityAlertPolicyState]] = ..., 
                storage_account_access_key: Optional[str] = ..., 
                storage_endpoint: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.ServerSecurityAlertPolicyListResult(Model):
        next_link: str
        value: list[ServerSecurityAlertPolicy]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.ServerUsage(Model):
        current_value: float
        display_name: str
        limit: float
        name: str
        next_reset_time: datetime
        resource_name: str
        unit: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.ServerUsageListResult(Model):
        next_link: str
        value: list[ServerUsage]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: List[ServerUsage], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.ServerVulnerabilityAssessment(ProxyResource):
        id: str
        name: str
        recurring_scans: VulnerabilityAssessmentRecurringScansProperties
        storage_account_access_key: str
        storage_container_path: str
        storage_container_sas_key: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                recurring_scans: Optional[VulnerabilityAssessmentRecurringScansProperties] = ..., 
                storage_account_access_key: Optional[str] = ..., 
                storage_container_path: Optional[str] = ..., 
                storage_container_sas_key: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.ServerVulnerabilityAssessmentListResult(Model):
        next_link: str
        value: list[ServerVulnerabilityAssessment]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.Sku(Model):
        capacity: int
        name: str
        tier: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                capacity: Optional[int] = ..., 
                name: Optional[str] = ..., 
                tier: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.SkuDescription(Model):
        location_info: list[SkuLocationInfoItem]
        locations: list[str]
        name: str
        resource_type: str
        restrictions: list[JSON]
        size: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.SkuDescriptionList(Model):
        value: list[SkuDescription]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.SkuLocationInfoItem(Model):
        location: str
        zones: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                location: str, 
                zones: Optional[List[str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.SkuName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPUTE_OPTIMIZED = "Compute optimized"
        STORAGE_OPTIMIZED = "Storage optimized"


    class azure.mgmt.synapse.models.SkuSize(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EXTRA_SMALL = "Extra small"
        LARGE = "Large"
        MEDIUM = "Medium"
        SMALL = "Small"


    class azure.mgmt.synapse.models.SparkConfigProperties(Model):
        configuration_type: Union[str, ConfigurationType]
        content: str
        filename: str
        time: datetime

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                configuration_type: Optional[Union[str, ConfigurationType]] = ..., 
                content: Optional[str] = ..., 
                filename: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.SparkConfigurationListResponse(Model):
        next_link: str
        value: list[SparkConfigurationResource]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: List[SparkConfigurationResource], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.SparkConfigurationResource(SubResource):
        annotations: list[str]
        config_merge_rule: dict[str, str]
        configs: dict[str, str]
        created: datetime
        created_by: str
        description: str
        etag: str
        id: str
        name: str
        notes: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                annotations: Optional[List[str]] = ..., 
                config_merge_rule: Optional[Dict[str, str]] = ..., 
                configs: Dict[str, str], 
                created: Optional[datetime] = ..., 
                created_by: Optional[str] = ..., 
                description: Optional[str] = ..., 
                notes: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.SqlPool(TrackedResource):
        collation: str
        create_mode: Union[str, CreateMode]
        creation_date: datetime
        id: str
        location: str
        max_size_bytes: int
        name: str
        provisioning_state: str
        recoverable_database_id: str
        restore_point_in_time: datetime
        sku: Sku
        source_database_deletion_date: datetime
        source_database_id: str
        status: str
        storage_account_type: Union[str, StorageAccountType]
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                collation: str = "", 
                create_mode: Optional[Union[str, CreateMode]] = ..., 
                location: str, 
                max_size_bytes: Optional[int] = ..., 
                provisioning_state: Optional[str] = ..., 
                recoverable_database_id: Optional[str] = ..., 
                restore_point_in_time: Optional[datetime] = ..., 
                sku: Optional[Sku] = ..., 
                source_database_deletion_date: Optional[datetime] = ..., 
                source_database_id: Optional[str] = ..., 
                storage_account_type: Union[str, StorageAccountType] = "GRS", 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.SqlPoolBlobAuditingPolicy(ProxyResource):
        audit_actions_and_groups: list[str]
        id: str
        is_azure_monitor_target_enabled: bool
        is_storage_secondary_key_in_use: bool
        kind: str
        name: str
        retention_days: int
        state: Union[str, BlobAuditingPolicyState]
        storage_account_access_key: str
        storage_account_subscription_id: str
        storage_endpoint: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                audit_actions_and_groups: Optional[List[str]] = ..., 
                is_azure_monitor_target_enabled: bool = False, 
                is_storage_secondary_key_in_use: Optional[bool] = ..., 
                retention_days: Optional[int] = ..., 
                state: Optional[Union[str, BlobAuditingPolicyState]] = ..., 
                storage_account_access_key: Optional[str] = ..., 
                storage_account_subscription_id: Optional[str] = ..., 
                storage_endpoint: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.SqlPoolBlobAuditingPolicyListResult(Model):
        next_link: str
        value: list[SqlPoolBlobAuditingPolicy]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.SqlPoolBlobAuditingPolicySqlPoolOperationListResult(Model):
        next_link: str
        value: list[SqlPoolOperation]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.SqlPoolColumn(ProxyResource):
        column_type: Union[str, ColumnDataType]
        id: str
        is_computed: bool
        name: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                column_type: Optional[Union[str, ColumnDataType]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.SqlPoolColumnListResult(Model):
        next_link: str
        value: list[SqlPoolColumn]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.SqlPoolConnectionPolicy(ProxyResource):
        id: str
        kind: str
        location: str
        name: str
        proxy_dns_name: str
        proxy_port: str
        redirection_state: str
        security_enabled_access: str
        state: str
        type: str
        use_server_default: str
        visibility: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                proxy_dns_name: Optional[str] = ..., 
                proxy_port: Optional[str] = ..., 
                redirection_state: Optional[str] = ..., 
                security_enabled_access: Optional[str] = ..., 
                state: Optional[str] = ..., 
                use_server_default: Optional[str] = ..., 
                visibility: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.SqlPoolInfoListResult(Model):
        next_link: str
        value: list[SqlPool]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[SqlPool]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.SqlPoolOperation(ProxyResource):
        database_name: str
        description: str
        error_code: int
        error_description: str
        error_severity: int
        estimated_completion_time: datetime
        id: str
        is_cancellable: bool
        is_user_error: bool
        name: str
        operation: str
        operation_friendly_name: str
        percent_complete: int
        server_name: str
        start_time: datetime
        state: Union[str, ManagementOperationState]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.SqlPoolPatchInfo(Model):
        collation: str
        create_mode: Union[str, CreateMode]
        creation_date: datetime
        location: str
        max_size_bytes: int
        provisioning_state: str
        recoverable_database_id: str
        restore_point_in_time: datetime
        sku: Sku
        source_database_deletion_date: datetime
        source_database_id: str
        status: str
        storage_account_type: Union[str, StorageAccountType]
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                collation: str = "", 
                create_mode: Optional[Union[str, CreateMode]] = ..., 
                location: Optional[str] = ..., 
                max_size_bytes: Optional[int] = ..., 
                provisioning_state: Optional[str] = ..., 
                recoverable_database_id: Optional[str] = ..., 
                restore_point_in_time: Optional[datetime] = ..., 
                sku: Optional[Sku] = ..., 
                source_database_deletion_date: Optional[datetime] = ..., 
                source_database_id: Optional[str] = ..., 
                storage_account_type: Union[str, StorageAccountType] = "GRS", 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.SqlPoolSchema(ProxyResource):
        id: str
        name: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.SqlPoolSchemaListResult(Model):
        next_link: str
        value: list[SqlPoolSchema]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.SqlPoolSecurityAlertPolicy(ProxyResource):
        creation_time: datetime
        disabled_alerts: list[str]
        email_account_admins: bool
        email_addresses: list[str]
        id: str
        name: str
        retention_days: int
        state: Union[str, SecurityAlertPolicyState]
        storage_account_access_key: str
        storage_endpoint: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                disabled_alerts: Optional[List[str]] = ..., 
                email_account_admins: Optional[bool] = ..., 
                email_addresses: Optional[List[str]] = ..., 
                retention_days: Optional[int] = ..., 
                state: Optional[Union[str, SecurityAlertPolicyState]] = ..., 
                storage_account_access_key: Optional[str] = ..., 
                storage_endpoint: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.SqlPoolTable(ProxyResource):
        id: str
        name: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.SqlPoolTableListResult(Model):
        next_link: str
        value: list[SqlPoolTable]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.SqlPoolUsage(Model):
        current_value: float
        display_name: str
        limit: float
        name: str
        next_reset_time: datetime
        resource_name: str
        unit: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.SqlPoolUsageListResult(Model):
        next_link: str
        value: list[SqlPoolUsage]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: List[SqlPoolUsage], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.SqlPoolVulnerabilityAssessment(ProxyResource):
        id: str
        name: str
        recurring_scans: VulnerabilityAssessmentRecurringScansProperties
        storage_account_access_key: str
        storage_container_path: str
        storage_container_sas_key: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                recurring_scans: Optional[VulnerabilityAssessmentRecurringScansProperties] = ..., 
                storage_account_access_key: Optional[str] = ..., 
                storage_container_path: Optional[str] = ..., 
                storage_container_sas_key: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.SqlPoolVulnerabilityAssessmentListResult(Model):
        next_link: str
        value: list[SqlPoolVulnerabilityAssessment]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.SqlPoolVulnerabilityAssessmentRuleBaseline(ProxyResource):
        baseline_results: list[SqlPoolVulnerabilityAssessmentRuleBaselineItem]
        id: str
        name: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                baseline_results: Optional[List[SqlPoolVulnerabilityAssessmentRuleBaselineItem]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.SqlPoolVulnerabilityAssessmentRuleBaselineItem(Model):
        result: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                result: List[str], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.SqlPoolVulnerabilityAssessmentScansExport(ProxyResource):
        exported_report_location: str
        id: str
        name: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.SsisEnvironment(SsisObjectMetadata):
        description: str
        folder_id: int
        id: int
        name: str
        type: Union[str, SsisObjectMetadataType]
        variables: list[SsisVariable]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                folder_id: Optional[int] = ..., 
                id: Optional[int] = ..., 
                name: Optional[str] = ..., 
                variables: Optional[List[SsisVariable]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.SsisEnvironmentReference(Model):
        environment_folder_name: str
        environment_name: str
        id: int
        reference_type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                environment_folder_name: Optional[str] = ..., 
                environment_name: Optional[str] = ..., 
                id: Optional[int] = ..., 
                reference_type: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.SsisFolder(SsisObjectMetadata):
        description: str
        id: int
        name: str
        type: Union[str, SsisObjectMetadataType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                id: Optional[int] = ..., 
                name: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.SsisObjectMetadata(Model):
        description: str
        id: int
        name: str
        type: Union[str, SsisObjectMetadataType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                id: Optional[int] = ..., 
                name: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.SsisObjectMetadataListResponse(Model):
        next_link: str
        value: list[SsisObjectMetadata]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[SsisObjectMetadata]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.SsisObjectMetadataStatusResponse(Model):
        error: str
        name: str
        properties: str
        status: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                error: Optional[str] = ..., 
                name: Optional[str] = ..., 
                properties: Optional[str] = ..., 
                status: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.SsisObjectMetadataType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ENVIRONMENT = "Environment"
        FOLDER = "Folder"
        PACKAGE = "Package"
        PROJECT = "Project"


    class azure.mgmt.synapse.models.SsisPackage(SsisObjectMetadata):
        description: str
        folder_id: int
        id: int
        name: str
        parameters: list[SsisParameter]
        project_id: int
        project_version: int
        type: Union[str, SsisObjectMetadataType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                folder_id: Optional[int] = ..., 
                id: Optional[int] = ..., 
                name: Optional[str] = ..., 
                parameters: Optional[List[SsisParameter]] = ..., 
                project_id: Optional[int] = ..., 
                project_version: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.SsisParameter(Model):
        data_type: str
        default_value: str
        description: str
        design_default_value: str
        id: int
        name: str
        required: bool
        sensitive: bool
        sensitive_default_value: str
        value_set: bool
        value_type: str
        variable: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                data_type: Optional[str] = ..., 
                default_value: Optional[str] = ..., 
                description: Optional[str] = ..., 
                design_default_value: Optional[str] = ..., 
                id: Optional[int] = ..., 
                name: Optional[str] = ..., 
                required: Optional[bool] = ..., 
                sensitive: Optional[bool] = ..., 
                sensitive_default_value: Optional[str] = ..., 
                value_set: Optional[bool] = ..., 
                value_type: Optional[str] = ..., 
                variable: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.SsisProject(SsisObjectMetadata):
        description: str
        environment_refs: list[SsisEnvironmentReference]
        folder_id: int
        id: int
        name: str
        parameters: list[SsisParameter]
        type: Union[str, SsisObjectMetadataType]
        version: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                environment_refs: Optional[List[SsisEnvironmentReference]] = ..., 
                folder_id: Optional[int] = ..., 
                id: Optional[int] = ..., 
                name: Optional[str] = ..., 
                parameters: Optional[List[SsisParameter]] = ..., 
                version: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.SsisVariable(Model):
        data_type: str
        description: str
        id: int
        name: str
        sensitive: bool
        sensitive_value: str
        value: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                data_type: Optional[str] = ..., 
                description: Optional[str] = ..., 
                id: Optional[int] = ..., 
                name: Optional[str] = ..., 
                sensitive: Optional[bool] = ..., 
                sensitive_value: Optional[str] = ..., 
                value: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.State(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREATING = "Creating"
        DELETED = "Deleted"
        DELETING = "Deleting"
        RUNNING = "Running"
        STARTING = "Starting"
        STOPPED = "Stopped"
        STOPPING = "Stopping"
        UNAVAILABLE = "Unavailable"
        UPDATING = "Updating"


    class azure.mgmt.synapse.models.StateValue(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONSISTENT = "Consistent"
        IN_CONSISTENT = "InConsistent"
        UPDATING = "Updating"


    class azure.mgmt.synapse.models.StorageAccountType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        GRS = "GRS"
        LRS = "LRS"


    class azure.mgmt.synapse.models.SubResource(AzureEntityResource):
        etag: str
        id: str
        name: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.SystemData(Model):
        created_at: datetime
        created_by: str
        created_by_type: Union[str, CreatedByType]
        last_modified_at: datetime
        last_modified_by: str
        last_modified_by_type: Union[str, CreatedByType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                created_at: Optional[datetime] = ..., 
                created_by: Optional[str] = ..., 
                created_by_type: Optional[Union[str, CreatedByType]] = ..., 
                last_modified_at: Optional[datetime] = ..., 
                last_modified_by: Optional[str] = ..., 
                last_modified_by_type: Optional[Union[str, CreatedByType]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.TableLevelSharingProperties(Model):
        external_tables_to_exclude: list[str]
        external_tables_to_include: list[str]
        materialized_views_to_exclude: list[str]
        materialized_views_to_include: list[str]
        tables_to_exclude: list[str]
        tables_to_include: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                external_tables_to_exclude: Optional[List[str]] = ..., 
                external_tables_to_include: Optional[List[str]] = ..., 
                materialized_views_to_exclude: Optional[List[str]] = ..., 
                materialized_views_to_include: Optional[List[str]] = ..., 
                tables_to_exclude: Optional[List[str]] = ..., 
                tables_to_include: Optional[List[str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.TopQueries(Model):
        aggregation_function: Union[str, QueryAggregationFunction]
        execution_type: Union[str, QueryExecutionType]
        interval_type: str
        number_of_top_queries: int
        observation_end_time: datetime
        observation_start_time: datetime
        observed_metric: Union[str, QueryObservedMetricType]
        queries: list[QueryStatistic]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.TopQueriesListResult(Model):
        value: list[TopQueries]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: List[TopQueries], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.TrackedResource(Resource):
        id: str
        location: str
        name: str
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                location: str, 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.TransparentDataEncryption(ProxyResource):
        id: str
        location: str
        name: str
        status: Union[str, TransparentDataEncryptionStatus]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                status: Optional[Union[str, TransparentDataEncryptionStatus]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.TransparentDataEncryptionListResult(Model):
        next_link: str
        value: list[TransparentDataEncryption]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.TransparentDataEncryptionName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CURRENT = "current"


    class azure.mgmt.synapse.models.TransparentDataEncryptionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.synapse.models.Type(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MICROSOFT_SYNAPSE_WORKSPACES_KUSTO_POOLS_ATTACHED_DATABASE_CONFIGURATIONS = "Microsoft.Synapse/workspaces/kustoPools/attachedDatabaseConfigurations"
        MICROSOFT_SYNAPSE_WORKSPACES_KUSTO_POOLS_DATABASES = "Microsoft.Synapse/workspaces/kustoPools/databases"


    class azure.mgmt.synapse.models.UpdateIntegrationRuntimeNodeRequest(Model):
        concurrent_jobs_limit: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                concurrent_jobs_limit: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.UpdateIntegrationRuntimeRequest(Model):
        auto_update: Union[str, IntegrationRuntimeAutoUpdate]
        update_delay_offset: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                auto_update: Optional[Union[str, IntegrationRuntimeAutoUpdate]] = ..., 
                update_delay_offset: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.UserAssignedManagedIdentity(Model):
        client_id: str
        principal_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.VirtualNetworkProfile(Model):
        compute_subnet_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                compute_subnet_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.VulnerabilityAssessmentName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEFAULT = "default"


    class azure.mgmt.synapse.models.VulnerabilityAssessmentPolicyBaselineName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEFAULT = "default"
        MASTER = "master"


    class azure.mgmt.synapse.models.VulnerabilityAssessmentRecurringScansProperties(Model):
        email_subscription_admins: bool
        emails: list[str]
        is_enabled: bool

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                email_subscription_admins: bool = True, 
                emails: Optional[List[str]] = ..., 
                is_enabled: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.VulnerabilityAssessmentScanError(Model):
        code: str
        message: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.VulnerabilityAssessmentScanRecord(ProxyResource):
        end_time: datetime
        errors: list[VulnerabilityAssessmentScanError]
        id: str
        name: str
        number_of_failed_security_checks: int
        scan_id: str
        start_time: datetime
        state: Union[str, VulnerabilityAssessmentScanState]
        storage_container_path: str
        trigger_type: Union[str, VulnerabilityAssessmentScanTriggerType]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.VulnerabilityAssessmentScanRecordListResult(Model):
        next_link: str
        value: list[VulnerabilityAssessmentScanRecord]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.VulnerabilityAssessmentScanState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAILED = "Failed"
        FAILED_TO_RUN = "FailedToRun"
        IN_PROGRESS = "InProgress"
        PASSED = "Passed"


    class azure.mgmt.synapse.models.VulnerabilityAssessmentScanTriggerType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ON_DEMAND = "OnDemand"
        RECURRING = "Recurring"


    class azure.mgmt.synapse.models.WorkloadClassifier(ProxyResource):
        context: str
        end_time: str
        id: str
        importance: str
        label: str
        member_name: str
        name: str
        start_time: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                context: Optional[str] = ..., 
                end_time: Optional[str] = ..., 
                importance: Optional[str] = ..., 
                label: Optional[str] = ..., 
                member_name: Optional[str] = ..., 
                start_time: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.WorkloadClassifierListResult(Model):
        next_link: str
        value: list[WorkloadClassifier]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.WorkloadGroup(ProxyResource):
        id: str
        importance: str
        max_resource_percent: int
        max_resource_percent_per_request: float
        min_resource_percent: int
        min_resource_percent_per_request: float
        name: str
        query_execution_timeout: int
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                importance: Optional[str] = ..., 
                max_resource_percent: Optional[int] = ..., 
                max_resource_percent_per_request: Optional[float] = ..., 
                min_resource_percent: Optional[int] = ..., 
                min_resource_percent_per_request: Optional[float] = ..., 
                query_execution_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.WorkloadGroupListResult(Model):
        next_link: str
        value: list[WorkloadGroup]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.Workspace(TrackedResource):
        adla_resource_id: str
        azure_ad_only_authentication: bool
        connectivity_endpoints: dict[str, str]
        csp_workspace_admin_properties: CspWorkspaceAdminProperties
        default_data_lake_storage: DataLakeStorageAccountDetails
        encryption: EncryptionDetails
        extra_properties: dict[str, JSON]
        id: str
        identity: ManagedIdentity
        location: str
        managed_resource_group_name: str
        managed_virtual_network: str
        managed_virtual_network_settings: ManagedVirtualNetworkSettings
        name: str
        private_endpoint_connections: list[PrivateEndpointConnection]
        provisioning_state: str
        public_network_access: Union[str, WorkspacePublicNetworkAccess]
        purview_configuration: PurviewConfiguration
        settings: dict[str, JSON]
        sql_administrator_login: str
        sql_administrator_login_password: str
        tags: dict[str, str]
        trusted_service_bypass_enabled: bool
        type: str
        virtual_network_profile: VirtualNetworkProfile
        workspace_repository_configuration: WorkspaceRepositoryConfiguration
        workspace_uid: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                azure_ad_only_authentication: Optional[bool] = ..., 
                connectivity_endpoints: Optional[Dict[str, str]] = ..., 
                csp_workspace_admin_properties: Optional[CspWorkspaceAdminProperties] = ..., 
                default_data_lake_storage: Optional[DataLakeStorageAccountDetails] = ..., 
                encryption: Optional[EncryptionDetails] = ..., 
                identity: Optional[ManagedIdentity] = ..., 
                location: str, 
                managed_resource_group_name: Optional[str] = ..., 
                managed_virtual_network: Optional[str] = ..., 
                managed_virtual_network_settings: Optional[ManagedVirtualNetworkSettings] = ..., 
                private_endpoint_connections: Optional[List[PrivateEndpointConnection]] = ..., 
                public_network_access: Optional[Union[str, WorkspacePublicNetworkAccess]] = ..., 
                purview_configuration: Optional[PurviewConfiguration] = ..., 
                sql_administrator_login: Optional[str] = ..., 
                sql_administrator_login_password: Optional[str] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                trusted_service_bypass_enabled: bool = False, 
                virtual_network_profile: Optional[VirtualNetworkProfile] = ..., 
                workspace_repository_configuration: Optional[WorkspaceRepositoryConfiguration] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.WorkspaceAadAdminInfo(ProxyResource):
        administrator_type: str
        id: str
        login: str
        name: str
        sid: str
        tenant_id: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                administrator_type: Optional[str] = ..., 
                login: Optional[str] = ..., 
                sid: Optional[str] = ..., 
                tenant_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.WorkspaceInfoListResult(Model):
        next_link: str
        value: list[Workspace]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[Workspace]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.WorkspaceKeyDetails(Model):
        key_vault_url: str
        name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                key_vault_url: Optional[str] = ..., 
                name: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.WorkspacePatchInfo(Model):
        encryption: EncryptionDetails
        identity: ManagedIdentity
        managed_virtual_network_settings: ManagedVirtualNetworkSettings
        provisioning_state: str
        public_network_access: Union[str, WorkspacePublicNetworkAccess]
        purview_configuration: PurviewConfiguration
        sql_administrator_login_password: str
        tags: dict[str, str]
        workspace_repository_configuration: WorkspaceRepositoryConfiguration

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                encryption: Optional[EncryptionDetails] = ..., 
                identity: Optional[ManagedIdentity] = ..., 
                managed_virtual_network_settings: Optional[ManagedVirtualNetworkSettings] = ..., 
                public_network_access: Optional[Union[str, WorkspacePublicNetworkAccess]] = ..., 
                purview_configuration: Optional[PurviewConfiguration] = ..., 
                sql_administrator_login_password: Optional[str] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                workspace_repository_configuration: Optional[WorkspaceRepositoryConfiguration] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.WorkspacePublicNetworkAccess(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.synapse.models.WorkspaceRepositoryConfiguration(Model):
        account_name: str
        collaboration_branch: str
        host_name: str
        last_commit_id: str
        project_name: str
        repository_name: str
        root_folder: str
        tenant_id: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                account_name: Optional[str] = ..., 
                collaboration_branch: Optional[str] = ..., 
                host_name: Optional[str] = ..., 
                last_commit_id: Optional[str] = ..., 
                project_name: Optional[str] = ..., 
                repository_name: Optional[str] = ..., 
                root_folder: Optional[str] = ..., 
                tenant_id: Optional[str] = ..., 
                type: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.synapse.models.WorkspaceStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAILED = "Failed"
        IN_PROGRESS = "InProgress"
        SUCCEEDED = "Succeeded"


namespace azure.mgmt.synapse.operations

    class azure.mgmt.synapse.operations.AzureADOnlyAuthenticationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                azure_ad_only_authentication_name: Union[str, AzureADOnlyAuthenticationName], 
                azure_ad_only_authentication_info: AzureADOnlyAuthentication, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AzureADOnlyAuthentication]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                azure_ad_only_authentication_name: Union[str, AzureADOnlyAuthenticationName], 
                azure_ad_only_authentication_info: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AzureADOnlyAuthentication]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                azure_ad_only_authentication_name: Union[str, AzureADOnlyAuthenticationName], 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AzureADOnlyAuthentication: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[AzureADOnlyAuthentication]: ...


    class azure.mgmt.synapse.operations.BigDataPoolsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                big_data_pool_name: str, 
                big_data_pool_info: BigDataPoolResourceInfo, 
                force: bool = False, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BigDataPoolResourceInfo]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                big_data_pool_name: str, 
                big_data_pool_info: IO, 
                force: bool = False, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BigDataPoolResourceInfo]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                big_data_pool_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[BigDataPoolResourceInfo]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                big_data_pool_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> BigDataPoolResourceInfo: ...

        @distributed_trace
        def list_by_workspace(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[BigDataPoolResourceInfo]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                big_data_pool_name: str, 
                big_data_pool_patch_info: BigDataPoolPatchInfo, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BigDataPoolResourceInfo: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                big_data_pool_name: str, 
                big_data_pool_patch_info: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BigDataPoolResourceInfo: ...


    class azure.mgmt.synapse.operations.DataMaskingPoliciesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                parameters: DataMaskingPolicy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DataMaskingPolicy: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DataMaskingPolicy: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                data_masking_policy_name: str = ..., 
                **kwargs: Any
            ) -> DataMaskingPolicy: ...


    class azure.mgmt.synapse.operations.DataMaskingRulesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                data_masking_rule_name: str, 
                parameters: DataMaskingRule, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DataMaskingRule: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                data_masking_rule_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DataMaskingRule: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                data_masking_rule_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                data_masking_policy_name: str = ..., 
                **kwargs: Any
            ) -> DataMaskingRule: ...

        @distributed_trace
        def list_by_sql_pool(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                data_masking_policy_name: str = ..., 
                **kwargs: Any
            ) -> Iterable[DataMaskingRule]: ...


    class azure.mgmt.synapse.operations.ExtendedSqlPoolBlobAuditingPoliciesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                parameters: ExtendedSqlPoolBlobAuditingPolicy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ExtendedSqlPoolBlobAuditingPolicy: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ExtendedSqlPoolBlobAuditingPolicy: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                *, 
                blob_auditing_policy_name: str = ..., 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ExtendedSqlPoolBlobAuditingPolicy: ...

        @distributed_trace
        def list_by_sql_pool(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[ExtendedSqlPoolBlobAuditingPolicy]: ...


    class azure.mgmt.synapse.operations.GetOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def integration_runtime_enable_interactivequery(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                integration_runtime_name: str, 
                integration_runtime_operation_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> IntegrationRuntimeEnableinteractivequery: ...

        @distributed_trace
        def integration_runtime_start(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                integration_runtime_name: str, 
                integration_runtime_operation_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> IntegrationRuntimeOperationStatus: ...

        @distributed_trace
        def integration_runtime_stop(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                integration_runtime_name: str, 
                integration_runtime_operation_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> IntegrationRuntimeStopOperationStatus: ...


    class azure.mgmt.synapse.operations.IntegrationRuntimeAuthKeysOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                integration_runtime_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> IntegrationRuntimeAuthKeys: ...

        @overload
        def regenerate(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                integration_runtime_name: str, 
                regenerate_key_parameters: IntegrationRuntimeRegenerateKeyParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> IntegrationRuntimeAuthKeys: ...

        @overload
        def regenerate(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                integration_runtime_name: str, 
                regenerate_key_parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> IntegrationRuntimeAuthKeys: ...


    class azure.mgmt.synapse.operations.IntegrationRuntimeConnectionInfosOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                integration_runtime_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> IntegrationRuntimeConnectionInfo: ...


    class azure.mgmt.synapse.operations.IntegrationRuntimeCredentialsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def sync(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                integration_runtime_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.synapse.operations.IntegrationRuntimeMonitoringDataOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                integration_runtime_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> IntegrationRuntimeMonitoringData: ...


    class azure.mgmt.synapse.operations.IntegrationRuntimeNodeIpAddressOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                integration_runtime_name: str, 
                node_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> IntegrationRuntimeNodeIpAddress: ...


    class azure.mgmt.synapse.operations.IntegrationRuntimeNodesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                integration_runtime_name: str, 
                node_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                integration_runtime_name: str, 
                node_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> SelfHostedIntegrationRuntimeNode: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                integration_runtime_name: str, 
                node_name: str, 
                update_integration_runtime_node_request: UpdateIntegrationRuntimeNodeRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SelfHostedIntegrationRuntimeNode: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                integration_runtime_name: str, 
                node_name: str, 
                update_integration_runtime_node_request: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SelfHostedIntegrationRuntimeNode: ...


    class azure.mgmt.synapse.operations.IntegrationRuntimeObjectMetadataOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def begin_refresh(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                integration_runtime_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[SsisObjectMetadataStatusResponse]: ...

        @overload
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                integration_runtime_name: str, 
                get_metadata_request: Optional[GetSsisObjectMetadataRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SsisObjectMetadataListResponse: ...

        @overload
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                integration_runtime_name: str, 
                get_metadata_request: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SsisObjectMetadataListResponse: ...


    class azure.mgmt.synapse.operations.IntegrationRuntimeStatusOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                integration_runtime_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> IntegrationRuntimeStatusResponse: ...


    class azure.mgmt.synapse.operations.IntegrationRuntimesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                integration_runtime_name: str, 
                integration_runtime: IntegrationRuntimeResource, 
                if_match: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[IntegrationRuntimeResource]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                integration_runtime_name: str, 
                integration_runtime: IO, 
                if_match: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[IntegrationRuntimeResource]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                integration_runtime_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_disable_interactive_query(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                integration_runtime_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_enable_interactive_query(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                integration_runtime_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_start(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                integration_runtime_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[IntegrationRuntimeStatusResponse]: ...

        @distributed_trace
        def begin_stop(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                integration_runtime_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                integration_runtime_name: str, 
                if_none_match: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Optional[IntegrationRuntimeResource]: ...

        @distributed_trace
        def list_by_workspace(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[IntegrationRuntimeResource]: ...

        @distributed_trace
        def list_outbound_network_dependencies_endpoints(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                integration_runtime_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> IntegrationRuntimeOutboundNetworkDependenciesEndpointsResponse: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                integration_runtime_name: str, 
                update_integration_runtime_request: UpdateIntegrationRuntimeRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> IntegrationRuntimeResource: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                integration_runtime_name: str, 
                update_integration_runtime_request: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> IntegrationRuntimeResource: ...

        @distributed_trace
        def upgrade(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                integration_runtime_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.synapse.operations.IpFirewallRulesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                rule_name: str, 
                ip_firewall_rule_info: IpFirewallRuleInfo, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[IpFirewallRuleInfo]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                rule_name: str, 
                ip_firewall_rule_info: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[IpFirewallRuleInfo]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                rule_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[IpFirewallRuleInfo]: ...

        @overload
        def begin_replace_all(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                request: ReplaceAllIpFirewallRulesRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ReplaceAllFirewallRulesOperationResponse]: ...

        @overload
        def begin_replace_all(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                request: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ReplaceAllFirewallRulesOperationResponse]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                rule_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> IpFirewallRuleInfo: ...

        @distributed_trace
        def list_by_workspace(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[IpFirewallRuleInfo]: ...


    class azure.mgmt.synapse.operations.KeysOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                key_name: str, 
                key_properties: Key, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Key: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                key_name: str, 
                key_properties: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Key: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                key_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Optional[Key]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                key_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Key: ...

        @distributed_trace
        def list_by_workspace(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[Key]: ...


    class azure.mgmt.synapse.operations.KustoOperationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def list(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[Operation]: ...


    class azure.mgmt.synapse.operations.KustoPoolAttachedDatabaseConfigurationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create_or_update(
                self, 
                workspace_name: str, 
                kusto_pool_name: str, 
                attached_database_configuration_name: str, 
                resource_group_name: str, 
                parameters: AttachedDatabaseConfiguration, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AttachedDatabaseConfiguration]: ...

        @overload
        def begin_create_or_update(
                self, 
                workspace_name: str, 
                kusto_pool_name: str, 
                attached_database_configuration_name: str, 
                resource_group_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AttachedDatabaseConfiguration]: ...

        @distributed_trace
        def begin_delete(
                self, 
                workspace_name: str, 
                kusto_pool_name: str, 
                attached_database_configuration_name: str, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                workspace_name: str, 
                kusto_pool_name: str, 
                attached_database_configuration_name: str, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AttachedDatabaseConfiguration: ...

        @distributed_trace
        def list_by_kusto_pool(
                self, 
                workspace_name: str, 
                kusto_pool_name: str, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[AttachedDatabaseConfiguration]: ...


    class azure.mgmt.synapse.operations.KustoPoolChildResourceOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def check_name_availability(
                self, 
                workspace_name: str, 
                kusto_pool_name: str, 
                resource_group_name: str, 
                resource_name: DatabaseCheckNameRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameResult: ...

        @overload
        def check_name_availability(
                self, 
                workspace_name: str, 
                kusto_pool_name: str, 
                resource_group_name: str, 
                resource_name: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameResult: ...


    class azure.mgmt.synapse.operations.KustoPoolDataConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                kusto_pool_name: str, 
                database_name: str, 
                data_connection_name: str, 
                parameters: DataConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DataConnection]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                kusto_pool_name: str, 
                database_name: str, 
                data_connection_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DataConnection]: ...

        @overload
        def begin_data_connection_validation(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                kusto_pool_name: str, 
                database_name: str, 
                parameters: DataConnectionValidation, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DataConnectionValidationListResult]: ...

        @overload
        def begin_data_connection_validation(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                kusto_pool_name: str, 
                database_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DataConnectionValidationListResult]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                kusto_pool_name: str, 
                database_name: str, 
                data_connection_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                kusto_pool_name: str, 
                database_name: str, 
                data_connection_name: str, 
                parameters: DataConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DataConnection]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                kusto_pool_name: str, 
                database_name: str, 
                data_connection_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DataConnection]: ...

        @overload
        def check_name_availability(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                kusto_pool_name: str, 
                database_name: str, 
                data_connection_name: DataConnectionCheckNameRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameResult: ...

        @overload
        def check_name_availability(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                kusto_pool_name: str, 
                database_name: str, 
                data_connection_name: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameResult: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                kusto_pool_name: str, 
                database_name: str, 
                data_connection_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> DataConnection: ...

        @distributed_trace
        def list_by_database(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                kusto_pool_name: str, 
                database_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[DataConnection]: ...


    class azure.mgmt.synapse.operations.KustoPoolDatabasePrincipalAssignmentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create_or_update(
                self, 
                workspace_name: str, 
                kusto_pool_name: str, 
                database_name: str, 
                principal_assignment_name: str, 
                resource_group_name: str, 
                parameters: DatabasePrincipalAssignment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DatabasePrincipalAssignment]: ...

        @overload
        def begin_create_or_update(
                self, 
                workspace_name: str, 
                kusto_pool_name: str, 
                database_name: str, 
                principal_assignment_name: str, 
                resource_group_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DatabasePrincipalAssignment]: ...

        @distributed_trace
        def begin_delete(
                self, 
                workspace_name: str, 
                kusto_pool_name: str, 
                database_name: str, 
                principal_assignment_name: str, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def check_name_availability(
                self, 
                workspace_name: str, 
                kusto_pool_name: str, 
                database_name: str, 
                resource_group_name: str, 
                principal_assignment_name: DatabasePrincipalAssignmentCheckNameRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameResult: ...

        @overload
        def check_name_availability(
                self, 
                workspace_name: str, 
                kusto_pool_name: str, 
                database_name: str, 
                resource_group_name: str, 
                principal_assignment_name: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameResult: ...

        @distributed_trace
        def get(
                self, 
                workspace_name: str, 
                kusto_pool_name: str, 
                database_name: str, 
                principal_assignment_name: str, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> DatabasePrincipalAssignment: ...

        @distributed_trace
        def list(
                self, 
                workspace_name: str, 
                kusto_pool_name: str, 
                database_name: str, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[DatabasePrincipalAssignment]: ...


    class azure.mgmt.synapse.operations.KustoPoolDatabasesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                kusto_pool_name: str, 
                database_name: str, 
                parameters: Database, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Database]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                kusto_pool_name: str, 
                database_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Database]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                kusto_pool_name: str, 
                database_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                kusto_pool_name: str, 
                database_name: str, 
                parameters: Database, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Database]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                kusto_pool_name: str, 
                database_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Database]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                kusto_pool_name: str, 
                database_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Database: ...

        @distributed_trace
        def list_by_kusto_pool(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                kusto_pool_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[Database]: ...


    class azure.mgmt.synapse.operations.KustoPoolPrincipalAssignmentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create_or_update(
                self, 
                workspace_name: str, 
                kusto_pool_name: str, 
                principal_assignment_name: str, 
                resource_group_name: str, 
                parameters: ClusterPrincipalAssignment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ClusterPrincipalAssignment]: ...

        @overload
        def begin_create_or_update(
                self, 
                workspace_name: str, 
                kusto_pool_name: str, 
                principal_assignment_name: str, 
                resource_group_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ClusterPrincipalAssignment]: ...

        @distributed_trace
        def begin_delete(
                self, 
                workspace_name: str, 
                kusto_pool_name: str, 
                principal_assignment_name: str, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def check_name_availability(
                self, 
                workspace_name: str, 
                kusto_pool_name: str, 
                resource_group_name: str, 
                principal_assignment_name: ClusterPrincipalAssignmentCheckNameRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameResult: ...

        @overload
        def check_name_availability(
                self, 
                workspace_name: str, 
                kusto_pool_name: str, 
                resource_group_name: str, 
                principal_assignment_name: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameResult: ...

        @distributed_trace
        def get(
                self, 
                workspace_name: str, 
                kusto_pool_name: str, 
                principal_assignment_name: str, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ClusterPrincipalAssignment: ...

        @distributed_trace
        def list(
                self, 
                workspace_name: str, 
                kusto_pool_name: str, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[ClusterPrincipalAssignment]: ...


    class azure.mgmt.synapse.operations.KustoPoolPrivateLinkResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                kusto_pool_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[KustoPoolPrivateLinkResources]: ...


    class azure.mgmt.synapse.operations.KustoPoolsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_add_language_extensions(
                self, 
                workspace_name: str, 
                kusto_pool_name: str, 
                resource_group_name: str, 
                language_extensions_to_add: LanguageExtensionsList, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_add_language_extensions(
                self, 
                workspace_name: str, 
                kusto_pool_name: str, 
                resource_group_name: str, 
                language_extensions_to_add: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_create_or_update(
                self, 
                workspace_name: str, 
                resource_group_name: str, 
                kusto_pool_name: str, 
                parameters: KustoPool, 
                if_match: Optional[str] = None, 
                if_none_match: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[KustoPool]: ...

        @overload
        def begin_create_or_update(
                self, 
                workspace_name: str, 
                resource_group_name: str, 
                kusto_pool_name: str, 
                parameters: IO, 
                if_match: Optional[str] = None, 
                if_none_match: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[KustoPool]: ...

        @distributed_trace
        def begin_delete(
                self, 
                workspace_name: str, 
                resource_group_name: str, 
                kusto_pool_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_detach_follower_databases(
                self, 
                workspace_name: str, 
                kusto_pool_name: str, 
                resource_group_name: str, 
                follower_database_to_remove: FollowerDatabaseDefinition, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_detach_follower_databases(
                self, 
                workspace_name: str, 
                kusto_pool_name: str, 
                resource_group_name: str, 
                follower_database_to_remove: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_remove_language_extensions(
                self, 
                workspace_name: str, 
                kusto_pool_name: str, 
                resource_group_name: str, 
                language_extensions_to_remove: LanguageExtensionsList, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_remove_language_extensions(
                self, 
                workspace_name: str, 
                kusto_pool_name: str, 
                resource_group_name: str, 
                language_extensions_to_remove: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_start(
                self, 
                workspace_name: str, 
                kusto_pool_name: str, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_stop(
                self, 
                workspace_name: str, 
                kusto_pool_name: str, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                workspace_name: str, 
                resource_group_name: str, 
                kusto_pool_name: str, 
                parameters: KustoPoolUpdate, 
                if_match: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[KustoPool]: ...

        @overload
        def begin_update(
                self, 
                workspace_name: str, 
                resource_group_name: str, 
                kusto_pool_name: str, 
                parameters: IO, 
                if_match: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[KustoPool]: ...

        @overload
        def check_name_availability(
                self, 
                location: str, 
                kusto_pool_name: KustoPoolCheckNameRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameResult: ...

        @overload
        def check_name_availability(
                self, 
                location: str, 
                kusto_pool_name: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameResult: ...

        @distributed_trace
        def get(
                self, 
                workspace_name: str, 
                kusto_pool_name: str, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> KustoPool: ...

        @distributed_trace
        def list_by_workspace(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> KustoPoolListResult: ...

        @distributed_trace
        def list_follower_databases(
                self, 
                workspace_name: str, 
                kusto_pool_name: str, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[FollowerDatabaseDefinition]: ...

        @distributed_trace
        def list_language_extensions(
                self, 
                workspace_name: str, 
                kusto_pool_name: str, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[LanguageExtension]: ...

        @distributed_trace
        def list_skus(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[SkuDescription]: ...

        @distributed_trace
        def list_skus_by_resource(
                self, 
                workspace_name: str, 
                kusto_pool_name: str, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[AzureResourceSku]: ...


    class azure.mgmt.synapse.operations.LibrariesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def list_by_workspace(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[LibraryResource]: ...


    class azure.mgmt.synapse.operations.LibraryOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                library_name: str, 
                workspace_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> LibraryResource: ...


    class azure.mgmt.synapse.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def check_name_availability(
                self, 
                request: CheckNameAvailabilityRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResponse: ...

        @overload
        def check_name_availability(
                self, 
                request: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResponse: ...

        @distributed_trace
        def get_azure_async_header_result(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                operation_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Optional[OperationResource]: ...

        @distributed_trace
        def get_location_header_result(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                operation_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> List[AvailableRpOperation]: ...


    class azure.mgmt.synapse.operations.PrivateEndpointConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                private_endpoint_connection_name: str, 
                request: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateEndpointConnection]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                private_endpoint_connection_name: str, 
                request: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateEndpointConnection]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                private_endpoint_connection_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[OperationResource]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                private_endpoint_connection_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[PrivateEndpointConnection]: ...


    class azure.mgmt.synapse.operations.PrivateEndpointConnectionsPrivateLinkHubOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                private_link_hub_name: str, 
                private_endpoint_connection_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> PrivateEndpointConnectionForPrivateLinkHub: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                private_link_hub_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[PrivateEndpointConnectionForPrivateLinkHub]: ...


    class azure.mgmt.synapse.operations.PrivateLinkHubPrivateLinkResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                private_link_hub_name: str, 
                private_link_resource_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> PrivateLinkResource: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                private_link_hub_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[PrivateLinkResource]: ...


    class azure.mgmt.synapse.operations.PrivateLinkHubsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                private_link_hub_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                private_link_hub_name: str, 
                private_link_hub_info: PrivateLinkHub, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrivateLinkHub: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                private_link_hub_name: str, 
                private_link_hub_info: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrivateLinkHub: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                private_link_hub_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> PrivateLinkHub: ...

        @distributed_trace
        def list(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[PrivateLinkHub]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[PrivateLinkHub]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                private_link_hub_name: str, 
                private_link_hub_patch_info: PrivateLinkHubPatchInfo, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrivateLinkHub: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                private_link_hub_name: str, 
                private_link_hub_patch_info: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrivateLinkHub: ...


    class azure.mgmt.synapse.operations.PrivateLinkResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                private_link_resource_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> PrivateLinkResource: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[PrivateLinkResource]: ...


    class azure.mgmt.synapse.operations.RestorableDroppedSqlPoolsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                restorable_dropped_sql_pool_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> RestorableDroppedSqlPool: ...

        @distributed_trace
        def list_by_workspace(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[RestorableDroppedSqlPool]: ...


    class azure.mgmt.synapse.operations.SparkConfigurationOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                spark_configuration_name: str, 
                workspace_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> SparkConfigurationResource: ...


    class azure.mgmt.synapse.operations.SparkConfigurationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def list_by_workspace(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[SparkConfigurationResource]: ...


    class azure.mgmt.synapse.operations.SqlPoolBlobAuditingPoliciesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                parameters: SqlPoolBlobAuditingPolicy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SqlPoolBlobAuditingPolicy: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SqlPoolBlobAuditingPolicy: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                *, 
                blob_auditing_policy_name: str = ..., 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> SqlPoolBlobAuditingPolicy: ...

        @distributed_trace
        def list_by_sql_pool(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[SqlPoolBlobAuditingPolicy]: ...


    class azure.mgmt.synapse.operations.SqlPoolColumnsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                schema_name: str, 
                table_name: str, 
                column_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> SqlPoolColumn: ...


    class azure.mgmt.synapse.operations.SqlPoolConnectionPoliciesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                connection_policy_name: Union[str, ConnectionPolicyName], 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> SqlPoolConnectionPolicy: ...


    class azure.mgmt.synapse.operations.SqlPoolDataWarehouseUserActivitiesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                data_warehouse_user_activity_name: Union[str, DataWarehouseUserActivityName], 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> DataWarehouseUserActivities: ...


    class azure.mgmt.synapse.operations.SqlPoolGeoBackupPoliciesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                geo_backup_policy_name: Union[str, GeoBackupPolicyName], 
                parameters: GeoBackupPolicy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GeoBackupPolicy: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                geo_backup_policy_name: Union[str, GeoBackupPolicyName], 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GeoBackupPolicy: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                geo_backup_policy_name: Union[str, GeoBackupPolicyName], 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> GeoBackupPolicy: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[GeoBackupPolicy]: ...


    class azure.mgmt.synapse.operations.SqlPoolMaintenanceWindowOptionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                maintenance_window_options_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> MaintenanceWindowOptions: ...


    class azure.mgmt.synapse.operations.SqlPoolMaintenanceWindowsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                maintenance_window_name: str, 
                parameters: MaintenanceWindows, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                maintenance_window_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                maintenance_window_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> MaintenanceWindows: ...


    class azure.mgmt.synapse.operations.SqlPoolMetadataSyncConfigsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                metadata_sync_configuration: MetadataSyncConfig, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MetadataSyncConfig: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                metadata_sync_configuration: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MetadataSyncConfig: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> MetadataSyncConfig: ...


    class azure.mgmt.synapse.operations.SqlPoolOperationResultsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def begin_get_location_header_result(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                operation_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[SqlPool]: ...


    class azure.mgmt.synapse.operations.SqlPoolOperationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[SqlPoolOperation]: ...


    class azure.mgmt.synapse.operations.SqlPoolRecommendedSensitivityLabelsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                parameters: RecommendedSensitivityLabelUpdateList, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.synapse.operations.SqlPoolReplicationLinksOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get_by_name(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                link_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ReplicationLink: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[ReplicationLink]: ...


    class azure.mgmt.synapse.operations.SqlPoolRestorePointsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                parameters: CreateSqlPoolRestorePointDefinition, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[RestorePoint]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[RestorePoint]: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                restore_point_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                restore_point_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> RestorePoint: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[RestorePoint]: ...


    class azure.mgmt.synapse.operations.SqlPoolSchemasOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                schema_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> SqlPoolSchema: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                filter: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[SqlPoolSchema]: ...


    class azure.mgmt.synapse.operations.SqlPoolSecurityAlertPoliciesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                security_alert_policy_name: Union[str, SecurityAlertPolicyName], 
                parameters: SqlPoolSecurityAlertPolicy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SqlPoolSecurityAlertPolicy: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                security_alert_policy_name: Union[str, SecurityAlertPolicyName], 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SqlPoolSecurityAlertPolicy: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                security_alert_policy_name: Union[str, SecurityAlertPolicyName], 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> SqlPoolSecurityAlertPolicy: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[SqlPoolSecurityAlertPolicy]: ...


    class azure.mgmt.synapse.operations.SqlPoolSensitivityLabelsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                schema_name: str, 
                table_name: str, 
                column_name: str, 
                parameters: SensitivityLabel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SensitivityLabel: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                schema_name: str, 
                table_name: str, 
                column_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SensitivityLabel: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                schema_name: str, 
                table_name: str, 
                column_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                sensitivity_label_source: str = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def disable_recommendation(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                schema_name: str, 
                table_name: str, 
                column_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                sensitivity_label_source: str = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def enable_recommendation(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                schema_name: str, 
                table_name: str, 
                column_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                sensitivity_label_source: str = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                schema_name: str, 
                table_name: str, 
                column_name: str, 
                sensitivity_label_source: Union[str, SensitivityLabelSource], 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> SensitivityLabel: ...

        @distributed_trace
        def list_current(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                filter: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[SensitivityLabel]: ...

        @distributed_trace
        def list_recommended(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                include_disabled_recommendations: Optional[bool] = None, 
                skip_token: Optional[str] = None, 
                filter: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[SensitivityLabel]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                parameters: SensitivityLabelUpdateList, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.synapse.operations.SqlPoolTableColumnsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def list_by_table_name(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                schema_name: str, 
                table_name: str, 
                filter: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[SqlPoolColumn]: ...


    class azure.mgmt.synapse.operations.SqlPoolTablesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                schema_name: str, 
                table_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> SqlPoolTable: ...

        @distributed_trace
        def list_by_schema(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                schema_name: str, 
                filter: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[SqlPoolTable]: ...


    class azure.mgmt.synapse.operations.SqlPoolTransparentDataEncryptionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                transparent_data_encryption_name: Union[str, TransparentDataEncryptionName], 
                parameters: TransparentDataEncryption, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TransparentDataEncryption: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                transparent_data_encryption_name: Union[str, TransparentDataEncryptionName], 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TransparentDataEncryption: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                transparent_data_encryption_name: Union[str, TransparentDataEncryptionName], 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> TransparentDataEncryption: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[TransparentDataEncryption]: ...


    class azure.mgmt.synapse.operations.SqlPoolUsagesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[SqlPoolUsage]: ...


    class azure.mgmt.synapse.operations.SqlPoolVulnerabilityAssessmentRuleBaselinesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                vulnerability_assessment_name: Union[str, VulnerabilityAssessmentName], 
                rule_id: str, 
                baseline_name: Union[str, VulnerabilityAssessmentPolicyBaselineName], 
                parameters: SqlPoolVulnerabilityAssessmentRuleBaseline, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SqlPoolVulnerabilityAssessmentRuleBaseline: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                vulnerability_assessment_name: Union[str, VulnerabilityAssessmentName], 
                rule_id: str, 
                baseline_name: Union[str, VulnerabilityAssessmentPolicyBaselineName], 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SqlPoolVulnerabilityAssessmentRuleBaseline: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                vulnerability_assessment_name: Union[str, VulnerabilityAssessmentName], 
                rule_id: str, 
                baseline_name: Union[str, VulnerabilityAssessmentPolicyBaselineName], 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                vulnerability_assessment_name: Union[str, VulnerabilityAssessmentName], 
                rule_id: str, 
                baseline_name: Union[str, VulnerabilityAssessmentPolicyBaselineName], 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> SqlPoolVulnerabilityAssessmentRuleBaseline: ...


    class azure.mgmt.synapse.operations.SqlPoolVulnerabilityAssessmentScansOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def begin_initiate_scan(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                vulnerability_assessment_name: Union[str, VulnerabilityAssessmentName], 
                scan_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def export(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                vulnerability_assessment_name: Union[str, VulnerabilityAssessmentName], 
                scan_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> SqlPoolVulnerabilityAssessmentScansExport: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                vulnerability_assessment_name: Union[str, VulnerabilityAssessmentName], 
                scan_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> VulnerabilityAssessmentScanRecord: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                vulnerability_assessment_name: Union[str, VulnerabilityAssessmentName], 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[VulnerabilityAssessmentScanRecord]: ...


    class azure.mgmt.synapse.operations.SqlPoolVulnerabilityAssessmentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                vulnerability_assessment_name: Union[str, VulnerabilityAssessmentName], 
                parameters: SqlPoolVulnerabilityAssessment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SqlPoolVulnerabilityAssessment: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                vulnerability_assessment_name: Union[str, VulnerabilityAssessmentName], 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SqlPoolVulnerabilityAssessment: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                vulnerability_assessment_name: Union[str, VulnerabilityAssessmentName], 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                vulnerability_assessment_name: Union[str, VulnerabilityAssessmentName], 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> SqlPoolVulnerabilityAssessment: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[SqlPoolVulnerabilityAssessment]: ...


    class azure.mgmt.synapse.operations.SqlPoolWorkloadClassifierOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                workload_group_name: str, 
                workload_classifier_name: str, 
                parameters: WorkloadClassifier, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[WorkloadClassifier]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                workload_group_name: str, 
                workload_classifier_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[WorkloadClassifier]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                workload_group_name: str, 
                workload_classifier_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                workload_group_name: str, 
                workload_classifier_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> WorkloadClassifier: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                workload_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[WorkloadClassifier]: ...


    class azure.mgmt.synapse.operations.SqlPoolWorkloadGroupOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                workload_group_name: str, 
                parameters: WorkloadGroup, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[WorkloadGroup]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                workload_group_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[WorkloadGroup]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                workload_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                workload_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> WorkloadGroup: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[WorkloadGroup]: ...


    class azure.mgmt.synapse.operations.SqlPoolsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                sql_pool_info: SqlPool, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SqlPool]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                sql_pool_info: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SqlPool]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[SqlPool]: ...

        @distributed_trace
        def begin_pause(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[SqlPool]: ...

        @distributed_trace
        def begin_resume(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[SqlPool]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                sql_pool_info: SqlPoolPatchInfo, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SqlPool]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                sql_pool_info: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SqlPool]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> SqlPool: ...

        @distributed_trace
        def list_by_workspace(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[SqlPool]: ...

        @overload
        def rename(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                parameters: ResourceMoveDefinition, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def rename(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.synapse.operations.WorkspaceAadAdminsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                aad_admin_info: WorkspaceAadAdminInfo, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[WorkspaceAadAdminInfo]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                aad_admin_info: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[WorkspaceAadAdminInfo]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> WorkspaceAadAdminInfo: ...


    class azure.mgmt.synapse.operations.WorkspaceManagedIdentitySqlControlSettingsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                managed_identity_sql_control_settings: ManagedIdentitySqlControlSettingsModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ManagedIdentitySqlControlSettingsModel]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                managed_identity_sql_control_settings: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ManagedIdentitySqlControlSettingsModel]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ManagedIdentitySqlControlSettingsModel: ...


    class azure.mgmt.synapse.operations.WorkspaceManagedSqlServerBlobAuditingPoliciesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                blob_auditing_policy_name: Union[str, BlobAuditingPolicyName], 
                parameters: ServerBlobAuditingPolicy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ServerBlobAuditingPolicy]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                blob_auditing_policy_name: Union[str, BlobAuditingPolicyName], 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ServerBlobAuditingPolicy]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                blob_auditing_policy_name: Union[str, BlobAuditingPolicyName], 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ServerBlobAuditingPolicy: ...

        @distributed_trace
        def list_by_workspace(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[ServerBlobAuditingPolicy]: ...


    class azure.mgmt.synapse.operations.WorkspaceManagedSqlServerDedicatedSQLMinimalTlsSettingsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                dedicated_sq_lminimal_tls_settings_name: Union[str, DedicatedSQLMinimalTlsSettingsName], 
                parameters: DedicatedSQLminimalTlsSettings, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DedicatedSQLminimalTlsSettings]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                dedicated_sq_lminimal_tls_settings_name: Union[str, DedicatedSQLMinimalTlsSettingsName], 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DedicatedSQLminimalTlsSettings]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                dedicated_sq_lminimal_tls_settings_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> DedicatedSQLminimalTlsSettings: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[DedicatedSQLminimalTlsSettings]: ...


    class azure.mgmt.synapse.operations.WorkspaceManagedSqlServerEncryptionProtectorOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                encryption_protector_name: Union[str, EncryptionProtectorName], 
                parameters: EncryptionProtector, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EncryptionProtector]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                encryption_protector_name: Union[str, EncryptionProtectorName], 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EncryptionProtector]: ...

        @distributed_trace
        def begin_revalidate(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                encryption_protector_name: Union[str, EncryptionProtectorName], 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                encryption_protector_name: Union[str, EncryptionProtectorName], 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> EncryptionProtector: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[EncryptionProtector]: ...


    class azure.mgmt.synapse.operations.WorkspaceManagedSqlServerExtendedBlobAuditingPoliciesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                blob_auditing_policy_name: Union[str, BlobAuditingPolicyName], 
                parameters: ExtendedServerBlobAuditingPolicy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ExtendedServerBlobAuditingPolicy]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                blob_auditing_policy_name: Union[str, BlobAuditingPolicyName], 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ExtendedServerBlobAuditingPolicy]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                blob_auditing_policy_name: Union[str, BlobAuditingPolicyName], 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ExtendedServerBlobAuditingPolicy: ...

        @distributed_trace
        def list_by_workspace(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[ExtendedServerBlobAuditingPolicy]: ...


    class azure.mgmt.synapse.operations.WorkspaceManagedSqlServerRecoverableSqlPoolsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                sql_pool_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> RecoverableSqlPool: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[RecoverableSqlPool]: ...


    class azure.mgmt.synapse.operations.WorkspaceManagedSqlServerSecurityAlertPolicyOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                security_alert_policy_name: Union[str, SecurityAlertPolicyNameAutoGenerated], 
                parameters: ServerSecurityAlertPolicy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ServerSecurityAlertPolicy]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                security_alert_policy_name: Union[str, SecurityAlertPolicyNameAutoGenerated], 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ServerSecurityAlertPolicy]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                security_alert_policy_name: Union[str, SecurityAlertPolicyNameAutoGenerated], 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ServerSecurityAlertPolicy: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[ServerSecurityAlertPolicy]: ...


    class azure.mgmt.synapse.operations.WorkspaceManagedSqlServerUsagesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[ServerUsage]: ...


    class azure.mgmt.synapse.operations.WorkspaceManagedSqlServerVulnerabilityAssessmentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                vulnerability_assessment_name: Union[str, VulnerabilityAssessmentName], 
                parameters: ServerVulnerabilityAssessment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ServerVulnerabilityAssessment: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                vulnerability_assessment_name: Union[str, VulnerabilityAssessmentName], 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ServerVulnerabilityAssessment: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                vulnerability_assessment_name: Union[str, VulnerabilityAssessmentName], 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                vulnerability_assessment_name: Union[str, VulnerabilityAssessmentName], 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ServerVulnerabilityAssessment: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[ServerVulnerabilityAssessment]: ...


    class azure.mgmt.synapse.operations.WorkspaceSqlAadAdminsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                aad_admin_info: WorkspaceAadAdminInfo, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[WorkspaceAadAdminInfo]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                aad_admin_info: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[WorkspaceAadAdminInfo]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> WorkspaceAadAdminInfo: ...


    class azure.mgmt.synapse.operations.WorkspacesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                workspace_info: Workspace, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Workspace]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                workspace_info: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Workspace]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[Workspace]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                workspace_patch_info: WorkspacePatchInfo, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Workspace]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                workspace_patch_info: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Workspace]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Workspace: ...

        @distributed_trace
        def list(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[Workspace]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[Workspace]: ...


```