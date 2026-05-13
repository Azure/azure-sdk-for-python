```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.storage

    class azure.mgmt.storage.StorageManagementClient: implements ContextManager 
        blob_containers: BlobContainersOperations
        blob_inventory_policies: BlobInventoryPoliciesOperations
        blob_services: BlobServicesOperations
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


namespace azure.mgmt.storage.aio

    class azure.mgmt.storage.aio.StorageManagementClient: implements AsyncContextManager 
        blob_containers: BlobContainersOperations
        blob_inventory_policies: BlobInventoryPoliciesOperations
        blob_services: BlobServicesOperations
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


namespace azure.mgmt.storage.aio.operations

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
                if_match: Optional[str] = None, 
                parameters: Optional[ImmutabilityPolicy] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ImmutabilityPolicy: ...

        @overload
        async def create_or_update_immutability_policy(
                self, 
                resource_group_name: str, 
                account_name: str, 
                container_name: str, 
                if_match: Optional[str] = None, 
                parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
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
                if_match: str, 
                **kwargs: Any
            ) -> ImmutabilityPolicy: ...

        @overload
        async def extend_immutability_policy(
                self, 
                resource_group_name: str, 
                account_name: str, 
                container_name: str, 
                if_match: str, 
                parameters: Optional[ImmutabilityPolicy] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ImmutabilityPolicy: ...

        @overload
        async def extend_immutability_policy(
                self, 
                resource_group_name: str, 
                account_name: str, 
                container_name: str, 
                if_match: str, 
                parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
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
                if_match: Optional[str] = None, 
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
                maxpagesize: Optional[str] = None, 
                filter: Optional[str] = None, 
                include: Optional[Union[str, ListContainersInclude]] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[ListContainerItem]: ...

        @distributed_trace_async
        async def lock_immutability_policy(
                self, 
                resource_group_name: str, 
                account_name: str, 
                container_name: str, 
                if_match: str, 
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
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BlobServiceProperties: ...


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
                maxpagesize: Optional[int] = None, 
                filter: Optional[str] = None, 
                include: Optional[Union[str, ListEncryptionScopesInclude]] = None, 
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
                maxpagesize: Optional[int] = None, 
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
                expand: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FileShare: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_name: str, 
                file_share: IO[bytes], 
                expand: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FileShare: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_name: str, 
                x_ms_snapshot: Optional[str] = None, 
                include: Optional[str] = None, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_name: str, 
                expand: Optional[str] = None, 
                x_ms_snapshot: Optional[str] = None, 
                **kwargs: Any
            ) -> FileShare: ...

        @overload
        async def lease(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_name: str, 
                x_ms_snapshot: Optional[str] = None, 
                parameters: Optional[LeaseShareRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LeaseShareResponse: ...

        @overload
        async def lease(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_name: str, 
                x_ms_snapshot: Optional[str] = None, 
                parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LeaseShareResponse: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                account_name: str, 
                maxpagesize: Optional[str] = None, 
                filter: Optional[str] = None, 
                expand: Optional[str] = None, 
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
                maxpagesize: Optional[int] = None, 
                filter: Optional[str] = None, 
                include: Optional[Union[str, ListLocalUserIncludeParam]] = None, 
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
                maxpagesize: Optional[str] = None, 
                filter: Optional[str] = None, 
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
                failover_type: Literal["Planned"] = "Planned", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_hierarchical_namespace_migration(
                self, 
                resource_group_name: str, 
                account_name: str, 
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
                expand: Optional[Union[str, StorageAccountExpand]] = None, 
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
                maxpagesize: Optional[int] = None, 
                filter: Optional[str] = None, 
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
                maxpagesize: Optional[int] = None, 
                filter: Optional[str] = None, 
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
                top: Optional[int] = None, 
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

    class azure.mgmt.storage.models.AccessPolicy(Model):
        expiry_time: datetime
        permission: str
        start_time: datetime

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                expiry_time: Optional[datetime] = ..., 
                permission: Optional[str] = ..., 
                start_time: Optional[datetime] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.AccessTier(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COLD = "Cold"
        COOL = "Cool"
        HOT = "Hot"
        PREMIUM = "Premium"


    class azure.mgmt.storage.models.AccountImmutabilityPolicyProperties(Model):
        allow_protected_append_writes: bool
        immutability_period_since_creation_in_days: int
        state: Union[str, AccountImmutabilityPolicyState]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                allow_protected_append_writes: Optional[bool] = ..., 
                immutability_period_since_creation_in_days: Optional[int] = ..., 
                state: Optional[Union[str, AccountImmutabilityPolicyState]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.AccountImmutabilityPolicyState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        LOCKED = "Locked"
        UNLOCKED = "Unlocked"


    class azure.mgmt.storage.models.AccountLimits(Model):
        max_file_shares: int
        max_provisioned_bandwidth_mi_b_per_sec: int
        max_provisioned_iops: int
        max_provisioned_storage_gi_b: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.AccountSasParameters(Model):
        ip_address_or_range: str
        key_to_sign: str
        permissions: Union[str, Permissions]
        protocols: Union[str, HttpProtocol]
        resource_types: Union[str, SignedResourceTypes]
        services: Union[str, Services]
        shared_access_expiry_time: datetime
        shared_access_start_time: datetime

        def __eq__(self, other: Any) -> bool: ...

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
                shared_access_start_time: Optional[datetime] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.AccountStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVAILABLE = "available"
        UNAVAILABLE = "unavailable"


    class azure.mgmt.storage.models.AccountType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPUTER = "Computer"
        USER = "User"


    class azure.mgmt.storage.models.AccountUsage(Model):
        live_shares: AccountUsageElements
        soft_deleted_shares: AccountUsageElements

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.AccountUsageElements(Model):
        file_share_count: int
        provisioned_bandwidth_mi_b_per_sec: int
        provisioned_iops: int
        provisioned_storage_gi_b: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.ActiveDirectoryProperties(Model):
        account_type: Union[str, AccountType]
        azure_storage_sid: str
        domain_guid: str
        domain_name: str
        domain_sid: str
        forest_name: str
        net_bios_domain_name: str
        sam_account_name: str

        def __eq__(self, other: Any) -> bool: ...

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
                sam_account_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.AllowedCopyScope(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AAD = "AAD"
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


    class azure.mgmt.storage.models.AzureEntityResource(Resource):
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
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.AzureFilesIdentityBasedAuthentication(Model):
        active_directory_properties: ActiveDirectoryProperties
        default_share_permission: Union[str, DefaultSharePermission]
        directory_service_options: Union[str, DirectoryServiceOptions]
        smb_o_auth_settings: SmbOAuthSettings

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                active_directory_properties: Optional[ActiveDirectoryProperties] = ..., 
                default_share_permission: Optional[Union[str, DefaultSharePermission]] = ..., 
                directory_service_options: Union[str, DirectoryServiceOptions], 
                smb_o_auth_settings: Optional[SmbOAuthSettings] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.BlobContainer(AzureEntityResource):
        default_encryption_scope: str
        deleted: bool
        deleted_time: datetime
        deny_encryption_scope_override: bool
        enable_nfs_v3_all_squash: bool
        enable_nfs_v3_root_squash: bool
        etag: str
        has_immutability_policy: bool
        has_legal_hold: bool
        id: str
        immutability_policy: ImmutabilityPolicyProperties
        immutable_storage_with_versioning: ImmutableStorageWithVersioning
        last_modified_time: datetime
        lease_duration: Union[str, LeaseDuration]
        lease_state: Union[str, LeaseState]
        lease_status: Union[str, LeaseStatus]
        legal_hold: LegalHoldProperties
        metadata: dict[str, str]
        name: str
        public_access: Union[str, PublicAccess]
        remaining_retention_days: int
        type: str
        version: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                default_encryption_scope: Optional[str] = ..., 
                deny_encryption_scope_override: Optional[bool] = ..., 
                enable_nfs_v3_all_squash: Optional[bool] = ..., 
                enable_nfs_v3_root_squash: Optional[bool] = ..., 
                immutable_storage_with_versioning: Optional[ImmutableStorageWithVersioning] = ..., 
                metadata: Optional[dict[str, str]] = ..., 
                public_access: Optional[Union[str, PublicAccess]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.BlobInventoryCreationTime(Model):
        last_n_days: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                last_n_days: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.BlobInventoryPolicy(Resource):
        id: str
        last_modified_time: datetime
        name: str
        policy: BlobInventoryPolicySchema
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                policy: Optional[BlobInventoryPolicySchema] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.BlobInventoryPolicyDefinition(Model):
        filters: BlobInventoryPolicyFilter
        format: Union[str, Format]
        object_type: Union[str, ObjectType]
        schedule: Union[str, Schedule]
        schema_fields: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                filters: Optional[BlobInventoryPolicyFilter] = ..., 
                format: Union[str, Format], 
                object_type: Union[str, ObjectType], 
                schedule: Union[str, Schedule], 
                schema_fields: list[str], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.BlobInventoryPolicyFilter(Model):
        blob_types: list[str]
        creation_time: BlobInventoryCreationTime
        exclude_prefix: list[str]
        include_blob_versions: bool
        include_deleted: bool
        include_snapshots: bool
        prefix_match: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                blob_types: Optional[list[str]] = ..., 
                creation_time: Optional[BlobInventoryCreationTime] = ..., 
                exclude_prefix: Optional[list[str]] = ..., 
                include_blob_versions: Optional[bool] = ..., 
                include_deleted: Optional[bool] = ..., 
                include_snapshots: Optional[bool] = ..., 
                prefix_match: Optional[list[str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.BlobInventoryPolicyName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEFAULT = "default"


    class azure.mgmt.storage.models.BlobInventoryPolicyRule(Model):
        definition: BlobInventoryPolicyDefinition
        destination: str
        enabled: bool
        name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                definition: BlobInventoryPolicyDefinition, 
                destination: str, 
                enabled: bool, 
                name: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.BlobInventoryPolicySchema(Model):
        destination: str
        enabled: bool
        rules: list[BlobInventoryPolicyRule]
        type: Union[str, InventoryRuleType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                enabled: bool, 
                rules: list[BlobInventoryPolicyRule], 
                type: Union[str, InventoryRuleType], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.BlobRestoreParameters(Model):
        blob_ranges: list[BlobRestoreRange]
        time_to_restore: datetime

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                blob_ranges: list[BlobRestoreRange], 
                time_to_restore: datetime, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.BlobRestoreProgressStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLETE = "Complete"
        FAILED = "Failed"
        IN_PROGRESS = "InProgress"


    class azure.mgmt.storage.models.BlobRestoreRange(Model):
        end_range: str
        start_range: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                end_range: str, 
                start_range: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.BlobRestoreStatus(Model):
        failure_reason: str
        parameters: BlobRestoreParameters
        restore_id: str
        status: Union[str, BlobRestoreProgressStatus]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.BlobServiceItems(Model):
        value: list[BlobServiceProperties]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.BlobServiceProperties(Resource):
        automatic_snapshot_policy_enabled: bool
        change_feed: ChangeFeed
        container_delete_retention_policy: DeleteRetentionPolicy
        cors: CorsRules
        default_service_version: str
        delete_retention_policy: DeleteRetentionPolicy
        id: str
        is_versioning_enabled: bool
        last_access_time_tracking_policy: LastAccessTimeTrackingPolicy
        name: str
        restore_policy: RestorePolicyProperties
        sku: Sku
        type: str

        def __eq__(self, other: Any) -> bool: ...

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
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.BurstingConstants(Model):
        burst_floor_iops: int
        burst_io_scalar: float
        burst_timeframe_seconds: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.Bypass(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_SERVICES = "AzureServices"
        LOGGING = "Logging"
        METRICS = "Metrics"
        NONE = "None"


    class azure.mgmt.storage.models.ChangeFeed(Model):
        enabled: bool
        retention_in_days: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ..., 
                retention_in_days: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.CheckNameAvailabilityResult(Model):
        message: str
        name_available: bool
        reason: Union[str, Reason]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.CloudErrorBody(Model):
        code: str
        details: list[CloudErrorBody]
        message: str
        target: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                details: Optional[list[CloudErrorBody]] = ..., 
                message: Optional[str] = ..., 
                target: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.CorsRule(Model):
        allowed_headers: list[str]
        allowed_methods: Union[list[str, AllowedMethods]]
        allowed_origins: list[str]
        exposed_headers: list[str]
        max_age_in_seconds: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                allowed_headers: list[str], 
                allowed_methods: list[Union[str, AllowedMethods]], 
                allowed_origins: list[str], 
                exposed_headers: list[str], 
                max_age_in_seconds: int, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.CorsRules(Model):
        cors_rules: list[CorsRule]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                cors_rules: Optional[list[CorsRule]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.storage.models.CustomDomain(Model):
        name: str
        use_sub_domain_name: bool

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                name: str, 
                use_sub_domain_name: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.DateAfterCreation(Model):
        days_after_creation_greater_than: float
        days_after_last_tier_change_greater_than: float

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                days_after_creation_greater_than: float, 
                days_after_last_tier_change_greater_than: Optional[float] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.DateAfterModification(Model):
        days_after_creation_greater_than: float
        days_after_last_access_time_greater_than: float
        days_after_last_tier_change_greater_than: float
        days_after_modification_greater_than: float

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                days_after_creation_greater_than: Optional[float] = ..., 
                days_after_last_access_time_greater_than: Optional[float] = ..., 
                days_after_last_tier_change_greater_than: Optional[float] = ..., 
                days_after_modification_greater_than: Optional[float] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.DefaultAction(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALLOW = "Allow"
        DENY = "Deny"


    class azure.mgmt.storage.models.DefaultSharePermission(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        STORAGE_FILE_DATA_SMB_SHARE_CONTRIBUTOR = "StorageFileDataSmbShareContributor"
        STORAGE_FILE_DATA_SMB_SHARE_ELEVATED_CONTRIBUTOR = "StorageFileDataSmbShareElevatedContributor"
        STORAGE_FILE_DATA_SMB_SHARE_READER = "StorageFileDataSmbShareReader"


    class azure.mgmt.storage.models.DeleteRetentionPolicy(Model):
        allow_permanent_delete: bool
        days: int
        enabled: bool

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                allow_permanent_delete: Optional[bool] = ..., 
                days: Optional[int] = ..., 
                enabled: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.DeletedAccount(ProxyResource):
        creation_time: str
        deletion_time: str
        id: str
        location: str
        name: str
        restore_reference: str
        storage_account_resource_id: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.DeletedAccountListResult(Model):
        next_link: str
        value: list[DeletedAccount]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.DeletedShare(Model):
        deleted_share_name: str
        deleted_share_version: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                deleted_share_name: str, 
                deleted_share_version: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.Dimension(Model):
        display_name: str
        name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ..., 
                name: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.DirectoryServiceOptions(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AADDS = "AADDS"
        AADKERB = "AADKERB"
        AD = "AD"
        NONE = "None"


    class azure.mgmt.storage.models.DnsEndpointType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_DNS_ZONE = "AzureDnsZone"
        STANDARD = "Standard"


    class azure.mgmt.storage.models.DualStackEndpointPreference(Model):
        publish_ipv6_endpoint: bool

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                publish_ipv6_endpoint: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.EnabledProtocols(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NFS = "NFS"
        SMB = "SMB"


    class azure.mgmt.storage.models.Encryption(Model):
        encryption_identity: EncryptionIdentity
        key_source: Union[str, KeySource]
        key_vault_properties: KeyVaultProperties
        require_infrastructure_encryption: bool
        services: EncryptionServices

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                encryption_identity: Optional[EncryptionIdentity] = ..., 
                key_source: Union[str, KeySource] = "Microsoft.Storage", 
                key_vault_properties: Optional[KeyVaultProperties] = ..., 
                require_infrastructure_encryption: Optional[bool] = ..., 
                services: Optional[EncryptionServices] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.EncryptionIdentity(Model):
        encryption_federated_identity_client_id: str
        encryption_user_assigned_identity: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                encryption_federated_identity_client_id: Optional[str] = ..., 
                encryption_user_assigned_identity: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.EncryptionInTransit(Model):
        required: bool

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                required: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.EncryptionScope(Resource):
        creation_time: datetime
        id: str
        key_vault_properties: EncryptionScopeKeyVaultProperties
        last_modified_time: datetime
        name: str
        require_infrastructure_encryption: bool
        source: Union[str, EncryptionScopeSource]
        state: Union[str, EncryptionScopeState]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                key_vault_properties: Optional[EncryptionScopeKeyVaultProperties] = ..., 
                require_infrastructure_encryption: Optional[bool] = ..., 
                source: Optional[Union[str, EncryptionScopeSource]] = ..., 
                state: Optional[Union[str, EncryptionScopeState]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.EncryptionScopeKeyVaultProperties(Model):
        current_versioned_key_identifier: str
        key_uri: str
        last_key_rotation_timestamp: datetime

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                key_uri: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.EncryptionScopeListResult(Model):
        next_link: str
        value: list[EncryptionScope]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.EncryptionScopeSource(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MICROSOFT_KEY_VAULT = "Microsoft.KeyVault"
        MICROSOFT_STORAGE = "Microsoft.Storage"


    class azure.mgmt.storage.models.EncryptionScopeState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.storage.models.EncryptionService(Model):
        enabled: bool
        key_type: Union[str, KeyType]
        last_enabled_time: datetime

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ..., 
                key_type: Optional[Union[str, KeyType]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.EncryptionServices(Model):
        blob: EncryptionService
        file: EncryptionService
        queue: EncryptionService
        table: EncryptionService

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                blob: Optional[EncryptionService] = ..., 
                file: Optional[EncryptionService] = ..., 
                queue: Optional[EncryptionService] = ..., 
                table: Optional[EncryptionService] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.Endpoints(Model):
        blob: str
        dfs: str
        file: str
        internet_endpoints: StorageAccountInternetEndpoints
        ipv6_endpoints: StorageAccountIpv6Endpoints
        microsoft_endpoints: StorageAccountMicrosoftEndpoints
        queue: str
        table: str
        web: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                internet_endpoints: Optional[StorageAccountInternetEndpoints] = ..., 
                ipv6_endpoints: Optional[StorageAccountIpv6Endpoints] = ..., 
                microsoft_endpoints: Optional[StorageAccountMicrosoftEndpoints] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.ErrorAdditionalInfo(Model):
        info: JSON
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.ErrorDetail(Model):
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
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.ErrorResponse(Model):
        error: ErrorResponseBody

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                error: Optional[ErrorResponseBody] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.ErrorResponseAutoGenerated(Model):
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
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.ErrorResponseBody(Model):
        code: str
        message: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                message: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.ExecutionTarget(Model):
        exclude_prefix: list[str]
        prefix: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                exclude_prefix: Optional[list[str]] = ..., 
                prefix: Optional[list[str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.ExecutionTrigger(Model):
        parameters: TriggerParameters
        type: Union[str, TriggerType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                parameters: TriggerParameters, 
                type: Union[str, TriggerType], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.ExecutionTriggerUpdate(Model):
        parameters: TriggerParametersUpdate
        type: Union[str, TriggerType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                parameters: Optional[TriggerParametersUpdate] = ..., 
                type: Optional[Union[str, TriggerType]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.ExpirationAction(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BLOCK = "Block"
        LOG = "Log"


    class azure.mgmt.storage.models.ExtendedLocation(Model):
        name: str
        type: Union[str, ExtendedLocationTypes]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                type: Optional[Union[str, ExtendedLocationTypes]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.ExtendedLocationTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EDGE_ZONE = "EdgeZone"


    class azure.mgmt.storage.models.FileServiceItems(Model):
        value: list[FileServiceProperties]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.FileServiceProperties(Resource):
        cors: CorsRules
        id: str
        name: str
        protocol_settings: ProtocolSettings
        share_delete_retention_policy: DeleteRetentionPolicy
        sku: Sku
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                cors: Optional[CorsRules] = ..., 
                protocol_settings: Optional[ProtocolSettings] = ..., 
                share_delete_retention_policy: Optional[DeleteRetentionPolicy] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.FileServiceUsage(Resource):
        id: str
        name: str
        properties: FileServiceUsageProperties
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.FileServiceUsageProperties(Model):
        bursting_constants: BurstingConstants
        file_share_limits: FileShareLimits
        file_share_recommendations: FileShareRecommendations
        storage_account_limits: AccountLimits
        storage_account_usage: AccountUsage

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.FileServiceUsages(Model):
        next_link: str
        value: list[FileServiceUsage]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.FileShare(AzureEntityResource):
        access_tier: Union[str, ShareAccessTier]
        access_tier_change_time: datetime
        access_tier_status: str
        deleted: bool
        deleted_time: datetime
        enabled_protocols: Union[str, EnabledProtocols]
        etag: str
        file_share_paid_bursting: FileSharePropertiesFileSharePaidBursting
        id: str
        included_burst_iops: int
        last_modified_time: datetime
        lease_duration: Union[str, LeaseDuration]
        lease_state: Union[str, LeaseState]
        lease_status: Union[str, LeaseStatus]
        max_burst_credits_for_iops: int
        metadata: dict[str, str]
        name: str
        next_allowed_provisioned_bandwidth_downgrade_time: datetime
        next_allowed_provisioned_iops_downgrade_time: datetime
        next_allowed_quota_downgrade_time: datetime
        provisioned_bandwidth_mibps: int
        provisioned_iops: int
        remaining_retention_days: int
        root_squash: Union[str, RootSquashType]
        share_quota: int
        share_usage_bytes: int
        signed_identifiers: list[SignedIdentifier]
        snapshot_time: datetime
        type: str
        version: str

        def __eq__(self, other: Any) -> bool: ...

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
                signed_identifiers: Optional[list[SignedIdentifier]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.FileShareItem(AzureEntityResource):
        access_tier: Union[str, ShareAccessTier]
        access_tier_change_time: datetime
        access_tier_status: str
        deleted: bool
        deleted_time: datetime
        enabled_protocols: Union[str, EnabledProtocols]
        etag: str
        file_share_paid_bursting: FileSharePropertiesFileSharePaidBursting
        id: str
        included_burst_iops: int
        last_modified_time: datetime
        lease_duration: Union[str, LeaseDuration]
        lease_state: Union[str, LeaseState]
        lease_status: Union[str, LeaseStatus]
        max_burst_credits_for_iops: int
        metadata: dict[str, str]
        name: str
        next_allowed_provisioned_bandwidth_downgrade_time: datetime
        next_allowed_provisioned_iops_downgrade_time: datetime
        next_allowed_quota_downgrade_time: datetime
        provisioned_bandwidth_mibps: int
        provisioned_iops: int
        remaining_retention_days: int
        root_squash: Union[str, RootSquashType]
        share_quota: int
        share_usage_bytes: int
        signed_identifiers: list[SignedIdentifier]
        snapshot_time: datetime
        type: str
        version: str

        def __eq__(self, other: Any) -> bool: ...

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
                signed_identifiers: Optional[list[SignedIdentifier]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.FileShareItems(Model):
        next_link: str
        value: list[FileShareItem]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.FileShareLimits(Model):
        max_provisioned_bandwidth_mi_b_per_sec: int
        max_provisioned_iops: int
        max_provisioned_storage_gi_b: int
        min_provisioned_bandwidth_mi_b_per_sec: int
        min_provisioned_iops: int
        min_provisioned_storage_gi_b: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.FileSharePropertiesFileSharePaidBursting(Model):
        paid_bursting_enabled: bool
        paid_bursting_max_bandwidth_mibps: int
        paid_bursting_max_iops: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                paid_bursting_enabled: Optional[bool] = ..., 
                paid_bursting_max_bandwidth_mibps: Optional[int] = ..., 
                paid_bursting_max_iops: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.FileShareRecommendations(Model):
        bandwidth_scalar: float
        base_bandwidth_mi_b_per_sec: int
        base_iops: int
        io_scalar: float

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.Format(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CSV = "Csv"
        PARQUET = "Parquet"


    class azure.mgmt.storage.models.GeoPriorityReplicationStatus(Model):
        is_blob_enabled: bool

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                is_blob_enabled: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.GeoReplicationStats(Model):
        can_failover: bool
        can_planned_failover: bool
        last_sync_time: datetime
        post_failover_redundancy: Union[str, PostFailoverRedundancy]
        post_planned_failover_redundancy: Union[str, PostPlannedFailoverRedundancy]
        status: Union[str, GeoReplicationStatus]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.GeoReplicationStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BOOTSTRAP = "Bootstrap"
        LIVE = "Live"
        UNAVAILABLE = "Unavailable"


    class azure.mgmt.storage.models.HttpProtocol(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HTTPS = "https"
        HTTPS_HTTP = "https,http"


    class azure.mgmt.storage.models.IPRule(Model):
        action: str
        ip_address_or_range: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                action: Optional[Literal[Allow]] = ..., 
                ip_address_or_range: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.Identity(Model):
        principal_id: str
        tenant_id: str
        type: Union[str, IdentityType]
        user_assigned_identities: dict[str, UserAssignedIdentity]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                type: Union[str, IdentityType], 
                user_assigned_identities: Optional[dict[str, UserAssignedIdentity]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.IdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        SYSTEM_ASSIGNED_USER_ASSIGNED = "SystemAssigned,UserAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.storage.models.ImmutabilityPolicy(AzureEntityResource):
        allow_protected_append_writes: bool
        allow_protected_append_writes_all: bool
        etag: str
        id: str
        immutability_period_since_creation_in_days: int
        name: str
        state: Union[str, ImmutabilityPolicyState]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                allow_protected_append_writes: Optional[bool] = ..., 
                allow_protected_append_writes_all: Optional[bool] = ..., 
                immutability_period_since_creation_in_days: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.ImmutabilityPolicyProperties(Model):
        allow_protected_append_writes: bool
        allow_protected_append_writes_all: bool
        etag: str
        immutability_period_since_creation_in_days: int
        state: Union[str, ImmutabilityPolicyState]
        update_history: list[UpdateHistoryProperty]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                allow_protected_append_writes: Optional[bool] = ..., 
                allow_protected_append_writes_all: Optional[bool] = ..., 
                immutability_period_since_creation_in_days: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.ImmutabilityPolicyState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LOCKED = "Locked"
        UNLOCKED = "Unlocked"


    class azure.mgmt.storage.models.ImmutabilityPolicyUpdateType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EXTEND = "extend"
        LOCK = "lock"
        PUT = "put"


    class azure.mgmt.storage.models.ImmutableStorageAccount(Model):
        enabled: bool
        immutability_policy: AccountImmutabilityPolicyProperties

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ..., 
                immutability_policy: Optional[AccountImmutabilityPolicyProperties] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.ImmutableStorageWithVersioning(Model):
        enabled: bool
        migration_state: Union[str, MigrationState]
        time_stamp: datetime

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.IntervalUnit(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DAYS = "Days"


    class azure.mgmt.storage.models.InventoryRuleType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INVENTORY = "Inventory"


    class azure.mgmt.storage.models.IssueType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONFIGURATION_PROPAGATION_FAILURE = "ConfigurationPropagationFailure"
        UNKNOWN = "Unknown"


    class azure.mgmt.storage.models.KeyCreationTime(Model):
        key1: datetime
        key2: datetime

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                key1: Optional[datetime] = ..., 
                key2: Optional[datetime] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.KeyPermission(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FULL = "Full"
        READ = "Read"


    class azure.mgmt.storage.models.KeyPolicy(Model):
        key_expiration_period_in_days: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                key_expiration_period_in_days: int, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.KeySource(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MICROSOFT_KEYVAULT = "Microsoft.Keyvault"
        MICROSOFT_STORAGE = "Microsoft.Storage"


    class azure.mgmt.storage.models.KeyType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCOUNT = "Account"
        SERVICE = "Service"


    class azure.mgmt.storage.models.KeyVaultProperties(Model):
        current_versioned_key_expiration_timestamp: datetime
        current_versioned_key_identifier: str
        key_name: str
        key_vault_uri: str
        key_version: str
        last_key_rotation_timestamp: datetime

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                key_name: Optional[str] = ..., 
                key_vault_uri: Optional[str] = ..., 
                key_version: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.Kind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BLOB_STORAGE = "BlobStorage"
        BLOCK_BLOB_STORAGE = "BlockBlobStorage"
        FILE_STORAGE = "FileStorage"
        STORAGE = "Storage"
        STORAGE_V2 = "StorageV2"


    class azure.mgmt.storage.models.LargeFileSharesState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.storage.models.LastAccessTimeTrackingPolicy(Model):
        blob_type: list[str]
        enable: bool
        name: Union[str, Name]
        tracking_granularity_in_days: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                blob_type: Optional[list[str]] = ..., 
                enable: bool, 
                name: Optional[Union[str, Name]] = ..., 
                tracking_granularity_in_days: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.LeaseContainerRequest(Model):
        action: Union[str, LeaseContainerRequestEnum]
        break_period: int
        lease_duration: int
        lease_id: str
        proposed_lease_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                action: Union[str, LeaseContainerRequestEnum], 
                break_period: Optional[int] = ..., 
                lease_duration: Optional[int] = ..., 
                lease_id: Optional[str] = ..., 
                proposed_lease_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.LeaseContainerRequestEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACQUIRE = "Acquire"
        BREAK = "Break"
        CHANGE = "Change"
        RELEASE = "Release"
        RENEW = "Renew"


    class azure.mgmt.storage.models.LeaseContainerResponse(Model):
        lease_id: str
        lease_time_seconds: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                lease_id: Optional[str] = ..., 
                lease_time_seconds: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.LeaseDuration(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FIXED = "Fixed"
        INFINITE = "Infinite"


    class azure.mgmt.storage.models.LeaseShareAction(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACQUIRE = "Acquire"
        BREAK = "Break"
        CHANGE = "Change"
        RELEASE = "Release"
        RENEW = "Renew"


    class azure.mgmt.storage.models.LeaseShareRequest(Model):
        action: Union[str, LeaseShareAction]
        break_period: int
        lease_duration: int
        lease_id: str
        proposed_lease_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                action: Union[str, LeaseShareAction], 
                break_period: Optional[int] = ..., 
                lease_duration: Optional[int] = ..., 
                lease_id: Optional[str] = ..., 
                proposed_lease_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.LeaseShareResponse(Model):
        lease_id: str
        lease_time_seconds: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                lease_id: Optional[str] = ..., 
                lease_time_seconds: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.LeaseState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVAILABLE = "Available"
        BREAKING = "Breaking"
        BROKEN = "Broken"
        EXPIRED = "Expired"
        LEASED = "Leased"


    class azure.mgmt.storage.models.LeaseStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LOCKED = "Locked"
        UNLOCKED = "Unlocked"


    class azure.mgmt.storage.models.LegalHold(Model):
        allow_protected_append_writes_all: bool
        has_legal_hold: bool
        tags: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                allow_protected_append_writes_all: Optional[bool] = ..., 
                tags: list[str], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.LegalHoldProperties(Model):
        has_legal_hold: bool
        protected_append_writes_history: ProtectedAppendWritesHistory
        tags: list[TagProperty]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                protected_append_writes_history: Optional[ProtectedAppendWritesHistory] = ..., 
                tags: Optional[list[TagProperty]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.ListAccountSasResponse(Model):
        account_sas_token: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.ListBlobInventoryPolicy(Model):
        value: list[BlobInventoryPolicy]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.ListContainerItem(AzureEntityResource):
        default_encryption_scope: str
        deleted: bool
        deleted_time: datetime
        deny_encryption_scope_override: bool
        enable_nfs_v3_all_squash: bool
        enable_nfs_v3_root_squash: bool
        etag: str
        has_immutability_policy: bool
        has_legal_hold: bool
        id: str
        immutability_policy: ImmutabilityPolicyProperties
        immutable_storage_with_versioning: ImmutableStorageWithVersioning
        last_modified_time: datetime
        lease_duration: Union[str, LeaseDuration]
        lease_state: Union[str, LeaseState]
        lease_status: Union[str, LeaseStatus]
        legal_hold: LegalHoldProperties
        metadata: dict[str, str]
        name: str
        public_access: Union[str, PublicAccess]
        remaining_retention_days: int
        type: str
        version: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                default_encryption_scope: Optional[str] = ..., 
                deny_encryption_scope_override: Optional[bool] = ..., 
                enable_nfs_v3_all_squash: Optional[bool] = ..., 
                enable_nfs_v3_root_squash: Optional[bool] = ..., 
                immutable_storage_with_versioning: Optional[ImmutableStorageWithVersioning] = ..., 
                metadata: Optional[dict[str, str]] = ..., 
                public_access: Optional[Union[str, PublicAccess]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.ListContainerItems(Model):
        next_link: str
        value: list[ListContainerItem]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.ListContainersInclude(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DELETED = "deleted"


    class azure.mgmt.storage.models.ListEncryptionScopesInclude(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALL = "All"
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.storage.models.ListLocalUserIncludeParam(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NFSV3 = "nfsv3"


    class azure.mgmt.storage.models.ListQueue(Resource):
        id: str
        metadata: dict[str, str]
        name: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                metadata: Optional[dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.ListQueueResource(Model):
        next_link: str
        value: list[ListQueue]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.ListQueueServices(Model):
        value: list[QueueServiceProperties]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.ListServiceSasResponse(Model):
        service_sas_token: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.ListTableResource(Model):
        next_link: str
        value: list[Table]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.ListTableServices(Model):
        value: list[TableServiceProperties]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.LocalUser(Resource):
        allow_acl_authorization: bool
        extended_groups: list[int]
        group_id: int
        has_shared_key: bool
        has_ssh_key: bool
        has_ssh_password: bool
        home_directory: str
        id: str
        is_nf_sv3_enabled: bool
        name: str
        permission_scopes: list[PermissionScope]
        sid: str
        ssh_authorized_keys: list[SshPublicKey]
        system_data: SystemData
        type: str
        user_id: int

        def __eq__(self, other: Any) -> bool: ...

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
                ssh_authorized_keys: Optional[list[SshPublicKey]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.LocalUserKeys(Model):
        shared_key: str
        ssh_authorized_keys: list[SshPublicKey]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                ssh_authorized_keys: Optional[list[SshPublicKey]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.LocalUserRegeneratePasswordResult(Model):
        ssh_password: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.LocalUsers(Model):
        next_link: str
        value: list[LocalUser]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[list[LocalUser]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.ManagementPolicy(Resource):
        id: str
        last_modified_time: datetime
        name: str
        policy: ManagementPolicySchema
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                policy: Optional[ManagementPolicySchema] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.ManagementPolicyAction(Model):
        base_blob: ManagementPolicyBaseBlob
        snapshot: ManagementPolicySnapShot
        version: ManagementPolicyVersion

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                base_blob: Optional[ManagementPolicyBaseBlob] = ..., 
                snapshot: Optional[ManagementPolicySnapShot] = ..., 
                version: Optional[ManagementPolicyVersion] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.ManagementPolicyBaseBlob(Model):
        delete: DateAfterModification
        enable_auto_tier_to_hot_from_cool: bool
        tier_to_archive: DateAfterModification
        tier_to_cold: DateAfterModification
        tier_to_cool: DateAfterModification
        tier_to_hot: DateAfterModification

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                delete: Optional[DateAfterModification] = ..., 
                enable_auto_tier_to_hot_from_cool: Optional[bool] = ..., 
                tier_to_archive: Optional[DateAfterModification] = ..., 
                tier_to_cold: Optional[DateAfterModification] = ..., 
                tier_to_cool: Optional[DateAfterModification] = ..., 
                tier_to_hot: Optional[DateAfterModification] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.ManagementPolicyDefinition(Model):
        actions: ManagementPolicyAction
        filters: ManagementPolicyFilter

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                actions: ManagementPolicyAction, 
                filters: Optional[ManagementPolicyFilter] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.ManagementPolicyFilter(Model):
        blob_index_match: list[TagFilter]
        blob_types: list[str]
        prefix_match: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                blob_index_match: Optional[list[TagFilter]] = ..., 
                blob_types: list[str], 
                prefix_match: Optional[list[str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.ManagementPolicyName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEFAULT = "default"


    class azure.mgmt.storage.models.ManagementPolicyRule(Model):
        definition: ManagementPolicyDefinition
        enabled: bool
        name: str
        type: Union[str, RuleType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                definition: ManagementPolicyDefinition, 
                enabled: Optional[bool] = ..., 
                name: str, 
                type: Union[str, RuleType], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.ManagementPolicySchema(Model):
        rules: list[ManagementPolicyRule]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                rules: list[ManagementPolicyRule], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.ManagementPolicySnapShot(Model):
        delete: DateAfterCreation
        tier_to_archive: DateAfterCreation
        tier_to_cold: DateAfterCreation
        tier_to_cool: DateAfterCreation
        tier_to_hot: DateAfterCreation

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                delete: Optional[DateAfterCreation] = ..., 
                tier_to_archive: Optional[DateAfterCreation] = ..., 
                tier_to_cold: Optional[DateAfterCreation] = ..., 
                tier_to_cool: Optional[DateAfterCreation] = ..., 
                tier_to_hot: Optional[DateAfterCreation] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.ManagementPolicyVersion(Model):
        delete: DateAfterCreation
        tier_to_archive: DateAfterCreation
        tier_to_cold: DateAfterCreation
        tier_to_cool: DateAfterCreation
        tier_to_hot: DateAfterCreation

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                delete: Optional[DateAfterCreation] = ..., 
                tier_to_archive: Optional[DateAfterCreation] = ..., 
                tier_to_cold: Optional[DateAfterCreation] = ..., 
                tier_to_cool: Optional[DateAfterCreation] = ..., 
                tier_to_hot: Optional[DateAfterCreation] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.MetricSpecification(Model):
        aggregation_type: str
        category: str
        dimensions: list[Dimension]
        display_description: str
        display_name: str
        fill_gap_with_zero: bool
        name: str
        resource_id_dimension_name_override: str
        unit: str

        def __eq__(self, other: Any) -> bool: ...

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
                unit: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


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


    class azure.mgmt.storage.models.Multichannel(Model):
        enabled: bool

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.Name(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCESS_TIME_TRACKING = "AccessTimeTracking"


    class azure.mgmt.storage.models.NetworkRuleSet(Model):
        bypass: Union[str, Bypass]
        default_action: Union[str, DefaultAction]
        ip_rules: list[IPRule]
        ipv6_rules: list[IPRule]
        resource_access_rules: list[ResourceAccessRule]
        virtual_network_rules: list[VirtualNetworkRule]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                bypass: Union[str, Bypass] = "AzureServices", 
                default_action: Union[str, DefaultAction] = "Allow", 
                ip_rules: Optional[list[IPRule]] = ..., 
                ipv6_rules: Optional[list[IPRule]] = ..., 
                resource_access_rules: Optional[list[ResourceAccessRule]] = ..., 
                virtual_network_rules: Optional[list[VirtualNetworkRule]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.NetworkSecurityPerimeter(Model):
        id: str
        location: str
        perimeter_guid: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                location: Optional[str] = ..., 
                perimeter_guid: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.NetworkSecurityPerimeterConfiguration(ProxyResourceAutoGenerated):
        id: str
        name: str
        network_security_perimeter: NetworkSecurityPerimeter
        profile: NetworkSecurityPerimeterConfigurationPropertiesProfile
        provisioning_issues: list[ProvisioningIssue]
        provisioning_state: Union[str, NetworkSecurityPerimeterConfigurationProvisioningState]
        resource_association: NetworkSecurityPerimeterConfigurationPropertiesResourceAssociation
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.NetworkSecurityPerimeterConfigurationList(Model):
        next_link: str
        value: list[NetworkSecurityPerimeterConfiguration]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.NetworkSecurityPerimeterConfigurationPropertiesProfile(Model):
        access_rules: list[NspAccessRule]
        access_rules_version: float
        diagnostic_settings_version: float
        enabled_log_categories: list[str]
        name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                access_rules: Optional[list[NspAccessRule]] = ..., 
                access_rules_version: Optional[float] = ..., 
                diagnostic_settings_version: Optional[float] = ..., 
                enabled_log_categories: Optional[list[str]] = ..., 
                name: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.NetworkSecurityPerimeterConfigurationPropertiesResourceAssociation(Model):
        access_mode: Union[str, ResourceAssociationAccessMode]
        name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                access_mode: Optional[Union[str, ResourceAssociationAccessMode]] = ..., 
                name: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.NetworkSecurityPerimeterConfigurationProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CANCELED = "Canceled"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.storage.models.NfsSetting(Model):
        encryption_in_transit: EncryptionInTransit

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                encryption_in_transit: Optional[EncryptionInTransit] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.NspAccessRule(Model):
        name: str
        properties: NspAccessRuleProperties

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.NspAccessRuleDirection(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INBOUND = "Inbound"
        OUTBOUND = "Outbound"


    class azure.mgmt.storage.models.NspAccessRuleProperties(Model):
        address_prefixes: list[str]
        direction: Union[str, NspAccessRuleDirection]
        fully_qualified_domain_names: list[str]
        network_security_perimeters: list[NetworkSecurityPerimeter]
        subscriptions: list[NspAccessRulePropertiesSubscriptionsItem]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                address_prefixes: Optional[list[str]] = ..., 
                direction: Optional[Union[str, NspAccessRuleDirection]] = ..., 
                subscriptions: Optional[list[NspAccessRulePropertiesSubscriptionsItem]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.NspAccessRulePropertiesSubscriptionsItem(Model):
        id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.ObjectReplicationPolicies(Model):
        value: list[ObjectReplicationPolicy]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[list[ObjectReplicationPolicy]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.ObjectReplicationPolicy(Resource):
        destination_account: str
        enabled_time: datetime
        id: str
        metrics: ObjectReplicationPolicyPropertiesMetrics
        name: str
        policy_id: str
        priority_replication: ObjectReplicationPolicyPropertiesPriorityReplication
        rules: list[ObjectReplicationPolicyRule]
        source_account: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                destination_account: Optional[str] = ..., 
                metrics: Optional[ObjectReplicationPolicyPropertiesMetrics] = ..., 
                priority_replication: Optional[ObjectReplicationPolicyPropertiesPriorityReplication] = ..., 
                rules: Optional[list[ObjectReplicationPolicyRule]] = ..., 
                source_account: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.ObjectReplicationPolicyFilter(Model):
        min_creation_time: str
        prefix_match: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                min_creation_time: Optional[str] = ..., 
                prefix_match: Optional[list[str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.ObjectReplicationPolicyPropertiesMetrics(Model):
        enabled: bool

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.ObjectReplicationPolicyPropertiesPriorityReplication(Model):
        enabled: bool

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.ObjectReplicationPolicyRule(Model):
        destination_container: str
        filters: ObjectReplicationPolicyFilter
        rule_id: str
        source_container: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                destination_container: str, 
                filters: Optional[ObjectReplicationPolicyFilter] = ..., 
                rule_id: Optional[str] = ..., 
                source_container: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.ObjectType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BLOB = "Blob"
        CONTAINER = "Container"


    class azure.mgmt.storage.models.Operation(Model):
        display: OperationDisplay
        name: str
        origin: str
        service_specification: ServiceSpecification

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                display: Optional[OperationDisplay] = ..., 
                name: Optional[str] = ..., 
                origin: Optional[str] = ..., 
                service_specification: Optional[ServiceSpecification] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.OperationDisplay(Model):
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
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.OperationListResult(Model):
        value: list[Operation]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[list[Operation]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.PermissionScope(Model):
        permissions: str
        resource_name: str
        service: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                permissions: str, 
                resource_name: str, 
                service: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.Permissions(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        A = "a"
        C = "c"
        D = "d"
        L = "l"
        P = "p"
        R = "r"
        U = "u"
        W = "w"


    class azure.mgmt.storage.models.Placement(Model):
        zone_placement_policy: Union[str, ZonePlacementPolicy]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                zone_placement_policy: Optional[Union[str, ZonePlacementPolicy]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.PostFailoverRedundancy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        STANDARD_LRS = "Standard_LRS"
        STANDARD_ZRS = "Standard_ZRS"


    class azure.mgmt.storage.models.PostPlannedFailoverRedundancy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        STANDARD_GRS = "Standard_GRS"
        STANDARD_GZRS = "Standard_GZRS"
        STANDARD_RAGRS = "Standard_RAGRS"
        STANDARD_RAGZRS = "Standard_RAGZRS"


    class azure.mgmt.storage.models.PrivateEndpoint(Model):
        id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.PrivateEndpointConnection(Resource):
        id: str
        name: str
        private_endpoint: PrivateEndpoint
        private_link_service_connection_state: PrivateLinkServiceConnectionState
        provisioning_state: Union[str, PrivateEndpointConnectionProvisioningState]
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
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.PrivateEndpointConnectionListResult(Model):
        value: list[PrivateEndpointConnection]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[list[PrivateEndpointConnection]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.PrivateEndpointConnectionProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.storage.models.PrivateEndpointServiceConnectionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPROVED = "Approved"
        PENDING = "Pending"
        REJECTED = "Rejected"


    class azure.mgmt.storage.models.PrivateLinkResource(Resource):
        group_id: str
        id: str
        name: str
        required_members: list[str]
        required_zone_names: list[str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                required_zone_names: Optional[list[str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.PrivateLinkResourceListResult(Model):
        value: list[PrivateLinkResource]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[list[PrivateLinkResource]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.PrivateLinkServiceConnectionState(Model):
        action_required: str
        description: str
        status: Union[str, PrivateEndpointServiceConnectionStatus]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                action_required: Optional[str] = ..., 
                description: Optional[str] = ..., 
                status: Optional[Union[str, PrivateEndpointServiceConnectionStatus]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.ProtectedAppendWritesHistory(Model):
        allow_protected_append_writes_all: bool
        timestamp: datetime

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                allow_protected_append_writes_all: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.ProtocolSettings(Model):
        nfs: NfsSetting
        smb: SmbSetting

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                nfs: Optional[NfsSetting] = ..., 
                smb: Optional[SmbSetting] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.ProvisioningIssue(Model):
        name: str
        properties: ProvisioningIssueProperties

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.ProvisioningIssueProperties(Model):
        description: str
        issue_type: Union[str, IssueType]
        severity: Union[str, Severity]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                issue_type: Optional[Union[str, IssueType]] = ..., 
                severity: Optional[Union[str, Severity]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        RESOLVING_DNS = "ResolvingDNS"
        SUCCEEDED = "Succeeded"
        VALIDATE_SUBSCRIPTION_QUOTA_BEGIN = "ValidateSubscriptionQuotaBegin"
        VALIDATE_SUBSCRIPTION_QUOTA_END = "ValidateSubscriptionQuotaEnd"


    class azure.mgmt.storage.models.ProxyResource(Resource):
        id: str
        name: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.ProxyResourceAutoGenerated(ResourceAutoGenerated):
        id: str
        name: str
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.PublicAccess(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BLOB = "Blob"
        CONTAINER = "Container"
        NONE = "None"


    class azure.mgmt.storage.models.PublicNetworkAccess(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"
        SECURED_BY_PERIMETER = "SecuredByPerimeter"


    class azure.mgmt.storage.models.QueueServiceProperties(Resource):
        cors: CorsRules
        id: str
        name: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                cors: Optional[CorsRules] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.Reason(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCOUNT_NAME_INVALID = "AccountNameInvalid"
        ALREADY_EXISTS = "AlreadyExists"


    class azure.mgmt.storage.models.ReasonCode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NOT_AVAILABLE_FOR_SUBSCRIPTION = "NotAvailableForSubscription"
        QUOTA_ID = "QuotaId"


    class azure.mgmt.storage.models.Resource(Model):
        id: str
        name: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.ResourceAccessRule(Model):
        resource_id: str
        tenant_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                resource_id: Optional[str] = ..., 
                tenant_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.ResourceAssociationAccessMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUDIT = "Audit"
        ENFORCED = "Enforced"
        LEARNING = "Learning"


    class azure.mgmt.storage.models.ResourceAutoGenerated(Model):
        id: str
        name: str
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.RestorePolicyProperties(Model):
        days: int
        enabled: bool
        last_enabled_time: datetime
        min_restore_time: datetime

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                days: Optional[int] = ..., 
                enabled: bool, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.Restriction(Model):
        reason_code: Union[str, ReasonCode]
        type: str
        values: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                reason_code: Optional[Union[str, ReasonCode]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.RootSquashType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALL_SQUASH = "AllSquash"
        NO_ROOT_SQUASH = "NoRootSquash"
        ROOT_SQUASH = "RootSquash"


    class azure.mgmt.storage.models.RoutingChoice(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNET_ROUTING = "InternetRouting"
        MICROSOFT_ROUTING = "MicrosoftRouting"


    class azure.mgmt.storage.models.RoutingPreference(Model):
        publish_internet_endpoints: bool
        publish_microsoft_endpoints: bool
        routing_choice: Union[str, RoutingChoice]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                publish_internet_endpoints: Optional[bool] = ..., 
                publish_microsoft_endpoints: Optional[bool] = ..., 
                routing_choice: Optional[Union[str, RoutingChoice]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.RuleType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LIFECYCLE = "Lifecycle"


    class azure.mgmt.storage.models.RunResult(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.storage.models.RunStatusEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FINISHED = "Finished"
        IN_PROGRESS = "InProgress"


    class azure.mgmt.storage.models.SKUCapability(Model):
        name: str
        value: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.SasPolicy(Model):
        expiration_action: Union[str, ExpirationAction]
        sas_expiration_period: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                expiration_action: Union[str, ExpirationAction] = "Log", 
                sas_expiration_period: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.Schedule(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DAILY = "Daily"
        WEEKLY = "Weekly"


    class azure.mgmt.storage.models.ServiceSasParameters(Model):
        cache_control: str
        canonicalized_resource: str
        content_disposition: str
        content_encoding: str
        content_language: str
        content_type: str
        identifier: str
        ip_address_or_range: str
        key_to_sign: str
        partition_key_end: str
        partition_key_start: str
        permissions: Union[str, Permissions]
        protocols: Union[str, HttpProtocol]
        resource: Union[str, SignedResource]
        row_key_end: str
        row_key_start: str
        shared_access_expiry_time: datetime
        shared_access_start_time: datetime

        def __eq__(self, other: Any) -> bool: ...

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
                shared_access_start_time: Optional[datetime] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.ServiceSpecification(Model):
        metric_specifications: list[MetricSpecification]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                metric_specifications: Optional[list[MetricSpecification]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


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


    class azure.mgmt.storage.models.SignedIdentifier(Model):
        access_policy: AccessPolicy
        id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                access_policy: Optional[AccessPolicy] = ..., 
                id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.SignedResource(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        B = "b"
        C = "c"
        F = "f"
        S = "s"


    class azure.mgmt.storage.models.SignedResourceTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        C = "c"
        O = "o"
        S = "s"


    class azure.mgmt.storage.models.Sku(Model):
        name: Union[str, SkuName]
        tier: Union[str, SkuTier]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                name: Union[str, SkuName], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.SkuConversionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAILED = "Failed"
        IN_PROGRESS = "InProgress"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.storage.models.SkuInformation(Model):
        capabilities: list[SKUCapability]
        kind: Union[str, Kind]
        location_info: list[SkuInformationLocationInfoItem]
        locations: list[str]
        name: Union[str, SkuName]
        resource_type: str
        restrictions: list[Restriction]
        tier: Union[str, SkuTier]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                location_info: Optional[list[SkuInformationLocationInfoItem]] = ..., 
                name: Union[str, SkuName], 
                restrictions: Optional[list[Restriction]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.SkuInformationLocationInfoItem(Model):
        location: str
        zones: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


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


    class azure.mgmt.storage.models.SmbOAuthSettings(Model):
        is_smb_o_auth_enabled: bool

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                is_smb_o_auth_enabled: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.SmbSetting(Model):
        authentication_methods: str
        channel_encryption: str
        encryption_in_transit: EncryptionInTransit
        kerberos_ticket_encryption: str
        multichannel: Multichannel
        versions: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                authentication_methods: Optional[str] = ..., 
                channel_encryption: Optional[str] = ..., 
                encryption_in_transit: Optional[EncryptionInTransit] = ..., 
                kerberos_ticket_encryption: Optional[str] = ..., 
                multichannel: Optional[Multichannel] = ..., 
                versions: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.SshPublicKey(Model):
        description: str
        key: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                key: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.State(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEPROVISIONING = "Deprovisioning"
        FAILED = "Failed"
        NETWORK_SOURCE_DELETED = "NetworkSourceDeleted"
        PROVISIONING = "Provisioning"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.storage.models.StorageAccount(TrackedResource):
        access_tier: Union[str, AccessTier]
        account_migration_in_progress: bool
        allow_blob_public_access: bool
        allow_cross_tenant_replication: bool
        allow_shared_key_access: bool
        allowed_copy_scope: Union[str, AllowedCopyScope]
        azure_files_identity_based_authentication: AzureFilesIdentityBasedAuthentication
        blob_restore_status: BlobRestoreStatus
        creation_time: datetime
        custom_domain: CustomDomain
        default_to_o_auth_authentication: bool
        dns_endpoint_type: Union[str, DnsEndpointType]
        dual_stack_endpoint_preference: DualStackEndpointPreference
        enable_extended_groups: bool
        enable_https_traffic_only: bool
        enable_nfs_v3: bool
        encryption: Encryption
        extended_location: ExtendedLocation
        failover_in_progress: bool
        geo_priority_replication_status: GeoPriorityReplicationStatus
        geo_replication_stats: GeoReplicationStats
        id: str
        identity: Identity
        immutable_storage_with_versioning: ImmutableStorageAccount
        is_hns_enabled: bool
        is_local_user_enabled: bool
        is_sftp_enabled: bool
        is_sku_conversion_blocked: bool
        key_creation_time: KeyCreationTime
        key_policy: KeyPolicy
        kind: Union[str, Kind]
        large_file_shares_state: Union[str, LargeFileSharesState]
        last_geo_failover_time: datetime
        location: str
        minimum_tls_version: Union[str, MinimumTlsVersion]
        name: str
        network_rule_set: NetworkRuleSet
        placement: Placement
        primary_endpoints: Endpoints
        primary_location: str
        private_endpoint_connections: list[PrivateEndpointConnection]
        provisioning_state: Union[str, ProvisioningState]
        public_network_access: Union[str, PublicNetworkAccess]
        routing_preference: RoutingPreference
        sas_policy: SasPolicy
        secondary_endpoints: Endpoints
        secondary_location: str
        sku: Sku
        status_of_primary: Union[str, AccountStatus]
        status_of_secondary: Union[str, AccountStatus]
        storage_account_sku_conversion_status: StorageAccountSkuConversionStatus
        tags: dict[str, str]
        type: str
        zones: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                allow_blob_public_access: Optional[bool] = ..., 
                allow_cross_tenant_replication: Optional[bool] = ..., 
                allow_shared_key_access: Optional[bool] = ..., 
                allowed_copy_scope: Optional[Union[str, AllowedCopyScope]] = ..., 
                azure_files_identity_based_authentication: Optional[AzureFilesIdentityBasedAuthentication] = ..., 
                default_to_o_auth_authentication: Optional[bool] = ..., 
                dns_endpoint_type: Optional[Union[str, DnsEndpointType]] = ..., 
                dual_stack_endpoint_preference: Optional[DualStackEndpointPreference] = ..., 
                enable_extended_groups: Optional[bool] = ..., 
                enable_https_traffic_only: Optional[bool] = ..., 
                enable_nfs_v3: Optional[bool] = ..., 
                extended_location: Optional[ExtendedLocation] = ..., 
                geo_priority_replication_status: Optional[GeoPriorityReplicationStatus] = ..., 
                identity: Optional[Identity] = ..., 
                immutable_storage_with_versioning: Optional[ImmutableStorageAccount] = ..., 
                is_hns_enabled: Optional[bool] = ..., 
                is_local_user_enabled: Optional[bool] = ..., 
                is_sftp_enabled: Optional[bool] = ..., 
                large_file_shares_state: Optional[Union[str, LargeFileSharesState]] = ..., 
                location: str, 
                minimum_tls_version: Optional[Union[str, MinimumTlsVersion]] = ..., 
                placement: Optional[Placement] = ..., 
                public_network_access: Optional[Union[str, PublicNetworkAccess]] = ..., 
                routing_preference: Optional[RoutingPreference] = ..., 
                storage_account_sku_conversion_status: Optional[StorageAccountSkuConversionStatus] = ..., 
                tags: Optional[dict[str, str]] = ..., 
                zones: Optional[list[str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.StorageAccountCheckNameAvailabilityParameters(Model):
        name: str
        type: str = "Microsoft.Storage/storageAccounts"

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
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.StorageAccountCreateParameters(Model):
        access_tier: Union[str, AccessTier]
        allow_blob_public_access: bool
        allow_cross_tenant_replication: bool
        allow_shared_key_access: bool
        allowed_copy_scope: Union[str, AllowedCopyScope]
        azure_files_identity_based_authentication: AzureFilesIdentityBasedAuthentication
        custom_domain: CustomDomain
        default_to_o_auth_authentication: bool
        dns_endpoint_type: Union[str, DnsEndpointType]
        dual_stack_endpoint_preference: DualStackEndpointPreference
        enable_extended_groups: bool
        enable_https_traffic_only: bool
        enable_nfs_v3: bool
        encryption: Encryption
        extended_location: ExtendedLocation
        geo_priority_replication_status: GeoPriorityReplicationStatus
        identity: Identity
        immutable_storage_with_versioning: ImmutableStorageAccount
        is_hns_enabled: bool
        is_local_user_enabled: bool
        is_sftp_enabled: bool
        key_policy: KeyPolicy
        kind: Union[str, Kind]
        large_file_shares_state: Union[str, LargeFileSharesState]
        location: str
        minimum_tls_version: Union[str, MinimumTlsVersion]
        network_rule_set: NetworkRuleSet
        placement: Placement
        public_network_access: Union[str, PublicNetworkAccess]
        routing_preference: RoutingPreference
        sas_policy: SasPolicy
        sku: Sku
        tags: dict[str, str]
        zones: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                access_tier: Optional[Union[str, AccessTier]] = ..., 
                allow_blob_public_access: Optional[bool] = ..., 
                allow_cross_tenant_replication: Optional[bool] = ..., 
                allow_shared_key_access: Optional[bool] = ..., 
                allowed_copy_scope: Optional[Union[str, AllowedCopyScope]] = ..., 
                azure_files_identity_based_authentication: Optional[AzureFilesIdentityBasedAuthentication] = ..., 
                custom_domain: Optional[CustomDomain] = ..., 
                default_to_o_auth_authentication: Optional[bool] = ..., 
                dns_endpoint_type: Optional[Union[str, DnsEndpointType]] = ..., 
                dual_stack_endpoint_preference: Optional[DualStackEndpointPreference] = ..., 
                enable_extended_groups: Optional[bool] = ..., 
                enable_https_traffic_only: Optional[bool] = ..., 
                enable_nfs_v3: Optional[bool] = ..., 
                encryption: Optional[Encryption] = ..., 
                extended_location: Optional[ExtendedLocation] = ..., 
                geo_priority_replication_status: Optional[GeoPriorityReplicationStatus] = ..., 
                identity: Optional[Identity] = ..., 
                immutable_storage_with_versioning: Optional[ImmutableStorageAccount] = ..., 
                is_hns_enabled: Optional[bool] = ..., 
                is_local_user_enabled: Optional[bool] = ..., 
                is_sftp_enabled: Optional[bool] = ..., 
                key_policy: Optional[KeyPolicy] = ..., 
                kind: Union[str, Kind], 
                large_file_shares_state: Optional[Union[str, LargeFileSharesState]] = ..., 
                location: str, 
                minimum_tls_version: Optional[Union[str, MinimumTlsVersion]] = ..., 
                network_rule_set: Optional[NetworkRuleSet] = ..., 
                placement: Optional[Placement] = ..., 
                public_network_access: Optional[Union[str, PublicNetworkAccess]] = ..., 
                routing_preference: Optional[RoutingPreference] = ..., 
                sas_policy: Optional[SasPolicy] = ..., 
                sku: Sku, 
                tags: Optional[dict[str, str]] = ..., 
                zones: Optional[list[str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.StorageAccountExpand(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BLOB_RESTORE_STATUS = "blobRestoreStatus"
        GEO_REPLICATION_STATS = "geoReplicationStats"


    class azure.mgmt.storage.models.StorageAccountInternetEndpoints(Model):
        blob: str
        dfs: str
        file: str
        web: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.StorageAccountIpv6Endpoints(Model):
        blob: str
        dfs: str
        file: str
        internet_endpoints: StorageAccountInternetEndpoints
        microsoft_endpoints: StorageAccountMicrosoftEndpoints
        queue: str
        table: str
        web: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                internet_endpoints: Optional[StorageAccountInternetEndpoints] = ..., 
                microsoft_endpoints: Optional[StorageAccountMicrosoftEndpoints] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.StorageAccountKey(Model):
        creation_time: datetime
        key_name: str
        permissions: Union[str, KeyPermission]
        value: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.StorageAccountListKeysResult(Model):
        keys: list[StorageAccountKey]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.StorageAccountListResult(Model):
        next_link: str
        value: list[StorageAccount]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.StorageAccountMicrosoftEndpoints(Model):
        blob: str
        dfs: str
        file: str
        queue: str
        table: str
        web: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.StorageAccountMigration(Model):
        id: str
        migration_failed_detailed_reason: str
        migration_failed_reason: str
        migration_status: Union[str, MigrationStatus]
        name: str
        target_sku_name: Union[str, SkuName]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                target_sku_name: Union[str, SkuName], 
                type: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.StorageAccountRegenerateKeyParameters(Model):
        key_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                key_name: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.StorageAccountSkuConversionStatus(Model):
        end_time: str
        sku_conversion_status: Union[str, SkuConversionStatus]
        start_time: str
        target_sku_name: Union[str, SkuName]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                target_sku_name: Optional[Union[str, SkuName]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.StorageAccountUpdateParameters(Model):
        access_tier: Union[str, AccessTier]
        allow_blob_public_access: bool
        allow_cross_tenant_replication: bool
        allow_shared_key_access: bool
        allowed_copy_scope: Union[str, AllowedCopyScope]
        azure_files_identity_based_authentication: AzureFilesIdentityBasedAuthentication
        custom_domain: CustomDomain
        default_to_o_auth_authentication: bool
        dns_endpoint_type: Union[str, DnsEndpointType]
        dual_stack_endpoint_preference: DualStackEndpointPreference
        enable_extended_groups: bool
        enable_https_traffic_only: bool
        encryption: Encryption
        geo_priority_replication_status: GeoPriorityReplicationStatus
        identity: Identity
        immutable_storage_with_versioning: ImmutableStorageAccount
        is_local_user_enabled: bool
        is_sftp_enabled: bool
        key_policy: KeyPolicy
        kind: Union[str, Kind]
        large_file_shares_state: Union[str, LargeFileSharesState]
        minimum_tls_version: Union[str, MinimumTlsVersion]
        network_rule_set: NetworkRuleSet
        placement: Placement
        public_network_access: Union[str, PublicNetworkAccess]
        routing_preference: RoutingPreference
        sas_policy: SasPolicy
        sku: Sku
        tags: dict[str, str]
        zones: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                access_tier: Optional[Union[str, AccessTier]] = ..., 
                allow_blob_public_access: Optional[bool] = ..., 
                allow_cross_tenant_replication: Optional[bool] = ..., 
                allow_shared_key_access: Optional[bool] = ..., 
                allowed_copy_scope: Optional[Union[str, AllowedCopyScope]] = ..., 
                azure_files_identity_based_authentication: Optional[AzureFilesIdentityBasedAuthentication] = ..., 
                custom_domain: Optional[CustomDomain] = ..., 
                default_to_o_auth_authentication: Optional[bool] = ..., 
                dns_endpoint_type: Optional[Union[str, DnsEndpointType]] = ..., 
                dual_stack_endpoint_preference: Optional[DualStackEndpointPreference] = ..., 
                enable_extended_groups: Optional[bool] = ..., 
                enable_https_traffic_only: Optional[bool] = ..., 
                encryption: Optional[Encryption] = ..., 
                geo_priority_replication_status: Optional[GeoPriorityReplicationStatus] = ..., 
                identity: Optional[Identity] = ..., 
                immutable_storage_with_versioning: Optional[ImmutableStorageAccount] = ..., 
                is_local_user_enabled: Optional[bool] = ..., 
                is_sftp_enabled: Optional[bool] = ..., 
                key_policy: Optional[KeyPolicy] = ..., 
                kind: Optional[Union[str, Kind]] = ..., 
                large_file_shares_state: Optional[Union[str, LargeFileSharesState]] = ..., 
                minimum_tls_version: Optional[Union[str, MinimumTlsVersion]] = ..., 
                network_rule_set: Optional[NetworkRuleSet] = ..., 
                placement: Optional[Placement] = ..., 
                public_network_access: Optional[Union[str, PublicNetworkAccess]] = ..., 
                routing_preference: Optional[RoutingPreference] = ..., 
                sas_policy: Optional[SasPolicy] = ..., 
                sku: Optional[Sku] = ..., 
                tags: Optional[dict[str, str]] = ..., 
                zones: Optional[list[str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.StorageQueue(Resource):
        approximate_message_count: int
        id: str
        metadata: dict[str, str]
        name: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                metadata: Optional[dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.StorageSkuListResult(Model):
        value: list[SkuInformation]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.StorageTaskAssignment(Resource):
        id: str
        name: str
        properties: StorageTaskAssignmentProperties
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: StorageTaskAssignmentProperties, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.StorageTaskAssignmentExecutionContext(Model):
        target: ExecutionTarget
        trigger: ExecutionTrigger

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                target: Optional[ExecutionTarget] = ..., 
                trigger: ExecutionTrigger, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.StorageTaskAssignmentProperties(Model):
        description: str
        enabled: bool
        execution_context: StorageTaskAssignmentExecutionContext
        provisioning_state: Union[str, ProvisioningState]
        report: StorageTaskAssignmentReport
        run_status: StorageTaskReportProperties
        task_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                description: str, 
                enabled: bool, 
                execution_context: StorageTaskAssignmentExecutionContext, 
                report: StorageTaskAssignmentReport, 
                run_status: Optional[StorageTaskReportProperties] = ..., 
                task_id: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.StorageTaskAssignmentReport(Model):
        prefix: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                prefix: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.StorageTaskAssignmentUpdateExecutionContext(Model):
        target: ExecutionTarget
        trigger: ExecutionTriggerUpdate

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                target: Optional[ExecutionTarget] = ..., 
                trigger: Optional[ExecutionTriggerUpdate] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.StorageTaskAssignmentUpdateParameters(Model):
        properties: StorageTaskAssignmentUpdateProperties

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[StorageTaskAssignmentUpdateProperties] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.StorageTaskAssignmentUpdateProperties(Model):
        description: str
        enabled: bool
        execution_context: StorageTaskAssignmentUpdateExecutionContext
        provisioning_state: Union[str, ProvisioningState]
        report: StorageTaskAssignmentUpdateReport
        run_status: StorageTaskReportProperties
        task_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                enabled: Optional[bool] = ..., 
                execution_context: Optional[StorageTaskAssignmentUpdateExecutionContext] = ..., 
                report: Optional[StorageTaskAssignmentUpdateReport] = ..., 
                run_status: Optional[StorageTaskReportProperties] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.StorageTaskAssignmentUpdateReport(Model):
        prefix: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                prefix: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.StorageTaskAssignmentsList(Model):
        next_link: str
        value: list[StorageTaskAssignment]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.StorageTaskReportInstance(ProxyResource):
        id: str
        name: str
        properties: StorageTaskReportProperties
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[StorageTaskReportProperties] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.StorageTaskReportProperties(Model):
        finish_time: str
        object_failed_count: str
        objects_operated_on_count: str
        objects_succeeded_count: str
        objects_targeted_count: str
        run_result: Union[str, RunResult]
        run_status_enum: Union[str, RunStatusEnum]
        run_status_error: str
        start_time: str
        storage_account_id: str
        summary_report_path: str
        task_assignment_id: str
        task_id: str
        task_version: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.StorageTaskReportSummary(Model):
        next_link: str
        value: list[StorageTaskReportInstance]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.SystemData(Model):
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
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.Table(Resource):
        id: str
        name: str
        signed_identifiers: list[TableSignedIdentifier]
        table_name: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                signed_identifiers: Optional[list[TableSignedIdentifier]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.TableAccessPolicy(Model):
        expiry_time: datetime
        permission: str
        start_time: datetime

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                expiry_time: Optional[datetime] = ..., 
                permission: str, 
                start_time: Optional[datetime] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.TableServiceProperties(Resource):
        cors: CorsRules
        id: str
        name: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                cors: Optional[CorsRules] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.TableSignedIdentifier(Model):
        access_policy: TableAccessPolicy
        id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                access_policy: Optional[TableAccessPolicy] = ..., 
                id: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.TagFilter(Model):
        name: str
        op: str
        value: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                name: str, 
                op: str, 
                value: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.TagProperty(Model):
        object_identifier: str
        tag: str
        tenant_id: str
        timestamp: datetime
        upn: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.TrackedResource(Resource):
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
                tags: Optional[dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.TriggerParameters(Model):
        end_by: datetime
        interval: int
        interval_unit: Union[str, IntervalUnit]
        start_from: datetime
        start_on: datetime

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                end_by: Optional[datetime] = ..., 
                interval: Optional[int] = ..., 
                interval_unit: Optional[Union[str, IntervalUnit]] = ..., 
                start_from: Optional[datetime] = ..., 
                start_on: Optional[datetime] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.TriggerParametersUpdate(Model):
        end_by: datetime
        interval: int
        interval_unit: Union[str, IntervalUnit]
        start_from: datetime
        start_on: datetime

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                end_by: Optional[datetime] = ..., 
                interval: Optional[int] = ..., 
                interval_unit: Optional[Union[str, IntervalUnit]] = ..., 
                start_from: Optional[datetime] = ..., 
                start_on: Optional[datetime] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.TriggerType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ON_SCHEDULE = "OnSchedule"
        RUN_ONCE = "RunOnce"


    class azure.mgmt.storage.models.UpdateHistoryProperty(Model):
        allow_protected_append_writes: bool
        allow_protected_append_writes_all: bool
        immutability_period_since_creation_in_days: int
        object_identifier: str
        tenant_id: str
        timestamp: datetime
        update: Union[str, ImmutabilityPolicyUpdateType]
        upn: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                allow_protected_append_writes: Optional[bool] = ..., 
                allow_protected_append_writes_all: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.Usage(Model):
        current_value: int
        limit: int
        name: UsageName
        unit: Union[str, UsageUnit]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.UsageListResult(Model):
        value: list[Usage]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[list[Usage]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.UsageName(Model):
        localized_value: str
        value: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.UsageUnit(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BYTES = "Bytes"
        BYTES_PER_SECOND = "BytesPerSecond"
        COUNT = "Count"
        COUNTS_PER_SECOND = "CountsPerSecond"
        PERCENT = "Percent"
        SECONDS = "Seconds"


    class azure.mgmt.storage.models.UserAssignedIdentity(Model):
        client_id: str
        principal_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.VirtualNetworkRule(Model):
        action: str
        state: Union[str, State]
        virtual_network_resource_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                action: Optional[Literal[Allow]] = ..., 
                state: Optional[Union[str, State]] = ..., 
                virtual_network_resource_id: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.storage.models.ZonePlacementPolicy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ANY = "Any"
        NONE = "None"


namespace azure.mgmt.storage.operations

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
                if_match: Optional[str] = None, 
                parameters: Optional[ImmutabilityPolicy] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ImmutabilityPolicy: ...

        @overload
        def create_or_update_immutability_policy(
                self, 
                resource_group_name: str, 
                account_name: str, 
                container_name: str, 
                if_match: Optional[str] = None, 
                parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
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
                if_match: str, 
                **kwargs: Any
            ) -> ImmutabilityPolicy: ...

        @overload
        def extend_immutability_policy(
                self, 
                resource_group_name: str, 
                account_name: str, 
                container_name: str, 
                if_match: str, 
                parameters: Optional[ImmutabilityPolicy] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ImmutabilityPolicy: ...

        @overload
        def extend_immutability_policy(
                self, 
                resource_group_name: str, 
                account_name: str, 
                container_name: str, 
                if_match: str, 
                parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
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
                if_match: Optional[str] = None, 
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
                maxpagesize: Optional[str] = None, 
                filter: Optional[str] = None, 
                include: Optional[Union[str, ListContainersInclude]] = None, 
                **kwargs: Any
            ) -> ItemPaged[ListContainerItem]: ...

        @distributed_trace
        def lock_immutability_policy(
                self, 
                resource_group_name: str, 
                account_name: str, 
                container_name: str, 
                if_match: str, 
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
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BlobServiceProperties: ...


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
                maxpagesize: Optional[int] = None, 
                filter: Optional[str] = None, 
                include: Optional[Union[str, ListEncryptionScopesInclude]] = None, 
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
                maxpagesize: Optional[int] = None, 
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
                expand: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FileShare: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_name: str, 
                file_share: IO[bytes], 
                expand: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FileShare: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_name: str, 
                x_ms_snapshot: Optional[str] = None, 
                include: Optional[str] = None, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_name: str, 
                expand: Optional[str] = None, 
                x_ms_snapshot: Optional[str] = None, 
                **kwargs: Any
            ) -> FileShare: ...

        @overload
        def lease(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_name: str, 
                x_ms_snapshot: Optional[str] = None, 
                parameters: Optional[LeaseShareRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LeaseShareResponse: ...

        @overload
        def lease(
                self, 
                resource_group_name: str, 
                account_name: str, 
                share_name: str, 
                x_ms_snapshot: Optional[str] = None, 
                parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LeaseShareResponse: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                account_name: str, 
                maxpagesize: Optional[str] = None, 
                filter: Optional[str] = None, 
                expand: Optional[str] = None, 
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
                maxpagesize: Optional[int] = None, 
                filter: Optional[str] = None, 
                include: Optional[Union[str, ListLocalUserIncludeParam]] = None, 
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
                maxpagesize: Optional[str] = None, 
                filter: Optional[str] = None, 
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
                failover_type: Literal["Planned"] = "Planned", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_hierarchical_namespace_migration(
                self, 
                resource_group_name: str, 
                account_name: str, 
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
                expand: Optional[Union[str, StorageAccountExpand]] = None, 
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
                maxpagesize: Optional[int] = None, 
                filter: Optional[str] = None, 
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
                maxpagesize: Optional[int] = None, 
                filter: Optional[str] = None, 
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
                top: Optional[int] = None, 
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


```