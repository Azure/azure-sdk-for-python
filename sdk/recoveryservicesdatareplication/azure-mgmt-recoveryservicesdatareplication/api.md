```py
namespace azure.mgmt.recoveryservicesdatareplication

    class azure.mgmt.recoveryservicesdatareplication.RecoveryServicesDataReplicationMgmtClient: implements ContextManager 
        check_name_availability: CheckNameAvailabilityOperations
        deployment_preflight: DeploymentPreflightOperations
        email_configuration: EmailConfigurationOperations
        event: EventOperations
        fabric: FabricOperations
        fabric_agent: FabricAgentOperations
        job: JobOperations
        location_based_operation_results: LocationBasedOperationResultsOperations
        operation_results: OperationResultsOperations
        operations: Operations
        policy: PolicyOperations
        private_endpoint_connections: PrivateEndpointConnectionsOperations
        private_link_resources: PrivateLinkResourcesOperations
        protected_item: ProtectedItemOperations
        recovery_point: RecoveryPointOperations
        replication_extension: ReplicationExtensionOperations
        vault: VaultOperations

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


namespace azure.mgmt.recoveryservicesdatareplication.aio

    class azure.mgmt.recoveryservicesdatareplication.aio.RecoveryServicesDataReplicationMgmtClient: implements AsyncContextManager 
        check_name_availability: CheckNameAvailabilityOperations
        deployment_preflight: DeploymentPreflightOperations
        email_configuration: EmailConfigurationOperations
        event: EventOperations
        fabric: FabricOperations
        fabric_agent: FabricAgentOperations
        job: JobOperations
        location_based_operation_results: LocationBasedOperationResultsOperations
        operation_results: OperationResultsOperations
        operations: Operations
        policy: PolicyOperations
        private_endpoint_connections: PrivateEndpointConnectionsOperations
        private_link_resources: PrivateLinkResourcesOperations
        protected_item: ProtectedItemOperations
        recovery_point: RecoveryPointOperations
        replication_extension: ReplicationExtensionOperations
        vault: VaultOperations

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


namespace azure.mgmt.recoveryservicesdatareplication.aio.operations

    class azure.mgmt.recoveryservicesdatareplication.aio.operations.CheckNameAvailabilityOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def post(
                self, 
                location: str, 
                body: Optional[CheckNameAvailabilityModel] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResponseModel: ...

        @overload
        async def post(
                self, 
                location: str, 
                body: Optional[CheckNameAvailabilityModel] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResponseModel: ...

        @overload
        async def post(
                self, 
                location: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResponseModel: ...


    class azure.mgmt.recoveryservicesdatareplication.aio.operations.DeploymentPreflightOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def post(
                self, 
                resource_group_name: str, 
                deployment_id: str, 
                body: Optional[DeploymentPreflightModel] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DeploymentPreflightModel: ...

        @overload
        async def post(
                self, 
                resource_group_name: str, 
                deployment_id: str, 
                body: Optional[DeploymentPreflightModel] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DeploymentPreflightModel: ...

        @overload
        async def post(
                self, 
                resource_group_name: str, 
                deployment_id: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DeploymentPreflightModel: ...


    class azure.mgmt.recoveryservicesdatareplication.aio.operations.EmailConfigurationOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                email_configuration_name: str, 
                body: EmailConfigurationModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EmailConfigurationModel: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                email_configuration_name: str, 
                body: EmailConfigurationModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EmailConfigurationModel: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                email_configuration_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EmailConfigurationModel: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                email_configuration_name: str, 
                **kwargs: Any
            ) -> EmailConfigurationModel: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[EmailConfigurationModel]: ...


    class azure.mgmt.recoveryservicesdatareplication.aio.operations.EventOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                event_name: str, 
                **kwargs: Any
            ) -> EventModel: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                *, 
                continuation_token_parameter: Optional[str] = ..., 
                odata_options: Optional[str] = ..., 
                page_size: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[EventModel]: ...


    class azure.mgmt.recoveryservicesdatareplication.aio.operations.FabricAgentOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                fabric_name: str, 
                fabric_agent_name: str, 
                body: FabricAgentModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[FabricAgentModel]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                fabric_name: str, 
                fabric_agent_name: str, 
                body: FabricAgentModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[FabricAgentModel]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                fabric_name: str, 
                fabric_agent_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[FabricAgentModel]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                fabric_name: str, 
                fabric_agent_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                fabric_name: str, 
                fabric_agent_name: str, 
                **kwargs: Any
            ) -> FabricAgentModel: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                fabric_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[FabricAgentModel]: ...


    class azure.mgmt.recoveryservicesdatareplication.aio.operations.FabricOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                fabric_name: str, 
                body: FabricModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[FabricModel]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                fabric_name: str, 
                body: FabricModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[FabricModel]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                fabric_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[FabricModel]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                fabric_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                fabric_name: str, 
                body: FabricModelUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[FabricModel]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                fabric_name: str, 
                body: FabricModelUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[FabricModel]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                fabric_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[FabricModel]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                fabric_name: str, 
                **kwargs: Any
            ) -> FabricModel: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                *, 
                continuation_token_parameter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[FabricModel]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[FabricModel]: ...


    class azure.mgmt.recoveryservicesdatareplication.aio.operations.JobOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                job_name: str, 
                **kwargs: Any
            ) -> JobModel: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                *, 
                continuation_token_parameter: Optional[str] = ..., 
                odata_options: Optional[str] = ..., 
                page_size: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[JobModel]: ...


    class azure.mgmt.recoveryservicesdatareplication.aio.operations.LocationBasedOperationResultsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                location: str, 
                operation_id: str, 
                **kwargs: Any
            ) -> OperationStatus: ...


    class azure.mgmt.recoveryservicesdatareplication.aio.operations.OperationResultsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                operation_id: str, 
                **kwargs: Any
            ) -> OperationStatus: ...


    class azure.mgmt.recoveryservicesdatareplication.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


    class azure.mgmt.recoveryservicesdatareplication.aio.operations.PolicyOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                policy_name: str, 
                body: PolicyModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PolicyModel]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                policy_name: str, 
                body: PolicyModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PolicyModel]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                policy_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PolicyModel]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                policy_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                policy_name: str, 
                **kwargs: Any
            ) -> PolicyModel: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[PolicyModel]: ...


    class azure.mgmt.recoveryservicesdatareplication.aio.operations.PrivateEndpointConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[PrivateEndpointConnection]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                private_endpoint_connection_name: str, 
                body: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                private_endpoint_connection_name: str, 
                body: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                private_endpoint_connection_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...


    class azure.mgmt.recoveryservicesdatareplication.aio.operations.PrivateLinkResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                private_link_resource_name: str, 
                **kwargs: Any
            ) -> PrivateLinkResource: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[PrivateLinkResource]: ...


    class azure.mgmt.recoveryservicesdatareplication.aio.operations.ProtectedItemOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                protected_item_name: str, 
                body: ProtectedItemModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ProtectedItemModel]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                protected_item_name: str, 
                body: ProtectedItemModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ProtectedItemModel]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                protected_item_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ProtectedItemModel]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                protected_item_name: str, 
                *, 
                force_delete: Optional[bool] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_planned_failover(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                protected_item_name: str, 
                body: PlannedFailoverModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PlannedFailoverModel]: ...

        @overload
        async def begin_planned_failover(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                protected_item_name: str, 
                body: PlannedFailoverModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PlannedFailoverModel]: ...

        @overload
        async def begin_planned_failover(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                protected_item_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PlannedFailoverModel]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                protected_item_name: str, 
                body: ProtectedItemModelUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ProtectedItemModel]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                protected_item_name: str, 
                body: ProtectedItemModelUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ProtectedItemModel]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                protected_item_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ProtectedItemModel]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                protected_item_name: str, 
                **kwargs: Any
            ) -> ProtectedItemModel: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                *, 
                continuation_token_parameter: Optional[str] = ..., 
                odata_options: Optional[str] = ..., 
                page_size: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[ProtectedItemModel]: ...


    class azure.mgmt.recoveryservicesdatareplication.aio.operations.RecoveryPointOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                protected_item_name: str, 
                recovery_point_name: str, 
                **kwargs: Any
            ) -> RecoveryPointModel: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                protected_item_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[RecoveryPointModel]: ...


    class azure.mgmt.recoveryservicesdatareplication.aio.operations.ReplicationExtensionOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                replication_extension_name: str, 
                body: ReplicationExtensionModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ReplicationExtensionModel]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                replication_extension_name: str, 
                body: ReplicationExtensionModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ReplicationExtensionModel]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                replication_extension_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ReplicationExtensionModel]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                replication_extension_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                replication_extension_name: str, 
                **kwargs: Any
            ) -> ReplicationExtensionModel: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ReplicationExtensionModel]: ...


    class azure.mgmt.recoveryservicesdatareplication.aio.operations.VaultOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                body: VaultModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VaultModel]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                body: VaultModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VaultModel]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VaultModel]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                body: VaultModelUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VaultModel]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                body: VaultModelUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VaultModel]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VaultModel]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                **kwargs: Any
            ) -> VaultModel: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                *, 
                continuation_token_parameter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[VaultModel]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[VaultModel]: ...


namespace azure.mgmt.recoveryservicesdatareplication.models

    class azure.mgmt.recoveryservicesdatareplication.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.recoveryservicesdatareplication.models.AffectedObjectDetails(_Model):
        description: Optional[str]
        type: Optional[Literal["object"]]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                type: Optional[Literal[object]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesdatareplication.models.AzStackHCIClusterProperties(_Model):
        cluster_name: str
        resource_name: str
        storage_account_name: str
        storage_containers: list[StorageContainerProperties]

        @overload
        def __init__(
                self, 
                *, 
                cluster_name: str, 
                resource_name: str, 
                storage_account_name: str, 
                storage_containers: list[StorageContainerProperties]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesdatareplication.models.AzStackHCIFabricModelCustomProperties(FabricModelCustomProperties, discriminator='AzStackHCI'):
        appliance_name: Optional[list[str]]
        az_stack_hci_site_id: str
        cluster: AzStackHCIClusterProperties
        fabric_container_id: Optional[str]
        fabric_resource_id: Optional[str]
        instance_type: Literal["AzStackHCI"]
        migration_hub_uri: Optional[str]
        migration_solution_id: str

        @overload
        def __init__(
                self, 
                *, 
                az_stack_hci_site_id: str, 
                cluster: AzStackHCIClusterProperties, 
                migration_solution_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesdatareplication.models.CheckNameAvailabilityModel(_Model):
        name: Optional[str]
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesdatareplication.models.CheckNameAvailabilityResponseModel(_Model):
        message: Optional[str]
        name_available: Optional[bool]
        reason: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                message: Optional[str] = ..., 
                name_available: Optional[bool] = ..., 
                reason: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesdatareplication.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.recoveryservicesdatareplication.models.DeploymentPreflightModel(_Model):
        resources: Optional[list[DeploymentPreflightResource]]

        @overload
        def __init__(
                self, 
                *, 
                resources: Optional[list[DeploymentPreflightResource]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesdatareplication.models.DeploymentPreflightResource(_Model):
        api_version: Optional[str]
        location: Optional[str]
        name: Optional[str]
        properties: Optional[Any]
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                api_version: Optional[str] = ..., 
                location: Optional[str] = ..., 
                name: Optional[str] = ..., 
                properties: Optional[Any] = ..., 
                type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesdatareplication.models.DiskControllerInputs(_Model):
        controller_id: int
        controller_location: int
        controller_name: str

        @overload
        def __init__(
                self, 
                *, 
                controller_id: int, 
                controller_location: int, 
                controller_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesdatareplication.models.EmailConfigurationModel(ProxyResource):
        id: str
        name: str
        properties: Optional[EmailConfigurationModelProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[EmailConfigurationModelProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesdatareplication.models.EmailConfigurationModelProperties(_Model):
        custom_email_addresses: Optional[list[str]]
        locale: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        send_to_owners: bool

        @overload
        def __init__(
                self, 
                *, 
                custom_email_addresses: Optional[list[str]] = ..., 
                locale: Optional[str] = ..., 
                send_to_owners: bool
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesdatareplication.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.recoveryservicesdatareplication.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.recoveryservicesdatareplication.models.ErrorModel(_Model):
        causes: Optional[str]
        code: Optional[str]
        creation_time: Optional[datetime]
        message: Optional[str]
        recommendation: Optional[str]
        severity: Optional[str]
        type: Optional[str]


    class azure.mgmt.recoveryservicesdatareplication.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesdatareplication.models.EventModel(ProxyResource):
        id: str
        name: str
        properties: Optional[EventModelProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[EventModelProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesdatareplication.models.EventModelCustomProperties(_Model):
        instance_type: str

        @overload
        def __init__(
                self, 
                *, 
                instance_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesdatareplication.models.EventModelProperties(_Model):
        correlation_id: Optional[str]
        custom_properties: EventModelCustomProperties
        description: Optional[str]
        event_name: Optional[str]
        event_type: Optional[str]
        health_errors: Optional[list[HealthErrorModel]]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        resource_name: Optional[str]
        resource_type: Optional[str]
        severity: Optional[str]
        time_of_occurrence: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                custom_properties: EventModelCustomProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesdatareplication.models.FabricAgentModel(ProxyResource):
        id: str
        name: str
        properties: Optional[FabricAgentModelProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[FabricAgentModelProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesdatareplication.models.FabricAgentModelCustomProperties(_Model):
        instance_type: str

        @overload
        def __init__(
                self, 
                *, 
                instance_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesdatareplication.models.FabricAgentModelProperties(_Model):
        authentication_identity: IdentityModel
        correlation_id: Optional[str]
        custom_properties: FabricAgentModelCustomProperties
        health_errors: Optional[list[HealthErrorModel]]
        is_responsive: Optional[bool]
        last_heartbeat: Optional[datetime]
        machine_id: str
        machine_name: str
        provisioning_state: Optional[Union[str, ProvisioningState]]
        resource_access_identity: IdentityModel
        version_number: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                authentication_identity: IdentityModel, 
                custom_properties: FabricAgentModelCustomProperties, 
                machine_id: str, 
                machine_name: str, 
                resource_access_identity: IdentityModel
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesdatareplication.models.FabricModel(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[FabricModelProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[FabricModelProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesdatareplication.models.FabricModelCustomProperties(_Model):
        instance_type: str

        @overload
        def __init__(
                self, 
                *, 
                instance_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesdatareplication.models.FabricModelProperties(_Model):
        custom_properties: FabricModelCustomProperties
        health: Optional[Union[str, HealthStatus]]
        health_errors: Optional[list[HealthErrorModel]]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        service_endpoint: Optional[str]
        service_resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                custom_properties: FabricModelCustomProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesdatareplication.models.FabricModelUpdate(_Model):
        id: Optional[str]
        name: Optional[str]
        properties: Optional[FabricModelProperties]
        system_data: Optional[SystemData]
        tags: Optional[dict[str, str]]
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[FabricModelProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesdatareplication.models.FailoverJobModelCustomProperties(JobModelCustomProperties, discriminator='FailoverJobDetails'):
        affected_object_details: AffectedObjectDetails
        instance_type: Literal["FailoverJobDetails"]
        protected_item_details: Optional[list[FailoverProtectedItemProperties]]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesdatareplication.models.FailoverProtectedItemProperties(_Model):
        network_name: Optional[str]
        protected_item_name: Optional[str]
        recovery_point_id: Optional[str]
        recovery_point_time: Optional[datetime]
        subnet: Optional[str]
        test_vm_name: Optional[str]
        vm_name: Optional[str]


    class azure.mgmt.recoveryservicesdatareplication.models.HealthErrorModel(_Model):
        affected_resource_correlation_ids: Optional[list[str]]
        affected_resource_type: Optional[str]
        category: Optional[str]
        causes: Optional[str]
        child_errors: Optional[list[InnerHealthErrorModel]]
        code: Optional[str]
        creation_time: Optional[datetime]
        health_category: Optional[str]
        is_customer_resolvable: Optional[bool]
        message: Optional[str]
        recommendation: Optional[str]
        severity: Optional[str]
        source: Optional[str]
        summary: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                affected_resource_correlation_ids: Optional[list[str]] = ..., 
                affected_resource_type: Optional[str] = ..., 
                child_errors: Optional[list[InnerHealthErrorModel]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesdatareplication.models.HealthStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CRITICAL = "Critical"
        NORMAL = "Normal"
        WARNING = "Warning"


    class azure.mgmt.recoveryservicesdatareplication.models.HyperVMigrateFabricModelCustomProperties(FabricModelCustomProperties, discriminator='HyperVMigrate'):
        fabric_container_id: Optional[str]
        fabric_resource_id: Optional[str]
        hyper_v_site_id: str
        instance_type: Literal["HyperVMigrate"]
        migration_hub_uri: Optional[str]
        migration_solution_id: str

        @overload
        def __init__(
                self, 
                *, 
                hyper_v_site_id: str, 
                migration_solution_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesdatareplication.models.HyperVToAzStackHCIDiskInput(_Model):
        disk_block_size: Optional[int]
        disk_controller: Optional[DiskControllerInputs]
        disk_file_format: str
        disk_id: str
        disk_identifier: Optional[str]
        disk_logical_sector_size: Optional[int]
        disk_physical_sector_size: Optional[int]
        disk_size_gb: int
        is_dynamic: Optional[bool]
        is_os_disk: bool
        storage_container_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                disk_block_size: Optional[int] = ..., 
                disk_controller: Optional[DiskControllerInputs] = ..., 
                disk_file_format: str, 
                disk_id: str, 
                disk_identifier: Optional[str] = ..., 
                disk_logical_sector_size: Optional[int] = ..., 
                disk_physical_sector_size: Optional[int] = ..., 
                disk_size_gb: int, 
                is_dynamic: Optional[bool] = ..., 
                is_os_disk: bool, 
                storage_container_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesdatareplication.models.HyperVToAzStackHCIEventModelCustomProperties(EventModelCustomProperties, discriminator='HyperVToAzStackHCI'):
        event_source_friendly_name: Optional[str]
        instance_type: Literal["HyperVToAzStackHCI"]
        protected_item_friendly_name: Optional[str]
        server_type: Optional[str]
        source_appliance_name: Optional[str]
        target_appliance_name: Optional[str]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesdatareplication.models.HyperVToAzStackHCINicInput(_Model):
        is_mac_migration_enabled: Optional[bool]
        is_static_ip_migration_enabled: Optional[bool]
        network_name: Optional[str]
        nic_id: str
        selection_type_for_failover: Union[str, VMNicSelection]
        target_network_id: Optional[str]
        test_network_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                is_mac_migration_enabled: Optional[bool] = ..., 
                is_static_ip_migration_enabled: Optional[bool] = ..., 
                nic_id: str, 
                selection_type_for_failover: Union[str, VMNicSelection], 
                target_network_id: Optional[str] = ..., 
                test_network_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesdatareplication.models.HyperVToAzStackHCIPlannedFailoverModelCustomProperties(PlannedFailoverModelCustomProperties, discriminator='HyperVToAzStackHCI'):
        instance_type: Literal["HyperVToAzStackHCI"]
        shutdown_source_vm: bool

        @overload
        def __init__(
                self, 
                *, 
                shutdown_source_vm: bool
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesdatareplication.models.HyperVToAzStackHCIPolicyModelCustomProperties(PolicyModelCustomProperties, discriminator='HyperVToAzStackHCI'):
        app_consistent_frequency_in_minutes: int
        crash_consistent_frequency_in_minutes: int
        instance_type: Literal["HyperVToAzStackHCI"]
        recovery_point_history_in_minutes: int

        @overload
        def __init__(
                self, 
                *, 
                app_consistent_frequency_in_minutes: int, 
                crash_consistent_frequency_in_minutes: int, 
                recovery_point_history_in_minutes: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesdatareplication.models.HyperVToAzStackHCIProtectedDiskProperties(_Model):
        capacity_in_bytes: Optional[int]
        disk_block_size: Optional[int]
        disk_logical_sector_size: Optional[int]
        disk_physical_sector_size: Optional[int]
        disk_type: Optional[str]
        is_dynamic: Optional[bool]
        is_os_disk: Optional[bool]
        migrate_disk_name: Optional[str]
        seed_disk_name: Optional[str]
        source_disk_id: Optional[str]
        source_disk_name: Optional[str]
        storage_container_id: Optional[str]
        storage_container_local_path: Optional[str]
        test_migrate_disk_name: Optional[str]


    class azure.mgmt.recoveryservicesdatareplication.models.HyperVToAzStackHCIProtectedItemModelCustomProperties(ProtectedItemModelCustomProperties, discriminator='HyperVToAzStackHCI'):
        active_location: Optional[Union[str, ProtectedItemActiveLocation]]
        custom_location_region: str
        disks_to_include: list[HyperVToAzStackHCIDiskInput]
        dynamic_memory_config: Optional[ProtectedItemDynamicMemoryConfig]
        fabric_discovery_machine_id: str
        failover_recovery_point_id: Optional[str]
        firmware_type: Optional[str]
        hyper_v_generation: str
        initial_replication_progress_percentage: Optional[int]
        instance_type: Literal["HyperVToAzStackHCI"]
        is_dynamic_ram: Optional[bool]
        last_recovery_point_id: Optional[str]
        last_recovery_point_received: Optional[datetime]
        last_replication_update_time: Optional[datetime]
        nics_to_include: list[HyperVToAzStackHCINicInput]
        os_name: Optional[str]
        os_type: Optional[str]
        protected_disks: Optional[list[HyperVToAzStackHCIProtectedDiskProperties]]
        protected_nics: Optional[list[HyperVToAzStackHCIProtectedNicProperties]]
        resync_progress_percentage: Optional[int]
        run_as_account_id: str
        source_appliance_name: Optional[str]
        source_cpu_cores: Optional[int]
        source_fabric_agent_name: str
        source_memory_in_mega_bytes: Optional[float]
        source_vm_name: Optional[str]
        storage_container_id: str
        target_appliance_name: Optional[str]
        target_arc_cluster_custom_location_id: str
        target_az_stack_hci_cluster_name: Optional[str]
        target_cpu_cores: Optional[int]
        target_fabric_agent_name: str
        target_hci_cluster_id: str
        target_location: Optional[str]
        target_memory_in_mega_bytes: Optional[int]
        target_network_id: Optional[str]
        target_resource_group_id: str
        target_vm_bios_id: Optional[str]
        target_vm_name: Optional[str]
        test_network_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                custom_location_region: str, 
                disks_to_include: list[HyperVToAzStackHCIDiskInput], 
                dynamic_memory_config: Optional[ProtectedItemDynamicMemoryConfig] = ..., 
                fabric_discovery_machine_id: str, 
                hyper_v_generation: str, 
                is_dynamic_ram: Optional[bool] = ..., 
                nics_to_include: list[HyperVToAzStackHCINicInput], 
                run_as_account_id: str, 
                source_fabric_agent_name: str, 
                storage_container_id: str, 
                target_arc_cluster_custom_location_id: str, 
                target_cpu_cores: Optional[int] = ..., 
                target_fabric_agent_name: str, 
                target_hci_cluster_id: str, 
                target_memory_in_mega_bytes: Optional[int] = ..., 
                target_network_id: Optional[str] = ..., 
                target_resource_group_id: str, 
                target_vm_name: Optional[str] = ..., 
                test_network_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesdatareplication.models.HyperVToAzStackHCIProtectedItemModelCustomPropertiesUpdate(ProtectedItemModelCustomPropertiesUpdate, discriminator='HyperVToAzStackHCI'):
        dynamic_memory_config: Optional[ProtectedItemDynamicMemoryConfig]
        instance_type: Literal["HyperVToAzStackHCI"]
        is_dynamic_ram: Optional[bool]
        nics_to_include: Optional[list[HyperVToAzStackHCINicInput]]
        os_type: Optional[str]
        target_cpu_cores: Optional[int]
        target_memory_in_mega_bytes: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                dynamic_memory_config: Optional[ProtectedItemDynamicMemoryConfig] = ..., 
                is_dynamic_ram: Optional[bool] = ..., 
                nics_to_include: Optional[list[HyperVToAzStackHCINicInput]] = ..., 
                os_type: Optional[str] = ..., 
                target_cpu_cores: Optional[int] = ..., 
                target_memory_in_mega_bytes: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesdatareplication.models.HyperVToAzStackHCIProtectedNicProperties(_Model):
        mac_address: Optional[str]
        network_name: Optional[str]
        nic_id: Optional[str]
        selection_type_for_failover: Optional[Union[str, VMNicSelection]]
        target_network_id: Optional[str]
        test_network_id: Optional[str]


    class azure.mgmt.recoveryservicesdatareplication.models.HyperVToAzStackHCIRecoveryPointModelCustomProperties(RecoveryPointModelCustomProperties, discriminator='HyperVToAzStackHCI'):
        disk_ids: Optional[list[str]]
        instance_type: Literal["HyperVToAzStackHCI"]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesdatareplication.models.HyperVToAzStackHCIReplicationExtensionModelCustomProperties(ReplicationExtensionModelCustomProperties, discriminator='HyperVToAzStackHCI'):
        asr_service_uri: Optional[str]
        az_stack_hci_fabric_arm_id: str
        az_stack_hci_site_id: Optional[str]
        gateway_service_uri: Optional[str]
        hyper_v_fabric_arm_id: str
        hyper_v_site_id: Optional[str]
        instance_type: Literal["HyperVToAzStackHCI"]
        rcm_service_uri: Optional[str]
        resource_group: Optional[str]
        resource_location: Optional[str]
        source_gateway_service_id: Optional[str]
        source_storage_container_name: Optional[str]
        storage_account_id: Optional[str]
        storage_account_sas_secret_name: Optional[str]
        subscription_id: Optional[str]
        target_gateway_service_id: Optional[str]
        target_storage_container_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                az_stack_hci_fabric_arm_id: str, 
                hyper_v_fabric_arm_id: str, 
                storage_account_id: Optional[str] = ..., 
                storage_account_sas_secret_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesdatareplication.models.IdentityModel(_Model):
        aad_authority: str
        application_id: str
        audience: str
        object_id: str
        tenant_id: str

        @overload
        def __init__(
                self, 
                *, 
                aad_authority: str, 
                application_id: str, 
                audience: str, 
                object_id: str, 
                tenant_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesdatareplication.models.InnerHealthErrorModel(_Model):
        category: Optional[str]
        causes: Optional[str]
        code: Optional[str]
        creation_time: Optional[datetime]
        health_category: Optional[str]
        is_customer_resolvable: Optional[bool]
        message: Optional[str]
        recommendation: Optional[str]
        severity: Optional[str]
        source: Optional[str]
        summary: Optional[str]


    class azure.mgmt.recoveryservicesdatareplication.models.JobModel(ProxyResource):
        id: str
        name: str
        properties: Optional[JobModelProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[JobModelProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesdatareplication.models.JobModelCustomProperties(_Model):
        affected_object_details: Optional[AffectedObjectDetails]
        instance_type: str

        @overload
        def __init__(
                self, 
                *, 
                instance_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesdatareplication.models.JobModelProperties(_Model):
        activity_id: Optional[str]
        allowed_actions: Optional[list[str]]
        custom_properties: JobModelCustomProperties
        display_name: Optional[str]
        end_time: Optional[datetime]
        errors: Optional[list[ErrorModel]]
        object_id: Optional[str]
        object_internal_id: Optional[str]
        object_internal_name: Optional[str]
        object_name: Optional[str]
        object_type: Optional[Union[str, JobObjectType]]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        replication_provider_id: Optional[str]
        source_fabric_provider_id: Optional[str]
        start_time: Optional[datetime]
        state: Optional[Union[str, JobState]]
        target_fabric_provider_id: Optional[str]
        tasks: Optional[list[TaskModel]]

        @overload
        def __init__(
                self, 
                *, 
                custom_properties: JobModelCustomProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesdatareplication.models.JobObjectType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVS_DISK_POOL = "AvsDiskPool"
        FABRIC = "Fabric"
        FABRIC_AGENT = "FabricAgent"
        POLICY = "Policy"
        PROTECTED_ITEM = "ProtectedItem"
        RECOVERY_PLAN = "RecoveryPlan"
        REPLICATION_EXTENSION = "ReplicationExtension"
        VAULT = "Vault"


    class azure.mgmt.recoveryservicesdatareplication.models.JobState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELLED = "Cancelled"
        CANCELLING = "Cancelling"
        COMPLETED_WITH_ERRORS = "CompletedWithErrors"
        COMPLETED_WITH_INFORMATION = "CompletedWithInformation"
        COMPLETED_WITH_WARNINGS = "CompletedWithWarnings"
        FAILED = "Failed"
        PENDING = "Pending"
        STARTED = "Started"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.recoveryservicesdatareplication.models.ManagedServiceIdentity(_Model):
        principal_id: Optional[str]
        tenant_id: Optional[str]
        type: Union[str, ManagedServiceIdentityType]
        user_assigned_identities: Optional[dict[str, UserAssignedIdentity]]

        @overload
        def __init__(
                self, 
                *, 
                type: Union[str, ManagedServiceIdentityType], 
                user_assigned_identities: Optional[dict[str, UserAssignedIdentity]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesdatareplication.models.ManagedServiceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        SYSTEM_ASSIGNED_USER_ASSIGNED = "SystemAssigned,UserAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.recoveryservicesdatareplication.models.Operation(_Model):
        action_type: Optional[Union[str, ActionType]]
        display: Optional[OperationDisplay]
        is_data_action: Optional[bool]
        name: Optional[str]
        origin: Optional[Union[str, Origin]]

        @overload
        def __init__(
                self, 
                *, 
                display: Optional[OperationDisplay] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesdatareplication.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.recoveryservicesdatareplication.models.OperationStatus(_Model):
        end_time: Optional[str]
        id: Optional[str]
        name: Optional[str]
        start_time: Optional[str]
        status: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                end_time: Optional[str] = ..., 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                start_time: Optional[str] = ..., 
                status: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesdatareplication.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.recoveryservicesdatareplication.models.PlannedFailoverModel(_Model):
        properties: PlannedFailoverModelProperties

        @overload
        def __init__(
                self, 
                *, 
                properties: PlannedFailoverModelProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesdatareplication.models.PlannedFailoverModelCustomProperties(_Model):
        instance_type: str

        @overload
        def __init__(
                self, 
                *, 
                instance_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesdatareplication.models.PlannedFailoverModelProperties(_Model):
        custom_properties: PlannedFailoverModelCustomProperties

        @overload
        def __init__(
                self, 
                *, 
                custom_properties: PlannedFailoverModelCustomProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesdatareplication.models.PolicyModel(ProxyResource):
        id: str
        name: str
        properties: Optional[PolicyModelProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[PolicyModelProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesdatareplication.models.PolicyModelCustomProperties(_Model):
        instance_type: str

        @overload
        def __init__(
                self, 
                *, 
                instance_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesdatareplication.models.PolicyModelProperties(_Model):
        custom_properties: PolicyModelCustomProperties
        provisioning_state: Optional[Union[str, ProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                custom_properties: PolicyModelCustomProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesdatareplication.models.PrivateEndpoint(_Model):
        id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesdatareplication.models.PrivateEndpointConnection(ProxyResource):
        id: str
        name: str
        properties: Optional[PrivateEndpointConnectionResponseProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[PrivateEndpointConnectionResponseProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesdatareplication.models.PrivateEndpointConnectionResponseProperties(_Model):
        private_endpoint: Optional[PrivateEndpoint]
        private_link_service_connection_state: Optional[PrivateLinkServiceConnectionState]
        provisioning_state: Optional[Union[str, ProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                private_endpoint: Optional[PrivateEndpoint] = ..., 
                private_link_service_connection_state: Optional[PrivateLinkServiceConnectionState] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesdatareplication.models.PrivateEndpointConnectionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPROVED = "Approved"
        DISCONNECTED = "Disconnected"
        PENDING = "Pending"
        REJECTED = "Rejected"


    class azure.mgmt.recoveryservicesdatareplication.models.PrivateLinkResource(ProxyResource):
        id: str
        name: str
        properties: Optional[PrivateLinkResourceProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[PrivateLinkResourceProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesdatareplication.models.PrivateLinkResourceProperties(_Model):
        group_id: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        required_members: Optional[list[str]]
        required_zone_names: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                group_id: Optional[str] = ..., 
                required_members: Optional[list[str]] = ..., 
                required_zone_names: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesdatareplication.models.PrivateLinkServiceConnectionState(_Model):
        actions_required: Optional[str]
        description: Optional[str]
        status: Optional[Union[str, PrivateEndpointConnectionStatus]]

        @overload
        def __init__(
                self, 
                *, 
                actions_required: Optional[str] = ..., 
                description: Optional[str] = ..., 
                status: Optional[Union[str, PrivateEndpointConnectionStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesdatareplication.models.ProtectedItemActiveLocation(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PRIMARY = "Primary"
        RECOVERY = "Recovery"


    class azure.mgmt.recoveryservicesdatareplication.models.ProtectedItemDynamicMemoryConfig(_Model):
        maximum_memory_in_mega_bytes: int
        minimum_memory_in_mega_bytes: int
        target_memory_buffer_percentage: int

        @overload
        def __init__(
                self, 
                *, 
                maximum_memory_in_mega_bytes: int, 
                minimum_memory_in_mega_bytes: int, 
                target_memory_buffer_percentage: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesdatareplication.models.ProtectedItemJobProperties(_Model):
        display_name: Optional[str]
        end_time: Optional[datetime]
        id: Optional[str]
        name: Optional[str]
        scenario_name: Optional[str]
        start_time: Optional[datetime]
        state: Optional[str]


    class azure.mgmt.recoveryservicesdatareplication.models.ProtectedItemModel(ProxyResource):
        id: str
        name: str
        properties: Optional[ProtectedItemModelProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ProtectedItemModelProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesdatareplication.models.ProtectedItemModelCustomProperties(_Model):
        instance_type: str

        @overload
        def __init__(
                self, 
                *, 
                instance_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesdatareplication.models.ProtectedItemModelCustomPropertiesUpdate(_Model):
        instance_type: str

        @overload
        def __init__(
                self, 
                *, 
                instance_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesdatareplication.models.ProtectedItemModelProperties(_Model):
        allowed_jobs: Optional[list[str]]
        correlation_id: Optional[str]
        current_job: Optional[ProtectedItemJobProperties]
        custom_properties: ProtectedItemModelCustomProperties
        fabric_agent_id: Optional[str]
        fabric_id: Optional[str]
        fabric_object_id: Optional[str]
        fabric_object_name: Optional[str]
        health_errors: Optional[list[HealthErrorModel]]
        last_failed_enable_protection_job: Optional[ProtectedItemJobProperties]
        last_failed_planned_failover_job: Optional[ProtectedItemJobProperties]
        last_successful_planned_failover_time: Optional[datetime]
        last_successful_test_failover_time: Optional[datetime]
        last_successful_unplanned_failover_time: Optional[datetime]
        last_test_failover_job: Optional[ProtectedItemJobProperties]
        policy_name: str
        protection_state: Optional[Union[str, ProtectionState]]
        protection_state_description: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        replication_extension_name: str
        replication_health: Optional[Union[str, HealthStatus]]
        resync_required: Optional[bool]
        resynchronization_state: Optional[Union[str, ResynchronizationState]]
        source_fabric_provider_id: Optional[str]
        target_fabric_agent_id: Optional[str]
        target_fabric_id: Optional[str]
        target_fabric_provider_id: Optional[str]
        test_failover_state: Optional[Union[str, TestFailoverState]]
        test_failover_state_description: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                custom_properties: ProtectedItemModelCustomProperties, 
                policy_name: str, 
                replication_extension_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesdatareplication.models.ProtectedItemModelPropertiesUpdate(_Model):
        custom_properties: Optional[ProtectedItemModelCustomPropertiesUpdate]

        @overload
        def __init__(
                self, 
                *, 
                custom_properties: Optional[ProtectedItemModelCustomPropertiesUpdate] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesdatareplication.models.ProtectedItemModelUpdate(_Model):
        id: Optional[str]
        name: Optional[str]
        properties: Optional[ProtectedItemModelPropertiesUpdate]
        system_data: Optional[SystemData]
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ProtectedItemModelPropertiesUpdate] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesdatareplication.models.ProtectionState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCEL_FAILOVER_FAILED_ON_PRIMARY = "CancelFailoverFailedOnPrimary"
        CANCEL_FAILOVER_FAILED_ON_RECOVERY = "CancelFailoverFailedOnRecovery"
        CANCEL_FAILOVER_IN_PROGRESS_ON_PRIMARY = "CancelFailoverInProgressOnPrimary"
        CANCEL_FAILOVER_IN_PROGRESS_ON_RECOVERY = "CancelFailoverInProgressOnRecovery"
        CANCEL_FAILOVER_STATES_BEGIN = "CancelFailoverStatesBegin"
        CANCEL_FAILOVER_STATES_END = "CancelFailoverStatesEnd"
        CHANGE_RECOVERY_POINT_COMPLETED = "ChangeRecoveryPointCompleted"
        CHANGE_RECOVERY_POINT_FAILED = "ChangeRecoveryPointFailed"
        CHANGE_RECOVERY_POINT_INITIATED = "ChangeRecoveryPointInitiated"
        CHANGE_RECOVERY_POINT_STATES_BEGIN = "ChangeRecoveryPointStatesBegin"
        CHANGE_RECOVERY_POINT_STATES_END = "ChangeRecoveryPointStatesEnd"
        COMMIT_FAILOVER_COMPLETED = "CommitFailoverCompleted"
        COMMIT_FAILOVER_FAILED_ON_PRIMARY = "CommitFailoverFailedOnPrimary"
        COMMIT_FAILOVER_FAILED_ON_RECOVERY = "CommitFailoverFailedOnRecovery"
        COMMIT_FAILOVER_IN_PROGRESS_ON_PRIMARY = "CommitFailoverInProgressOnPrimary"
        COMMIT_FAILOVER_IN_PROGRESS_ON_RECOVERY = "CommitFailoverInProgressOnRecovery"
        COMMIT_FAILOVER_STATES_BEGIN = "CommitFailoverStatesBegin"
        COMMIT_FAILOVER_STATES_END = "CommitFailoverStatesEnd"
        DISABLING_FAILED = "DisablingFailed"
        DISABLING_PROTECTION = "DisablingProtection"
        ENABLING_FAILED = "EnablingFailed"
        ENABLING_PROTECTION = "EnablingProtection"
        INITIAL_REPLICATION_COMPLETED_ON_PRIMARY = "InitialReplicationCompletedOnPrimary"
        INITIAL_REPLICATION_COMPLETED_ON_RECOVERY = "InitialReplicationCompletedOnRecovery"
        INITIAL_REPLICATION_FAILED = "InitialReplicationFailed"
        INITIAL_REPLICATION_IN_PROGRESS = "InitialReplicationInProgress"
        INITIAL_REPLICATION_STATES_BEGIN = "InitialReplicationStatesBegin"
        INITIAL_REPLICATION_STATES_END = "InitialReplicationStatesEnd"
        MARKED_FOR_DELETION = "MarkedForDeletion"
        PLANNED_FAILOVER_COMPLETED = "PlannedFailoverCompleted"
        PLANNED_FAILOVER_COMPLETING = "PlannedFailoverCompleting"
        PLANNED_FAILOVER_COMPLETION_FAILED = "PlannedFailoverCompletionFailed"
        PLANNED_FAILOVER_FAILED = "PlannedFailoverFailed"
        PLANNED_FAILOVER_INITIATED = "PlannedFailoverInitiated"
        PLANNED_FAILOVER_TRANSITION_STATES_BEGIN = "PlannedFailoverTransitionStatesBegin"
        PLANNED_FAILOVER_TRANSITION_STATES_END = "PlannedFailoverTransitionStatesEnd"
        PROTECTED = "Protected"
        PROTECTED_STATES_BEGIN = "ProtectedStatesBegin"
        PROTECTED_STATES_END = "ProtectedStatesEnd"
        REPROTECT_FAILED = "ReprotectFailed"
        REPROTECT_INITIATED = "ReprotectInitiated"
        REPROTECT_STATES_BEGIN = "ReprotectStatesBegin"
        REPROTECT_STATES_END = "ReprotectStatesEnd"
        UNPLANNED_FAILOVER_COMPLETED = "UnplannedFailoverCompleted"
        UNPLANNED_FAILOVER_COMPLETING = "UnplannedFailoverCompleting"
        UNPLANNED_FAILOVER_COMPLETION_FAILED = "UnplannedFailoverCompletionFailed"
        UNPLANNED_FAILOVER_FAILED = "UnplannedFailoverFailed"
        UNPLANNED_FAILOVER_INITIATED = "UnplannedFailoverInitiated"
        UNPLANNED_FAILOVER_TRANSITION_STATES_BEGIN = "UnplannedFailoverTransitionStatesBegin"
        UNPLANNED_FAILOVER_TRANSITION_STATES_END = "UnplannedFailoverTransitionStatesEnd"
        UNPROTECTED_STATES_BEGIN = "UnprotectedStatesBegin"
        UNPROTECTED_STATES_END = "UnprotectedStatesEnd"


    class azure.mgmt.recoveryservicesdatareplication.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETED = "Deleted"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.recoveryservicesdatareplication.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.recoveryservicesdatareplication.models.RecoveryPointModel(ProxyResource):
        id: str
        name: str
        properties: Optional[RecoveryPointModelProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[RecoveryPointModelProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesdatareplication.models.RecoveryPointModelCustomProperties(_Model):
        instance_type: str

        @overload
        def __init__(
                self, 
                *, 
                instance_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesdatareplication.models.RecoveryPointModelProperties(_Model):
        custom_properties: RecoveryPointModelCustomProperties
        provisioning_state: Optional[Union[str, ProvisioningState]]
        recovery_point_time: datetime
        recovery_point_type: Union[str, RecoveryPointType]

        @overload
        def __init__(
                self, 
                *, 
                custom_properties: RecoveryPointModelCustomProperties, 
                recovery_point_time: datetime, 
                recovery_point_type: Union[str, RecoveryPointType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesdatareplication.models.RecoveryPointType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION_CONSISTENT = "ApplicationConsistent"
        CRASH_CONSISTENT = "CrashConsistent"


    class azure.mgmt.recoveryservicesdatareplication.models.ReplicationExtensionModel(ProxyResource):
        id: str
        name: str
        properties: Optional[ReplicationExtensionModelProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ReplicationExtensionModelProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesdatareplication.models.ReplicationExtensionModelCustomProperties(_Model):
        instance_type: str

        @overload
        def __init__(
                self, 
                *, 
                instance_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesdatareplication.models.ReplicationExtensionModelProperties(_Model):
        custom_properties: ReplicationExtensionModelCustomProperties
        provisioning_state: Optional[Union[str, ProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                custom_properties: ReplicationExtensionModelCustomProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesdatareplication.models.ReplicationVaultType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISASTER_RECOVERY = "DisasterRecovery"
        MIGRATE = "Migrate"


    class azure.mgmt.recoveryservicesdatareplication.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.recoveryservicesdatareplication.models.ResynchronizationState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        RESYNCHRONIZATION_COMPLETED = "ResynchronizationCompleted"
        RESYNCHRONIZATION_FAILED = "ResynchronizationFailed"
        RESYNCHRONIZATION_INITIATED = "ResynchronizationInitiated"


    class azure.mgmt.recoveryservicesdatareplication.models.StorageContainerProperties(_Model):
        cluster_shared_volume_path: str
        name: str

        @overload
        def __init__(
                self, 
                *, 
                cluster_shared_volume_path: str, 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesdatareplication.models.SystemData(_Model):
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


    class azure.mgmt.recoveryservicesdatareplication.models.TaskModel(_Model):
        children_jobs: Optional[list[JobModel]]
        custom_properties: Optional[TaskModelCustomProperties]
        end_time: Optional[datetime]
        start_time: Optional[datetime]
        state: Optional[Union[str, TaskState]]
        task_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                children_jobs: Optional[list[JobModel]] = ..., 
                custom_properties: Optional[TaskModelCustomProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesdatareplication.models.TaskModelCustomProperties(_Model):
        instance_type: str

        @overload
        def __init__(
                self, 
                *, 
                instance_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesdatareplication.models.TaskState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELLED = "Cancelled"
        FAILED = "Failed"
        PENDING = "Pending"
        SKIPPED = "Skipped"
        STARTED = "Started"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.recoveryservicesdatareplication.models.TestFailoverCleanupJobModelCustomProperties(JobModelCustomProperties, discriminator='TestFailoverCleanupJobDetails'):
        affected_object_details: AffectedObjectDetails
        comments: Optional[str]
        instance_type: Literal["TestFailoverCleanupJobDetails"]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesdatareplication.models.TestFailoverJobModelCustomProperties(JobModelCustomProperties, discriminator='TestFailoverJobDetails'):
        affected_object_details: AffectedObjectDetails
        instance_type: Literal["TestFailoverJobDetails"]
        protected_item_details: Optional[list[FailoverProtectedItemProperties]]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesdatareplication.models.TestFailoverState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MARKED_FOR_DELETION = "MarkedForDeletion"
        NONE = "None"
        TEST_FAILOVER_CLEANUP_COMPLETING = "TestFailoverCleanupCompleting"
        TEST_FAILOVER_CLEANUP_INITIATED = "TestFailoverCleanupInitiated"
        TEST_FAILOVER_COMPLETED = "TestFailoverCompleted"
        TEST_FAILOVER_COMPLETING = "TestFailoverCompleting"
        TEST_FAILOVER_COMPLETION_FAILED = "TestFailoverCompletionFailed"
        TEST_FAILOVER_FAILED = "TestFailoverFailed"
        TEST_FAILOVER_INITIATED = "TestFailoverInitiated"


    class azure.mgmt.recoveryservicesdatareplication.models.TrackedResource(Resource):
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


    class azure.mgmt.recoveryservicesdatareplication.models.UserAssignedIdentity(_Model):
        client_id: Optional[str]
        principal_id: Optional[str]


    class azure.mgmt.recoveryservicesdatareplication.models.VMNicSelection(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NOT_SELECTED = "NotSelected"
        SELECTED_BY_DEFAULT = "SelectedByDefault"
        SELECTED_BY_USER = "SelectedByUser"
        SELECTED_BY_USER_OVERRIDE = "SelectedByUserOverride"


    class azure.mgmt.recoveryservicesdatareplication.models.VMwareFabricAgentModelCustomProperties(FabricAgentModelCustomProperties, discriminator='VMware'):
        bios_id: str
        instance_type: Literal["VMware"]
        mars_authentication_identity: IdentityModel

        @overload
        def __init__(
                self, 
                *, 
                bios_id: str, 
                mars_authentication_identity: IdentityModel
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesdatareplication.models.VMwareMigrateFabricModelCustomProperties(FabricModelCustomProperties, discriminator='VMwareMigrate'):
        instance_type: Literal["VMwareMigrate"]
        migration_solution_id: str
        vmware_site_id: str

        @overload
        def __init__(
                self, 
                *, 
                migration_solution_id: str, 
                vmware_site_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesdatareplication.models.VMwareToAzStackHCIDiskInput(_Model):
        disk_block_size: Optional[int]
        disk_controller: Optional[DiskControllerInputs]
        disk_file_format: str
        disk_id: str
        disk_identifier: Optional[str]
        disk_logical_sector_size: Optional[int]
        disk_physical_sector_size: Optional[int]
        disk_size_gb: int
        is_dynamic: Optional[bool]
        is_os_disk: bool
        storage_container_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                disk_block_size: Optional[int] = ..., 
                disk_controller: Optional[DiskControllerInputs] = ..., 
                disk_file_format: str, 
                disk_id: str, 
                disk_identifier: Optional[str] = ..., 
                disk_logical_sector_size: Optional[int] = ..., 
                disk_physical_sector_size: Optional[int] = ..., 
                disk_size_gb: int, 
                is_dynamic: Optional[bool] = ..., 
                is_os_disk: bool, 
                storage_container_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesdatareplication.models.VMwareToAzStackHCIEventModelCustomProperties(EventModelCustomProperties, discriminator='VMwareToAzStackHCI'):
        event_source_friendly_name: Optional[str]
        instance_type: Literal["VMwareToAzStackHCI"]
        protected_item_friendly_name: Optional[str]
        server_type: Optional[str]
        source_appliance_name: Optional[str]
        target_appliance_name: Optional[str]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesdatareplication.models.VMwareToAzStackHCINicInput(_Model):
        is_mac_migration_enabled: Optional[bool]
        is_static_ip_migration_enabled: Optional[bool]
        label: str
        network_name: Optional[str]
        nic_id: str
        selection_type_for_failover: Union[str, VMNicSelection]
        target_network_id: Optional[str]
        test_network_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                is_mac_migration_enabled: Optional[bool] = ..., 
                is_static_ip_migration_enabled: Optional[bool] = ..., 
                label: str, 
                nic_id: str, 
                selection_type_for_failover: Union[str, VMNicSelection], 
                target_network_id: Optional[str] = ..., 
                test_network_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesdatareplication.models.VMwareToAzStackHCIPlannedFailoverModelCustomProperties(PlannedFailoverModelCustomProperties, discriminator='VMwareToAzStackHCI'):
        instance_type: Literal["VMwareToAzStackHCI"]
        shutdown_source_vm: bool

        @overload
        def __init__(
                self, 
                *, 
                shutdown_source_vm: bool
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesdatareplication.models.VMwareToAzStackHCIPolicyModelCustomProperties(PolicyModelCustomProperties, discriminator='VMwareToAzStackHCI'):
        app_consistent_frequency_in_minutes: int
        crash_consistent_frequency_in_minutes: int
        instance_type: Literal["VMwareToAzStackHCI"]
        recovery_point_history_in_minutes: int

        @overload
        def __init__(
                self, 
                *, 
                app_consistent_frequency_in_minutes: int, 
                crash_consistent_frequency_in_minutes: int, 
                recovery_point_history_in_minutes: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesdatareplication.models.VMwareToAzStackHCIProtectedDiskProperties(_Model):
        capacity_in_bytes: Optional[int]
        disk_block_size: Optional[int]
        disk_logical_sector_size: Optional[int]
        disk_physical_sector_size: Optional[int]
        disk_type: Optional[str]
        is_dynamic: Optional[bool]
        is_os_disk: Optional[bool]
        migrate_disk_name: Optional[str]
        seed_disk_name: Optional[str]
        source_disk_id: Optional[str]
        source_disk_name: Optional[str]
        storage_container_id: Optional[str]
        storage_container_local_path: Optional[str]
        test_migrate_disk_name: Optional[str]


    class azure.mgmt.recoveryservicesdatareplication.models.VMwareToAzStackHCIProtectedItemModelCustomProperties(ProtectedItemModelCustomProperties, discriminator='VMwareToAzStackHCI'):
        active_location: Optional[Union[str, ProtectedItemActiveLocation]]
        custom_location_region: str
        disks_to_include: list[VMwareToAzStackHCIDiskInput]
        dynamic_memory_config: Optional[ProtectedItemDynamicMemoryConfig]
        fabric_discovery_machine_id: str
        failover_recovery_point_id: Optional[str]
        firmware_type: Optional[str]
        hyper_v_generation: str
        initial_replication_progress_percentage: Optional[int]
        instance_type: Literal["VMwareToAzStackHCI"]
        is_dynamic_ram: Optional[bool]
        last_recovery_point_id: Optional[str]
        last_recovery_point_received: Optional[datetime]
        last_replication_update_time: Optional[datetime]
        migration_progress_percentage: Optional[int]
        nics_to_include: list[VMwareToAzStackHCINicInput]
        os_name: Optional[str]
        os_type: Optional[str]
        perform_auto_resync: Optional[bool]
        protected_disks: Optional[list[VMwareToAzStackHCIProtectedDiskProperties]]
        protected_nics: Optional[list[VMwareToAzStackHCIProtectedNicProperties]]
        resume_progress_percentage: Optional[int]
        resume_retry_count: Optional[int]
        resync_progress_percentage: Optional[int]
        resync_required: Optional[bool]
        resync_retry_count: Optional[int]
        resync_state: Optional[Union[str, VMwareToAzureMigrateResyncState]]
        run_as_account_id: str
        source_appliance_name: Optional[str]
        source_cpu_cores: Optional[int]
        source_fabric_agent_name: str
        source_memory_in_mega_bytes: Optional[float]
        source_vm_name: Optional[str]
        storage_container_id: str
        target_appliance_name: Optional[str]
        target_arc_cluster_custom_location_id: str
        target_az_stack_hci_cluster_name: Optional[str]
        target_cpu_cores: Optional[int]
        target_fabric_agent_name: str
        target_hci_cluster_id: str
        target_location: Optional[str]
        target_memory_in_mega_bytes: Optional[int]
        target_network_id: Optional[str]
        target_resource_group_id: str
        target_vm_bios_id: Optional[str]
        target_vm_name: Optional[str]
        test_network_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                custom_location_region: str, 
                disks_to_include: list[VMwareToAzStackHCIDiskInput], 
                dynamic_memory_config: Optional[ProtectedItemDynamicMemoryConfig] = ..., 
                fabric_discovery_machine_id: str, 
                hyper_v_generation: str, 
                is_dynamic_ram: Optional[bool] = ..., 
                nics_to_include: list[VMwareToAzStackHCINicInput], 
                perform_auto_resync: Optional[bool] = ..., 
                run_as_account_id: str, 
                source_fabric_agent_name: str, 
                storage_container_id: str, 
                target_arc_cluster_custom_location_id: str, 
                target_cpu_cores: Optional[int] = ..., 
                target_fabric_agent_name: str, 
                target_hci_cluster_id: str, 
                target_memory_in_mega_bytes: Optional[int] = ..., 
                target_network_id: Optional[str] = ..., 
                target_resource_group_id: str, 
                target_vm_name: Optional[str] = ..., 
                test_network_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesdatareplication.models.VMwareToAzStackHCIProtectedItemModelCustomPropertiesUpdate(ProtectedItemModelCustomPropertiesUpdate, discriminator='VMwareToAzStackHCI'):
        dynamic_memory_config: Optional[ProtectedItemDynamicMemoryConfig]
        instance_type: Literal["VMwareToAzStackHCI"]
        is_dynamic_ram: Optional[bool]
        nics_to_include: Optional[list[VMwareToAzStackHCINicInput]]
        os_type: Optional[str]
        target_cpu_cores: Optional[int]
        target_memory_in_mega_bytes: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                dynamic_memory_config: Optional[ProtectedItemDynamicMemoryConfig] = ..., 
                is_dynamic_ram: Optional[bool] = ..., 
                nics_to_include: Optional[list[VMwareToAzStackHCINicInput]] = ..., 
                os_type: Optional[str] = ..., 
                target_cpu_cores: Optional[int] = ..., 
                target_memory_in_mega_bytes: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesdatareplication.models.VMwareToAzStackHCIProtectedNicProperties(_Model):
        is_primary_nic: Optional[bool]
        label: Optional[str]
        mac_address: Optional[str]
        network_name: Optional[str]
        nic_id: Optional[str]
        selection_type_for_failover: Optional[Union[str, VMNicSelection]]
        target_network_id: Optional[str]
        test_network_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                is_primary_nic: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesdatareplication.models.VMwareToAzStackHCIRecoveryPointModelCustomProperties(RecoveryPointModelCustomProperties, discriminator='VMwareToAzStackHCIRecoveryPointModelCustomProperties'):
        disk_ids: Optional[list[str]]
        instance_type: Literal["VMwareToAzStackHCIRecoveryPointModelCustomProperties"]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesdatareplication.models.VMwareToAzStackHCIReplicationExtensionModelCustomProperties(ReplicationExtensionModelCustomProperties, discriminator='VMwareToAzStackHCI'):
        asr_service_uri: Optional[str]
        az_stack_hci_fabric_arm_id: str
        az_stack_hci_site_id: Optional[str]
        gateway_service_uri: Optional[str]
        instance_type: Literal["VMwareToAzStackHCI"]
        rcm_service_uri: Optional[str]
        resource_group: Optional[str]
        resource_location: Optional[str]
        source_gateway_service_id: Optional[str]
        source_storage_container_name: Optional[str]
        storage_account_id: Optional[str]
        storage_account_sas_secret_name: Optional[str]
        subscription_id: Optional[str]
        target_gateway_service_id: Optional[str]
        target_storage_container_name: Optional[str]
        vmware_fabric_arm_id: str
        vmware_site_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                az_stack_hci_fabric_arm_id: str, 
                storage_account_id: Optional[str] = ..., 
                storage_account_sas_secret_name: Optional[str] = ..., 
                vmware_fabric_arm_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesdatareplication.models.VMwareToAzureMigrateResyncState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        PREPARED_FOR_RESYNCHRONIZATION = "PreparedForResynchronization"
        STARTED_RESYNCHRONIZATION = "StartedResynchronization"


    class azure.mgmt.recoveryservicesdatareplication.models.VaultIdentityModel(_Model):
        principal_id: Optional[str]
        tenant_id: Optional[str]
        type: Union[str, VaultIdentityType]

        @overload
        def __init__(
                self, 
                *, 
                type: Union[str, VaultIdentityType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesdatareplication.models.VaultIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.recoveryservicesdatareplication.models.VaultModel(TrackedResource):
        id: str
        identity: Optional[ManagedServiceIdentity]
        location: str
        name: str
        properties: Optional[VaultModelProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                location: str, 
                properties: Optional[VaultModelProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesdatareplication.models.VaultModelProperties(_Model):
        provisioning_state: Optional[Union[str, ProvisioningState]]
        service_resource_id: Optional[str]
        vault_type: Optional[Union[str, ReplicationVaultType]]

        @overload
        def __init__(
                self, 
                *, 
                vault_type: Optional[Union[str, ReplicationVaultType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservicesdatareplication.models.VaultModelUpdate(_Model):
        id: Optional[str]
        identity: Optional[VaultIdentityModel]
        name: Optional[str]
        properties: Optional[VaultModelProperties]
        system_data: Optional[SystemData]
        tags: Optional[dict[str, str]]
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[VaultIdentityModel] = ..., 
                properties: Optional[VaultModelProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


namespace azure.mgmt.recoveryservicesdatareplication.operations

    class azure.mgmt.recoveryservicesdatareplication.operations.CheckNameAvailabilityOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def post(
                self, 
                location: str, 
                body: Optional[CheckNameAvailabilityModel] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResponseModel: ...

        @overload
        def post(
                self, 
                location: str, 
                body: Optional[CheckNameAvailabilityModel] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResponseModel: ...

        @overload
        def post(
                self, 
                location: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResponseModel: ...


    class azure.mgmt.recoveryservicesdatareplication.operations.DeploymentPreflightOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def post(
                self, 
                resource_group_name: str, 
                deployment_id: str, 
                body: Optional[DeploymentPreflightModel] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DeploymentPreflightModel: ...

        @overload
        def post(
                self, 
                resource_group_name: str, 
                deployment_id: str, 
                body: Optional[DeploymentPreflightModel] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DeploymentPreflightModel: ...

        @overload
        def post(
                self, 
                resource_group_name: str, 
                deployment_id: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DeploymentPreflightModel: ...


    class azure.mgmt.recoveryservicesdatareplication.operations.EmailConfigurationOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                email_configuration_name: str, 
                body: EmailConfigurationModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EmailConfigurationModel: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                email_configuration_name: str, 
                body: EmailConfigurationModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EmailConfigurationModel: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                email_configuration_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EmailConfigurationModel: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                email_configuration_name: str, 
                **kwargs: Any
            ) -> EmailConfigurationModel: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                **kwargs: Any
            ) -> ItemPaged[EmailConfigurationModel]: ...


    class azure.mgmt.recoveryservicesdatareplication.operations.EventOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                event_name: str, 
                **kwargs: Any
            ) -> EventModel: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                *, 
                continuation_token_parameter: Optional[str] = ..., 
                odata_options: Optional[str] = ..., 
                page_size: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[EventModel]: ...


    class azure.mgmt.recoveryservicesdatareplication.operations.FabricAgentOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                fabric_name: str, 
                fabric_agent_name: str, 
                body: FabricAgentModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[FabricAgentModel]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                fabric_name: str, 
                fabric_agent_name: str, 
                body: FabricAgentModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[FabricAgentModel]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                fabric_name: str, 
                fabric_agent_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[FabricAgentModel]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                fabric_name: str, 
                fabric_agent_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                fabric_name: str, 
                fabric_agent_name: str, 
                **kwargs: Any
            ) -> FabricAgentModel: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                fabric_name: str, 
                **kwargs: Any
            ) -> ItemPaged[FabricAgentModel]: ...


    class azure.mgmt.recoveryservicesdatareplication.operations.FabricOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                fabric_name: str, 
                body: FabricModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[FabricModel]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                fabric_name: str, 
                body: FabricModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[FabricModel]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                fabric_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[FabricModel]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                fabric_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                fabric_name: str, 
                body: FabricModelUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[FabricModel]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                fabric_name: str, 
                body: FabricModelUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[FabricModel]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                fabric_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[FabricModel]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                fabric_name: str, 
                **kwargs: Any
            ) -> FabricModel: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                *, 
                continuation_token_parameter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[FabricModel]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[FabricModel]: ...


    class azure.mgmt.recoveryservicesdatareplication.operations.JobOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                job_name: str, 
                **kwargs: Any
            ) -> JobModel: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                *, 
                continuation_token_parameter: Optional[str] = ..., 
                odata_options: Optional[str] = ..., 
                page_size: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[JobModel]: ...


    class azure.mgmt.recoveryservicesdatareplication.operations.LocationBasedOperationResultsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                location: str, 
                operation_id: str, 
                **kwargs: Any
            ) -> OperationStatus: ...


    class azure.mgmt.recoveryservicesdatareplication.operations.OperationResultsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                operation_id: str, 
                **kwargs: Any
            ) -> OperationStatus: ...


    class azure.mgmt.recoveryservicesdatareplication.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


    class azure.mgmt.recoveryservicesdatareplication.operations.PolicyOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                policy_name: str, 
                body: PolicyModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PolicyModel]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                policy_name: str, 
                body: PolicyModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PolicyModel]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                policy_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PolicyModel]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                policy_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                policy_name: str, 
                **kwargs: Any
            ) -> PolicyModel: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                **kwargs: Any
            ) -> ItemPaged[PolicyModel]: ...


    class azure.mgmt.recoveryservicesdatareplication.operations.PrivateEndpointConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                **kwargs: Any
            ) -> ItemPaged[PrivateEndpointConnection]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                private_endpoint_connection_name: str, 
                body: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                private_endpoint_connection_name: str, 
                body: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                private_endpoint_connection_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...


    class azure.mgmt.recoveryservicesdatareplication.operations.PrivateLinkResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                private_link_resource_name: str, 
                **kwargs: Any
            ) -> PrivateLinkResource: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                **kwargs: Any
            ) -> ItemPaged[PrivateLinkResource]: ...


    class azure.mgmt.recoveryservicesdatareplication.operations.ProtectedItemOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                protected_item_name: str, 
                body: ProtectedItemModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ProtectedItemModel]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                protected_item_name: str, 
                body: ProtectedItemModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ProtectedItemModel]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                protected_item_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ProtectedItemModel]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                protected_item_name: str, 
                *, 
                force_delete: Optional[bool] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_planned_failover(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                protected_item_name: str, 
                body: PlannedFailoverModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PlannedFailoverModel]: ...

        @overload
        def begin_planned_failover(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                protected_item_name: str, 
                body: PlannedFailoverModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PlannedFailoverModel]: ...

        @overload
        def begin_planned_failover(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                protected_item_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PlannedFailoverModel]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                protected_item_name: str, 
                body: ProtectedItemModelUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ProtectedItemModel]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                protected_item_name: str, 
                body: ProtectedItemModelUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ProtectedItemModel]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                protected_item_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ProtectedItemModel]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                protected_item_name: str, 
                **kwargs: Any
            ) -> ProtectedItemModel: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                *, 
                continuation_token_parameter: Optional[str] = ..., 
                odata_options: Optional[str] = ..., 
                page_size: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[ProtectedItemModel]: ...


    class azure.mgmt.recoveryservicesdatareplication.operations.RecoveryPointOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                protected_item_name: str, 
                recovery_point_name: str, 
                **kwargs: Any
            ) -> RecoveryPointModel: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                protected_item_name: str, 
                **kwargs: Any
            ) -> ItemPaged[RecoveryPointModel]: ...


    class azure.mgmt.recoveryservicesdatareplication.operations.ReplicationExtensionOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                replication_extension_name: str, 
                body: ReplicationExtensionModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ReplicationExtensionModel]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                replication_extension_name: str, 
                body: ReplicationExtensionModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ReplicationExtensionModel]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                replication_extension_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ReplicationExtensionModel]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                replication_extension_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                replication_extension_name: str, 
                **kwargs: Any
            ) -> ReplicationExtensionModel: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ReplicationExtensionModel]: ...


    class azure.mgmt.recoveryservicesdatareplication.operations.VaultOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                body: VaultModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VaultModel]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                body: VaultModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VaultModel]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VaultModel]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                body: VaultModelUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VaultModel]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                body: VaultModelUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VaultModel]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VaultModel]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                **kwargs: Any
            ) -> VaultModel: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                *, 
                continuation_token_parameter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[VaultModel]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[VaultModel]: ...


namespace azure.mgmt.recoveryservicesdatareplication.types

    class azure.mgmt.recoveryservicesdatareplication.types.AzStackHCIClusterProperties(TypedDict, total=False):
        key "clusterName": Required[str]
        key "resourceName": Required[str]
        key "storageAccountName": Required[str]
        key "storageContainers": Required[list[StorageContainerProperties]]
        clusterName: str
        resourceName: str
        storageAccountName: str
        storageContainers: list[StorageContainerProperties]


    class azure.mgmt.recoveryservicesdatareplication.types.AzStackHCIFabricModelCustomProperties(TypedDict, total=False):
        key "azStackHciSiteId": Required[str]
        key "cluster": Required[AzStackHCIClusterProperties]
        key "fabricContainerId": str
        key "fabricResourceId": str
        key "instanceType": Required[Literal["AzStackHCI"]]
        key "migrationHubUri": str
        key "migrationSolutionId": Required[str]
        applianceName: list[str]
        azStackHciSiteId: str
        cluster: AzStackHCIClusterProperties
        fabricContainerId: str
        fabricResourceId: str
        instanceType: Literal[AzStackHCI]
        migrationHubUri: str
        migrationSolutionId: str


    class azure.mgmt.recoveryservicesdatareplication.types.CheckNameAvailabilityModel(TypedDict, total=False):
        key "name": str
        key "type": str
        name: str
        type: str


    class azure.mgmt.recoveryservicesdatareplication.types.DeploymentPreflightModel(TypedDict, total=False):
        resources: list[DeploymentPreflightResource]


    class azure.mgmt.recoveryservicesdatareplication.types.DeploymentPreflightResource(TypedDict, total=False):
        key "apiVersion": str
        key "location": str
        key "name": str
        key "properties": Any
        key "type": str
        apiVersion: str
        location: str
        name: str
        properties: Any
        type: str


    class azure.mgmt.recoveryservicesdatareplication.types.DiskControllerInputs(TypedDict, total=False):
        key "controllerId": Required[int]
        key "controllerLocation": Required[int]
        key "controllerName": Required[str]
        controllerId: int
        controllerLocation: int
        controllerName: str


    class azure.mgmt.recoveryservicesdatareplication.types.EmailConfigurationModel(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('EmailConfigurationModelProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: EmailConfigurationModelProperties
        systemData: SystemData
        type: str


    class azure.mgmt.recoveryservicesdatareplication.types.EmailConfigurationModelProperties(TypedDict, total=False):
        key "locale": str
        key "provisioningState": Union[str, ProvisioningState]
        key "sendToOwners": Required[bool]
        customEmailAddresses: list[str]
        locale: str
        provisioningState: Union[str, ProvisioningState]
        sendToOwners: bool


    class azure.mgmt.recoveryservicesdatareplication.types.FabricAgentModel(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('FabricAgentModelProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: FabricAgentModelProperties
        systemData: SystemData
        type: str


    class azure.mgmt.recoveryservicesdatareplication.types.FabricAgentModelCustomProperties(TypedDict, total=False):
        key "biosId": Required[str]
        key "instanceType": Required[Literal["VMware"]]
        key "marsAuthenticationIdentity": Required[IdentityModel]
        biosId: str
        instanceType: Literal[VMware]
        marsAuthenticationIdentity: IdentityModel


    class azure.mgmt.recoveryservicesdatareplication.types.FabricAgentModelProperties(TypedDict, total=False):
        key "authenticationIdentity": Required[IdentityModel]
        key "correlationId": str
        key "customProperties": Required[FabricAgentModelCustomProperties]
        key "isResponsive": bool
        key "lastHeartbeat": str
        key "machineId": Required[str]
        key "machineName": Required[str]
        key "provisioningState": Union[str, ProvisioningState]
        key "resourceAccessIdentity": Required[IdentityModel]
        key "versionNumber": str
        authenticationIdentity: IdentityModel
        correlationId: str
        customProperties: FabricAgentModelCustomProperties
        healthErrors: list[HealthErrorModel]
        isResponsive: bool
        lastHeartbeat: str
        machineId: str
        machineName: str
        provisioningState: Union[str, ProvisioningState]
        resourceAccessIdentity: IdentityModel
        versionNumber: str


    class azure.mgmt.recoveryservicesdatareplication.types.FabricModel(TrackedResource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('FabricModelProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: FabricModelProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.recoveryservicesdatareplication.types.FabricModelProperties(TypedDict, total=False):
        key "customProperties": Required[FabricModelCustomProperties]
        key "health": Union[str, HealthStatus]
        key "provisioningState": Union[str, ProvisioningState]
        key "serviceEndpoint": str
        key "serviceResourceId": str
        customProperties: FabricModelCustomProperties
        health: Union[str, HealthStatus]
        healthErrors: list[HealthErrorModel]
        provisioningState: Union[str, ProvisioningState]
        serviceEndpoint: str
        serviceResourceId: str


    class azure.mgmt.recoveryservicesdatareplication.types.FabricModelUpdate(TypedDict, total=False):
        key "id": str
        key "name": str
        key "properties": ForwardRef('FabricModelProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: FabricModelProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.recoveryservicesdatareplication.types.HealthErrorModel(TypedDict, total=False):
        key "affectedResourceType": str
        key "category": str
        key "causes": str
        key "code": str
        key "creationTime": str
        key "healthCategory": str
        key "isCustomerResolvable": bool
        key "message": str
        key "recommendation": str
        key "severity": str
        key "source": str
        key "summary": str
        affectedResourceCorrelationIds: list[str]
        affectedResourceType: str
        category: str
        causes: str
        childErrors: list[InnerHealthErrorModel]
        code: str
        creationTime: str
        healthCategory: str
        isCustomerResolvable: bool
        message: str
        recommendation: str
        severity: str
        source: str
        summary: str


    class azure.mgmt.recoveryservicesdatareplication.types.HyperVMigrateFabricModelCustomProperties(TypedDict, total=False):
        key "fabricContainerId": str
        key "fabricResourceId": str
        key "hyperVSiteId": Required[str]
        key "instanceType": Required[Literal["HyperVMigrate"]]
        key "migrationHubUri": str
        key "migrationSolutionId": Required[str]
        fabricContainerId: str
        fabricResourceId: str
        hyperVSiteId: str
        instanceType: Literal[HyperVMigrate]
        migrationHubUri: str
        migrationSolutionId: str


    class azure.mgmt.recoveryservicesdatareplication.types.HyperVToAzStackHCIDiskInput(TypedDict, total=False):
        key "diskBlockSize": int
        key "diskController": ForwardRef('DiskControllerInputs', module='types')
        key "diskFileFormat": Required[str]
        key "diskId": Required[str]
        key "diskIdentifier": str
        key "diskLogicalSectorSize": int
        key "diskPhysicalSectorSize": int
        key "diskSizeGB": Required[int]
        key "isDynamic": bool
        key "isOsDisk": Required[bool]
        key "storageContainerId": str
        diskBlockSize: int
        diskController: DiskControllerInputs
        diskFileFormat: str
        diskId: str
        diskIdentifier: str
        diskLogicalSectorSize: int
        diskPhysicalSectorSize: int
        diskSizeGB: int
        isDynamic: bool
        isOsDisk: bool
        storageContainerId: str


    class azure.mgmt.recoveryservicesdatareplication.types.HyperVToAzStackHCINicInput(TypedDict, total=False):
        key "isMacMigrationEnabled": bool
        key "isStaticIpMigrationEnabled": bool
        key "networkName": str
        key "nicId": Required[str]
        key "selectionTypeForFailover": Required[Union[str, VMNicSelection]]
        key "targetNetworkId": str
        key "testNetworkId": str
        isMacMigrationEnabled: bool
        isStaticIpMigrationEnabled: bool
        networkName: str
        nicId: str
        selectionTypeForFailover: Union[str, VMNicSelection]
        targetNetworkId: str
        testNetworkId: str


    class azure.mgmt.recoveryservicesdatareplication.types.HyperVToAzStackHCIPlannedFailoverModelCustomProperties(TypedDict, total=False):
        key "instanceType": Required[Literal["HyperVToAzStackHCI"]]
        key "shutdownSourceVM": Required[bool]
        instanceType: Literal[HyperVToAzStackHCI]
        shutdownSourceVM: bool


    class azure.mgmt.recoveryservicesdatareplication.types.HyperVToAzStackHCIPolicyModelCustomProperties(TypedDict, total=False):
        key "appConsistentFrequencyInMinutes": Required[int]
        key "crashConsistentFrequencyInMinutes": Required[int]
        key "instanceType": Required[Literal["HyperVToAzStackHCI"]]
        key "recoveryPointHistoryInMinutes": Required[int]
        appConsistentFrequencyInMinutes: int
        crashConsistentFrequencyInMinutes: int
        instanceType: Literal[HyperVToAzStackHCI]
        recoveryPointHistoryInMinutes: int


    class azure.mgmt.recoveryservicesdatareplication.types.HyperVToAzStackHCIProtectedDiskProperties(TypedDict, total=False):
        key "capacityInBytes": int
        key "diskBlockSize": int
        key "diskLogicalSectorSize": int
        key "diskPhysicalSectorSize": int
        key "diskType": str
        key "isDynamic": bool
        key "isOsDisk": bool
        key "migrateDiskName": str
        key "seedDiskName": str
        key "sourceDiskId": str
        key "sourceDiskName": str
        key "storageContainerId": str
        key "storageContainerLocalPath": str
        key "testMigrateDiskName": str
        capacityInBytes: int
        diskBlockSize: int
        diskLogicalSectorSize: int
        diskPhysicalSectorSize: int
        diskType: str
        isDynamic: bool
        isOsDisk: bool
        migrateDiskName: str
        seedDiskName: str
        sourceDiskId: str
        sourceDiskName: str
        storageContainerId: str
        storageContainerLocalPath: str
        testMigrateDiskName: str


    class azure.mgmt.recoveryservicesdatareplication.types.HyperVToAzStackHCIProtectedItemModelCustomProperties(TypedDict, total=False):
        key "activeLocation": Union[str, ProtectedItemActiveLocation]
        key "customLocationRegion": Required[str]
        key "disksToInclude": Required[list[HyperVToAzStackHCIDiskInput]]
        key "dynamicMemoryConfig": ForwardRef('ProtectedItemDynamicMemoryConfig', module='types')
        key "fabricDiscoveryMachineId": Required[str]
        key "failoverRecoveryPointId": str
        key "firmwareType": str
        key "hyperVGeneration": Required[str]
        key "initialReplicationProgressPercentage": int
        key "instanceType": Required[Literal["HyperVToAzStackHCI"]]
        key "isDynamicRam": bool
        key "lastRecoveryPointId": str
        key "lastRecoveryPointReceived": str
        key "lastReplicationUpdateTime": str
        key "nicsToInclude": Required[list[HyperVToAzStackHCINicInput]]
        key "osName": str
        key "osType": str
        key "resyncProgressPercentage": int
        key "runAsAccountId": Required[str]
        key "sourceApplianceName": str
        key "sourceCpuCores": int
        key "sourceFabricAgentName": Required[str]
        key "sourceMemoryInMegaBytes": float
        key "sourceVmName": str
        key "storageContainerId": Required[str]
        key "targetApplianceName": str
        key "targetArcClusterCustomLocationId": Required[str]
        key "targetAzStackHciClusterName": str
        key "targetCpuCores": int
        key "targetFabricAgentName": Required[str]
        key "targetHciClusterId": Required[str]
        key "targetLocation": str
        key "targetMemoryInMegaBytes": int
        key "targetNetworkId": str
        key "targetResourceGroupId": Required[str]
        key "targetVmBiosId": str
        key "targetVmName": str
        key "testNetworkId": str
        activeLocation: Union[str, ProtectedItemActiveLocation]
        customLocationRegion: str
        disksToInclude: list[HyperVToAzStackHCIDiskInput]
        dynamicMemoryConfig: ProtectedItemDynamicMemoryConfig
        fabricDiscoveryMachineId: str
        failoverRecoveryPointId: str
        firmwareType: str
        hyperVGeneration: str
        initialReplicationProgressPercentage: int
        instanceType: Literal[HyperVToAzStackHCI]
        isDynamicRam: bool
        lastRecoveryPointId: str
        lastRecoveryPointReceived: str
        lastReplicationUpdateTime: str
        nicsToInclude: list[HyperVToAzStackHCINicInput]
        osName: str
        osType: str
        protectedDisks: list[HyperVToAzStackHCIProtectedDiskProperties]
        protectedNics: list[HyperVToAzStackHCIProtectedNicProperties]
        resyncProgressPercentage: int
        runAsAccountId: str
        sourceApplianceName: str
        sourceCpuCores: int
        sourceFabricAgentName: str
        sourceMemoryInMegaBytes: float
        sourceVmName: str
        storageContainerId: str
        targetApplianceName: str
        targetArcClusterCustomLocationId: str
        targetAzStackHciClusterName: str
        targetCpuCores: int
        targetFabricAgentName: str
        targetHciClusterId: str
        targetLocation: str
        targetMemoryInMegaBytes: int
        targetNetworkId: str
        targetResourceGroupId: str
        targetVmBiosId: str
        targetVmName: str
        testNetworkId: str


    class azure.mgmt.recoveryservicesdatareplication.types.HyperVToAzStackHCIProtectedItemModelCustomPropertiesUpdate(TypedDict, total=False):
        key "dynamicMemoryConfig": ForwardRef('ProtectedItemDynamicMemoryConfig', module='types')
        key "instanceType": Required[Literal["HyperVToAzStackHCI"]]
        key "isDynamicRam": bool
        key "osType": str
        key "targetCpuCores": int
        key "targetMemoryInMegaBytes": int
        dynamicMemoryConfig: ProtectedItemDynamicMemoryConfig
        instanceType: Literal[HyperVToAzStackHCI]
        isDynamicRam: bool
        nicsToInclude: list[HyperVToAzStackHCINicInput]
        osType: str
        targetCpuCores: int
        targetMemoryInMegaBytes: int


    class azure.mgmt.recoveryservicesdatareplication.types.HyperVToAzStackHCIProtectedNicProperties(TypedDict, total=False):
        key "macAddress": str
        key "networkName": str
        key "nicId": str
        key "selectionTypeForFailover": Union[str, VMNicSelection]
        key "targetNetworkId": str
        key "testNetworkId": str
        macAddress: str
        networkName: str
        nicId: str
        selectionTypeForFailover: Union[str, VMNicSelection]
        targetNetworkId: str
        testNetworkId: str


    class azure.mgmt.recoveryservicesdatareplication.types.HyperVToAzStackHCIReplicationExtensionModelCustomProperties(TypedDict, total=False):
        key "asrServiceUri": str
        key "azStackHciFabricArmId": Required[str]
        key "azStackHciSiteId": str
        key "gatewayServiceUri": str
        key "hyperVFabricArmId": Required[str]
        key "hyperVSiteId": str
        key "instanceType": Required[Literal["HyperVToAzStackHCI"]]
        key "rcmServiceUri": str
        key "resourceGroup": str
        key "resourceLocation": str
        key "sourceGatewayServiceId": str
        key "sourceStorageContainerName": str
        key "storageAccountId": str
        key "storageAccountSasSecretName": str
        key "subscriptionId": str
        key "targetGatewayServiceId": str
        key "targetStorageContainerName": str
        asrServiceUri: str
        azStackHciFabricArmId: str
        azStackHciSiteId: str
        gatewayServiceUri: str
        hyperVFabricArmId: str
        hyperVSiteId: str
        instanceType: Literal[HyperVToAzStackHCI]
        rcmServiceUri: str
        resourceGroup: str
        resourceLocation: str
        sourceGatewayServiceId: str
        sourceStorageContainerName: str
        storageAccountId: str
        storageAccountSasSecretName: str
        subscriptionId: str
        targetGatewayServiceId: str
        targetStorageContainerName: str


    class azure.mgmt.recoveryservicesdatareplication.types.IdentityModel(TypedDict, total=False):
        key "aadAuthority": Required[str]
        key "applicationId": Required[str]
        key "audience": Required[str]
        key "objectId": Required[str]
        key "tenantId": Required[str]
        aadAuthority: str
        applicationId: str
        audience: str
        objectId: str
        tenantId: str


    class azure.mgmt.recoveryservicesdatareplication.types.InnerHealthErrorModel(TypedDict, total=False):
        key "category": str
        key "causes": str
        key "code": str
        key "creationTime": str
        key "healthCategory": str
        key "isCustomerResolvable": bool
        key "message": str
        key "recommendation": str
        key "severity": str
        key "source": str
        key "summary": str
        category: str
        causes: str
        code: str
        creationTime: str
        healthCategory: str
        isCustomerResolvable: bool
        message: str
        recommendation: str
        severity: str
        source: str
        summary: str


    class azure.mgmt.recoveryservicesdatareplication.types.ManagedServiceIdentity(TypedDict, total=False):
        key "principalId": str
        key "tenantId": str
        key "type": Required[Union[str, ManagedServiceIdentityType]]
        principalId: str
        tenantId: str
        type: Union[str, ManagedServiceIdentityType]
        userAssignedIdentities: dict[str, UserAssignedIdentity]


    class azure.mgmt.recoveryservicesdatareplication.types.PlannedFailoverModel(TypedDict, total=False):
        key "properties": Required[PlannedFailoverModelProperties]
        properties: PlannedFailoverModelProperties


    class azure.mgmt.recoveryservicesdatareplication.types.PlannedFailoverModelProperties(TypedDict, total=False):
        key "customProperties": Required[PlannedFailoverModelCustomProperties]
        customProperties: PlannedFailoverModelCustomProperties


    class azure.mgmt.recoveryservicesdatareplication.types.PolicyModel(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('PolicyModelProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: PolicyModelProperties
        systemData: SystemData
        type: str


    class azure.mgmt.recoveryservicesdatareplication.types.PolicyModelProperties(TypedDict, total=False):
        key "customProperties": Required[PolicyModelCustomProperties]
        key "provisioningState": Union[str, ProvisioningState]
        customProperties: PolicyModelCustomProperties
        provisioningState: Union[str, ProvisioningState]


    class azure.mgmt.recoveryservicesdatareplication.types.PrivateEndpoint(TypedDict, total=False):
        key "id": str
        id: str


    class azure.mgmt.recoveryservicesdatareplication.types.PrivateEndpointConnection(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('PrivateEndpointConnectionResponseProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: PrivateEndpointConnectionResponseProperties
        systemData: SystemData
        type: str


    class azure.mgmt.recoveryservicesdatareplication.types.PrivateEndpointConnectionResponseProperties(TypedDict, total=False):
        key "privateEndpoint": ForwardRef('PrivateEndpoint', module='types')
        key "privateLinkServiceConnectionState": ForwardRef('PrivateLinkServiceConnectionState', module='types')
        key "provisioningState": Union[str, ProvisioningState]
        privateEndpoint: PrivateEndpoint
        privateLinkServiceConnectionState: PrivateLinkServiceConnectionState
        provisioningState: Union[str, ProvisioningState]


    class azure.mgmt.recoveryservicesdatareplication.types.PrivateLinkServiceConnectionState(TypedDict, total=False):
        key "actionsRequired": str
        key "description": str
        key "status": Union[str, PrivateEndpointConnectionStatus]
        actionsRequired: str
        description: str
        status: Union[str, PrivateEndpointConnectionStatus]


    class azure.mgmt.recoveryservicesdatareplication.types.ProtectedItemDynamicMemoryConfig(TypedDict, total=False):
        key "maximumMemoryInMegaBytes": Required[int]
        key "minimumMemoryInMegaBytes": Required[int]
        key "targetMemoryBufferPercentage": Required[int]
        maximumMemoryInMegaBytes: int
        minimumMemoryInMegaBytes: int
        targetMemoryBufferPercentage: int


    class azure.mgmt.recoveryservicesdatareplication.types.ProtectedItemJobProperties(TypedDict, total=False):
        key "displayName": str
        key "endTime": str
        key "id": str
        key "name": str
        key "scenarioName": str
        key "startTime": str
        key "state": str
        displayName: str
        endTime: str
        id: str
        name: str
        scenarioName: str
        startTime: str
        state: str


    class azure.mgmt.recoveryservicesdatareplication.types.ProtectedItemModel(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('ProtectedItemModelProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: ProtectedItemModelProperties
        systemData: SystemData
        type: str


    class azure.mgmt.recoveryservicesdatareplication.types.ProtectedItemModelProperties(TypedDict, total=False):
        key "correlationId": str
        key "currentJob": ForwardRef('ProtectedItemJobProperties', module='types')
        key "customProperties": Required[ProtectedItemModelCustomProperties]
        key "fabricAgentId": str
        key "fabricId": str
        key "fabricObjectId": str
        key "fabricObjectName": str
        key "lastFailedEnableProtectionJob": ForwardRef('ProtectedItemJobProperties', module='types')
        key "lastFailedPlannedFailoverJob": ForwardRef('ProtectedItemJobProperties', module='types')
        key "lastSuccessfulPlannedFailoverTime": str
        key "lastSuccessfulTestFailoverTime": str
        key "lastSuccessfulUnplannedFailoverTime": str
        key "lastTestFailoverJob": ForwardRef('ProtectedItemJobProperties', module='types')
        key "policyName": Required[str]
        key "protectionState": Union[str, ProtectionState]
        key "protectionStateDescription": str
        key "provisioningState": Union[str, ProvisioningState]
        key "replicationExtensionName": Required[str]
        key "replicationHealth": Union[str, HealthStatus]
        key "resyncRequired": bool
        key "resynchronizationState": Union[str, ResynchronizationState]
        key "sourceFabricProviderId": str
        key "targetFabricAgentId": str
        key "targetFabricId": str
        key "targetFabricProviderId": str
        key "testFailoverState": Union[str, TestFailoverState]
        key "testFailoverStateDescription": str
        allowedJobs: list[str]
        correlationId: str
        currentJob: ProtectedItemJobProperties
        customProperties: ProtectedItemModelCustomProperties
        fabricAgentId: str
        fabricId: str
        fabricObjectId: str
        fabricObjectName: str
        healthErrors: list[HealthErrorModel]
        lastFailedEnableProtectionJob: ProtectedItemJobProperties
        lastFailedPlannedFailoverJob: ProtectedItemJobProperties
        lastSuccessfulPlannedFailoverTime: str
        lastSuccessfulTestFailoverTime: str
        lastSuccessfulUnplannedFailoverTime: str
        lastTestFailoverJob: ProtectedItemJobProperties
        policyName: str
        protectionState: Union[str, ProtectionState]
        protectionStateDescription: str
        provisioningState: Union[str, ProvisioningState]
        replicationExtensionName: str
        replicationHealth: Union[str, HealthStatus]
        resyncRequired: bool
        resynchronizationState: Union[str, ResynchronizationState]
        sourceFabricProviderId: str
        targetFabricAgentId: str
        targetFabricId: str
        targetFabricProviderId: str
        testFailoverState: Union[str, TestFailoverState]
        testFailoverStateDescription: str


    class azure.mgmt.recoveryservicesdatareplication.types.ProtectedItemModelPropertiesUpdate(TypedDict, total=False):
        key "customProperties": ForwardRef('ProtectedItemModelCustomPropertiesUpdate', module='types')
        customProperties: ProtectedItemModelCustomPropertiesUpdate


    class azure.mgmt.recoveryservicesdatareplication.types.ProtectedItemModelUpdate(TypedDict, total=False):
        key "id": str
        key "name": str
        key "properties": ForwardRef('ProtectedItemModelPropertiesUpdate', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: ProtectedItemModelPropertiesUpdate
        systemData: SystemData
        type: str


    class azure.mgmt.recoveryservicesdatareplication.types.ProxyResource(Resource):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        systemData: SystemData
        type: str


    class azure.mgmt.recoveryservicesdatareplication.types.ReplicationExtensionModel(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('ReplicationExtensionModelProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: ReplicationExtensionModelProperties
        systemData: SystemData
        type: str


    class azure.mgmt.recoveryservicesdatareplication.types.ReplicationExtensionModelProperties(TypedDict, total=False):
        key "customProperties": Required[ReplicationExtensionModelCustomProperties]
        key "provisioningState": Union[str, ProvisioningState]
        customProperties: ReplicationExtensionModelCustomProperties
        provisioningState: Union[str, ProvisioningState]


    class azure.mgmt.recoveryservicesdatareplication.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        systemData: SystemData
        type: str


    class azure.mgmt.recoveryservicesdatareplication.types.StorageContainerProperties(TypedDict, total=False):
        key "clusterSharedVolumePath": Required[str]
        key "name": Required[str]
        clusterSharedVolumePath: str
        name: str


    class azure.mgmt.recoveryservicesdatareplication.types.SystemData(TypedDict, total=False):
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


    class azure.mgmt.recoveryservicesdatareplication.types.TrackedResource(Resource):
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


    class azure.mgmt.recoveryservicesdatareplication.types.UserAssignedIdentity(TypedDict, total=False):
        key "clientId": str
        key "principalId": str
        clientId: str
        principalId: str


    class azure.mgmt.recoveryservicesdatareplication.types.VMwareFabricAgentModelCustomProperties(TypedDict, total=False):
        key "biosId": Required[str]
        key "instanceType": Required[Literal["VMware"]]
        key "marsAuthenticationIdentity": Required[IdentityModel]
        biosId: str
        instanceType: Literal[VMware]
        marsAuthenticationIdentity: IdentityModel


    class azure.mgmt.recoveryservicesdatareplication.types.VMwareMigrateFabricModelCustomProperties(TypedDict, total=False):
        key "instanceType": Required[Literal["VMwareMigrate"]]
        key "migrationSolutionId": Required[str]
        key "vmwareSiteId": Required[str]
        instanceType: Literal[VMwareMigrate]
        migrationSolutionId: str
        vmwareSiteId: str


    class azure.mgmt.recoveryservicesdatareplication.types.VMwareToAzStackHCIDiskInput(TypedDict, total=False):
        key "diskBlockSize": int
        key "diskController": ForwardRef('DiskControllerInputs', module='types')
        key "diskFileFormat": Required[str]
        key "diskId": Required[str]
        key "diskIdentifier": str
        key "diskLogicalSectorSize": int
        key "diskPhysicalSectorSize": int
        key "diskSizeGB": Required[int]
        key "isDynamic": bool
        key "isOsDisk": Required[bool]
        key "storageContainerId": str
        diskBlockSize: int
        diskController: DiskControllerInputs
        diskFileFormat: str
        diskId: str
        diskIdentifier: str
        diskLogicalSectorSize: int
        diskPhysicalSectorSize: int
        diskSizeGB: int
        isDynamic: bool
        isOsDisk: bool
        storageContainerId: str


    class azure.mgmt.recoveryservicesdatareplication.types.VMwareToAzStackHCINicInput(TypedDict, total=False):
        key "isMacMigrationEnabled": bool
        key "isStaticIpMigrationEnabled": bool
        key "label": Required[str]
        key "networkName": str
        key "nicId": Required[str]
        key "selectionTypeForFailover": Required[Union[str, VMNicSelection]]
        key "targetNetworkId": str
        key "testNetworkId": str
        isMacMigrationEnabled: bool
        isStaticIpMigrationEnabled: bool
        label: str
        networkName: str
        nicId: str
        selectionTypeForFailover: Union[str, VMNicSelection]
        targetNetworkId: str
        testNetworkId: str


    class azure.mgmt.recoveryservicesdatareplication.types.VMwareToAzStackHCIPlannedFailoverModelCustomProperties(TypedDict, total=False):
        key "instanceType": Required[Literal["VMwareToAzStackHCI"]]
        key "shutdownSourceVM": Required[bool]
        instanceType: Literal[VMwareToAzStackHCI]
        shutdownSourceVM: bool


    class azure.mgmt.recoveryservicesdatareplication.types.VMwareToAzStackHCIPolicyModelCustomProperties(TypedDict, total=False):
        key "appConsistentFrequencyInMinutes": Required[int]
        key "crashConsistentFrequencyInMinutes": Required[int]
        key "instanceType": Required[Literal["VMwareToAzStackHCI"]]
        key "recoveryPointHistoryInMinutes": Required[int]
        appConsistentFrequencyInMinutes: int
        crashConsistentFrequencyInMinutes: int
        instanceType: Literal[VMwareToAzStackHCI]
        recoveryPointHistoryInMinutes: int


    class azure.mgmt.recoveryservicesdatareplication.types.VMwareToAzStackHCIProtectedDiskProperties(TypedDict, total=False):
        key "capacityInBytes": int
        key "diskBlockSize": int
        key "diskLogicalSectorSize": int
        key "diskPhysicalSectorSize": int
        key "diskType": str
        key "isDynamic": bool
        key "isOsDisk": bool
        key "migrateDiskName": str
        key "seedDiskName": str
        key "sourceDiskId": str
        key "sourceDiskName": str
        key "storageContainerId": str
        key "storageContainerLocalPath": str
        key "testMigrateDiskName": str
        capacityInBytes: int
        diskBlockSize: int
        diskLogicalSectorSize: int
        diskPhysicalSectorSize: int
        diskType: str
        isDynamic: bool
        isOsDisk: bool
        migrateDiskName: str
        seedDiskName: str
        sourceDiskId: str
        sourceDiskName: str
        storageContainerId: str
        storageContainerLocalPath: str
        testMigrateDiskName: str


    class azure.mgmt.recoveryservicesdatareplication.types.VMwareToAzStackHCIProtectedItemModelCustomProperties(TypedDict, total=False):
        key "activeLocation": Union[str, ProtectedItemActiveLocation]
        key "customLocationRegion": Required[str]
        key "disksToInclude": Required[list[VMwareToAzStackHCIDiskInput]]
        key "dynamicMemoryConfig": ForwardRef('ProtectedItemDynamicMemoryConfig', module='types')
        key "fabricDiscoveryMachineId": Required[str]
        key "failoverRecoveryPointId": str
        key "firmwareType": str
        key "hyperVGeneration": Required[str]
        key "initialReplicationProgressPercentage": int
        key "instanceType": Required[Literal["VMwareToAzStackHCI"]]
        key "isDynamicRam": bool
        key "lastRecoveryPointId": str
        key "lastRecoveryPointReceived": str
        key "lastReplicationUpdateTime": str
        key "migrationProgressPercentage": int
        key "nicsToInclude": Required[list[VMwareToAzStackHCINicInput]]
        key "osName": str
        key "osType": str
        key "performAutoResync": bool
        key "resumeProgressPercentage": int
        key "resumeRetryCount": int
        key "resyncProgressPercentage": int
        key "resyncRequired": bool
        key "resyncRetryCount": int
        key "resyncState": Union[str, VMwareToAzureMigrateResyncState]
        key "runAsAccountId": Required[str]
        key "sourceApplianceName": str
        key "sourceCpuCores": int
        key "sourceFabricAgentName": Required[str]
        key "sourceMemoryInMegaBytes": float
        key "sourceVmName": str
        key "storageContainerId": Required[str]
        key "targetApplianceName": str
        key "targetArcClusterCustomLocationId": Required[str]
        key "targetAzStackHciClusterName": str
        key "targetCpuCores": int
        key "targetFabricAgentName": Required[str]
        key "targetHciClusterId": Required[str]
        key "targetLocation": str
        key "targetMemoryInMegaBytes": int
        key "targetNetworkId": str
        key "targetResourceGroupId": Required[str]
        key "targetVmBiosId": str
        key "targetVmName": str
        key "testNetworkId": str
        activeLocation: Union[str, ProtectedItemActiveLocation]
        customLocationRegion: str
        disksToInclude: list[VMwareToAzStackHCIDiskInput]
        dynamicMemoryConfig: ProtectedItemDynamicMemoryConfig
        fabricDiscoveryMachineId: str
        failoverRecoveryPointId: str
        firmwareType: str
        hyperVGeneration: str
        initialReplicationProgressPercentage: int
        instanceType: Literal[VMwareToAzStackHCI]
        isDynamicRam: bool
        lastRecoveryPointId: str
        lastRecoveryPointReceived: str
        lastReplicationUpdateTime: str
        migrationProgressPercentage: int
        nicsToInclude: list[VMwareToAzStackHCINicInput]
        osName: str
        osType: str
        performAutoResync: bool
        protectedDisks: list[VMwareToAzStackHCIProtectedDiskProperties]
        protectedNics: list[VMwareToAzStackHCIProtectedNicProperties]
        resumeProgressPercentage: int
        resumeRetryCount: int
        resyncProgressPercentage: int
        resyncRequired: bool
        resyncRetryCount: int
        resyncState: Union[str, VMwareToAzureMigrateResyncState]
        runAsAccountId: str
        sourceApplianceName: str
        sourceCpuCores: int
        sourceFabricAgentName: str
        sourceMemoryInMegaBytes: float
        sourceVmName: str
        storageContainerId: str
        targetApplianceName: str
        targetArcClusterCustomLocationId: str
        targetAzStackHciClusterName: str
        targetCpuCores: int
        targetFabricAgentName: str
        targetHciClusterId: str
        targetLocation: str
        targetMemoryInMegaBytes: int
        targetNetworkId: str
        targetResourceGroupId: str
        targetVmBiosId: str
        targetVmName: str
        testNetworkId: str


    class azure.mgmt.recoveryservicesdatareplication.types.VMwareToAzStackHCIProtectedItemModelCustomPropertiesUpdate(TypedDict, total=False):
        key "dynamicMemoryConfig": ForwardRef('ProtectedItemDynamicMemoryConfig', module='types')
        key "instanceType": Required[Literal["VMwareToAzStackHCI"]]
        key "isDynamicRam": bool
        key "osType": str
        key "targetCpuCores": int
        key "targetMemoryInMegaBytes": int
        dynamicMemoryConfig: ProtectedItemDynamicMemoryConfig
        instanceType: Literal[VMwareToAzStackHCI]
        isDynamicRam: bool
        nicsToInclude: list[VMwareToAzStackHCINicInput]
        osType: str
        targetCpuCores: int
        targetMemoryInMegaBytes: int


    class azure.mgmt.recoveryservicesdatareplication.types.VMwareToAzStackHCIProtectedNicProperties(TypedDict, total=False):
        key "isPrimaryNic": bool
        key "label": str
        key "macAddress": str
        key "networkName": str
        key "nicId": str
        key "selectionTypeForFailover": Union[str, VMNicSelection]
        key "targetNetworkId": str
        key "testNetworkId": str
        isPrimaryNic: bool
        label: str
        macAddress: str
        networkName: str
        nicId: str
        selectionTypeForFailover: Union[str, VMNicSelection]
        targetNetworkId: str
        testNetworkId: str


    class azure.mgmt.recoveryservicesdatareplication.types.VMwareToAzStackHCIReplicationExtensionModelCustomProperties(TypedDict, total=False):
        key "asrServiceUri": str
        key "azStackHciFabricArmId": Required[str]
        key "azStackHciSiteId": str
        key "gatewayServiceUri": str
        key "instanceType": Required[Literal["VMwareToAzStackHCI"]]
        key "rcmServiceUri": str
        key "resourceGroup": str
        key "resourceLocation": str
        key "sourceGatewayServiceId": str
        key "sourceStorageContainerName": str
        key "storageAccountId": str
        key "storageAccountSasSecretName": str
        key "subscriptionId": str
        key "targetGatewayServiceId": str
        key "targetStorageContainerName": str
        key "vmwareFabricArmId": Required[str]
        key "vmwareSiteId": str
        asrServiceUri: str
        azStackHciFabricArmId: str
        azStackHciSiteId: str
        gatewayServiceUri: str
        instanceType: Literal[VMwareToAzStackHCI]
        rcmServiceUri: str
        resourceGroup: str
        resourceLocation: str
        sourceGatewayServiceId: str
        sourceStorageContainerName: str
        storageAccountId: str
        storageAccountSasSecretName: str
        subscriptionId: str
        targetGatewayServiceId: str
        targetStorageContainerName: str
        vmwareFabricArmId: str
        vmwareSiteId: str


    class azure.mgmt.recoveryservicesdatareplication.types.VaultIdentityModel(TypedDict, total=False):
        key "principalId": str
        key "tenantId": str
        key "type": Required[Union[str, VaultIdentityType]]
        principalId: str
        tenantId: str
        type: Union[str, VaultIdentityType]


    class azure.mgmt.recoveryservicesdatareplication.types.VaultModel(TrackedResource):
        key "id": str
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('VaultModelProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        identity: ManagedServiceIdentity
        location: str
        name: str
        properties: VaultModelProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.recoveryservicesdatareplication.types.VaultModelProperties(TypedDict, total=False):
        key "provisioningState": Union[str, ProvisioningState]
        key "serviceResourceId": str
        key "vaultType": Union[str, ReplicationVaultType]
        provisioningState: Union[str, ProvisioningState]
        serviceResourceId: str
        vaultType: Union[str, ReplicationVaultType]


    class azure.mgmt.recoveryservicesdatareplication.types.VaultModelUpdate(TypedDict, total=False):
        key "id": str
        key "identity": ForwardRef('VaultIdentityModel', module='types')
        key "name": str
        key "properties": ForwardRef('VaultModelProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        identity: VaultIdentityModel
        name: str
        properties: VaultModelProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


```