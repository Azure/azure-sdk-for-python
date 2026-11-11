```py
namespace azure.mgmt.servicefabricmanagedclusters

    class azure.mgmt.servicefabricmanagedclusters.ServiceFabricManagedClustersManagementClient: implements ContextManager 
        application_type_versions: ApplicationTypeVersionsOperations
        application_types: ApplicationTypesOperations
        applications: ApplicationsOperations
        managed_apply_maintenance_window: ManagedApplyMaintenanceWindowOperations
        managed_az_resiliency_status: ManagedAzResiliencyStatusOperations
        managed_cluster_version: ManagedClusterVersionOperations
        managed_clusters: ManagedClustersOperations
        managed_maintenance_window_status: ManagedMaintenanceWindowStatusOperations
        managed_unsupported_vm_sizes: ManagedUnsupportedVMSizesOperations
        node_type_skus: NodeTypeSkusOperations
        node_types: NodeTypesOperations
        operation_results: OperationResultsOperations
        operation_status: OperationStatusOperations
        operations: Operations
        services: ServicesOperations

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


namespace azure.mgmt.servicefabricmanagedclusters.aio

    class azure.mgmt.servicefabricmanagedclusters.aio.ServiceFabricManagedClustersManagementClient: implements AsyncContextManager 
        application_type_versions: ApplicationTypeVersionsOperations
        application_types: ApplicationTypesOperations
        applications: ApplicationsOperations
        managed_apply_maintenance_window: ManagedApplyMaintenanceWindowOperations
        managed_az_resiliency_status: ManagedAzResiliencyStatusOperations
        managed_cluster_version: ManagedClusterVersionOperations
        managed_clusters: ManagedClustersOperations
        managed_maintenance_window_status: ManagedMaintenanceWindowStatusOperations
        managed_unsupported_vm_sizes: ManagedUnsupportedVMSizesOperations
        node_type_skus: NodeTypeSkusOperations
        node_types: NodeTypesOperations
        operation_results: OperationResultsOperations
        operation_status: OperationStatusOperations
        operations: Operations
        services: ServicesOperations

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


namespace azure.mgmt.servicefabricmanagedclusters.aio.operations

    class azure.mgmt.servicefabricmanagedclusters.aio.operations.ApplicationTypeVersionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_type_name: str, 
                version: str, 
                parameters: ApplicationTypeVersionResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ApplicationTypeVersionResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_type_name: str, 
                version: str, 
                parameters: ApplicationTypeVersionResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ApplicationTypeVersionResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_type_name: str, 
                version: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ApplicationTypeVersionResource]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_type_name: str, 
                version: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_type_name: str, 
                version: str, 
                **kwargs: Any
            ) -> ApplicationTypeVersionResource: ...

        @distributed_trace
        def list_by_application_types(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_type_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ApplicationTypeVersionResource]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_type_name: str, 
                version: str, 
                parameters: ApplicationTypeVersionUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplicationTypeVersionResource: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_type_name: str, 
                version: str, 
                parameters: ApplicationTypeVersionUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplicationTypeVersionResource: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_type_name: str, 
                version: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplicationTypeVersionResource: ...


    class azure.mgmt.servicefabricmanagedclusters.aio.operations.ApplicationTypesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_type_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_type_name: str, 
                parameters: ApplicationTypeResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplicationTypeResource: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_type_name: str, 
                parameters: ApplicationTypeResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplicationTypeResource: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_type_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplicationTypeResource: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_type_name: str, 
                **kwargs: Any
            ) -> ApplicationTypeResource: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ApplicationTypeResource]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_type_name: str, 
                parameters: ApplicationTypeUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplicationTypeResource: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_type_name: str, 
                parameters: ApplicationTypeUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplicationTypeResource: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_type_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplicationTypeResource: ...


    class azure.mgmt.servicefabricmanagedclusters.aio.operations.ApplicationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_name: str, 
                parameters: ApplicationResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ApplicationResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_name: str, 
                parameters: ApplicationResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ApplicationResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ApplicationResource]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_fetch_health(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_name: str, 
                parameters: ApplicationFetchHealthRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_fetch_health(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_name: str, 
                parameters: ApplicationFetchHealthRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_fetch_health(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_read_upgrade(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_restart_deployed_code_package(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_name: str, 
                parameters: RestartDeployedCodePackageRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_restart_deployed_code_package(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_name: str, 
                parameters: RestartDeployedCodePackageRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_restart_deployed_code_package(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_resume_upgrade(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_name: str, 
                parameters: RuntimeResumeApplicationUpgradeParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_resume_upgrade(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_name: str, 
                parameters: RuntimeResumeApplicationUpgradeParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_resume_upgrade(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_start_rollback(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_name: str, 
                parameters: ApplicationUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ApplicationResource]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_name: str, 
                parameters: ApplicationUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ApplicationResource]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ApplicationResource]: ...

        @overload
        async def begin_update_upgrade(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_name: str, 
                parameters: RuntimeUpdateApplicationUpgradeParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update_upgrade(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_name: str, 
                parameters: RuntimeUpdateApplicationUpgradeParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update_upgrade(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_name: str, 
                **kwargs: Any
            ) -> ApplicationResource: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ApplicationResource]: ...


    class azure.mgmt.servicefabricmanagedclusters.aio.operations.ManagedApplyMaintenanceWindowOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def post(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                body: Optional[ApplyMaintenanceWindowRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def post(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                body: Optional[ApplyMaintenanceWindowRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def post(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.servicefabricmanagedclusters.aio.operations.ManagedAzResiliencyStatusOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> ManagedAzResiliencyStatus: ...


    class azure.mgmt.servicefabricmanagedclusters.aio.operations.ManagedClusterVersionOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                location: str, 
                cluster_version: str, 
                **kwargs: Any
            ) -> ManagedClusterCodeVersionResult: ...

        @distributed_trace_async
        async def get_by_environment(
                self, 
                location: str, 
                environment: Union[str, ManagedClusterVersionEnvironment], 
                cluster_version: str, 
                **kwargs: Any
            ) -> ManagedClusterCodeVersionResult: ...

        @distributed_trace_async
        async def list(
                self, 
                location: str, 
                **kwargs: Any
            ) -> List[ManagedClusterCodeVersionResult]: ...

        @distributed_trace_async
        async def list_by_environment(
                self, 
                location: str, 
                environment: Union[str, ManagedClusterVersionEnvironment], 
                **kwargs: Any
            ) -> List[ManagedClusterCodeVersionResult]: ...


    class azure.mgmt.servicefabricmanagedclusters.aio.operations.ManagedClustersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                parameters: ManagedCluster, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ManagedCluster]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                parameters: ManagedCluster, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ManagedCluster]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ManagedCluster]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_start_fault_simulation(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                parameters: FaultSimulationContentWrapper, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[FaultSimulation]: ...

        @overload
        async def begin_start_fault_simulation(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                parameters: FaultSimulationContentWrapper, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[FaultSimulation]: ...

        @overload
        async def begin_start_fault_simulation(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[FaultSimulation]: ...

        @overload
        async def begin_stop_fault_simulation(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                parameters: FaultSimulationIdContent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[FaultSimulation]: ...

        @overload
        async def begin_stop_fault_simulation(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                parameters: FaultSimulationIdContent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[FaultSimulation]: ...

        @overload
        async def begin_stop_fault_simulation(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[FaultSimulation]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                parameters: ManagedClusterUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ManagedCluster]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                parameters: ManagedClusterUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ManagedCluster]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ManagedCluster]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> ManagedCluster: ...

        @overload
        async def get_fault_simulation(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                parameters: FaultSimulationIdContent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FaultSimulation: ...

        @overload
        async def get_fault_simulation(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                parameters: FaultSimulationIdContent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FaultSimulation: ...

        @overload
        async def get_fault_simulation(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FaultSimulation: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ManagedCluster]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[ManagedCluster]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'cluster_name', 'accept']}, api_versions_list=['2026-05-01-preview'])
        def list_fault_simulation(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[FaultSimulation]: ...


    class azure.mgmt.servicefabricmanagedclusters.aio.operations.ManagedMaintenanceWindowStatusOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> ManagedMaintenanceWindowStatus: ...


    class azure.mgmt.servicefabricmanagedclusters.aio.operations.ManagedUnsupportedVMSizesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                location: str, 
                vm_size: str, 
                **kwargs: Any
            ) -> ManagedVMSize: ...

        @distributed_trace
        def list(
                self, 
                location: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ManagedVMSize]: ...


    class azure.mgmt.servicefabricmanagedclusters.aio.operations.NodeTypeSkusOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                node_type_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[NodeTypeAvailableSku]: ...


    class azure.mgmt.servicefabricmanagedclusters.aio.operations.NodeTypesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                node_type_name: str, 
                parameters: NodeType, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NodeType]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                node_type_name: str, 
                parameters: NodeType, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NodeType]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                node_type_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NodeType]: ...

        @overload
        async def begin_deallocate(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                node_type_name: str, 
                parameters: NodeTypeActionParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_deallocate(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                node_type_name: str, 
                parameters: NodeTypeActionParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_deallocate(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                node_type_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                node_type_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_delete_node(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                node_type_name: str, 
                parameters: NodeTypeActionParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_delete_node(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                node_type_name: str, 
                parameters: NodeTypeActionParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_delete_node(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                node_type_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_redeploy(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                node_type_name: str, 
                parameters: NodeTypeActionParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_redeploy(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                node_type_name: str, 
                parameters: NodeTypeActionParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_redeploy(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                node_type_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_reimage(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                node_type_name: str, 
                parameters: NodeTypeActionParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_reimage(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                node_type_name: str, 
                parameters: NodeTypeActionParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_reimage(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                node_type_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_restart(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                node_type_name: str, 
                parameters: NodeTypeActionParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_restart(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                node_type_name: str, 
                parameters: NodeTypeActionParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_restart(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                node_type_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_start(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                node_type_name: str, 
                parameters: NodeTypeActionParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_start(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                node_type_name: str, 
                parameters: NodeTypeActionParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_start(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                node_type_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_start_fault_simulation(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                node_type_name: str, 
                parameters: FaultSimulationContentWrapper, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[FaultSimulation]: ...

        @overload
        async def begin_start_fault_simulation(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                node_type_name: str, 
                parameters: FaultSimulationContentWrapper, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[FaultSimulation]: ...

        @overload
        async def begin_start_fault_simulation(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                node_type_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[FaultSimulation]: ...

        @overload
        async def begin_stop_fault_simulation(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                node_type_name: str, 
                parameters: FaultSimulationIdContent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[FaultSimulation]: ...

        @overload
        async def begin_stop_fault_simulation(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                node_type_name: str, 
                parameters: FaultSimulationIdContent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[FaultSimulation]: ...

        @overload
        async def begin_stop_fault_simulation(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                node_type_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[FaultSimulation]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                node_type_name: str, 
                parameters: NodeTypeUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NodeType]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                node_type_name: str, 
                parameters: NodeTypeUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NodeType]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                node_type_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NodeType]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                node_type_name: str, 
                **kwargs: Any
            ) -> NodeType: ...

        @overload
        async def get_fault_simulation(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                node_type_name: str, 
                parameters: FaultSimulationIdContent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FaultSimulation: ...

        @overload
        async def get_fault_simulation(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                node_type_name: str, 
                parameters: FaultSimulationIdContent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FaultSimulation: ...

        @overload
        async def get_fault_simulation(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                node_type_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FaultSimulation: ...

        @distributed_trace
        def list_by_managed_clusters(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[NodeType]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'cluster_name', 'node_type_name', 'accept']}, api_versions_list=['2026-05-01-preview'])
        def list_fault_simulation(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                node_type_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[FaultSimulation]: ...


    class azure.mgmt.servicefabricmanagedclusters.aio.operations.OperationResultsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                location: str, 
                operation_id: str, 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.servicefabricmanagedclusters.aio.operations.OperationStatusOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                location: str, 
                operation_id: str, 
                **kwargs: Any
            ) -> LongRunningOperationResult: ...


    class azure.mgmt.servicefabricmanagedclusters.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[OperationResult]: ...


    class azure.mgmt.servicefabricmanagedclusters.aio.operations.ServicesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_name: str, 
                service_name: str, 
                parameters: ServiceResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ServiceResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_name: str, 
                service_name: str, 
                parameters: ServiceResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ServiceResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_name: str, 
                service_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ServiceResource]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_name: str, 
                service_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_restart_replica(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_name: str, 
                service_name: str, 
                parameters: RestartReplicaRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_restart_replica(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_name: str, 
                service_name: str, 
                parameters: RestartReplicaRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_restart_replica(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_name: str, 
                service_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_name: str, 
                service_name: str, 
                **kwargs: Any
            ) -> ServiceResource: ...

        @distributed_trace
        def list_by_applications(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ServiceResource]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_name: str, 
                service_name: str, 
                parameters: ServiceUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ServiceResource: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_name: str, 
                service_name: str, 
                parameters: ServiceUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ServiceResource: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_name: str, 
                service_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ServiceResource: ...


namespace azure.mgmt.servicefabricmanagedclusters.models

    class azure.mgmt.servicefabricmanagedclusters.models.Access(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALLOW = "allow"
        DENY = "deny"


    class azure.mgmt.servicefabricmanagedclusters.models.AddRemoveIncrementalNamedPartitionScalingMechanism(ScalingMechanism, discriminator='AddRemoveIncrementalNamedPartition'):
        kind: Literal[ServiceScalingMechanismKind.ADD_REMOVE_INCREMENTAL_NAMED_PARTITION]
        max_partition_count: int
        min_partition_count: int
        scale_increment: int

        @overload
        def __init__(
                self, 
                *, 
                max_partition_count: int, 
                min_partition_count: int, 
                scale_increment: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicefabricmanagedclusters.models.AdditionalNetworkInterfaceConfiguration(_Model):
        dscp_configuration: Optional[SubResource]
        enable_accelerated_networking: Optional[bool]
        ip_configurations: list[IpConfiguration]
        name: str

        @overload
        def __init__(
                self, 
                *, 
                dscp_configuration: Optional[SubResource] = ..., 
                enable_accelerated_networking: Optional[bool] = ..., 
                ip_configurations: list[IpConfiguration], 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicefabricmanagedclusters.models.ApplicationFetchHealthRequest(_Model):
        deployed_applications_health_state_filter: Optional[Union[str, HealthFilter]]
        events_health_state_filter: Optional[Union[str, HealthFilter]]
        exclude_health_statistics: Optional[bool]
        services_health_state_filter: Optional[Union[str, HealthFilter]]
        timeout: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                deployed_applications_health_state_filter: Optional[Union[str, HealthFilter]] = ..., 
                events_health_state_filter: Optional[Union[str, HealthFilter]] = ..., 
                exclude_health_statistics: Optional[bool] = ..., 
                services_health_state_filter: Optional[Union[str, HealthFilter]] = ..., 
                timeout: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicefabricmanagedclusters.models.ApplicationHealthPolicy(_Model):
        consider_warning_as_error: bool
        default_service_type_health_policy: Optional[ServiceTypeHealthPolicy]
        max_percent_unhealthy_deployed_applications: int
        service_type_health_policy_map: Optional[dict[str, ServiceTypeHealthPolicy]]

        @overload
        def __init__(
                self, 
                *, 
                consider_warning_as_error: bool, 
                default_service_type_health_policy: Optional[ServiceTypeHealthPolicy] = ..., 
                max_percent_unhealthy_deployed_applications: int, 
                service_type_health_policy_map: Optional[dict[str, ServiceTypeHealthPolicy]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicefabricmanagedclusters.models.ApplicationResource(ProxyResource):
        id: str
        identity: Optional[ManagedIdentity]
        location: Optional[str]
        name: str
        properties: Optional[ApplicationResourceProperties]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedIdentity] = ..., 
                location: Optional[str] = ..., 
                properties: Optional[ApplicationResourceProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.servicefabricmanagedclusters.models.ApplicationResourceProperties(_Model):
        managed_identities: Optional[list[ApplicationUserAssignedIdentity]]
        parameters: Optional[dict[str, str]]
        provisioning_state: Optional[str]
        upgrade_policy: Optional[ApplicationUpgradePolicy]
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                managed_identities: Optional[list[ApplicationUserAssignedIdentity]] = ..., 
                parameters: Optional[dict[str, str]] = ..., 
                upgrade_policy: Optional[ApplicationUpgradePolicy] = ..., 
                version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicefabricmanagedclusters.models.ApplicationTypeResource(ProxyResource):
        id: str
        location: Optional[str]
        name: str
        properties: Optional[ApplicationTypeResourceProperties]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                properties: Optional[ApplicationTypeResourceProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.servicefabricmanagedclusters.models.ApplicationTypeResourceProperties(_Model):
        provisioning_state: Optional[str]


    class azure.mgmt.servicefabricmanagedclusters.models.ApplicationTypeUpdateParameters(_Model):
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicefabricmanagedclusters.models.ApplicationTypeVersionResource(ProxyResource):
        id: str
        location: Optional[str]
        name: str
        properties: Optional[ApplicationTypeVersionResourceProperties]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                properties: Optional[ApplicationTypeVersionResourceProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.servicefabricmanagedclusters.models.ApplicationTypeVersionResourceProperties(_Model):
        app_package_url: str
        provisioning_state: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                app_package_url: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicefabricmanagedclusters.models.ApplicationTypeVersionUpdateParameters(_Model):
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicefabricmanagedclusters.models.ApplicationTypeVersionsCleanupPolicy(_Model):
        max_unused_versions_to_keep: int

        @overload
        def __init__(
                self, 
                *, 
                max_unused_versions_to_keep: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicefabricmanagedclusters.models.ApplicationUpdateParameters(_Model):
        properties: Optional[ApplicationUpdateParametersProperties]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ApplicationUpdateParametersProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicefabricmanagedclusters.models.ApplicationUpdateParametersProperties(_Model):
        parameters: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                parameters: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicefabricmanagedclusters.models.ApplicationUpgradePolicy(_Model):
        application_health_policy: Optional[ApplicationHealthPolicy]
        force_restart: Optional[bool]
        instance_close_delay_duration: Optional[int]
        recreate_application: Optional[bool]
        rolling_upgrade_monitoring_policy: Optional[RollingUpgradeMonitoringPolicy]
        upgrade_mode: Optional[Union[str, RollingUpgradeMode]]
        upgrade_replica_set_check_timeout: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                application_health_policy: Optional[ApplicationHealthPolicy] = ..., 
                force_restart: Optional[bool] = ..., 
                instance_close_delay_duration: Optional[int] = ..., 
                recreate_application: Optional[bool] = ..., 
                rolling_upgrade_monitoring_policy: Optional[RollingUpgradeMonitoringPolicy] = ..., 
                upgrade_mode: Optional[Union[str, RollingUpgradeMode]] = ..., 
                upgrade_replica_set_check_timeout: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicefabricmanagedclusters.models.ApplicationUserAssignedIdentity(_Model):
        name: str
        principal_id: str

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                principal_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicefabricmanagedclusters.models.ApplyMaintenanceWindowRequest(_Model):
        duration: Optional[str]
        start_date_time: Optional[str]
        time_zone: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                duration: Optional[str] = ..., 
                start_date_time: Optional[str] = ..., 
                time_zone: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicefabricmanagedclusters.models.AutoGeneratedDomainNameLabelScope(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NO_REUSE = "NoReuse"
        RESOURCE_GROUP_REUSE = "ResourceGroupReuse"
        SUBSCRIPTION_REUSE = "SubscriptionReuse"
        TENANT_REUSE = "TenantReuse"


    class azure.mgmt.servicefabricmanagedclusters.models.AvailableOperationDisplay(_Model):
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


    class azure.mgmt.servicefabricmanagedclusters.models.AveragePartitionLoadScalingTrigger(ScalingTrigger, discriminator='AveragePartitionLoadTrigger'):
        kind: Literal[ServiceScalingTriggerKind.AVERAGE_PARTITION_LOAD_TRIGGER]
        lower_load_threshold: float
        metric_name: str
        scale_interval: str
        upper_load_threshold: float

        @overload
        def __init__(
                self, 
                *, 
                lower_load_threshold: float, 
                metric_name: str, 
                scale_interval: str, 
                upper_load_threshold: float
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicefabricmanagedclusters.models.AverageServiceLoadScalingTrigger(ScalingTrigger, discriminator='AverageServiceLoadTrigger'):
        kind: Literal[ServiceScalingTriggerKind.AVERAGE_SERVICE_LOAD_TRIGGER]
        lower_load_threshold: float
        metric_name: str
        scale_interval: str
        upper_load_threshold: float
        use_only_primary_load: bool

        @overload
        def __init__(
                self, 
                *, 
                lower_load_threshold: float, 
                metric_name: str, 
                scale_interval: str, 
                upper_load_threshold: float, 
                use_only_primary_load: bool
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicefabricmanagedclusters.models.AzureActiveDirectory(_Model):
        client_application: Optional[str]
        cluster_application: Optional[str]
        tenant_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                client_application: Optional[str] = ..., 
                cluster_application: Optional[str] = ..., 
                tenant_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicefabricmanagedclusters.models.ClientCertificate(_Model):
        common_name: Optional[str]
        is_admin: bool
        issuer_thumbprint: Optional[str]
        thumbprint: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                common_name: Optional[str] = ..., 
                is_admin: bool, 
                issuer_thumbprint: Optional[str] = ..., 
                thumbprint: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicefabricmanagedclusters.models.ClusterHealthPolicy(_Model):
        max_percent_unhealthy_applications: int
        max_percent_unhealthy_nodes: int

        @overload
        def __init__(
                self, 
                *, 
                max_percent_unhealthy_applications: int, 
                max_percent_unhealthy_nodes: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicefabricmanagedclusters.models.ClusterMonitoringPolicy(_Model):
        health_check_retry_timeout: str
        health_check_stable_duration: str
        health_check_wait_duration: str
        upgrade_domain_timeout: str
        upgrade_timeout: str

        @overload
        def __init__(
                self, 
                *, 
                health_check_retry_timeout: str, 
                health_check_stable_duration: str, 
                health_check_wait_duration: str, 
                upgrade_domain_timeout: str, 
                upgrade_timeout: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicefabricmanagedclusters.models.ClusterState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BASELINE_UPGRADE = "BaselineUpgrade"
        DEPLOYING = "Deploying"
        READY = "Ready"
        UPGRADE_FAILED = "UpgradeFailed"
        UPGRADING = "Upgrading"
        WAITING_FOR_NODES = "WaitingForNodes"


    class azure.mgmt.servicefabricmanagedclusters.models.ClusterUpgradeCadence(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        WAVE0 = "Wave0"
        WAVE1 = "Wave1"
        WAVE2 = "Wave2"


    class azure.mgmt.servicefabricmanagedclusters.models.ClusterUpgradeDeltaHealthPolicy(_Model):
        max_percent_delta_unhealthy_applications: Optional[int]
        max_percent_delta_unhealthy_nodes: int
        max_percent_upgrade_domain_delta_unhealthy_nodes: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                max_percent_delta_unhealthy_applications: Optional[int] = ..., 
                max_percent_delta_unhealthy_nodes: int, 
                max_percent_upgrade_domain_delta_unhealthy_nodes: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicefabricmanagedclusters.models.ClusterUpgradeMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTOMATIC = "Automatic"
        MANUAL = "Manual"


    class azure.mgmt.servicefabricmanagedclusters.models.ClusterUpgradePolicy(_Model):
        delta_health_policy: Optional[ClusterUpgradeDeltaHealthPolicy]
        force_restart: Optional[bool]
        health_policy: Optional[ClusterHealthPolicy]
        monitoring_policy: Optional[ClusterMonitoringPolicy]
        upgrade_replica_set_check_timeout: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                delta_health_policy: Optional[ClusterUpgradeDeltaHealthPolicy] = ..., 
                force_restart: Optional[bool] = ..., 
                health_policy: Optional[ClusterHealthPolicy] = ..., 
                monitoring_policy: Optional[ClusterMonitoringPolicy] = ..., 
                upgrade_replica_set_check_timeout: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicefabricmanagedclusters.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.servicefabricmanagedclusters.models.Direction(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INBOUND = "inbound"
        OUTBOUND = "outbound"


    class azure.mgmt.servicefabricmanagedclusters.models.DiskType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PREMIUM_LRS = "Premium_LRS"
        PREMIUM_V2_LRS = "PremiumV2_LRS"
        PREMIUM_ZRS = "Premium_ZRS"
        STANDARD_LRS = "Standard_LRS"
        STANDARD_SSD_LRS = "StandardSSD_LRS"
        STANDARD_SSD_ZRS = "StandardSSD_ZRS"


    class azure.mgmt.servicefabricmanagedclusters.models.EndpointRangeDescription(_Model):
        end_port: int
        start_port: int

        @overload
        def __init__(
                self, 
                *, 
                end_port: int, 
                start_port: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicefabricmanagedclusters.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.servicefabricmanagedclusters.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.servicefabricmanagedclusters.models.ErrorModelError(_Model):
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


    class azure.mgmt.servicefabricmanagedclusters.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicefabricmanagedclusters.models.EvictionPolicyType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEALLOCATE = "Deallocate"
        DELETE = "Delete"


    class azure.mgmt.servicefabricmanagedclusters.models.FailureAction(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MANUAL = "Manual"
        ROLLBACK = "Rollback"


    class azure.mgmt.servicefabricmanagedclusters.models.FaultKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ZONE = "Zone"


    class azure.mgmt.servicefabricmanagedclusters.models.FaultSimulation(_Model):
        details: Optional[FaultSimulationDetails]
        end_time: Optional[datetime]
        simulation_id: Optional[str]
        start_time: Optional[datetime]
        status: Optional[Union[str, FaultSimulationStatus]]

        @overload
        def __init__(
                self, 
                *, 
                details: Optional[FaultSimulationDetails] = ..., 
                end_time: Optional[datetime] = ..., 
                simulation_id: Optional[str] = ..., 
                start_time: Optional[datetime] = ..., 
                status: Optional[Union[str, FaultSimulationStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicefabricmanagedclusters.models.FaultSimulationConstraints(_Model):
        expiration_time: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                expiration_time: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicefabricmanagedclusters.models.FaultSimulationContent(_Model):
        constraints: Optional[FaultSimulationConstraints]
        fault_kind: str
        force: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                constraints: Optional[FaultSimulationConstraints] = ..., 
                fault_kind: str, 
                force: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicefabricmanagedclusters.models.FaultSimulationContentWrapper(_Model):
        parameters: FaultSimulationContent

        @overload
        def __init__(
                self, 
                *, 
                parameters: FaultSimulationContent
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicefabricmanagedclusters.models.FaultSimulationDetails(_Model):
        cluster_id: Optional[str]
        node_type_fault_simulation: Optional[list[NodeTypeFaultSimulation]]
        operation_id: Optional[str]
        parameters: Optional[FaultSimulationContent]

        @overload
        def __init__(
                self, 
                *, 
                cluster_id: Optional[str] = ..., 
                node_type_fault_simulation: Optional[list[NodeTypeFaultSimulation]] = ..., 
                operation_id: Optional[str] = ..., 
                parameters: Optional[FaultSimulationContent] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicefabricmanagedclusters.models.FaultSimulationIdContent(_Model):
        simulation_id: str

        @overload
        def __init__(
                self, 
                *, 
                simulation_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicefabricmanagedclusters.models.FaultSimulationStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        DONE = "Done"
        STARTING = "Starting"
        START_FAILED = "StartFailed"
        STOPPING = "Stopping"
        STOP_FAILED = "StopFailed"


    class azure.mgmt.servicefabricmanagedclusters.models.FrontendConfiguration(_Model):
        application_gateway_backend_address_pool_id: Optional[str]
        ip_address_type: Optional[Union[str, IPAddressType]]
        load_balancer_backend_address_pool_id: Optional[str]
        load_balancer_inbound_nat_pool_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                application_gateway_backend_address_pool_id: Optional[str] = ..., 
                ip_address_type: Optional[Union[str, IPAddressType]] = ..., 
                load_balancer_backend_address_pool_id: Optional[str] = ..., 
                load_balancer_inbound_nat_pool_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicefabricmanagedclusters.models.HealthFilter(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALL = "All"
        DEFAULT = "Default"
        ERROR = "Error"
        NONE = "None"
        OK = "Ok"
        WARNING = "Warning"


    class azure.mgmt.servicefabricmanagedclusters.models.HostEndpointSettings(_Model):
        in_vm_access_control_profile_reference_id: Optional[str]
        mode: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                in_vm_access_control_profile_reference_id: Optional[str] = ..., 
                mode: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicefabricmanagedclusters.models.IPAddressType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        I_PV4 = "IPv4"
        I_PV6 = "IPv6"


    class azure.mgmt.servicefabricmanagedclusters.models.IpConfiguration(_Model):
        application_gateway_backend_address_pools: Optional[list[SubResource]]
        load_balancer_backend_address_pools: Optional[list[SubResource]]
        load_balancer_inbound_nat_pools: Optional[list[SubResource]]
        name: str
        private_ip_address_version: Optional[Union[str, PrivateIPAddressVersion]]
        public_ip_address_configuration: Optional[IpConfigurationPublicIPAddressConfiguration]
        subnet: Optional[SubResource]

        @overload
        def __init__(
                self, 
                *, 
                application_gateway_backend_address_pools: Optional[list[SubResource]] = ..., 
                load_balancer_backend_address_pools: Optional[list[SubResource]] = ..., 
                load_balancer_inbound_nat_pools: Optional[list[SubResource]] = ..., 
                name: str, 
                private_ip_address_version: Optional[Union[str, PrivateIPAddressVersion]] = ..., 
                public_ip_address_configuration: Optional[IpConfigurationPublicIPAddressConfiguration] = ..., 
                subnet: Optional[SubResource] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicefabricmanagedclusters.models.IpConfigurationPublicIPAddressConfiguration(_Model):
        ip_tags: Optional[list[IpTag]]
        name: str
        public_ip_address_version: Optional[Union[str, PublicIPAddressVersion]]

        @overload
        def __init__(
                self, 
                *, 
                ip_tags: Optional[list[IpTag]] = ..., 
                name: str, 
                public_ip_address_version: Optional[Union[str, PublicIPAddressVersion]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicefabricmanagedclusters.models.IpTag(_Model):
        ip_tag_type: str
        tag: str

        @overload
        def __init__(
                self, 
                *, 
                ip_tag_type: str, 
                tag: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicefabricmanagedclusters.models.LoadBalancingRule(_Model):
        backend_port: int
        frontend_port: int
        load_distribution: Optional[str]
        probe_port: Optional[int]
        probe_protocol: Union[str, ProbeProtocol]
        probe_request_path: Optional[str]
        protocol: Union[str, Protocol]

        @overload
        def __init__(
                self, 
                *, 
                backend_port: int, 
                frontend_port: int, 
                load_distribution: Optional[str] = ..., 
                probe_port: Optional[int] = ..., 
                probe_protocol: Union[str, ProbeProtocol], 
                probe_request_path: Optional[str] = ..., 
                protocol: Union[str, Protocol]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicefabricmanagedclusters.models.LongRunningOperationResult(_Model):
        end_time: Optional[datetime]
        error: Optional[ErrorModelError]
        name: Optional[str]
        percent_complete: Optional[float]
        start_time: Optional[datetime]
        status: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                end_time: Optional[datetime] = ..., 
                error: Optional[ErrorModelError] = ..., 
                name: Optional[str] = ..., 
                percent_complete: Optional[float] = ..., 
                start_time: Optional[datetime] = ..., 
                status: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicefabricmanagedclusters.models.ManagedAzResiliencyStatus(_Model):
        base_resource_status: Optional[list[ResourceAzStatus]]
        is_cluster_zone_resilient: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                base_resource_status: Optional[list[ResourceAzStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicefabricmanagedclusters.models.ManagedCluster(TrackedResource):
        etag: Optional[str]
        id: str
        location: str
        name: str
        properties: Optional[ManagedClusterProperties]
        sku: Sku
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[ManagedClusterProperties] = ..., 
                sku: Sku, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.servicefabricmanagedclusters.models.ManagedClusterAddOnFeature(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BACKUP_RESTORE_SERVICE = "BackupRestoreService"
        DNS_SERVICE = "DnsService"
        RESOURCE_MONITOR_SERVICE = "ResourceMonitorService"


    class azure.mgmt.servicefabricmanagedclusters.models.ManagedClusterCodeVersionResult(_Model):
        id: Optional[str]
        name: Optional[str]
        properties: Optional[ManagedClusterVersionDetails]
        type: Optional[str]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                properties: Optional[ManagedClusterVersionDetails] = ..., 
                type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.servicefabricmanagedclusters.models.ManagedClusterProperties(_Model):
        addon_features: Optional[list[Union[str, ManagedClusterAddOnFeature]]]
        admin_password: Optional[str]
        admin_user_name: str
        allocated_outbound_ports: Optional[int]
        allow_rdp_access: Optional[bool]
        application_type_versions_cleanup_policy: Optional[ApplicationTypeVersionsCleanupPolicy]
        auto_generated_domain_name_label_scope: Optional[Union[str, AutoGeneratedDomainNameLabelScope]]
        auxiliary_subnets: Optional[list[Subnet]]
        azure_active_directory: Optional[AzureActiveDirectory]
        client_connection_port: Optional[int]
        clients: Optional[list[ClientCertificate]]
        cluster_certificate_thumbprints: Optional[list[str]]
        cluster_code_version: Optional[str]
        cluster_id: Optional[str]
        cluster_state: Optional[Union[str, ClusterState]]
        cluster_upgrade_cadence: Optional[Union[str, ClusterUpgradeCadence]]
        cluster_upgrade_mode: Optional[Union[str, ClusterUpgradeMode]]
        ddos_protection_plan_id: Optional[str]
        dns_name: str
        enable_auto_os_upgrade: Optional[bool]
        enable_http_gateway_exclusive_auth_mode: Optional[bool]
        enable_ipv6: Optional[bool]
        enable_outbound_only_node_types: Optional[bool]
        enable_service_public_ip: Optional[bool]
        fabric_settings: Optional[list[SettingsSectionDescription]]
        fqdn: Optional[str]
        http_gateway_connection_port: Optional[int]
        http_gateway_token_auth_connection_port: Optional[int]
        ip_tags: Optional[list[IpTag]]
        ipv4_address: Optional[str]
        ipv6_address: Optional[str]
        load_balancing_rules: Optional[list[LoadBalancingRule]]
        network_security_rules: Optional[list[NetworkSecurityRule]]
        provisioning_state: Optional[Union[str, ManagedResourceProvisioningState]]
        public_i_pv6_prefix_id: Optional[str]
        public_ip_prefix_id: Optional[str]
        service_endpoints: Optional[list[ServiceEndpoint]]
        skip_managed_nsg_assignment: Optional[bool]
        subnet_id: Optional[str]
        upgrade_description: Optional[ClusterUpgradePolicy]
        use_custom_vnet: Optional[bool]
        vm_image: Optional[str]
        zonal_resiliency: Optional[bool]
        zonal_update_mode: Optional[Union[str, ZonalUpdateMode]]

        @overload
        def __init__(
                self, 
                *, 
                addon_features: Optional[list[Union[str, ManagedClusterAddOnFeature]]] = ..., 
                admin_password: Optional[str] = ..., 
                admin_user_name: str, 
                allocated_outbound_ports: Optional[int] = ..., 
                allow_rdp_access: Optional[bool] = ..., 
                application_type_versions_cleanup_policy: Optional[ApplicationTypeVersionsCleanupPolicy] = ..., 
                auto_generated_domain_name_label_scope: Optional[Union[str, AutoGeneratedDomainNameLabelScope]] = ..., 
                auxiliary_subnets: Optional[list[Subnet]] = ..., 
                azure_active_directory: Optional[AzureActiveDirectory] = ..., 
                client_connection_port: Optional[int] = ..., 
                clients: Optional[list[ClientCertificate]] = ..., 
                cluster_code_version: Optional[str] = ..., 
                cluster_upgrade_cadence: Optional[Union[str, ClusterUpgradeCadence]] = ..., 
                cluster_upgrade_mode: Optional[Union[str, ClusterUpgradeMode]] = ..., 
                ddos_protection_plan_id: Optional[str] = ..., 
                dns_name: str, 
                enable_auto_os_upgrade: Optional[bool] = ..., 
                enable_http_gateway_exclusive_auth_mode: Optional[bool] = ..., 
                enable_ipv6: Optional[bool] = ..., 
                enable_outbound_only_node_types: Optional[bool] = ..., 
                enable_service_public_ip: Optional[bool] = ..., 
                fabric_settings: Optional[list[SettingsSectionDescription]] = ..., 
                http_gateway_connection_port: Optional[int] = ..., 
                http_gateway_token_auth_connection_port: Optional[int] = ..., 
                ip_tags: Optional[list[IpTag]] = ..., 
                load_balancing_rules: Optional[list[LoadBalancingRule]] = ..., 
                network_security_rules: Optional[list[NetworkSecurityRule]] = ..., 
                public_i_pv6_prefix_id: Optional[str] = ..., 
                public_ip_prefix_id: Optional[str] = ..., 
                service_endpoints: Optional[list[ServiceEndpoint]] = ..., 
                skip_managed_nsg_assignment: Optional[bool] = ..., 
                subnet_id: Optional[str] = ..., 
                upgrade_description: Optional[ClusterUpgradePolicy] = ..., 
                use_custom_vnet: Optional[bool] = ..., 
                vm_image: Optional[str] = ..., 
                zonal_resiliency: Optional[bool] = ..., 
                zonal_update_mode: Optional[Union[str, ZonalUpdateMode]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicefabricmanagedclusters.models.ManagedClusterUpdateParameters(_Model):
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicefabricmanagedclusters.models.ManagedClusterVersionDetails(_Model):
        cluster_code_version: Optional[str]
        os_type: Optional[Union[str, OsType]]
        support_expiry_utc: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                cluster_code_version: Optional[str] = ..., 
                os_type: Optional[Union[str, OsType]] = ..., 
                support_expiry_utc: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicefabricmanagedclusters.models.ManagedClusterVersionEnvironment(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        WINDOWS = "Windows"


    class azure.mgmt.servicefabricmanagedclusters.models.ManagedIdentity(_Model):
        principal_id: Optional[str]
        tenant_id: Optional[str]
        type: Optional[Union[str, ManagedIdentityType]]
        user_assigned_identities: Optional[dict[str, UserAssignedIdentity]]

        @overload
        def __init__(
                self, 
                *, 
                type: Optional[Union[str, ManagedIdentityType]] = ..., 
                user_assigned_identities: Optional[dict[str, UserAssignedIdentity]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicefabricmanagedclusters.models.ManagedIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        SYSTEM_ASSIGNED_USER_ASSIGNED = "SystemAssigned, UserAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.servicefabricmanagedclusters.models.ManagedMaintenanceWindowStatus(_Model):
        can_apply_updates: Optional[bool]
        is_region_ready: Optional[bool]
        is_window_active: Optional[bool]
        is_window_enabled: Optional[bool]
        last_window_end_time_utc: Optional[datetime]
        last_window_start_time_utc: Optional[datetime]
        last_window_status_update_at_utc: Optional[datetime]


    class azure.mgmt.servicefabricmanagedclusters.models.ManagedResourceProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATED = "Created"
        CREATING = "Creating"
        DELETED = "Deleted"
        DELETING = "Deleting"
        FAILED = "Failed"
        NONE = "None"
        OTHER = "Other"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.servicefabricmanagedclusters.models.ManagedVMSize(_Model):
        id: Optional[str]
        name: Optional[str]
        properties: Optional[VMSize]
        type: Optional[str]


    class azure.mgmt.servicefabricmanagedclusters.models.MoveCost(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HIGH = "High"
        LOW = "Low"
        MEDIUM = "Medium"
        ZERO = "Zero"


    class azure.mgmt.servicefabricmanagedclusters.models.NamedPartitionScheme(Partition, discriminator='Named'):
        names: list[str]
        partition_scheme: Literal[PartitionScheme.NAMED]

        @overload
        def __init__(
                self, 
                *, 
                names: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicefabricmanagedclusters.models.NetworkSecurityRule(_Model):
        access: Union[str, Access]
        description: Optional[str]
        destination_address_prefix: Optional[str]
        destination_address_prefixes: Optional[list[str]]
        destination_port_range: Optional[str]
        destination_port_ranges: Optional[list[str]]
        direction: Union[str, Direction]
        name: str
        priority: int
        protocol: Union[str, NsgProtocol]
        source_address_prefix: Optional[str]
        source_address_prefixes: Optional[list[str]]
        source_port_range: Optional[str]
        source_port_ranges: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                access: Union[str, Access], 
                description: Optional[str] = ..., 
                destination_address_prefix: Optional[str] = ..., 
                destination_address_prefixes: Optional[list[str]] = ..., 
                destination_port_range: Optional[str] = ..., 
                destination_port_ranges: Optional[list[str]] = ..., 
                direction: Union[str, Direction], 
                name: str, 
                priority: int, 
                protocol: Union[str, NsgProtocol], 
                source_address_prefix: Optional[str] = ..., 
                source_address_prefixes: Optional[list[str]] = ..., 
                source_port_range: Optional[str] = ..., 
                source_port_ranges: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicefabricmanagedclusters.models.NodeType(ProxyResource):
        id: str
        name: str
        properties: Optional[NodeTypeProperties]
        sku: Optional[NodeTypeSku]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[NodeTypeProperties] = ..., 
                sku: Optional[NodeTypeSku] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.servicefabricmanagedclusters.models.NodeTypeActionParameters(_Model):
        force: Optional[bool]
        nodes: Optional[list[str]]
        update_type: Optional[Union[str, UpdateType]]

        @overload
        def __init__(
                self, 
                *, 
                force: Optional[bool] = ..., 
                nodes: Optional[list[str]] = ..., 
                update_type: Optional[Union[str, UpdateType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicefabricmanagedclusters.models.NodeTypeAvailableSku(_Model):
        capacity: Optional[NodeTypeSkuCapacity]
        resource_type: Optional[str]
        sku: Optional[NodeTypeSupportedSku]


    class azure.mgmt.servicefabricmanagedclusters.models.NodeTypeFaultSimulation(_Model):
        node_type_name: Optional[str]
        operation_id: Optional[str]
        operation_status: Optional[Union[str, SfmcOperationStatus]]
        status: Optional[Union[str, FaultSimulationStatus]]

        @overload
        def __init__(
                self, 
                *, 
                node_type_name: Optional[str] = ..., 
                operation_id: Optional[str] = ..., 
                operation_status: Optional[Union[str, SfmcOperationStatus]] = ..., 
                status: Optional[Union[str, FaultSimulationStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicefabricmanagedclusters.models.NodeTypeNatConfig(_Model):
        backend_port: Optional[int]
        frontend_port_range_end: Optional[int]
        frontend_port_range_start: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                backend_port: Optional[int] = ..., 
                frontend_port_range_end: Optional[int] = ..., 
                frontend_port_range_start: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicefabricmanagedclusters.models.NodeTypeProperties(_Model):
        additional_data_disks: Optional[list[VmssDataDisk]]
        additional_network_interface_configurations: Optional[list[AdditionalNetworkInterfaceConfiguration]]
        application_ports: Optional[EndpointRangeDescription]
        capacities: Optional[dict[str, str]]
        computer_name_prefix: Optional[str]
        data_disk_letter: Optional[str]
        data_disk_size_gb: Optional[int]
        data_disk_type: Optional[Union[str, DiskType]]
        dscp_configuration_id: Optional[str]
        enable_accelerated_networking: Optional[bool]
        enable_encryption_at_host: Optional[bool]
        enable_node_public_i_pv6: Optional[bool]
        enable_node_public_ip: Optional[bool]
        enable_over_provisioning: Optional[bool]
        enable_resilient_ephemeral_os_disk: Optional[bool]
        ephemeral_ports: Optional[EndpointRangeDescription]
        eviction_policy: Optional[Union[str, EvictionPolicyType]]
        frontend_configurations: Optional[list[FrontendConfiguration]]
        host_group_id: Optional[str]
        is_outbound_only: Optional[bool]
        is_primary: bool
        is_spot_vm: Optional[bool]
        is_stateless: Optional[bool]
        multiple_placement_groups: Optional[bool]
        nat_configurations: Optional[list[NodeTypeNatConfig]]
        nat_gateway_id: Optional[str]
        network_security_rules: Optional[list[NetworkSecurityRule]]
        placement_properties: Optional[dict[str, str]]
        provisioning_state: Optional[Union[str, ManagedResourceProvisioningState]]
        proxy_agent_settings: Optional[ProxyAgentSettings]
        scale_in_policy: Optional[ScaleInPolicy]
        secure_boot_enabled: Optional[bool]
        security_encryption_type: Optional[Union[str, SecurityEncryptionType]]
        security_type: Optional[Union[str, SecurityType]]
        service_artifact_reference_id: Optional[str]
        spot_restore_timeout: Optional[str]
        subnet_id: Optional[str]
        use_default_public_load_balancer: Optional[bool]
        use_ephemeral_os_disk: Optional[bool]
        use_temp_data_disk: Optional[bool]
        vm_applications: Optional[list[VmApplication]]
        vm_extensions: Optional[list[VMSSExtension]]
        vm_image_offer: Optional[str]
        vm_image_plan: Optional[VmImagePlan]
        vm_image_publisher: Optional[str]
        vm_image_resource_id: Optional[str]
        vm_image_sku: Optional[str]
        vm_image_version: Optional[str]
        vm_instance_count: int
        vm_managed_identity: Optional[VmManagedIdentity]
        vm_secrets: Optional[list[VaultSecretGroup]]
        vm_setup_actions: Optional[list[Union[str, VmSetupAction]]]
        vm_shared_gallery_image_id: Optional[str]
        vm_size: Optional[str]
        zone_balance: Optional[bool]
        zones: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                additional_data_disks: Optional[list[VmssDataDisk]] = ..., 
                additional_network_interface_configurations: Optional[list[AdditionalNetworkInterfaceConfiguration]] = ..., 
                application_ports: Optional[EndpointRangeDescription] = ..., 
                capacities: Optional[dict[str, str]] = ..., 
                computer_name_prefix: Optional[str] = ..., 
                data_disk_letter: Optional[str] = ..., 
                data_disk_size_gb: Optional[int] = ..., 
                data_disk_type: Optional[Union[str, DiskType]] = ..., 
                dscp_configuration_id: Optional[str] = ..., 
                enable_accelerated_networking: Optional[bool] = ..., 
                enable_encryption_at_host: Optional[bool] = ..., 
                enable_node_public_i_pv6: Optional[bool] = ..., 
                enable_node_public_ip: Optional[bool] = ..., 
                enable_over_provisioning: Optional[bool] = ..., 
                enable_resilient_ephemeral_os_disk: Optional[bool] = ..., 
                ephemeral_ports: Optional[EndpointRangeDescription] = ..., 
                eviction_policy: Optional[Union[str, EvictionPolicyType]] = ..., 
                frontend_configurations: Optional[list[FrontendConfiguration]] = ..., 
                host_group_id: Optional[str] = ..., 
                is_outbound_only: Optional[bool] = ..., 
                is_primary: bool, 
                is_spot_vm: Optional[bool] = ..., 
                is_stateless: Optional[bool] = ..., 
                multiple_placement_groups: Optional[bool] = ..., 
                nat_configurations: Optional[list[NodeTypeNatConfig]] = ..., 
                nat_gateway_id: Optional[str] = ..., 
                network_security_rules: Optional[list[NetworkSecurityRule]] = ..., 
                placement_properties: Optional[dict[str, str]] = ..., 
                proxy_agent_settings: Optional[ProxyAgentSettings] = ..., 
                scale_in_policy: Optional[ScaleInPolicy] = ..., 
                secure_boot_enabled: Optional[bool] = ..., 
                security_encryption_type: Optional[Union[str, SecurityEncryptionType]] = ..., 
                security_type: Optional[Union[str, SecurityType]] = ..., 
                service_artifact_reference_id: Optional[str] = ..., 
                spot_restore_timeout: Optional[str] = ..., 
                subnet_id: Optional[str] = ..., 
                use_default_public_load_balancer: Optional[bool] = ..., 
                use_ephemeral_os_disk: Optional[bool] = ..., 
                use_temp_data_disk: Optional[bool] = ..., 
                vm_applications: Optional[list[VmApplication]] = ..., 
                vm_extensions: Optional[list[VMSSExtension]] = ..., 
                vm_image_offer: Optional[str] = ..., 
                vm_image_plan: Optional[VmImagePlan] = ..., 
                vm_image_publisher: Optional[str] = ..., 
                vm_image_resource_id: Optional[str] = ..., 
                vm_image_sku: Optional[str] = ..., 
                vm_image_version: Optional[str] = ..., 
                vm_instance_count: int, 
                vm_managed_identity: Optional[VmManagedIdentity] = ..., 
                vm_secrets: Optional[list[VaultSecretGroup]] = ..., 
                vm_setup_actions: Optional[list[Union[str, VmSetupAction]]] = ..., 
                vm_shared_gallery_image_id: Optional[str] = ..., 
                vm_size: Optional[str] = ..., 
                zone_balance: Optional[bool] = ..., 
                zones: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicefabricmanagedclusters.models.NodeTypeSku(_Model):
        capacity: int
        name: Optional[str]
        tier: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                capacity: int, 
                name: Optional[str] = ..., 
                tier: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicefabricmanagedclusters.models.NodeTypeSkuCapacity(_Model):
        default: Optional[int]
        maximum: Optional[int]
        minimum: Optional[int]
        scale_type: Optional[Union[str, NodeTypeSkuScaleType]]


    class azure.mgmt.servicefabricmanagedclusters.models.NodeTypeSkuScaleType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTOMATIC = "Automatic"
        MANUAL = "Manual"
        NONE = "None"


    class azure.mgmt.servicefabricmanagedclusters.models.NodeTypeSupportedSku(_Model):
        name: Optional[str]
        tier: Optional[str]


    class azure.mgmt.servicefabricmanagedclusters.models.NodeTypeUpdateParameters(_Model):
        sku: Optional[NodeTypeSku]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                sku: Optional[NodeTypeSku] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicefabricmanagedclusters.models.NsgProtocol(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AH = "ah"
        ESP = "esp"
        HTTP = "http"
        HTTPS = "https"
        ICMP = "icmp"
        TCP = "tcp"
        UDP = "udp"


    class azure.mgmt.servicefabricmanagedclusters.models.OperationResult(_Model):
        display: Optional[AvailableOperationDisplay]
        is_data_action: Optional[bool]
        name: Optional[str]
        next_link: Optional[str]
        origin: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                display: Optional[AvailableOperationDisplay] = ..., 
                is_data_action: Optional[bool] = ..., 
                name: Optional[str] = ..., 
                next_link: Optional[str] = ..., 
                origin: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicefabricmanagedclusters.models.OsType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        WINDOWS = "Windows"


    class azure.mgmt.servicefabricmanagedclusters.models.Partition(_Model):
        partition_scheme: str

        @overload
        def __init__(
                self, 
                *, 
                partition_scheme: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicefabricmanagedclusters.models.PartitionInstanceCountScaleMechanism(ScalingMechanism, discriminator='ScalePartitionInstanceCount'):
        kind: Literal[ServiceScalingMechanismKind.SCALE_PARTITION_INSTANCE_COUNT]
        max_instance_count: int
        min_instance_count: int
        scale_increment: int

        @overload
        def __init__(
                self, 
                *, 
                max_instance_count: int, 
                min_instance_count: int, 
                scale_increment: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicefabricmanagedclusters.models.PartitionScheme(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NAMED = "Named"
        SINGLETON = "Singleton"
        UNIFORM_INT64_RANGE = "UniformInt64Range"


    class azure.mgmt.servicefabricmanagedclusters.models.PrivateEndpointNetworkPolicies(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "disabled"
        ENABLED = "enabled"


    class azure.mgmt.servicefabricmanagedclusters.models.PrivateIPAddressVersion(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        I_PV4 = "IPv4"
        I_PV6 = "IPv6"


    class azure.mgmt.servicefabricmanagedclusters.models.PrivateLinkServiceNetworkPolicies(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "disabled"
        ENABLED = "enabled"


    class azure.mgmt.servicefabricmanagedclusters.models.ProbeProtocol(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HTTP = "http"
        HTTPS = "https"
        TCP = "tcp"


    class azure.mgmt.servicefabricmanagedclusters.models.Protocol(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        TCP = "tcp"
        UDP = "udp"


    class azure.mgmt.servicefabricmanagedclusters.models.ProxyAgentSettings(_Model):
        add_proxy_agent_extension: Optional[bool]
        enabled: Optional[bool]
        imds: Optional[HostEndpointSettings]
        key_incarnation_id: Optional[int]
        wire_server: Optional[HostEndpointSettings]

        @overload
        def __init__(
                self, 
                *, 
                add_proxy_agent_extension: Optional[bool] = ..., 
                enabled: Optional[bool] = ..., 
                imds: Optional[HostEndpointSettings] = ..., 
                key_incarnation_id: Optional[int] = ..., 
                wire_server: Optional[HostEndpointSettings] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicefabricmanagedclusters.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.servicefabricmanagedclusters.models.PublicIPAddressVersion(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        I_PV4 = "IPv4"
        I_PV6 = "IPv6"


    class azure.mgmt.servicefabricmanagedclusters.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.servicefabricmanagedclusters.models.ResourceAzStatus(_Model):
        details: Optional[str]
        is_zone_resilient: Optional[bool]
        resource_name: Optional[str]
        resource_type: Optional[str]


    class azure.mgmt.servicefabricmanagedclusters.models.RestartDeployedCodePackageRequest(_Model):
        code_package_instance_id: str
        code_package_name: str
        node_name: str
        service_manifest_name: str
        service_package_activation_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                code_package_instance_id: str, 
                code_package_name: str, 
                node_name: str, 
                service_manifest_name: str, 
                service_package_activation_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicefabricmanagedclusters.models.RestartKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SIMULTANEOUS = "Simultaneous"


    class azure.mgmt.servicefabricmanagedclusters.models.RestartReplicaRequest(_Model):
        force_restart: Optional[bool]
        partition_id: str
        replica_ids: list[int]
        restart_kind: Union[str, RestartKind]
        timeout: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                force_restart: Optional[bool] = ..., 
                partition_id: str, 
                replica_ids: list[int], 
                restart_kind: Union[str, RestartKind], 
                timeout: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicefabricmanagedclusters.models.RollingUpgradeMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MONITORED = "Monitored"
        UNMONITORED_AUTO = "UnmonitoredAuto"


    class azure.mgmt.servicefabricmanagedclusters.models.RollingUpgradeMonitoringPolicy(_Model):
        failure_action: Union[str, FailureAction]
        health_check_retry_timeout: str
        health_check_stable_duration: str
        health_check_wait_duration: str
        upgrade_domain_timeout: str
        upgrade_timeout: str

        @overload
        def __init__(
                self, 
                *, 
                failure_action: Union[str, FailureAction], 
                health_check_retry_timeout: str, 
                health_check_stable_duration: str, 
                health_check_wait_duration: str, 
                upgrade_domain_timeout: str, 
                upgrade_timeout: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicefabricmanagedclusters.models.RuntimeApplicationHealthPolicy(_Model):
        consider_warning_as_error: bool
        default_service_type_health_policy: Optional[RuntimeServiceTypeHealthPolicy]
        max_percent_unhealthy_deployed_applications: int
        service_type_health_policy_map: Optional[dict[str, RuntimeServiceTypeHealthPolicy]]

        @overload
        def __init__(
                self, 
                *, 
                consider_warning_as_error: bool, 
                default_service_type_health_policy: Optional[RuntimeServiceTypeHealthPolicy] = ..., 
                max_percent_unhealthy_deployed_applications: int, 
                service_type_health_policy_map: Optional[dict[str, RuntimeServiceTypeHealthPolicy]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicefabricmanagedclusters.models.RuntimeFailureAction(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MANUAL = "Manual"
        ROLLBACK = "Rollback"


    class azure.mgmt.servicefabricmanagedclusters.models.RuntimeResumeApplicationUpgradeParameters(_Model):
        upgrade_domain_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                upgrade_domain_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicefabricmanagedclusters.models.RuntimeRollingUpgradeMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MONITORED = "Monitored"
        UNMONITORED_AUTO = "UnmonitoredAuto"
        UNMONITORED_MANUAL = "UnmonitoredManual"


    class azure.mgmt.servicefabricmanagedclusters.models.RuntimeRollingUpgradeUpdateMonitoringPolicy(_Model):
        failure_action: Optional[Union[str, RuntimeFailureAction]]
        force_restart: Optional[bool]
        health_check_retry_timeout_in_milliseconds: Optional[str]
        health_check_stable_duration_in_milliseconds: Optional[str]
        health_check_wait_duration_in_milliseconds: Optional[str]
        instance_close_delay_duration_in_seconds: Optional[int]
        replica_set_check_timeout_in_milliseconds: Optional[int]
        rolling_upgrade_mode: Union[str, RuntimeRollingUpgradeMode]
        upgrade_domain_timeout_in_milliseconds: Optional[str]
        upgrade_timeout_in_milliseconds: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                failure_action: Optional[Union[str, RuntimeFailureAction]] = ..., 
                force_restart: Optional[bool] = ..., 
                health_check_retry_timeout_in_milliseconds: Optional[str] = ..., 
                health_check_stable_duration_in_milliseconds: Optional[str] = ..., 
                health_check_wait_duration_in_milliseconds: Optional[str] = ..., 
                instance_close_delay_duration_in_seconds: Optional[int] = ..., 
                replica_set_check_timeout_in_milliseconds: Optional[int] = ..., 
                rolling_upgrade_mode: Union[str, RuntimeRollingUpgradeMode], 
                upgrade_domain_timeout_in_milliseconds: Optional[str] = ..., 
                upgrade_timeout_in_milliseconds: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicefabricmanagedclusters.models.RuntimeServiceTypeHealthPolicy(_Model):
        max_percent_unhealthy_partitions_per_service: int
        max_percent_unhealthy_replicas_per_partition: int
        max_percent_unhealthy_services: int

        @overload
        def __init__(
                self, 
                *, 
                max_percent_unhealthy_partitions_per_service: int, 
                max_percent_unhealthy_replicas_per_partition: int, 
                max_percent_unhealthy_services: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicefabricmanagedclusters.models.RuntimeUpdateApplicationUpgradeParameters(_Model):
        application_health_policy: Optional[RuntimeApplicationHealthPolicy]
        name: str
        update_description: Optional[RuntimeRollingUpgradeUpdateMonitoringPolicy]
        upgrade_kind: Union[str, RuntimeUpgradeKind]

        @overload
        def __init__(
                self, 
                *, 
                application_health_policy: Optional[RuntimeApplicationHealthPolicy] = ..., 
                name: str, 
                update_description: Optional[RuntimeRollingUpgradeUpdateMonitoringPolicy] = ..., 
                upgrade_kind: Union[str, RuntimeUpgradeKind]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicefabricmanagedclusters.models.RuntimeUpgradeKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ROLLING = "Rolling"


    class azure.mgmt.servicefabricmanagedclusters.models.ScaleInPolicy(_Model):
        mode: Optional[Union[str, ScaleInPolicyMode]]

        @overload
        def __init__(
                self, 
                *, 
                mode: Optional[Union[str, ScaleInPolicyMode]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicefabricmanagedclusters.models.ScaleInPolicyMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEFAULT = "Default"
        NEWEST_NODE_FIRST = "NewestNodeFirst"
        OLDEST_NODE_FIRST = "OldestNodeFirst"


    class azure.mgmt.servicefabricmanagedclusters.models.ScalingMechanism(_Model):
        kind: str

        @overload
        def __init__(
                self, 
                *, 
                kind: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicefabricmanagedclusters.models.ScalingPolicy(_Model):
        scaling_mechanism: ScalingMechanism
        scaling_trigger: ScalingTrigger

        @overload
        def __init__(
                self, 
                *, 
                scaling_mechanism: ScalingMechanism, 
                scaling_trigger: ScalingTrigger
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicefabricmanagedclusters.models.ScalingTrigger(_Model):
        kind: str

        @overload
        def __init__(
                self, 
                *, 
                kind: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicefabricmanagedclusters.models.SecurityEncryptionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISK_WITH_VM_GUEST_STATE = "DiskWithVMGuestState"
        VM_GUEST_STATE_ONLY = "VMGuestStateOnly"


    class azure.mgmt.servicefabricmanagedclusters.models.SecurityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONFIDENTIAL_VM = "ConfidentialVM"
        STANDARD = "Standard"
        TRUSTED_LAUNCH = "TrustedLaunch"


    class azure.mgmt.servicefabricmanagedclusters.models.ServiceCorrelation(_Model):
        scheme: Union[str, ServiceCorrelationScheme]
        service_name: str

        @overload
        def __init__(
                self, 
                *, 
                scheme: Union[str, ServiceCorrelationScheme], 
                service_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicefabricmanagedclusters.models.ServiceCorrelationScheme(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALIGNED_AFFINITY = "AlignedAffinity"
        NON_ALIGNED_AFFINITY = "NonAlignedAffinity"


    class azure.mgmt.servicefabricmanagedclusters.models.ServiceEndpoint(_Model):
        locations: Optional[list[str]]
        network_identifier: Optional[str]
        service: str

        @overload
        def __init__(
                self, 
                *, 
                locations: Optional[list[str]] = ..., 
                network_identifier: Optional[str] = ..., 
                service: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicefabricmanagedclusters.models.ServiceKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        STATEFUL = "Stateful"
        STATELESS = "Stateless"


    class azure.mgmt.servicefabricmanagedclusters.models.ServiceLoadMetric(_Model):
        default_load: Optional[int]
        name: str
        primary_default_load: Optional[int]
        secondary_default_load: Optional[int]
        weight: Optional[Union[str, ServiceLoadMetricWeight]]

        @overload
        def __init__(
                self, 
                *, 
                default_load: Optional[int] = ..., 
                name: str, 
                primary_default_load: Optional[int] = ..., 
                secondary_default_load: Optional[int] = ..., 
                weight: Optional[Union[str, ServiceLoadMetricWeight]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicefabricmanagedclusters.models.ServiceLoadMetricWeight(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HIGH = "High"
        LOW = "Low"
        MEDIUM = "Medium"
        ZERO = "Zero"


    class azure.mgmt.servicefabricmanagedclusters.models.ServicePackageActivationMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EXCLUSIVE_PROCESS = "ExclusiveProcess"
        SHARED_PROCESS = "SharedProcess"


    class azure.mgmt.servicefabricmanagedclusters.models.ServicePlacementInvalidDomainPolicy(ServicePlacementPolicy, discriminator='InvalidDomain'):
        domain_name: str
        type: Literal[ServicePlacementPolicyType.INVALID_DOMAIN]

        @overload
        def __init__(
                self, 
                *, 
                domain_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicefabricmanagedclusters.models.ServicePlacementNonPartiallyPlaceServicePolicy(ServicePlacementPolicy, discriminator='NonPartiallyPlaceService'):
        type: Literal[ServicePlacementPolicyType.NON_PARTIALLY_PLACE_SERVICE]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicefabricmanagedclusters.models.ServicePlacementPolicy(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicefabricmanagedclusters.models.ServicePlacementPolicyType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INVALID_DOMAIN = "InvalidDomain"
        NON_PARTIALLY_PLACE_SERVICE = "NonPartiallyPlaceService"
        PREFERRED_PRIMARY_DOMAIN = "PreferredPrimaryDomain"
        REQUIRED_DOMAIN = "RequiredDomain"
        REQUIRED_DOMAIN_DISTRIBUTION = "RequiredDomainDistribution"


    class azure.mgmt.servicefabricmanagedclusters.models.ServicePlacementPreferPrimaryDomainPolicy(ServicePlacementPolicy, discriminator='PreferredPrimaryDomain'):
        domain_name: str
        type: Literal[ServicePlacementPolicyType.PREFERRED_PRIMARY_DOMAIN]

        @overload
        def __init__(
                self, 
                *, 
                domain_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicefabricmanagedclusters.models.ServicePlacementRequireDomainDistributionPolicy(ServicePlacementPolicy, discriminator='RequiredDomainDistribution'):
        domain_name: str
        type: Literal[ServicePlacementPolicyType.REQUIRED_DOMAIN_DISTRIBUTION]

        @overload
        def __init__(
                self, 
                *, 
                domain_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicefabricmanagedclusters.models.ServicePlacementRequiredDomainPolicy(ServicePlacementPolicy, discriminator='RequiredDomain'):
        domain_name: str
        type: Literal[ServicePlacementPolicyType.REQUIRED_DOMAIN]

        @overload
        def __init__(
                self, 
                *, 
                domain_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicefabricmanagedclusters.models.ServiceResource(ProxyResource):
        id: str
        location: Optional[str]
        name: str
        properties: Optional[ServiceResourceProperties]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                properties: Optional[ServiceResourceProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicefabricmanagedclusters.models.ServiceResourceProperties(ServiceResourcePropertiesBase):
        correlation_scheme: list[ServiceCorrelation]
        default_move_cost: Union[str, MoveCost]
        partition_description: Partition
        placement_constraints: str
        provisioning_state: Optional[str]
        scaling_policies: list[ScalingPolicy]
        service_dns_name: Optional[str]
        service_kind: str
        service_load_metrics: list[ServiceLoadMetric]
        service_package_activation_mode: Optional[Union[str, ServicePackageActivationMode]]
        service_placement_policies: list[ServicePlacementPolicy]
        service_type_name: str

        @overload
        def __init__(
                self, 
                *, 
                correlation_scheme: Optional[list[ServiceCorrelation]] = ..., 
                default_move_cost: Optional[Union[str, MoveCost]] = ..., 
                partition_description: Partition, 
                placement_constraints: Optional[str] = ..., 
                scaling_policies: Optional[list[ScalingPolicy]] = ..., 
                service_dns_name: Optional[str] = ..., 
                service_kind: str, 
                service_load_metrics: Optional[list[ServiceLoadMetric]] = ..., 
                service_package_activation_mode: Optional[Union[str, ServicePackageActivationMode]] = ..., 
                service_placement_policies: Optional[list[ServicePlacementPolicy]] = ..., 
                service_type_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicefabricmanagedclusters.models.ServiceResourcePropertiesBase(_Model):
        correlation_scheme: Optional[list[ServiceCorrelation]]
        default_move_cost: Optional[Union[str, MoveCost]]
        placement_constraints: Optional[str]
        scaling_policies: Optional[list[ScalingPolicy]]
        service_load_metrics: Optional[list[ServiceLoadMetric]]
        service_placement_policies: Optional[list[ServicePlacementPolicy]]

        @overload
        def __init__(
                self, 
                *, 
                correlation_scheme: Optional[list[ServiceCorrelation]] = ..., 
                default_move_cost: Optional[Union[str, MoveCost]] = ..., 
                placement_constraints: Optional[str] = ..., 
                scaling_policies: Optional[list[ScalingPolicy]] = ..., 
                service_load_metrics: Optional[list[ServiceLoadMetric]] = ..., 
                service_placement_policies: Optional[list[ServicePlacementPolicy]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicefabricmanagedclusters.models.ServiceScalingMechanismKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ADD_REMOVE_INCREMENTAL_NAMED_PARTITION = "AddRemoveIncrementalNamedPartition"
        SCALE_PARTITION_INSTANCE_COUNT = "ScalePartitionInstanceCount"


    class azure.mgmt.servicefabricmanagedclusters.models.ServiceScalingTriggerKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVERAGE_PARTITION_LOAD_TRIGGER = "AveragePartitionLoadTrigger"
        AVERAGE_SERVICE_LOAD_TRIGGER = "AverageServiceLoadTrigger"


    class azure.mgmt.servicefabricmanagedclusters.models.ServiceTypeHealthPolicy(_Model):
        max_percent_unhealthy_partitions_per_service: int
        max_percent_unhealthy_replicas_per_partition: int
        max_percent_unhealthy_services: int

        @overload
        def __init__(
                self, 
                *, 
                max_percent_unhealthy_partitions_per_service: int, 
                max_percent_unhealthy_replicas_per_partition: int, 
                max_percent_unhealthy_services: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicefabricmanagedclusters.models.ServiceUpdateParameters(_Model):
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicefabricmanagedclusters.models.SettingsParameterDescription(_Model):
        name: str
        value: str

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                value: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicefabricmanagedclusters.models.SettingsSectionDescription(_Model):
        name: str
        parameters: list[SettingsParameterDescription]

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                parameters: list[SettingsParameterDescription]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicefabricmanagedclusters.models.SfmcOperationStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ABORTED = "Aborted"
        CANCELED = "Canceled"
        CREATED = "Created"
        FAILED = "Failed"
        STARTED = "Started"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.servicefabricmanagedclusters.models.SingletonPartitionScheme(Partition, discriminator='Singleton'):
        partition_scheme: Literal[PartitionScheme.SINGLETON]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicefabricmanagedclusters.models.Sku(_Model):
        name: Union[str, SkuName]

        @overload
        def __init__(
                self, 
                *, 
                name: Union[str, SkuName]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicefabricmanagedclusters.models.SkuName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BASIC = "Basic"
        STANDARD = "Standard"


    class azure.mgmt.servicefabricmanagedclusters.models.StatefulServiceProperties(ServiceResourceProperties, discriminator='Stateful'):
        correlation_scheme: list[ServiceCorrelation]
        default_move_cost: Union[str, MoveCost]
        has_persisted_state: Optional[bool]
        min_replica_set_size: Optional[int]
        partition_description: Partition
        placement_constraints: str
        provisioning_state: str
        quorum_loss_wait_duration: Optional[str]
        replica_restart_wait_duration: Optional[str]
        scaling_policies: list[ScalingPolicy]
        service_dns_name: str
        service_kind: Literal[ServiceKind.STATEFUL]
        service_load_metrics: list[ServiceLoadMetric]
        service_package_activation_mode: Union[str, ServicePackageActivationMode]
        service_placement_policies: list[ServicePlacementPolicy]
        service_placement_time_limit: Optional[str]
        service_type_name: str
        stand_by_replica_keep_duration: Optional[str]
        target_replica_set_size: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                correlation_scheme: Optional[list[ServiceCorrelation]] = ..., 
                default_move_cost: Optional[Union[str, MoveCost]] = ..., 
                has_persisted_state: Optional[bool] = ..., 
                min_replica_set_size: Optional[int] = ..., 
                partition_description: Partition, 
                placement_constraints: Optional[str] = ..., 
                quorum_loss_wait_duration: Optional[str] = ..., 
                replica_restart_wait_duration: Optional[str] = ..., 
                scaling_policies: Optional[list[ScalingPolicy]] = ..., 
                service_dns_name: Optional[str] = ..., 
                service_load_metrics: Optional[list[ServiceLoadMetric]] = ..., 
                service_package_activation_mode: Optional[Union[str, ServicePackageActivationMode]] = ..., 
                service_placement_policies: Optional[list[ServicePlacementPolicy]] = ..., 
                service_placement_time_limit: Optional[str] = ..., 
                service_type_name: str, 
                stand_by_replica_keep_duration: Optional[str] = ..., 
                target_replica_set_size: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicefabricmanagedclusters.models.StatelessServiceProperties(ServiceResourceProperties, discriminator='Stateless'):
        correlation_scheme: list[ServiceCorrelation]
        default_move_cost: Union[str, MoveCost]
        instance_count: int
        min_instance_count: Optional[int]
        min_instance_percentage: Optional[int]
        partition_description: Partition
        placement_constraints: str
        provisioning_state: str
        scaling_policies: list[ScalingPolicy]
        service_dns_name: str
        service_kind: Literal[ServiceKind.STATELESS]
        service_load_metrics: list[ServiceLoadMetric]
        service_package_activation_mode: Union[str, ServicePackageActivationMode]
        service_placement_policies: list[ServicePlacementPolicy]
        service_type_name: str

        @overload
        def __init__(
                self, 
                *, 
                correlation_scheme: Optional[list[ServiceCorrelation]] = ..., 
                default_move_cost: Optional[Union[str, MoveCost]] = ..., 
                instance_count: int, 
                min_instance_count: Optional[int] = ..., 
                min_instance_percentage: Optional[int] = ..., 
                partition_description: Partition, 
                placement_constraints: Optional[str] = ..., 
                scaling_policies: Optional[list[ScalingPolicy]] = ..., 
                service_dns_name: Optional[str] = ..., 
                service_load_metrics: Optional[list[ServiceLoadMetric]] = ..., 
                service_package_activation_mode: Optional[Union[str, ServicePackageActivationMode]] = ..., 
                service_placement_policies: Optional[list[ServicePlacementPolicy]] = ..., 
                service_type_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicefabricmanagedclusters.models.SubResource(_Model):
        id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicefabricmanagedclusters.models.Subnet(_Model):
        enable_ipv6: Optional[bool]
        name: str
        network_security_group_id: Optional[str]
        private_endpoint_network_policies: Optional[Union[str, PrivateEndpointNetworkPolicies]]
        private_link_service_network_policies: Optional[Union[str, PrivateLinkServiceNetworkPolicies]]

        @overload
        def __init__(
                self, 
                *, 
                enable_ipv6: Optional[bool] = ..., 
                name: str, 
                network_security_group_id: Optional[str] = ..., 
                private_endpoint_network_policies: Optional[Union[str, PrivateEndpointNetworkPolicies]] = ..., 
                private_link_service_network_policies: Optional[Union[str, PrivateLinkServiceNetworkPolicies]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicefabricmanagedclusters.models.SystemData(_Model):
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


    class azure.mgmt.servicefabricmanagedclusters.models.TrackedResource(Resource):
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


    class azure.mgmt.servicefabricmanagedclusters.models.UniformInt64RangePartitionScheme(Partition, discriminator='UniformInt64Range'):
        count: int
        high_key: int
        low_key: int
        partition_scheme: Literal[PartitionScheme.UNIFORM_INT64_RANGE]

        @overload
        def __init__(
                self, 
                *, 
                count: int, 
                high_key: int, 
                low_key: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicefabricmanagedclusters.models.UpdateType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BY_UPGRADE_DOMAIN = "ByUpgradeDomain"
        DEFAULT = "Default"


    class azure.mgmt.servicefabricmanagedclusters.models.UserAssignedIdentity(_Model):
        client_id: Optional[str]
        principal_id: Optional[str]


    class azure.mgmt.servicefabricmanagedclusters.models.VMSSExtension(_Model):
        name: str
        properties: VMSSExtensionProperties

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                properties: VMSSExtensionProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.servicefabricmanagedclusters.models.VMSSExtensionProperties(_Model):
        auto_upgrade_minor_version: Optional[bool]
        enable_automatic_upgrade: Optional[bool]
        force_update_tag: Optional[str]
        protected_settings: Optional[Any]
        provision_after_extensions: Optional[list[str]]
        provisioning_state: Optional[str]
        publisher: str
        settings: Optional[Any]
        setup_order: Optional[list[Union[str, VmssExtensionSetupOrder]]]
        type: str
        type_handler_version: str

        @overload
        def __init__(
                self, 
                *, 
                auto_upgrade_minor_version: Optional[bool] = ..., 
                enable_automatic_upgrade: Optional[bool] = ..., 
                force_update_tag: Optional[str] = ..., 
                protected_settings: Optional[Any] = ..., 
                provision_after_extensions: Optional[list[str]] = ..., 
                publisher: str, 
                settings: Optional[Any] = ..., 
                setup_order: Optional[list[Union[str, VmssExtensionSetupOrder]]] = ..., 
                type: str, 
                type_handler_version: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicefabricmanagedclusters.models.VMSize(_Model):
        size: Optional[str]


    class azure.mgmt.servicefabricmanagedclusters.models.VaultCertificate(_Model):
        certificate_store: str
        certificate_url: str

        @overload
        def __init__(
                self, 
                *, 
                certificate_store: str, 
                certificate_url: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicefabricmanagedclusters.models.VaultSecretGroup(_Model):
        source_vault: SubResource
        vault_certificates: list[VaultCertificate]

        @overload
        def __init__(
                self, 
                *, 
                source_vault: SubResource, 
                vault_certificates: list[VaultCertificate]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicefabricmanagedclusters.models.VmApplication(_Model):
        configuration_reference: Optional[str]
        enable_automatic_upgrade: Optional[bool]
        order: Optional[int]
        package_reference_id: str
        treat_failure_as_deployment_failure: Optional[bool]
        vm_gallery_tags: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                configuration_reference: Optional[str] = ..., 
                enable_automatic_upgrade: Optional[bool] = ..., 
                order: Optional[int] = ..., 
                package_reference_id: str, 
                treat_failure_as_deployment_failure: Optional[bool] = ..., 
                vm_gallery_tags: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicefabricmanagedclusters.models.VmImagePlan(_Model):
        name: Optional[str]
        product: Optional[str]
        promotion_code: Optional[str]
        publisher: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                product: Optional[str] = ..., 
                promotion_code: Optional[str] = ..., 
                publisher: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicefabricmanagedclusters.models.VmManagedIdentity(_Model):
        user_assigned_identities: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                user_assigned_identities: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicefabricmanagedclusters.models.VmSetupAction(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ENABLE_CONTAINERS = "EnableContainers"
        ENABLE_HYPER_V = "EnableHyperV"


    class azure.mgmt.servicefabricmanagedclusters.models.VmssDataDisk(_Model):
        disk_letter: str
        disk_size_gb: int
        disk_type: Union[str, DiskType]
        lun: int

        @overload
        def __init__(
                self, 
                *, 
                disk_letter: str, 
                disk_size_gb: int, 
                disk_type: Union[str, DiskType], 
                lun: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicefabricmanagedclusters.models.VmssExtensionSetupOrder(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BEFORE_SF_RUNTIME = "BeforeSFRuntime"


    class azure.mgmt.servicefabricmanagedclusters.models.ZonalUpdateMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAST = "Fast"
        STANDARD = "Standard"


    class azure.mgmt.servicefabricmanagedclusters.models.ZoneFaultSimulationContent(FaultSimulationContent, discriminator='Zone'):
        constraints: FaultSimulationConstraints
        fault_kind: Literal[FaultKind.ZONE]
        force: bool
        zones: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                constraints: Optional[FaultSimulationConstraints] = ..., 
                force: Optional[bool] = ..., 
                zones: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


namespace azure.mgmt.servicefabricmanagedclusters.operations

    class azure.mgmt.servicefabricmanagedclusters.operations.ApplicationTypeVersionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_type_name: str, 
                version: str, 
                parameters: ApplicationTypeVersionResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ApplicationTypeVersionResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_type_name: str, 
                version: str, 
                parameters: ApplicationTypeVersionResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ApplicationTypeVersionResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_type_name: str, 
                version: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ApplicationTypeVersionResource]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_type_name: str, 
                version: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_type_name: str, 
                version: str, 
                **kwargs: Any
            ) -> ApplicationTypeVersionResource: ...

        @distributed_trace
        def list_by_application_types(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_type_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ApplicationTypeVersionResource]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_type_name: str, 
                version: str, 
                parameters: ApplicationTypeVersionUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplicationTypeVersionResource: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_type_name: str, 
                version: str, 
                parameters: ApplicationTypeVersionUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplicationTypeVersionResource: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_type_name: str, 
                version: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplicationTypeVersionResource: ...


    class azure.mgmt.servicefabricmanagedclusters.operations.ApplicationTypesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_type_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_type_name: str, 
                parameters: ApplicationTypeResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplicationTypeResource: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_type_name: str, 
                parameters: ApplicationTypeResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplicationTypeResource: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_type_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplicationTypeResource: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_type_name: str, 
                **kwargs: Any
            ) -> ApplicationTypeResource: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ApplicationTypeResource]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_type_name: str, 
                parameters: ApplicationTypeUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplicationTypeResource: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_type_name: str, 
                parameters: ApplicationTypeUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplicationTypeResource: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_type_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplicationTypeResource: ...


    class azure.mgmt.servicefabricmanagedclusters.operations.ApplicationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_name: str, 
                parameters: ApplicationResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ApplicationResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_name: str, 
                parameters: ApplicationResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ApplicationResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ApplicationResource]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_fetch_health(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_name: str, 
                parameters: ApplicationFetchHealthRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_fetch_health(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_name: str, 
                parameters: ApplicationFetchHealthRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_fetch_health(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_read_upgrade(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_restart_deployed_code_package(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_name: str, 
                parameters: RestartDeployedCodePackageRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_restart_deployed_code_package(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_name: str, 
                parameters: RestartDeployedCodePackageRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_restart_deployed_code_package(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_resume_upgrade(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_name: str, 
                parameters: RuntimeResumeApplicationUpgradeParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_resume_upgrade(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_name: str, 
                parameters: RuntimeResumeApplicationUpgradeParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_resume_upgrade(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_start_rollback(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_name: str, 
                parameters: ApplicationUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ApplicationResource]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_name: str, 
                parameters: ApplicationUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ApplicationResource]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ApplicationResource]: ...

        @overload
        def begin_update_upgrade(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_name: str, 
                parameters: RuntimeUpdateApplicationUpgradeParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update_upgrade(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_name: str, 
                parameters: RuntimeUpdateApplicationUpgradeParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update_upgrade(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_name: str, 
                **kwargs: Any
            ) -> ApplicationResource: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ApplicationResource]: ...


    class azure.mgmt.servicefabricmanagedclusters.operations.ManagedApplyMaintenanceWindowOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def post(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                body: Optional[ApplyMaintenanceWindowRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def post(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                body: Optional[ApplyMaintenanceWindowRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def post(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.servicefabricmanagedclusters.operations.ManagedAzResiliencyStatusOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> ManagedAzResiliencyStatus: ...


    class azure.mgmt.servicefabricmanagedclusters.operations.ManagedClusterVersionOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                location: str, 
                cluster_version: str, 
                **kwargs: Any
            ) -> ManagedClusterCodeVersionResult: ...

        @distributed_trace
        def get_by_environment(
                self, 
                location: str, 
                environment: Union[str, ManagedClusterVersionEnvironment], 
                cluster_version: str, 
                **kwargs: Any
            ) -> ManagedClusterCodeVersionResult: ...

        @distributed_trace
        def list(
                self, 
                location: str, 
                **kwargs: Any
            ) -> List[ManagedClusterCodeVersionResult]: ...

        @distributed_trace
        def list_by_environment(
                self, 
                location: str, 
                environment: Union[str, ManagedClusterVersionEnvironment], 
                **kwargs: Any
            ) -> List[ManagedClusterCodeVersionResult]: ...


    class azure.mgmt.servicefabricmanagedclusters.operations.ManagedClustersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                parameters: ManagedCluster, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ManagedCluster]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                parameters: ManagedCluster, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ManagedCluster]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ManagedCluster]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_start_fault_simulation(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                parameters: FaultSimulationContentWrapper, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[FaultSimulation]: ...

        @overload
        def begin_start_fault_simulation(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                parameters: FaultSimulationContentWrapper, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[FaultSimulation]: ...

        @overload
        def begin_start_fault_simulation(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[FaultSimulation]: ...

        @overload
        def begin_stop_fault_simulation(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                parameters: FaultSimulationIdContent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[FaultSimulation]: ...

        @overload
        def begin_stop_fault_simulation(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                parameters: FaultSimulationIdContent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[FaultSimulation]: ...

        @overload
        def begin_stop_fault_simulation(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[FaultSimulation]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                parameters: ManagedClusterUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ManagedCluster]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                parameters: ManagedClusterUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ManagedCluster]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ManagedCluster]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> ManagedCluster: ...

        @overload
        def get_fault_simulation(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                parameters: FaultSimulationIdContent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FaultSimulation: ...

        @overload
        def get_fault_simulation(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                parameters: FaultSimulationIdContent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FaultSimulation: ...

        @overload
        def get_fault_simulation(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FaultSimulation: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ManagedCluster]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[ManagedCluster]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'cluster_name', 'accept']}, api_versions_list=['2026-05-01-preview'])
        def list_fault_simulation(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> ItemPaged[FaultSimulation]: ...


    class azure.mgmt.servicefabricmanagedclusters.operations.ManagedMaintenanceWindowStatusOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> ManagedMaintenanceWindowStatus: ...


    class azure.mgmt.servicefabricmanagedclusters.operations.ManagedUnsupportedVMSizesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                location: str, 
                vm_size: str, 
                **kwargs: Any
            ) -> ManagedVMSize: ...

        @distributed_trace
        def list(
                self, 
                location: str, 
                **kwargs: Any
            ) -> ItemPaged[ManagedVMSize]: ...


    class azure.mgmt.servicefabricmanagedclusters.operations.NodeTypeSkusOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                node_type_name: str, 
                **kwargs: Any
            ) -> ItemPaged[NodeTypeAvailableSku]: ...


    class azure.mgmt.servicefabricmanagedclusters.operations.NodeTypesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                node_type_name: str, 
                parameters: NodeType, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NodeType]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                node_type_name: str, 
                parameters: NodeType, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NodeType]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                node_type_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NodeType]: ...

        @overload
        def begin_deallocate(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                node_type_name: str, 
                parameters: NodeTypeActionParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_deallocate(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                node_type_name: str, 
                parameters: NodeTypeActionParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_deallocate(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                node_type_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                node_type_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_delete_node(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                node_type_name: str, 
                parameters: NodeTypeActionParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_delete_node(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                node_type_name: str, 
                parameters: NodeTypeActionParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_delete_node(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                node_type_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_redeploy(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                node_type_name: str, 
                parameters: NodeTypeActionParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_redeploy(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                node_type_name: str, 
                parameters: NodeTypeActionParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_redeploy(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                node_type_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_reimage(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                node_type_name: str, 
                parameters: NodeTypeActionParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_reimage(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                node_type_name: str, 
                parameters: NodeTypeActionParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_reimage(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                node_type_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_restart(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                node_type_name: str, 
                parameters: NodeTypeActionParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_restart(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                node_type_name: str, 
                parameters: NodeTypeActionParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_restart(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                node_type_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_start(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                node_type_name: str, 
                parameters: NodeTypeActionParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_start(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                node_type_name: str, 
                parameters: NodeTypeActionParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_start(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                node_type_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_start_fault_simulation(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                node_type_name: str, 
                parameters: FaultSimulationContentWrapper, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[FaultSimulation]: ...

        @overload
        def begin_start_fault_simulation(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                node_type_name: str, 
                parameters: FaultSimulationContentWrapper, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[FaultSimulation]: ...

        @overload
        def begin_start_fault_simulation(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                node_type_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[FaultSimulation]: ...

        @overload
        def begin_stop_fault_simulation(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                node_type_name: str, 
                parameters: FaultSimulationIdContent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[FaultSimulation]: ...

        @overload
        def begin_stop_fault_simulation(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                node_type_name: str, 
                parameters: FaultSimulationIdContent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[FaultSimulation]: ...

        @overload
        def begin_stop_fault_simulation(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                node_type_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[FaultSimulation]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                node_type_name: str, 
                parameters: NodeTypeUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NodeType]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                node_type_name: str, 
                parameters: NodeTypeUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NodeType]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                node_type_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NodeType]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                node_type_name: str, 
                **kwargs: Any
            ) -> NodeType: ...

        @overload
        def get_fault_simulation(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                node_type_name: str, 
                parameters: FaultSimulationIdContent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FaultSimulation: ...

        @overload
        def get_fault_simulation(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                node_type_name: str, 
                parameters: FaultSimulationIdContent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FaultSimulation: ...

        @overload
        def get_fault_simulation(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                node_type_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FaultSimulation: ...

        @distributed_trace
        def list_by_managed_clusters(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> ItemPaged[NodeType]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'cluster_name', 'node_type_name', 'accept']}, api_versions_list=['2026-05-01-preview'])
        def list_fault_simulation(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                node_type_name: str, 
                **kwargs: Any
            ) -> ItemPaged[FaultSimulation]: ...


    class azure.mgmt.servicefabricmanagedclusters.operations.OperationResultsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                location: str, 
                operation_id: str, 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.servicefabricmanagedclusters.operations.OperationStatusOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                location: str, 
                operation_id: str, 
                **kwargs: Any
            ) -> LongRunningOperationResult: ...


    class azure.mgmt.servicefabricmanagedclusters.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[OperationResult]: ...


    class azure.mgmt.servicefabricmanagedclusters.operations.ServicesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_name: str, 
                service_name: str, 
                parameters: ServiceResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ServiceResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_name: str, 
                service_name: str, 
                parameters: ServiceResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ServiceResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_name: str, 
                service_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ServiceResource]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_name: str, 
                service_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_restart_replica(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_name: str, 
                service_name: str, 
                parameters: RestartReplicaRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_restart_replica(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_name: str, 
                service_name: str, 
                parameters: RestartReplicaRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_restart_replica(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_name: str, 
                service_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_name: str, 
                service_name: str, 
                **kwargs: Any
            ) -> ServiceResource: ...

        @distributed_trace
        def list_by_applications(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ServiceResource]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_name: str, 
                service_name: str, 
                parameters: ServiceUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ServiceResource: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_name: str, 
                service_name: str, 
                parameters: ServiceUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ServiceResource: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_name: str, 
                service_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ServiceResource: ...


namespace azure.mgmt.servicefabricmanagedclusters.types

    class azure.mgmt.servicefabricmanagedclusters.types.AddRemoveIncrementalNamedPartitionScalingMechanism(TypedDict, total=False):
        key "kind": Required[Literal[ServiceScalingMechanismKind.ADD_REMOVE_INCREMENTAL_NAMED_PARTITION]]
        key "maxPartitionCount": Required[int]
        key "minPartitionCount": Required[int]
        key "scaleIncrement": Required[int]
        kind: Literal[ServiceScalingMechanismKind.ADD_REMOVE_INCREMENTAL_NAMED_PARTITION]
        maxPartitionCount: int
        minPartitionCount: int
        scaleIncrement: int


    class azure.mgmt.servicefabricmanagedclusters.types.AdditionalNetworkInterfaceConfiguration(TypedDict, total=False):
        key "dscpConfiguration": ForwardRef('SubResource', module='types')
        key "enableAcceleratedNetworking": bool
        key "ipConfigurations": Required[list[IpConfiguration]]
        key "name": Required[str]
        dscpConfiguration: SubResource
        enableAcceleratedNetworking: bool
        ipConfigurations: list[IpConfiguration]
        name: str


    class azure.mgmt.servicefabricmanagedclusters.types.ApplicationFetchHealthRequest(TypedDict, total=False):
        key "deployedApplicationsHealthStateFilter": Union[str, HealthFilter]
        key "eventsHealthStateFilter": Union[str, HealthFilter]
        key "excludeHealthStatistics": bool
        key "servicesHealthStateFilter": Union[str, HealthFilter]
        key "timeout": int
        deployedApplicationsHealthStateFilter: Union[str, HealthFilter]
        eventsHealthStateFilter: Union[str, HealthFilter]
        excludeHealthStatistics: bool
        servicesHealthStateFilter: Union[str, HealthFilter]
        timeout: int


    class azure.mgmt.servicefabricmanagedclusters.types.ApplicationHealthPolicy(TypedDict, total=False):
        key "considerWarningAsError": Required[bool]
        key "defaultServiceTypeHealthPolicy": ForwardRef('ServiceTypeHealthPolicy', module='types')
        key "maxPercentUnhealthyDeployedApplications": Required[int]
        considerWarningAsError: bool
        defaultServiceTypeHealthPolicy: ServiceTypeHealthPolicy
        maxPercentUnhealthyDeployedApplications: int
        serviceTypeHealthPolicyMap: dict[str, ServiceTypeHealthPolicy]


    class azure.mgmt.servicefabricmanagedclusters.types.ApplicationResource(ProxyResource):
        key "id": str
        key "identity": ForwardRef('ManagedIdentity', module='types')
        key "location": str
        key "name": str
        key "properties": ForwardRef('ApplicationResourceProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        identity: ManagedIdentity
        location: str
        name: str
        properties: ApplicationResourceProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.servicefabricmanagedclusters.types.ApplicationResourceProperties(TypedDict, total=False):
        key "provisioningState": str
        key "upgradePolicy": ForwardRef('ApplicationUpgradePolicy', module='types')
        key "version": str
        managedIdentities: list[ApplicationUserAssignedIdentity]
        parameters: dict[str, str]
        provisioningState: str
        upgradePolicy: ApplicationUpgradePolicy
        version: str


    class azure.mgmt.servicefabricmanagedclusters.types.ApplicationTypeResource(ProxyResource):
        key "id": str
        key "location": str
        key "name": str
        key "properties": ForwardRef('ApplicationTypeResourceProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: ApplicationTypeResourceProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.servicefabricmanagedclusters.types.ApplicationTypeResourceProperties(TypedDict, total=False):
        key "provisioningState": str
        provisioningState: str


    class azure.mgmt.servicefabricmanagedclusters.types.ApplicationTypeUpdateParameters(TypedDict, total=False):
        tags: dict[str, str]


    class azure.mgmt.servicefabricmanagedclusters.types.ApplicationTypeVersionResource(ProxyResource):
        key "id": str
        key "location": str
        key "name": str
        key "properties": ForwardRef('ApplicationTypeVersionResourceProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: ApplicationTypeVersionResourceProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.servicefabricmanagedclusters.types.ApplicationTypeVersionResourceProperties(TypedDict, total=False):
        key "appPackageUrl": Required[str]
        key "provisioningState": str
        appPackageUrl: str
        provisioningState: str


    class azure.mgmt.servicefabricmanagedclusters.types.ApplicationTypeVersionUpdateParameters(TypedDict, total=False):
        tags: dict[str, str]


    class azure.mgmt.servicefabricmanagedclusters.types.ApplicationTypeVersionsCleanupPolicy(TypedDict, total=False):
        key "maxUnusedVersionsToKeep": Required[int]
        maxUnusedVersionsToKeep: int


    class azure.mgmt.servicefabricmanagedclusters.types.ApplicationUpdateParameters(TypedDict, total=False):
        key "properties": ForwardRef('ApplicationUpdateParametersProperties', module='types')
        properties: ApplicationUpdateParametersProperties
        tags: dict[str, str]


    class azure.mgmt.servicefabricmanagedclusters.types.ApplicationUpdateParametersProperties(TypedDict, total=False):
        parameters: dict[str, str]


    class azure.mgmt.servicefabricmanagedclusters.types.ApplicationUpgradePolicy(TypedDict, total=False):
        key "applicationHealthPolicy": ForwardRef('ApplicationHealthPolicy', module='types')
        key "forceRestart": bool
        key "instanceCloseDelayDuration": int
        key "recreateApplication": bool
        key "rollingUpgradeMonitoringPolicy": ForwardRef('RollingUpgradeMonitoringPolicy', module='types')
        key "upgradeMode": Union[str, RollingUpgradeMode]
        key "upgradeReplicaSetCheckTimeout": int
        applicationHealthPolicy: ApplicationHealthPolicy
        forceRestart: bool
        instanceCloseDelayDuration: int
        recreateApplication: bool
        rollingUpgradeMonitoringPolicy: RollingUpgradeMonitoringPolicy
        upgradeMode: Union[str, RollingUpgradeMode]
        upgradeReplicaSetCheckTimeout: int


    class azure.mgmt.servicefabricmanagedclusters.types.ApplicationUserAssignedIdentity(TypedDict, total=False):
        key "name": Required[str]
        key "principalId": Required[str]
        name: str
        principalId: str


    class azure.mgmt.servicefabricmanagedclusters.types.ApplyMaintenanceWindowRequest(TypedDict, total=False):
        key "duration": str
        key "startDateTime": str
        key "timeZone": str
        duration: str
        startDateTime: str
        timeZone: str


    class azure.mgmt.servicefabricmanagedclusters.types.AveragePartitionLoadScalingTrigger(TypedDict, total=False):
        key "kind": Required[Literal[ServiceScalingTriggerKind.AVERAGE_PARTITION_LOAD_TRIGGER]]
        key "lowerLoadThreshold": Required[float]
        key "metricName": Required[str]
        key "scaleInterval": Required[str]
        key "upperLoadThreshold": Required[float]
        kind: Literal[ServiceScalingTriggerKind.AVERAGE_PARTITION_LOAD_TRIGGER]
        lowerLoadThreshold: float
        metricName: str
        scaleInterval: str
        upperLoadThreshold: float


    class azure.mgmt.servicefabricmanagedclusters.types.AverageServiceLoadScalingTrigger(TypedDict, total=False):
        key "kind": Required[Literal[ServiceScalingTriggerKind.AVERAGE_SERVICE_LOAD_TRIGGER]]
        key "lowerLoadThreshold": Required[float]
        key "metricName": Required[str]
        key "scaleInterval": Required[str]
        key "upperLoadThreshold": Required[float]
        key "useOnlyPrimaryLoad": Required[bool]
        kind: Literal[ServiceScalingTriggerKind.AVERAGE_SERVICE_LOAD_TRIGGER]
        lowerLoadThreshold: float
        metricName: str
        scaleInterval: str
        upperLoadThreshold: float
        useOnlyPrimaryLoad: bool


    class azure.mgmt.servicefabricmanagedclusters.types.AzureActiveDirectory(TypedDict, total=False):
        key "clientApplication": str
        key "clusterApplication": str
        key "tenantId": str
        clientApplication: str
        clusterApplication: str
        tenantId: str


    class azure.mgmt.servicefabricmanagedclusters.types.ClientCertificate(TypedDict, total=False):
        key "commonName": str
        key "isAdmin": Required[bool]
        key "issuerThumbprint": str
        key "thumbprint": str
        commonName: str
        isAdmin: bool
        issuerThumbprint: str
        thumbprint: str


    class azure.mgmt.servicefabricmanagedclusters.types.ClusterHealthPolicy(TypedDict, total=False):
        key "maxPercentUnhealthyApplications": Required[int]
        key "maxPercentUnhealthyNodes": Required[int]
        maxPercentUnhealthyApplications: int
        maxPercentUnhealthyNodes: int


    class azure.mgmt.servicefabricmanagedclusters.types.ClusterMonitoringPolicy(TypedDict, total=False):
        key "healthCheckRetryTimeout": Required[str]
        key "healthCheckStableDuration": Required[str]
        key "healthCheckWaitDuration": Required[str]
        key "upgradeDomainTimeout": Required[str]
        key "upgradeTimeout": Required[str]
        healthCheckRetryTimeout: str
        healthCheckStableDuration: str
        healthCheckWaitDuration: str
        upgradeDomainTimeout: str
        upgradeTimeout: str


    class azure.mgmt.servicefabricmanagedclusters.types.ClusterUpgradeDeltaHealthPolicy(TypedDict, total=False):
        key "maxPercentDeltaUnhealthyApplications": int
        key "maxPercentDeltaUnhealthyNodes": Required[int]
        key "maxPercentUpgradeDomainDeltaUnhealthyNodes": int
        maxPercentDeltaUnhealthyApplications: int
        maxPercentDeltaUnhealthyNodes: int
        maxPercentUpgradeDomainDeltaUnhealthyNodes: int


    class azure.mgmt.servicefabricmanagedclusters.types.ClusterUpgradePolicy(TypedDict, total=False):
        key "deltaHealthPolicy": ForwardRef('ClusterUpgradeDeltaHealthPolicy', module='types')
        key "forceRestart": bool
        key "healthPolicy": ForwardRef('ClusterHealthPolicy', module='types')
        key "monitoringPolicy": ForwardRef('ClusterMonitoringPolicy', module='types')
        key "upgradeReplicaSetCheckTimeout": str
        deltaHealthPolicy: ClusterUpgradeDeltaHealthPolicy
        forceRestart: bool
        healthPolicy: ClusterHealthPolicy
        monitoringPolicy: ClusterMonitoringPolicy
        upgradeReplicaSetCheckTimeout: str


    class azure.mgmt.servicefabricmanagedclusters.types.EndpointRangeDescription(TypedDict, total=False):
        key "endPort": Required[int]
        key "startPort": Required[int]
        endPort: int
        startPort: int


    class azure.mgmt.servicefabricmanagedclusters.types.FaultKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ZONE = "Zone"


    class azure.mgmt.servicefabricmanagedclusters.types.FaultSimulationConstraints(TypedDict, total=False):
        key "expirationTime": str
        expirationTime: str


    class azure.mgmt.servicefabricmanagedclusters.types.FaultSimulationContent(TypedDict, total=False):
        key "constraints": ForwardRef('FaultSimulationConstraints', module='types')
        key "faultKind": Required[Literal[FaultKind.ZONE]]
        key "force": bool
        constraints: FaultSimulationConstraints
        faultKind: Literal[FaultKind.ZONE]
        force: bool
        zones: list[str]


    class azure.mgmt.servicefabricmanagedclusters.types.FaultSimulationContentWrapper(TypedDict, total=False):
        key "parameters": Required[FaultSimulationContent]
        parameters: FaultSimulationContent


    class azure.mgmt.servicefabricmanagedclusters.types.FaultSimulationIdContent(TypedDict, total=False):
        key "simulationId": Required[str]
        simulationId: str


    class azure.mgmt.servicefabricmanagedclusters.types.FrontendConfiguration(TypedDict, total=False):
        key "applicationGatewayBackendAddressPoolId": str
        key "ipAddressType": Union[str, IPAddressType]
        key "loadBalancerBackendAddressPoolId": str
        key "loadBalancerInboundNatPoolId": str
        applicationGatewayBackendAddressPoolId: str
        ipAddressType: Union[str, IPAddressType]
        loadBalancerBackendAddressPoolId: str
        loadBalancerInboundNatPoolId: str


    class azure.mgmt.servicefabricmanagedclusters.types.HostEndpointSettings(TypedDict, total=False):
        key "inVMAccessControlProfileReferenceId": str
        key "mode": str
        inVMAccessControlProfileReferenceId: str
        mode: str


    class azure.mgmt.servicefabricmanagedclusters.types.IpConfiguration(TypedDict, total=False):
        key "name": Required[str]
        key "privateIPAddressVersion": Union[str, PrivateIPAddressVersion]
        key "publicIPAddressConfiguration": ForwardRef('IpConfigurationPublicIPAddressConfiguration', module='types')
        key "subnet": ForwardRef('SubResource', module='types')
        applicationGatewayBackendAddressPools: list[SubResource]
        loadBalancerBackendAddressPools: list[SubResource]
        loadBalancerInboundNatPools: list[SubResource]
        name: str
        privateIPAddressVersion: Union[str, PrivateIPAddressVersion]
        publicIPAddressConfiguration: IpConfigurationPublicIPAddressConfiguration
        subnet: SubResource


    class azure.mgmt.servicefabricmanagedclusters.types.IpConfigurationPublicIPAddressConfiguration(TypedDict, total=False):
        key "name": Required[str]
        key "publicIPAddressVersion": Union[str, PublicIPAddressVersion]
        ipTags: list[IpTag]
        name: str
        publicIPAddressVersion: Union[str, PublicIPAddressVersion]


    class azure.mgmt.servicefabricmanagedclusters.types.IpTag(TypedDict, total=False):
        key "ipTagType": Required[str]
        key "tag": Required[str]
        ipTagType: str
        tag: str


    class azure.mgmt.servicefabricmanagedclusters.types.LoadBalancingRule(TypedDict, total=False):
        key "backendPort": Required[int]
        key "frontendPort": Required[int]
        key "loadDistribution": str
        key "probePort": int
        key "probeProtocol": Required[Union[str, ProbeProtocol]]
        key "probeRequestPath": str
        key "protocol": Required[Union[str, Protocol]]
        backendPort: int
        frontendPort: int
        loadDistribution: str
        probePort: int
        probeProtocol: Union[str, ProbeProtocol]
        probeRequestPath: str
        protocol: Union[str, Protocol]


    class azure.mgmt.servicefabricmanagedclusters.types.ManagedCluster(TrackedResource):
        key "etag": str
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('ManagedClusterProperties', module='types')
        key "sku": Required[Sku]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        location: str
        name: str
        properties: ManagedClusterProperties
        sku: Sku
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.servicefabricmanagedclusters.types.ManagedClusterProperties(TypedDict, total=False):
        key "VMImage": str
        key "adminPassword": str
        key "adminUserName": Required[str]
        key "allocatedOutboundPorts": int
        key "allowRdpAccess": bool
        key "applicationTypeVersionsCleanupPolicy": ForwardRef('ApplicationTypeVersionsCleanupPolicy', module='types')
        key "autoGeneratedDomainNameLabelScope": Union[str, AutoGeneratedDomainNameLabelScope]
        key "azureActiveDirectory": ForwardRef('AzureActiveDirectory', module='types')
        key "clientConnectionPort": int
        key "clusterCodeVersion": str
        key "clusterId": str
        key "clusterState": Union[str, ClusterState]
        key "clusterUpgradeCadence": Union[str, ClusterUpgradeCadence]
        key "clusterUpgradeMode": Union[str, ClusterUpgradeMode]
        key "ddosProtectionPlanId": str
        key "dnsName": Required[str]
        key "enableAutoOSUpgrade": bool
        key "enableHttpGatewayExclusiveAuthMode": bool
        key "enableIpv6": bool
        key "enableOutboundOnlyNodeTypes": bool
        key "enableServicePublicIP": bool
        key "fqdn": str
        key "httpGatewayConnectionPort": int
        key "httpGatewayTokenAuthConnectionPort": int
        key "ipv4Address": str
        key "ipv6Address": str
        key "provisioningState": Union[str, ManagedResourceProvisioningState]
        key "publicIPPrefixId": str
        key "publicIPv6PrefixId": str
        key "skipManagedNsgAssignment": bool
        key "subnetId": str
        key "upgradeDescription": ForwardRef('ClusterUpgradePolicy', module='types')
        key "useCustomVnet": bool
        key "zonalResiliency": bool
        key "zonalUpdateMode": Union[str, ZonalUpdateMode]
        VMImage: str
        addonFeatures: list[Union[str, ManagedClusterAddOnFeature]]
        adminPassword: str
        adminUserName: str
        allocatedOutboundPorts: int
        allowRdpAccess: bool
        applicationTypeVersionsCleanupPolicy: ApplicationTypeVersionsCleanupPolicy
        autoGeneratedDomainNameLabelScope: Union[str, AutoGeneratedDomainNameLabelScope]
        auxiliarySubnets: list[Subnet]
        azureActiveDirectory: AzureActiveDirectory
        clientConnectionPort: int
        clients: list[ClientCertificate]
        clusterCertificateThumbprints: list[str]
        clusterCodeVersion: str
        clusterId: str
        clusterState: Union[str, ClusterState]
        clusterUpgradeCadence: Union[str, ClusterUpgradeCadence]
        clusterUpgradeMode: Union[str, ClusterUpgradeMode]
        ddosProtectionPlanId: str
        dnsName: str
        enableAutoOSUpgrade: bool
        enableHttpGatewayExclusiveAuthMode: bool
        enableIpv6: bool
        enableOutboundOnlyNodeTypes: bool
        enableServicePublicIP: bool
        fabricSettings: list[SettingsSectionDescription]
        fqdn: str
        httpGatewayConnectionPort: int
        httpGatewayTokenAuthConnectionPort: int
        ipTags: list[IpTag]
        ipv4Address: str
        ipv6Address: str
        loadBalancingRules: list[LoadBalancingRule]
        networkSecurityRules: list[NetworkSecurityRule]
        provisioningState: Union[str, ManagedResourceProvisioningState]
        publicIPPrefixId: str
        publicIPv6PrefixId: str
        serviceEndpoints: list[ServiceEndpoint]
        skipManagedNsgAssignment: bool
        subnetId: str
        upgradeDescription: ClusterUpgradePolicy
        useCustomVnet: bool
        zonalResiliency: bool
        zonalUpdateMode: Union[str, ZonalUpdateMode]


    class azure.mgmt.servicefabricmanagedclusters.types.ManagedClusterUpdateParameters(TypedDict, total=False):
        tags: dict[str, str]


    class azure.mgmt.servicefabricmanagedclusters.types.ManagedIdentity(TypedDict, total=False):
        key "principalId": str
        key "tenantId": str
        key "type": Union[str, ManagedIdentityType]
        principalId: str
        tenantId: str
        type: Union[str, ManagedIdentityType]
        userAssignedIdentities: dict[str, UserAssignedIdentity]


    class azure.mgmt.servicefabricmanagedclusters.types.NamedPartitionScheme(TypedDict, total=False):
        key "names": Required[list[str]]
        key "partitionScheme": Required[Literal[PartitionScheme.NAMED]]
        names: list[str]
        partitionScheme: Literal[PartitionScheme.NAMED]


    class azure.mgmt.servicefabricmanagedclusters.types.NetworkSecurityRule(TypedDict, total=False):
        key "access": Required[Union[str, Access]]
        key "description": str
        key "destinationAddressPrefix": str
        key "destinationPortRange": str
        key "direction": Required[Union[str, Direction]]
        key "name": Required[str]
        key "priority": Required[int]
        key "protocol": Required[Union[str, NsgProtocol]]
        key "sourceAddressPrefix": str
        key "sourcePortRange": str
        access: Union[str, Access]
        description: str
        destinationAddressPrefix: str
        destinationAddressPrefixes: list[str]
        destinationPortRange: str
        destinationPortRanges: list[str]
        direction: Union[str, Direction]
        name: str
        priority: int
        protocol: Union[str, NsgProtocol]
        sourceAddressPrefix: str
        sourceAddressPrefixes: list[str]
        sourcePortRange: str
        sourcePortRanges: list[str]


    class azure.mgmt.servicefabricmanagedclusters.types.NodeType(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('NodeTypeProperties', module='types')
        key "sku": ForwardRef('NodeTypeSku', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: NodeTypeProperties
        sku: NodeTypeSku
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.servicefabricmanagedclusters.types.NodeTypeActionParameters(TypedDict, total=False):
        key "force": bool
        key "updateType": Union[str, UpdateType]
        force: bool
        nodes: list[str]
        updateType: Union[str, UpdateType]


    class azure.mgmt.servicefabricmanagedclusters.types.NodeTypeNatConfig(TypedDict, total=False):
        key "backendPort": int
        key "frontendPortRangeEnd": int
        key "frontendPortRangeStart": int
        backendPort: int
        frontendPortRangeEnd: int
        frontendPortRangeStart: int


    class azure.mgmt.servicefabricmanagedclusters.types.NodeTypeProperties(TypedDict, total=False):
        key "applicationPorts": ForwardRef('EndpointRangeDescription', module='types')
        key "computerNamePrefix": str
        key "dataDiskLetter": str
        key "dataDiskSizeGB": int
        key "dataDiskType": Union[str, DiskType]
        key "dscpConfigurationId": str
        key "enableAcceleratedNetworking": bool
        key "enableEncryptionAtHost": bool
        key "enableNodePublicIP": bool
        key "enableNodePublicIPv6": bool
        key "enableOverProvisioning": bool
        key "enableResilientEphemeralOsDisk": bool
        key "ephemeralPorts": ForwardRef('EndpointRangeDescription', module='types')
        key "evictionPolicy": Union[str, EvictionPolicyType]
        key "hostGroupId": str
        key "isOutboundOnly": bool
        key "isPrimary": Required[bool]
        key "isSpotVM": bool
        key "isStateless": bool
        key "multiplePlacementGroups": bool
        key "natGatewayId": str
        key "provisioningState": Union[str, ManagedResourceProvisioningState]
        key "proxyAgentSettings": ForwardRef('ProxyAgentSettings', module='types')
        key "scaleInPolicy": ForwardRef('ScaleInPolicy', module='types')
        key "secureBootEnabled": bool
        key "securityEncryptionType": Union[str, SecurityEncryptionType]
        key "securityType": Union[str, SecurityType]
        key "serviceArtifactReferenceId": str
        key "spotRestoreTimeout": str
        key "subnetId": str
        key "useDefaultPublicLoadBalancer": bool
        key "useEphemeralOSDisk": bool
        key "useTempDataDisk": bool
        key "vmImageOffer": str
        key "vmImagePlan": ForwardRef('VmImagePlan', module='types')
        key "vmImagePublisher": str
        key "vmImageResourceId": str
        key "vmImageSku": str
        key "vmImageVersion": str
        key "vmInstanceCount": Required[int]
        key "vmManagedIdentity": ForwardRef('VmManagedIdentity', module='types')
        key "vmSharedGalleryImageId": str
        key "vmSize": str
        key "zoneBalance": bool
        additionalDataDisks: list[VmssDataDisk]
        additionalNetworkInterfaceConfigurations: list[AdditionalNetworkInterfaceConfiguration]
        applicationPorts: EndpointRangeDescription
        capacities: dict[str, str]
        computerNamePrefix: str
        dataDiskLetter: str
        dataDiskSizeGB: int
        dataDiskType: Union[str, DiskType]
        dscpConfigurationId: str
        enableAcceleratedNetworking: bool
        enableEncryptionAtHost: bool
        enableNodePublicIP: bool
        enableNodePublicIPv6: bool
        enableOverProvisioning: bool
        enableResilientEphemeralOsDisk: bool
        ephemeralPorts: EndpointRangeDescription
        evictionPolicy: Union[str, EvictionPolicyType]
        frontendConfigurations: list[FrontendConfiguration]
        hostGroupId: str
        isOutboundOnly: bool
        isPrimary: bool
        isSpotVM: bool
        isStateless: bool
        multiplePlacementGroups: bool
        natConfigurations: list[NodeTypeNatConfig]
        natGatewayId: str
        networkSecurityRules: list[NetworkSecurityRule]
        placementProperties: dict[str, str]
        provisioningState: Union[str, ManagedResourceProvisioningState]
        proxyAgentSettings: ProxyAgentSettings
        scaleInPolicy: ScaleInPolicy
        secureBootEnabled: bool
        securityEncryptionType: Union[str, SecurityEncryptionType]
        securityType: Union[str, SecurityType]
        serviceArtifactReferenceId: str
        spotRestoreTimeout: str
        subnetId: str
        useDefaultPublicLoadBalancer: bool
        useEphemeralOSDisk: bool
        useTempDataDisk: bool
        vmApplications: list[VmApplication]
        vmExtensions: list[VMSSExtension]
        vmImageOffer: str
        vmImagePlan: VmImagePlan
        vmImagePublisher: str
        vmImageResourceId: str
        vmImageSku: str
        vmImageVersion: str
        vmInstanceCount: int
        vmManagedIdentity: VmManagedIdentity
        vmSecrets: list[VaultSecretGroup]
        vmSetupActions: list[Union[str, VmSetupAction]]
        vmSharedGalleryImageId: str
        vmSize: str
        zoneBalance: bool
        zones: list[str]


    class azure.mgmt.servicefabricmanagedclusters.types.NodeTypeSku(TypedDict, total=False):
        key "capacity": Required[int]
        key "name": str
        key "tier": str
        capacity: int
        name: str
        tier: str


    class azure.mgmt.servicefabricmanagedclusters.types.NodeTypeUpdateParameters(TypedDict, total=False):
        key "sku": ForwardRef('NodeTypeSku', module='types')
        sku: NodeTypeSku
        tags: dict[str, str]


    class azure.mgmt.servicefabricmanagedclusters.types.PartitionInstanceCountScaleMechanism(TypedDict, total=False):
        key "kind": Required[Literal[ServiceScalingMechanismKind.SCALE_PARTITION_INSTANCE_COUNT]]
        key "maxInstanceCount": Required[int]
        key "minInstanceCount": Required[int]
        key "scaleIncrement": Required[int]
        kind: Literal[ServiceScalingMechanismKind.SCALE_PARTITION_INSTANCE_COUNT]
        maxInstanceCount: int
        minInstanceCount: int
        scaleIncrement: int


    class azure.mgmt.servicefabricmanagedclusters.types.PartitionScheme(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NAMED = "Named"
        SINGLETON = "Singleton"
        UNIFORM_INT64_RANGE = "UniformInt64Range"


    class azure.mgmt.servicefabricmanagedclusters.types.ProxyAgentSettings(TypedDict, total=False):
        key "addProxyAgentExtension": bool
        key "enabled": bool
        key "imds": ForwardRef('HostEndpointSettings', module='types')
        key "keyIncarnationId": int
        key "wireServer": ForwardRef('HostEndpointSettings', module='types')
        addProxyAgentExtension: bool
        enabled: bool
        imds: HostEndpointSettings
        keyIncarnationId: int
        wireServer: HostEndpointSettings


    class azure.mgmt.servicefabricmanagedclusters.types.ProxyResource(Resource):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        systemData: SystemData
        type: str


    class azure.mgmt.servicefabricmanagedclusters.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        systemData: SystemData
        type: str


    class azure.mgmt.servicefabricmanagedclusters.types.RestartDeployedCodePackageRequest(TypedDict, total=False):
        key "codePackageInstanceId": Required[str]
        key "codePackageName": Required[str]
        key "nodeName": Required[str]
        key "serviceManifestName": Required[str]
        key "servicePackageActivationId": str
        codePackageInstanceId: str
        codePackageName: str
        nodeName: str
        serviceManifestName: str
        servicePackageActivationId: str


    class azure.mgmt.servicefabricmanagedclusters.types.RestartReplicaRequest(TypedDict, total=False):
        key "forceRestart": bool
        key "partitionId": Required[str]
        key "replicaIds": Required[list[int]]
        key "restartKind": Required[Union[str, RestartKind]]
        key "timeout": int
        forceRestart: bool
        partitionId: str
        replicaIds: list[int]
        restartKind: Union[str, RestartKind]
        timeout: int


    class azure.mgmt.servicefabricmanagedclusters.types.RollingUpgradeMonitoringPolicy(TypedDict, total=False):
        key "failureAction": Required[Union[str, FailureAction]]
        key "healthCheckRetryTimeout": Required[str]
        key "healthCheckStableDuration": Required[str]
        key "healthCheckWaitDuration": Required[str]
        key "upgradeDomainTimeout": Required[str]
        key "upgradeTimeout": Required[str]
        failureAction: Union[str, FailureAction]
        healthCheckRetryTimeout: str
        healthCheckStableDuration: str
        healthCheckWaitDuration: str
        upgradeDomainTimeout: str
        upgradeTimeout: str


    class azure.mgmt.servicefabricmanagedclusters.types.RuntimeApplicationHealthPolicy(TypedDict, total=False):
        key "considerWarningAsError": Required[bool]
        key "defaultServiceTypeHealthPolicy": ForwardRef('RuntimeServiceTypeHealthPolicy', module='types')
        key "maxPercentUnhealthyDeployedApplications": Required[int]
        considerWarningAsError: bool
        defaultServiceTypeHealthPolicy: RuntimeServiceTypeHealthPolicy
        maxPercentUnhealthyDeployedApplications: int
        serviceTypeHealthPolicyMap: dict[str, RuntimeServiceTypeHealthPolicy]


    class azure.mgmt.servicefabricmanagedclusters.types.RuntimeResumeApplicationUpgradeParameters(TypedDict, total=False):
        key "upgradeDomainName": str
        upgradeDomainName: str


    class azure.mgmt.servicefabricmanagedclusters.types.RuntimeRollingUpgradeUpdateMonitoringPolicy(TypedDict, total=False):
        key "failureAction": Union[str, RuntimeFailureAction]
        key "forceRestart": bool
        key "healthCheckRetryTimeoutInMilliseconds": str
        key "healthCheckStableDurationInMilliseconds": str
        key "healthCheckWaitDurationInMilliseconds": str
        key "instanceCloseDelayDurationInSeconds": int
        key "replicaSetCheckTimeoutInMilliseconds": int
        key "rollingUpgradeMode": Required[Union[str, RuntimeRollingUpgradeMode]]
        key "upgradeDomainTimeoutInMilliseconds": str
        key "upgradeTimeoutInMilliseconds": str
        failureAction: Union[str, RuntimeFailureAction]
        forceRestart: bool
        healthCheckRetryTimeoutInMilliseconds: str
        healthCheckStableDurationInMilliseconds: str
        healthCheckWaitDurationInMilliseconds: str
        instanceCloseDelayDurationInSeconds: int
        replicaSetCheckTimeoutInMilliseconds: int
        rollingUpgradeMode: Union[str, RuntimeRollingUpgradeMode]
        upgradeDomainTimeoutInMilliseconds: str
        upgradeTimeoutInMilliseconds: str


    class azure.mgmt.servicefabricmanagedclusters.types.RuntimeServiceTypeHealthPolicy(TypedDict, total=False):
        key "maxPercentUnhealthyPartitionsPerService": Required[int]
        key "maxPercentUnhealthyReplicasPerPartition": Required[int]
        key "maxPercentUnhealthyServices": Required[int]
        maxPercentUnhealthyPartitionsPerService: int
        maxPercentUnhealthyReplicasPerPartition: int
        maxPercentUnhealthyServices: int


    class azure.mgmt.servicefabricmanagedclusters.types.RuntimeUpdateApplicationUpgradeParameters(TypedDict, total=False):
        key "applicationHealthPolicy": ForwardRef('RuntimeApplicationHealthPolicy', module='types')
        key "name": Required[str]
        key "updateDescription": ForwardRef('RuntimeRollingUpgradeUpdateMonitoringPolicy', module='types')
        key "upgradeKind": Required[Union[str, RuntimeUpgradeKind]]
        applicationHealthPolicy: RuntimeApplicationHealthPolicy
        name: str
        updateDescription: RuntimeRollingUpgradeUpdateMonitoringPolicy
        upgradeKind: Union[str, RuntimeUpgradeKind]


    class azure.mgmt.servicefabricmanagedclusters.types.ScaleInPolicy(TypedDict, total=False):
        key "mode": Union[str, ScaleInPolicyMode]
        mode: Union[str, ScaleInPolicyMode]


    class azure.mgmt.servicefabricmanagedclusters.types.ScalingPolicy(TypedDict, total=False):
        key "scalingMechanism": Required[ScalingMechanism]
        key "scalingTrigger": Required[ScalingTrigger]
        scalingMechanism: ScalingMechanism
        scalingTrigger: ScalingTrigger


    class azure.mgmt.servicefabricmanagedclusters.types.ServiceCorrelation(TypedDict, total=False):
        key "scheme": Required[Union[str, ServiceCorrelationScheme]]
        key "serviceName": Required[str]
        scheme: Union[str, ServiceCorrelationScheme]
        serviceName: str


    class azure.mgmt.servicefabricmanagedclusters.types.ServiceEndpoint(TypedDict, total=False):
        key "networkIdentifier": str
        key "service": Required[str]
        locations: list[str]
        networkIdentifier: str
        service: str


    class azure.mgmt.servicefabricmanagedclusters.types.ServiceKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        STATEFUL = "Stateful"
        STATELESS = "Stateless"


    class azure.mgmt.servicefabricmanagedclusters.types.ServiceLoadMetric(TypedDict, total=False):
        key "defaultLoad": int
        key "name": Required[str]
        key "primaryDefaultLoad": int
        key "secondaryDefaultLoad": int
        key "weight": Union[str, ServiceLoadMetricWeight]
        defaultLoad: int
        name: str
        primaryDefaultLoad: int
        secondaryDefaultLoad: int
        weight: Union[str, ServiceLoadMetricWeight]


    class azure.mgmt.servicefabricmanagedclusters.types.ServicePlacementInvalidDomainPolicy(TypedDict, total=False):
        key "domainName": Required[str]
        key "type": Required[Literal[ServicePlacementPolicyType.INVALID_DOMAIN]]
        domainName: str
        type: Literal[ServicePlacementPolicyType.INVALID_DOMAIN]


    class azure.mgmt.servicefabricmanagedclusters.types.ServicePlacementNonPartiallyPlaceServicePolicy(TypedDict, total=False):
        key "type": Required[Literal[ServicePlacementPolicyType.NON_PARTIALLY_PLACE_SERVICE]]
        type: Literal[ServicePlacementPolicyType.NON_PARTIALLY_PLACE_SERVICE]


    class azure.mgmt.servicefabricmanagedclusters.types.ServicePlacementPolicyType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INVALID_DOMAIN = "InvalidDomain"
        NON_PARTIALLY_PLACE_SERVICE = "NonPartiallyPlaceService"
        PREFERRED_PRIMARY_DOMAIN = "PreferredPrimaryDomain"
        REQUIRED_DOMAIN = "RequiredDomain"
        REQUIRED_DOMAIN_DISTRIBUTION = "RequiredDomainDistribution"


    class azure.mgmt.servicefabricmanagedclusters.types.ServicePlacementPreferPrimaryDomainPolicy(TypedDict, total=False):
        key "domainName": Required[str]
        key "type": Required[Literal[ServicePlacementPolicyType.PREFERRED_PRIMARY_DOMAIN]]
        domainName: str
        type: Literal[ServicePlacementPolicyType.PREFERRED_PRIMARY_DOMAIN]


    class azure.mgmt.servicefabricmanagedclusters.types.ServicePlacementRequireDomainDistributionPolicy(TypedDict, total=False):
        key "domainName": Required[str]
        key "type": Required[Literal[ServicePlacementPolicyType.REQUIRED_DOMAIN_DISTRIBUTION]]
        domainName: str
        type: Literal[ServicePlacementPolicyType.REQUIRED_DOMAIN_DISTRIBUTION]


    class azure.mgmt.servicefabricmanagedclusters.types.ServicePlacementRequiredDomainPolicy(TypedDict, total=False):
        key "domainName": Required[str]
        key "type": Required[Literal[ServicePlacementPolicyType.REQUIRED_DOMAIN]]
        domainName: str
        type: Literal[ServicePlacementPolicyType.REQUIRED_DOMAIN]


    class azure.mgmt.servicefabricmanagedclusters.types.ServiceResource(ProxyResource):
        key "id": str
        key "location": str
        key "name": str
        key "properties": ForwardRef('ServiceResourceProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: ServiceResourceProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.servicefabricmanagedclusters.types.ServiceResourcePropertiesBase(TypedDict, total=False):
        key "defaultMoveCost": Union[str, MoveCost]
        key "placementConstraints": str
        correlationScheme: list[ServiceCorrelation]
        defaultMoveCost: Union[str, MoveCost]
        placementConstraints: str
        scalingPolicies: list[ScalingPolicy]
        serviceLoadMetrics: list[ServiceLoadMetric]
        servicePlacementPolicies: list[ServicePlacementPolicy]


    class azure.mgmt.servicefabricmanagedclusters.types.ServiceScalingMechanismKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ADD_REMOVE_INCREMENTAL_NAMED_PARTITION = "AddRemoveIncrementalNamedPartition"
        SCALE_PARTITION_INSTANCE_COUNT = "ScalePartitionInstanceCount"


    class azure.mgmt.servicefabricmanagedclusters.types.ServiceScalingTriggerKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVERAGE_PARTITION_LOAD_TRIGGER = "AveragePartitionLoadTrigger"
        AVERAGE_SERVICE_LOAD_TRIGGER = "AverageServiceLoadTrigger"


    class azure.mgmt.servicefabricmanagedclusters.types.ServiceTypeHealthPolicy(TypedDict, total=False):
        key "maxPercentUnhealthyPartitionsPerService": Required[int]
        key "maxPercentUnhealthyReplicasPerPartition": Required[int]
        key "maxPercentUnhealthyServices": Required[int]
        maxPercentUnhealthyPartitionsPerService: int
        maxPercentUnhealthyReplicasPerPartition: int
        maxPercentUnhealthyServices: int


    class azure.mgmt.servicefabricmanagedclusters.types.ServiceUpdateParameters(TypedDict, total=False):
        tags: dict[str, str]


    class azure.mgmt.servicefabricmanagedclusters.types.SettingsParameterDescription(TypedDict, total=False):
        key "name": Required[str]
        key "value": Required[str]
        name: str
        value: str


    class azure.mgmt.servicefabricmanagedclusters.types.SettingsSectionDescription(TypedDict, total=False):
        key "name": Required[str]
        key "parameters": Required[list[SettingsParameterDescription]]
        name: str
        parameters: list[SettingsParameterDescription]


    class azure.mgmt.servicefabricmanagedclusters.types.SingletonPartitionScheme(TypedDict, total=False):
        key "partitionScheme": Required[Literal[PartitionScheme.SINGLETON]]
        partitionScheme: Literal[PartitionScheme.SINGLETON]


    class azure.mgmt.servicefabricmanagedclusters.types.Sku(TypedDict, total=False):
        key "name": Required[Union[str, SkuName]]
        name: Union[str, SkuName]


    class azure.mgmt.servicefabricmanagedclusters.types.StatefulServiceProperties(TypedDict, total=False):
        key "defaultMoveCost": Union[str, MoveCost]
        key "hasPersistedState": bool
        key "minReplicaSetSize": int
        key "partitionDescription": Required[Partition]
        key "placementConstraints": str
        key "provisioningState": str
        key "quorumLossWaitDuration": str
        key "replicaRestartWaitDuration": str
        key "serviceDnsName": str
        key "serviceKind": Required[Literal[ServiceKind.STATEFUL]]
        key "servicePackageActivationMode": Union[str, ServicePackageActivationMode]
        key "servicePlacementTimeLimit": str
        key "serviceTypeName": Required[str]
        key "standByReplicaKeepDuration": str
        key "targetReplicaSetSize": int
        correlationScheme: list[ServiceCorrelation]
        defaultMoveCost: Union[str, MoveCost]
        hasPersistedState: bool
        minReplicaSetSize: int
        partitionDescription: Partition
        placementConstraints: str
        provisioningState: str
        quorumLossWaitDuration: str
        replicaRestartWaitDuration: str
        scalingPolicies: list[ScalingPolicy]
        serviceDnsName: str
        serviceKind: Literal[ServiceKind.STATEFUL]
        serviceLoadMetrics: list[ServiceLoadMetric]
        servicePackageActivationMode: Union[str, ServicePackageActivationMode]
        servicePlacementPolicies: list[ServicePlacementPolicy]
        servicePlacementTimeLimit: str
        serviceTypeName: str
        standByReplicaKeepDuration: str
        targetReplicaSetSize: int


    class azure.mgmt.servicefabricmanagedclusters.types.StatelessServiceProperties(TypedDict, total=False):
        key "defaultMoveCost": Union[str, MoveCost]
        key "instanceCount": Required[int]
        key "minInstanceCount": int
        key "minInstancePercentage": int
        key "partitionDescription": Required[Partition]
        key "placementConstraints": str
        key "provisioningState": str
        key "serviceDnsName": str
        key "serviceKind": Required[Literal[ServiceKind.STATELESS]]
        key "servicePackageActivationMode": Union[str, ServicePackageActivationMode]
        key "serviceTypeName": Required[str]
        correlationScheme: list[ServiceCorrelation]
        defaultMoveCost: Union[str, MoveCost]
        instanceCount: int
        minInstanceCount: int
        minInstancePercentage: int
        partitionDescription: Partition
        placementConstraints: str
        provisioningState: str
        scalingPolicies: list[ScalingPolicy]
        serviceDnsName: str
        serviceKind: Literal[ServiceKind.STATELESS]
        serviceLoadMetrics: list[ServiceLoadMetric]
        servicePackageActivationMode: Union[str, ServicePackageActivationMode]
        servicePlacementPolicies: list[ServicePlacementPolicy]
        serviceTypeName: str


    class azure.mgmt.servicefabricmanagedclusters.types.SubResource(TypedDict, total=False):
        key "id": str
        id: str


    class azure.mgmt.servicefabricmanagedclusters.types.Subnet(TypedDict, total=False):
        key "enableIpv6": bool
        key "name": Required[str]
        key "networkSecurityGroupId": str
        key "privateEndpointNetworkPolicies": Union[str, PrivateEndpointNetworkPolicies]
        key "privateLinkServiceNetworkPolicies": Union[str, PrivateLinkServiceNetworkPolicies]
        enableIpv6: bool
        name: str
        networkSecurityGroupId: str
        privateEndpointNetworkPolicies: Union[str, PrivateEndpointNetworkPolicies]
        privateLinkServiceNetworkPolicies: Union[str, PrivateLinkServiceNetworkPolicies]


    class azure.mgmt.servicefabricmanagedclusters.types.SystemData(TypedDict, total=False):
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


    class azure.mgmt.servicefabricmanagedclusters.types.TrackedResource(Resource):
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


    class azure.mgmt.servicefabricmanagedclusters.types.UniformInt64RangePartitionScheme(TypedDict, total=False):
        key "count": Required[int]
        key "highKey": Required[int]
        key "lowKey": Required[int]
        key "partitionScheme": Required[Literal[PartitionScheme.UNIFORM_INT64_RANGE]]
        count: int
        highKey: int
        lowKey: int
        partitionScheme: Literal[PartitionScheme.UNIFORM_INT64_RANGE]


    class azure.mgmt.servicefabricmanagedclusters.types.UserAssignedIdentity(TypedDict, total=False):
        key "clientId": str
        key "principalId": str
        clientId: str
        principalId: str


    class azure.mgmt.servicefabricmanagedclusters.types.VMSSExtension(TypedDict, total=False):
        key "name": Required[str]
        key "properties": Required[VMSSExtensionProperties]
        name: str
        properties: VMSSExtensionProperties


    class azure.mgmt.servicefabricmanagedclusters.types.VMSSExtensionProperties(TypedDict, total=False):
        key "autoUpgradeMinorVersion": bool
        key "enableAutomaticUpgrade": bool
        key "forceUpdateTag": str
        key "protectedSettings": Any
        key "provisioningState": str
        key "publisher": Required[str]
        key "settings": Any
        key "type": Required[str]
        key "typeHandlerVersion": Required[str]
        autoUpgradeMinorVersion: bool
        enableAutomaticUpgrade: bool
        forceUpdateTag: str
        protectedSettings: Any
        provisionAfterExtensions: list[str]
        provisioningState: str
        publisher: str
        settings: Any
        setupOrder: list[Union[str, VmssExtensionSetupOrder]]
        type: str
        typeHandlerVersion: str


    class azure.mgmt.servicefabricmanagedclusters.types.VaultCertificate(TypedDict, total=False):
        key "certificateStore": Required[str]
        key "certificateUrl": Required[str]
        certificateStore: str
        certificateUrl: str


    class azure.mgmt.servicefabricmanagedclusters.types.VaultSecretGroup(TypedDict, total=False):
        key "sourceVault": Required[SubResource]
        key "vaultCertificates": Required[list[VaultCertificate]]
        sourceVault: SubResource
        vaultCertificates: list[VaultCertificate]


    class azure.mgmt.servicefabricmanagedclusters.types.VmApplication(TypedDict, total=False):
        key "configurationReference": str
        key "enableAutomaticUpgrade": bool
        key "order": int
        key "packageReferenceId": Required[str]
        key "treatFailureAsDeploymentFailure": bool
        key "vmGalleryTags": str
        configurationReference: str
        enableAutomaticUpgrade: bool
        order: int
        packageReferenceId: str
        treatFailureAsDeploymentFailure: bool
        vmGalleryTags: str


    class azure.mgmt.servicefabricmanagedclusters.types.VmImagePlan(TypedDict, total=False):
        key "name": str
        key "product": str
        key "promotionCode": str
        key "publisher": str
        name: str
        product: str
        promotionCode: str
        publisher: str


    class azure.mgmt.servicefabricmanagedclusters.types.VmManagedIdentity(TypedDict, total=False):
        userAssignedIdentities: list[str]


    class azure.mgmt.servicefabricmanagedclusters.types.VmssDataDisk(TypedDict, total=False):
        key "diskLetter": Required[str]
        key "diskSizeGB": Required[int]
        key "diskType": Required[Union[str, DiskType]]
        key "lun": Required[int]
        diskLetter: str
        diskSizeGB: int
        diskType: Union[str, DiskType]
        lun: int


    class azure.mgmt.servicefabricmanagedclusters.types.ZoneFaultSimulationContent(TypedDict, total=False):
        key "constraints": ForwardRef('FaultSimulationConstraints', module='types')
        key "faultKind": Required[Literal[FaultKind.ZONE]]
        key "force": bool
        constraints: FaultSimulationConstraints
        faultKind: Literal[FaultKind.ZONE]
        force: bool
        zones: list[str]


```