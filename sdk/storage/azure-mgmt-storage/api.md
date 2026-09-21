```py
namespace azure.mgmt.storage

    class azure.mgmt.storage.StorageManagementClient: implements ContextManager 
        advanced_platform_metrics: AdvancedPlatformMetricsOperations
        blob_containers: BlobContainersOperations
        blob_inventory_policies: BlobInventoryPoliciesOperations
        blob_services: BlobServicesOperations
        connectors: ConnectorsOperations
        data_shares: DataSharesOperations
        deleted_accounts: DeletedAccountsOperations
        encryption_scopes: EncryptionScopesOperations
        file_services: FileServicesOperations
        file_shares: FileSharesOperations
        local_users: LocalUsersOperations
        management_policies: ManagementPoliciesOperations
        network_security_perimeter_configurations: NetworkSecurityPerimeterConfigurationsOperations
        object_replication_policies: ObjectReplicationPoliciesOperations
        operations: Operations
        private_endpoint_connections: PrivateEndpointConnectionsOperations
        private_link_resources: PrivateLinkResourcesOperations
        queue: QueueOperations
        queue_services: QueueServicesOperations
        skus: SkusOperations
        storage_accounts: StorageAccountsOperations
        storage_task_assignment_instances_report: StorageTaskAssignmentInstancesReportOperations
        storage_task_assignments: StorageTaskAssignmentsOperations
        storage_task_assignments_instances_report: StorageTaskAssignmentsInstancesReportOperations
        table: TableOperations
        table_services: TableServicesOperations
        usages: UsagesOperations

        def __init__(
                self, 
                credential: TokenCredential, 
                subscription_id: str, 
                base_url: Optional[str] = None, 
                *, 
                api_version: str = ..., 
                cloud_setting: Optional[AzureClouds] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def close(self) -> None: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> HttpResponse: ...


namespace azure.mgmt.storage.aio

    class azure.mgmt.storage.aio.StorageManagementClient: implements AsyncContextManager 
        advanced_platform_metrics: AdvancedPlatformMetricsOperations
        blob_containers: BlobContainersOperations
        blob_inventory_policies: BlobInventoryPoliciesOperations
        blob_services: BlobServicesOperations
        connectors: ConnectorsOperations
        data_shares: DataSharesOperations
        deleted_accounts: DeletedAccountsOperations
        encryption_scopes: EncryptionScopesOperations
        file_services: FileServicesOperations
        file_shares: FileSharesOperations
        local_users: LocalUsersOperations
        management_policies: ManagementPoliciesOperations
        network_security_perimeter_configurations: NetworkSecurityPerimeterConfigurationsOperations
        object_replication_policies: ObjectReplicationPoliciesOperations
        operations: Operations
        private_endpoint_connections: PrivateEndpointConnectionsOperations
        private_link_resources: PrivateLinkResourcesOperations
        queue: QueueOperations
        queue_services: QueueServicesOperations
        skus: SkusOperations
        storage_accounts: StorageAccountsOperations
        storage_task_assignment_instances_report: StorageTaskAssignmentInstancesReportOperations
        storage_task_assignments: StorageTaskAssignmentsOperations
        storage_task_assignments_instances_report: StorageTaskAssignmentsInstancesReportOperations
        table: TableOperations
        table_services: TableServicesOperations
        usages: UsagesOperations

        def __init__(
                self, 
                credential: AsyncTokenCredential, 
                subscription_id: str, 
                base_url: Optional[str] = None, 
                *, 
                api_version: str = ..., 
                cloud_setting: Optional[AzureClouds] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        async def close(self) -> None: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> Awaitable[AsyncHttpResponse]: ...


namespace azure.mgmt.storage.aio.operations

    class azure.mgmt.storage.aio.operations.AdvancedPlatformMetricsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                advanced_platform_metrics_rule_type: Union[str, AdvancedPlatformMetricsRuleType], 
                resource: AdvancedPlatformMetricsRule, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AdvancedPlatformMetricsRule: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                advanced_platform_metrics_rule_type: Union[str, AdvancedPlatformMetricsRuleType], 
                resource: AdvancedPlatformMetricsRule, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AdvancedPlatformMetricsRule: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                advanced_platform_metrics_rule_type: Union[str, AdvancedPlatformMetricsRuleType], 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AdvancedPlatformMetricsRule: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-04-01', params_added_on={'2026-04-01': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'advanced_platform_metrics_rule_type']}, api_versions_list=['2026-04-01'])
        async def delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                advanced_platform_metrics_rule_type: Union[str, AdvancedPlatformMetricsRuleType], 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-04-01', params_added_on={'2026-04-01': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'advanced_platform_metrics_rule_type', 'accept']}, api_versions_list=['2026-04-01'])
        async def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                advanced_platform_metrics_rule_type: Union[str, AdvancedPlatformMetricsRuleType], 
                **kwargs: Any
            ) -> AdvancedPlatformMetricsRule: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-04-01', params_added_on={'2026-04-01': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'accept']}, api_versions_list=['2026-04-01'])
        def list(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[AdvancedPlatformMetricsRule]: ...


    class azure.mgmt.storage.aio.operations.BlobContainersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_object_level_worm(
                self, 
                resource_group_name: str, 
                account_name: str, 
                container_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def clear_legal_hold(
                self, 
                resource_group_name: str, 
                account_name: str, 
                container_name: str, 
                legal_hold: LegalHold, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LegalHold: ...

        @overload
        async def clear_legal_hold(
                self, 
                resource_group_name: str, 
                account_name: str, 
                container_name: str, 
                legal_hold: LegalHold, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LegalHold: ...

        @overload
        async def clear_legal_hold(
                self, 
                resource_group_name: str, 
                account_name: str, 
                container_name: str, 
                legal_hold: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LegalHold: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                container_name: str, 
                blob_container: BlobContainer, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BlobContainer: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                container_name: str, 
                blob_container: BlobContainer, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BlobContainer: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                container_name: str, 
                blob_container: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BlobContainer: ...

        @overload
        async def create_or_update_immutability_policy(
                self, 
                resource_group_name: str, 
                account_name: str, 
                container_name: str, 
                parameters: Optional[ImmutabilityPolicy] = None, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> ImmutabilityPolicy: ...

        @overload
        async def create_or_update_immutability_policy(
                self, 
                resource_group_name: str, 
                account_name: str, 
                container_name: str, 
                parameters: Optional[ImmutabilityPolicy] = None, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> ImmutabilityPolicy: ...

        @overload
        async def create_or_update_immutability_policy(
                self, 
                resource_group_name: str, 
                account_name: str, 
                container_name: str, 
                parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> ImmutabilityPolicy: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                container_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def delete_immutability_policy(
                self, 
                resource_group_name: str, 
                account_name: str, 
                container_name: str, 
                *, 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> ImmutabilityPolicy: ...

        @overload
        async def extend_immutability_policy(
                self, 
                resource_group_name: str, 
                account_name: str, 
                container_name: str, 
                parameters: Optional[ImmutabilityPolicy] = None, 
                *, 
                content_type: str = "application/json", 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> ImmutabilityPolicy: ...

        @overload
        async def extend_immutability_policy(
                self, 
                resource_group_name: str, 
                account_name: str, 
                container_name: str, 
                parameters: Optional[ImmutabilityPolicy] = None, 
                *, 
                content_type: str = "application/json", 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> ImmutabilityPolicy: ...

        @overload
        async def extend_immutability_policy(
                self, 
                resource_group_name: str, 
                account_name: str, 
                container_name: str, 
                parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> ImmutabilityPolicy: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                container_name: str, 
                **kwargs: Any
            ) -> BlobContainer: ...

        @distributed_trace_async
        async def get_immutability_policy(
                self, 
                resource_group_name: str, 
                account_name: str, 
                container_name: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> ImmutabilityPolicy: ...

        @overload
        async def lease(
                self, 
                resource_group_name: str, 
                account_name: str, 
                container_name: str, 
                parameters: Optional[LeaseContainerRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LeaseContainerResponse: ...

        @overload
        async def lease(
                self, 
                resource_group_name: str, 
                account_name: str, 
                container_name: str, 
                parameters: Optional[LeaseContainerRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LeaseContainerResponse: ...

        @overload
        async def lease(
                self, 
                resource_group_name: str, 
                account_name: str, 
                container_name: str, 
                parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LeaseContainerResponse: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                account_name: str, 
                *, 
                filter: Optional[str] = ..., 
                include: Optional[Union[str, ListContainersInclude]] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[ListContainerItem]: ...

        @distributed_trace_async
        async def lock_immutability_policy(
                self, 
                resource_group_name: str, 
                account_name: str, 
                container_name: str, 
                *, 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> ImmutabilityPolicy: ...

        @overload
        async def set_legal_hold(
                self, 
                resource_group_name: str, 
                account_name: str, 
                container_name: str, 
                legal_hold: LegalHold, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LegalHold: ...

        @overload
        async def set_legal_hold(
                self, 
                resource_group_name: str, 
                account_name: str, 
                container_name: str, 
                legal_hold: LegalHold, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LegalHold: ...

        @overload
        async def set_legal_hold(
                self, 
                resource_group_name: str, 
                account_name: str, 
                container_name: str, 
                legal_hold: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LegalHold: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                container_name: str, 
                blob_container: BlobContainer, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BlobContainer: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                container_name: str, 
                blob_container: BlobContainer, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BlobContainer: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                container_name: str, 
                blob_container: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BlobContainer: ...


    class azure.mgmt.storage.aio.operations.BlobInventoryPoliciesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                blob_inventory_policy_name: Union[str, BlobInventoryPolicyName], 
                properties: BlobInventoryPolicy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BlobInventoryPolicy: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                blob_inventory_policy_name: Union[str, BlobInventoryPolicyName], 
                properties: BlobInventoryPolicy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BlobInventoryPolicy: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                blob_inventory_policy_name: Union[str, BlobInventoryPolicyName], 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BlobInventoryPolicy: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                blob_inventory_policy_name: Union[str, BlobInventoryPolicyName], 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                blob_inventory_policy_name: Union[str, BlobInventoryPolicyName], 
                **kwargs: Any
            ) -> BlobInventoryPolicy: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[BlobInventoryPolicy]: ...


    class azure.mgmt.storage.aio.operations.BlobServicesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get_service_properties(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> BlobServiceProperties: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[BlobServiceProperties]: ...

        @overload
        async def set_service_properties(
                self, 
                resource_group_name: str, 
                account_name: str, 
                parameters: BlobServiceProperties, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BlobServiceProperties: ...

        @overload
        async def set_service_properties(
                self, 
                resource_group_name: str, 
                account_name: str, 
                parameters: BlobServiceProperties, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BlobServiceProperties: ...

        @overload
        async def set_service_properties(
                self, 
                resource_group_name: str, 
                account_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BlobServiceProperties: ...


    class azure.mgmt.storage.aio.operations.ConnectorsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                connector_name: str, 
                resource: Connector, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Connector]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                connector_name: str, 
                resource: Connector, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Connector]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                connector_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Connector]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-08-01', params_added_on={'2025-08-01': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'connector_name']}, api_versions_list=['2025-08-01', '2026-04-01'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                connector_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_test_existing_connection(
                self, 
                resource_group_name: str, 
                account_name: str, 
                connector_name: str, 
                body: TestExistingConnectionRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[TestConnectionResponse]: ...

        @overload
        async def begin_test_existing_connection(
                self, 
                resource_group_name: str, 
                account_name: str, 
                connector_name: str, 
                body: TestExistingConnectionRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[TestConnectionResponse]: ...

        @overload
        async def begin_test_existing_connection(
                self, 
                resource_group_name: str, 
                account_name: str, 
                connector_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[TestConnectionResponse]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                connector_name: str, 
                properties: ConnectorUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Connector]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                connector_name: str, 
                properties: ConnectorUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Connector]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                connector_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Connector]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-08-01', params_added_on={'2025-08-01': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'connector_name', 'accept']}, api_versions_list=['2025-08-01', '2026-04-01'])
        async def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                connector_name: str, 
                **kwargs: Any
            ) -> Connector: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-08-01', params_added_on={'2025-08-01': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'accept']}, api_versions_list=['2025-08-01', '2026-04-01'])
        def list_by_storage_account(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Connector]: ...


    class azure.mgmt.storage.aio.operations.DataSharesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                data_share_name: str, 
                resource: DataShare, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DataShare]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                data_share_name: str, 
                resource: DataShare, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DataShare]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                data_share_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DataShare]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-08-01', params_added_on={'2025-08-01': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'data_share_name']}, api_versions_list=['2025-08-01', '2026-04-01'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                data_share_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                data_share_name: str, 
                properties: DataShareUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DataShare]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                data_share_name: str, 
                properties: DataShareUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DataShare]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                data_share_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DataShare]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-08-01', params_added_on={'2025-08-01': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'data_share_name', 'accept']}, api_versions_list=['2025-08-01', '2026-04-01'])
        async def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                data_share_name: str, 
                **kwargs: Any
            ) -> DataShare: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-08-01', params_added_on={'2025-08-01': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'accept']}, api_versions_list=['2025-08-01', '2026-04-01'])
        def list_by_storage_account(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[DataShare]: ...


    class azure.mgmt.storage.aio.operations.DeletedAccountsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                deleted_account_name: str, 
                location: str, 
                **kwargs: Any
            ) -> DeletedAccount: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[DeletedAccount]: ...


    class azure.mgmt.storage.aio.operations.EncryptionScopesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                encryption_scope_name: str, 
                **kwargs: Any
            ) -> EncryptionScope: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                account_name: str, 
                *, 
                filter: Optional[str] = ..., 
                include: Optional[Union[str, ListEncryptionScopesInclude]] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[EncryptionScope]: ...

        @overload
        async def patch(
                self, 
                resource_group_name: str, 
                account_name: str, 
                encryption_scope_name: str, 
                encryption_scope: EncryptionScope, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EncryptionScope: ...

        @overload
        async def patch(
                self, 
                resource_group_name: str, 
                account_name: str, 
                encryption_scope_name: str, 
                encryption_scope: EncryptionScope, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EncryptionScope: ...

        @overload
        async def patch(
                self, 
                resource_group_name: str, 
                account_name: str, 
                encryption_scope_name: str, 
                encryption_scope: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EncryptionScope: ...

        @overload
        async def put(
                self, 
                resource_group_name: str, 
                account_name: str, 
                encryption_scope_name: str, 
                encryption_scope: EncryptionScope, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EncryptionScope: ...

        @overload
        async def put(
                self, 
                resource_group_name: str, 
                account_name: str, 
                encryption_scope_name: str, 
                encryption_scope: EncryptionScope, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EncryptionScope: ...

        @overload
        async def put(
                self, 
                resource_group_name: str, 
                account_name: str, 
                encryption_scope_name: str, 
                encryption_scope: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EncryptionScope: ...


    class azure.mgmt.storage.aio.operations.FileServicesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get_service_properties(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> FileServiceProperties: ...

        @distributed_trace_async
        async def get_service_usage(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> FileServiceUsage: ...

        @distributed_trace_async
        async def list(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> FileServiceItems: ...

        @distributed_trace
        def list_service_usages(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[FileServiceUsage]: ...

        @overload
        async def set_service_properties(
                self, 
                resource_group_name: str, 
                account_name: str, 
                parameters: FileServiceProperties, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FileServiceProperties: ...

        @overload
        async def set_service_properties(
                self, 
                resource_group_name: str, 
                account_name: str, 
                parameters: FileServiceProperties, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FileServiceProperties: ...

        @overload
        async def set_service_properties(
                self, 
                resource_group_name: str, 
                account_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FileServiceProperties: ...


    class azure.mgmt.storage.aio.operations.FileSharesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_name: str, 
                file_share: FileShare, 
                *, 
                content_type: str = "application/json", 
                expand: Optional[str] = ..., 
                **kwargs: Any
            ) -> FileShare: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_name: str, 
                file_share: FileShare, 
                *, 
                content_type: str = "application/json", 
                expand: Optional[str] = ..., 
                **kwargs: Any
            ) -> FileShare: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_name: str, 
                file_share: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                expand: Optional[str] = ..., 
                **kwargs: Any
            ) -> FileShare: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_name: str, 
                *, 
                include: Optional[str] = ..., 
                x_ms_snapshot: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_name: str, 
                *, 
                expand: Optional[str] = ..., 
                x_ms_snapshot: Optional[str] = ..., 
                **kwargs: Any
            ) -> FileShare: ...

        @overload
        async def lease(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_name: str, 
                parameters: Optional[LeaseShareRequest] = None, 
                *, 
                content_type: str = "application/json", 
                x_ms_snapshot: Optional[str] = ..., 
                **kwargs: Any
            ) -> LeaseShareResponse: ...

        @overload
        async def lease(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_name: str, 
                parameters: Optional[LeaseShareRequest] = None, 
                *, 
                content_type: str = "application/json", 
                x_ms_snapshot: Optional[str] = ..., 
                **kwargs: Any
            ) -> LeaseShareResponse: ...

        @overload
        async def lease(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_name: str, 
                parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                x_ms_snapshot: Optional[str] = ..., 
                **kwargs: Any
            ) -> LeaseShareResponse: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                account_name: str, 
                *, 
                expand: Optional[str] = ..., 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[FileShareItem]: ...

        @overload
        async def restore(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_name: str, 
                deleted_share: DeletedShare, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def restore(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_name: str, 
                deleted_share: DeletedShare, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def restore(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_name: str, 
                deleted_share: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_name: str, 
                file_share: FileShare, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FileShare: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_name: str, 
                file_share: FileShare, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FileShare: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_name: str, 
                file_share: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FileShare: ...


    class azure.mgmt.storage.aio.operations.LocalUsersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                username: str, 
                properties: LocalUser, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LocalUser: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                username: str, 
                properties: LocalUser, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LocalUser: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                username: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LocalUser: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                username: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                username: str, 
                **kwargs: Any
            ) -> LocalUser: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                account_name: str, 
                *, 
                filter: Optional[str] = ..., 
                include: Optional[Union[str, ListLocalUserIncludeParam]] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[LocalUser]: ...

        @distributed_trace_async
        async def list_keys(
                self, 
                resource_group_name: str, 
                account_name: str, 
                username: str, 
                **kwargs: Any
            ) -> LocalUserKeys: ...

        @distributed_trace_async
        async def regenerate_password(
                self, 
                resource_group_name: str, 
                account_name: str, 
                username: str, 
                **kwargs: Any
            ) -> LocalUserRegeneratePasswordResult: ...


    class azure.mgmt.storage.aio.operations.ManagementPoliciesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                management_policy_name: Union[str, ManagementPolicyName], 
                properties: ManagementPolicy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ManagementPolicy: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                management_policy_name: Union[str, ManagementPolicyName], 
                properties: ManagementPolicy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ManagementPolicy: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                management_policy_name: Union[str, ManagementPolicyName], 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ManagementPolicy: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                management_policy_name: Union[str, ManagementPolicyName], 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                management_policy_name: Union[str, ManagementPolicyName], 
                **kwargs: Any
            ) -> ManagementPolicy: ...


    class azure.mgmt.storage.aio.operations.NetworkSecurityPerimeterConfigurationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_reconcile(
                self, 
                resource_group_name: str, 
                account_name: str, 
                network_security_perimeter_configuration_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                network_security_perimeter_configuration_name: str, 
                **kwargs: Any
            ) -> NetworkSecurityPerimeterConfiguration: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[NetworkSecurityPerimeterConfiguration]: ...


    class azure.mgmt.storage.aio.operations.ObjectReplicationPoliciesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                object_replication_policy_id: str, 
                properties: ObjectReplicationPolicy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ObjectReplicationPolicy: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                object_replication_policy_id: str, 
                properties: ObjectReplicationPolicy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ObjectReplicationPolicy: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                object_replication_policy_id: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ObjectReplicationPolicy: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                object_replication_policy_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                object_replication_policy_id: str, 
                **kwargs: Any
            ) -> ObjectReplicationPolicy: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ObjectReplicationPolicy]: ...


    class azure.mgmt.storage.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


    class azure.mgmt.storage.aio.operations.PrivateEndpointConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[PrivateEndpointConnection]: ...

        @overload
        async def put(
                self, 
                resource_group_name: str, 
                account_name: str, 
                private_endpoint_connection_name: str, 
                properties: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @overload
        async def put(
                self, 
                resource_group_name: str, 
                account_name: str, 
                private_endpoint_connection_name: str, 
                properties: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @overload
        async def put(
                self, 
                resource_group_name: str, 
                account_name: str, 
                private_endpoint_connection_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...


    class azure.mgmt.storage.aio.operations.PrivateLinkResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def list_by_storage_account(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> PrivateLinkResourceListResult: ...


    class azure.mgmt.storage.aio.operations.QueueOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                queue_name: str, 
                queue: StorageQueue, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StorageQueue: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                queue_name: str, 
                queue: StorageQueue, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StorageQueue: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                queue_name: str, 
                queue: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StorageQueue: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                queue_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                queue_name: str, 
                **kwargs: Any
            ) -> StorageQueue: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                account_name: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[ListQueue]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                queue_name: str, 
                queue: StorageQueue, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StorageQueue: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                queue_name: str, 
                queue: StorageQueue, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StorageQueue: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                queue_name: str, 
                queue: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StorageQueue: ...


    class azure.mgmt.storage.aio.operations.QueueServicesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get_service_properties(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> QueueServiceProperties: ...

        @distributed_trace_async
        async def list(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> ListQueueServices: ...

        @overload
        async def set_service_properties(
                self, 
                resource_group_name: str, 
                account_name: str, 
                parameters: QueueServiceProperties, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> QueueServiceProperties: ...

        @overload
        async def set_service_properties(
                self, 
                resource_group_name: str, 
                account_name: str, 
                parameters: QueueServiceProperties, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> QueueServiceProperties: ...

        @overload
        async def set_service_properties(
                self, 
                resource_group_name: str, 
                account_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> QueueServiceProperties: ...


    class azure.mgmt.storage.aio.operations.SkusOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[SkuInformation]: ...


    class azure.mgmt.storage.aio.operations.StorageAccountsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_abort_hierarchical_namespace_migration(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                parameters: StorageAccountCreateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[StorageAccount]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                parameters: StorageAccountCreateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[StorageAccount]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[StorageAccount]: ...

        @overload
        async def begin_customer_initiated_migration(
                self, 
                resource_group_name: str, 
                account_name: str, 
                parameters: StorageAccountMigration, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_customer_initiated_migration(
                self, 
                resource_group_name: str, 
                account_name: str, 
                parameters: StorageAccountMigration, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_customer_initiated_migration(
                self, 
                resource_group_name: str, 
                account_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_failover(
                self, 
                resource_group_name: str, 
                account_name: str, 
                *, 
                failover_type: Literal["Planned"] = "Planned", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_hierarchical_namespace_migration(
                self, 
                resource_group_name: str, 
                account_name: str, 
                *, 
                request_type: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_restore_blob_ranges(
                self, 
                resource_group_name: str, 
                account_name: str, 
                parameters: BlobRestoreParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BlobRestoreStatus]: ...

        @overload
        async def begin_restore_blob_ranges(
                self, 
                resource_group_name: str, 
                account_name: str, 
                parameters: BlobRestoreParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BlobRestoreStatus]: ...

        @overload
        async def begin_restore_blob_ranges(
                self, 
                resource_group_name: str, 
                account_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BlobRestoreStatus]: ...

        @overload
        async def check_name_availability(
                self, 
                account_name: StorageAccountCheckNameAvailabilityParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResult: ...

        @overload
        async def check_name_availability(
                self, 
                account_name: StorageAccountCheckNameAvailabilityParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResult: ...

        @overload
        async def check_name_availability(
                self, 
                account_name: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResult: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get_customer_initiated_migration(
                self, 
                resource_group_name: str, 
                account_name: str, 
                migration_name: Union[str, MigrationName], 
                **kwargs: Any
            ) -> StorageAccountMigration: ...

        @distributed_trace_async
        async def get_properties(
                self, 
                resource_group_name: str, 
                account_name: str, 
                *, 
                expand: Optional[Union[str, StorageAccountExpand]] = ..., 
                **kwargs: Any
            ) -> StorageAccount: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[StorageAccount]: ...

        @overload
        async def list_account_sas(
                self, 
                resource_group_name: str, 
                account_name: str, 
                parameters: AccountSasParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ListAccountSasResponse: ...

        @overload
        async def list_account_sas(
                self, 
                resource_group_name: str, 
                account_name: str, 
                parameters: AccountSasParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ListAccountSasResponse: ...

        @overload
        async def list_account_sas(
                self, 
                resource_group_name: str, 
                account_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ListAccountSasResponse: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[StorageAccount]: ...

        @distributed_trace_async
        async def list_keys(
                self, 
                resource_group_name: str, 
                account_name: str, 
                *, 
                expand: Literal["kerb"] = "kerb", 
                **kwargs: Any
            ) -> StorageAccountListKeysResult: ...

        @overload
        async def list_service_sas(
                self, 
                resource_group_name: str, 
                account_name: str, 
                parameters: ServiceSasParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ListServiceSasResponse: ...

        @overload
        async def list_service_sas(
                self, 
                resource_group_name: str, 
                account_name: str, 
                parameters: ServiceSasParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ListServiceSasResponse: ...

        @overload
        async def list_service_sas(
                self, 
                resource_group_name: str, 
                account_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ListServiceSasResponse: ...

        @overload
        async def regenerate_key(
                self, 
                resource_group_name: str, 
                account_name: str, 
                regenerate_key: StorageAccountRegenerateKeyParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StorageAccountListKeysResult: ...

        @overload
        async def regenerate_key(
                self, 
                resource_group_name: str, 
                account_name: str, 
                regenerate_key: StorageAccountRegenerateKeyParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StorageAccountListKeysResult: ...

        @overload
        async def regenerate_key(
                self, 
                resource_group_name: str, 
                account_name: str, 
                regenerate_key: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StorageAccountListKeysResult: ...

        @distributed_trace_async
        async def revoke_user_delegation_keys(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                parameters: StorageAccountUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StorageAccount: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                parameters: StorageAccountUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StorageAccount: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StorageAccount: ...


    class azure.mgmt.storage.aio.operations.StorageTaskAssignmentInstancesReportOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                account_name: str, 
                storage_task_assignment_name: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[StorageTaskReportInstance]: ...


    class azure.mgmt.storage.aio.operations.StorageTaskAssignmentsInstancesReportOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                account_name: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[StorageTaskReportInstance]: ...


    class azure.mgmt.storage.aio.operations.StorageTaskAssignmentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                storage_task_assignment_name: str, 
                parameters: StorageTaskAssignment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[StorageTaskAssignment]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                storage_task_assignment_name: str, 
                parameters: StorageTaskAssignment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[StorageTaskAssignment]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                storage_task_assignment_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[StorageTaskAssignment]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                storage_task_assignment_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-08-01', params_added_on={'2025-08-01': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'storage_task_assignment_name']}, api_versions_list=['2025-08-01', '2026-04-01'])
        async def begin_stop_assignment(
                self, 
                resource_group_name: str, 
                account_name: str, 
                storage_task_assignment_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                storage_task_assignment_name: str, 
                parameters: StorageTaskAssignmentUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[StorageTaskAssignment]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                storage_task_assignment_name: str, 
                parameters: StorageTaskAssignmentUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[StorageTaskAssignment]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                storage_task_assignment_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[StorageTaskAssignment]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                storage_task_assignment_name: str, 
                **kwargs: Any
            ) -> StorageTaskAssignment: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                account_name: str, 
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[StorageTaskAssignment]: ...


    class azure.mgmt.storage.aio.operations.TableOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                table_name: str, 
                parameters: Optional[Table] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Table: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                table_name: str, 
                parameters: Optional[Table] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Table: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                table_name: str, 
                parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Table: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                table_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                table_name: str, 
                **kwargs: Any
            ) -> Table: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Table]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                table_name: str, 
                parameters: Optional[Table] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Table: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                table_name: str, 
                parameters: Optional[Table] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Table: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                table_name: str, 
                parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Table: ...


    class azure.mgmt.storage.aio.operations.TableServicesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get_service_properties(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> TableServiceProperties: ...

        @distributed_trace_async
        async def list(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> ListTableServices: ...

        @overload
        async def set_service_properties(
                self, 
                resource_group_name: str, 
                account_name: str, 
                parameters: TableServiceProperties, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TableServiceProperties: ...

        @overload
        async def set_service_properties(
                self, 
                resource_group_name: str, 
                account_name: str, 
                parameters: TableServiceProperties, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TableServiceProperties: ...

        @overload
        async def set_service_properties(
                self, 
                resource_group_name: str, 
                account_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TableServiceProperties: ...


    class azure.mgmt.storage.aio.operations.UsagesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_by_location(
                self, 
                location: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Usage]: ...


namespace azure.mgmt.storage.models

    class azure.mgmt.storage.models.AccessPolicy(_Model):
        expiry_time: Optional[datetime]
        permission: Optional[str]
        start_time: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                expiry_time: Optional[datetime] = ..., 
                permission: Optional[str] = ..., 
                start_time: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.AccessTier(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COLD = "Cold"
        COOL = "Cool"
        HOT = "Hot"
        PREMIUM = "Premium"
        SMART = "Smart"


    class azure.mgmt.storage.models.AccountImmutabilityPolicyProperties(_Model):
        allow_protected_append_writes: Optional[bool]
        immutability_period_since_creation_in_days: Optional[int]
        state: Optional[Union[str, AccountImmutabilityPolicyState]]

        @overload
        def __init__(
                self, 
                *, 
                allow_protected_append_writes: Optional[bool] = ..., 
                immutability_period_since_creation_in_days: Optional[int] = ..., 
                state: Optional[Union[str, AccountImmutabilityPolicyState]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.AccountImmutabilityPolicyState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        LOCKED = "Locked"
        UNLOCKED = "Unlocked"


    class azure.mgmt.storage.models.AccountLimits(_Model):
        max_file_shares: Optional[int]
        max_provisioned_bandwidth_mi_b_per_sec: Optional[int]
        max_provisioned_iops: Optional[int]
        max_provisioned_storage_gi_b: Optional[int]


    class azure.mgmt.storage.models.AccountSasParameters(_Model):
        ip_address_or_range: Optional[str]
        key_to_sign: Optional[str]
        permissions: Union[str, Permissions]
        protocols: Optional[Union[str, HttpProtocol]]
        resource_types: Union[str, SignedResourceTypes]
        services: Union[str, Services]
        shared_access_expiry_time: datetime
        shared_access_start_time: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                ip_address_or_range: Optional[str] = ..., 
                key_to_sign: Optional[str] = ..., 
                permissions: Union[str, Permissions], 
                protocols: Optional[Union[str, HttpProtocol]] = ..., 
                resource_types: Union[str, SignedResourceTypes], 
                services: Union[str, Services], 
                shared_access_expiry_time: datetime, 
                shared_access_start_time: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.AccountStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVAILABLE = "available"
        UNAVAILABLE = "unavailable"


    class azure.mgmt.storage.models.AccountType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPUTER = "Computer"
        USER = "User"


    class azure.mgmt.storage.models.AccountUsage(_Model):
        live_shares: Optional[AccountUsageElements]
        soft_deleted_shares: Optional[AccountUsageElements]

        @overload
        def __init__(
                self, 
                *, 
                live_shares: Optional[AccountUsageElements] = ..., 
                soft_deleted_shares: Optional[AccountUsageElements] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.AccountUsageElements(_Model):
        file_share_count: Optional[int]
        provisioned_bandwidth_mi_b_per_sec: Optional[int]
        provisioned_iops: Optional[int]
        provisioned_storage_gi_b: Optional[int]


    class azure.mgmt.storage.models.ActiveDirectoryProperties(_Model):
        account_type: Optional[Union[str, AccountType]]
        azure_storage_sid: Optional[str]
        domain_guid: Optional[str]
        domain_name: Optional[str]
        domain_sid: Optional[str]
        forest_name: Optional[str]
        net_bios_domain_name: Optional[str]
        sam_account_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                account_type: Optional[Union[str, AccountType]] = ..., 
                azure_storage_sid: Optional[str] = ..., 
                domain_guid: Optional[str] = ..., 
                domain_name: Optional[str] = ..., 
                domain_sid: Optional[str] = ..., 
                forest_name: Optional[str] = ..., 
                net_bios_domain_name: Optional[str] = ..., 
                sam_account_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.AdvancedPlatformMetricsFilterType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALL_CONTAINERS_FILTER = "AllContainersFilter"
        CONTAINER_LIST_FILTER = "ContainerListFilter"
        CONTAINER_PREFIX_FILTER = "ContainerPrefixFilter"


    class azure.mgmt.storage.models.AdvancedPlatformMetricsRule(ProxyResource):
        id: str
        name: str
        properties: Optional[AdvancedPlatformMetricsRuleProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AdvancedPlatformMetricsRuleProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.AdvancedPlatformMetricsRuleConfig(_Model):
        filter_type: Optional[Union[str, AdvancedPlatformMetricsFilterType]]
        filter_values: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                filter_type: Optional[Union[str, AdvancedPlatformMetricsFilterType]] = ..., 
                filter_values: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.AdvancedPlatformMetricsRuleProperties(_Model):
        enabled: bool
        last_modified_time: Optional[datetime]
        metrics_emitted: Optional[list[Union[str, MetricsEmitted]]]
        rule_config: AdvancedPlatformMetricsRuleConfig
        rule_type: Optional[Union[str, AdvancedPlatformMetricsRuleType]]

        @overload
        def __init__(
                self, 
                *, 
                enabled: bool, 
                rule_config: AdvancedPlatformMetricsRuleConfig
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.AdvancedPlatformMetricsRuleType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONTAINER_LEVEL_CAPACITY_METRICS = "ContainerLevelCapacityMetrics"


    class azure.mgmt.storage.models.AllowedCopyScope(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AAD = "AAD"
        ALL = "All"
        PRIVATE_LINK = "PrivateLink"


    class azure.mgmt.storage.models.AllowedMethods(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONNECT = "CONNECT"
        DELETE = "DELETE"
        GET = "GET"
        HEAD = "HEAD"
        MERGE = "MERGE"
        OPTIONS = "OPTIONS"
        PATCH = "PATCH"
        POST = "POST"
        PUT = "PUT"
        TRACE = "TRACE"


    class azure.mgmt.storage.models.AzureEntityResource(ResourceAutoGenerated):
        etag: Optional[str]
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.storage.models.AzureFilesIdentityBasedAuthentication(_Model):
        active_directory_properties: Optional[ActiveDirectoryProperties]
        default_share_permission: Optional[Union[str, DefaultSharePermission]]
        directory_service_options: Union[str, DirectoryServiceOptions]
        smb_o_auth_settings: Optional[SmbOAuthSettings]

        @overload
        def __init__(
                self, 
                *, 
                active_directory_properties: Optional[ActiveDirectoryProperties] = ..., 
                default_share_permission: Optional[Union[str, DefaultSharePermission]] = ..., 
                directory_service_options: Union[str, DirectoryServiceOptions], 
                smb_o_auth_settings: Optional[SmbOAuthSettings] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.BlobContainer(ProxyResource):
        container_properties: Optional[ContainerProperties]
        etag: Optional[str]
        id: str
        name: str
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                container_properties: Optional[ContainerProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.storage.models.BlobInventoryCreationTime(_Model):
        last_n_days: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                last_n_days: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.BlobInventoryPolicy(ProxyResource):
        id: str
        name: str
        properties: Optional[BlobInventoryPolicyProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[BlobInventoryPolicyProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.storage.models.BlobInventoryPolicyDefinition(_Model):
        filters: Optional[BlobInventoryPolicyFilter]
        format: Union[str, Format]
        object_type: Union[str, ObjectType]
        schedule: Union[str, Schedule]
        schema_fields: list[str]

        @overload
        def __init__(
                self, 
                *, 
                filters: Optional[BlobInventoryPolicyFilter] = ..., 
                format: Union[str, Format], 
                object_type: Union[str, ObjectType], 
                schedule: Union[str, Schedule], 
                schema_fields: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.BlobInventoryPolicyFilter(_Model):
        blob_types: Optional[list[str]]
        creation_time: Optional[BlobInventoryCreationTime]
        exclude_prefix: Optional[list[str]]
        include_blob_versions: Optional[bool]
        include_deleted: Optional[bool]
        include_snapshots: Optional[bool]
        prefix_match: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                blob_types: Optional[list[str]] = ..., 
                creation_time: Optional[BlobInventoryCreationTime] = ..., 
                exclude_prefix: Optional[list[str]] = ..., 
                include_blob_versions: Optional[bool] = ..., 
                include_deleted: Optional[bool] = ..., 
                include_snapshots: Optional[bool] = ..., 
                prefix_match: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.BlobInventoryPolicyName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEFAULT = "default"


    class azure.mgmt.storage.models.BlobInventoryPolicyProperties(_Model):
        last_modified_time: Optional[datetime]
        policy: BlobInventoryPolicySchema

        @overload
        def __init__(
                self, 
                *, 
                policy: BlobInventoryPolicySchema
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.BlobInventoryPolicyRule(_Model):
        definition: BlobInventoryPolicyDefinition
        destination: str
        enabled: bool
        name: str

        @overload
        def __init__(
                self, 
                *, 
                definition: BlobInventoryPolicyDefinition, 
                destination: str, 
                enabled: bool, 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.BlobInventoryPolicySchema(_Model):
        destination: Optional[str]
        enabled: bool
        rules: list[BlobInventoryPolicyRule]
        type: Union[str, InventoryRuleType]

        @overload
        def __init__(
                self, 
                *, 
                enabled: bool, 
                rules: list[BlobInventoryPolicyRule], 
                type: Union[str, InventoryRuleType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.BlobRestoreParameters(_Model):
        blob_ranges: list[BlobRestoreRange]
        time_to_restore: datetime

        @overload
        def __init__(
                self, 
                *, 
                blob_ranges: list[BlobRestoreRange], 
                time_to_restore: datetime
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.BlobRestoreProgressStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLETE = "Complete"
        FAILED = "Failed"
        IN_PROGRESS = "InProgress"


    class azure.mgmt.storage.models.BlobRestoreRange(_Model):
        end_range: str
        start_range: str

        @overload
        def __init__(
                self, 
                *, 
                end_range: str, 
                start_range: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.BlobRestoreStatus(_Model):
        failure_reason: Optional[str]
        parameters: Optional[BlobRestoreParameters]
        restore_id: Optional[str]
        status: Optional[Union[str, BlobRestoreProgressStatus]]


    class azure.mgmt.storage.models.BlobServiceProperties(ProxyResource):
        blob_service_properties: Optional[BlobServicePropertiesProperties]
        id: str
        name: str
        sku: Optional[Sku]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                blob_service_properties: Optional[BlobServicePropertiesProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.storage.models.BlobServicePropertiesProperties(_Model):
        automatic_snapshot_policy_enabled: Optional[bool]
        change_feed: Optional[ChangeFeed]
        container_delete_retention_policy: Optional[DeleteRetentionPolicy]
        cors: Optional[CorsRules]
        default_service_version: Optional[str]
        delete_retention_policy: Optional[DeleteRetentionPolicy]
        is_versioning_enabled: Optional[bool]
        last_access_time_tracking_policy: Optional[LastAccessTimeTrackingPolicy]
        restore_policy: Optional[RestorePolicyProperties]
        static_website: Optional[StaticWebsite]

        @overload
        def __init__(
                self, 
                *, 
                automatic_snapshot_policy_enabled: Optional[bool] = ..., 
                change_feed: Optional[ChangeFeed] = ..., 
                container_delete_retention_policy: Optional[DeleteRetentionPolicy] = ..., 
                cors: Optional[CorsRules] = ..., 
                default_service_version: Optional[str] = ..., 
                delete_retention_policy: Optional[DeleteRetentionPolicy] = ..., 
                is_versioning_enabled: Optional[bool] = ..., 
                last_access_time_tracking_policy: Optional[LastAccessTimeTrackingPolicy] = ..., 
                restore_policy: Optional[RestorePolicyProperties] = ..., 
                static_website: Optional[StaticWebsite] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.BurstingConstants(_Model):
        burst_floor_iops: Optional[int]
        burst_io_scalar: Optional[float]
        burst_timeframe_seconds: Optional[int]


    class azure.mgmt.storage.models.Bypass(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_SERVICES = "AzureServices"
        LOGGING = "Logging"
        METRICS = "Metrics"
        NONE = "None"


    class azure.mgmt.storage.models.ChangeFeed(_Model):
        enabled: Optional[bool]
        retention_in_days: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ..., 
                retention_in_days: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.CheckNameAvailabilityResult(_Model):
        message: Optional[str]
        name_available: Optional[bool]
        reason: Optional[Union[str, Reason]]


    class azure.mgmt.storage.models.CloudError(_Model):
        error: Optional[CloudErrorBody]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[CloudErrorBody] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.CloudErrorBody(_Model):
        code: Optional[str]
        details: Optional[list[CloudErrorBody]]
        message: Optional[str]
        target: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                details: Optional[list[CloudErrorBody]] = ..., 
                message: Optional[str] = ..., 
                target: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.Connector(TrackedResource):
        id: str
        location: str
        name: str
        properties: StorageConnectorProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: StorageConnectorProperties, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.ConnectorUpdate(TrackedResourceUpdate):
        id: str
        name: str
        properties: Optional[StorageConnectorPropertiesUpdate]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[StorageConnectorPropertiesUpdate] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.ContainerProperties(_Model):
        default_encryption_scope: Optional[str]
        deleted: Optional[bool]
        deleted_time: Optional[datetime]
        deny_encryption_scope_override: Optional[bool]
        enable_nfs_v3_all_squash: Optional[bool]
        enable_nfs_v3_root_squash: Optional[bool]
        has_immutability_policy: Optional[bool]
        has_legal_hold: Optional[bool]
        immutability_policy: Optional[ImmutabilityPolicyProperties]
        immutable_storage_with_versioning: Optional[ImmutableStorageWithVersioning]
        last_modified_time: Optional[datetime]
        lease_duration: Optional[Union[str, LeaseDuration]]
        lease_state: Optional[Union[str, LeaseState]]
        lease_status: Optional[Union[str, LeaseStatus]]
        legal_hold: Optional[LegalHoldProperties]
        metadata: Optional[dict[str, str]]
        public_access: Optional[Union[str, PublicAccess]]
        remaining_retention_days: Optional[int]
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                default_encryption_scope: Optional[str] = ..., 
                deny_encryption_scope_override: Optional[bool] = ..., 
                enable_nfs_v3_all_squash: Optional[bool] = ..., 
                enable_nfs_v3_root_squash: Optional[bool] = ..., 
                immutable_storage_with_versioning: Optional[ImmutableStorageWithVersioning] = ..., 
                metadata: Optional[dict[str, str]] = ..., 
                public_access: Optional[Union[str, PublicAccess]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.CorsRule(_Model):
        allowed_headers: list[str]
        allowed_methods: list[Union[str, AllowedMethods]]
        allowed_origins: list[str]
        exposed_headers: list[str]
        max_age_in_seconds: int

        @overload
        def __init__(
                self, 
                *, 
                allowed_headers: list[str], 
                allowed_methods: list[Union[str, AllowedMethods]], 
                allowed_origins: list[str], 
                exposed_headers: list[str], 
                max_age_in_seconds: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.CorsRules(_Model):
        cors_rules: Optional[list[CorsRule]]

        @overload
        def __init__(
                self, 
                *, 
                cors_rules: Optional[list[CorsRule]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.storage.models.CustomDomain(_Model):
        name: str
        use_sub_domain_name: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                use_sub_domain_name: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.DataShare(TrackedResource):
        id: str
        location: str
        name: str
        properties: StorageDataShareProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: StorageDataShareProperties, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.DataShareConnection(StorageConnectorConnection, discriminator='DataShare'):
        data_share_uri: str
        type: Literal[StorageConnectorConnectionType.DATA_SHARE]

        @overload
        def __init__(
                self, 
                *, 
                data_share_uri: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.DataShareSource(StorageConnectorSource, discriminator='DataShare'):
        auth_properties: StorageConnectorAuthProperties
        connection: StorageConnectorConnection
        type: Literal[StorageConnectorSourceType.DATA_SHARE]

        @overload
        def __init__(
                self, 
                *, 
                auth_properties: StorageConnectorAuthProperties, 
                connection: StorageConnectorConnection
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.DataShareSourceUpdate(StorageConnectorSourceUpdate, discriminator='DataShare'):
        auth_properties: Optional[StorageConnectorAuthPropertiesUpdate]
        type: Literal[StorageConnectorSourceType.DATA_SHARE]

        @overload
        def __init__(
                self, 
                *, 
                auth_properties: Optional[StorageConnectorAuthPropertiesUpdate] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.DataShareUpdate(TrackedResourceUpdate):
        id: str
        name: str
        properties: Optional[StorageDataSharePropertiesUpdate]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[StorageDataSharePropertiesUpdate] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.DateAfterCreation(_Model):
        days_after_creation_greater_than: float
        days_after_last_tier_change_greater_than: Optional[float]

        @overload
        def __init__(
                self, 
                *, 
                days_after_creation_greater_than: float, 
                days_after_last_tier_change_greater_than: Optional[float] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.DateAfterModification(_Model):
        days_after_creation_greater_than: Optional[float]
        days_after_last_access_time_greater_than: Optional[float]
        days_after_last_tier_change_greater_than: Optional[float]
        days_after_modification_greater_than: Optional[float]

        @overload
        def __init__(
                self, 
                *, 
                days_after_creation_greater_than: Optional[float] = ..., 
                days_after_last_access_time_greater_than: Optional[float] = ..., 
                days_after_last_tier_change_greater_than: Optional[float] = ..., 
                days_after_modification_greater_than: Optional[float] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.DefaultAction(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALLOW = "Allow"
        DENY = "Deny"


    class azure.mgmt.storage.models.DefaultSharePermission(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        STORAGE_FILE_DATA_SMB_SHARE_CONTRIBUTOR = "StorageFileDataSmbShareContributor"
        STORAGE_FILE_DATA_SMB_SHARE_ELEVATED_CONTRIBUTOR = "StorageFileDataSmbShareElevatedContributor"
        STORAGE_FILE_DATA_SMB_SHARE_READER = "StorageFileDataSmbShareReader"


    class azure.mgmt.storage.models.DeleteRetentionPolicy(_Model):
        allow_permanent_delete: Optional[bool]
        days: Optional[int]
        enabled: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                allow_permanent_delete: Optional[bool] = ..., 
                days: Optional[int] = ..., 
                enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.DeletedAccount(ProxyResource):
        id: str
        name: str
        properties: Optional[DeletedAccountProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[DeletedAccountProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.storage.models.DeletedAccountProperties(_Model):
        creation_time: Optional[str]
        deletion_time: Optional[str]
        location: Optional[str]
        restore_reference: Optional[str]
        storage_account_resource_id: Optional[str]


    class azure.mgmt.storage.models.DeletedShare(_Model):
        deleted_share_name: str
        deleted_share_version: str

        @overload
        def __init__(
                self, 
                *, 
                deleted_share_name: str, 
                deleted_share_version: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.Dimension(_Model):
        display_name: Optional[str]
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ..., 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.DirectoryServiceOptions(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AADDS = "AADDS"
        AADKERB = "AADKERB"
        AD = "AD"
        NONE = "None"


    class azure.mgmt.storage.models.DnsEndpointType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_DNS_ZONE = "AzureDnsZone"
        STANDARD = "Standard"


    class azure.mgmt.storage.models.DualStackEndpointPreference(_Model):
        publish_ipv6_endpoint: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                publish_ipv6_endpoint: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.EnabledProtocols(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NFS = "NFS"
        SMB = "SMB"


    class azure.mgmt.storage.models.Encryption(_Model):
        encryption_identity: Optional[EncryptionIdentity]
        key_source: Optional[Union[str, KeySource]]
        key_vault_properties: Optional[KeyVaultProperties]
        require_infrastructure_encryption: Optional[bool]
        services: Optional[EncryptionServices]

        @overload
        def __init__(
                self, 
                *, 
                encryption_identity: Optional[EncryptionIdentity] = ..., 
                key_source: Optional[Union[str, KeySource]] = ..., 
                key_vault_properties: Optional[KeyVaultProperties] = ..., 
                require_infrastructure_encryption: Optional[bool] = ..., 
                services: Optional[EncryptionServices] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.EncryptionIdentity(_Model):
        encryption_federated_identity_client_id: Optional[str]
        encryption_user_assigned_identity: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                encryption_federated_identity_client_id: Optional[str] = ..., 
                encryption_user_assigned_identity: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.EncryptionInTransit(_Model):
        required: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                required: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.EncryptionScope(ProxyResource):
        encryption_scope_properties: Optional[EncryptionScopeProperties]
        id: str
        name: str
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                encryption_scope_properties: Optional[EncryptionScopeProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.storage.models.EncryptionScopeKeyVaultProperties(_Model):
        current_versioned_key_identifier: Optional[str]
        key_uri: Optional[str]
        last_key_rotation_timestamp: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                key_uri: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.EncryptionScopeProperties(_Model):
        creation_time: Optional[datetime]
        key_vault_properties: Optional[EncryptionScopeKeyVaultProperties]
        last_modified_time: Optional[datetime]
        require_infrastructure_encryption: Optional[bool]
        source: Optional[Union[str, EncryptionScopeSource]]
        state: Optional[Union[str, EncryptionScopeState]]

        @overload
        def __init__(
                self, 
                *, 
                key_vault_properties: Optional[EncryptionScopeKeyVaultProperties] = ..., 
                require_infrastructure_encryption: Optional[bool] = ..., 
                source: Optional[Union[str, EncryptionScopeSource]] = ..., 
                state: Optional[Union[str, EncryptionScopeState]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.EncryptionScopeSource(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MICROSOFT_KEY_VAULT = "Microsoft.KeyVault"
        MICROSOFT_STORAGE = "Microsoft.Storage"


    class azure.mgmt.storage.models.EncryptionScopeState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.storage.models.EncryptionService(_Model):
        enabled: Optional[bool]
        key_type: Optional[Union[str, KeyType]]
        last_enabled_time: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ..., 
                key_type: Optional[Union[str, KeyType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.EncryptionServices(_Model):
        blob: Optional[EncryptionService]
        file: Optional[EncryptionService]
        queue: Optional[EncryptionService]
        table: Optional[EncryptionService]

        @overload
        def __init__(
                self, 
                *, 
                blob: Optional[EncryptionService] = ..., 
                file: Optional[EncryptionService] = ..., 
                queue: Optional[EncryptionService] = ..., 
                table: Optional[EncryptionService] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.Endpoints(_Model):
        blob: Optional[str]
        dfs: Optional[str]
        file: Optional[str]
        internet_endpoints: Optional[StorageAccountInternetEndpoints]
        ipv6_endpoints: Optional[StorageAccountIpv6Endpoints]
        microsoft_endpoints: Optional[StorageAccountMicrosoftEndpoints]
        queue: Optional[str]
        table: Optional[str]
        web: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                internet_endpoints: Optional[StorageAccountInternetEndpoints] = ..., 
                ipv6_endpoints: Optional[StorageAccountIpv6Endpoints] = ..., 
                microsoft_endpoints: Optional[StorageAccountMicrosoftEndpoints] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.storage.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.storage.models.ErrorResponse(_Model):
        error: Optional[ErrorResponseBody]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorResponseBody] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.ErrorResponseAutoGenerated(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.ErrorResponseBody(_Model):
        code: Optional[str]
        message: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                message: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.ExecutionTarget(_Model):
        exclude_prefix: Optional[list[str]]
        prefix: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                exclude_prefix: Optional[list[str]] = ..., 
                prefix: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.ExecutionTrigger(_Model):
        parameters: TriggerParameters
        type: Union[str, TriggerType]

        @overload
        def __init__(
                self, 
                *, 
                parameters: TriggerParameters, 
                type: Union[str, TriggerType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.ExecutionTriggerUpdate(_Model):
        parameters: Optional[TriggerParametersUpdate]
        type: Optional[Union[str, TriggerType]]

        @overload
        def __init__(
                self, 
                *, 
                parameters: Optional[TriggerParametersUpdate] = ..., 
                type: Optional[Union[str, TriggerType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.ExpirationAction(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BLOCK = "Block"
        LOG = "Log"


    class azure.mgmt.storage.models.ExtendedLocation(_Model):
        name: Optional[str]
        type: Optional[Union[str, ExtendedLocationTypes]]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                type: Optional[Union[str, ExtendedLocationTypes]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.ExtendedLocationTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EDGE_ZONE = "EdgeZone"


    class azure.mgmt.storage.models.FileServiceItems(_Model):
        value: Optional[list[FileServiceProperties]]


    class azure.mgmt.storage.models.FileServiceProperties(ProxyResource):
        file_service_properties: Optional[FileServicePropertiesProperties]
        id: str
        name: str
        sku: Optional[Sku]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                file_service_properties: Optional[FileServicePropertiesProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.storage.models.FileServicePropertiesProperties(_Model):
        cors: Optional[CorsRules]
        protocol_settings: Optional[ProtocolSettings]
        share_delete_retention_policy: Optional[DeleteRetentionPolicy]

        @overload
        def __init__(
                self, 
                *, 
                cors: Optional[CorsRules] = ..., 
                protocol_settings: Optional[ProtocolSettings] = ..., 
                share_delete_retention_policy: Optional[DeleteRetentionPolicy] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.FileServiceUsage(ProxyResource):
        id: str
        name: str
        properties: Optional[FileServiceUsageProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[FileServiceUsageProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.FileServiceUsageProperties(_Model):
        bursting_constants: Optional[BurstingConstants]
        file_share_limits: Optional[FileShareLimits]
        file_share_recommendations: Optional[FileShareRecommendations]
        storage_account_limits: Optional[AccountLimits]
        storage_account_usage: Optional[AccountUsage]


    class azure.mgmt.storage.models.FileShare(ProxyResource):
        etag: Optional[str]
        file_share_properties: Optional[FileShareProperties]
        id: str
        name: str
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                file_share_properties: Optional[FileShareProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.storage.models.FileShareItem(AzureEntityResource):
        etag: str
        id: str
        name: str
        properties: Optional[FileShareProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[FileShareProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.storage.models.FileShareLimits(_Model):
        guardrail_bandwidth_scalar: Optional[float]
        guardrail_io_scalar: Optional[float]
        max_provisioned_bandwidth_mi_b_per_sec: Optional[int]
        max_provisioned_iops: Optional[int]
        max_provisioned_storage_gi_b: Optional[int]
        min_provisioned_bandwidth_mi_b_per_sec: Optional[int]
        min_provisioned_iops: Optional[int]
        min_provisioned_storage_gi_b: Optional[int]


    class azure.mgmt.storage.models.FileShareProperties(_Model):
        access_tier: Optional[Union[str, ShareAccessTier]]
        access_tier_change_time: Optional[datetime]
        access_tier_status: Optional[str]
        deleted: Optional[bool]
        deleted_time: Optional[datetime]
        enabled_protocols: Optional[Union[str, EnabledProtocols]]
        file_share_paid_bursting: Optional[FileSharePropertiesFileSharePaidBursting]
        included_burst_iops: Optional[int]
        last_modified_time: Optional[datetime]
        lease_duration: Optional[Union[str, LeaseDuration]]
        lease_state: Optional[Union[str, LeaseState]]
        lease_status: Optional[Union[str, LeaseStatus]]
        max_burst_credits_for_iops: Optional[int]
        metadata: Optional[dict[str, str]]
        next_allowed_provisioned_bandwidth_downgrade_time: Optional[datetime]
        next_allowed_provisioned_iops_downgrade_time: Optional[datetime]
        next_allowed_quota_downgrade_time: Optional[datetime]
        provisioned_bandwidth_mibps: Optional[int]
        provisioned_iops: Optional[int]
        remaining_retention_days: Optional[int]
        root_squash: Optional[Union[str, RootSquashType]]
        share_quota: Optional[int]
        share_usage_bytes: Optional[int]
        signed_identifiers: Optional[list[SignedIdentifier]]
        snapshot_time: Optional[datetime]
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                access_tier: Optional[Union[str, ShareAccessTier]] = ..., 
                enabled_protocols: Optional[Union[str, EnabledProtocols]] = ..., 
                file_share_paid_bursting: Optional[FileSharePropertiesFileSharePaidBursting] = ..., 
                metadata: Optional[dict[str, str]] = ..., 
                provisioned_bandwidth_mibps: Optional[int] = ..., 
                provisioned_iops: Optional[int] = ..., 
                root_squash: Optional[Union[str, RootSquashType]] = ..., 
                share_quota: Optional[int] = ..., 
                signed_identifiers: Optional[list[SignedIdentifier]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.FileSharePropertiesFileSharePaidBursting(_Model):
        paid_bursting_enabled: Optional[bool]
        paid_bursting_max_bandwidth_mibps: Optional[int]
        paid_bursting_max_iops: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                paid_bursting_enabled: Optional[bool] = ..., 
                paid_bursting_max_bandwidth_mibps: Optional[int] = ..., 
                paid_bursting_max_iops: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.FileShareRecommendations(_Model):
        bandwidth_scalar: Optional[float]
        base_bandwidth_mi_b_per_sec: Optional[int]
        base_iops: Optional[int]
        io_scalar: Optional[float]


    class azure.mgmt.storage.models.Format(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CSV = "Csv"
        PARQUET = "Parquet"


    class azure.mgmt.storage.models.GeoPriorityReplicationStatus(_Model):
        is_blob_enabled: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                is_blob_enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.GeoReplicationStats(_Model):
        can_failover: Optional[bool]
        can_planned_failover: Optional[bool]
        last_sync_time: Optional[datetime]
        post_failover_redundancy: Optional[Union[str, PostFailoverRedundancy]]
        post_planned_failover_redundancy: Optional[Union[str, PostPlannedFailoverRedundancy]]
        status: Optional[Union[str, GeoReplicationStatus]]


    class azure.mgmt.storage.models.GeoReplicationStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BOOTSTRAP = "Bootstrap"
        LIVE = "Live"
        UNAVAILABLE = "Unavailable"


    class azure.mgmt.storage.models.HttpProtocol(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HTTPS = "https"
        HTTPS_HTTP = "https,http"


    class azure.mgmt.storage.models.IPRule(_Model):
        action: Optional[Literal["Allow"]]
        ip_address_or_range: str

        @overload
        def __init__(
                self, 
                *, 
                action: Optional[Literal[Allow]] = ..., 
                ip_address_or_range: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.Identity(_Model):
        principal_id: Optional[str]
        tenant_id: Optional[str]
        type: Union[str, IdentityType]
        user_assigned_identities: Optional[dict[str, UserAssignedIdentity]]

        @overload
        def __init__(
                self, 
                *, 
                type: Union[str, IdentityType], 
                user_assigned_identities: Optional[dict[str, UserAssignedIdentity]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.IdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        SYSTEM_ASSIGNED_USER_ASSIGNED = "SystemAssigned,UserAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.storage.models.ImmutabilityPolicy(ProxyResource):
        etag: Optional[str]
        id: str
        name: str
        properties: ImmutabilityPolicyProperty
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: ImmutabilityPolicyProperty
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.storage.models.ImmutabilityPolicyProperties(_Model):
        etag: Optional[str]
        properties: Optional[ImmutabilityPolicyProperty]
        update_history: Optional[list[UpdateHistoryProperty]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ImmutabilityPolicyProperty] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.storage.models.ImmutabilityPolicyProperty(_Model):
        allow_protected_append_writes: Optional[bool]
        allow_protected_append_writes_all: Optional[bool]
        immutability_period_since_creation_in_days: Optional[int]
        state: Optional[Union[str, ImmutabilityPolicyState]]

        @overload
        def __init__(
                self, 
                *, 
                allow_protected_append_writes: Optional[bool] = ..., 
                allow_protected_append_writes_all: Optional[bool] = ..., 
                immutability_period_since_creation_in_days: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.ImmutabilityPolicyState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LOCKED = "Locked"
        UNLOCKED = "Unlocked"


    class azure.mgmt.storage.models.ImmutabilityPolicyUpdateType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EXTEND = "extend"
        LOCK = "lock"
        PUT = "put"


    class azure.mgmt.storage.models.ImmutableStorageAccount(_Model):
        enabled: Optional[bool]
        immutability_policy: Optional[AccountImmutabilityPolicyProperties]

        @overload
        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ..., 
                immutability_policy: Optional[AccountImmutabilityPolicyProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.ImmutableStorageWithVersioning(_Model):
        enabled: Optional[bool]
        migration_state: Optional[Union[str, MigrationState]]
        time_stamp: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.IntervalUnit(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DAYS = "Days"


    class azure.mgmt.storage.models.InventoryRuleType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INVENTORY = "Inventory"


    class azure.mgmt.storage.models.IssueType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONFIGURATION_PROPAGATION_FAILURE = "ConfigurationPropagationFailure"
        UNKNOWN = "Unknown"


    class azure.mgmt.storage.models.KeyCreationTime(_Model):
        key1: Optional[datetime]
        key2: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                key1: Optional[datetime] = ..., 
                key2: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.KeyPermission(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FULL = "Full"
        READ = "Read"


    class azure.mgmt.storage.models.KeyPolicy(_Model):
        key_expiration_period_in_days: int

        @overload
        def __init__(
                self, 
                *, 
                key_expiration_period_in_days: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.KeySource(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MICROSOFT_KEYVAULT = "Microsoft.Keyvault"
        MICROSOFT_STORAGE = "Microsoft.Storage"


    class azure.mgmt.storage.models.KeyType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCOUNT = "Account"
        SERVICE = "Service"


    class azure.mgmt.storage.models.KeyVaultProperties(_Model):
        current_versioned_key_expiration_timestamp: Optional[datetime]
        current_versioned_key_identifier: Optional[str]
        key_name: Optional[str]
        key_vault_uri: Optional[str]
        key_version: Optional[str]
        last_key_rotation_timestamp: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                key_name: Optional[str] = ..., 
                key_vault_uri: Optional[str] = ..., 
                key_version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.Kind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BLOB_STORAGE = "BlobStorage"
        BLOCK_BLOB_STORAGE = "BlockBlobStorage"
        FILE_STORAGE = "FileStorage"
        STORAGE = "Storage"
        STORAGE_V2 = "StorageV2"


    class azure.mgmt.storage.models.LargeFileSharesState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.storage.models.LastAccessTimeTrackingPolicy(_Model):
        blob_type: Optional[list[str]]
        enable: bool
        name: Optional[Union[str, Name]]
        tracking_granularity_in_days: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                blob_type: Optional[list[str]] = ..., 
                enable: bool, 
                name: Optional[Union[str, Name]] = ..., 
                tracking_granularity_in_days: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.LeaseContainerRequest(_Model):
        action: Union[str, LeaseContainerRequestAction]
        break_period: Optional[int]
        lease_duration: Optional[int]
        lease_id: Optional[str]
        proposed_lease_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                action: Union[str, LeaseContainerRequestAction], 
                break_period: Optional[int] = ..., 
                lease_duration: Optional[int] = ..., 
                lease_id: Optional[str] = ..., 
                proposed_lease_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.LeaseContainerRequestAction(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACQUIRE = "Acquire"
        BREAK = "Break"
        CHANGE = "Change"
        RELEASE = "Release"
        RENEW = "Renew"


    class azure.mgmt.storage.models.LeaseContainerResponse(_Model):
        lease_id: Optional[str]
        lease_time_seconds: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                lease_id: Optional[str] = ..., 
                lease_time_seconds: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.LeaseDuration(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FIXED = "Fixed"
        INFINITE = "Infinite"


    class azure.mgmt.storage.models.LeaseShareAction(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACQUIRE = "Acquire"
        BREAK = "Break"
        CHANGE = "Change"
        RELEASE = "Release"
        RENEW = "Renew"


    class azure.mgmt.storage.models.LeaseShareRequest(_Model):
        action: Union[str, LeaseShareAction]
        break_period: Optional[int]
        lease_duration: Optional[int]
        lease_id: Optional[str]
        proposed_lease_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                action: Union[str, LeaseShareAction], 
                break_period: Optional[int] = ..., 
                lease_duration: Optional[int] = ..., 
                lease_id: Optional[str] = ..., 
                proposed_lease_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.LeaseShareResponse(_Model):
        lease_id: Optional[str]
        lease_time_seconds: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                lease_id: Optional[str] = ..., 
                lease_time_seconds: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.LeaseState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVAILABLE = "Available"
        BREAKING = "Breaking"
        BROKEN = "Broken"
        EXPIRED = "Expired"
        LEASED = "Leased"


    class azure.mgmt.storage.models.LeaseStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LOCKED = "Locked"
        UNLOCKED = "Unlocked"


    class azure.mgmt.storage.models.LegalHold(_Model):
        allow_protected_append_writes_all: Optional[bool]
        has_legal_hold: Optional[bool]
        tags: list[str]

        @overload
        def __init__(
                self, 
                *, 
                allow_protected_append_writes_all: Optional[bool] = ..., 
                tags: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.LegalHoldProperties(_Model):
        has_legal_hold: Optional[bool]
        protected_append_writes_history: Optional[ProtectedAppendWritesHistory]
        tags: Optional[list[TagProperty]]

        @overload
        def __init__(
                self, 
                *, 
                protected_append_writes_history: Optional[ProtectedAppendWritesHistory] = ..., 
                tags: Optional[list[TagProperty]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.ListAccountSasResponse(_Model):
        account_sas_token: Optional[str]


    class azure.mgmt.storage.models.ListContainerItem(AzureEntityResource):
        etag: str
        id: str
        name: str
        properties: Optional[ContainerProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ContainerProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.storage.models.ListContainersInclude(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DELETED = "deleted"


    class azure.mgmt.storage.models.ListEncryptionScopesInclude(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALL = "All"
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.storage.models.ListLocalUserIncludeParam(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NFSV3 = "nfsv3"


    class azure.mgmt.storage.models.ListQueue(ResourceAutoGenerated):
        id: str
        name: str
        queue_properties: Optional[ListQueueProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                queue_properties: Optional[ListQueueProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.storage.models.ListQueueProperties(_Model):
        metadata: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                metadata: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.ListQueueServices(_Model):
        value: Optional[list[QueueServiceProperties]]


    class azure.mgmt.storage.models.ListServiceSasResponse(_Model):
        service_sas_token: Optional[str]


    class azure.mgmt.storage.models.ListTableServices(_Model):
        value: Optional[list[TableServiceProperties]]


    class azure.mgmt.storage.models.LocalUser(ProxyResource):
        id: str
        name: str
        properties: Optional[LocalUserProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[LocalUserProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.storage.models.LocalUserKeys(_Model):
        shared_key: Optional[str]
        ssh_authorized_keys: Optional[list[SshPublicKey]]

        @overload
        def __init__(
                self, 
                *, 
                ssh_authorized_keys: Optional[list[SshPublicKey]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.LocalUserProperties(_Model):
        allow_acl_authorization: Optional[bool]
        extended_groups: Optional[list[int]]
        group_id: Optional[int]
        has_shared_key: Optional[bool]
        has_ssh_key: Optional[bool]
        has_ssh_password: Optional[bool]
        home_directory: Optional[str]
        is_nf_sv3_enabled: Optional[bool]
        permission_scopes: Optional[list[PermissionScope]]
        sid: Optional[str]
        ssh_authorized_keys: Optional[list[SshPublicKey]]
        user_id: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                allow_acl_authorization: Optional[bool] = ..., 
                extended_groups: Optional[list[int]] = ..., 
                group_id: Optional[int] = ..., 
                has_shared_key: Optional[bool] = ..., 
                has_ssh_key: Optional[bool] = ..., 
                has_ssh_password: Optional[bool] = ..., 
                home_directory: Optional[str] = ..., 
                is_nf_sv3_enabled: Optional[bool] = ..., 
                permission_scopes: Optional[list[PermissionScope]] = ..., 
                ssh_authorized_keys: Optional[list[SshPublicKey]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.LocalUserRegeneratePasswordResult(_Model):
        ssh_password: Optional[str]


    class azure.mgmt.storage.models.ManagedIdentityAuthProperties(StorageConnectorAuthProperties, discriminator='ManagedIdentity'):
        identity_resource_id: Optional[str]
        type: Literal[StorageConnectorAuthType.MANAGED_IDENTITY]

        @overload
        def __init__(
                self, 
                *, 
                identity_resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.ManagedIdentityAuthPropertiesUpdate(StorageConnectorAuthPropertiesUpdate, discriminator='ManagedIdentity'):
        identity_resource_id: Optional[str]
        type: Literal[StorageConnectorAuthType.MANAGED_IDENTITY]

        @overload
        def __init__(
                self, 
                *, 
                identity_resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.ManagementPolicy(ProxyResource):
        id: str
        name: str
        properties: Optional[ManagementPolicyProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ManagementPolicyProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.storage.models.ManagementPolicyAction(_Model):
        base_blob: Optional[ManagementPolicyBaseBlob]
        snapshot: Optional[ManagementPolicySnapShot]
        version: Optional[ManagementPolicyVersion]

        @overload
        def __init__(
                self, 
                *, 
                base_blob: Optional[ManagementPolicyBaseBlob] = ..., 
                snapshot: Optional[ManagementPolicySnapShot] = ..., 
                version: Optional[ManagementPolicyVersion] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.ManagementPolicyBaseBlob(_Model):
        delete: Optional[DateAfterModification]
        enable_auto_tier_to_hot_from_cool: Optional[bool]
        tier_to_archive: Optional[DateAfterModification]
        tier_to_cold: Optional[DateAfterModification]
        tier_to_cool: Optional[DateAfterModification]
        tier_to_hot: Optional[DateAfterModification]

        @overload
        def __init__(
                self, 
                *, 
                delete: Optional[DateAfterModification] = ..., 
                enable_auto_tier_to_hot_from_cool: Optional[bool] = ..., 
                tier_to_archive: Optional[DateAfterModification] = ..., 
                tier_to_cold: Optional[DateAfterModification] = ..., 
                tier_to_cool: Optional[DateAfterModification] = ..., 
                tier_to_hot: Optional[DateAfterModification] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.ManagementPolicyDefinition(_Model):
        actions: ManagementPolicyAction
        filters: Optional[ManagementPolicyFilter]

        @overload
        def __init__(
                self, 
                *, 
                actions: ManagementPolicyAction, 
                filters: Optional[ManagementPolicyFilter] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.ManagementPolicyFilter(_Model):
        blob_index_match: Optional[list[TagFilter]]
        blob_types: list[str]
        prefix_match: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                blob_index_match: Optional[list[TagFilter]] = ..., 
                blob_types: list[str], 
                prefix_match: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.ManagementPolicyName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEFAULT = "default"


    class azure.mgmt.storage.models.ManagementPolicyProperties(_Model):
        last_modified_time: Optional[datetime]
        policy: ManagementPolicySchema

        @overload
        def __init__(
                self, 
                *, 
                policy: ManagementPolicySchema
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.ManagementPolicyRule(_Model):
        definition: ManagementPolicyDefinition
        enabled: Optional[bool]
        name: str
        type: Union[str, RuleType]

        @overload
        def __init__(
                self, 
                *, 
                definition: ManagementPolicyDefinition, 
                enabled: Optional[bool] = ..., 
                name: str, 
                type: Union[str, RuleType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.ManagementPolicySchema(_Model):
        rules: list[ManagementPolicyRule]

        @overload
        def __init__(
                self, 
                *, 
                rules: list[ManagementPolicyRule]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.ManagementPolicySnapShot(_Model):
        delete: Optional[DateAfterCreation]
        tier_to_archive: Optional[DateAfterCreation]
        tier_to_cold: Optional[DateAfterCreation]
        tier_to_cool: Optional[DateAfterCreation]
        tier_to_hot: Optional[DateAfterCreation]

        @overload
        def __init__(
                self, 
                *, 
                delete: Optional[DateAfterCreation] = ..., 
                tier_to_archive: Optional[DateAfterCreation] = ..., 
                tier_to_cold: Optional[DateAfterCreation] = ..., 
                tier_to_cool: Optional[DateAfterCreation] = ..., 
                tier_to_hot: Optional[DateAfterCreation] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.ManagementPolicyVersion(_Model):
        delete: Optional[DateAfterCreation]
        tier_to_archive: Optional[DateAfterCreation]
        tier_to_cold: Optional[DateAfterCreation]
        tier_to_cool: Optional[DateAfterCreation]
        tier_to_hot: Optional[DateAfterCreation]

        @overload
        def __init__(
                self, 
                *, 
                delete: Optional[DateAfterCreation] = ..., 
                tier_to_archive: Optional[DateAfterCreation] = ..., 
                tier_to_cold: Optional[DateAfterCreation] = ..., 
                tier_to_cool: Optional[DateAfterCreation] = ..., 
                tier_to_hot: Optional[DateAfterCreation] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.MetricSpecification(_Model):
        aggregation_type: Optional[str]
        category: Optional[str]
        dimensions: Optional[list[Dimension]]
        display_description: Optional[str]
        display_name: Optional[str]
        fill_gap_with_zero: Optional[bool]
        name: Optional[str]
        resource_id_dimension_name_override: Optional[str]
        unit: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                aggregation_type: Optional[str] = ..., 
                category: Optional[str] = ..., 
                dimensions: Optional[list[Dimension]] = ..., 
                display_description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                fill_gap_with_zero: Optional[bool] = ..., 
                name: Optional[str] = ..., 
                resource_id_dimension_name_override: Optional[str] = ..., 
                unit: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.MetricsEmitted(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONTAINER_BLOB_COUNT = "ContainerBlobCount"
        CONTAINER_USED_SIZE = "ContainerUsedSize"


    class azure.mgmt.storage.models.MigrationName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEFAULT = "default"


    class azure.mgmt.storage.models.MigrationState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLETED = "Completed"
        IN_PROGRESS = "InProgress"


    class azure.mgmt.storage.models.MigrationStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLETE = "Complete"
        FAILED = "Failed"
        INVALID = "Invalid"
        IN_PROGRESS = "InProgress"
        SUBMITTED_FOR_CONVERSION = "SubmittedForConversion"


    class azure.mgmt.storage.models.MinimumTlsVersion(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        TLS1_0 = "TLS1_0"
        TLS1_1 = "TLS1_1"
        TLS1_2 = "TLS1_2"
        TLS1_3 = "TLS1_3"


    class azure.mgmt.storage.models.Multichannel(_Model):
        enabled: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.Name(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCESS_TIME_TRACKING = "AccessTimeTracking"


    class azure.mgmt.storage.models.NativeDataSharingProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.storage.models.NetworkRuleSet(_Model):
        bypass: Optional[Union[str, Bypass]]
        default_action: Union[str, DefaultAction]
        ip_rules: Optional[list[IPRule]]
        ipv6_rules: Optional[list[IPRule]]
        resource_access_rules: Optional[list[ResourceAccessRule]]
        virtual_network_rules: Optional[list[VirtualNetworkRule]]

        @overload
        def __init__(
                self, 
                *, 
                bypass: Optional[Union[str, Bypass]] = ..., 
                default_action: Union[str, DefaultAction], 
                ip_rules: Optional[list[IPRule]] = ..., 
                ipv6_rules: Optional[list[IPRule]] = ..., 
                resource_access_rules: Optional[list[ResourceAccessRule]] = ..., 
                virtual_network_rules: Optional[list[VirtualNetworkRule]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.NetworkSecurityPerimeter(_Model):
        id: Optional[str]
        location: Optional[str]
        perimeter_guid: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                location: Optional[str] = ..., 
                perimeter_guid: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.NetworkSecurityPerimeterConfiguration(ProxyResource):
        id: str
        name: str
        properties: Optional[NetworkSecurityPerimeterConfigurationProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[NetworkSecurityPerimeterConfigurationProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.storage.models.NetworkSecurityPerimeterConfigurationProperties(_Model):
        network_security_perimeter: Optional[NetworkSecurityPerimeter]
        profile: Optional[NetworkSecurityPerimeterConfigurationPropertiesProfile]
        provisioning_issues: Optional[list[ProvisioningIssue]]
        provisioning_state: Optional[Union[str, NetworkSecurityPerimeterConfigurationProvisioningState]]
        resource_association: Optional[NetworkSecurityPerimeterConfigurationPropertiesResourceAssociation]


    class azure.mgmt.storage.models.NetworkSecurityPerimeterConfigurationPropertiesProfile(_Model):
        access_rules: Optional[list[NspAccessRule]]
        access_rules_version: Optional[float]
        diagnostic_settings_version: Optional[float]
        enabled_log_categories: Optional[list[str]]
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                access_rules: Optional[list[NspAccessRule]] = ..., 
                access_rules_version: Optional[float] = ..., 
                diagnostic_settings_version: Optional[float] = ..., 
                enabled_log_categories: Optional[list[str]] = ..., 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.NetworkSecurityPerimeterConfigurationPropertiesResourceAssociation(_Model):
        access_mode: Optional[Union[str, ResourceAssociationAccessMode]]
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                access_mode: Optional[Union[str, ResourceAssociationAccessMode]] = ..., 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.NetworkSecurityPerimeterConfigurationProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CANCELED = "Canceled"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.storage.models.NfsSetting(_Model):
        encryption_in_transit: Optional[EncryptionInTransit]

        @overload
        def __init__(
                self, 
                *, 
                encryption_in_transit: Optional[EncryptionInTransit] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.NspAccessRule(_Model):
        name: Optional[str]
        properties: Optional[NspAccessRuleProperties]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.NspAccessRuleDirection(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INBOUND = "Inbound"
        OUTBOUND = "Outbound"


    class azure.mgmt.storage.models.NspAccessRuleProperties(_Model):
        address_prefixes: Optional[list[str]]
        direction: Optional[Union[str, NspAccessRuleDirection]]
        fully_qualified_domain_names: Optional[list[str]]
        network_security_perimeters: Optional[list[NetworkSecurityPerimeter]]
        subscriptions: Optional[list[NspAccessRulePropertiesSubscriptionsItem]]

        @overload
        def __init__(
                self, 
                *, 
                address_prefixes: Optional[list[str]] = ..., 
                direction: Optional[Union[str, NspAccessRuleDirection]] = ..., 
                subscriptions: Optional[list[NspAccessRulePropertiesSubscriptionsItem]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.NspAccessRulePropertiesSubscriptionsItem(_Model):
        id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.ObjectReplicationPolicy(ProxyResource):
        id: str
        name: str
        properties: Optional[ObjectReplicationPolicyProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ObjectReplicationPolicyProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.storage.models.ObjectReplicationPolicyFilter(_Model):
        min_creation_time: Optional[str]
        prefix_match: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                min_creation_time: Optional[str] = ..., 
                prefix_match: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.ObjectReplicationPolicyProperties(_Model):
        destination_account: str
        enabled_time: Optional[datetime]
        metrics: Optional[ObjectReplicationPolicyPropertiesMetrics]
        policy_id: Optional[str]
        priority_replication: Optional[ObjectReplicationPolicyPropertiesPriorityReplication]
        rules: Optional[list[ObjectReplicationPolicyRule]]
        source_account: str
        tags_replication: Optional[ObjectReplicationPolicyPropertiesTagsReplication]

        @overload
        def __init__(
                self, 
                *, 
                destination_account: str, 
                metrics: Optional[ObjectReplicationPolicyPropertiesMetrics] = ..., 
                priority_replication: Optional[ObjectReplicationPolicyPropertiesPriorityReplication] = ..., 
                rules: Optional[list[ObjectReplicationPolicyRule]] = ..., 
                source_account: str, 
                tags_replication: Optional[ObjectReplicationPolicyPropertiesTagsReplication] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.ObjectReplicationPolicyPropertiesMetrics(_Model):
        enabled: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.ObjectReplicationPolicyPropertiesPriorityReplication(_Model):
        enabled: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.ObjectReplicationPolicyPropertiesTagsReplication(_Model):
        enabled: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.ObjectReplicationPolicyRule(_Model):
        destination_container: str
        filters: Optional[ObjectReplicationPolicyFilter]
        rule_id: Optional[str]
        source_container: str

        @overload
        def __init__(
                self, 
                *, 
                destination_container: str, 
                filters: Optional[ObjectReplicationPolicyFilter] = ..., 
                rule_id: Optional[str] = ..., 
                source_container: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.ObjectType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BLOB = "Blob"
        CONTAINER = "Container"


    class azure.mgmt.storage.models.Operation(_Model):
        display: Optional[OperationDisplay]
        name: Optional[str]
        operation_properties: Optional[OperationProperties]
        origin: Optional[str]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                display: Optional[OperationDisplay] = ..., 
                name: Optional[str] = ..., 
                operation_properties: Optional[OperationProperties] = ..., 
                origin: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.storage.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                operation: Optional[str] = ..., 
                provider: Optional[str] = ..., 
                resource: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.OperationProperties(_Model):
        service_specification: Optional[ServiceSpecification]

        @overload
        def __init__(
                self, 
                *, 
                service_specification: Optional[ServiceSpecification] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.PermissionScope(_Model):
        permissions: str
        resource_name: str
        service: str

        @overload
        def __init__(
                self, 
                *, 
                permissions: str, 
                resource_name: str, 
                service: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.Permissions(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        A = "a"
        C = "c"
        D = "d"
        L = "l"
        P = "p"
        R = "r"
        U = "u"
        W = "w"


    class azure.mgmt.storage.models.Placement(_Model):
        zone_placement_policy: Optional[Union[str, ZonePlacementPolicy]]

        @overload
        def __init__(
                self, 
                *, 
                zone_placement_policy: Optional[Union[str, ZonePlacementPolicy]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.PostFailoverRedundancy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        STANDARD_LRS = "Standard_LRS"
        STANDARD_ZRS = "Standard_ZRS"


    class azure.mgmt.storage.models.PostPlannedFailoverRedundancy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        STANDARD_GRS = "Standard_GRS"
        STANDARD_GZRS = "Standard_GZRS"
        STANDARD_RAGRS = "Standard_RAGRS"
        STANDARD_RAGZRS = "Standard_RAGZRS"


    class azure.mgmt.storage.models.PrivateEndpoint(_Model):
        id: Optional[str]


    class azure.mgmt.storage.models.PrivateEndpointConnection(ProxyResource):
        id: str
        name: str
        properties: Optional[PrivateEndpointConnectionProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[PrivateEndpointConnectionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.storage.models.PrivateEndpointConnectionProperties(_Model):
        private_endpoint: Optional[PrivateEndpoint]
        private_link_service_connection_state: PrivateLinkServiceConnectionState
        provisioning_state: Optional[Union[str, PrivateEndpointConnectionProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                private_endpoint: Optional[PrivateEndpoint] = ..., 
                private_link_service_connection_state: PrivateLinkServiceConnectionState
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.PrivateEndpointConnectionProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.storage.models.PrivateEndpointServiceConnectionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPROVED = "Approved"
        PENDING = "Pending"
        REJECTED = "Rejected"


    class azure.mgmt.storage.models.PrivateLinkResource(ResourceAutoGenerated):
        id: str
        name: str
        properties: Optional[PrivateLinkResourceProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[PrivateLinkResourceProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.storage.models.PrivateLinkResourceListResult(_Model):
        value: Optional[list[PrivateLinkResource]]

        @overload
        def __init__(
                self, 
                *, 
                value: Optional[list[PrivateLinkResource]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.PrivateLinkResourceProperties(_Model):
        group_id: Optional[str]
        required_members: Optional[list[str]]
        required_zone_names: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                required_zone_names: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.PrivateLinkServiceConnectionState(_Model):
        action_required: Optional[str]
        description: Optional[str]
        status: Optional[Union[str, PrivateEndpointServiceConnectionStatus]]

        @overload
        def __init__(
                self, 
                *, 
                action_required: Optional[str] = ..., 
                description: Optional[str] = ..., 
                status: Optional[Union[str, PrivateEndpointServiceConnectionStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.ProtectedAppendWritesHistory(_Model):
        allow_protected_append_writes_all: Optional[bool]
        timestamp: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                allow_protected_append_writes_all: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.ProtocolSettings(_Model):
        nfs: Optional[NfsSetting]
        smb: Optional[SmbSetting]

        @overload
        def __init__(
                self, 
                *, 
                nfs: Optional[NfsSetting] = ..., 
                smb: Optional[SmbSetting] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.ProvisioningIssue(_Model):
        name: Optional[str]
        properties: Optional[ProvisioningIssueProperties]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.ProvisioningIssueProperties(_Model):
        description: Optional[str]
        issue_type: Optional[Union[str, IssueType]]
        severity: Optional[Union[str, Severity]]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                issue_type: Optional[Union[str, IssueType]] = ..., 
                severity: Optional[Union[str, Severity]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREATING = "Creating"
        RESOLVING_DNS = "ResolvingDNS"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.storage.models.ProxyResource(ResourceAutoGenerated):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.storage.models.PublicAccess(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BLOB = "Blob"
        CONTAINER = "Container"
        NONE = "None"


    class azure.mgmt.storage.models.PublicNetworkAccess(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"
        SECURED_BY_PERIMETER = "SecuredByPerimeter"


    class azure.mgmt.storage.models.QueueProperties(_Model):
        approximate_message_count: Optional[int]
        metadata: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                metadata: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.QueueServiceProperties(ProxyResource):
        id: str
        name: str
        queue_service_properties: Optional[QueueServicePropertiesProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                queue_service_properties: Optional[QueueServicePropertiesProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.storage.models.QueueServicePropertiesProperties(_Model):
        cors: Optional[CorsRules]

        @overload
        def __init__(
                self, 
                *, 
                cors: Optional[CorsRules] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.Reason(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCOUNT_NAME_INVALID = "AccountNameInvalid"
        ALREADY_EXISTS = "AlreadyExists"


    class azure.mgmt.storage.models.ReasonCode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NOT_AVAILABLE_FOR_SUBSCRIPTION = "NotAvailableForSubscription"
        QUOTA_ID = "QuotaId"


    class azure.mgmt.storage.models.ResourceAccessRule(_Model):
        resource_id: Optional[str]
        tenant_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                resource_id: Optional[str] = ..., 
                tenant_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.ResourceAssociationAccessMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUDIT = "Audit"
        ENFORCED = "Enforced"
        LEARNING = "Learning"


    class azure.mgmt.storage.models.ResourceAutoGenerated(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.storage.models.RestorePolicyProperties(_Model):
        days: Optional[int]
        enabled: bool
        last_enabled_time: Optional[datetime]
        min_restore_time: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                days: Optional[int] = ..., 
                enabled: bool
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.Restriction(_Model):
        reason_code: Optional[Union[str, ReasonCode]]
        type: Optional[str]
        values_property: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                reason_code: Optional[Union[str, ReasonCode]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.RootSquashType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALL_SQUASH = "AllSquash"
        NO_ROOT_SQUASH = "NoRootSquash"
        ROOT_SQUASH = "RootSquash"


    class azure.mgmt.storage.models.RoutingChoice(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNET_ROUTING = "InternetRouting"
        MICROSOFT_ROUTING = "MicrosoftRouting"


    class azure.mgmt.storage.models.RoutingPreference(_Model):
        publish_internet_endpoints: Optional[bool]
        publish_microsoft_endpoints: Optional[bool]
        routing_choice: Optional[Union[str, RoutingChoice]]

        @overload
        def __init__(
                self, 
                *, 
                publish_internet_endpoints: Optional[bool] = ..., 
                publish_microsoft_endpoints: Optional[bool] = ..., 
                routing_choice: Optional[Union[str, RoutingChoice]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.RuleType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LIFECYCLE = "Lifecycle"


    class azure.mgmt.storage.models.RunResult(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.storage.models.RunStatusEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FINISHED = "Finished"
        IN_PROGRESS = "InProgress"


    class azure.mgmt.storage.models.SKUCapability(_Model):
        name: Optional[str]
        value: Optional[str]


    class azure.mgmt.storage.models.SasPolicy(_Model):
        expiration_action: Union[str, ExpirationAction]
        sas_expiration_period: str

        @overload
        def __init__(
                self, 
                *, 
                expiration_action: Union[str, ExpirationAction], 
                sas_expiration_period: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.Schedule(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DAILY = "Daily"
        WEEKLY = "Weekly"


    class azure.mgmt.storage.models.ServiceSasParameters(_Model):
        cache_control: Optional[str]
        canonicalized_resource: str
        content_disposition: Optional[str]
        content_encoding: Optional[str]
        content_language: Optional[str]
        content_type: Optional[str]
        identifier: Optional[str]
        ip_address_or_range: Optional[str]
        key_to_sign: Optional[str]
        partition_key_end: Optional[str]
        partition_key_start: Optional[str]
        permissions: Optional[Union[str, Permissions]]
        protocols: Optional[Union[str, HttpProtocol]]
        resource: Optional[Union[str, SignedResource]]
        row_key_end: Optional[str]
        row_key_start: Optional[str]
        shared_access_expiry_time: Optional[datetime]
        shared_access_start_time: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                cache_control: Optional[str] = ..., 
                canonicalized_resource: str, 
                content_disposition: Optional[str] = ..., 
                content_encoding: Optional[str] = ..., 
                content_language: Optional[str] = ..., 
                content_type: Optional[str] = ..., 
                identifier: Optional[str] = ..., 
                ip_address_or_range: Optional[str] = ..., 
                key_to_sign: Optional[str] = ..., 
                partition_key_end: Optional[str] = ..., 
                partition_key_start: Optional[str] = ..., 
                permissions: Optional[Union[str, Permissions]] = ..., 
                protocols: Optional[Union[str, HttpProtocol]] = ..., 
                resource: Optional[Union[str, SignedResource]] = ..., 
                row_key_end: Optional[str] = ..., 
                row_key_start: Optional[str] = ..., 
                shared_access_expiry_time: Optional[datetime] = ..., 
                shared_access_start_time: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.ServiceSharedKeyAccessProperties(_Model):
        enabled: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.ServiceSpecification(_Model):
        metric_specifications: Optional[list[MetricSpecification]]

        @overload
        def __init__(
                self, 
                *, 
                metric_specifications: Optional[list[MetricSpecification]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.Services(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        B = "b"
        F = "f"
        Q = "q"
        T = "t"


    class azure.mgmt.storage.models.Severity(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ERROR = "Error"
        WARNING = "Warning"


    class azure.mgmt.storage.models.ShareAccessTier(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COOL = "Cool"
        HOT = "Hot"
        PREMIUM = "Premium"
        TRANSACTION_OPTIMIZED = "TransactionOptimized"


    class azure.mgmt.storage.models.SignedIdentifier(_Model):
        access_policy: Optional[AccessPolicy]
        id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                access_policy: Optional[AccessPolicy] = ..., 
                id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.SignedResource(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        B = "b"
        C = "c"
        F = "f"
        S = "s"


    class azure.mgmt.storage.models.SignedResourceTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        C = "c"
        O = "o"
        S = "s"


    class azure.mgmt.storage.models.Sku(_Model):
        name: Union[str, SkuName]
        tier: Optional[Union[str, SkuTier]]

        @overload
        def __init__(
                self, 
                *, 
                name: Union[str, SkuName]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.SkuConversionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAILED = "Failed"
        IN_PROGRESS = "InProgress"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.storage.models.SkuInformation(_Model):
        capabilities: Optional[list[SKUCapability]]
        kind: Optional[Union[str, Kind]]
        location_info: Optional[list[SkuInformationLocationInfoItem]]
        locations: Optional[list[str]]
        name: Union[str, SkuName]
        resource_type: Optional[str]
        restrictions: Optional[list[Restriction]]
        tier: Optional[Union[str, SkuTier]]

        @overload
        def __init__(
                self, 
                *, 
                location_info: Optional[list[SkuInformationLocationInfoItem]] = ..., 
                name: Union[str, SkuName], 
                restrictions: Optional[list[Restriction]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.SkuInformationLocationInfoItem(_Model):
        location: Optional[str]
        zones: Optional[list[str]]


    class azure.mgmt.storage.models.SkuName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PREMIUM_LRS = "Premium_LRS"
        PREMIUM_V2_LRS = "PremiumV2_LRS"
        PREMIUM_V2_ZRS = "PremiumV2_ZRS"
        PREMIUM_ZRS = "Premium_ZRS"
        STANDARD_GRS = "Standard_GRS"
        STANDARD_GZRS = "Standard_GZRS"
        STANDARD_LRS = "Standard_LRS"
        STANDARD_RAGRS = "Standard_RAGRS"
        STANDARD_RAGZRS = "Standard_RAGZRS"
        STANDARD_V2_GRS = "StandardV2_GRS"
        STANDARD_V2_GZRS = "StandardV2_GZRS"
        STANDARD_V2_LRS = "StandardV2_LRS"
        STANDARD_V2_ZRS = "StandardV2_ZRS"
        STANDARD_ZRS = "Standard_ZRS"


    class azure.mgmt.storage.models.SkuTier(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PREMIUM = "Premium"
        STANDARD = "Standard"


    class azure.mgmt.storage.models.SmbOAuthSettings(_Model):
        is_smb_o_auth_enabled: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                is_smb_o_auth_enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.SmbSetting(_Model):
        authentication_methods: Optional[str]
        channel_encryption: Optional[str]
        encryption_in_transit: Optional[EncryptionInTransit]
        kerberos_ticket_encryption: Optional[str]
        multichannel: Optional[Multichannel]
        versions: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                authentication_methods: Optional[str] = ..., 
                channel_encryption: Optional[str] = ..., 
                encryption_in_transit: Optional[EncryptionInTransit] = ..., 
                kerberos_ticket_encryption: Optional[str] = ..., 
                multichannel: Optional[Multichannel] = ..., 
                versions: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.SshPublicKey(_Model):
        description: Optional[str]
        key: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                key: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.State(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEPROVISIONING = "Deprovisioning"
        FAILED = "Failed"
        NETWORK_SOURCE_DELETED = "NetworkSourceDeleted"
        PROVISIONING = "Provisioning"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.storage.models.StaticWebsite(_Model):
        default_index_document_path: Optional[str]
        enabled: bool
        error_document404_path: Optional[str]
        index_document: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                default_index_document_path: Optional[str] = ..., 
                enabled: bool, 
                error_document404_path: Optional[str] = ..., 
                index_document: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.StorageAccount(TrackedResource):
        extended_location: Optional[ExtendedLocation]
        id: str
        identity: Optional[Identity]
        kind: Optional[Union[str, Kind]]
        location: str
        name: str
        placement: Optional[Placement]
        properties: Optional[StorageAccountProperties]
        sku: Optional[Sku]
        system_data: SystemData
        tags: dict[str, str]
        type: str
        zones: Optional[list[str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                extended_location: Optional[ExtendedLocation] = ..., 
                identity: Optional[Identity] = ..., 
                location: str, 
                placement: Optional[Placement] = ..., 
                properties: Optional[StorageAccountProperties] = ..., 
                tags: Optional[dict[str, str]] = ..., 
                zones: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.storage.models.StorageAccountCheckNameAvailabilityParameters(_Model):
        name: str
        type: Literal["Storage/storageAccounts"]

        @overload
        def __init__(
                self, 
                *, 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.StorageAccountCreateParameters(_Model):
        extended_location: Optional[ExtendedLocation]
        identity: Optional[Identity]
        kind: Union[str, Kind]
        location: str
        placement: Optional[Placement]
        properties: Optional[StorageAccountPropertiesCreateParameters]
        sku: Sku
        tags: Optional[dict[str, str]]
        zones: Optional[list[str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                extended_location: Optional[ExtendedLocation] = ..., 
                identity: Optional[Identity] = ..., 
                kind: Union[str, Kind], 
                location: str, 
                placement: Optional[Placement] = ..., 
                properties: Optional[StorageAccountPropertiesCreateParameters] = ..., 
                sku: Sku, 
                tags: Optional[dict[str, str]] = ..., 
                zones: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.storage.models.StorageAccountExpand(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BLOB_RESTORE_STATUS = "blobRestoreStatus"
        GEO_REPLICATION_STATS = "geoReplicationStats"


    class azure.mgmt.storage.models.StorageAccountInternetEndpoints(_Model):
        blob: Optional[str]
        dfs: Optional[str]
        file: Optional[str]
        web: Optional[str]


    class azure.mgmt.storage.models.StorageAccountIpv6Endpoints(_Model):
        blob: Optional[str]
        dfs: Optional[str]
        file: Optional[str]
        internet_endpoints: Optional[StorageAccountInternetEndpoints]
        microsoft_endpoints: Optional[StorageAccountMicrosoftEndpoints]
        queue: Optional[str]
        table: Optional[str]
        web: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                internet_endpoints: Optional[StorageAccountInternetEndpoints] = ..., 
                microsoft_endpoints: Optional[StorageAccountMicrosoftEndpoints] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.StorageAccountKey(_Model):
        creation_time: Optional[datetime]
        key_name: Optional[str]
        permissions: Optional[Union[str, KeyPermission]]
        value: Optional[str]


    class azure.mgmt.storage.models.StorageAccountListKeysResult(_Model):
        keys_property: Optional[list[StorageAccountKey]]


    class azure.mgmt.storage.models.StorageAccountMicrosoftEndpoints(_Model):
        blob: Optional[str]
        dfs: Optional[str]
        file: Optional[str]
        queue: Optional[str]
        table: Optional[str]
        web: Optional[str]


    class azure.mgmt.storage.models.StorageAccountMigration(ProxyResource):
        id: str
        name: str
        storage_account_migration_details: StorageAccountMigrationProperties
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                storage_account_migration_details: StorageAccountMigrationProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.storage.models.StorageAccountMigrationProperties(_Model):
        migration_failed_detailed_reason: Optional[str]
        migration_failed_reason: Optional[str]
        migration_status: Optional[Union[str, MigrationStatus]]
        target_sku_name: Union[str, SkuName]

        @overload
        def __init__(
                self, 
                *, 
                target_sku_name: Union[str, SkuName]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.StorageAccountProperties(_Model):
        access_tier: Optional[Union[str, AccessTier]]
        account_migration_in_progress: Optional[bool]
        allow_blob_public_access: Optional[bool]
        allow_cross_tenant_replication: Optional[bool]
        allow_shared_key_access: Optional[bool]
        allow_shared_key_access_for_services: Optional[StorageAccountSharedKeyAccessProperties]
        allowed_copy_scope: Optional[Union[str, AllowedCopyScope]]
        azure_files_identity_based_authentication: Optional[AzureFilesIdentityBasedAuthentication]
        blob_restore_status: Optional[BlobRestoreStatus]
        creation_time: Optional[datetime]
        custom_domain: Optional[CustomDomain]
        data_collaboration_policy_properties: Optional[StorageDataCollaborationPolicyProperties]
        default_to_o_auth_authentication: Optional[bool]
        dns_endpoint_type: Optional[Union[str, DnsEndpointType]]
        dual_stack_endpoint_preference: Optional[DualStackEndpointPreference]
        enable_extended_groups: Optional[bool]
        enable_https_traffic_only: Optional[bool]
        enable_nfs_v3: Optional[bool]
        encryption: Optional[Encryption]
        failover_in_progress: Optional[bool]
        geo_priority_replication_status: Optional[GeoPriorityReplicationStatus]
        geo_replication_stats: Optional[GeoReplicationStats]
        immutable_storage_with_versioning: Optional[ImmutableStorageAccount]
        is_hns_enabled: Optional[bool]
        is_local_user_enabled: Optional[bool]
        is_sftp_enabled: Optional[bool]
        is_sku_conversion_blocked: Optional[bool]
        key_creation_time: Optional[KeyCreationTime]
        key_policy: Optional[KeyPolicy]
        large_file_shares_state: Optional[Union[str, LargeFileSharesState]]
        last_geo_failover_time: Optional[datetime]
        minimum_tls_version: Optional[Union[str, MinimumTlsVersion]]
        network_rule_set: Optional[NetworkRuleSet]
        primary_endpoints: Optional[Endpoints]
        primary_location: Optional[str]
        private_endpoint_connections: Optional[list[PrivateEndpointConnection]]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        public_network_access: Optional[Union[str, PublicNetworkAccess]]
        routing_preference: Optional[RoutingPreference]
        sas_policy: Optional[SasPolicy]
        secondary_endpoints: Optional[Endpoints]
        secondary_location: Optional[str]
        status_of_primary: Optional[Union[str, AccountStatus]]
        status_of_secondary: Optional[Union[str, AccountStatus]]
        storage_account_sku_conversion_status: Optional[StorageAccountSkuConversionStatus]

        @overload
        def __init__(
                self, 
                *, 
                allow_blob_public_access: Optional[bool] = ..., 
                allow_cross_tenant_replication: Optional[bool] = ..., 
                allow_shared_key_access: Optional[bool] = ..., 
                allow_shared_key_access_for_services: Optional[StorageAccountSharedKeyAccessProperties] = ..., 
                allowed_copy_scope: Optional[Union[str, AllowedCopyScope]] = ..., 
                azure_files_identity_based_authentication: Optional[AzureFilesIdentityBasedAuthentication] = ..., 
                data_collaboration_policy_properties: Optional[StorageDataCollaborationPolicyProperties] = ..., 
                default_to_o_auth_authentication: Optional[bool] = ..., 
                dns_endpoint_type: Optional[Union[str, DnsEndpointType]] = ..., 
                dual_stack_endpoint_preference: Optional[DualStackEndpointPreference] = ..., 
                enable_extended_groups: Optional[bool] = ..., 
                enable_https_traffic_only: Optional[bool] = ..., 
                enable_nfs_v3: Optional[bool] = ..., 
                geo_priority_replication_status: Optional[GeoPriorityReplicationStatus] = ..., 
                immutable_storage_with_versioning: Optional[ImmutableStorageAccount] = ..., 
                is_hns_enabled: Optional[bool] = ..., 
                is_local_user_enabled: Optional[bool] = ..., 
                is_sftp_enabled: Optional[bool] = ..., 
                large_file_shares_state: Optional[Union[str, LargeFileSharesState]] = ..., 
                minimum_tls_version: Optional[Union[str, MinimumTlsVersion]] = ..., 
                public_network_access: Optional[Union[str, PublicNetworkAccess]] = ..., 
                routing_preference: Optional[RoutingPreference] = ..., 
                storage_account_sku_conversion_status: Optional[StorageAccountSkuConversionStatus] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.StorageAccountPropertiesCreateParameters(_Model):
        access_tier: Optional[Union[str, AccessTier]]
        allow_blob_public_access: Optional[bool]
        allow_cross_tenant_replication: Optional[bool]
        allow_shared_key_access: Optional[bool]
        allow_shared_key_access_for_services: Optional[StorageAccountSharedKeyAccessProperties]
        allowed_copy_scope: Optional[Union[str, AllowedCopyScope]]
        azure_files_identity_based_authentication: Optional[AzureFilesIdentityBasedAuthentication]
        custom_domain: Optional[CustomDomain]
        data_collaboration_policy_properties: Optional[StorageDataCollaborationPolicyProperties]
        default_to_o_auth_authentication: Optional[bool]
        dns_endpoint_type: Optional[Union[str, DnsEndpointType]]
        dual_stack_endpoint_preference: Optional[DualStackEndpointPreference]
        enable_extended_groups: Optional[bool]
        enable_https_traffic_only: Optional[bool]
        enable_nfs_v3: Optional[bool]
        encryption: Optional[Encryption]
        geo_priority_replication_status: Optional[GeoPriorityReplicationStatus]
        immutable_storage_with_versioning: Optional[ImmutableStorageAccount]
        is_hns_enabled: Optional[bool]
        is_local_user_enabled: Optional[bool]
        is_sftp_enabled: Optional[bool]
        key_policy: Optional[KeyPolicy]
        large_file_shares_state: Optional[Union[str, LargeFileSharesState]]
        minimum_tls_version: Optional[Union[str, MinimumTlsVersion]]
        network_rule_set: Optional[NetworkRuleSet]
        public_network_access: Optional[Union[str, PublicNetworkAccess]]
        routing_preference: Optional[RoutingPreference]
        sas_policy: Optional[SasPolicy]

        @overload
        def __init__(
                self, 
                *, 
                access_tier: Optional[Union[str, AccessTier]] = ..., 
                allow_blob_public_access: Optional[bool] = ..., 
                allow_cross_tenant_replication: Optional[bool] = ..., 
                allow_shared_key_access: Optional[bool] = ..., 
                allow_shared_key_access_for_services: Optional[StorageAccountSharedKeyAccessProperties] = ..., 
                allowed_copy_scope: Optional[Union[str, AllowedCopyScope]] = ..., 
                azure_files_identity_based_authentication: Optional[AzureFilesIdentityBasedAuthentication] = ..., 
                custom_domain: Optional[CustomDomain] = ..., 
                data_collaboration_policy_properties: Optional[StorageDataCollaborationPolicyProperties] = ..., 
                default_to_o_auth_authentication: Optional[bool] = ..., 
                dns_endpoint_type: Optional[Union[str, DnsEndpointType]] = ..., 
                dual_stack_endpoint_preference: Optional[DualStackEndpointPreference] = ..., 
                enable_extended_groups: Optional[bool] = ..., 
                enable_https_traffic_only: Optional[bool] = ..., 
                enable_nfs_v3: Optional[bool] = ..., 
                encryption: Optional[Encryption] = ..., 
                geo_priority_replication_status: Optional[GeoPriorityReplicationStatus] = ..., 
                immutable_storage_with_versioning: Optional[ImmutableStorageAccount] = ..., 
                is_hns_enabled: Optional[bool] = ..., 
                is_local_user_enabled: Optional[bool] = ..., 
                is_sftp_enabled: Optional[bool] = ..., 
                key_policy: Optional[KeyPolicy] = ..., 
                large_file_shares_state: Optional[Union[str, LargeFileSharesState]] = ..., 
                minimum_tls_version: Optional[Union[str, MinimumTlsVersion]] = ..., 
                network_rule_set: Optional[NetworkRuleSet] = ..., 
                public_network_access: Optional[Union[str, PublicNetworkAccess]] = ..., 
                routing_preference: Optional[RoutingPreference] = ..., 
                sas_policy: Optional[SasPolicy] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.StorageAccountPropertiesUpdateParameters(_Model):
        access_tier: Optional[Union[str, AccessTier]]
        allow_blob_public_access: Optional[bool]
        allow_cross_tenant_replication: Optional[bool]
        allow_shared_key_access: Optional[bool]
        allow_shared_key_access_for_services: Optional[StorageAccountSharedKeyAccessProperties]
        allowed_copy_scope: Optional[Union[str, AllowedCopyScope]]
        azure_files_identity_based_authentication: Optional[AzureFilesIdentityBasedAuthentication]
        custom_domain: Optional[CustomDomain]
        data_collaboration_policy_properties: Optional[StorageDataCollaborationPolicyProperties]
        default_to_o_auth_authentication: Optional[bool]
        dns_endpoint_type: Optional[Union[str, DnsEndpointType]]
        dual_stack_endpoint_preference: Optional[DualStackEndpointPreference]
        enable_extended_groups: Optional[bool]
        enable_https_traffic_only: Optional[bool]
        encryption: Optional[Encryption]
        geo_priority_replication_status: Optional[GeoPriorityReplicationStatus]
        immutable_storage_with_versioning: Optional[ImmutableStorageAccount]
        is_local_user_enabled: Optional[bool]
        is_sftp_enabled: Optional[bool]
        key_policy: Optional[KeyPolicy]
        large_file_shares_state: Optional[Union[str, LargeFileSharesState]]
        minimum_tls_version: Optional[Union[str, MinimumTlsVersion]]
        network_rule_set: Optional[NetworkRuleSet]
        public_network_access: Optional[Union[str, PublicNetworkAccess]]
        routing_preference: Optional[RoutingPreference]
        sas_policy: Optional[SasPolicy]

        @overload
        def __init__(
                self, 
                *, 
                access_tier: Optional[Union[str, AccessTier]] = ..., 
                allow_blob_public_access: Optional[bool] = ..., 
                allow_cross_tenant_replication: Optional[bool] = ..., 
                allow_shared_key_access: Optional[bool] = ..., 
                allow_shared_key_access_for_services: Optional[StorageAccountSharedKeyAccessProperties] = ..., 
                allowed_copy_scope: Optional[Union[str, AllowedCopyScope]] = ..., 
                azure_files_identity_based_authentication: Optional[AzureFilesIdentityBasedAuthentication] = ..., 
                custom_domain: Optional[CustomDomain] = ..., 
                data_collaboration_policy_properties: Optional[StorageDataCollaborationPolicyProperties] = ..., 
                default_to_o_auth_authentication: Optional[bool] = ..., 
                dns_endpoint_type: Optional[Union[str, DnsEndpointType]] = ..., 
                dual_stack_endpoint_preference: Optional[DualStackEndpointPreference] = ..., 
                enable_extended_groups: Optional[bool] = ..., 
                enable_https_traffic_only: Optional[bool] = ..., 
                encryption: Optional[Encryption] = ..., 
                geo_priority_replication_status: Optional[GeoPriorityReplicationStatus] = ..., 
                immutable_storage_with_versioning: Optional[ImmutableStorageAccount] = ..., 
                is_local_user_enabled: Optional[bool] = ..., 
                is_sftp_enabled: Optional[bool] = ..., 
                key_policy: Optional[KeyPolicy] = ..., 
                large_file_shares_state: Optional[Union[str, LargeFileSharesState]] = ..., 
                minimum_tls_version: Optional[Union[str, MinimumTlsVersion]] = ..., 
                network_rule_set: Optional[NetworkRuleSet] = ..., 
                public_network_access: Optional[Union[str, PublicNetworkAccess]] = ..., 
                routing_preference: Optional[RoutingPreference] = ..., 
                sas_policy: Optional[SasPolicy] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.StorageAccountRegenerateKeyParameters(_Model):
        key_name: str

        @overload
        def __init__(
                self, 
                *, 
                key_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.StorageAccountSharedKeyAccessProperties(_Model):
        blob: Optional[ServiceSharedKeyAccessProperties]
        file: Optional[ServiceSharedKeyAccessProperties]
        queue: Optional[ServiceSharedKeyAccessProperties]
        table: Optional[ServiceSharedKeyAccessProperties]

        @overload
        def __init__(
                self, 
                *, 
                blob: Optional[ServiceSharedKeyAccessProperties] = ..., 
                file: Optional[ServiceSharedKeyAccessProperties] = ..., 
                queue: Optional[ServiceSharedKeyAccessProperties] = ..., 
                table: Optional[ServiceSharedKeyAccessProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.StorageAccountSkuConversionStatus(_Model):
        end_time: Optional[str]
        sku_conversion_status: Optional[Union[str, SkuConversionStatus]]
        start_time: Optional[str]
        target_sku_name: Optional[Union[str, SkuName]]

        @overload
        def __init__(
                self, 
                *, 
                target_sku_name: Optional[Union[str, SkuName]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.StorageAccountUpdateParameters(_Model):
        identity: Optional[Identity]
        kind: Optional[Union[str, Kind]]
        placement: Optional[Placement]
        properties: Optional[StorageAccountPropertiesUpdateParameters]
        sku: Optional[Sku]
        tags: Optional[dict[str, str]]
        zones: Optional[list[str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[Identity] = ..., 
                kind: Optional[Union[str, Kind]] = ..., 
                placement: Optional[Placement] = ..., 
                properties: Optional[StorageAccountPropertiesUpdateParameters] = ..., 
                sku: Optional[Sku] = ..., 
                tags: Optional[dict[str, str]] = ..., 
                zones: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.storage.models.StorageConnectorAuthProperties(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.StorageConnectorAuthPropertiesUpdate(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.StorageConnectorAuthType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MANAGED_IDENTITY = "ManagedIdentity"


    class azure.mgmt.storage.models.StorageConnectorConnection(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.StorageConnectorConnectionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DATA_SHARE = "DataShare"


    class azure.mgmt.storage.models.StorageConnectorDataSourceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_DATA_SHARE = "Azure_DataShare"


    class azure.mgmt.storage.models.StorageConnectorProperties(_Model):
        creation_time: Optional[str]
        data_source_type: Union[str, StorageConnectorDataSourceType]
        description: Optional[str]
        provisioning_state: Optional[Union[str, NativeDataSharingProvisioningState]]
        source: StorageConnectorSource
        state: Optional[Union[str, StorageConnectorState]]
        test_connection: Optional[bool]
        unique_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                data_source_type: Union[str, StorageConnectorDataSourceType], 
                description: Optional[str] = ..., 
                source: StorageConnectorSource, 
                state: Optional[Union[str, StorageConnectorState]] = ..., 
                test_connection: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.StorageConnectorPropertiesUpdate(_Model):
        description: Optional[str]
        source: Optional[StorageConnectorSourceUpdate]
        state: Optional[Union[str, StorageConnectorState]]
        test_connection: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                source: Optional[StorageConnectorSourceUpdate] = ..., 
                state: Optional[Union[str, StorageConnectorState]] = ..., 
                test_connection: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.StorageConnectorSource(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.StorageConnectorSourceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DATA_SHARE = "DataShare"


    class azure.mgmt.storage.models.StorageConnectorSourceUpdate(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.StorageConnectorState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        INACTIVE = "Inactive"


    class azure.mgmt.storage.models.StorageDataCollaborationPolicyProperties(_Model):
        allow_cross_tenant_data_sharing: Optional[bool]
        allow_storage_connectors: Optional[bool]
        allow_storage_data_shares: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                allow_cross_tenant_data_sharing: Optional[bool] = ..., 
                allow_storage_connectors: Optional[bool] = ..., 
                allow_storage_data_shares: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.StorageDataShareAccessPolicy(_Model):
        permission: Union[str, StorageDataShareAccessPolicyPermission]
        principal_id: str
        tenant_id: str

        @overload
        def __init__(
                self, 
                *, 
                permission: Union[str, StorageDataShareAccessPolicyPermission], 
                principal_id: str, 
                tenant_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.StorageDataShareAccessPolicyPermission(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        READ = "Read"


    class azure.mgmt.storage.models.StorageDataShareAsset(_Model):
        asset_path: str
        display_name: str

        @overload
        def __init__(
                self, 
                *, 
                asset_path: str, 
                display_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.StorageDataShareProperties(_Model):
        access_policies: list[StorageDataShareAccessPolicy]
        assets: list[StorageDataShareAsset]
        data_share_identifier: Optional[str]
        data_share_uri: Optional[str]
        description: Optional[str]
        provisioning_state: Optional[Union[str, NativeDataSharingProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                access_policies: list[StorageDataShareAccessPolicy], 
                assets: list[StorageDataShareAsset], 
                description: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.StorageDataSharePropertiesUpdate(_Model):
        access_policies: Optional[list[StorageDataShareAccessPolicy]]
        assets: Optional[list[StorageDataShareAsset]]
        description: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                access_policies: Optional[list[StorageDataShareAccessPolicy]] = ..., 
                assets: Optional[list[StorageDataShareAsset]] = ..., 
                description: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.StorageQueue(ProxyResource):
        id: str
        name: str
        queue_properties: Optional[QueueProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                queue_properties: Optional[QueueProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.storage.models.StorageTaskAssignment(ProxyResource):
        id: str
        name: str
        properties: Optional[StorageTaskAssignmentProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[StorageTaskAssignmentProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.StorageTaskAssignmentExecutionContext(_Model):
        target: Optional[ExecutionTarget]
        trigger: ExecutionTrigger

        @overload
        def __init__(
                self, 
                *, 
                target: Optional[ExecutionTarget] = ..., 
                trigger: ExecutionTrigger
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.StorageTaskAssignmentProperties(_Model):
        description: str
        enabled: bool
        execution_context: StorageTaskAssignmentExecutionContext
        provisioning_state: Optional[Union[str, StorageTaskAssignmentProvisioningState]]
        report: StorageTaskAssignmentReport
        run_status: Optional[StorageTaskReportProperties]
        task_id: str

        @overload
        def __init__(
                self, 
                *, 
                description: str, 
                enabled: bool, 
                execution_context: StorageTaskAssignmentExecutionContext, 
                report: StorageTaskAssignmentReport, 
                run_status: Optional[StorageTaskReportProperties] = ..., 
                task_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.StorageTaskAssignmentProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        VALIDATE_SUBSCRIPTION_QUOTA_BEGIN = "ValidateSubscriptionQuotaBegin"
        VALIDATE_SUBSCRIPTION_QUOTA_END = "ValidateSubscriptionQuotaEnd"


    class azure.mgmt.storage.models.StorageTaskAssignmentReport(_Model):
        prefix: str

        @overload
        def __init__(
                self, 
                *, 
                prefix: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.StorageTaskAssignmentUpdateExecutionContext(_Model):
        target: Optional[ExecutionTarget]
        trigger: Optional[ExecutionTriggerUpdate]

        @overload
        def __init__(
                self, 
                *, 
                target: Optional[ExecutionTarget] = ..., 
                trigger: Optional[ExecutionTriggerUpdate] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.StorageTaskAssignmentUpdateParameters(_Model):
        properties: Optional[StorageTaskAssignmentUpdateProperties]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[StorageTaskAssignmentUpdateProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.StorageTaskAssignmentUpdateProperties(_Model):
        description: Optional[str]
        enabled: Optional[bool]
        execution_context: Optional[StorageTaskAssignmentUpdateExecutionContext]
        provisioning_state: Optional[Union[str, StorageTaskAssignmentProvisioningState]]
        report: Optional[StorageTaskAssignmentUpdateReport]
        run_status: Optional[StorageTaskReportProperties]
        task_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                enabled: Optional[bool] = ..., 
                execution_context: Optional[StorageTaskAssignmentUpdateExecutionContext] = ..., 
                report: Optional[StorageTaskAssignmentUpdateReport] = ..., 
                run_status: Optional[StorageTaskReportProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.StorageTaskAssignmentUpdateReport(_Model):
        prefix: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                prefix: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.StorageTaskReportInstance(ProxyResource):
        id: str
        name: str
        properties: Optional[StorageTaskReportProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[StorageTaskReportProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.StorageTaskReportProperties(_Model):
        finish_time: Optional[str]
        object_failed_count: Optional[str]
        objects_operated_on_count: Optional[str]
        objects_succeeded_count: Optional[str]
        objects_targeted_count: Optional[str]
        run_result: Optional[Union[str, RunResult]]
        run_status_enum: Optional[Union[str, RunStatusEnum]]
        run_status_error: Optional[str]
        start_time: Optional[str]
        storage_account_id: Optional[str]
        summary_report_path: Optional[str]
        task_assignment_id: Optional[str]
        task_id: Optional[str]
        task_version: Optional[str]


    class azure.mgmt.storage.models.SystemData(_Model):
        created_at: Optional[datetime]
        created_by: Optional[str]
        created_by_type: Optional[Union[str, CreatedByType]]
        last_modified_at: Optional[datetime]
        last_modified_by: Optional[str]
        last_modified_by_type: Optional[Union[str, CreatedByType]]

        @overload
        def __init__(
                self, 
                *, 
                created_at: Optional[datetime] = ..., 
                created_by: Optional[str] = ..., 
                created_by_type: Optional[Union[str, CreatedByType]] = ..., 
                last_modified_at: Optional[datetime] = ..., 
                last_modified_by: Optional[str] = ..., 
                last_modified_by_type: Optional[Union[str, CreatedByType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.Table(ProxyResource):
        id: str
        name: str
        system_data: SystemData
        table_properties: Optional[TableProperties]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                table_properties: Optional[TableProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.storage.models.TableAccessPolicy(_Model):
        expiry_time: Optional[datetime]
        permission: str
        start_time: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                expiry_time: Optional[datetime] = ..., 
                permission: str, 
                start_time: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.TableProperties(_Model):
        signed_identifiers: Optional[list[TableSignedIdentifier]]
        table_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                signed_identifiers: Optional[list[TableSignedIdentifier]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.TableServiceProperties(ProxyResource):
        id: str
        name: str
        system_data: SystemData
        table_service_properties: Optional[TableServicePropertiesProperties]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                table_service_properties: Optional[TableServicePropertiesProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.storage.models.TableServicePropertiesProperties(_Model):
        cors: Optional[CorsRules]

        @overload
        def __init__(
                self, 
                *, 
                cors: Optional[CorsRules] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.TableSignedIdentifier(_Model):
        access_policy: Optional[TableAccessPolicy]
        id: str

        @overload
        def __init__(
                self, 
                *, 
                access_policy: Optional[TableAccessPolicy] = ..., 
                id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.TagFilter(_Model):
        name: str
        op: str
        value: str

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                op: str, 
                value: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.TagProperty(_Model):
        object_identifier: Optional[str]
        tag: Optional[str]
        tenant_id: Optional[str]
        timestamp: Optional[datetime]
        upn: Optional[str]


    class azure.mgmt.storage.models.TestConnectionResponse(_Model):
        storage_connector_error_message: Optional[str]
        storage_connector_method_name: str
        storage_connector_request_id: str

        @overload
        def __init__(
                self, 
                *, 
                storage_connector_error_message: Optional[str] = ..., 
                storage_connector_method_name: str, 
                storage_connector_request_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.TestExistingConnectionRequest(_Model):
        unique_id: str

        @overload
        def __init__(
                self, 
                *, 
                unique_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.TrackedResource(ResourceAutoGenerated):
        id: str
        location: str
        name: str
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.TrackedResourceUpdate(ResourceAutoGenerated):
        id: str
        name: str
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.TriggerParameters(_Model):
        end_by: Optional[datetime]
        interval: Optional[int]
        interval_unit: Optional[Union[str, IntervalUnit]]
        start_from: Optional[datetime]
        start_on: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                end_by: Optional[datetime] = ..., 
                interval: Optional[int] = ..., 
                interval_unit: Optional[Union[str, IntervalUnit]] = ..., 
                start_from: Optional[datetime] = ..., 
                start_on: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.TriggerParametersUpdate(_Model):
        end_by: Optional[datetime]
        interval: Optional[int]
        interval_unit: Optional[Union[str, IntervalUnit]]
        start_from: Optional[datetime]
        start_on: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                end_by: Optional[datetime] = ..., 
                interval: Optional[int] = ..., 
                interval_unit: Optional[Union[str, IntervalUnit]] = ..., 
                start_from: Optional[datetime] = ..., 
                start_on: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.TriggerType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MOCK_RUN = "MockRun"
        ON_SCHEDULE = "OnSchedule"
        RUN_ONCE = "RunOnce"


    class azure.mgmt.storage.models.UpdateHistoryProperty(_Model):
        allow_protected_append_writes: Optional[bool]
        allow_protected_append_writes_all: Optional[bool]
        immutability_period_since_creation_in_days: Optional[int]
        object_identifier: Optional[str]
        tenant_id: Optional[str]
        timestamp: Optional[datetime]
        update_property: Optional[Union[str, ImmutabilityPolicyUpdateType]]
        upn: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                allow_protected_append_writes: Optional[bool] = ..., 
                allow_protected_append_writes_all: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.Usage(_Model):
        current_value: Optional[int]
        limit: Optional[int]
        name: Optional[UsageName]
        unit: Optional[Union[str, UsageUnit]]


    class azure.mgmt.storage.models.UsageName(_Model):
        localized_value: Optional[str]
        value: Optional[str]


    class azure.mgmt.storage.models.UsageUnit(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BYTES = "Bytes"
        BYTES_PER_SECOND = "BytesPerSecond"
        COUNT = "Count"
        COUNTS_PER_SECOND = "CountsPerSecond"
        PERCENT = "Percent"
        SECONDS = "Seconds"


    class azure.mgmt.storage.models.UserAssignedIdentity(_Model):
        client_id: Optional[str]
        principal_id: Optional[str]


    class azure.mgmt.storage.models.VirtualNetworkRule(_Model):
        action: Optional[Literal["Allow"]]
        state: Optional[Union[str, State]]
        virtual_network_resource_id: str

        @overload
        def __init__(
                self, 
                *, 
                action: Optional[Literal[Allow]] = ..., 
                state: Optional[Union[str, State]] = ..., 
                virtual_network_resource_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storage.models.ZonePlacementPolicy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ANY = "Any"
        NONE = "None"


namespace azure.mgmt.storage.operations

    class azure.mgmt.storage.operations.AdvancedPlatformMetricsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                advanced_platform_metrics_rule_type: Union[str, AdvancedPlatformMetricsRuleType], 
                resource: AdvancedPlatformMetricsRule, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AdvancedPlatformMetricsRule: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                advanced_platform_metrics_rule_type: Union[str, AdvancedPlatformMetricsRuleType], 
                resource: AdvancedPlatformMetricsRule, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AdvancedPlatformMetricsRule: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                advanced_platform_metrics_rule_type: Union[str, AdvancedPlatformMetricsRuleType], 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AdvancedPlatformMetricsRule: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-04-01', params_added_on={'2026-04-01': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'advanced_platform_metrics_rule_type']}, api_versions_list=['2026-04-01'])
        def delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                advanced_platform_metrics_rule_type: Union[str, AdvancedPlatformMetricsRuleType], 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-04-01', params_added_on={'2026-04-01': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'advanced_platform_metrics_rule_type', 'accept']}, api_versions_list=['2026-04-01'])
        def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                advanced_platform_metrics_rule_type: Union[str, AdvancedPlatformMetricsRuleType], 
                **kwargs: Any
            ) -> AdvancedPlatformMetricsRule: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-04-01', params_added_on={'2026-04-01': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'accept']}, api_versions_list=['2026-04-01'])
        def list(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> ItemPaged[AdvancedPlatformMetricsRule]: ...


    class azure.mgmt.storage.operations.BlobContainersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_object_level_worm(
                self, 
                resource_group_name: str, 
                account_name: str, 
                container_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def clear_legal_hold(
                self, 
                resource_group_name: str, 
                account_name: str, 
                container_name: str, 
                legal_hold: LegalHold, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LegalHold: ...

        @overload
        def clear_legal_hold(
                self, 
                resource_group_name: str, 
                account_name: str, 
                container_name: str, 
                legal_hold: LegalHold, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LegalHold: ...

        @overload
        def clear_legal_hold(
                self, 
                resource_group_name: str, 
                account_name: str, 
                container_name: str, 
                legal_hold: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LegalHold: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                container_name: str, 
                blob_container: BlobContainer, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BlobContainer: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                container_name: str, 
                blob_container: BlobContainer, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BlobContainer: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                container_name: str, 
                blob_container: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BlobContainer: ...

        @overload
        def create_or_update_immutability_policy(
                self, 
                resource_group_name: str, 
                account_name: str, 
                container_name: str, 
                parameters: Optional[ImmutabilityPolicy] = None, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> ImmutabilityPolicy: ...

        @overload
        def create_or_update_immutability_policy(
                self, 
                resource_group_name: str, 
                account_name: str, 
                container_name: str, 
                parameters: Optional[ImmutabilityPolicy] = None, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> ImmutabilityPolicy: ...

        @overload
        def create_or_update_immutability_policy(
                self, 
                resource_group_name: str, 
                account_name: str, 
                container_name: str, 
                parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> ImmutabilityPolicy: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                container_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete_immutability_policy(
                self, 
                resource_group_name: str, 
                account_name: str, 
                container_name: str, 
                *, 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> ImmutabilityPolicy: ...

        @overload
        def extend_immutability_policy(
                self, 
                resource_group_name: str, 
                account_name: str, 
                container_name: str, 
                parameters: Optional[ImmutabilityPolicy] = None, 
                *, 
                content_type: str = "application/json", 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> ImmutabilityPolicy: ...

        @overload
        def extend_immutability_policy(
                self, 
                resource_group_name: str, 
                account_name: str, 
                container_name: str, 
                parameters: Optional[ImmutabilityPolicy] = None, 
                *, 
                content_type: str = "application/json", 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> ImmutabilityPolicy: ...

        @overload
        def extend_immutability_policy(
                self, 
                resource_group_name: str, 
                account_name: str, 
                container_name: str, 
                parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> ImmutabilityPolicy: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                container_name: str, 
                **kwargs: Any
            ) -> BlobContainer: ...

        @distributed_trace
        def get_immutability_policy(
                self, 
                resource_group_name: str, 
                account_name: str, 
                container_name: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> ImmutabilityPolicy: ...

        @overload
        def lease(
                self, 
                resource_group_name: str, 
                account_name: str, 
                container_name: str, 
                parameters: Optional[LeaseContainerRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LeaseContainerResponse: ...

        @overload
        def lease(
                self, 
                resource_group_name: str, 
                account_name: str, 
                container_name: str, 
                parameters: Optional[LeaseContainerRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LeaseContainerResponse: ...

        @overload
        def lease(
                self, 
                resource_group_name: str, 
                account_name: str, 
                container_name: str, 
                parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LeaseContainerResponse: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                account_name: str, 
                *, 
                filter: Optional[str] = ..., 
                include: Optional[Union[str, ListContainersInclude]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[ListContainerItem]: ...

        @distributed_trace
        def lock_immutability_policy(
                self, 
                resource_group_name: str, 
                account_name: str, 
                container_name: str, 
                *, 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> ImmutabilityPolicy: ...

        @overload
        def set_legal_hold(
                self, 
                resource_group_name: str, 
                account_name: str, 
                container_name: str, 
                legal_hold: LegalHold, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LegalHold: ...

        @overload
        def set_legal_hold(
                self, 
                resource_group_name: str, 
                account_name: str, 
                container_name: str, 
                legal_hold: LegalHold, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LegalHold: ...

        @overload
        def set_legal_hold(
                self, 
                resource_group_name: str, 
                account_name: str, 
                container_name: str, 
                legal_hold: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LegalHold: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                container_name: str, 
                blob_container: BlobContainer, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BlobContainer: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                container_name: str, 
                blob_container: BlobContainer, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BlobContainer: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                container_name: str, 
                blob_container: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BlobContainer: ...


    class azure.mgmt.storage.operations.BlobInventoryPoliciesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                blob_inventory_policy_name: Union[str, BlobInventoryPolicyName], 
                properties: BlobInventoryPolicy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BlobInventoryPolicy: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                blob_inventory_policy_name: Union[str, BlobInventoryPolicyName], 
                properties: BlobInventoryPolicy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BlobInventoryPolicy: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                blob_inventory_policy_name: Union[str, BlobInventoryPolicyName], 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BlobInventoryPolicy: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                blob_inventory_policy_name: Union[str, BlobInventoryPolicyName], 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                blob_inventory_policy_name: Union[str, BlobInventoryPolicyName], 
                **kwargs: Any
            ) -> BlobInventoryPolicy: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> ItemPaged[BlobInventoryPolicy]: ...


    class azure.mgmt.storage.operations.BlobServicesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get_service_properties(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> BlobServiceProperties: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> ItemPaged[BlobServiceProperties]: ...

        @overload
        def set_service_properties(
                self, 
                resource_group_name: str, 
                account_name: str, 
                parameters: BlobServiceProperties, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BlobServiceProperties: ...

        @overload
        def set_service_properties(
                self, 
                resource_group_name: str, 
                account_name: str, 
                parameters: BlobServiceProperties, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BlobServiceProperties: ...

        @overload
        def set_service_properties(
                self, 
                resource_group_name: str, 
                account_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BlobServiceProperties: ...


    class azure.mgmt.storage.operations.ConnectorsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                connector_name: str, 
                resource: Connector, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Connector]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                connector_name: str, 
                resource: Connector, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Connector]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                connector_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Connector]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-08-01', params_added_on={'2025-08-01': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'connector_name']}, api_versions_list=['2025-08-01', '2026-04-01'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                connector_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_test_existing_connection(
                self, 
                resource_group_name: str, 
                account_name: str, 
                connector_name: str, 
                body: TestExistingConnectionRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[TestConnectionResponse]: ...

        @overload
        def begin_test_existing_connection(
                self, 
                resource_group_name: str, 
                account_name: str, 
                connector_name: str, 
                body: TestExistingConnectionRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[TestConnectionResponse]: ...

        @overload
        def begin_test_existing_connection(
                self, 
                resource_group_name: str, 
                account_name: str, 
                connector_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[TestConnectionResponse]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                connector_name: str, 
                properties: ConnectorUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Connector]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                connector_name: str, 
                properties: ConnectorUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Connector]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                connector_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Connector]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-08-01', params_added_on={'2025-08-01': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'connector_name', 'accept']}, api_versions_list=['2025-08-01', '2026-04-01'])
        def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                connector_name: str, 
                **kwargs: Any
            ) -> Connector: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-08-01', params_added_on={'2025-08-01': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'accept']}, api_versions_list=['2025-08-01', '2026-04-01'])
        def list_by_storage_account(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Connector]: ...


    class azure.mgmt.storage.operations.DataSharesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                data_share_name: str, 
                resource: DataShare, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DataShare]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                data_share_name: str, 
                resource: DataShare, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DataShare]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                data_share_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DataShare]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-08-01', params_added_on={'2025-08-01': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'data_share_name']}, api_versions_list=['2025-08-01', '2026-04-01'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                data_share_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                data_share_name: str, 
                properties: DataShareUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DataShare]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                data_share_name: str, 
                properties: DataShareUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DataShare]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                data_share_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DataShare]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-08-01', params_added_on={'2025-08-01': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'data_share_name', 'accept']}, api_versions_list=['2025-08-01', '2026-04-01'])
        def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                data_share_name: str, 
                **kwargs: Any
            ) -> DataShare: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-08-01', params_added_on={'2025-08-01': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'accept']}, api_versions_list=['2025-08-01', '2026-04-01'])
        def list_by_storage_account(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> ItemPaged[DataShare]: ...


    class azure.mgmt.storage.operations.DeletedAccountsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                deleted_account_name: str, 
                location: str, 
                **kwargs: Any
            ) -> DeletedAccount: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[DeletedAccount]: ...


    class azure.mgmt.storage.operations.EncryptionScopesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                encryption_scope_name: str, 
                **kwargs: Any
            ) -> EncryptionScope: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                account_name: str, 
                *, 
                filter: Optional[str] = ..., 
                include: Optional[Union[str, ListEncryptionScopesInclude]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[EncryptionScope]: ...

        @overload
        def patch(
                self, 
                resource_group_name: str, 
                account_name: str, 
                encryption_scope_name: str, 
                encryption_scope: EncryptionScope, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EncryptionScope: ...

        @overload
        def patch(
                self, 
                resource_group_name: str, 
                account_name: str, 
                encryption_scope_name: str, 
                encryption_scope: EncryptionScope, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EncryptionScope: ...

        @overload
        def patch(
                self, 
                resource_group_name: str, 
                account_name: str, 
                encryption_scope_name: str, 
                encryption_scope: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EncryptionScope: ...

        @overload
        def put(
                self, 
                resource_group_name: str, 
                account_name: str, 
                encryption_scope_name: str, 
                encryption_scope: EncryptionScope, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EncryptionScope: ...

        @overload
        def put(
                self, 
                resource_group_name: str, 
                account_name: str, 
                encryption_scope_name: str, 
                encryption_scope: EncryptionScope, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EncryptionScope: ...

        @overload
        def put(
                self, 
                resource_group_name: str, 
                account_name: str, 
                encryption_scope_name: str, 
                encryption_scope: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EncryptionScope: ...


    class azure.mgmt.storage.operations.FileServicesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get_service_properties(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> FileServiceProperties: ...

        @distributed_trace
        def get_service_usage(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> FileServiceUsage: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> FileServiceItems: ...

        @distributed_trace
        def list_service_usages(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> ItemPaged[FileServiceUsage]: ...

        @overload
        def set_service_properties(
                self, 
                resource_group_name: str, 
                account_name: str, 
                parameters: FileServiceProperties, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FileServiceProperties: ...

        @overload
        def set_service_properties(
                self, 
                resource_group_name: str, 
                account_name: str, 
                parameters: FileServiceProperties, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FileServiceProperties: ...

        @overload
        def set_service_properties(
                self, 
                resource_group_name: str, 
                account_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FileServiceProperties: ...


    class azure.mgmt.storage.operations.FileSharesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_name: str, 
                file_share: FileShare, 
                *, 
                content_type: str = "application/json", 
                expand: Optional[str] = ..., 
                **kwargs: Any
            ) -> FileShare: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_name: str, 
                file_share: FileShare, 
                *, 
                content_type: str = "application/json", 
                expand: Optional[str] = ..., 
                **kwargs: Any
            ) -> FileShare: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_name: str, 
                file_share: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                expand: Optional[str] = ..., 
                **kwargs: Any
            ) -> FileShare: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_name: str, 
                *, 
                include: Optional[str] = ..., 
                x_ms_snapshot: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_name: str, 
                *, 
                expand: Optional[str] = ..., 
                x_ms_snapshot: Optional[str] = ..., 
                **kwargs: Any
            ) -> FileShare: ...

        @overload
        def lease(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_name: str, 
                parameters: Optional[LeaseShareRequest] = None, 
                *, 
                content_type: str = "application/json", 
                x_ms_snapshot: Optional[str] = ..., 
                **kwargs: Any
            ) -> LeaseShareResponse: ...

        @overload
        def lease(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_name: str, 
                parameters: Optional[LeaseShareRequest] = None, 
                *, 
                content_type: str = "application/json", 
                x_ms_snapshot: Optional[str] = ..., 
                **kwargs: Any
            ) -> LeaseShareResponse: ...

        @overload
        def lease(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_name: str, 
                parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                x_ms_snapshot: Optional[str] = ..., 
                **kwargs: Any
            ) -> LeaseShareResponse: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                account_name: str, 
                *, 
                expand: Optional[str] = ..., 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[FileShareItem]: ...

        @overload
        def restore(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_name: str, 
                deleted_share: DeletedShare, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def restore(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_name: str, 
                deleted_share: DeletedShare, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def restore(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_name: str, 
                deleted_share: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_name: str, 
                file_share: FileShare, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FileShare: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_name: str, 
                file_share: FileShare, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FileShare: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_name: str, 
                file_share: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FileShare: ...


    class azure.mgmt.storage.operations.LocalUsersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                username: str, 
                properties: LocalUser, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LocalUser: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                username: str, 
                properties: LocalUser, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LocalUser: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                username: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LocalUser: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                username: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                username: str, 
                **kwargs: Any
            ) -> LocalUser: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                account_name: str, 
                *, 
                filter: Optional[str] = ..., 
                include: Optional[Union[str, ListLocalUserIncludeParam]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[LocalUser]: ...

        @distributed_trace
        def list_keys(
                self, 
                resource_group_name: str, 
                account_name: str, 
                username: str, 
                **kwargs: Any
            ) -> LocalUserKeys: ...

        @distributed_trace
        def regenerate_password(
                self, 
                resource_group_name: str, 
                account_name: str, 
                username: str, 
                **kwargs: Any
            ) -> LocalUserRegeneratePasswordResult: ...


    class azure.mgmt.storage.operations.ManagementPoliciesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                management_policy_name: Union[str, ManagementPolicyName], 
                properties: ManagementPolicy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ManagementPolicy: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                management_policy_name: Union[str, ManagementPolicyName], 
                properties: ManagementPolicy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ManagementPolicy: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                management_policy_name: Union[str, ManagementPolicyName], 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ManagementPolicy: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                management_policy_name: Union[str, ManagementPolicyName], 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                management_policy_name: Union[str, ManagementPolicyName], 
                **kwargs: Any
            ) -> ManagementPolicy: ...


    class azure.mgmt.storage.operations.NetworkSecurityPerimeterConfigurationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_reconcile(
                self, 
                resource_group_name: str, 
                account_name: str, 
                network_security_perimeter_configuration_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                network_security_perimeter_configuration_name: str, 
                **kwargs: Any
            ) -> NetworkSecurityPerimeterConfiguration: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> ItemPaged[NetworkSecurityPerimeterConfiguration]: ...


    class azure.mgmt.storage.operations.ObjectReplicationPoliciesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                object_replication_policy_id: str, 
                properties: ObjectReplicationPolicy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ObjectReplicationPolicy: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                object_replication_policy_id: str, 
                properties: ObjectReplicationPolicy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ObjectReplicationPolicy: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                object_replication_policy_id: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ObjectReplicationPolicy: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                object_replication_policy_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                object_replication_policy_id: str, 
                **kwargs: Any
            ) -> ObjectReplicationPolicy: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ObjectReplicationPolicy]: ...


    class azure.mgmt.storage.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


    class azure.mgmt.storage.operations.PrivateEndpointConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> ItemPaged[PrivateEndpointConnection]: ...

        @overload
        def put(
                self, 
                resource_group_name: str, 
                account_name: str, 
                private_endpoint_connection_name: str, 
                properties: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @overload
        def put(
                self, 
                resource_group_name: str, 
                account_name: str, 
                private_endpoint_connection_name: str, 
                properties: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @overload
        def put(
                self, 
                resource_group_name: str, 
                account_name: str, 
                private_endpoint_connection_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...


    class azure.mgmt.storage.operations.PrivateLinkResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_by_storage_account(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> PrivateLinkResourceListResult: ...


    class azure.mgmt.storage.operations.QueueOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                queue_name: str, 
                queue: StorageQueue, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StorageQueue: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                queue_name: str, 
                queue: StorageQueue, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StorageQueue: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                queue_name: str, 
                queue: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StorageQueue: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                queue_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                queue_name: str, 
                **kwargs: Any
            ) -> StorageQueue: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                account_name: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[ListQueue]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                queue_name: str, 
                queue: StorageQueue, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StorageQueue: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                queue_name: str, 
                queue: StorageQueue, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StorageQueue: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                queue_name: str, 
                queue: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StorageQueue: ...


    class azure.mgmt.storage.operations.QueueServicesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get_service_properties(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> QueueServiceProperties: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> ListQueueServices: ...

        @overload
        def set_service_properties(
                self, 
                resource_group_name: str, 
                account_name: str, 
                parameters: QueueServiceProperties, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> QueueServiceProperties: ...

        @overload
        def set_service_properties(
                self, 
                resource_group_name: str, 
                account_name: str, 
                parameters: QueueServiceProperties, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> QueueServiceProperties: ...

        @overload
        def set_service_properties(
                self, 
                resource_group_name: str, 
                account_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> QueueServiceProperties: ...


    class azure.mgmt.storage.operations.SkusOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[SkuInformation]: ...


    class azure.mgmt.storage.operations.StorageAccountsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_abort_hierarchical_namespace_migration(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                parameters: StorageAccountCreateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[StorageAccount]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                parameters: StorageAccountCreateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[StorageAccount]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[StorageAccount]: ...

        @overload
        def begin_customer_initiated_migration(
                self, 
                resource_group_name: str, 
                account_name: str, 
                parameters: StorageAccountMigration, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_customer_initiated_migration(
                self, 
                resource_group_name: str, 
                account_name: str, 
                parameters: StorageAccountMigration, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_customer_initiated_migration(
                self, 
                resource_group_name: str, 
                account_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_failover(
                self, 
                resource_group_name: str, 
                account_name: str, 
                *, 
                failover_type: Literal["Planned"] = "Planned", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_hierarchical_namespace_migration(
                self, 
                resource_group_name: str, 
                account_name: str, 
                *, 
                request_type: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_restore_blob_ranges(
                self, 
                resource_group_name: str, 
                account_name: str, 
                parameters: BlobRestoreParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BlobRestoreStatus]: ...

        @overload
        def begin_restore_blob_ranges(
                self, 
                resource_group_name: str, 
                account_name: str, 
                parameters: BlobRestoreParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BlobRestoreStatus]: ...

        @overload
        def begin_restore_blob_ranges(
                self, 
                resource_group_name: str, 
                account_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BlobRestoreStatus]: ...

        @overload
        def check_name_availability(
                self, 
                account_name: StorageAccountCheckNameAvailabilityParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResult: ...

        @overload
        def check_name_availability(
                self, 
                account_name: StorageAccountCheckNameAvailabilityParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResult: ...

        @overload
        def check_name_availability(
                self, 
                account_name: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResult: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get_customer_initiated_migration(
                self, 
                resource_group_name: str, 
                account_name: str, 
                migration_name: Union[str, MigrationName], 
                **kwargs: Any
            ) -> StorageAccountMigration: ...

        @distributed_trace
        def get_properties(
                self, 
                resource_group_name: str, 
                account_name: str, 
                *, 
                expand: Optional[Union[str, StorageAccountExpand]] = ..., 
                **kwargs: Any
            ) -> StorageAccount: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[StorageAccount]: ...

        @overload
        def list_account_sas(
                self, 
                resource_group_name: str, 
                account_name: str, 
                parameters: AccountSasParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ListAccountSasResponse: ...

        @overload
        def list_account_sas(
                self, 
                resource_group_name: str, 
                account_name: str, 
                parameters: AccountSasParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ListAccountSasResponse: ...

        @overload
        def list_account_sas(
                self, 
                resource_group_name: str, 
                account_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ListAccountSasResponse: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[StorageAccount]: ...

        @distributed_trace
        def list_keys(
                self, 
                resource_group_name: str, 
                account_name: str, 
                *, 
                expand: Literal["kerb"] = "kerb", 
                **kwargs: Any
            ) -> StorageAccountListKeysResult: ...

        @overload
        def list_service_sas(
                self, 
                resource_group_name: str, 
                account_name: str, 
                parameters: ServiceSasParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ListServiceSasResponse: ...

        @overload
        def list_service_sas(
                self, 
                resource_group_name: str, 
                account_name: str, 
                parameters: ServiceSasParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ListServiceSasResponse: ...

        @overload
        def list_service_sas(
                self, 
                resource_group_name: str, 
                account_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ListServiceSasResponse: ...

        @overload
        def regenerate_key(
                self, 
                resource_group_name: str, 
                account_name: str, 
                regenerate_key: StorageAccountRegenerateKeyParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StorageAccountListKeysResult: ...

        @overload
        def regenerate_key(
                self, 
                resource_group_name: str, 
                account_name: str, 
                regenerate_key: StorageAccountRegenerateKeyParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StorageAccountListKeysResult: ...

        @overload
        def regenerate_key(
                self, 
                resource_group_name: str, 
                account_name: str, 
                regenerate_key: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StorageAccountListKeysResult: ...

        @distributed_trace
        def revoke_user_delegation_keys(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> None: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                parameters: StorageAccountUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StorageAccount: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                parameters: StorageAccountUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StorageAccount: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StorageAccount: ...


    class azure.mgmt.storage.operations.StorageTaskAssignmentInstancesReportOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                account_name: str, 
                storage_task_assignment_name: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[StorageTaskReportInstance]: ...


    class azure.mgmt.storage.operations.StorageTaskAssignmentsInstancesReportOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                account_name: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[StorageTaskReportInstance]: ...


    class azure.mgmt.storage.operations.StorageTaskAssignmentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                storage_task_assignment_name: str, 
                parameters: StorageTaskAssignment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[StorageTaskAssignment]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                storage_task_assignment_name: str, 
                parameters: StorageTaskAssignment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[StorageTaskAssignment]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                storage_task_assignment_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[StorageTaskAssignment]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                storage_task_assignment_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-08-01', params_added_on={'2025-08-01': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'storage_task_assignment_name']}, api_versions_list=['2025-08-01', '2026-04-01'])
        def begin_stop_assignment(
                self, 
                resource_group_name: str, 
                account_name: str, 
                storage_task_assignment_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                storage_task_assignment_name: str, 
                parameters: StorageTaskAssignmentUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[StorageTaskAssignment]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                storage_task_assignment_name: str, 
                parameters: StorageTaskAssignmentUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[StorageTaskAssignment]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                storage_task_assignment_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[StorageTaskAssignment]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                storage_task_assignment_name: str, 
                **kwargs: Any
            ) -> StorageTaskAssignment: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                account_name: str, 
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[StorageTaskAssignment]: ...


    class azure.mgmt.storage.operations.TableOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                table_name: str, 
                parameters: Optional[Table] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Table: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                table_name: str, 
                parameters: Optional[Table] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Table: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                table_name: str, 
                parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Table: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                table_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                table_name: str, 
                **kwargs: Any
            ) -> Table: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Table]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                table_name: str, 
                parameters: Optional[Table] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Table: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                table_name: str, 
                parameters: Optional[Table] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Table: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                table_name: str, 
                parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Table: ...


    class azure.mgmt.storage.operations.TableServicesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get_service_properties(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> TableServiceProperties: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> ListTableServices: ...

        @overload
        def set_service_properties(
                self, 
                resource_group_name: str, 
                account_name: str, 
                parameters: TableServiceProperties, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TableServiceProperties: ...

        @overload
        def set_service_properties(
                self, 
                resource_group_name: str, 
                account_name: str, 
                parameters: TableServiceProperties, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TableServiceProperties: ...

        @overload
        def set_service_properties(
                self, 
                resource_group_name: str, 
                account_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TableServiceProperties: ...


    class azure.mgmt.storage.operations.UsagesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_by_location(
                self, 
                location: str, 
                **kwargs: Any
            ) -> ItemPaged[Usage]: ...


namespace azure.mgmt.storage.types

    class azure.mgmt.storage.types.AccessPolicy(TypedDict, total=False):
        key "expiryTime": str
        key "permission": str
        key "startTime": str
        expiryTime: str
        permission: str
        startTime: str


    class azure.mgmt.storage.types.AccountImmutabilityPolicyProperties(TypedDict, total=False):
        key "allowProtectedAppendWrites": bool
        key "immutabilityPeriodSinceCreationInDays": int
        key "state": Union[str, AccountImmutabilityPolicyState]
        allowProtectedAppendWrites: bool
        immutabilityPeriodSinceCreationInDays: int
        state: Union[str, AccountImmutabilityPolicyState]


    class azure.mgmt.storage.types.AccountSasParameters(TypedDict, total=False):
        key "keyToSign": str
        key "signedExpiry": Required[str]
        key "signedIp": str
        key "signedPermission": Required[Union[str, Permissions]]
        key "signedProtocol": Union[str, HttpProtocol]
        key "signedResourceTypes": Required[Union[str, SignedResourceTypes]]
        key "signedServices": Required[Union[str, Services]]
        key "signedStart": str
        keyToSign: str
        signedExpiry: str
        signedIp: str
        signedPermission: Union[str, Permissions]
        signedProtocol: Union[str, HttpProtocol]
        signedResourceTypes: Union[str, SignedResourceTypes]
        signedServices: Union[str, Services]
        signedStart: str


    class azure.mgmt.storage.types.ActiveDirectoryProperties(TypedDict, total=False):
        key "accountType": Union[str, AccountType]
        key "azureStorageSid": str
        key "domainGuid": str
        key "domainName": str
        key "domainSid": str
        key "forestName": str
        key "netBiosDomainName": str
        key "samAccountName": str
        accountType: Union[str, AccountType]
        azureStorageSid: str
        domainGuid: str
        domainName: str
        domainSid: str
        forestName: str
        netBiosDomainName: str
        samAccountName: str


    class azure.mgmt.storage.types.AdvancedPlatformMetricsRule(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('AdvancedPlatformMetricsRuleProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: AdvancedPlatformMetricsRuleProperties
        systemData: SystemData
        type: str


    class azure.mgmt.storage.types.AdvancedPlatformMetricsRuleConfig(TypedDict, total=False):
        key "filterType": Union[str, AdvancedPlatformMetricsFilterType]
        filterType: Union[str, AdvancedPlatformMetricsFilterType]
        filterValues: list[str]


    class azure.mgmt.storage.types.AdvancedPlatformMetricsRuleProperties(TypedDict, total=False):
        key "enabled": Required[bool]
        key "lastModifiedTime": str
        key "ruleConfig": Required[AdvancedPlatformMetricsRuleConfig]
        key "ruleType": Union[str, AdvancedPlatformMetricsRuleType]
        enabled: bool
        lastModifiedTime: str
        metricsEmitted: list[Union[str, MetricsEmitted]]
        ruleConfig: AdvancedPlatformMetricsRuleConfig
        ruleType: Union[str, AdvancedPlatformMetricsRuleType]


    class azure.mgmt.storage.types.AzureFilesIdentityBasedAuthentication(TypedDict, total=False):
        key "activeDirectoryProperties": ForwardRef('ActiveDirectoryProperties', module='types')
        key "defaultSharePermission": Union[str, DefaultSharePermission]
        key "directoryServiceOptions": Required[Union[str, DirectoryServiceOptions]]
        key "smbOAuthSettings": ForwardRef('SmbOAuthSettings', module='types')
        activeDirectoryProperties: ActiveDirectoryProperties
        defaultSharePermission: Union[str, DefaultSharePermission]
        directoryServiceOptions: Union[str, DirectoryServiceOptions]
        smbOAuthSettings: SmbOAuthSettings


    class azure.mgmt.storage.types.BlobContainer(ProxyResource):
        key "etag": str
        key "id": str
        key "name": str
        key "properties": ForwardRef('ContainerProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        name: str
        properties: ContainerProperties
        systemData: SystemData
        type: str


    class azure.mgmt.storage.types.BlobInventoryCreationTime(TypedDict, total=False):
        key "lastNDays": int
        lastNDays: int


    class azure.mgmt.storage.types.BlobInventoryPolicy(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('BlobInventoryPolicyProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: BlobInventoryPolicyProperties
        systemData: SystemData
        type: str


    class azure.mgmt.storage.types.BlobInventoryPolicyDefinition(TypedDict, total=False):
        key "filters": ForwardRef('BlobInventoryPolicyFilter', module='types')
        key "format": Required[Union[str, Format]]
        key "objectType": Required[Union[str, ObjectType]]
        key "schedule": Required[Union[str, Schedule]]
        key "schemaFields": Required[list[str]]
        filters: BlobInventoryPolicyFilter
        format: Union[str, Format]
        objectType: Union[str, ObjectType]
        schedule: Union[str, Schedule]
        schemaFields: list[str]


    class azure.mgmt.storage.types.BlobInventoryPolicyFilter(TypedDict, total=False):
        key "creationTime": ForwardRef('BlobInventoryCreationTime', module='types')
        key "includeBlobVersions": bool
        key "includeDeleted": bool
        key "includeSnapshots": bool
        blobTypes: list[str]
        creationTime: BlobInventoryCreationTime
        excludePrefix: list[str]
        includeBlobVersions: bool
        includeDeleted: bool
        includeSnapshots: bool
        prefixMatch: list[str]


    class azure.mgmt.storage.types.BlobInventoryPolicyProperties(TypedDict, total=False):
        key "lastModifiedTime": str
        key "policy": Required[BlobInventoryPolicySchema]
        lastModifiedTime: str
        policy: BlobInventoryPolicySchema


    class azure.mgmt.storage.types.BlobInventoryPolicyRule(TypedDict, total=False):
        key "definition": Required[BlobInventoryPolicyDefinition]
        key "destination": Required[str]
        key "enabled": Required[bool]
        key "name": Required[str]
        definition: BlobInventoryPolicyDefinition
        destination: str
        enabled: bool
        name: str


    class azure.mgmt.storage.types.BlobInventoryPolicySchema(TypedDict, total=False):
        key "destination": str
        key "enabled": Required[bool]
        key "rules": Required[list[BlobInventoryPolicyRule]]
        key "type": Required[Union[str, InventoryRuleType]]
        destination: str
        enabled: bool
        rules: list[BlobInventoryPolicyRule]
        type: Union[str, InventoryRuleType]


    class azure.mgmt.storage.types.BlobRestoreParameters(TypedDict, total=False):
        key "blobRanges": Required[list[BlobRestoreRange]]
        key "timeToRestore": Required[str]
        blobRanges: list[BlobRestoreRange]
        timeToRestore: str


    class azure.mgmt.storage.types.BlobRestoreRange(TypedDict, total=False):
        key "endRange": Required[str]
        key "startRange": Required[str]
        endRange: str
        startRange: str


    class azure.mgmt.storage.types.BlobServiceProperties(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('BlobServicePropertiesProperties', module='types')
        key "sku": ForwardRef('Sku', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: BlobServicePropertiesProperties
        sku: Sku
        systemData: SystemData
        type: str


    class azure.mgmt.storage.types.BlobServicePropertiesProperties(TypedDict, total=False):
        key "automaticSnapshotPolicyEnabled": bool
        key "changeFeed": ForwardRef('ChangeFeed', module='types')
        key "containerDeleteRetentionPolicy": ForwardRef('DeleteRetentionPolicy', module='types')
        key "cors": ForwardRef('CorsRules', module='types')
        key "defaultServiceVersion": str
        key "deleteRetentionPolicy": ForwardRef('DeleteRetentionPolicy', module='types')
        key "isVersioningEnabled": bool
        key "lastAccessTimeTrackingPolicy": ForwardRef('LastAccessTimeTrackingPolicy', module='types')
        key "restorePolicy": ForwardRef('RestorePolicyProperties', module='types')
        key "staticWebsite": ForwardRef('StaticWebsite', module='types')
        automaticSnapshotPolicyEnabled: bool
        changeFeed: ChangeFeed
        containerDeleteRetentionPolicy: DeleteRetentionPolicy
        cors: CorsRules
        defaultServiceVersion: str
        deleteRetentionPolicy: DeleteRetentionPolicy
        isVersioningEnabled: bool
        lastAccessTimeTrackingPolicy: LastAccessTimeTrackingPolicy
        restorePolicy: RestorePolicyProperties
        staticWebsite: StaticWebsite


    class azure.mgmt.storage.types.ChangeFeed(TypedDict, total=False):
        key "enabled": bool
        key "retentionInDays": int
        enabled: bool
        retentionInDays: int


    class azure.mgmt.storage.types.Connector(TrackedResource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": Required[StorageConnectorProperties]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: StorageConnectorProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.storage.types.ConnectorUpdate(TrackedResourceUpdate):
        key "id": str
        key "name": str
        key "properties": ForwardRef('StorageConnectorPropertiesUpdate', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: StorageConnectorPropertiesUpdate
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.storage.types.ContainerProperties(TypedDict, total=False):
        key "defaultEncryptionScope": str
        key "deleted": bool
        key "deletedTime": str
        key "denyEncryptionScopeOverride": bool
        key "enableNfsV3AllSquash": bool
        key "enableNfsV3RootSquash": bool
        key "hasImmutabilityPolicy": bool
        key "hasLegalHold": bool
        key "immutabilityPolicy": ForwardRef('ImmutabilityPolicyProperties', module='types')
        key "immutableStorageWithVersioning": ForwardRef('ImmutableStorageWithVersioning', module='types')
        key "lastModifiedTime": str
        key "leaseDuration": Union[str, LeaseDuration]
        key "leaseState": Union[str, LeaseState]
        key "leaseStatus": Union[str, LeaseStatus]
        key "legalHold": ForwardRef('LegalHoldProperties', module='types')
        key "publicAccess": Union[str, PublicAccess]
        key "remainingRetentionDays": int
        key "version": str
        defaultEncryptionScope: str
        deleted: bool
        deletedTime: str
        denyEncryptionScopeOverride: bool
        enableNfsV3AllSquash: bool
        enableNfsV3RootSquash: bool
        hasImmutabilityPolicy: bool
        hasLegalHold: bool
        immutabilityPolicy: ImmutabilityPolicyProperties
        immutableStorageWithVersioning: ImmutableStorageWithVersioning
        lastModifiedTime: str
        leaseDuration: Union[str, LeaseDuration]
        leaseState: Union[str, LeaseState]
        leaseStatus: Union[str, LeaseStatus]
        legalHold: LegalHoldProperties
        metadata: dict[str, str]
        publicAccess: Union[str, PublicAccess]
        remainingRetentionDays: int
        version: str


    class azure.mgmt.storage.types.CorsRule(TypedDict, total=False):
        key "allowedHeaders": Required[list[str]]
        key "allowedMethods": Required[list[Union[str, AllowedMethods]]]
        key "allowedOrigins": Required[list[str]]
        key "exposedHeaders": Required[list[str]]
        key "maxAgeInSeconds": Required[int]
        allowedHeaders: list[str]
        allowedMethods: list[Union[str, AllowedMethods]]
        allowedOrigins: list[str]
        exposedHeaders: list[str]
        maxAgeInSeconds: int


    class azure.mgmt.storage.types.CorsRules(TypedDict, total=False):
        corsRules: list[CorsRule]


    class azure.mgmt.storage.types.CustomDomain(TypedDict, total=False):
        key "name": Required[str]
        key "useSubDomainName": bool
        name: str
        useSubDomainName: bool


    class azure.mgmt.storage.types.DataShare(TrackedResource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": Required[StorageDataShareProperties]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: StorageDataShareProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.storage.types.DataShareConnection(TypedDict, total=False):
        key "dataShareUri": Required[str]
        key "type": Required[Literal[StorageConnectorConnectionType.DATA_SHARE]]
        dataShareUri: str
        type: Literal[StorageConnectorConnectionType.DATA_SHARE]


    class azure.mgmt.storage.types.DataShareSource(TypedDict, total=False):
        key "authProperties": Required[StorageConnectorAuthProperties]
        key "connection": Required[StorageConnectorConnection]
        key "type": Required[Literal[StorageConnectorSourceType.DATA_SHARE]]
        authProperties: StorageConnectorAuthProperties
        connection: StorageConnectorConnection
        type: Literal[StorageConnectorSourceType.DATA_SHARE]


    class azure.mgmt.storage.types.DataShareSourceUpdate(TypedDict, total=False):
        key "authProperties": ForwardRef('StorageConnectorAuthPropertiesUpdate', module='types')
        key "type": Required[Literal[StorageConnectorSourceType.DATA_SHARE]]
        authProperties: StorageConnectorAuthPropertiesUpdate
        type: Literal[StorageConnectorSourceType.DATA_SHARE]


    class azure.mgmt.storage.types.DataShareUpdate(TrackedResourceUpdate):
        key "id": str
        key "name": str
        key "properties": ForwardRef('StorageDataSharePropertiesUpdate', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: StorageDataSharePropertiesUpdate
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.storage.types.DateAfterCreation(TypedDict, total=False):
        key "daysAfterCreationGreaterThan": Required[float]
        key "daysAfterLastTierChangeGreaterThan": float
        daysAfterCreationGreaterThan: float
        daysAfterLastTierChangeGreaterThan: float


    class azure.mgmt.storage.types.DateAfterModification(TypedDict, total=False):
        key "daysAfterCreationGreaterThan": float
        key "daysAfterLastAccessTimeGreaterThan": float
        key "daysAfterLastTierChangeGreaterThan": float
        key "daysAfterModificationGreaterThan": float
        daysAfterCreationGreaterThan: float
        daysAfterLastAccessTimeGreaterThan: float
        daysAfterLastTierChangeGreaterThan: float
        daysAfterModificationGreaterThan: float


    class azure.mgmt.storage.types.DeleteRetentionPolicy(TypedDict, total=False):
        key "allowPermanentDelete": bool
        key "days": int
        key "enabled": bool
        allowPermanentDelete: bool
        days: int
        enabled: bool


    class azure.mgmt.storage.types.DeletedShare(TypedDict, total=False):
        key "deletedShareName": Required[str]
        key "deletedShareVersion": Required[str]
        deletedShareName: str
        deletedShareVersion: str


    class azure.mgmt.storage.types.DualStackEndpointPreference(TypedDict, total=False):
        key "publishIpv6Endpoint": bool
        publishIpv6Endpoint: bool


    class azure.mgmt.storage.types.Encryption(TypedDict, total=False):
        key "identity": ForwardRef('EncryptionIdentity', module='types')
        key "keySource": Union[str, KeySource]
        key "keyvaultproperties": ForwardRef('KeyVaultProperties', module='types')
        key "requireInfrastructureEncryption": bool
        key "services": ForwardRef('EncryptionServices', module='types')
        identity: EncryptionIdentity
        keySource: Union[str, KeySource]
        keyvaultproperties: KeyVaultProperties
        requireInfrastructureEncryption: bool
        services: EncryptionServices


    class azure.mgmt.storage.types.EncryptionIdentity(TypedDict, total=False):
        key "federatedIdentityClientId": str
        key "userAssignedIdentity": str
        federatedIdentityClientId: str
        userAssignedIdentity: str


    class azure.mgmt.storage.types.EncryptionInTransit(TypedDict, total=False):
        key "required": bool
        required: bool


    class azure.mgmt.storage.types.EncryptionScope(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('EncryptionScopeProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: EncryptionScopeProperties
        systemData: SystemData
        type: str


    class azure.mgmt.storage.types.EncryptionScopeKeyVaultProperties(TypedDict, total=False):
        key "currentVersionedKeyIdentifier": str
        key "keyUri": str
        key "lastKeyRotationTimestamp": str
        currentVersionedKeyIdentifier: str
        keyUri: str
        lastKeyRotationTimestamp: str


    class azure.mgmt.storage.types.EncryptionScopeProperties(TypedDict, total=False):
        key "creationTime": str
        key "keyVaultProperties": ForwardRef('EncryptionScopeKeyVaultProperties', module='types')
        key "lastModifiedTime": str
        key "requireInfrastructureEncryption": bool
        key "source": Union[str, EncryptionScopeSource]
        key "state": Union[str, EncryptionScopeState]
        creationTime: str
        keyVaultProperties: EncryptionScopeKeyVaultProperties
        lastModifiedTime: str
        requireInfrastructureEncryption: bool
        source: Union[str, EncryptionScopeSource]
        state: Union[str, EncryptionScopeState]


    class azure.mgmt.storage.types.EncryptionService(TypedDict, total=False):
        key "enabled": bool
        key "keyType": Union[str, KeyType]
        key "lastEnabledTime": str
        enabled: bool
        keyType: Union[str, KeyType]
        lastEnabledTime: str


    class azure.mgmt.storage.types.EncryptionServices(TypedDict, total=False):
        key "blob": ForwardRef('EncryptionService', module='types')
        key "file": ForwardRef('EncryptionService', module='types')
        key "queue": ForwardRef('EncryptionService', module='types')
        key "table": ForwardRef('EncryptionService', module='types')
        blob: EncryptionService
        file: EncryptionService
        queue: EncryptionService
        table: EncryptionService


    class azure.mgmt.storage.types.ExecutionTarget(TypedDict, total=False):
        excludePrefix: list[str]
        prefix: list[str]


    class azure.mgmt.storage.types.ExecutionTrigger(TypedDict, total=False):
        key "parameters": Required[TriggerParameters]
        key "type": Required[Union[str, TriggerType]]
        parameters: TriggerParameters
        type: Union[str, TriggerType]


    class azure.mgmt.storage.types.ExecutionTriggerUpdate(TypedDict, total=False):
        key "parameters": ForwardRef('TriggerParametersUpdate', module='types')
        key "type": Union[str, TriggerType]
        parameters: TriggerParametersUpdate
        type: Union[str, TriggerType]


    class azure.mgmt.storage.types.ExtendedLocation(TypedDict, total=False):
        key "name": str
        key "type": Union[str, ExtendedLocationTypes]
        name: str
        type: Union[str, ExtendedLocationTypes]


    class azure.mgmt.storage.types.FileServiceProperties(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('FileServicePropertiesProperties', module='types')
        key "sku": ForwardRef('Sku', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: FileServicePropertiesProperties
        sku: Sku
        systemData: SystemData
        type: str


    class azure.mgmt.storage.types.FileServicePropertiesProperties(TypedDict, total=False):
        key "cors": ForwardRef('CorsRules', module='types')
        key "protocolSettings": ForwardRef('ProtocolSettings', module='types')
        key "shareDeleteRetentionPolicy": ForwardRef('DeleteRetentionPolicy', module='types')
        cors: CorsRules
        protocolSettings: ProtocolSettings
        shareDeleteRetentionPolicy: DeleteRetentionPolicy


    class azure.mgmt.storage.types.FileShare(ProxyResource):
        key "etag": str
        key "id": str
        key "name": str
        key "properties": ForwardRef('FileShareProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        name: str
        properties: FileShareProperties
        systemData: SystemData
        type: str


    class azure.mgmt.storage.types.FileShareProperties(TypedDict, total=False):
        key "accessTier": Union[str, ShareAccessTier]
        key "accessTierChangeTime": str
        key "accessTierStatus": str
        key "deleted": bool
        key "deletedTime": str
        key "enabledProtocols": Union[str, EnabledProtocols]
        key "fileSharePaidBursting": ForwardRef('FileSharePropertiesFileSharePaidBursting', module='types')
        key "includedBurstIops": int
        key "lastModifiedTime": str
        key "leaseDuration": Union[str, LeaseDuration]
        key "leaseState": Union[str, LeaseState]
        key "leaseStatus": Union[str, LeaseStatus]
        key "maxBurstCreditsForIops": int
        key "nextAllowedProvisionedBandwidthDowngradeTime": str
        key "nextAllowedProvisionedIopsDowngradeTime": str
        key "nextAllowedQuotaDowngradeTime": str
        key "provisionedBandwidthMibps": int
        key "provisionedIops": int
        key "remainingRetentionDays": int
        key "rootSquash": Union[str, RootSquashType]
        key "shareQuota": int
        key "shareUsageBytes": int
        key "snapshotTime": str
        key "version": str
        accessTier: Union[str, ShareAccessTier]
        accessTierChangeTime: str
        accessTierStatus: str
        deleted: bool
        deletedTime: str
        enabledProtocols: Union[str, EnabledProtocols]
        fileSharePaidBursting: FileSharePropertiesFileSharePaidBursting
        includedBurstIops: int
        lastModifiedTime: str
        leaseDuration: Union[str, LeaseDuration]
        leaseState: Union[str, LeaseState]
        leaseStatus: Union[str, LeaseStatus]
        maxBurstCreditsForIops: int
        metadata: dict[str, str]
        nextAllowedProvisionedBandwidthDowngradeTime: str
        nextAllowedProvisionedIopsDowngradeTime: str
        nextAllowedQuotaDowngradeTime: str
        provisionedBandwidthMibps: int
        provisionedIops: int
        remainingRetentionDays: int
        rootSquash: Union[str, RootSquashType]
        shareQuota: int
        shareUsageBytes: int
        signedIdentifiers: list[SignedIdentifier]
        snapshotTime: str
        version: str


    class azure.mgmt.storage.types.FileSharePropertiesFileSharePaidBursting(TypedDict, total=False):
        key "paidBurstingEnabled": bool
        key "paidBurstingMaxBandwidthMibps": int
        key "paidBurstingMaxIops": int
        paidBurstingEnabled: bool
        paidBurstingMaxBandwidthMibps: int
        paidBurstingMaxIops: int


    class azure.mgmt.storage.types.GeoPriorityReplicationStatus(TypedDict, total=False):
        key "isBlobEnabled": bool
        isBlobEnabled: bool


    class azure.mgmt.storage.types.IPRule(TypedDict, total=False):
        key "action": Literal["Allow"]
        key "value": Required[str]
        action: Literal[Allow]
        value: str


    class azure.mgmt.storage.types.Identity(TypedDict, total=False):
        key "principalId": str
        key "tenantId": str
        key "type": Required[Union[str, IdentityType]]
        principalId: str
        tenantId: str
        type: Union[str, IdentityType]
        userAssignedIdentities: dict[str, UserAssignedIdentity]


    class azure.mgmt.storage.types.ImmutabilityPolicy(ProxyResource):
        key "etag": str
        key "id": str
        key "name": str
        key "properties": Required[ImmutabilityPolicyProperty]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        name: str
        properties: ImmutabilityPolicyProperty
        systemData: SystemData
        type: str


    class azure.mgmt.storage.types.ImmutabilityPolicyProperties(TypedDict, total=False):
        key "etag": str
        key "properties": ForwardRef('ImmutabilityPolicyProperty', module='types')
        etag: str
        properties: ImmutabilityPolicyProperty
        updateHistory: list[UpdateHistoryProperty]


    class azure.mgmt.storage.types.ImmutabilityPolicyProperty(TypedDict, total=False):
        key "allowProtectedAppendWrites": bool
        key "allowProtectedAppendWritesAll": bool
        key "immutabilityPeriodSinceCreationInDays": int
        key "state": Union[str, ImmutabilityPolicyState]
        allowProtectedAppendWrites: bool
        allowProtectedAppendWritesAll: bool
        immutabilityPeriodSinceCreationInDays: int
        state: Union[str, ImmutabilityPolicyState]


    class azure.mgmt.storage.types.ImmutableStorageAccount(TypedDict, total=False):
        key "enabled": bool
        key "immutabilityPolicy": ForwardRef('AccountImmutabilityPolicyProperties', module='types')
        enabled: bool
        immutabilityPolicy: AccountImmutabilityPolicyProperties


    class azure.mgmt.storage.types.ImmutableStorageWithVersioning(TypedDict, total=False):
        key "enabled": bool
        key "migrationState": Union[str, MigrationState]
        key "timeStamp": str
        enabled: bool
        migrationState: Union[str, MigrationState]
        timeStamp: str


    class azure.mgmt.storage.types.KeyPolicy(TypedDict, total=False):
        key "keyExpirationPeriodInDays": Required[int]
        keyExpirationPeriodInDays: int


    class azure.mgmt.storage.types.KeyVaultProperties(TypedDict, total=False):
        key "currentVersionedKeyExpirationTimestamp": str
        key "currentVersionedKeyIdentifier": str
        key "keyname": str
        key "keyvaulturi": str
        key "keyversion": str
        key "lastKeyRotationTimestamp": str
        currentVersionedKeyExpirationTimestamp: str
        currentVersionedKeyIdentifier: str
        keyname: str
        keyvaulturi: str
        keyversion: str
        lastKeyRotationTimestamp: str


    class azure.mgmt.storage.types.LastAccessTimeTrackingPolicy(TypedDict, total=False):
        key "enable": Required[bool]
        key "name": Union[str, Name]
        key "trackingGranularityInDays": int
        blobType: list[str]
        enable: bool
        name: Union[str, Name]
        trackingGranularityInDays: int


    class azure.mgmt.storage.types.LeaseContainerRequest(TypedDict, total=False):
        key "action": Required[Union[str, LeaseContainerRequestAction]]
        key "breakPeriod": int
        key "leaseDuration": int
        key "leaseId": str
        key "proposedLeaseId": str
        action: Union[str, LeaseContainerRequestAction]
        breakPeriod: int
        leaseDuration: int
        leaseId: str
        proposedLeaseId: str


    class azure.mgmt.storage.types.LeaseShareRequest(TypedDict, total=False):
        key "action": Required[Union[str, LeaseShareAction]]
        key "breakPeriod": int
        key "leaseDuration": int
        key "leaseId": str
        key "proposedLeaseId": str
        action: Union[str, LeaseShareAction]
        breakPeriod: int
        leaseDuration: int
        leaseId: str
        proposedLeaseId: str


    class azure.mgmt.storage.types.LegalHold(TypedDict, total=False):
        key "allowProtectedAppendWritesAll": bool
        key "hasLegalHold": bool
        key "tags": Required[list[str]]
        allowProtectedAppendWritesAll: bool
        hasLegalHold: bool
        tags: list[str]


    class azure.mgmt.storage.types.LegalHoldProperties(TypedDict, total=False):
        key "hasLegalHold": bool
        key "protectedAppendWritesHistory": ForwardRef('ProtectedAppendWritesHistory', module='types')
        hasLegalHold: bool
        protectedAppendWritesHistory: ProtectedAppendWritesHistory
        tags: list[TagProperty]


    class azure.mgmt.storage.types.LocalUser(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('LocalUserProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: LocalUserProperties
        systemData: SystemData
        type: str


    class azure.mgmt.storage.types.LocalUserProperties(TypedDict, total=False):
        key "allowAclAuthorization": bool
        key "groupId": int
        key "hasSharedKey": bool
        key "hasSshKey": bool
        key "hasSshPassword": bool
        key "homeDirectory": str
        key "isNFSv3Enabled": bool
        key "sid": str
        key "userId": int
        allowAclAuthorization: bool
        extendedGroups: list[int]
        groupId: int
        hasSharedKey: bool
        hasSshKey: bool
        hasSshPassword: bool
        homeDirectory: str
        isNFSv3Enabled: bool
        permissionScopes: list[PermissionScope]
        sid: str
        sshAuthorizedKeys: list[SshPublicKey]
        userId: int


    class azure.mgmt.storage.types.ManagedIdentityAuthProperties(TypedDict, total=False):
        key "identityResourceId": str
        key "type": Required[Literal[StorageConnectorAuthType.MANAGED_IDENTITY]]
        identityResourceId: str
        type: Literal[StorageConnectorAuthType.MANAGED_IDENTITY]


    class azure.mgmt.storage.types.ManagedIdentityAuthPropertiesUpdate(TypedDict, total=False):
        key "identityResourceId": str
        key "type": Required[Literal[StorageConnectorAuthType.MANAGED_IDENTITY]]
        identityResourceId: str
        type: Literal[StorageConnectorAuthType.MANAGED_IDENTITY]


    class azure.mgmt.storage.types.ManagementPolicy(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('ManagementPolicyProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: ManagementPolicyProperties
        systemData: SystemData
        type: str


    class azure.mgmt.storage.types.ManagementPolicyAction(TypedDict, total=False):
        key "baseBlob": ForwardRef('ManagementPolicyBaseBlob', module='types')
        key "snapshot": ForwardRef('ManagementPolicySnapShot', module='types')
        key "version": ForwardRef('ManagementPolicyVersion', module='types')
        baseBlob: ManagementPolicyBaseBlob
        snapshot: ManagementPolicySnapShot
        version: ManagementPolicyVersion


    class azure.mgmt.storage.types.ManagementPolicyBaseBlob(TypedDict, total=False):
        key "delete": ForwardRef('DateAfterModification', module='types')
        key "enableAutoTierToHotFromCool": bool
        key "tierToArchive": ForwardRef('DateAfterModification', module='types')
        key "tierToCold": ForwardRef('DateAfterModification', module='types')
        key "tierToCool": ForwardRef('DateAfterModification', module='types')
        key "tierToHot": ForwardRef('DateAfterModification', module='types')
        delete: DateAfterModification
        enableAutoTierToHotFromCool: bool
        tierToArchive: DateAfterModification
        tierToCold: DateAfterModification
        tierToCool: DateAfterModification
        tierToHot: DateAfterModification


    class azure.mgmt.storage.types.ManagementPolicyDefinition(TypedDict, total=False):
        key "actions": Required[ManagementPolicyAction]
        key "filters": ForwardRef('ManagementPolicyFilter', module='types')
        actions: ManagementPolicyAction
        filters: ManagementPolicyFilter


    class azure.mgmt.storage.types.ManagementPolicyFilter(TypedDict, total=False):
        key "blobTypes": Required[list[str]]
        blobIndexMatch: list[TagFilter]
        blobTypes: list[str]
        prefixMatch: list[str]


    class azure.mgmt.storage.types.ManagementPolicyProperties(TypedDict, total=False):
        key "lastModifiedTime": str
        key "policy": Required[ManagementPolicySchema]
        lastModifiedTime: str
        policy: ManagementPolicySchema


    class azure.mgmt.storage.types.ManagementPolicyRule(TypedDict, total=False):
        key "definition": Required[ManagementPolicyDefinition]
        key "enabled": bool
        key "name": Required[str]
        key "type": Required[Union[str, RuleType]]
        definition: ManagementPolicyDefinition
        enabled: bool
        name: str
        type: Union[str, RuleType]


    class azure.mgmt.storage.types.ManagementPolicySchema(TypedDict, total=False):
        key "rules": Required[list[ManagementPolicyRule]]
        rules: list[ManagementPolicyRule]


    class azure.mgmt.storage.types.ManagementPolicySnapShot(TypedDict, total=False):
        key "delete": ForwardRef('DateAfterCreation', module='types')
        key "tierToArchive": ForwardRef('DateAfterCreation', module='types')
        key "tierToCold": ForwardRef('DateAfterCreation', module='types')
        key "tierToCool": ForwardRef('DateAfterCreation', module='types')
        key "tierToHot": ForwardRef('DateAfterCreation', module='types')
        delete: DateAfterCreation
        tierToArchive: DateAfterCreation
        tierToCold: DateAfterCreation
        tierToCool: DateAfterCreation
        tierToHot: DateAfterCreation


    class azure.mgmt.storage.types.ManagementPolicyVersion(TypedDict, total=False):
        key "delete": ForwardRef('DateAfterCreation', module='types')
        key "tierToArchive": ForwardRef('DateAfterCreation', module='types')
        key "tierToCold": ForwardRef('DateAfterCreation', module='types')
        key "tierToCool": ForwardRef('DateAfterCreation', module='types')
        key "tierToHot": ForwardRef('DateAfterCreation', module='types')
        delete: DateAfterCreation
        tierToArchive: DateAfterCreation
        tierToCold: DateAfterCreation
        tierToCool: DateAfterCreation
        tierToHot: DateAfterCreation


    class azure.mgmt.storage.types.Multichannel(TypedDict, total=False):
        key "enabled": bool
        enabled: bool


    class azure.mgmt.storage.types.NetworkRuleSet(TypedDict, total=False):
        key "bypass": Union[str, Bypass]
        key "defaultAction": Required[Union[str, DefaultAction]]
        bypass: Union[str, Bypass]
        defaultAction: Union[str, DefaultAction]
        ipRules: list[IPRule]
        ipv6Rules: list[IPRule]
        resourceAccessRules: list[ResourceAccessRule]
        virtualNetworkRules: list[VirtualNetworkRule]


    class azure.mgmt.storage.types.NfsSetting(TypedDict, total=False):
        key "encryptionInTransit": ForwardRef('EncryptionInTransit', module='types')
        encryptionInTransit: EncryptionInTransit


    class azure.mgmt.storage.types.ObjectReplicationPolicy(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('ObjectReplicationPolicyProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: ObjectReplicationPolicyProperties
        systemData: SystemData
        type: str


    class azure.mgmt.storage.types.ObjectReplicationPolicyFilter(TypedDict, total=False):
        key "minCreationTime": str
        minCreationTime: str
        prefixMatch: list[str]


    class azure.mgmt.storage.types.ObjectReplicationPolicyProperties(TypedDict, total=False):
        key "destinationAccount": Required[str]
        key "enabledTime": str
        key "metrics": ForwardRef('ObjectReplicationPolicyPropertiesMetrics', module='types')
        key "policyId": str
        key "priorityReplication": ForwardRef('ObjectReplicationPolicyPropertiesPriorityReplication', module='types')
        key "sourceAccount": Required[str]
        key "tagsReplication": ForwardRef('ObjectReplicationPolicyPropertiesTagsReplication', module='types')
        destinationAccount: str
        enabledTime: str
        metrics: ObjectReplicationPolicyPropertiesMetrics
        policyId: str
        priorityReplication: ObjectReplicationPolicyPropertiesPriorityReplication
        rules: list[ObjectReplicationPolicyRule]
        sourceAccount: str
        tagsReplication: ObjectReplicationPolicyPropertiesTagsReplication


    class azure.mgmt.storage.types.ObjectReplicationPolicyPropertiesMetrics(TypedDict, total=False):
        key "enabled": bool
        enabled: bool


    class azure.mgmt.storage.types.ObjectReplicationPolicyPropertiesPriorityReplication(TypedDict, total=False):
        key "enabled": bool
        enabled: bool


    class azure.mgmt.storage.types.ObjectReplicationPolicyPropertiesTagsReplication(TypedDict, total=False):
        key "enabled": bool
        enabled: bool


    class azure.mgmt.storage.types.ObjectReplicationPolicyRule(TypedDict, total=False):
        key "destinationContainer": Required[str]
        key "filters": ForwardRef('ObjectReplicationPolicyFilter', module='types')
        key "ruleId": str
        key "sourceContainer": Required[str]
        destinationContainer: str
        filters: ObjectReplicationPolicyFilter
        ruleId: str
        sourceContainer: str


    class azure.mgmt.storage.types.PermissionScope(TypedDict, total=False):
        key "permissions": Required[str]
        key "resourceName": Required[str]
        key "service": Required[str]
        permissions: str
        resourceName: str
        service: str


    class azure.mgmt.storage.types.Placement(TypedDict, total=False):
        key "zonePlacementPolicy": Union[str, ZonePlacementPolicy]
        zonePlacementPolicy: Union[str, ZonePlacementPolicy]


    class azure.mgmt.storage.types.PrivateEndpoint(TypedDict, total=False):
        key "id": str
        id: str


    class azure.mgmt.storage.types.PrivateEndpointConnection(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('PrivateEndpointConnectionProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: PrivateEndpointConnectionProperties
        systemData: SystemData
        type: str


    class azure.mgmt.storage.types.PrivateEndpointConnectionProperties(TypedDict, total=False):
        key "privateEndpoint": ForwardRef('PrivateEndpoint', module='types')
        key "privateLinkServiceConnectionState": Required[PrivateLinkServiceConnectionState]
        key "provisioningState": Union[str, PrivateEndpointConnectionProvisioningState]
        privateEndpoint: PrivateEndpoint
        privateLinkServiceConnectionState: PrivateLinkServiceConnectionState
        provisioningState: Union[str, PrivateEndpointConnectionProvisioningState]


    class azure.mgmt.storage.types.PrivateLinkServiceConnectionState(TypedDict, total=False):
        key "actionRequired": str
        key "description": str
        key "status": Union[str, PrivateEndpointServiceConnectionStatus]
        actionRequired: str
        description: str
        status: Union[str, PrivateEndpointServiceConnectionStatus]


    class azure.mgmt.storage.types.ProtectedAppendWritesHistory(TypedDict, total=False):
        key "allowProtectedAppendWritesAll": bool
        key "timestamp": str
        allowProtectedAppendWritesAll: bool
        timestamp: str


    class azure.mgmt.storage.types.ProtocolSettings(TypedDict, total=False):
        key "nfs": ForwardRef('NfsSetting', module='types')
        key "smb": ForwardRef('SmbSetting', module='types')
        nfs: NfsSetting
        smb: SmbSetting


    class azure.mgmt.storage.types.ProxyResource(ResourceAutoGenerated):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        systemData: SystemData
        type: str


    class azure.mgmt.storage.types.QueueProperties(TypedDict, total=False):
        key "approximateMessageCount": int
        approximateMessageCount: int
        metadata: dict[str, str]


    class azure.mgmt.storage.types.QueueServiceProperties(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('QueueServicePropertiesProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: QueueServicePropertiesProperties
        systemData: SystemData
        type: str


    class azure.mgmt.storage.types.QueueServicePropertiesProperties(TypedDict, total=False):
        key "cors": ForwardRef('CorsRules', module='types')
        cors: CorsRules


    class azure.mgmt.storage.types.ResourceAccessRule(TypedDict, total=False):
        key "resourceId": str
        key "tenantId": str
        resourceId: str
        tenantId: str


    class azure.mgmt.storage.types.ResourceAutoGenerated(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        systemData: SystemData
        type: str


    class azure.mgmt.storage.types.RestorePolicyProperties(TypedDict, total=False):
        key "days": int
        key "enabled": Required[bool]
        key "lastEnabledTime": str
        key "minRestoreTime": str
        days: int
        enabled: bool
        lastEnabledTime: str
        minRestoreTime: str


    class azure.mgmt.storage.types.RoutingPreference(TypedDict, total=False):
        key "publishInternetEndpoints": bool
        key "publishMicrosoftEndpoints": bool
        key "routingChoice": Union[str, RoutingChoice]
        publishInternetEndpoints: bool
        publishMicrosoftEndpoints: bool
        routingChoice: Union[str, RoutingChoice]


    class azure.mgmt.storage.types.SasPolicy(TypedDict, total=False):
        key "expirationAction": Required[Union[str, ExpirationAction]]
        key "sasExpirationPeriod": Required[str]
        expirationAction: Union[str, ExpirationAction]
        sasExpirationPeriod: str


    class azure.mgmt.storage.types.ServiceSasParameters(TypedDict, total=False):
        key "canonicalizedResource": Required[str]
        key "endPk": str
        key "endRk": str
        key "keyToSign": str
        key "rscc": str
        key "rscd": str
        key "rsce": str
        key "rscl": str
        key "rsct": str
        key "signedExpiry": str
        key "signedIdentifier": str
        key "signedIp": str
        key "signedPermission": Union[str, Permissions]
        key "signedProtocol": Union[str, HttpProtocol]
        key "signedResource": Union[str, SignedResource]
        key "signedStart": str
        key "startPk": str
        key "startRk": str
        canonicalizedResource: str
        endPk: str
        endRk: str
        keyToSign: str
        rscc: str
        rscd: str
        rsce: str
        rscl: str
        rsct: str
        signedExpiry: str
        signedIdentifier: str
        signedIp: str
        signedPermission: Union[str, Permissions]
        signedProtocol: Union[str, HttpProtocol]
        signedResource: Union[str, SignedResource]
        signedStart: str
        startPk: str
        startRk: str


    class azure.mgmt.storage.types.ServiceSharedKeyAccessProperties(TypedDict, total=False):
        key "enabled": bool
        enabled: bool


    class azure.mgmt.storage.types.SignedIdentifier(TypedDict, total=False):
        key "accessPolicy": ForwardRef('AccessPolicy', module='types')
        key "id": str
        accessPolicy: AccessPolicy
        id: str


    class azure.mgmt.storage.types.Sku(TypedDict, total=False):
        key "name": Required[Union[str, SkuName]]
        key "tier": Union[str, SkuTier]
        name: Union[str, SkuName]
        tier: Union[str, SkuTier]


    class azure.mgmt.storage.types.SmbOAuthSettings(TypedDict, total=False):
        key "isSmbOAuthEnabled": bool
        isSmbOAuthEnabled: bool


    class azure.mgmt.storage.types.SmbSetting(TypedDict, total=False):
        key "authenticationMethods": str
        key "channelEncryption": str
        key "encryptionInTransit": ForwardRef('EncryptionInTransit', module='types')
        key "kerberosTicketEncryption": str
        key "multichannel": ForwardRef('Multichannel', module='types')
        key "versions": str
        authenticationMethods: str
        channelEncryption: str
        encryptionInTransit: EncryptionInTransit
        kerberosTicketEncryption: str
        multichannel: Multichannel
        versions: str


    class azure.mgmt.storage.types.SshPublicKey(TypedDict, total=False):
        key "description": str
        key "key": str
        description: str
        key: str


    class azure.mgmt.storage.types.StaticWebsite(TypedDict, total=False):
        key "defaultIndexDocumentPath": str
        key "enabled": Required[bool]
        key "errorDocument404Path": str
        key "indexDocument": str
        defaultIndexDocumentPath: str
        enabled: bool
        errorDocument404Path: str
        indexDocument: str


    class azure.mgmt.storage.types.StorageAccountCheckNameAvailabilityParameters(TypedDict, total=False):
        key "name": Required[str]
        key "type": Required[Literal["Storage/storageAccounts"]]
        name: str
        type: Literal[Storage/storageAccounts]


    class azure.mgmt.storage.types.StorageAccountCreateParameters(TypedDict, total=False):
        key "extendedLocation": ForwardRef('ExtendedLocation', module='types')
        key "identity": ForwardRef('Identity', module='types')
        key "kind": Required[Union[str, Kind]]
        key "location": Required[str]
        key "placement": ForwardRef('Placement', module='types')
        key "properties": ForwardRef('StorageAccountPropertiesCreateParameters', module='types')
        key "sku": Required[Sku]
        extendedLocation: ExtendedLocation
        identity: Identity
        kind: Union[str, Kind]
        location: str
        placement: Placement
        properties: StorageAccountPropertiesCreateParameters
        sku: Sku
        tags: dict[str, str]
        zones: list[str]


    class azure.mgmt.storage.types.StorageAccountMigration(ProxyResource):
        key "id": str
        key "name": str
        key "properties": Required[StorageAccountMigrationProperties]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: StorageAccountMigrationProperties
        systemData: SystemData
        type: str


    class azure.mgmt.storage.types.StorageAccountMigrationProperties(TypedDict, total=False):
        key "migrationFailedDetailedReason": str
        key "migrationFailedReason": str
        key "migrationStatus": Union[str, MigrationStatus]
        key "targetSkuName": Required[Union[str, SkuName]]
        migrationFailedDetailedReason: str
        migrationFailedReason: str
        migrationStatus: Union[str, MigrationStatus]
        targetSkuName: Union[str, SkuName]


    class azure.mgmt.storage.types.StorageAccountPropertiesCreateParameters(TypedDict, total=False):
        key "accessTier": Union[str, AccessTier]
        key "allowBlobPublicAccess": bool
        key "allowCrossTenantReplication": bool
        key "allowSharedKeyAccess": bool
        key "allowSharedKeyAccessForServices": ForwardRef('StorageAccountSharedKeyAccessProperties', module='types')
        key "allowedCopyScope": Union[str, AllowedCopyScope]
        key "azureFilesIdentityBasedAuthentication": ForwardRef('AzureFilesIdentityBasedAuthentication', module='types')
        key "customDomain": ForwardRef('CustomDomain', module='types')
        key "dataCollaborationPolicyProperties": ForwardRef('StorageDataCollaborationPolicyProperties', module='types')
        key "defaultToOAuthAuthentication": bool
        key "dnsEndpointType": Union[str, DnsEndpointType]
        key "dualStackEndpointPreference": ForwardRef('DualStackEndpointPreference', module='types')
        key "enableExtendedGroups": bool
        key "encryption": ForwardRef('Encryption', module='types')
        key "geoPriorityReplicationStatus": ForwardRef('GeoPriorityReplicationStatus', module='types')
        key "immutableStorageWithVersioning": ForwardRef('ImmutableStorageAccount', module='types')
        key "isHnsEnabled": bool
        key "isLocalUserEnabled": bool
        key "isNfsV3Enabled": bool
        key "isSftpEnabled": bool
        key "keyPolicy": ForwardRef('KeyPolicy', module='types')
        key "largeFileSharesState": Union[str, LargeFileSharesState]
        key "minimumTlsVersion": Union[str, MinimumTlsVersion]
        key "networkAcls": ForwardRef('NetworkRuleSet', module='types')
        key "publicNetworkAccess": Union[str, PublicNetworkAccess]
        key "routingPreference": ForwardRef('RoutingPreference', module='types')
        key "sasPolicy": ForwardRef('SasPolicy', module='types')
        key "supportsHttpsTrafficOnly": bool
        accessTier: Union[str, AccessTier]
        allowBlobPublicAccess: bool
        allowCrossTenantReplication: bool
        allowSharedKeyAccess: bool
        allowSharedKeyAccessForServices: StorageAccountSharedKeyAccessProperties
        allowedCopyScope: Union[str, AllowedCopyScope]
        azureFilesIdentityBasedAuthentication: AzureFilesIdentityBasedAuthentication
        customDomain: CustomDomain
        dataCollaborationPolicyProperties: StorageDataCollaborationPolicyProperties
        defaultToOAuthAuthentication: bool
        dnsEndpointType: Union[str, DnsEndpointType]
        dualStackEndpointPreference: DualStackEndpointPreference
        enableExtendedGroups: bool
        encryption: Encryption
        geoPriorityReplicationStatus: GeoPriorityReplicationStatus
        immutableStorageWithVersioning: ImmutableStorageAccount
        isHnsEnabled: bool
        isLocalUserEnabled: bool
        isNfsV3Enabled: bool
        isSftpEnabled: bool
        keyPolicy: KeyPolicy
        largeFileSharesState: Union[str, LargeFileSharesState]
        minimumTlsVersion: Union[str, MinimumTlsVersion]
        networkAcls: NetworkRuleSet
        publicNetworkAccess: Union[str, PublicNetworkAccess]
        routingPreference: RoutingPreference
        sasPolicy: SasPolicy
        supportsHttpsTrafficOnly: bool


    class azure.mgmt.storage.types.StorageAccountPropertiesUpdateParameters(TypedDict, total=False):
        key "accessTier": Union[str, AccessTier]
        key "allowBlobPublicAccess": bool
        key "allowCrossTenantReplication": bool
        key "allowSharedKeyAccess": bool
        key "allowSharedKeyAccessForServices": ForwardRef('StorageAccountSharedKeyAccessProperties', module='types')
        key "allowedCopyScope": Union[str, AllowedCopyScope]
        key "azureFilesIdentityBasedAuthentication": ForwardRef('AzureFilesIdentityBasedAuthentication', module='types')
        key "customDomain": ForwardRef('CustomDomain', module='types')
        key "dataCollaborationPolicyProperties": ForwardRef('StorageDataCollaborationPolicyProperties', module='types')
        key "defaultToOAuthAuthentication": bool
        key "dnsEndpointType": Union[str, DnsEndpointType]
        key "dualStackEndpointPreference": ForwardRef('DualStackEndpointPreference', module='types')
        key "enableExtendedGroups": bool
        key "encryption": ForwardRef('Encryption', module='types')
        key "geoPriorityReplicationStatus": ForwardRef('GeoPriorityReplicationStatus', module='types')
        key "immutableStorageWithVersioning": ForwardRef('ImmutableStorageAccount', module='types')
        key "isLocalUserEnabled": bool
        key "isSftpEnabled": bool
        key "keyPolicy": ForwardRef('KeyPolicy', module='types')
        key "largeFileSharesState": Union[str, LargeFileSharesState]
        key "minimumTlsVersion": Union[str, MinimumTlsVersion]
        key "networkAcls": ForwardRef('NetworkRuleSet', module='types')
        key "publicNetworkAccess": Union[str, PublicNetworkAccess]
        key "routingPreference": ForwardRef('RoutingPreference', module='types')
        key "sasPolicy": ForwardRef('SasPolicy', module='types')
        key "supportsHttpsTrafficOnly": bool
        accessTier: Union[str, AccessTier]
        allowBlobPublicAccess: bool
        allowCrossTenantReplication: bool
        allowSharedKeyAccess: bool
        allowSharedKeyAccessForServices: StorageAccountSharedKeyAccessProperties
        allowedCopyScope: Union[str, AllowedCopyScope]
        azureFilesIdentityBasedAuthentication: AzureFilesIdentityBasedAuthentication
        customDomain: CustomDomain
        dataCollaborationPolicyProperties: StorageDataCollaborationPolicyProperties
        defaultToOAuthAuthentication: bool
        dnsEndpointType: Union[str, DnsEndpointType]
        dualStackEndpointPreference: DualStackEndpointPreference
        enableExtendedGroups: bool
        encryption: Encryption
        geoPriorityReplicationStatus: GeoPriorityReplicationStatus
        immutableStorageWithVersioning: ImmutableStorageAccount
        isLocalUserEnabled: bool
        isSftpEnabled: bool
        keyPolicy: KeyPolicy
        largeFileSharesState: Union[str, LargeFileSharesState]
        minimumTlsVersion: Union[str, MinimumTlsVersion]
        networkAcls: NetworkRuleSet
        publicNetworkAccess: Union[str, PublicNetworkAccess]
        routingPreference: RoutingPreference
        sasPolicy: SasPolicy
        supportsHttpsTrafficOnly: bool


    class azure.mgmt.storage.types.StorageAccountRegenerateKeyParameters(TypedDict, total=False):
        key "keyName": Required[str]
        keyName: str


    class azure.mgmt.storage.types.StorageAccountSharedKeyAccessProperties(TypedDict, total=False):
        key "blob": ForwardRef('ServiceSharedKeyAccessProperties', module='types')
        key "file": ForwardRef('ServiceSharedKeyAccessProperties', module='types')
        key "queue": ForwardRef('ServiceSharedKeyAccessProperties', module='types')
        key "table": ForwardRef('ServiceSharedKeyAccessProperties', module='types')
        blob: ServiceSharedKeyAccessProperties
        file: ServiceSharedKeyAccessProperties
        queue: ServiceSharedKeyAccessProperties
        table: ServiceSharedKeyAccessProperties


    class azure.mgmt.storage.types.StorageAccountUpdateParameters(TypedDict, total=False):
        key "identity": ForwardRef('Identity', module='types')
        key "kind": Union[str, Kind]
        key "placement": ForwardRef('Placement', module='types')
        key "properties": ForwardRef('StorageAccountPropertiesUpdateParameters', module='types')
        key "sku": ForwardRef('Sku', module='types')
        identity: Identity
        kind: Union[str, Kind]
        placement: Placement
        properties: StorageAccountPropertiesUpdateParameters
        sku: Sku
        tags: dict[str, str]
        zones: list[str]


    class azure.mgmt.storage.types.StorageConnectorAuthProperties(TypedDict, total=False):
        key "identityResourceId": str
        key "type": Required[Literal[StorageConnectorAuthType.MANAGED_IDENTITY]]
        identityResourceId: str
        type: Literal[StorageConnectorAuthType.MANAGED_IDENTITY]


    class azure.mgmt.storage.types.StorageConnectorAuthPropertiesUpdate(TypedDict, total=False):
        key "identityResourceId": str
        key "type": Required[Literal[StorageConnectorAuthType.MANAGED_IDENTITY]]
        identityResourceId: str
        type: Literal[StorageConnectorAuthType.MANAGED_IDENTITY]


    class azure.mgmt.storage.types.StorageConnectorAuthType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MANAGED_IDENTITY = "ManagedIdentity"


    class azure.mgmt.storage.types.StorageConnectorConnection(TypedDict, total=False):
        key "dataShareUri": Required[str]
        key "type": Required[Literal[StorageConnectorConnectionType.DATA_SHARE]]
        dataShareUri: str
        type: Literal[StorageConnectorConnectionType.DATA_SHARE]


    class azure.mgmt.storage.types.StorageConnectorConnectionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DATA_SHARE = "DataShare"


    class azure.mgmt.storage.types.StorageConnectorProperties(TypedDict, total=False):
        key "creationTime": str
        key "dataSourceType": Required[Union[str, StorageConnectorDataSourceType]]
        key "description": str
        key "provisioningState": Union[str, NativeDataSharingProvisioningState]
        key "source": Required[StorageConnectorSource]
        key "state": Union[str, StorageConnectorState]
        key "testConnection": bool
        key "uniqueId": str
        creationTime: str
        dataSourceType: Union[str, StorageConnectorDataSourceType]
        description: str
        provisioningState: Union[str, NativeDataSharingProvisioningState]
        source: StorageConnectorSource
        state: Union[str, StorageConnectorState]
        testConnection: bool
        uniqueId: str


    class azure.mgmt.storage.types.StorageConnectorPropertiesUpdate(TypedDict, total=False):
        key "description": str
        key "source": ForwardRef('StorageConnectorSourceUpdate', module='types')
        key "state": Union[str, StorageConnectorState]
        key "testConnection": bool
        description: str
        source: StorageConnectorSourceUpdate
        state: Union[str, StorageConnectorState]
        testConnection: bool


    class azure.mgmt.storage.types.StorageConnectorSource(TypedDict, total=False):
        key "authProperties": Required[StorageConnectorAuthProperties]
        key "connection": Required[StorageConnectorConnection]
        key "type": Required[Literal[StorageConnectorSourceType.DATA_SHARE]]
        authProperties: StorageConnectorAuthProperties
        connection: StorageConnectorConnection
        type: Literal[StorageConnectorSourceType.DATA_SHARE]


    class azure.mgmt.storage.types.StorageConnectorSourceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DATA_SHARE = "DataShare"


    class azure.mgmt.storage.types.StorageConnectorSourceUpdate(TypedDict, total=False):
        key "authProperties": ForwardRef('StorageConnectorAuthPropertiesUpdate', module='types')
        key "type": Required[Literal[StorageConnectorSourceType.DATA_SHARE]]
        authProperties: StorageConnectorAuthPropertiesUpdate
        type: Literal[StorageConnectorSourceType.DATA_SHARE]


    class azure.mgmt.storage.types.StorageDataCollaborationPolicyProperties(TypedDict, total=False):
        key "allowCrossTenantDataSharing": bool
        key "allowStorageConnectors": bool
        key "allowStorageDataShares": bool
        allowCrossTenantDataSharing: bool
        allowStorageConnectors: bool
        allowStorageDataShares: bool


    class azure.mgmt.storage.types.StorageDataShareAccessPolicy(TypedDict, total=False):
        key "permission": Required[Union[str, StorageDataShareAccessPolicyPermission]]
        key "principalId": Required[str]
        key "tenantId": Required[str]
        permission: Union[str, StorageDataShareAccessPolicyPermission]
        principalId: str
        tenantId: str


    class azure.mgmt.storage.types.StorageDataShareAsset(TypedDict, total=False):
        key "assetPath": Required[str]
        key "displayName": Required[str]
        assetPath: str
        displayName: str


    class azure.mgmt.storage.types.StorageDataShareProperties(TypedDict, total=False):
        key "accessPolicies": Required[list[StorageDataShareAccessPolicy]]
        key "assets": Required[list[StorageDataShareAsset]]
        key "dataShareIdentifier": str
        key "dataShareUri": str
        key "description": str
        key "provisioningState": Union[str, NativeDataSharingProvisioningState]
        accessPolicies: list[StorageDataShareAccessPolicy]
        assets: list[StorageDataShareAsset]
        dataShareIdentifier: str
        dataShareUri: str
        description: str
        provisioningState: Union[str, NativeDataSharingProvisioningState]


    class azure.mgmt.storage.types.StorageDataSharePropertiesUpdate(TypedDict, total=False):
        key "description": str
        accessPolicies: list[StorageDataShareAccessPolicy]
        assets: list[StorageDataShareAsset]
        description: str


    class azure.mgmt.storage.types.StorageQueue(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('QueueProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: QueueProperties
        systemData: SystemData
        type: str


    class azure.mgmt.storage.types.StorageTaskAssignment(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('StorageTaskAssignmentProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: StorageTaskAssignmentProperties
        systemData: SystemData
        type: str


    class azure.mgmt.storage.types.StorageTaskAssignmentExecutionContext(TypedDict, total=False):
        key "target": ForwardRef('ExecutionTarget', module='types')
        key "trigger": Required[ExecutionTrigger]
        target: ExecutionTarget
        trigger: ExecutionTrigger


    class azure.mgmt.storage.types.StorageTaskAssignmentProperties(TypedDict, total=False):
        key "description": Required[str]
        key "enabled": Required[bool]
        key "executionContext": Required[StorageTaskAssignmentExecutionContext]
        key "provisioningState": Union[str, StorageTaskAssignmentProvisioningState]
        key "report": Required[StorageTaskAssignmentReport]
        key "runStatus": ForwardRef('StorageTaskReportProperties', module='types')
        key "taskId": Required[str]
        description: str
        enabled: bool
        executionContext: StorageTaskAssignmentExecutionContext
        provisioningState: Union[str, StorageTaskAssignmentProvisioningState]
        report: StorageTaskAssignmentReport
        runStatus: StorageTaskReportProperties
        taskId: str


    class azure.mgmt.storage.types.StorageTaskAssignmentReport(TypedDict, total=False):
        key "prefix": Required[str]
        prefix: str


    class azure.mgmt.storage.types.StorageTaskAssignmentUpdateExecutionContext(TypedDict, total=False):
        key "target": ForwardRef('ExecutionTarget', module='types')
        key "trigger": ForwardRef('ExecutionTriggerUpdate', module='types')
        target: ExecutionTarget
        trigger: ExecutionTriggerUpdate


    class azure.mgmt.storage.types.StorageTaskAssignmentUpdateParameters(TypedDict, total=False):
        key "properties": ForwardRef('StorageTaskAssignmentUpdateProperties', module='types')
        properties: StorageTaskAssignmentUpdateProperties


    class azure.mgmt.storage.types.StorageTaskAssignmentUpdateProperties(TypedDict, total=False):
        key "description": str
        key "enabled": bool
        key "executionContext": ForwardRef('StorageTaskAssignmentUpdateExecutionContext', module='types')
        key "provisioningState": Union[str, StorageTaskAssignmentProvisioningState]
        key "report": ForwardRef('StorageTaskAssignmentUpdateReport', module='types')
        key "runStatus": ForwardRef('StorageTaskReportProperties', module='types')
        key "taskId": str
        description: str
        enabled: bool
        executionContext: StorageTaskAssignmentUpdateExecutionContext
        provisioningState: Union[str, StorageTaskAssignmentProvisioningState]
        report: StorageTaskAssignmentUpdateReport
        runStatus: StorageTaskReportProperties
        taskId: str


    class azure.mgmt.storage.types.StorageTaskAssignmentUpdateReport(TypedDict, total=False):
        key "prefix": str
        prefix: str


    class azure.mgmt.storage.types.StorageTaskReportProperties(TypedDict, total=False):
        key "finishTime": str
        key "objectFailedCount": str
        key "objectsOperatedOnCount": str
        key "objectsSucceededCount": str
        key "objectsTargetedCount": str
        key "runResult": Union[str, RunResult]
        key "runStatusEnum": Union[str, RunStatusEnum]
        key "runStatusError": str
        key "startTime": str
        key "storageAccountId": str
        key "summaryReportPath": str
        key "taskAssignmentId": str
        key "taskId": str
        key "taskVersion": str
        finishTime: str
        objectFailedCount: str
        objectsOperatedOnCount: str
        objectsSucceededCount: str
        objectsTargetedCount: str
        runResult: Union[str, RunResult]
        runStatusEnum: Union[str, RunStatusEnum]
        runStatusError: str
        startTime: str
        storageAccountId: str
        summaryReportPath: str
        taskAssignmentId: str
        taskId: str
        taskVersion: str


    class azure.mgmt.storage.types.SystemData(TypedDict, total=False):
        key "createdAt": str
        key "createdBy": str
        key "createdByType": Union[str, CreatedByType]
        key "lastModifiedAt": str
        key "lastModifiedBy": str
        key "lastModifiedByType": Union[str, CreatedByType]
        createdAt: str
        createdBy: str
        createdByType: Union[str, CreatedByType]
        lastModifiedAt: str
        lastModifiedBy: str
        lastModifiedByType: Union[str, CreatedByType]


    class azure.mgmt.storage.types.Table(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('TableProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: TableProperties
        systemData: SystemData
        type: str


    class azure.mgmt.storage.types.TableAccessPolicy(TypedDict, total=False):
        key "expiryTime": str
        key "permission": Required[str]
        key "startTime": str
        expiryTime: str
        permission: str
        startTime: str


    class azure.mgmt.storage.types.TableProperties(TypedDict, total=False):
        key "tableName": str
        signedIdentifiers: list[TableSignedIdentifier]
        tableName: str


    class azure.mgmt.storage.types.TableServiceProperties(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('TableServicePropertiesProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: TableServicePropertiesProperties
        systemData: SystemData
        type: str


    class azure.mgmt.storage.types.TableServicePropertiesProperties(TypedDict, total=False):
        key "cors": ForwardRef('CorsRules', module='types')
        cors: CorsRules


    class azure.mgmt.storage.types.TableSignedIdentifier(TypedDict, total=False):
        key "accessPolicy": ForwardRef('TableAccessPolicy', module='types')
        key "id": Required[str]
        accessPolicy: TableAccessPolicy
        id: str


    class azure.mgmt.storage.types.TagFilter(TypedDict, total=False):
        key "name": Required[str]
        key "op": Required[str]
        key "value": Required[str]
        name: str
        op: str
        value: str


    class azure.mgmt.storage.types.TagProperty(TypedDict, total=False):
        key "objectIdentifier": str
        key "tag": str
        key "tenantId": str
        key "timestamp": str
        key "upn": str
        objectIdentifier: str
        tag: str
        tenantId: str
        timestamp: str
        upn: str


    class azure.mgmt.storage.types.TestExistingConnectionRequest(TypedDict, total=False):
        key "uniqueId": Required[str]
        uniqueId: str


    class azure.mgmt.storage.types.TrackedResource(ResourceAutoGenerated):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.storage.types.TrackedResourceUpdate(ResourceAutoGenerated):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.storage.types.TriggerParameters(TypedDict, total=False):
        key "endBy": str
        key "interval": int
        key "intervalUnit": Union[str, IntervalUnit]
        key "startFrom": str
        key "startOn": str
        endBy: str
        interval: int
        intervalUnit: Union[str, IntervalUnit]
        startFrom: str
        startOn: str


    class azure.mgmt.storage.types.TriggerParametersUpdate(TypedDict, total=False):
        key "endBy": str
        key "interval": int
        key "intervalUnit": Union[str, IntervalUnit]
        key "startFrom": str
        key "startOn": str
        endBy: str
        interval: int
        intervalUnit: Union[str, IntervalUnit]
        startFrom: str
        startOn: str


    class azure.mgmt.storage.types.UpdateHistoryProperty(TypedDict, total=False):
        key "allowProtectedAppendWrites": bool
        key "allowProtectedAppendWritesAll": bool
        key "immutabilityPeriodSinceCreationInDays": int
        key "objectIdentifier": str
        key "tenantId": str
        key "timestamp": str
        key "update": Union[str, ImmutabilityPolicyUpdateType]
        key "upn": str
        allowProtectedAppendWrites: bool
        allowProtectedAppendWritesAll: bool
        immutabilityPeriodSinceCreationInDays: int
        objectIdentifier: str
        tenantId: str
        timestamp: str
        update: Union[str, ImmutabilityPolicyUpdateType]
        upn: str


    class azure.mgmt.storage.types.UserAssignedIdentity(TypedDict, total=False):
        key "clientId": str
        key "principalId": str
        clientId: str
        principalId: str


    class azure.mgmt.storage.types.VirtualNetworkRule(TypedDict, total=False):
        key "action": Literal["Allow"]
        key "id": Required[str]
        key "state": Union[str, State]
        action: Literal[Allow]
        id: str
        state: Union[str, State]


```