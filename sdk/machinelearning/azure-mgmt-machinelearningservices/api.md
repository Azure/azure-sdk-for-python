```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.machinelearningservices

    class azure.mgmt.machinelearningservices.MachineLearningServicesMgmtClient: implements ContextManager 
        batch_deployments: BatchDeploymentsOperations
        batch_endpoints: BatchEndpointsOperations
        code_containers: CodeContainersOperations
        code_versions: CodeVersionsOperations
        component_containers: ComponentContainersOperations
        component_versions: ComponentVersionsOperations
        compute: ComputeOperations
        data_containers: DataContainersOperations
        data_versions: DataVersionsOperations
        datastores: DatastoresOperations
        environment_containers: EnvironmentContainersOperations
        environment_versions: EnvironmentVersionsOperations
        jobs: JobsOperations
        model_containers: ModelContainersOperations
        model_versions: ModelVersionsOperations
        online_deployments: OnlineDeploymentsOperations
        online_endpoints: OnlineEndpointsOperations
        operations: Operations
        private_endpoint_connections: PrivateEndpointConnectionsOperations
        private_link_resources: PrivateLinkResourcesOperations
        quotas: QuotasOperations
        registries: RegistriesOperations
        registry_code_containers: RegistryCodeContainersOperations
        registry_code_versions: RegistryCodeVersionsOperations
        registry_component_containers: RegistryComponentContainersOperations
        registry_component_versions: RegistryComponentVersionsOperations
        registry_data_containers: RegistryDataContainersOperations
        registry_data_versions: RegistryDataVersionsOperations
        registry_environment_containers: RegistryEnvironmentContainersOperations
        registry_environment_versions: RegistryEnvironmentVersionsOperations
        registry_model_containers: RegistryModelContainersOperations
        registry_model_versions: RegistryModelVersionsOperations
        schedules: SchedulesOperations
        usages: UsagesOperations
        virtual_machine_sizes: VirtualMachineSizesOperations
        workspace_connections: WorkspaceConnectionsOperations
        workspace_features: WorkspaceFeaturesOperations
        workspaces: WorkspacesOperations

        def __init__(
                self, 
                credential: TokenCredential, 
                subscription_id: str, 
                base_url: str = "https://management.azure.com", 
                *, 
                api_version: str = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def close(self) -> None: ...


namespace azure.mgmt.machinelearningservices.aio

    class azure.mgmt.machinelearningservices.aio.MachineLearningServicesMgmtClient: implements AsyncContextManager 
        batch_deployments: BatchDeploymentsOperations
        batch_endpoints: BatchEndpointsOperations
        code_containers: CodeContainersOperations
        code_versions: CodeVersionsOperations
        component_containers: ComponentContainersOperations
        component_versions: ComponentVersionsOperations
        compute: ComputeOperations
        data_containers: DataContainersOperations
        data_versions: DataVersionsOperations
        datastores: DatastoresOperations
        environment_containers: EnvironmentContainersOperations
        environment_versions: EnvironmentVersionsOperations
        jobs: JobsOperations
        model_containers: ModelContainersOperations
        model_versions: ModelVersionsOperations
        online_deployments: OnlineDeploymentsOperations
        online_endpoints: OnlineEndpointsOperations
        operations: Operations
        private_endpoint_connections: PrivateEndpointConnectionsOperations
        private_link_resources: PrivateLinkResourcesOperations
        quotas: QuotasOperations
        registries: RegistriesOperations
        registry_code_containers: RegistryCodeContainersOperations
        registry_code_versions: RegistryCodeVersionsOperations
        registry_component_containers: RegistryComponentContainersOperations
        registry_component_versions: RegistryComponentVersionsOperations
        registry_data_containers: RegistryDataContainersOperations
        registry_data_versions: RegistryDataVersionsOperations
        registry_environment_containers: RegistryEnvironmentContainersOperations
        registry_environment_versions: RegistryEnvironmentVersionsOperations
        registry_model_containers: RegistryModelContainersOperations
        registry_model_versions: RegistryModelVersionsOperations
        schedules: SchedulesOperations
        usages: UsagesOperations
        virtual_machine_sizes: VirtualMachineSizesOperations
        workspace_connections: WorkspaceConnectionsOperations
        workspace_features: WorkspaceFeaturesOperations
        workspaces: WorkspacesOperations

        def __init__(
                self, 
                credential: AsyncTokenCredential, 
                subscription_id: str, 
                base_url: str = "https://management.azure.com", 
                *, 
                api_version: str = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        async def close(self) -> None: ...


namespace azure.mgmt.machinelearningservices.aio.operations

    class azure.mgmt.machinelearningservices.aio.operations.BatchDeploymentsOperations:

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
                endpoint_name: str, 
                deployment_name: str, 
                body: BatchDeployment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BatchDeployment]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                endpoint_name: str, 
                deployment_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BatchDeployment]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                endpoint_name: str, 
                deployment_name: str, 
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
                endpoint_name: str, 
                deployment_name: str, 
                body: PartialBatchDeploymentPartialMinimalTrackedResourceWithProperties, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BatchDeployment]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                endpoint_name: str, 
                deployment_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BatchDeployment]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                endpoint_name: str, 
                deployment_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> BatchDeployment: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                endpoint_name: str, 
                order_by: Optional[str] = None, 
                top: Optional[int] = None, 
                skip: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[BatchDeployment]: ...


    class azure.mgmt.machinelearningservices.aio.operations.BatchEndpointsOperations:

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
                endpoint_name: str, 
                body: BatchEndpoint, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BatchEndpoint]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                endpoint_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BatchEndpoint]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                endpoint_name: str, 
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
                endpoint_name: str, 
                body: PartialMinimalTrackedResourceWithIdentity, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BatchEndpoint]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                endpoint_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BatchEndpoint]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                endpoint_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> BatchEndpoint: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                count: Optional[int] = None, 
                skip: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[BatchEndpoint]: ...

        @distributed_trace_async
        async def list_keys(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                endpoint_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> EndpointAuthKeys: ...


    class azure.mgmt.machinelearningservices.aio.operations.CodeContainersOperations:

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
                name: str, 
                body: CodeContainer, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CodeContainer: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CodeContainer: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> CodeContainer: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                skip: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[CodeContainer]: ...


    class azure.mgmt.machinelearningservices.aio.operations.CodeVersionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_get_start_pending_upload(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                name: str, 
                version: str, 
                body: PendingUploadRequestDto, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PendingUploadResponseDto: ...

        @overload
        async def create_or_get_start_pending_upload(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                name: str, 
                version: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PendingUploadResponseDto: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                name: str, 
                version: str, 
                body: CodeVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CodeVersion: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                name: str, 
                version: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CodeVersion: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                name: str, 
                version: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                name: str, 
                version: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> CodeVersion: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                name: str, 
                order_by: Optional[str] = None, 
                top: Optional[int] = None, 
                skip: Optional[str] = None, 
                hash: Optional[str] = None, 
                hash_version: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[CodeVersion]: ...


    class azure.mgmt.machinelearningservices.aio.operations.ComponentContainersOperations:

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
                name: str, 
                body: ComponentContainer, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ComponentContainer: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ComponentContainer: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ComponentContainer: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                skip: Optional[str] = None, 
                list_view_type: Optional[Union[str, ListViewType]] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[ComponentContainer]: ...


    class azure.mgmt.machinelearningservices.aio.operations.ComponentVersionsOperations:

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
                name: str, 
                version: str, 
                body: ComponentVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ComponentVersion: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                name: str, 
                version: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ComponentVersion: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                name: str, 
                version: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                name: str, 
                version: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ComponentVersion: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                name: str, 
                order_by: Optional[str] = None, 
                top: Optional[int] = None, 
                skip: Optional[str] = None, 
                list_view_type: Optional[Union[str, ListViewType]] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[ComponentVersion]: ...


    class azure.mgmt.machinelearningservices.aio.operations.ComputeOperations:

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
                compute_name: str, 
                parameters: ComputeResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ComputeResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                compute_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ComputeResource]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                compute_name: str, 
                underlying_resource_action: Union[str, UnderlyingResourceAction], 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_restart(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                compute_name: str, 
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
                compute_name: str, 
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
                resource_group_name: str, 
                workspace_name: str, 
                compute_name: str, 
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
                compute_name: str, 
                parameters: ClusterUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ComputeResource]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                compute_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ComputeResource]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                compute_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ComputeResource: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                skip: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[ComputeResource]: ...

        @distributed_trace_async
        async def list_keys(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                compute_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ComputeSecrets: ...

        @distributed_trace
        def list_nodes(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                compute_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[AmlComputeNodeInformation]: ...


    class azure.mgmt.machinelearningservices.aio.operations.DataContainersOperations:

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
                name: str, 
                body: DataContainer, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DataContainer: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DataContainer: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> DataContainer: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                skip: Optional[str] = None, 
                list_view_type: Optional[Union[str, ListViewType]] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[DataContainer]: ...


    class azure.mgmt.machinelearningservices.aio.operations.DataVersionsOperations:

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
                name: str, 
                version: str, 
                body: DataVersionBase, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DataVersionBase: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                name: str, 
                version: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DataVersionBase: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                name: str, 
                version: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                name: str, 
                version: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> DataVersionBase: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                name: str, 
                order_by: Optional[str] = None, 
                top: Optional[int] = None, 
                skip: Optional[str] = None, 
                tags: Optional[str] = None, 
                list_view_type: Optional[Union[str, ListViewType]] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[DataVersionBase]: ...


    class azure.mgmt.machinelearningservices.aio.operations.DatastoresOperations:

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
                name: str, 
                body: Datastore, 
                skip_validation: bool = False, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Datastore: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                name: str, 
                body: IO, 
                skip_validation: bool = False, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Datastore: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Datastore: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                skip: Optional[str] = None, 
                count: int = 30, 
                is_default: Optional[bool] = None, 
                names: Optional[List[str]] = None, 
                search_text: Optional[str] = None, 
                order_by: Optional[str] = None, 
                order_by_asc: bool = False, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[Datastore]: ...

        @distributed_trace_async
        async def list_secrets(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> DatastoreSecrets: ...


    class azure.mgmt.machinelearningservices.aio.operations.EnvironmentContainersOperations:

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
                name: str, 
                body: EnvironmentContainer, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EnvironmentContainer: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EnvironmentContainer: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> EnvironmentContainer: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                skip: Optional[str] = None, 
                list_view_type: Optional[Union[str, ListViewType]] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[EnvironmentContainer]: ...


    class azure.mgmt.machinelearningservices.aio.operations.EnvironmentVersionsOperations:

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
                name: str, 
                version: str, 
                body: EnvironmentVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EnvironmentVersion: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                name: str, 
                version: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EnvironmentVersion: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                name: str, 
                version: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                name: str, 
                version: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> EnvironmentVersion: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                name: str, 
                order_by: Optional[str] = None, 
                top: Optional[int] = None, 
                skip: Optional[str] = None, 
                list_view_type: Optional[Union[str, ListViewType]] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[EnvironmentVersion]: ...


    class azure.mgmt.machinelearningservices.aio.operations.JobsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_cancel(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                id: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                id: str, 
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
                workspace_name: str, 
                id: str, 
                body: JobBase, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JobBase: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                id: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JobBase: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> JobBase: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                skip: Optional[str] = None, 
                job_type: Optional[str] = None, 
                tag: Optional[str] = None, 
                list_view_type: Optional[Union[str, ListViewType]] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[JobBase]: ...


    class azure.mgmt.machinelearningservices.aio.operations.ModelContainersOperations:

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
                name: str, 
                body: ModelContainer, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ModelContainer: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ModelContainer: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ModelContainer: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                skip: Optional[str] = None, 
                count: Optional[int] = None, 
                list_view_type: Optional[Union[str, ListViewType]] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[ModelContainer]: ...


    class azure.mgmt.machinelearningservices.aio.operations.ModelVersionsOperations:

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
                name: str, 
                version: str, 
                body: ModelVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ModelVersion: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                name: str, 
                version: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ModelVersion: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                name: str, 
                version: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                name: str, 
                version: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ModelVersion: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                name: str, 
                skip: Optional[str] = None, 
                order_by: Optional[str] = None, 
                top: Optional[int] = None, 
                version: Optional[str] = None, 
                description: Optional[str] = None, 
                offset: Optional[int] = None, 
                tags: Optional[str] = None, 
                properties: Optional[str] = None, 
                feed: Optional[str] = None, 
                list_view_type: Optional[Union[str, ListViewType]] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[ModelVersion]: ...


    class azure.mgmt.machinelearningservices.aio.operations.OnlineDeploymentsOperations:

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
                endpoint_name: str, 
                deployment_name: str, 
                body: OnlineDeployment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OnlineDeployment]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                endpoint_name: str, 
                deployment_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OnlineDeployment]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                endpoint_name: str, 
                deployment_name: str, 
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
                endpoint_name: str, 
                deployment_name: str, 
                body: PartialMinimalTrackedResourceWithSku, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OnlineDeployment]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                endpoint_name: str, 
                deployment_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OnlineDeployment]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                endpoint_name: str, 
                deployment_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> OnlineDeployment: ...

        @overload
        async def get_logs(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                endpoint_name: str, 
                deployment_name: str, 
                body: DeploymentLogsRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DeploymentLogs: ...

        @overload
        async def get_logs(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                endpoint_name: str, 
                deployment_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DeploymentLogs: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                endpoint_name: str, 
                order_by: Optional[str] = None, 
                top: Optional[int] = None, 
                skip: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[OnlineDeployment]: ...

        @distributed_trace
        def list_skus(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                endpoint_name: str, 
                deployment_name: str, 
                count: Optional[int] = None, 
                skip: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[SkuResource]: ...


    class azure.mgmt.machinelearningservices.aio.operations.OnlineEndpointsOperations:

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
                endpoint_name: str, 
                body: OnlineEndpoint, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OnlineEndpoint]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                endpoint_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OnlineEndpoint]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                endpoint_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_regenerate_keys(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                endpoint_name: str, 
                body: RegenerateEndpointKeysRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_regenerate_keys(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                endpoint_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                endpoint_name: str, 
                body: PartialMinimalTrackedResourceWithIdentity, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OnlineEndpoint]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                endpoint_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OnlineEndpoint]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                endpoint_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> OnlineEndpoint: ...

        @distributed_trace_async
        async def get_token(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                endpoint_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> EndpointAuthToken: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                name: Optional[str] = None, 
                count: Optional[int] = None, 
                compute_type: Optional[Union[str, EndpointComputeType]] = None, 
                skip: Optional[str] = None, 
                tags: Optional[str] = None, 
                properties: Optional[str] = None, 
                order_by: Optional[Union[str, OrderString]] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[OnlineEndpoint]: ...

        @distributed_trace_async
        async def list_keys(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                endpoint_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> EndpointAuthKeys: ...


    class azure.mgmt.machinelearningservices.aio.operations.Operations:

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
            ) -> AsyncIterable[AmlOperation]: ...


    class azure.mgmt.machinelearningservices.aio.operations.PrivateEndpointConnectionsOperations:

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
                private_endpoint_connection_name: str, 
                properties: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                private_endpoint_connection_name: str, 
                properties: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                private_endpoint_connection_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

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


    class azure.mgmt.machinelearningservices.aio.operations.PrivateLinkResourcesOperations:

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
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> PrivateLinkResourceListResult: ...


    class azure.mgmt.machinelearningservices.aio.operations.QuotasOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                location: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[ResourceQuota]: ...

        @overload
        async def update(
                self, 
                location: str, 
                parameters: QuotaUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> UpdateWorkspaceQuotasResult: ...

        @overload
        async def update(
                self, 
                location: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> UpdateWorkspaceQuotasResult: ...


    class azure.mgmt.machinelearningservices.aio.operations.RegistriesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                body: Registry, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Registry]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Registry]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_remove_regions(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                body: Registry, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Registry]: ...

        @overload
        async def begin_remove_regions(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Registry]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Registry: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[Registry]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[Registry]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                body: PartialRegistryPartialTrackedResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Registry: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Registry: ...


    class azure.mgmt.machinelearningservices.aio.operations.RegistryCodeContainersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                code_name: str, 
                body: CodeContainer, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CodeContainer]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                code_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CodeContainer]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                code_name: str, 
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
                registry_name: str, 
                code_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> CodeContainer: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                skip: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[CodeContainer]: ...


    class azure.mgmt.machinelearningservices.aio.operations.RegistryCodeVersionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                code_name: str, 
                version: str, 
                body: CodeVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CodeVersion]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                code_name: str, 
                version: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CodeVersion]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                code_name: str, 
                version: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def create_or_get_start_pending_upload(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                code_name: str, 
                version: str, 
                body: PendingUploadRequestDto, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PendingUploadResponseDto: ...

        @overload
        async def create_or_get_start_pending_upload(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                code_name: str, 
                version: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PendingUploadResponseDto: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                code_name: str, 
                version: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> CodeVersion: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                code_name: str, 
                order_by: Optional[str] = None, 
                top: Optional[int] = None, 
                skip: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[CodeVersion]: ...


    class azure.mgmt.machinelearningservices.aio.operations.RegistryComponentContainersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                component_name: str, 
                body: ComponentContainer, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ComponentContainer]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                component_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ComponentContainer]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                component_name: str, 
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
                registry_name: str, 
                component_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ComponentContainer: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                skip: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[ComponentContainer]: ...


    class azure.mgmt.machinelearningservices.aio.operations.RegistryComponentVersionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                component_name: str, 
                version: str, 
                body: ComponentVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ComponentVersion]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                component_name: str, 
                version: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ComponentVersion]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                component_name: str, 
                version: str, 
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
                registry_name: str, 
                component_name: str, 
                version: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ComponentVersion: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                component_name: str, 
                order_by: Optional[str] = None, 
                top: Optional[int] = None, 
                skip: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[ComponentVersion]: ...


    class azure.mgmt.machinelearningservices.aio.operations.RegistryDataContainersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                name: str, 
                body: DataContainer, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DataContainer]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DataContainer]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                name: str, 
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
                registry_name: str, 
                name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> DataContainer: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                skip: Optional[str] = None, 
                list_view_type: Optional[Union[str, ListViewType]] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[DataContainer]: ...


    class azure.mgmt.machinelearningservices.aio.operations.RegistryDataVersionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                name: str, 
                version: str, 
                body: DataVersionBase, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DataVersionBase]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                name: str, 
                version: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DataVersionBase]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                name: str, 
                version: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def create_or_get_start_pending_upload(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                name: str, 
                version: str, 
                body: PendingUploadRequestDto, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PendingUploadResponseDto: ...

        @overload
        async def create_or_get_start_pending_upload(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                name: str, 
                version: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PendingUploadResponseDto: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                name: str, 
                version: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> DataVersionBase: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                name: str, 
                order_by: Optional[str] = None, 
                top: Optional[int] = None, 
                skip: Optional[str] = None, 
                tags: Optional[str] = None, 
                list_view_type: Optional[Union[str, ListViewType]] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[DataVersionBase]: ...


    class azure.mgmt.machinelearningservices.aio.operations.RegistryEnvironmentContainersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                environment_name: str, 
                body: EnvironmentContainer, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EnvironmentContainer]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                environment_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EnvironmentContainer]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                environment_name: str, 
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
                registry_name: str, 
                environment_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> EnvironmentContainer: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                skip: Optional[str] = None, 
                list_view_type: Optional[Union[str, ListViewType]] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[EnvironmentContainer]: ...


    class azure.mgmt.machinelearningservices.aio.operations.RegistryEnvironmentVersionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                environment_name: str, 
                version: str, 
                body: EnvironmentVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EnvironmentVersion]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                environment_name: str, 
                version: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EnvironmentVersion]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                environment_name: str, 
                version: str, 
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
                registry_name: str, 
                environment_name: str, 
                version: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> EnvironmentVersion: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                environment_name: str, 
                order_by: Optional[str] = None, 
                top: Optional[int] = None, 
                skip: Optional[str] = None, 
                list_view_type: Optional[Union[str, ListViewType]] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[EnvironmentVersion]: ...


    class azure.mgmt.machinelearningservices.aio.operations.RegistryModelContainersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                model_name: str, 
                body: ModelContainer, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ModelContainer]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                model_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ModelContainer]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                model_name: str, 
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
                registry_name: str, 
                model_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ModelContainer: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                skip: Optional[str] = None, 
                list_view_type: Optional[Union[str, ListViewType]] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[ModelContainer]: ...


    class azure.mgmt.machinelearningservices.aio.operations.RegistryModelVersionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                model_name: str, 
                version: str, 
                body: ModelVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ModelVersion]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                model_name: str, 
                version: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ModelVersion]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                model_name: str, 
                version: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def create_or_get_start_pending_upload(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                model_name: str, 
                version: str, 
                body: PendingUploadRequestDto, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PendingUploadResponseDto: ...

        @overload
        async def create_or_get_start_pending_upload(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                model_name: str, 
                version: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PendingUploadResponseDto: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                model_name: str, 
                version: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ModelVersion: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                model_name: str, 
                skip: Optional[str] = None, 
                order_by: Optional[str] = None, 
                top: Optional[int] = None, 
                version: Optional[str] = None, 
                description: Optional[str] = None, 
                tags: Optional[str] = None, 
                properties: Optional[str] = None, 
                list_view_type: Optional[Union[str, ListViewType]] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[ModelVersion]: ...


    class azure.mgmt.machinelearningservices.aio.operations.SchedulesOperations:

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
                name: str, 
                body: Schedule, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Schedule]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Schedule]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                name: str, 
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
                name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Schedule: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                skip: Optional[str] = None, 
                list_view_type: Optional[Union[str, ScheduleListViewType]] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[Schedule]: ...


    class azure.mgmt.machinelearningservices.aio.operations.UsagesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                location: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[Usage]: ...


    class azure.mgmt.machinelearningservices.aio.operations.VirtualMachineSizesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def list(
                self, 
                location: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> VirtualMachineSizeListResult: ...


    class azure.mgmt.machinelearningservices.aio.operations.WorkspaceConnectionsOperations:

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
                connection_name: str, 
                parameters: WorkspaceConnectionPropertiesV2BasicResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> WorkspaceConnectionPropertiesV2BasicResource: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                connection_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> WorkspaceConnectionPropertiesV2BasicResource: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                connection_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                connection_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> WorkspaceConnectionPropertiesV2BasicResource: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                target: Optional[str] = None, 
                category: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[WorkspaceConnectionPropertiesV2BasicResource]: ...


    class azure.mgmt.machinelearningservices.aio.operations.WorkspaceFeaturesOperations:

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
            ) -> AsyncIterable[AmlUserFeature]: ...


    class azure.mgmt.machinelearningservices.aio.operations.WorkspacesOperations:

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
                parameters: Workspace, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Workspace]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                parameters: IO, 
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
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_diagnose(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                parameters: Optional[DiagnoseWorkspaceParameters] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DiagnoseResponseResult]: ...

        @overload
        async def begin_diagnose(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                parameters: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DiagnoseResponseResult]: ...

        @distributed_trace_async
        async def begin_prepare_notebook(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[NotebookResourceInfo]: ...

        @distributed_trace_async
        async def begin_resync_keys(
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

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                parameters: WorkspaceUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Workspace]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                parameters: IO, 
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
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                skip: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[Workspace]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                skip: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[Workspace]: ...

        @distributed_trace_async
        async def list_keys(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ListWorkspaceKeysResult: ...

        @distributed_trace_async
        async def list_notebook_access_token(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> NotebookAccessTokenResult: ...

        @distributed_trace_async
        async def list_notebook_keys(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ListNotebookKeysResult: ...

        @distributed_trace_async
        async def list_outbound_network_dependencies_endpoints(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ExternalFQDNResponse: ...

        @distributed_trace_async
        async def list_storage_account_keys(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ListStorageAccountKeysResult: ...


namespace azure.mgmt.machinelearningservices.models

    class azure.mgmt.machinelearningservices.models.AKS(Compute, AKSSchema):
        compute_location: str
        compute_type: Union[str, ComputeType]
        created_on: datetime
        description: str
        disable_local_auth: bool
        is_attached_compute: bool
        modified_on: datetime
        properties: AKSSchemaProperties
        provisioning_errors: list[ErrorResponse]
        provisioning_state: Union[str, ProvisioningState]
        resource_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                compute_location: Optional[str] = ..., 
                description: Optional[str] = ..., 
                disable_local_auth: Optional[bool] = ..., 
                properties: Optional[AKSSchemaProperties] = ..., 
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


    class azure.mgmt.machinelearningservices.models.AKSSchema(Model):
        properties: AKSSchemaProperties

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[AKSSchemaProperties] = ..., 
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


    class azure.mgmt.machinelearningservices.models.AKSSchemaProperties(Model):
        agent_count: int
        agent_vm_size: str
        aks_networking_configuration: AksNetworkingConfiguration
        cluster_fqdn: str
        cluster_purpose: Union[str, ClusterPurpose]
        load_balancer_subnet: str
        load_balancer_type: Union[str, LoadBalancerType]
        ssl_configuration: SslConfiguration
        system_services: list[SystemService]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                agent_count: Optional[int] = ..., 
                agent_vm_size: Optional[str] = ..., 
                aks_networking_configuration: Optional[AksNetworkingConfiguration] = ..., 
                cluster_fqdn: Optional[str] = ..., 
                cluster_purpose: Union[str, ClusterPurpose] = "FastProd", 
                load_balancer_subnet: Optional[str] = ..., 
                load_balancer_type: Union[str, LoadBalancerType] = "PublicIp", 
                ssl_configuration: Optional[SslConfiguration] = ..., 
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


    class azure.mgmt.machinelearningservices.models.AccountKeyDatastoreCredentials(DatastoreCredentials):
        credentials_type: Union[str, CredentialsType]
        secrets: AccountKeyDatastoreSecrets

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                secrets: AccountKeyDatastoreSecrets, 
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


    class azure.mgmt.machinelearningservices.models.AccountKeyDatastoreSecrets(DatastoreSecrets):
        key: str
        secrets_type: Union[str, SecretsType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                key: Optional[str] = ..., 
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


    class azure.mgmt.machinelearningservices.models.AcrDetails(Model):
        system_created_acr_account: SystemCreatedAcrAccount
        user_created_acr_account: UserCreatedAcrAccount

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                system_created_acr_account: Optional[SystemCreatedAcrAccount] = ..., 
                user_created_acr_account: Optional[UserCreatedAcrAccount] = ..., 
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


    class azure.mgmt.machinelearningservices.models.AksComputeSecrets(ComputeSecrets, AksComputeSecretsProperties):
        admin_kube_config: str
        compute_type: Union[str, ComputeType]
        image_pull_secret_name: str
        user_kube_config: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                admin_kube_config: Optional[str] = ..., 
                image_pull_secret_name: Optional[str] = ..., 
                user_kube_config: Optional[str] = ..., 
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


    class azure.mgmt.machinelearningservices.models.AksComputeSecretsProperties(Model):
        admin_kube_config: str
        image_pull_secret_name: str
        user_kube_config: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                admin_kube_config: Optional[str] = ..., 
                image_pull_secret_name: Optional[str] = ..., 
                user_kube_config: Optional[str] = ..., 
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


    class azure.mgmt.machinelearningservices.models.AksNetworkingConfiguration(Model):
        dns_service_ip: str
        docker_bridge_cidr: str
        service_cidr: str
        subnet_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                dns_service_ip: Optional[str] = ..., 
                docker_bridge_cidr: Optional[str] = ..., 
                service_cidr: Optional[str] = ..., 
                subnet_id: Optional[str] = ..., 
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


    class azure.mgmt.machinelearningservices.models.AllNodes(Nodes):
        nodes_value_type: Union[str, NodesValueType]

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


    class azure.mgmt.machinelearningservices.models.AllocationState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        RESIZING = "Resizing"
        STEADY = "Steady"


    class azure.mgmt.machinelearningservices.models.AmlCompute(Compute, AmlComputeSchema):
        compute_location: str
        compute_type: Union[str, ComputeType]
        created_on: datetime
        description: str
        disable_local_auth: bool
        is_attached_compute: bool
        modified_on: datetime
        properties: AmlComputeProperties
        provisioning_errors: list[ErrorResponse]
        provisioning_state: Union[str, ProvisioningState]
        resource_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                compute_location: Optional[str] = ..., 
                description: Optional[str] = ..., 
                disable_local_auth: Optional[bool] = ..., 
                properties: Optional[AmlComputeProperties] = ..., 
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


    class azure.mgmt.machinelearningservices.models.AmlComputeNodeInformation(Model):
        node_id: str
        node_state: Union[str, NodeState]
        port: int
        private_ip_address: str
        public_ip_address: str
        run_id: str

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


    class azure.mgmt.machinelearningservices.models.AmlComputeNodesInformation(Model):
        next_link: str
        nodes: list[AmlComputeNodeInformation]

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


    class azure.mgmt.machinelearningservices.models.AmlComputeProperties(Model):
        allocation_state: Union[str, AllocationState]
        allocation_state_transition_time: datetime
        current_node_count: int
        enable_node_public_ip: bool
        errors: list[ErrorResponse]
        isolated_network: bool
        node_state_counts: NodeStateCounts
        os_type: Union[str, OsType]
        property_bag: JSON
        remote_login_port_public_access: Union[str, RemoteLoginPortPublicAccess]
        scale_settings: ScaleSettings
        subnet: ResourceId
        target_node_count: int
        user_account_credentials: UserAccountCredentials
        virtual_machine_image: VirtualMachineImage
        vm_priority: Union[str, VmPriority]
        vm_size: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                enable_node_public_ip: bool = True, 
                isolated_network: Optional[bool] = ..., 
                os_type: Union[str, OsType] = "Linux", 
                property_bag: Optional[JSON] = ..., 
                remote_login_port_public_access: Union[str, RemoteLoginPortPublicAccess] = "NotSpecified", 
                scale_settings: Optional[ScaleSettings] = ..., 
                subnet: Optional[ResourceId] = ..., 
                user_account_credentials: Optional[UserAccountCredentials] = ..., 
                virtual_machine_image: Optional[VirtualMachineImage] = ..., 
                vm_priority: Optional[Union[str, VmPriority]] = ..., 
                vm_size: Optional[str] = ..., 
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


    class azure.mgmt.machinelearningservices.models.AmlComputeSchema(Model):
        properties: AmlComputeProperties

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[AmlComputeProperties] = ..., 
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


    class azure.mgmt.machinelearningservices.models.AmlOperation(Model):
        display: AmlOperationDisplay
        is_data_action: bool
        name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                display: Optional[AmlOperationDisplay] = ..., 
                is_data_action: Optional[bool] = ..., 
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


    class azure.mgmt.machinelearningservices.models.AmlOperationDisplay(Model):
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


    class azure.mgmt.machinelearningservices.models.AmlOperationListResult(Model):
        value: list[AmlOperation]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[AmlOperation]] = ..., 
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


    class azure.mgmt.machinelearningservices.models.AmlToken(IdentityConfiguration):
        identity_type: Union[str, IdentityConfigurationType]

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


    class azure.mgmt.machinelearningservices.models.AmlUserFeature(Model):
        description: str
        display_name: str
        id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                id: Optional[str] = ..., 
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


    class azure.mgmt.machinelearningservices.models.ApplicationSharingPolicy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PERSONAL = "Personal"
        SHARED = "Shared"


    class azure.mgmt.machinelearningservices.models.ArmResourceId(Model):
        resource_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
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


    class azure.mgmt.machinelearningservices.models.AssetBase(ResourceBase):
        description: str
        is_anonymous: bool
        is_archived: bool
        properties: dict[str, str]
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                is_anonymous: bool = False, 
                is_archived: bool = False, 
                properties: Optional[Dict[str, str]] = ..., 
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


    class azure.mgmt.machinelearningservices.models.AssetContainer(ResourceBase):
        description: str
        is_archived: bool
        latest_version: str
        next_version: str
        properties: dict[str, str]
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                is_archived: bool = False, 
                properties: Optional[Dict[str, str]] = ..., 
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


    class azure.mgmt.machinelearningservices.models.AssetJobInput(Model):
        mode: Union[str, InputDeliveryMode]
        uri: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                mode: Optional[Union[str, InputDeliveryMode]] = ..., 
                uri: str, 
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


    class azure.mgmt.machinelearningservices.models.AssetJobOutput(Model):
        mode: Union[str, OutputDeliveryMode]
        uri: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                mode: Optional[Union[str, OutputDeliveryMode]] = ..., 
                uri: Optional[str] = ..., 
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


    class azure.mgmt.machinelearningservices.models.AssetProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.machinelearningservices.models.AssetReferenceBase(Model):
        reference_type: Union[str, ReferenceType]

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


    class azure.mgmt.machinelearningservices.models.AssignedUser(Model):
        object_id: str
        tenant_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                object_id: str, 
                tenant_id: str, 
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


    class azure.mgmt.machinelearningservices.models.AutoForecastHorizon(ForecastHorizon):
        mode: Union[str, ForecastHorizonMode]

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


    class azure.mgmt.machinelearningservices.models.AutoMLJob(JobBaseProperties):
        component_id: str
        compute_id: str
        description: str
        display_name: str
        environment_id: str
        environment_variables: dict[str, str]
        experiment_name: str
        identity: IdentityConfiguration
        is_archived: bool
        job_type: Union[str, JobType]
        outputs: dict[str, JobOutput]
        properties: dict[str, str]
        resources: JobResourceConfiguration
        services: dict[str, JobService]
        status: Union[str, JobStatus]
        tags: dict[str, str]
        task_details: AutoMLVertical

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                component_id: Optional[str] = ..., 
                compute_id: Optional[str] = ..., 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                environment_id: Optional[str] = ..., 
                environment_variables: Optional[Dict[str, str]] = ..., 
                experiment_name: str = "Default", 
                identity: Optional[IdentityConfiguration] = ..., 
                is_archived: bool = False, 
                outputs: Optional[Dict[str, JobOutput]] = ..., 
                properties: Optional[Dict[str, str]] = ..., 
                resources: Optional[JobResourceConfiguration] = ..., 
                services: Optional[Dict[str, JobService]] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                task_details: AutoMLVertical, 
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


    class azure.mgmt.machinelearningservices.models.AutoMLVertical(Model):
        log_verbosity: Union[str, LogVerbosity]
        target_column_name: str
        task_type: Union[str, TaskType]
        training_data: MLTableJobInput

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                log_verbosity: Optional[Union[str, LogVerbosity]] = ..., 
                target_column_name: Optional[str] = ..., 
                training_data: MLTableJobInput, 
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


    class azure.mgmt.machinelearningservices.models.AutoNCrossValidations(NCrossValidations):
        mode: Union[str, NCrossValidationsMode]

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


    class azure.mgmt.machinelearningservices.models.AutoPauseProperties(Model):
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


    class azure.mgmt.machinelearningservices.models.AutoRebuildSetting(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ON_BASE_IMAGE_UPDATE = "OnBaseImageUpdate"


    class azure.mgmt.machinelearningservices.models.AutoScaleProperties(Model):
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


    class azure.mgmt.machinelearningservices.models.AutoSeasonality(Seasonality):
        mode: Union[str, SeasonalityMode]

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


    class azure.mgmt.machinelearningservices.models.AutoTargetLags(TargetLags):
        mode: Union[str, TargetLagsMode]

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


    class azure.mgmt.machinelearningservices.models.AutoTargetRollingWindowSize(TargetRollingWindowSize):
        mode: Union[str, TargetRollingWindowSizeMode]

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


    class azure.mgmt.machinelearningservices.models.Autosave(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LOCAL = "Local"
        NONE = "None"
        REMOTE = "Remote"


    class azure.mgmt.machinelearningservices.models.AzureBlobDatastore(DatastoreProperties):
        account_name: str
        container_name: str
        credentials: DatastoreCredentials
        datastore_type: Union[str, DatastoreType]
        description: str
        endpoint: str
        is_default: bool
        properties: dict[str, str]
        protocol: str
        service_data_access_auth_identity: Union[str, ServiceDataAccessAuthIdentity]
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                account_name: Optional[str] = ..., 
                container_name: Optional[str] = ..., 
                credentials: DatastoreCredentials, 
                description: Optional[str] = ..., 
                endpoint: Optional[str] = ..., 
                properties: Optional[Dict[str, str]] = ..., 
                protocol: Optional[str] = ..., 
                service_data_access_auth_identity: Optional[Union[str, ServiceDataAccessAuthIdentity]] = ..., 
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


    class azure.mgmt.machinelearningservices.models.AzureDataLakeGen1Datastore(DatastoreProperties):
        credentials: DatastoreCredentials
        datastore_type: Union[str, DatastoreType]
        description: str
        is_default: bool
        properties: dict[str, str]
        service_data_access_auth_identity: Union[str, ServiceDataAccessAuthIdentity]
        store_name: str
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                credentials: DatastoreCredentials, 
                description: Optional[str] = ..., 
                properties: Optional[Dict[str, str]] = ..., 
                service_data_access_auth_identity: Optional[Union[str, ServiceDataAccessAuthIdentity]] = ..., 
                store_name: str, 
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


    class azure.mgmt.machinelearningservices.models.AzureDataLakeGen2Datastore(DatastoreProperties):
        account_name: str
        credentials: DatastoreCredentials
        datastore_type: Union[str, DatastoreType]
        description: str
        endpoint: str
        filesystem: str
        is_default: bool
        properties: dict[str, str]
        protocol: str
        service_data_access_auth_identity: Union[str, ServiceDataAccessAuthIdentity]
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                account_name: str, 
                credentials: DatastoreCredentials, 
                description: Optional[str] = ..., 
                endpoint: Optional[str] = ..., 
                filesystem: str, 
                properties: Optional[Dict[str, str]] = ..., 
                protocol: Optional[str] = ..., 
                service_data_access_auth_identity: Optional[Union[str, ServiceDataAccessAuthIdentity]] = ..., 
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


    class azure.mgmt.machinelearningservices.models.AzureFileDatastore(DatastoreProperties):
        account_name: str
        credentials: DatastoreCredentials
        datastore_type: Union[str, DatastoreType]
        description: str
        endpoint: str
        file_share_name: str
        is_default: bool
        properties: dict[str, str]
        protocol: str
        service_data_access_auth_identity: Union[str, ServiceDataAccessAuthIdentity]
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                account_name: str, 
                credentials: DatastoreCredentials, 
                description: Optional[str] = ..., 
                endpoint: Optional[str] = ..., 
                file_share_name: str, 
                properties: Optional[Dict[str, str]] = ..., 
                protocol: Optional[str] = ..., 
                service_data_access_auth_identity: Optional[Union[str, ServiceDataAccessAuthIdentity]] = ..., 
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


    class azure.mgmt.machinelearningservices.models.BanditPolicy(EarlyTerminationPolicy):
        delay_evaluation: int
        evaluation_interval: int
        policy_type: Union[str, EarlyTerminationPolicyType]
        slack_amount: float
        slack_factor: float

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                delay_evaluation: int = 0, 
                evaluation_interval: int = 0, 
                slack_amount: float = 0, 
                slack_factor: float = 0, 
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


    class azure.mgmt.machinelearningservices.models.BatchDeployment(TrackedResource):
        id: str
        identity: ManagedServiceIdentity
        kind: str
        location: str
        name: str
        properties: BatchDeploymentProperties
        sku: Sku
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                kind: Optional[str] = ..., 
                location: str, 
                properties: BatchDeploymentProperties, 
                sku: Optional[Sku] = ..., 
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


    class azure.mgmt.machinelearningservices.models.BatchDeploymentProperties(EndpointDeploymentPropertiesBase):
        code_configuration: CodeConfiguration
        compute: str
        description: str
        environment_id: str
        environment_variables: dict[str, str]
        error_threshold: int
        logging_level: Union[str, BatchLoggingLevel]
        max_concurrency_per_instance: int
        mini_batch_size: int
        model: AssetReferenceBase
        output_action: Union[str, BatchOutputAction]
        output_file_name: str
        properties: dict[str, str]
        provisioning_state: Union[str, DeploymentProvisioningState]
        resources: DeploymentResourceConfiguration
        retry_settings: BatchRetrySettings

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                code_configuration: Optional[CodeConfiguration] = ..., 
                compute: Optional[str] = ..., 
                description: Optional[str] = ..., 
                environment_id: Optional[str] = ..., 
                environment_variables: Optional[Dict[str, str]] = ..., 
                error_threshold: int = -1, 
                logging_level: Optional[Union[str, BatchLoggingLevel]] = ..., 
                max_concurrency_per_instance: int = 1, 
                mini_batch_size: int = 10, 
                model: Optional[AssetReferenceBase] = ..., 
                output_action: Optional[Union[str, BatchOutputAction]] = ..., 
                output_file_name: str = "predictions.csv", 
                properties: Optional[Dict[str, str]] = ..., 
                resources: Optional[DeploymentResourceConfiguration] = ..., 
                retry_settings: Optional[BatchRetrySettings] = ..., 
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


    class azure.mgmt.machinelearningservices.models.BatchDeploymentTrackedResourceArmPaginatedResult(Model):
        next_link: str
        value: list[BatchDeployment]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[BatchDeployment]] = ..., 
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


    class azure.mgmt.machinelearningservices.models.BatchEndpoint(TrackedResource):
        id: str
        identity: ManagedServiceIdentity
        kind: str
        location: str
        name: str
        properties: BatchEndpointProperties
        sku: Sku
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                kind: Optional[str] = ..., 
                location: str, 
                properties: BatchEndpointProperties, 
                sku: Optional[Sku] = ..., 
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


    class azure.mgmt.machinelearningservices.models.BatchEndpointDefaults(Model):
        deployment_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                deployment_name: Optional[str] = ..., 
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


    class azure.mgmt.machinelearningservices.models.BatchEndpointProperties(EndpointPropertiesBase):
        auth_mode: Union[str, EndpointAuthMode]
        defaults: BatchEndpointDefaults
        description: str
        keys: EndpointAuthKeys
        properties: dict[str, str]
        provisioning_state: Union[str, EndpointProvisioningState]
        scoring_uri: str
        swagger_uri: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                auth_mode: Union[str, EndpointAuthMode], 
                defaults: Optional[BatchEndpointDefaults] = ..., 
                description: Optional[str] = ..., 
                keys: Optional[EndpointAuthKeys] = ..., 
                properties: Optional[Dict[str, str]] = ..., 
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


    class azure.mgmt.machinelearningservices.models.BatchEndpointTrackedResourceArmPaginatedResult(Model):
        next_link: str
        value: list[BatchEndpoint]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[BatchEndpoint]] = ..., 
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


    class azure.mgmt.machinelearningservices.models.BatchLoggingLevel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEBUG = "Debug"
        INFO = "Info"
        WARNING = "Warning"


    class azure.mgmt.machinelearningservices.models.BatchOutputAction(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPEND_ROW = "AppendRow"
        SUMMARY_ONLY = "SummaryOnly"


    class azure.mgmt.machinelearningservices.models.BatchRetrySettings(Model):
        max_retries: int
        timeout: timedelta

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                max_retries: int = 3, 
                timeout: timedelta = "PT30S", 
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


    class azure.mgmt.machinelearningservices.models.BayesianSamplingAlgorithm(SamplingAlgorithm):
        sampling_algorithm_type: Union[str, SamplingAlgorithmType]

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


    class azure.mgmt.machinelearningservices.models.BillingCurrency(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        USD = "USD"


    class azure.mgmt.machinelearningservices.models.BindOptions(Model):
        create_host_path: bool
        propagation: str
        selinux: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                create_host_path: Optional[bool] = ..., 
                propagation: Optional[str] = ..., 
                selinux: Optional[str] = ..., 
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


    class azure.mgmt.machinelearningservices.models.BlobReferenceForConsumptionDto(Model):
        blob_uri: str
        credential: PendingUploadCredentialDto
        storage_account_arm_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                blob_uri: Optional[str] = ..., 
                credential: Optional[PendingUploadCredentialDto] = ..., 
                storage_account_arm_id: Optional[str] = ..., 
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


    class azure.mgmt.machinelearningservices.models.BlockedTransformers(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CAT_TARGET_ENCODER = "CatTargetEncoder"
        COUNT_VECTORIZER = "CountVectorizer"
        HASH_ONE_HOT_ENCODER = "HashOneHotEncoder"
        LABEL_ENCODER = "LabelEncoder"
        NAIVE_BAYES = "NaiveBayes"
        ONE_HOT_ENCODER = "OneHotEncoder"
        TEXT_TARGET_ENCODER = "TextTargetEncoder"
        TF_IDF = "TfIdf"
        WORD_EMBEDDING = "WordEmbedding"
        WO_E_TARGET_ENCODER = "WoETargetEncoder"


    class azure.mgmt.machinelearningservices.models.BuildContext(Model):
        context_uri: str
        dockerfile_path: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                context_uri: str, 
                dockerfile_path: str = "Dockerfile", 
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


    class azure.mgmt.machinelearningservices.models.Caching(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        READ_ONLY = "ReadOnly"
        READ_WRITE = "ReadWrite"


    class azure.mgmt.machinelearningservices.models.CertificateDatastoreCredentials(DatastoreCredentials):
        authority_url: str
        client_id: str
        credentials_type: Union[str, CredentialsType]
        resource_url: str
        secrets: CertificateDatastoreSecrets
        tenant_id: str
        thumbprint: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                authority_url: Optional[str] = ..., 
                client_id: str, 
                resource_url: Optional[str] = ..., 
                secrets: CertificateDatastoreSecrets, 
                tenant_id: str, 
                thumbprint: str, 
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


    class azure.mgmt.machinelearningservices.models.CertificateDatastoreSecrets(DatastoreSecrets):
        certificate: str
        secrets_type: Union[str, SecretsType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                certificate: Optional[str] = ..., 
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


    class azure.mgmt.machinelearningservices.models.Classification(TableVertical, AutoMLVertical):
        cv_split_column_names: list[str]
        featurization_settings: TableVerticalFeaturizationSettings
        limit_settings: TableVerticalLimitSettings
        log_verbosity: Union[str, LogVerbosity]
        n_cross_validations: NCrossValidations
        positive_label: str
        primary_metric: Union[str, ClassificationPrimaryMetrics]
        target_column_name: str
        task_type: Union[str, TaskType]
        test_data: MLTableJobInput
        test_data_size: float
        training_data: MLTableJobInput
        training_settings: ClassificationTrainingSettings
        validation_data: MLTableJobInput
        validation_data_size: float
        weight_column_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                cv_split_column_names: Optional[List[str]] = ..., 
                featurization_settings: Optional[TableVerticalFeaturizationSettings] = ..., 
                limit_settings: Optional[TableVerticalLimitSettings] = ..., 
                log_verbosity: Optional[Union[str, LogVerbosity]] = ..., 
                n_cross_validations: Optional[NCrossValidations] = ..., 
                positive_label: Optional[str] = ..., 
                primary_metric: Optional[Union[str, ClassificationPrimaryMetrics]] = ..., 
                target_column_name: Optional[str] = ..., 
                test_data: Optional[MLTableJobInput] = ..., 
                test_data_size: Optional[float] = ..., 
                training_data: MLTableJobInput, 
                training_settings: Optional[ClassificationTrainingSettings] = ..., 
                validation_data: Optional[MLTableJobInput] = ..., 
                validation_data_size: Optional[float] = ..., 
                weight_column_name: Optional[str] = ..., 
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


    class azure.mgmt.machinelearningservices.models.ClassificationModels(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BERNOULLI_NAIVE_BAYES = "BernoulliNaiveBayes"
        DECISION_TREE = "DecisionTree"
        EXTREME_RANDOM_TREES = "ExtremeRandomTrees"
        GRADIENT_BOOSTING = "GradientBoosting"
        KNN = "KNN"
        LIGHT_GBM = "LightGBM"
        LINEAR_SVM = "LinearSVM"
        LOGISTIC_REGRESSION = "LogisticRegression"
        MULTINOMIAL_NAIVE_BAYES = "MultinomialNaiveBayes"
        RANDOM_FOREST = "RandomForest"
        SGD = "SGD"
        SVM = "SVM"
        XG_BOOST_CLASSIFIER = "XGBoostClassifier"


    class azure.mgmt.machinelearningservices.models.ClassificationMultilabelPrimaryMetrics(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCURACY = "Accuracy"
        AUC_WEIGHTED = "AUCWeighted"
        AVERAGE_PRECISION_SCORE_WEIGHTED = "AveragePrecisionScoreWeighted"
        IOU = "IOU"
        NORM_MACRO_RECALL = "NormMacroRecall"
        PRECISION_SCORE_WEIGHTED = "PrecisionScoreWeighted"


    class azure.mgmt.machinelearningservices.models.ClassificationPrimaryMetrics(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCURACY = "Accuracy"
        AUC_WEIGHTED = "AUCWeighted"
        AVERAGE_PRECISION_SCORE_WEIGHTED = "AveragePrecisionScoreWeighted"
        NORM_MACRO_RECALL = "NormMacroRecall"
        PRECISION_SCORE_WEIGHTED = "PrecisionScoreWeighted"


    class azure.mgmt.machinelearningservices.models.ClassificationTrainingSettings(TrainingSettings):
        allowed_training_algorithms: Union[list[str, ClassificationModels]]
        blocked_training_algorithms: Union[list[str, ClassificationModels]]
        enable_dnn_training: bool
        enable_model_explainability: bool
        enable_onnx_compatible_models: bool
        enable_stack_ensemble: bool
        enable_vote_ensemble: bool
        ensemble_model_download_timeout: timedelta
        stack_ensemble_settings: StackEnsembleSettings

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                allowed_training_algorithms: Optional[List[Union[str, ClassificationModels]]] = ..., 
                blocked_training_algorithms: Optional[List[Union[str, ClassificationModels]]] = ..., 
                enable_dnn_training: bool = False, 
                enable_model_explainability: bool = True, 
                enable_onnx_compatible_models: bool = False, 
                enable_stack_ensemble: bool = True, 
                enable_vote_ensemble: bool = True, 
                ensemble_model_download_timeout: timedelta = "PT5M", 
                stack_ensemble_settings: Optional[StackEnsembleSettings] = ..., 
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


    class azure.mgmt.machinelearningservices.models.ClusterPurpose(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DENSE_PROD = "DenseProd"
        DEV_TEST = "DevTest"
        FAST_PROD = "FastProd"


    class azure.mgmt.machinelearningservices.models.ClusterUpdateParameters(Model):
        properties: ScaleSettingsInformation

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[ScaleSettingsInformation] = ..., 
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


    class azure.mgmt.machinelearningservices.models.CodeConfiguration(Model):
        code_id: str
        scoring_script: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                code_id: Optional[str] = ..., 
                scoring_script: str, 
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


    class azure.mgmt.machinelearningservices.models.CodeContainer(Resource):
        id: str
        name: str
        properties: CodeContainerProperties
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: CodeContainerProperties, 
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


    class azure.mgmt.machinelearningservices.models.CodeContainerProperties(AssetContainer):
        description: str
        is_archived: bool
        latest_version: str
        next_version: str
        properties: dict[str, str]
        provisioning_state: Union[str, AssetProvisioningState]
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                is_archived: bool = False, 
                properties: Optional[Dict[str, str]] = ..., 
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


    class azure.mgmt.machinelearningservices.models.CodeContainerResourceArmPaginatedResult(Model):
        next_link: str
        value: list[CodeContainer]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[CodeContainer]] = ..., 
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


    class azure.mgmt.machinelearningservices.models.CodeVersion(Resource):
        id: str
        name: str
        properties: CodeVersionProperties
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: CodeVersionProperties, 
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


    class azure.mgmt.machinelearningservices.models.CodeVersionProperties(AssetBase):
        code_uri: str
        description: str
        is_anonymous: bool
        is_archived: bool
        properties: dict[str, str]
        provisioning_state: Union[str, AssetProvisioningState]
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                code_uri: Optional[str] = ..., 
                description: Optional[str] = ..., 
                is_anonymous: bool = False, 
                is_archived: bool = False, 
                properties: Optional[Dict[str, str]] = ..., 
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


    class azure.mgmt.machinelearningservices.models.CodeVersionResourceArmPaginatedResult(Model):
        next_link: str
        value: list[CodeVersion]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[CodeVersion]] = ..., 
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


    class azure.mgmt.machinelearningservices.models.ColumnTransformer(Model):
        fields: list[str]
        parameters: JSON

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                fields: Optional[List[str]] = ..., 
                parameters: Optional[JSON] = ..., 
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


    class azure.mgmt.machinelearningservices.models.CommandJob(JobBaseProperties):
        code_id: str
        command: str
        component_id: str
        compute_id: str
        description: str
        display_name: str
        distribution: DistributionConfiguration
        environment_id: str
        environment_variables: dict[str, str]
        experiment_name: str
        identity: IdentityConfiguration
        inputs: dict[str, JobInput]
        is_archived: bool
        job_type: Union[str, JobType]
        limits: CommandJobLimits
        outputs: dict[str, JobOutput]
        parameters: JSON
        properties: dict[str, str]
        resources: JobResourceConfiguration
        services: dict[str, JobService]
        status: Union[str, JobStatus]
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                code_id: Optional[str] = ..., 
                command: str, 
                component_id: Optional[str] = ..., 
                compute_id: Optional[str] = ..., 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                distribution: Optional[DistributionConfiguration] = ..., 
                environment_id: str, 
                environment_variables: Optional[Dict[str, str]] = ..., 
                experiment_name: str = "Default", 
                identity: Optional[IdentityConfiguration] = ..., 
                inputs: Optional[Dict[str, JobInput]] = ..., 
                is_archived: bool = False, 
                limits: Optional[CommandJobLimits] = ..., 
                outputs: Optional[Dict[str, JobOutput]] = ..., 
                properties: Optional[Dict[str, str]] = ..., 
                resources: Optional[JobResourceConfiguration] = ..., 
                services: Optional[Dict[str, JobService]] = ..., 
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


    class azure.mgmt.machinelearningservices.models.CommandJobLimits(JobLimits):
        job_limits_type: Union[str, JobLimitsType]
        timeout: timedelta

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                timeout: Optional[timedelta] = ..., 
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


    class azure.mgmt.machinelearningservices.models.ComponentContainer(Resource):
        id: str
        name: str
        properties: ComponentContainerProperties
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: ComponentContainerProperties, 
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


    class azure.mgmt.machinelearningservices.models.ComponentContainerProperties(AssetContainer):
        description: str
        is_archived: bool
        latest_version: str
        next_version: str
        properties: dict[str, str]
        provisioning_state: Union[str, AssetProvisioningState]
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                is_archived: bool = False, 
                properties: Optional[Dict[str, str]] = ..., 
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


    class azure.mgmt.machinelearningservices.models.ComponentContainerResourceArmPaginatedResult(Model):
        next_link: str
        value: list[ComponentContainer]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[ComponentContainer]] = ..., 
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


    class azure.mgmt.machinelearningservices.models.ComponentVersion(Resource):
        id: str
        name: str
        properties: ComponentVersionProperties
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: ComponentVersionProperties, 
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


    class azure.mgmt.machinelearningservices.models.ComponentVersionProperties(AssetBase):
        component_spec: JSON
        description: str
        is_anonymous: bool
        is_archived: bool
        properties: dict[str, str]
        provisioning_state: Union[str, AssetProvisioningState]
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                component_spec: Optional[JSON] = ..., 
                description: Optional[str] = ..., 
                is_anonymous: bool = False, 
                is_archived: bool = False, 
                properties: Optional[Dict[str, str]] = ..., 
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


    class azure.mgmt.machinelearningservices.models.ComponentVersionResourceArmPaginatedResult(Model):
        next_link: str
        value: list[ComponentVersion]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[ComponentVersion]] = ..., 
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


    class azure.mgmt.machinelearningservices.models.Compute(Model):
        compute_location: str
        compute_type: Union[str, ComputeType]
        created_on: datetime
        description: str
        disable_local_auth: bool
        is_attached_compute: bool
        modified_on: datetime
        provisioning_errors: list[ErrorResponse]
        provisioning_state: Union[str, ProvisioningState]
        resource_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                compute_location: Optional[str] = ..., 
                description: Optional[str] = ..., 
                disable_local_auth: Optional[bool] = ..., 
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


    class azure.mgmt.machinelearningservices.models.ComputeInstance(Compute, ComputeInstanceSchema):
        compute_location: str
        compute_type: Union[str, ComputeType]
        created_on: datetime
        description: str
        disable_local_auth: bool
        is_attached_compute: bool
        modified_on: datetime
        properties: ComputeInstanceProperties
        provisioning_errors: list[ErrorResponse]
        provisioning_state: Union[str, ProvisioningState]
        resource_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                compute_location: Optional[str] = ..., 
                description: Optional[str] = ..., 
                disable_local_auth: Optional[bool] = ..., 
                properties: Optional[ComputeInstanceProperties] = ..., 
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


    class azure.mgmt.machinelearningservices.models.ComputeInstanceApplication(Model):
        display_name: str
        endpoint_uri: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ..., 
                endpoint_uri: Optional[str] = ..., 
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


    class azure.mgmt.machinelearningservices.models.ComputeInstanceAuthorizationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PERSONAL = "personal"


    class azure.mgmt.machinelearningservices.models.ComputeInstanceConnectivityEndpoints(Model):
        private_ip_address: str
        public_ip_address: str

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


    class azure.mgmt.machinelearningservices.models.ComputeInstanceContainer(Model):
        autosave: Union[str, Autosave]
        environment: ComputeInstanceEnvironmentInfo
        gpu: str
        name: str
        network: Union[str, Network]
        services: list[JSON]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                autosave: Optional[Union[str, Autosave]] = ..., 
                environment: Optional[ComputeInstanceEnvironmentInfo] = ..., 
                gpu: Optional[str] = ..., 
                name: Optional[str] = ..., 
                network: Optional[Union[str, Network]] = ..., 
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


    class azure.mgmt.machinelearningservices.models.ComputeInstanceCreatedBy(Model):
        user_id: str
        user_name: str
        user_org_id: str

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


    class azure.mgmt.machinelearningservices.models.ComputeInstanceDataDisk(Model):
        caching: Union[str, Caching]
        disk_size_gb: int
        lun: int
        storage_account_type: Union[str, StorageAccountType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                caching: Optional[Union[str, Caching]] = ..., 
                disk_size_gb: Optional[int] = ..., 
                lun: Optional[int] = ..., 
                storage_account_type: Union[str, StorageAccountType] = "Standard_LRS", 
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


    class azure.mgmt.machinelearningservices.models.ComputeInstanceDataMount(Model):
        created_by: str
        error: str
        mount_action: Union[str, MountAction]
        mount_name: str
        mount_path: str
        mount_state: Union[str, MountState]
        mounted_on: datetime
        source: str
        source_type: Union[str, SourceType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                created_by: Optional[str] = ..., 
                error: Optional[str] = ..., 
                mount_action: Optional[Union[str, MountAction]] = ..., 
                mount_name: Optional[str] = ..., 
                mount_path: Optional[str] = ..., 
                mount_state: Optional[Union[str, MountState]] = ..., 
                mounted_on: Optional[datetime] = ..., 
                source: Optional[str] = ..., 
                source_type: Optional[Union[str, SourceType]] = ..., 
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


    class azure.mgmt.machinelearningservices.models.ComputeInstanceEnvironmentInfo(Model):
        name: str
        version: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                version: Optional[str] = ..., 
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


    class azure.mgmt.machinelearningservices.models.ComputeInstanceLastOperation(Model):
        operation_name: Union[str, OperationName]
        operation_status: Union[str, OperationStatus]
        operation_time: datetime
        operation_trigger: Union[str, OperationTrigger]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                operation_name: Optional[Union[str, OperationName]] = ..., 
                operation_status: Optional[Union[str, OperationStatus]] = ..., 
                operation_time: Optional[datetime] = ..., 
                operation_trigger: Optional[Union[str, OperationTrigger]] = ..., 
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


    class azure.mgmt.machinelearningservices.models.ComputeInstanceProperties(Model):
        application_sharing_policy: Union[str, ApplicationSharingPolicy]
        applications: list[ComputeInstanceApplication]
        compute_instance_authorization_type: Union[str, ComputeInstanceAuthorizationType]
        connectivity_endpoints: ComputeInstanceConnectivityEndpoints
        containers: list[ComputeInstanceContainer]
        created_by: ComputeInstanceCreatedBy
        custom_services: list[CustomService]
        data_disks: list[ComputeInstanceDataDisk]
        data_mounts: list[ComputeInstanceDataMount]
        enable_node_public_ip: bool
        errors: list[ErrorResponse]
        last_operation: ComputeInstanceLastOperation
        os_image_metadata: ImageMetadata
        personal_compute_instance_settings: PersonalComputeInstanceSettings
        schedules: ComputeSchedules
        setup_scripts: SetupScripts
        ssh_settings: ComputeInstanceSshSettings
        state: Union[str, ComputeInstanceState]
        subnet: ResourceId
        versions: ComputeInstanceVersion
        vm_size: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                application_sharing_policy: Union[str, ApplicationSharingPolicy] = "Shared", 
                compute_instance_authorization_type: Union[str, ComputeInstanceAuthorizationType] = "personal", 
                custom_services: Optional[List[CustomService]] = ..., 
                enable_node_public_ip: Optional[bool] = ..., 
                personal_compute_instance_settings: Optional[PersonalComputeInstanceSettings] = ..., 
                schedules: Optional[ComputeSchedules] = ..., 
                setup_scripts: Optional[SetupScripts] = ..., 
                ssh_settings: Optional[ComputeInstanceSshSettings] = ..., 
                subnet: Optional[ResourceId] = ..., 
                vm_size: Optional[str] = ..., 
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


    class azure.mgmt.machinelearningservices.models.ComputeInstanceSchema(Model):
        properties: ComputeInstanceProperties

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[ComputeInstanceProperties] = ..., 
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


    class azure.mgmt.machinelearningservices.models.ComputeInstanceSshSettings(Model):
        admin_public_key: str
        admin_user_name: str
        ssh_port: int
        ssh_public_access: Union[str, SshPublicAccess]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                admin_public_key: Optional[str] = ..., 
                ssh_public_access: Union[str, SshPublicAccess] = "Disabled", 
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


    class azure.mgmt.machinelearningservices.models.ComputeInstanceState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREATE_FAILED = "CreateFailed"
        CREATING = "Creating"
        DELETING = "Deleting"
        JOB_RUNNING = "JobRunning"
        RESTARTING = "Restarting"
        RUNNING = "Running"
        SETTING_UP = "SettingUp"
        SETUP_FAILED = "SetupFailed"
        STARTING = "Starting"
        STOPPED = "Stopped"
        STOPPING = "Stopping"
        UNKNOWN = "Unknown"
        UNUSABLE = "Unusable"
        USER_SETTING_UP = "UserSettingUp"
        USER_SETUP_FAILED = "UserSetupFailed"


    class azure.mgmt.machinelearningservices.models.ComputeInstanceVersion(Model):
        runtime: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                runtime: Optional[str] = ..., 
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


    class azure.mgmt.machinelearningservices.models.ComputePowerAction(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        START = "Start"
        STOP = "Stop"


    class azure.mgmt.machinelearningservices.models.ComputeResource(Resource, ComputeResourceSchema):
        id: str
        identity: ManagedServiceIdentity
        location: str
        name: str
        properties: Compute
        sku: Sku
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                location: Optional[str] = ..., 
                properties: Optional[Compute] = ..., 
                sku: Optional[Sku] = ..., 
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


    class azure.mgmt.machinelearningservices.models.ComputeResourceSchema(Model):
        properties: Compute

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[Compute] = ..., 
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


    class azure.mgmt.machinelearningservices.models.ComputeSchedules(Model):
        compute_start_stop: list[ComputeStartStopSchedule]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                compute_start_stop: Optional[List[ComputeStartStopSchedule]] = ..., 
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


    class azure.mgmt.machinelearningservices.models.ComputeSecrets(Model):
        compute_type: Union[str, ComputeType]

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


    class azure.mgmt.machinelearningservices.models.ComputeStartStopSchedule(Model):
        action: Union[str, ComputePowerAction]
        cron: Cron
        id: str
        provisioning_status: Union[str, ProvisioningStatus]
        recurrence: Recurrence
        schedule: ScheduleBase
        status: Union[str, ScheduleStatus]
        trigger_type: Union[str, TriggerType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                action: Optional[Union[str, ComputePowerAction]] = ..., 
                cron: Optional[Cron] = ..., 
                recurrence: Optional[Recurrence] = ..., 
                schedule: Optional[ScheduleBase] = ..., 
                status: Optional[Union[str, ScheduleStatus]] = ..., 
                trigger_type: Optional[Union[str, TriggerType]] = ..., 
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


    class azure.mgmt.machinelearningservices.models.ComputeType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AKS = "AKS"
        AML_COMPUTE = "AmlCompute"
        COMPUTE_INSTANCE = "ComputeInstance"
        DATABRICKS = "Databricks"
        DATA_FACTORY = "DataFactory"
        DATA_LAKE_ANALYTICS = "DataLakeAnalytics"
        HD_INSIGHT = "HDInsight"
        KUBERNETES = "Kubernetes"
        SYNAPSE_SPARK = "SynapseSpark"
        VIRTUAL_MACHINE = "VirtualMachine"


    class azure.mgmt.machinelearningservices.models.ConnectionAuthType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MANAGED_IDENTITY = "ManagedIdentity"
        NONE = "None"
        PAT = "PAT"
        SAS = "SAS"
        USERNAME_PASSWORD = "UsernamePassword"


    class azure.mgmt.machinelearningservices.models.ConnectionCategory(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONTAINER_REGISTRY = "ContainerRegistry"
        GIT = "Git"
        PYTHON_FEED = "PythonFeed"


    class azure.mgmt.machinelearningservices.models.ContainerResourceRequirements(Model):
        container_resource_limits: ContainerResourceSettings
        container_resource_requests: ContainerResourceSettings

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                container_resource_limits: Optional[ContainerResourceSettings] = ..., 
                container_resource_requests: Optional[ContainerResourceSettings] = ..., 
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


    class azure.mgmt.machinelearningservices.models.ContainerResourceSettings(Model):
        cpu: str
        gpu: str
        memory: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                cpu: Optional[str] = ..., 
                gpu: Optional[str] = ..., 
                memory: Optional[str] = ..., 
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


    class azure.mgmt.machinelearningservices.models.ContainerType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INFERENCE_SERVER = "InferenceServer"
        STORAGE_INITIALIZER = "StorageInitializer"


    class azure.mgmt.machinelearningservices.models.CosmosDbSettings(Model):
        collections_throughput: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                collections_throughput: Optional[int] = ..., 
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


    class azure.mgmt.machinelearningservices.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.machinelearningservices.models.CredentialsType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCOUNT_KEY = "AccountKey"
        CERTIFICATE = "Certificate"
        NONE = "None"
        SAS = "Sas"
        SERVICE_PRINCIPAL = "ServicePrincipal"


    class azure.mgmt.machinelearningservices.models.Cron(Model):
        expression: str
        start_time: str
        time_zone: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                expression: Optional[str] = ..., 
                start_time: Optional[str] = ..., 
                time_zone: str = "UTC", 
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


    class azure.mgmt.machinelearningservices.models.CronTrigger(TriggerBase):
        end_time: str
        expression: str
        start_time: str
        time_zone: str
        trigger_type: Union[str, TriggerType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                end_time: Optional[str] = ..., 
                expression: str, 
                start_time: Optional[str] = ..., 
                time_zone: str = "UTC", 
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


    class azure.mgmt.machinelearningservices.models.CustomForecastHorizon(ForecastHorizon):
        mode: Union[str, ForecastHorizonMode]
        value: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: int, 
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


    class azure.mgmt.machinelearningservices.models.CustomModelJobInput(AssetJobInput, JobInput):
        description: str
        job_input_type: Union[str, JobInputType]
        mode: Union[str, InputDeliveryMode]
        uri: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                mode: Optional[Union[str, InputDeliveryMode]] = ..., 
                uri: str, 
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


    class azure.mgmt.machinelearningservices.models.CustomModelJobOutput(AssetJobOutput, JobOutput):
        description: str
        job_output_type: Union[str, JobOutputType]
        mode: Union[str, OutputDeliveryMode]
        uri: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                mode: Optional[Union[str, OutputDeliveryMode]] = ..., 
                uri: Optional[str] = ..., 
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


    class azure.mgmt.machinelearningservices.models.CustomNCrossValidations(NCrossValidations):
        mode: Union[str, NCrossValidationsMode]
        value: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: int, 
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


    class azure.mgmt.machinelearningservices.models.CustomSeasonality(Seasonality):
        mode: Union[str, SeasonalityMode]
        value: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: int, 
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


    class azure.mgmt.machinelearningservices.models.CustomService(Model):
        additional_properties: dict[str, any]
        docker: Docker
        endpoints: list[Endpoint]
        environment_variables: dict[str, EnvironmentVariable]
        image: Image
        name: str
        volumes: list[VolumeDefinition]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                additional_properties: Optional[Dict[str, Any]] = ..., 
                docker: Optional[Docker] = ..., 
                endpoints: Optional[List[Endpoint]] = ..., 
                environment_variables: Optional[Dict[str, EnvironmentVariable]] = ..., 
                image: Optional[Image] = ..., 
                name: Optional[str] = ..., 
                volumes: Optional[List[VolumeDefinition]] = ..., 
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


    class azure.mgmt.machinelearningservices.models.CustomTargetLags(TargetLags):
        mode: Union[str, TargetLagsMode]
        values: list[int]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                values: List[int], 
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


    class azure.mgmt.machinelearningservices.models.CustomTargetRollingWindowSize(TargetRollingWindowSize):
        mode: Union[str, TargetRollingWindowSizeMode]
        value: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: int, 
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


    class azure.mgmt.machinelearningservices.models.DataContainer(Resource):
        id: str
        name: str
        properties: DataContainerProperties
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: DataContainerProperties, 
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


    class azure.mgmt.machinelearningservices.models.DataContainerProperties(AssetContainer):
        data_type: Union[str, DataType]
        description: str
        is_archived: bool
        latest_version: str
        next_version: str
        properties: dict[str, str]
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                data_type: Union[str, DataType], 
                description: Optional[str] = ..., 
                is_archived: bool = False, 
                properties: Optional[Dict[str, str]] = ..., 
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


    class azure.mgmt.machinelearningservices.models.DataContainerResourceArmPaginatedResult(Model):
        next_link: str
        value: list[DataContainer]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[DataContainer]] = ..., 
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


    class azure.mgmt.machinelearningservices.models.DataFactory(Compute):
        compute_location: str
        compute_type: Union[str, ComputeType]
        created_on: datetime
        description: str
        disable_local_auth: bool
        is_attached_compute: bool
        modified_on: datetime
        provisioning_errors: list[ErrorResponse]
        provisioning_state: Union[str, ProvisioningState]
        resource_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                compute_location: Optional[str] = ..., 
                description: Optional[str] = ..., 
                disable_local_auth: Optional[bool] = ..., 
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


    class azure.mgmt.machinelearningservices.models.DataLakeAnalytics(Compute, DataLakeAnalyticsSchema):
        compute_location: str
        compute_type: Union[str, ComputeType]
        created_on: datetime
        description: str
        disable_local_auth: bool
        is_attached_compute: bool
        modified_on: datetime
        properties: DataLakeAnalyticsSchemaProperties
        provisioning_errors: list[ErrorResponse]
        provisioning_state: Union[str, ProvisioningState]
        resource_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                compute_location: Optional[str] = ..., 
                description: Optional[str] = ..., 
                disable_local_auth: Optional[bool] = ..., 
                properties: Optional[DataLakeAnalyticsSchemaProperties] = ..., 
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


    class azure.mgmt.machinelearningservices.models.DataLakeAnalyticsSchema(Model):
        properties: DataLakeAnalyticsSchemaProperties

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[DataLakeAnalyticsSchemaProperties] = ..., 
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


    class azure.mgmt.machinelearningservices.models.DataLakeAnalyticsSchemaProperties(Model):
        data_lake_store_account_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                data_lake_store_account_name: Optional[str] = ..., 
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


    class azure.mgmt.machinelearningservices.models.DataPathAssetReference(AssetReferenceBase):
        datastore_id: str
        path: str
        reference_type: Union[str, ReferenceType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                datastore_id: Optional[str] = ..., 
                path: Optional[str] = ..., 
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


    class azure.mgmt.machinelearningservices.models.DataType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MLTABLE = "mltable"
        URI_FILE = "uri_file"
        URI_FOLDER = "uri_folder"


    class azure.mgmt.machinelearningservices.models.DataVersionBase(Resource):
        id: str
        name: str
        properties: DataVersionBaseProperties
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: DataVersionBaseProperties, 
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


    class azure.mgmt.machinelearningservices.models.DataVersionBaseProperties(AssetBase):
        data_type: Union[str, DataType]
        data_uri: str
        description: str
        is_anonymous: bool
        is_archived: bool
        properties: dict[str, str]
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                data_uri: str, 
                description: Optional[str] = ..., 
                is_anonymous: bool = False, 
                is_archived: bool = False, 
                properties: Optional[Dict[str, str]] = ..., 
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


    class azure.mgmt.machinelearningservices.models.DataVersionBaseResourceArmPaginatedResult(Model):
        next_link: str
        value: list[DataVersionBase]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[DataVersionBase]] = ..., 
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


    class azure.mgmt.machinelearningservices.models.Databricks(Compute, DatabricksSchema):
        compute_location: str
        compute_type: Union[str, ComputeType]
        created_on: datetime
        description: str
        disable_local_auth: bool
        is_attached_compute: bool
        modified_on: datetime
        properties: DatabricksProperties
        provisioning_errors: list[ErrorResponse]
        provisioning_state: Union[str, ProvisioningState]
        resource_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                compute_location: Optional[str] = ..., 
                description: Optional[str] = ..., 
                disable_local_auth: Optional[bool] = ..., 
                properties: Optional[DatabricksProperties] = ..., 
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


    class azure.mgmt.machinelearningservices.models.DatabricksComputeSecrets(ComputeSecrets, DatabricksComputeSecretsProperties):
        compute_type: Union[str, ComputeType]
        databricks_access_token: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                databricks_access_token: Optional[str] = ..., 
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


    class azure.mgmt.machinelearningservices.models.DatabricksComputeSecretsProperties(Model):
        databricks_access_token: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                databricks_access_token: Optional[str] = ..., 
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


    class azure.mgmt.machinelearningservices.models.DatabricksProperties(Model):
        databricks_access_token: str
        workspace_url: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                databricks_access_token: Optional[str] = ..., 
                workspace_url: Optional[str] = ..., 
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


    class azure.mgmt.machinelearningservices.models.DatabricksSchema(Model):
        properties: DatabricksProperties

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[DatabricksProperties] = ..., 
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


    class azure.mgmt.machinelearningservices.models.Datastore(Resource):
        id: str
        name: str
        properties: DatastoreProperties
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: DatastoreProperties, 
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


    class azure.mgmt.machinelearningservices.models.DatastoreCredentials(Model):
        credentials_type: Union[str, CredentialsType]

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


    class azure.mgmt.machinelearningservices.models.DatastoreProperties(ResourceBase):
        credentials: DatastoreCredentials
        datastore_type: Union[str, DatastoreType]
        description: str
        is_default: bool
        properties: dict[str, str]
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                credentials: DatastoreCredentials, 
                description: Optional[str] = ..., 
                properties: Optional[Dict[str, str]] = ..., 
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


    class azure.mgmt.machinelearningservices.models.DatastoreResourceArmPaginatedResult(Model):
        next_link: str
        value: list[Datastore]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[Datastore]] = ..., 
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


    class azure.mgmt.machinelearningservices.models.DatastoreSecrets(Model):
        secrets_type: Union[str, SecretsType]

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


    class azure.mgmt.machinelearningservices.models.DatastoreType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_BLOB = "AzureBlob"
        AZURE_DATA_LAKE_GEN1 = "AzureDataLakeGen1"
        AZURE_DATA_LAKE_GEN2 = "AzureDataLakeGen2"
        AZURE_FILE = "AzureFile"


    class azure.mgmt.machinelearningservices.models.DefaultScaleSettings(OnlineScaleSettings):
        scale_type: Union[str, ScaleType]

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


    class azure.mgmt.machinelearningservices.models.DeploymentLogs(Model):
        content: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                content: Optional[str] = ..., 
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


    class azure.mgmt.machinelearningservices.models.DeploymentLogsRequest(Model):
        container_type: Union[str, ContainerType]
        tail: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                container_type: Optional[Union[str, ContainerType]] = ..., 
                tail: Optional[int] = ..., 
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


    class azure.mgmt.machinelearningservices.models.DeploymentProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SCALING = "Scaling"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.machinelearningservices.models.DeploymentResourceConfiguration(ResourceConfiguration):
        instance_count: int
        instance_type: str
        properties: dict[str, JSON]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                instance_count: int = 1, 
                instance_type: Optional[str] = ..., 
                properties: Optional[Dict[str, JSON]] = ..., 
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


    class azure.mgmt.machinelearningservices.models.DiagnoseRequestProperties(Model):
        application_insights: dict[str, JSON]
        container_registry: dict[str, JSON]
        dns_resolution: dict[str, JSON]
        key_vault: dict[str, JSON]
        nsg: dict[str, JSON]
        others: dict[str, JSON]
        resource_lock: dict[str, JSON]
        storage_account: dict[str, JSON]
        udr: dict[str, JSON]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                application_insights: Optional[Dict[str, JSON]] = ..., 
                container_registry: Optional[Dict[str, JSON]] = ..., 
                dns_resolution: Optional[Dict[str, JSON]] = ..., 
                key_vault: Optional[Dict[str, JSON]] = ..., 
                nsg: Optional[Dict[str, JSON]] = ..., 
                others: Optional[Dict[str, JSON]] = ..., 
                resource_lock: Optional[Dict[str, JSON]] = ..., 
                storage_account: Optional[Dict[str, JSON]] = ..., 
                udr: Optional[Dict[str, JSON]] = ..., 
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


    class azure.mgmt.machinelearningservices.models.DiagnoseResponseResult(Model):
        value: DiagnoseResponseResultValue

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[DiagnoseResponseResultValue] = ..., 
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


    class azure.mgmt.machinelearningservices.models.DiagnoseResponseResultValue(Model):
        application_insights_results: list[DiagnoseResult]
        container_registry_results: list[DiagnoseResult]
        dns_resolution_results: list[DiagnoseResult]
        key_vault_results: list[DiagnoseResult]
        network_security_rule_results: list[DiagnoseResult]
        other_results: list[DiagnoseResult]
        resource_lock_results: list[DiagnoseResult]
        storage_account_results: list[DiagnoseResult]
        user_defined_route_results: list[DiagnoseResult]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                application_insights_results: Optional[List[DiagnoseResult]] = ..., 
                container_registry_results: Optional[List[DiagnoseResult]] = ..., 
                dns_resolution_results: Optional[List[DiagnoseResult]] = ..., 
                key_vault_results: Optional[List[DiagnoseResult]] = ..., 
                network_security_rule_results: Optional[List[DiagnoseResult]] = ..., 
                other_results: Optional[List[DiagnoseResult]] = ..., 
                resource_lock_results: Optional[List[DiagnoseResult]] = ..., 
                storage_account_results: Optional[List[DiagnoseResult]] = ..., 
                user_defined_route_results: Optional[List[DiagnoseResult]] = ..., 
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


    class azure.mgmt.machinelearningservices.models.DiagnoseResult(Model):
        code: str
        level: Union[str, DiagnoseResultLevel]
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


    class azure.mgmt.machinelearningservices.models.DiagnoseResultLevel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ERROR = "Error"
        INFORMATION = "Information"
        WARNING = "Warning"


    class azure.mgmt.machinelearningservices.models.DiagnoseWorkspaceParameters(Model):
        value: DiagnoseRequestProperties

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[DiagnoseRequestProperties] = ..., 
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


    class azure.mgmt.machinelearningservices.models.DistributionConfiguration(Model):
        distribution_type: Union[str, DistributionType]

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


    class azure.mgmt.machinelearningservices.models.DistributionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MPI = "Mpi"
        PY_TORCH = "PyTorch"
        TENSOR_FLOW = "TensorFlow"


    class azure.mgmt.machinelearningservices.models.Docker(Model):
        additional_properties: dict[str, any]
        privileged: bool

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                additional_properties: Optional[Dict[str, Any]] = ..., 
                privileged: Optional[bool] = ..., 
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


    class azure.mgmt.machinelearningservices.models.EarlyTerminationPolicy(Model):
        delay_evaluation: int
        evaluation_interval: int
        policy_type: Union[str, EarlyTerminationPolicyType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                delay_evaluation: int = 0, 
                evaluation_interval: int = 0, 
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


    class azure.mgmt.machinelearningservices.models.EarlyTerminationPolicyType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BANDIT = "Bandit"
        MEDIAN_STOPPING = "MedianStopping"
        TRUNCATION_SELECTION = "TruncationSelection"


    class azure.mgmt.machinelearningservices.models.EgressPublicNetworkAccessType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.machinelearningservices.models.EncryptionKeyVaultProperties(Model):
        identity_client_id: str
        key_identifier: str
        key_vault_arm_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                identity_client_id: Optional[str] = ..., 
                key_identifier: str, 
                key_vault_arm_id: str, 
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


    class azure.mgmt.machinelearningservices.models.EncryptionProperty(Model):
        identity: IdentityForCmk
        key_vault_properties: EncryptionKeyVaultProperties
        status: Union[str, EncryptionStatus]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                identity: Optional[IdentityForCmk] = ..., 
                key_vault_properties: EncryptionKeyVaultProperties, 
                status: Union[str, EncryptionStatus], 
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


    class azure.mgmt.machinelearningservices.models.EncryptionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.machinelearningservices.models.Endpoint(Model):
        host_ip: str
        name: str
        protocol: Union[str, Protocol]
        published: int
        target: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                host_ip: Optional[str] = ..., 
                name: Optional[str] = ..., 
                protocol: Union[str, Protocol] = "tcp", 
                published: Optional[int] = ..., 
                target: Optional[int] = ..., 
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


    class azure.mgmt.machinelearningservices.models.EndpointAuthKeys(Model):
        primary_key: str
        secondary_key: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                primary_key: Optional[str] = ..., 
                secondary_key: Optional[str] = ..., 
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


    class azure.mgmt.machinelearningservices.models.EndpointAuthMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AAD_TOKEN = "AADToken"
        AML_TOKEN = "AMLToken"
        KEY = "Key"


    class azure.mgmt.machinelearningservices.models.EndpointAuthToken(Model):
        access_token: str
        expiry_time_utc: int
        refresh_after_time_utc: int
        token_type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                access_token: Optional[str] = ..., 
                expiry_time_utc: int = 0, 
                refresh_after_time_utc: int = 0, 
                token_type: Optional[str] = ..., 
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


    class azure.mgmt.machinelearningservices.models.EndpointComputeType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_ML_COMPUTE = "AzureMLCompute"
        KUBERNETES = "Kubernetes"
        MANAGED = "Managed"


    class azure.mgmt.machinelearningservices.models.EndpointDeploymentPropertiesBase(Model):
        code_configuration: CodeConfiguration
        description: str
        environment_id: str
        environment_variables: dict[str, str]
        properties: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                code_configuration: Optional[CodeConfiguration] = ..., 
                description: Optional[str] = ..., 
                environment_id: Optional[str] = ..., 
                environment_variables: Optional[Dict[str, str]] = ..., 
                properties: Optional[Dict[str, str]] = ..., 
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


    class azure.mgmt.machinelearningservices.models.EndpointPropertiesBase(Model):
        auth_mode: Union[str, EndpointAuthMode]
        description: str
        keys: EndpointAuthKeys
        properties: dict[str, str]
        scoring_uri: str
        swagger_uri: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                auth_mode: Union[str, EndpointAuthMode], 
                description: Optional[str] = ..., 
                keys: Optional[EndpointAuthKeys] = ..., 
                properties: Optional[Dict[str, str]] = ..., 
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


    class azure.mgmt.machinelearningservices.models.EndpointProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.machinelearningservices.models.EndpointScheduleAction(ScheduleActionBase):
        action_type: Union[str, ScheduleActionType]
        endpoint_invocation_definition: JSON

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                endpoint_invocation_definition: JSON, 
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


    class azure.mgmt.machinelearningservices.models.EndpointServiceConnectionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPROVED = "Approved"
        DISCONNECTED = "Disconnected"
        PENDING = "Pending"
        REJECTED = "Rejected"


    class azure.mgmt.machinelearningservices.models.EnvironmentContainer(Resource):
        id: str
        name: str
        properties: EnvironmentContainerProperties
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: EnvironmentContainerProperties, 
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


    class azure.mgmt.machinelearningservices.models.EnvironmentContainerProperties(AssetContainer):
        description: str
        is_archived: bool
        latest_version: str
        next_version: str
        properties: dict[str, str]
        provisioning_state: Union[str, AssetProvisioningState]
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                is_archived: bool = False, 
                properties: Optional[Dict[str, str]] = ..., 
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


    class azure.mgmt.machinelearningservices.models.EnvironmentContainerResourceArmPaginatedResult(Model):
        next_link: str
        value: list[EnvironmentContainer]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[EnvironmentContainer]] = ..., 
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


    class azure.mgmt.machinelearningservices.models.EnvironmentType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CURATED = "Curated"
        USER_CREATED = "UserCreated"


    class azure.mgmt.machinelearningservices.models.EnvironmentVariable(Model):
        additional_properties: dict[str, any]
        type: Union[str, EnvironmentVariableType]
        value: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                additional_properties: Optional[Dict[str, Any]] = ..., 
                type: Union[str, EnvironmentVariableType] = "local", 
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


    class azure.mgmt.machinelearningservices.models.EnvironmentVariableType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LOCAL = "local"


    class azure.mgmt.machinelearningservices.models.EnvironmentVersion(Resource):
        id: str
        name: str
        properties: EnvironmentVersionProperties
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: EnvironmentVersionProperties, 
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


    class azure.mgmt.machinelearningservices.models.EnvironmentVersionProperties(AssetBase):
        auto_rebuild: Union[str, AutoRebuildSetting]
        build: BuildContext
        conda_file: str
        description: str
        environment_type: Union[str, EnvironmentType]
        image: str
        inference_config: InferenceContainerProperties
        is_anonymous: bool
        is_archived: bool
        os_type: Union[str, OperatingSystemType]
        properties: dict[str, str]
        provisioning_state: Union[str, AssetProvisioningState]
        stage: str
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                auto_rebuild: Optional[Union[str, AutoRebuildSetting]] = ..., 
                build: Optional[BuildContext] = ..., 
                conda_file: Optional[str] = ..., 
                description: Optional[str] = ..., 
                image: Optional[str] = ..., 
                inference_config: Optional[InferenceContainerProperties] = ..., 
                is_anonymous: bool = False, 
                is_archived: bool = False, 
                os_type: Optional[Union[str, OperatingSystemType]] = ..., 
                properties: Optional[Dict[str, str]] = ..., 
                stage: Optional[str] = ..., 
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


    class azure.mgmt.machinelearningservices.models.EnvironmentVersionResourceArmPaginatedResult(Model):
        next_link: str
        value: list[EnvironmentVersion]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[EnvironmentVersion]] = ..., 
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


    class azure.mgmt.machinelearningservices.models.ErrorAdditionalInfo(Model):
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


    class azure.mgmt.machinelearningservices.models.ErrorDetail(Model):
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


    class azure.mgmt.machinelearningservices.models.ErrorResponse(Model):
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


    class azure.mgmt.machinelearningservices.models.EstimatedVMPrice(Model):
        os_type: Union[str, VMPriceOSType]
        retail_price: float
        vm_tier: Union[str, VMTier]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                os_type: Union[str, VMPriceOSType], 
                retail_price: float, 
                vm_tier: Union[str, VMTier], 
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


    class azure.mgmt.machinelearningservices.models.EstimatedVMPrices(Model):
        billing_currency: Union[str, BillingCurrency]
        unit_of_measure: Union[str, UnitOfMeasure]
        values: list[EstimatedVMPrice]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                billing_currency: Union[str, BillingCurrency], 
                unit_of_measure: Union[str, UnitOfMeasure], 
                values: List[EstimatedVMPrice], 
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


    class azure.mgmt.machinelearningservices.models.ExternalFQDNResponse(Model):
        value: list[FQDNEndpoints]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[FQDNEndpoints]] = ..., 
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


    class azure.mgmt.machinelearningservices.models.FQDNEndpoint(Model):
        domain_name: str
        endpoint_details: list[FQDNEndpointDetail]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                domain_name: Optional[str] = ..., 
                endpoint_details: Optional[List[FQDNEndpointDetail]] = ..., 
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


    class azure.mgmt.machinelearningservices.models.FQDNEndpointDetail(Model):
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


    class azure.mgmt.machinelearningservices.models.FQDNEndpoints(Model):
        properties: FQDNEndpointsProperties

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[FQDNEndpointsProperties] = ..., 
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


    class azure.mgmt.machinelearningservices.models.FQDNEndpointsProperties(Model):
        category: str
        endpoints: list[FQDNEndpoint]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                category: Optional[str] = ..., 
                endpoints: Optional[List[FQDNEndpoint]] = ..., 
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


    class azure.mgmt.machinelearningservices.models.FeatureLags(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTO = "Auto"
        NONE = "None"


    class azure.mgmt.machinelearningservices.models.FeaturizationMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTO = "Auto"
        CUSTOM = "Custom"
        OFF = "Off"


    class azure.mgmt.machinelearningservices.models.FeaturizationSettings(Model):
        dataset_language: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                dataset_language: Optional[str] = ..., 
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


    class azure.mgmt.machinelearningservices.models.FlavorData(Model):
        data: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                data: Optional[Dict[str, str]] = ..., 
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


    class azure.mgmt.machinelearningservices.models.ForecastHorizon(Model):
        mode: Union[str, ForecastHorizonMode]

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


    class azure.mgmt.machinelearningservices.models.ForecastHorizonMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTO = "Auto"
        CUSTOM = "Custom"


    class azure.mgmt.machinelearningservices.models.Forecasting(TableVertical, AutoMLVertical):
        cv_split_column_names: list[str]
        featurization_settings: TableVerticalFeaturizationSettings
        forecasting_settings: ForecastingSettings
        limit_settings: TableVerticalLimitSettings
        log_verbosity: Union[str, LogVerbosity]
        n_cross_validations: NCrossValidations
        primary_metric: Union[str, ForecastingPrimaryMetrics]
        target_column_name: str
        task_type: Union[str, TaskType]
        test_data: MLTableJobInput
        test_data_size: float
        training_data: MLTableJobInput
        training_settings: ForecastingTrainingSettings
        validation_data: MLTableJobInput
        validation_data_size: float
        weight_column_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                cv_split_column_names: Optional[List[str]] = ..., 
                featurization_settings: Optional[TableVerticalFeaturizationSettings] = ..., 
                forecasting_settings: Optional[ForecastingSettings] = ..., 
                limit_settings: Optional[TableVerticalLimitSettings] = ..., 
                log_verbosity: Optional[Union[str, LogVerbosity]] = ..., 
                n_cross_validations: Optional[NCrossValidations] = ..., 
                primary_metric: Optional[Union[str, ForecastingPrimaryMetrics]] = ..., 
                target_column_name: Optional[str] = ..., 
                test_data: Optional[MLTableJobInput] = ..., 
                test_data_size: Optional[float] = ..., 
                training_data: MLTableJobInput, 
                training_settings: Optional[ForecastingTrainingSettings] = ..., 
                validation_data: Optional[MLTableJobInput] = ..., 
                validation_data_size: Optional[float] = ..., 
                weight_column_name: Optional[str] = ..., 
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


    class azure.mgmt.machinelearningservices.models.ForecastingModels(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ARIMAX = "Arimax"
        AUTO_ARIMA = "AutoArima"
        AVERAGE = "Average"
        DECISION_TREE = "DecisionTree"
        ELASTIC_NET = "ElasticNet"
        EXPONENTIAL_SMOOTHING = "ExponentialSmoothing"
        EXTREME_RANDOM_TREES = "ExtremeRandomTrees"
        GRADIENT_BOOSTING = "GradientBoosting"
        KNN = "KNN"
        LASSO_LARS = "LassoLars"
        LIGHT_GBM = "LightGBM"
        NAIVE = "Naive"
        PROPHET = "Prophet"
        RANDOM_FOREST = "RandomForest"
        SEASONAL_AVERAGE = "SeasonalAverage"
        SEASONAL_NAIVE = "SeasonalNaive"
        SGD = "SGD"
        TCN_FORECASTER = "TCNForecaster"
        XG_BOOST_REGRESSOR = "XGBoostRegressor"


    class azure.mgmt.machinelearningservices.models.ForecastingPrimaryMetrics(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NORMALIZED_MEAN_ABSOLUTE_ERROR = "NormalizedMeanAbsoluteError"
        NORMALIZED_ROOT_MEAN_SQUARED_ERROR = "NormalizedRootMeanSquaredError"
        R2_SCORE = "R2Score"
        SPEARMAN_CORRELATION = "SpearmanCorrelation"


    class azure.mgmt.machinelearningservices.models.ForecastingSettings(Model):
        country_or_region_for_holidays: str
        cv_step_size: int
        feature_lags: Union[str, FeatureLags]
        forecast_horizon: ForecastHorizon
        frequency: str
        seasonality: Seasonality
        short_series_handling_config: Union[str, ShortSeriesHandlingConfiguration]
        target_aggregate_function: Union[str, TargetAggregationFunction]
        target_lags: TargetLags
        target_rolling_window_size: TargetRollingWindowSize
        time_column_name: str
        time_series_id_column_names: list[str]
        use_stl: Union[str, UseStl]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                country_or_region_for_holidays: Optional[str] = ..., 
                cv_step_size: Optional[int] = ..., 
                feature_lags: Optional[Union[str, FeatureLags]] = ..., 
                forecast_horizon: Optional[ForecastHorizon] = ..., 
                frequency: Optional[str] = ..., 
                seasonality: Optional[Seasonality] = ..., 
                short_series_handling_config: Optional[Union[str, ShortSeriesHandlingConfiguration]] = ..., 
                target_aggregate_function: Optional[Union[str, TargetAggregationFunction]] = ..., 
                target_lags: Optional[TargetLags] = ..., 
                target_rolling_window_size: Optional[TargetRollingWindowSize] = ..., 
                time_column_name: Optional[str] = ..., 
                time_series_id_column_names: Optional[List[str]] = ..., 
                use_stl: Optional[Union[str, UseStl]] = ..., 
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


    class azure.mgmt.machinelearningservices.models.ForecastingTrainingSettings(TrainingSettings):
        allowed_training_algorithms: Union[list[str, ForecastingModels]]
        blocked_training_algorithms: Union[list[str, ForecastingModels]]
        enable_dnn_training: bool
        enable_model_explainability: bool
        enable_onnx_compatible_models: bool
        enable_stack_ensemble: bool
        enable_vote_ensemble: bool
        ensemble_model_download_timeout: timedelta
        stack_ensemble_settings: StackEnsembleSettings

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                allowed_training_algorithms: Optional[List[Union[str, ForecastingModels]]] = ..., 
                blocked_training_algorithms: Optional[List[Union[str, ForecastingModels]]] = ..., 
                enable_dnn_training: bool = False, 
                enable_model_explainability: bool = True, 
                enable_onnx_compatible_models: bool = False, 
                enable_stack_ensemble: bool = True, 
                enable_vote_ensemble: bool = True, 
                ensemble_model_download_timeout: timedelta = "PT5M", 
                stack_ensemble_settings: Optional[StackEnsembleSettings] = ..., 
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


    class azure.mgmt.machinelearningservices.models.Goal(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MAXIMIZE = "Maximize"
        MINIMIZE = "Minimize"


    class azure.mgmt.machinelearningservices.models.GridSamplingAlgorithm(SamplingAlgorithm):
        sampling_algorithm_type: Union[str, SamplingAlgorithmType]

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


    class azure.mgmt.machinelearningservices.models.HDInsight(Compute, HDInsightSchema):
        compute_location: str
        compute_type: Union[str, ComputeType]
        created_on: datetime
        description: str
        disable_local_auth: bool
        is_attached_compute: bool
        modified_on: datetime
        properties: HDInsightProperties
        provisioning_errors: list[ErrorResponse]
        provisioning_state: Union[str, ProvisioningState]
        resource_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                compute_location: Optional[str] = ..., 
                description: Optional[str] = ..., 
                disable_local_auth: Optional[bool] = ..., 
                properties: Optional[HDInsightProperties] = ..., 
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


    class azure.mgmt.machinelearningservices.models.HDInsightProperties(Model):
        address: str
        administrator_account: VirtualMachineSshCredentials
        ssh_port: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                address: Optional[str] = ..., 
                administrator_account: Optional[VirtualMachineSshCredentials] = ..., 
                ssh_port: Optional[int] = ..., 
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


    class azure.mgmt.machinelearningservices.models.HDInsightSchema(Model):
        properties: HDInsightProperties

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[HDInsightProperties] = ..., 
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


    class azure.mgmt.machinelearningservices.models.IdAssetReference(AssetReferenceBase):
        asset_id: str
        reference_type: Union[str, ReferenceType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                asset_id: str, 
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


    class azure.mgmt.machinelearningservices.models.IdentityConfiguration(Model):
        identity_type: Union[str, IdentityConfigurationType]

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


    class azure.mgmt.machinelearningservices.models.IdentityConfigurationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AML_TOKEN = "AMLToken"
        MANAGED = "Managed"
        USER_IDENTITY = "UserIdentity"


    class azure.mgmt.machinelearningservices.models.IdentityForCmk(Model):
        user_assigned_identity: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
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


    class azure.mgmt.machinelearningservices.models.IdleShutdownSetting(Model):
        idle_time_before_shutdown: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                idle_time_before_shutdown: Optional[str] = ..., 
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


    class azure.mgmt.machinelearningservices.models.Image(Model):
        additional_properties: dict[str, any]
        reference: str
        type: Union[str, ImageType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                additional_properties: Optional[Dict[str, Any]] = ..., 
                reference: Optional[str] = ..., 
                type: Union[str, ImageType] = "docker", 
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


    class azure.mgmt.machinelearningservices.models.ImageClassification(ImageClassificationBase, AutoMLVertical):
        limit_settings: ImageLimitSettings
        log_verbosity: Union[str, LogVerbosity]
        model_settings: ImageModelSettingsClassification
        primary_metric: Union[str, ClassificationPrimaryMetrics]
        search_space: list[ImageModelDistributionSettingsClassification]
        sweep_settings: ImageSweepSettings
        target_column_name: str
        task_type: Union[str, TaskType]
        training_data: MLTableJobInput
        validation_data: MLTableJobInput
        validation_data_size: float

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                limit_settings: ImageLimitSettings, 
                log_verbosity: Optional[Union[str, LogVerbosity]] = ..., 
                model_settings: Optional[ImageModelSettingsClassification] = ..., 
                primary_metric: Optional[Union[str, ClassificationPrimaryMetrics]] = ..., 
                search_space: Optional[List[ImageModelDistributionSettingsClassification]] = ..., 
                sweep_settings: Optional[ImageSweepSettings] = ..., 
                target_column_name: Optional[str] = ..., 
                training_data: MLTableJobInput, 
                validation_data: Optional[MLTableJobInput] = ..., 
                validation_data_size: Optional[float] = ..., 
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


    class azure.mgmt.machinelearningservices.models.ImageClassificationBase(ImageVertical):
        limit_settings: ImageLimitSettings
        model_settings: ImageModelSettingsClassification
        search_space: list[ImageModelDistributionSettingsClassification]
        sweep_settings: ImageSweepSettings
        validation_data: MLTableJobInput
        validation_data_size: float

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                limit_settings: ImageLimitSettings, 
                model_settings: Optional[ImageModelSettingsClassification] = ..., 
                search_space: Optional[List[ImageModelDistributionSettingsClassification]] = ..., 
                sweep_settings: Optional[ImageSweepSettings] = ..., 
                validation_data: Optional[MLTableJobInput] = ..., 
                validation_data_size: Optional[float] = ..., 
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


    class azure.mgmt.machinelearningservices.models.ImageClassificationMultilabel(ImageClassificationBase, AutoMLVertical):
        limit_settings: ImageLimitSettings
        log_verbosity: Union[str, LogVerbosity]
        model_settings: ImageModelSettingsClassification
        primary_metric: Union[str, ClassificationMultilabelPrimaryMetrics]
        search_space: list[ImageModelDistributionSettingsClassification]
        sweep_settings: ImageSweepSettings
        target_column_name: str
        task_type: Union[str, TaskType]
        training_data: MLTableJobInput
        validation_data: MLTableJobInput
        validation_data_size: float

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                limit_settings: ImageLimitSettings, 
                log_verbosity: Optional[Union[str, LogVerbosity]] = ..., 
                model_settings: Optional[ImageModelSettingsClassification] = ..., 
                primary_metric: Optional[Union[str, ClassificationMultilabelPrimaryMetrics]] = ..., 
                search_space: Optional[List[ImageModelDistributionSettingsClassification]] = ..., 
                sweep_settings: Optional[ImageSweepSettings] = ..., 
                target_column_name: Optional[str] = ..., 
                training_data: MLTableJobInput, 
                validation_data: Optional[MLTableJobInput] = ..., 
                validation_data_size: Optional[float] = ..., 
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


    class azure.mgmt.machinelearningservices.models.ImageInstanceSegmentation(ImageObjectDetectionBase, AutoMLVertical):
        limit_settings: ImageLimitSettings
        log_verbosity: Union[str, LogVerbosity]
        model_settings: ImageModelSettingsObjectDetection
        primary_metric: Union[str, InstanceSegmentationPrimaryMetrics]
        search_space: list[ImageModelDistributionSettingsObjectDetection]
        sweep_settings: ImageSweepSettings
        target_column_name: str
        task_type: Union[str, TaskType]
        training_data: MLTableJobInput
        validation_data: MLTableJobInput
        validation_data_size: float

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                limit_settings: ImageLimitSettings, 
                log_verbosity: Optional[Union[str, LogVerbosity]] = ..., 
                model_settings: Optional[ImageModelSettingsObjectDetection] = ..., 
                primary_metric: Optional[Union[str, InstanceSegmentationPrimaryMetrics]] = ..., 
                search_space: Optional[List[ImageModelDistributionSettingsObjectDetection]] = ..., 
                sweep_settings: Optional[ImageSweepSettings] = ..., 
                target_column_name: Optional[str] = ..., 
                training_data: MLTableJobInput, 
                validation_data: Optional[MLTableJobInput] = ..., 
                validation_data_size: Optional[float] = ..., 
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


    class azure.mgmt.machinelearningservices.models.ImageLimitSettings(Model):
        max_concurrent_trials: int
        max_trials: int
        timeout: timedelta

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                max_concurrent_trials: int = 1, 
                max_trials: int = 1, 
                timeout: timedelta = "P7D", 
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


    class azure.mgmt.machinelearningservices.models.ImageMetadata(Model):
        current_image_version: str
        is_latest_os_image_version: bool
        latest_image_version: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                current_image_version: Optional[str] = ..., 
                is_latest_os_image_version: Optional[bool] = ..., 
                latest_image_version: Optional[str] = ..., 
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


    class azure.mgmt.machinelearningservices.models.ImageModelDistributionSettings(Model):
        ams_gradient: str
        augmentations: str
        beta1: str
        beta2: str
        distributed: str
        early_stopping: str
        early_stopping_delay: str
        early_stopping_patience: str
        enable_onnx_normalization: str
        evaluation_frequency: str
        gradient_accumulation_step: str
        layers_to_freeze: str
        learning_rate: str
        learning_rate_scheduler: str
        model_name: str
        momentum: str
        nesterov: str
        number_of_epochs: str
        number_of_workers: str
        optimizer: str
        random_seed: str
        step_lr_gamma: str
        step_lr_step_size: str
        training_batch_size: str
        validation_batch_size: str
        warmup_cosine_lr_cycles: str
        warmup_cosine_lr_warmup_epochs: str
        weight_decay: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                ams_gradient: Optional[str] = ..., 
                augmentations: Optional[str] = ..., 
                beta1: Optional[str] = ..., 
                beta2: Optional[str] = ..., 
                distributed: Optional[str] = ..., 
                early_stopping: Optional[str] = ..., 
                early_stopping_delay: Optional[str] = ..., 
                early_stopping_patience: Optional[str] = ..., 
                enable_onnx_normalization: Optional[str] = ..., 
                evaluation_frequency: Optional[str] = ..., 
                gradient_accumulation_step: Optional[str] = ..., 
                layers_to_freeze: Optional[str] = ..., 
                learning_rate: Optional[str] = ..., 
                learning_rate_scheduler: Optional[str] = ..., 
                model_name: Optional[str] = ..., 
                momentum: Optional[str] = ..., 
                nesterov: Optional[str] = ..., 
                number_of_epochs: Optional[str] = ..., 
                number_of_workers: Optional[str] = ..., 
                optimizer: Optional[str] = ..., 
                random_seed: Optional[str] = ..., 
                step_lr_gamma: Optional[str] = ..., 
                step_lr_step_size: Optional[str] = ..., 
                training_batch_size: Optional[str] = ..., 
                validation_batch_size: Optional[str] = ..., 
                warmup_cosine_lr_cycles: Optional[str] = ..., 
                warmup_cosine_lr_warmup_epochs: Optional[str] = ..., 
                weight_decay: Optional[str] = ..., 
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


    class azure.mgmt.machinelearningservices.models.ImageModelDistributionSettingsClassification(ImageModelDistributionSettings):
        ams_gradient: str
        augmentations: str
        beta1: str
        beta2: str
        distributed: str
        early_stopping: str
        early_stopping_delay: str
        early_stopping_patience: str
        enable_onnx_normalization: str
        evaluation_frequency: str
        gradient_accumulation_step: str
        layers_to_freeze: str
        learning_rate: str
        learning_rate_scheduler: str
        model_name: str
        momentum: str
        nesterov: str
        number_of_epochs: str
        number_of_workers: str
        optimizer: str
        random_seed: str
        step_lr_gamma: str
        step_lr_step_size: str
        training_batch_size: str
        training_crop_size: str
        validation_batch_size: str
        validation_crop_size: str
        validation_resize_size: str
        warmup_cosine_lr_cycles: str
        warmup_cosine_lr_warmup_epochs: str
        weight_decay: str
        weighted_loss: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                ams_gradient: Optional[str] = ..., 
                augmentations: Optional[str] = ..., 
                beta1: Optional[str] = ..., 
                beta2: Optional[str] = ..., 
                distributed: Optional[str] = ..., 
                early_stopping: Optional[str] = ..., 
                early_stopping_delay: Optional[str] = ..., 
                early_stopping_patience: Optional[str] = ..., 
                enable_onnx_normalization: Optional[str] = ..., 
                evaluation_frequency: Optional[str] = ..., 
                gradient_accumulation_step: Optional[str] = ..., 
                layers_to_freeze: Optional[str] = ..., 
                learning_rate: Optional[str] = ..., 
                learning_rate_scheduler: Optional[str] = ..., 
                model_name: Optional[str] = ..., 
                momentum: Optional[str] = ..., 
                nesterov: Optional[str] = ..., 
                number_of_epochs: Optional[str] = ..., 
                number_of_workers: Optional[str] = ..., 
                optimizer: Optional[str] = ..., 
                random_seed: Optional[str] = ..., 
                step_lr_gamma: Optional[str] = ..., 
                step_lr_step_size: Optional[str] = ..., 
                training_batch_size: Optional[str] = ..., 
                training_crop_size: Optional[str] = ..., 
                validation_batch_size: Optional[str] = ..., 
                validation_crop_size: Optional[str] = ..., 
                validation_resize_size: Optional[str] = ..., 
                warmup_cosine_lr_cycles: Optional[str] = ..., 
                warmup_cosine_lr_warmup_epochs: Optional[str] = ..., 
                weight_decay: Optional[str] = ..., 
                weighted_loss: Optional[str] = ..., 
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


    class azure.mgmt.machinelearningservices.models.ImageModelDistributionSettingsObjectDetection(ImageModelDistributionSettings):
        ams_gradient: str
        augmentations: str
        beta1: str
        beta2: str
        box_detections_per_image: str
        box_score_threshold: str
        distributed: str
        early_stopping: str
        early_stopping_delay: str
        early_stopping_patience: str
        enable_onnx_normalization: str
        evaluation_frequency: str
        gradient_accumulation_step: str
        image_size: str
        layers_to_freeze: str
        learning_rate: str
        learning_rate_scheduler: str
        max_size: str
        min_size: str
        model_name: str
        model_size: str
        momentum: str
        multi_scale: str
        nesterov: str
        nms_iou_threshold: str
        number_of_epochs: str
        number_of_workers: str
        optimizer: str
        random_seed: str
        step_lr_gamma: str
        step_lr_step_size: str
        tile_grid_size: str
        tile_overlap_ratio: str
        tile_predictions_nms_threshold: str
        training_batch_size: str
        validation_batch_size: str
        validation_iou_threshold: str
        validation_metric_type: str
        warmup_cosine_lr_cycles: str
        warmup_cosine_lr_warmup_epochs: str
        weight_decay: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                ams_gradient: Optional[str] = ..., 
                augmentations: Optional[str] = ..., 
                beta1: Optional[str] = ..., 
                beta2: Optional[str] = ..., 
                box_detections_per_image: Optional[str] = ..., 
                box_score_threshold: Optional[str] = ..., 
                distributed: Optional[str] = ..., 
                early_stopping: Optional[str] = ..., 
                early_stopping_delay: Optional[str] = ..., 
                early_stopping_patience: Optional[str] = ..., 
                enable_onnx_normalization: Optional[str] = ..., 
                evaluation_frequency: Optional[str] = ..., 
                gradient_accumulation_step: Optional[str] = ..., 
                image_size: Optional[str] = ..., 
                layers_to_freeze: Optional[str] = ..., 
                learning_rate: Optional[str] = ..., 
                learning_rate_scheduler: Optional[str] = ..., 
                max_size: Optional[str] = ..., 
                min_size: Optional[str] = ..., 
                model_name: Optional[str] = ..., 
                model_size: Optional[str] = ..., 
                momentum: Optional[str] = ..., 
                multi_scale: Optional[str] = ..., 
                nesterov: Optional[str] = ..., 
                nms_iou_threshold: Optional[str] = ..., 
                number_of_epochs: Optional[str] = ..., 
                number_of_workers: Optional[str] = ..., 
                optimizer: Optional[str] = ..., 
                random_seed: Optional[str] = ..., 
                step_lr_gamma: Optional[str] = ..., 
                step_lr_step_size: Optional[str] = ..., 
                tile_grid_size: Optional[str] = ..., 
                tile_overlap_ratio: Optional[str] = ..., 
                tile_predictions_nms_threshold: Optional[str] = ..., 
                training_batch_size: Optional[str] = ..., 
                validation_batch_size: Optional[str] = ..., 
                validation_iou_threshold: Optional[str] = ..., 
                validation_metric_type: Optional[str] = ..., 
                warmup_cosine_lr_cycles: Optional[str] = ..., 
                warmup_cosine_lr_warmup_epochs: Optional[str] = ..., 
                weight_decay: Optional[str] = ..., 
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


    class azure.mgmt.machinelearningservices.models.ImageModelSettings(Model):
        advanced_settings: str
        ams_gradient: bool
        augmentations: str
        beta1: float
        beta2: float
        checkpoint_frequency: int
        checkpoint_model: MLFlowModelJobInput
        checkpoint_run_id: str
        distributed: bool
        early_stopping: bool
        early_stopping_delay: int
        early_stopping_patience: int
        enable_onnx_normalization: bool
        evaluation_frequency: int
        gradient_accumulation_step: int
        layers_to_freeze: int
        learning_rate: float
        learning_rate_scheduler: Union[str, LearningRateScheduler]
        model_name: str
        momentum: float
        nesterov: bool
        number_of_epochs: int
        number_of_workers: int
        optimizer: Union[str, StochasticOptimizer]
        random_seed: int
        step_lr_gamma: float
        step_lr_step_size: int
        training_batch_size: int
        validation_batch_size: int
        warmup_cosine_lr_cycles: float
        warmup_cosine_lr_warmup_epochs: int
        weight_decay: float

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                advanced_settings: Optional[str] = ..., 
                ams_gradient: Optional[bool] = ..., 
                augmentations: Optional[str] = ..., 
                beta1: Optional[float] = ..., 
                beta2: Optional[float] = ..., 
                checkpoint_frequency: Optional[int] = ..., 
                checkpoint_model: Optional[MLFlowModelJobInput] = ..., 
                checkpoint_run_id: Optional[str] = ..., 
                distributed: Optional[bool] = ..., 
                early_stopping: Optional[bool] = ..., 
                early_stopping_delay: Optional[int] = ..., 
                early_stopping_patience: Optional[int] = ..., 
                enable_onnx_normalization: Optional[bool] = ..., 
                evaluation_frequency: Optional[int] = ..., 
                gradient_accumulation_step: Optional[int] = ..., 
                layers_to_freeze: Optional[int] = ..., 
                learning_rate: Optional[float] = ..., 
                learning_rate_scheduler: Optional[Union[str, LearningRateScheduler]] = ..., 
                model_name: Optional[str] = ..., 
                momentum: Optional[float] = ..., 
                nesterov: Optional[bool] = ..., 
                number_of_epochs: Optional[int] = ..., 
                number_of_workers: Optional[int] = ..., 
                optimizer: Optional[Union[str, StochasticOptimizer]] = ..., 
                random_seed: Optional[int] = ..., 
                step_lr_gamma: Optional[float] = ..., 
                step_lr_step_size: Optional[int] = ..., 
                training_batch_size: Optional[int] = ..., 
                validation_batch_size: Optional[int] = ..., 
                warmup_cosine_lr_cycles: Optional[float] = ..., 
                warmup_cosine_lr_warmup_epochs: Optional[int] = ..., 
                weight_decay: Optional[float] = ..., 
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


    class azure.mgmt.machinelearningservices.models.ImageModelSettingsClassification(ImageModelSettings):
        advanced_settings: str
        ams_gradient: bool
        augmentations: str
        beta1: float
        beta2: float
        checkpoint_frequency: int
        checkpoint_model: MLFlowModelJobInput
        checkpoint_run_id: str
        distributed: bool
        early_stopping: bool
        early_stopping_delay: int
        early_stopping_patience: int
        enable_onnx_normalization: bool
        evaluation_frequency: int
        gradient_accumulation_step: int
        layers_to_freeze: int
        learning_rate: float
        learning_rate_scheduler: Union[str, LearningRateScheduler]
        model_name: str
        momentum: float
        nesterov: bool
        number_of_epochs: int
        number_of_workers: int
        optimizer: Union[str, StochasticOptimizer]
        random_seed: int
        step_lr_gamma: float
        step_lr_step_size: int
        training_batch_size: int
        training_crop_size: int
        validation_batch_size: int
        validation_crop_size: int
        validation_resize_size: int
        warmup_cosine_lr_cycles: float
        warmup_cosine_lr_warmup_epochs: int
        weight_decay: float
        weighted_loss: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                advanced_settings: Optional[str] = ..., 
                ams_gradient: Optional[bool] = ..., 
                augmentations: Optional[str] = ..., 
                beta1: Optional[float] = ..., 
                beta2: Optional[float] = ..., 
                checkpoint_frequency: Optional[int] = ..., 
                checkpoint_model: Optional[MLFlowModelJobInput] = ..., 
                checkpoint_run_id: Optional[str] = ..., 
                distributed: Optional[bool] = ..., 
                early_stopping: Optional[bool] = ..., 
                early_stopping_delay: Optional[int] = ..., 
                early_stopping_patience: Optional[int] = ..., 
                enable_onnx_normalization: Optional[bool] = ..., 
                evaluation_frequency: Optional[int] = ..., 
                gradient_accumulation_step: Optional[int] = ..., 
                layers_to_freeze: Optional[int] = ..., 
                learning_rate: Optional[float] = ..., 
                learning_rate_scheduler: Optional[Union[str, LearningRateScheduler]] = ..., 
                model_name: Optional[str] = ..., 
                momentum: Optional[float] = ..., 
                nesterov: Optional[bool] = ..., 
                number_of_epochs: Optional[int] = ..., 
                number_of_workers: Optional[int] = ..., 
                optimizer: Optional[Union[str, StochasticOptimizer]] = ..., 
                random_seed: Optional[int] = ..., 
                step_lr_gamma: Optional[float] = ..., 
                step_lr_step_size: Optional[int] = ..., 
                training_batch_size: Optional[int] = ..., 
                training_crop_size: Optional[int] = ..., 
                validation_batch_size: Optional[int] = ..., 
                validation_crop_size: Optional[int] = ..., 
                validation_resize_size: Optional[int] = ..., 
                warmup_cosine_lr_cycles: Optional[float] = ..., 
                warmup_cosine_lr_warmup_epochs: Optional[int] = ..., 
                weight_decay: Optional[float] = ..., 
                weighted_loss: Optional[int] = ..., 
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


    class azure.mgmt.machinelearningservices.models.ImageModelSettingsObjectDetection(ImageModelSettings):
        advanced_settings: str
        ams_gradient: bool
        augmentations: str
        beta1: float
        beta2: float
        box_detections_per_image: int
        box_score_threshold: float
        checkpoint_frequency: int
        checkpoint_model: MLFlowModelJobInput
        checkpoint_run_id: str
        distributed: bool
        early_stopping: bool
        early_stopping_delay: int
        early_stopping_patience: int
        enable_onnx_normalization: bool
        evaluation_frequency: int
        gradient_accumulation_step: int
        image_size: int
        layers_to_freeze: int
        learning_rate: float
        learning_rate_scheduler: Union[str, LearningRateScheduler]
        max_size: int
        min_size: int
        model_name: str
        model_size: Union[str, ModelSize]
        momentum: float
        multi_scale: bool
        nesterov: bool
        nms_iou_threshold: float
        number_of_epochs: int
        number_of_workers: int
        optimizer: Union[str, StochasticOptimizer]
        random_seed: int
        step_lr_gamma: float
        step_lr_step_size: int
        tile_grid_size: str
        tile_overlap_ratio: float
        tile_predictions_nms_threshold: float
        training_batch_size: int
        validation_batch_size: int
        validation_iou_threshold: float
        validation_metric_type: Union[str, ValidationMetricType]
        warmup_cosine_lr_cycles: float
        warmup_cosine_lr_warmup_epochs: int
        weight_decay: float

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                advanced_settings: Optional[str] = ..., 
                ams_gradient: Optional[bool] = ..., 
                augmentations: Optional[str] = ..., 
                beta1: Optional[float] = ..., 
                beta2: Optional[float] = ..., 
                box_detections_per_image: Optional[int] = ..., 
                box_score_threshold: Optional[float] = ..., 
                checkpoint_frequency: Optional[int] = ..., 
                checkpoint_model: Optional[MLFlowModelJobInput] = ..., 
                checkpoint_run_id: Optional[str] = ..., 
                distributed: Optional[bool] = ..., 
                early_stopping: Optional[bool] = ..., 
                early_stopping_delay: Optional[int] = ..., 
                early_stopping_patience: Optional[int] = ..., 
                enable_onnx_normalization: Optional[bool] = ..., 
                evaluation_frequency: Optional[int] = ..., 
                gradient_accumulation_step: Optional[int] = ..., 
                image_size: Optional[int] = ..., 
                layers_to_freeze: Optional[int] = ..., 
                learning_rate: Optional[float] = ..., 
                learning_rate_scheduler: Optional[Union[str, LearningRateScheduler]] = ..., 
                max_size: Optional[int] = ..., 
                min_size: Optional[int] = ..., 
                model_name: Optional[str] = ..., 
                model_size: Optional[Union[str, ModelSize]] = ..., 
                momentum: Optional[float] = ..., 
                multi_scale: Optional[bool] = ..., 
                nesterov: Optional[bool] = ..., 
                nms_iou_threshold: Optional[float] = ..., 
                number_of_epochs: Optional[int] = ..., 
                number_of_workers: Optional[int] = ..., 
                optimizer: Optional[Union[str, StochasticOptimizer]] = ..., 
                random_seed: Optional[int] = ..., 
                step_lr_gamma: Optional[float] = ..., 
                step_lr_step_size: Optional[int] = ..., 
                tile_grid_size: Optional[str] = ..., 
                tile_overlap_ratio: Optional[float] = ..., 
                tile_predictions_nms_threshold: Optional[float] = ..., 
                training_batch_size: Optional[int] = ..., 
                validation_batch_size: Optional[int] = ..., 
                validation_iou_threshold: Optional[float] = ..., 
                validation_metric_type: Optional[Union[str, ValidationMetricType]] = ..., 
                warmup_cosine_lr_cycles: Optional[float] = ..., 
                warmup_cosine_lr_warmup_epochs: Optional[int] = ..., 
                weight_decay: Optional[float] = ..., 
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


    class azure.mgmt.machinelearningservices.models.ImageObjectDetection(ImageObjectDetectionBase, AutoMLVertical):
        limit_settings: ImageLimitSettings
        log_verbosity: Union[str, LogVerbosity]
        model_settings: ImageModelSettingsObjectDetection
        primary_metric: Union[str, ObjectDetectionPrimaryMetrics]
        search_space: list[ImageModelDistributionSettingsObjectDetection]
        sweep_settings: ImageSweepSettings
        target_column_name: str
        task_type: Union[str, TaskType]
        training_data: MLTableJobInput
        validation_data: MLTableJobInput
        validation_data_size: float

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                limit_settings: ImageLimitSettings, 
                log_verbosity: Optional[Union[str, LogVerbosity]] = ..., 
                model_settings: Optional[ImageModelSettingsObjectDetection] = ..., 
                primary_metric: Optional[Union[str, ObjectDetectionPrimaryMetrics]] = ..., 
                search_space: Optional[List[ImageModelDistributionSettingsObjectDetection]] = ..., 
                sweep_settings: Optional[ImageSweepSettings] = ..., 
                target_column_name: Optional[str] = ..., 
                training_data: MLTableJobInput, 
                validation_data: Optional[MLTableJobInput] = ..., 
                validation_data_size: Optional[float] = ..., 
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


    class azure.mgmt.machinelearningservices.models.ImageObjectDetectionBase(ImageVertical):
        limit_settings: ImageLimitSettings
        model_settings: ImageModelSettingsObjectDetection
        search_space: list[ImageModelDistributionSettingsObjectDetection]
        sweep_settings: ImageSweepSettings
        validation_data: MLTableJobInput
        validation_data_size: float

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                limit_settings: ImageLimitSettings, 
                model_settings: Optional[ImageModelSettingsObjectDetection] = ..., 
                search_space: Optional[List[ImageModelDistributionSettingsObjectDetection]] = ..., 
                sweep_settings: Optional[ImageSweepSettings] = ..., 
                validation_data: Optional[MLTableJobInput] = ..., 
                validation_data_size: Optional[float] = ..., 
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


    class azure.mgmt.machinelearningservices.models.ImageSweepSettings(Model):
        early_termination: EarlyTerminationPolicy
        sampling_algorithm: Union[str, SamplingAlgorithmType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                early_termination: Optional[EarlyTerminationPolicy] = ..., 
                sampling_algorithm: Union[str, SamplingAlgorithmType], 
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


    class azure.mgmt.machinelearningservices.models.ImageType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZUREML = "azureml"
        DOCKER = "docker"


    class azure.mgmt.machinelearningservices.models.ImageVertical(Model):
        limit_settings: ImageLimitSettings
        sweep_settings: ImageSweepSettings
        validation_data: MLTableJobInput
        validation_data_size: float

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                limit_settings: ImageLimitSettings, 
                sweep_settings: Optional[ImageSweepSettings] = ..., 
                validation_data: Optional[MLTableJobInput] = ..., 
                validation_data_size: Optional[float] = ..., 
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


    class azure.mgmt.machinelearningservices.models.InferenceContainerProperties(Model):
        liveness_route: Route
        readiness_route: Route
        scoring_route: Route

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                liveness_route: Optional[Route] = ..., 
                readiness_route: Optional[Route] = ..., 
                scoring_route: Optional[Route] = ..., 
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


    class azure.mgmt.machinelearningservices.models.InputDeliveryMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DIRECT = "Direct"
        DOWNLOAD = "Download"
        EVAL_DOWNLOAD = "EvalDownload"
        EVAL_MOUNT = "EvalMount"
        READ_ONLY_MOUNT = "ReadOnlyMount"
        READ_WRITE_MOUNT = "ReadWriteMount"


    class azure.mgmt.machinelearningservices.models.InstanceSegmentationPrimaryMetrics(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MEAN_AVERAGE_PRECISION = "MeanAveragePrecision"


    class azure.mgmt.machinelearningservices.models.InstanceTypeSchema(Model):
        node_selector: dict[str, str]
        resources: InstanceTypeSchemaResources

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                node_selector: Optional[Dict[str, str]] = ..., 
                resources: Optional[InstanceTypeSchemaResources] = ..., 
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


    class azure.mgmt.machinelearningservices.models.InstanceTypeSchemaResources(Model):
        limits: dict[str, str]
        requests: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                limits: Optional[Dict[str, str]] = ..., 
                requests: Optional[Dict[str, str]] = ..., 
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


    class azure.mgmt.machinelearningservices.models.JobBase(Resource):
        id: str
        name: str
        properties: JobBaseProperties
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: JobBaseProperties, 
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


    class azure.mgmt.machinelearningservices.models.JobBaseProperties(ResourceBase):
        component_id: str
        compute_id: str
        description: str
        display_name: str
        experiment_name: str
        identity: IdentityConfiguration
        is_archived: bool
        job_type: Union[str, JobType]
        properties: dict[str, str]
        services: dict[str, JobService]
        status: Union[str, JobStatus]
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                component_id: Optional[str] = ..., 
                compute_id: Optional[str] = ..., 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                experiment_name: str = "Default", 
                identity: Optional[IdentityConfiguration] = ..., 
                is_archived: bool = False, 
                properties: Optional[Dict[str, str]] = ..., 
                services: Optional[Dict[str, JobService]] = ..., 
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


    class azure.mgmt.machinelearningservices.models.JobBaseResourceArmPaginatedResult(Model):
        next_link: str
        value: list[JobBase]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[JobBase]] = ..., 
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


    class azure.mgmt.machinelearningservices.models.JobInput(Model):
        description: str
        job_input_type: Union[str, JobInputType]

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


    class azure.mgmt.machinelearningservices.models.JobInputType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CUSTOM_MODEL = "custom_model"
        LITERAL = "literal"
        MLFLOW_MODEL = "mlflow_model"
        MLTABLE = "mltable"
        TRITON_MODEL = "triton_model"
        URI_FILE = "uri_file"
        URI_FOLDER = "uri_folder"


    class azure.mgmt.machinelearningservices.models.JobLimits(Model):
        job_limits_type: Union[str, JobLimitsType]
        timeout: timedelta

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                timeout: Optional[timedelta] = ..., 
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


    class azure.mgmt.machinelearningservices.models.JobLimitsType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMMAND = "Command"
        SWEEP = "Sweep"


    class azure.mgmt.machinelearningservices.models.JobOutput(Model):
        description: str
        job_output_type: Union[str, JobOutputType]

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


    class azure.mgmt.machinelearningservices.models.JobOutputType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CUSTOM_MODEL = "custom_model"
        MLFLOW_MODEL = "mlflow_model"
        MLTABLE = "mltable"
        TRITON_MODEL = "triton_model"
        URI_FILE = "uri_file"
        URI_FOLDER = "uri_folder"


    class azure.mgmt.machinelearningservices.models.JobResourceConfiguration(ResourceConfiguration):
        docker_args: str
        instance_count: int
        instance_type: str
        properties: dict[str, JSON]
        shm_size: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                docker_args: Optional[str] = ..., 
                instance_count: int = 1, 
                instance_type: Optional[str] = ..., 
                properties: Optional[Dict[str, JSON]] = ..., 
                shm_size: str = "2g", 
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


    class azure.mgmt.machinelearningservices.models.JobScheduleAction(ScheduleActionBase):
        action_type: Union[str, ScheduleActionType]
        job_definition: JobBaseProperties

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                job_definition: JobBaseProperties, 
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


    class azure.mgmt.machinelearningservices.models.JobService(Model):
        endpoint: str
        error_message: str
        job_service_type: str
        nodes: Nodes
        port: int
        properties: dict[str, str]
        status: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                endpoint: Optional[str] = ..., 
                job_service_type: Optional[str] = ..., 
                nodes: Optional[Nodes] = ..., 
                port: Optional[int] = ..., 
                properties: Optional[Dict[str, str]] = ..., 
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


    class azure.mgmt.machinelearningservices.models.JobStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CANCEL_REQUESTED = "CancelRequested"
        COMPLETED = "Completed"
        FAILED = "Failed"
        FINALIZING = "Finalizing"
        NOT_RESPONDING = "NotResponding"
        NOT_STARTED = "NotStarted"
        PAUSED = "Paused"
        PREPARING = "Preparing"
        PROVISIONING = "Provisioning"
        QUEUED = "Queued"
        RUNNING = "Running"
        STARTING = "Starting"
        UNKNOWN = "Unknown"


    class azure.mgmt.machinelearningservices.models.JobType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTO_ML = "AutoML"
        COMMAND = "Command"
        PIPELINE = "Pipeline"
        SWEEP = "Sweep"


    class azure.mgmt.machinelearningservices.models.KeyType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PRIMARY = "Primary"
        SECONDARY = "Secondary"


    class azure.mgmt.machinelearningservices.models.Kubernetes(Compute, KubernetesSchema):
        compute_location: str
        compute_type: Union[str, ComputeType]
        created_on: datetime
        description: str
        disable_local_auth: bool
        is_attached_compute: bool
        modified_on: datetime
        properties: KubernetesProperties
        provisioning_errors: list[ErrorResponse]
        provisioning_state: Union[str, ProvisioningState]
        resource_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                compute_location: Optional[str] = ..., 
                description: Optional[str] = ..., 
                disable_local_auth: Optional[bool] = ..., 
                properties: Optional[KubernetesProperties] = ..., 
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


    class azure.mgmt.machinelearningservices.models.KubernetesOnlineDeployment(OnlineDeploymentProperties):
        app_insights_enabled: bool
        code_configuration: CodeConfiguration
        container_resource_requirements: ContainerResourceRequirements
        description: str
        egress_public_network_access: Union[str, EgressPublicNetworkAccessType]
        endpoint_compute_type: Union[str, EndpointComputeType]
        environment_id: str
        environment_variables: dict[str, str]
        instance_type: str
        liveness_probe: ProbeSettings
        model: str
        model_mount_path: str
        properties: dict[str, str]
        provisioning_state: Union[str, DeploymentProvisioningState]
        readiness_probe: ProbeSettings
        request_settings: OnlineRequestSettings
        scale_settings: OnlineScaleSettings

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                app_insights_enabled: bool = False, 
                code_configuration: Optional[CodeConfiguration] = ..., 
                container_resource_requirements: Optional[ContainerResourceRequirements] = ..., 
                description: Optional[str] = ..., 
                egress_public_network_access: Optional[Union[str, EgressPublicNetworkAccessType]] = ..., 
                environment_id: Optional[str] = ..., 
                environment_variables: Optional[Dict[str, str]] = ..., 
                instance_type: Optional[str] = ..., 
                liveness_probe: Optional[ProbeSettings] = ..., 
                model: Optional[str] = ..., 
                model_mount_path: Optional[str] = ..., 
                properties: Optional[Dict[str, str]] = ..., 
                readiness_probe: Optional[ProbeSettings] = ..., 
                request_settings: Optional[OnlineRequestSettings] = ..., 
                scale_settings: Optional[OnlineScaleSettings] = ..., 
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


    class azure.mgmt.machinelearningservices.models.KubernetesProperties(Model):
        default_instance_type: str
        extension_instance_release_train: str
        extension_principal_id: str
        instance_types: dict[str, InstanceTypeSchema]
        namespace: str
        relay_connection_string: str
        service_bus_connection_string: str
        vc_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                default_instance_type: Optional[str] = ..., 
                extension_instance_release_train: Optional[str] = ..., 
                extension_principal_id: Optional[str] = ..., 
                instance_types: Optional[Dict[str, InstanceTypeSchema]] = ..., 
                namespace: str = "default", 
                relay_connection_string: Optional[str] = ..., 
                service_bus_connection_string: Optional[str] = ..., 
                vc_name: Optional[str] = ..., 
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


    class azure.mgmt.machinelearningservices.models.KubernetesSchema(Model):
        properties: KubernetesProperties

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[KubernetesProperties] = ..., 
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


    class azure.mgmt.machinelearningservices.models.LearningRateScheduler(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        STEP = "Step"
        WARMUP_COSINE = "WarmupCosine"


    class azure.mgmt.machinelearningservices.models.ListAmlUserFeatureResult(Model):
        next_link: str
        value: list[AmlUserFeature]

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


    class azure.mgmt.machinelearningservices.models.ListNotebookKeysResult(Model):
        primary_access_key: str
        secondary_access_key: str

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


    class azure.mgmt.machinelearningservices.models.ListStorageAccountKeysResult(Model):
        user_storage_key: str

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


    class azure.mgmt.machinelearningservices.models.ListUsagesResult(Model):
        next_link: str
        value: list[Usage]

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


    class azure.mgmt.machinelearningservices.models.ListViewType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE_ONLY = "ActiveOnly"
        ALL = "All"
        ARCHIVED_ONLY = "ArchivedOnly"


    class azure.mgmt.machinelearningservices.models.ListWorkspaceKeysResult(Model):
        app_insights_instrumentation_key: str
        container_registry_credentials: RegistryListCredentialsResult
        notebook_access_keys: ListNotebookKeysResult
        user_storage_key: str
        user_storage_resource_id: str

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


    class azure.mgmt.machinelearningservices.models.ListWorkspaceQuotas(Model):
        next_link: str
        value: list[ResourceQuota]

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


    class azure.mgmt.machinelearningservices.models.LiteralJobInput(JobInput):
        description: str
        job_input_type: Union[str, JobInputType]
        value: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
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


    class azure.mgmt.machinelearningservices.models.LoadBalancerType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL_LOAD_BALANCER = "InternalLoadBalancer"
        PUBLIC_IP = "PublicIp"


    class azure.mgmt.machinelearningservices.models.LogVerbosity(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CRITICAL = "Critical"
        DEBUG = "Debug"
        ERROR = "Error"
        INFO = "Info"
        NOT_SET = "NotSet"
        WARNING = "Warning"


    class azure.mgmt.machinelearningservices.models.MLFlowModelJobInput(AssetJobInput, JobInput):
        description: str
        job_input_type: Union[str, JobInputType]
        mode: Union[str, InputDeliveryMode]
        uri: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                mode: Optional[Union[str, InputDeliveryMode]] = ..., 
                uri: str, 
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


    class azure.mgmt.machinelearningservices.models.MLFlowModelJobOutput(AssetJobOutput, JobOutput):
        description: str
        job_output_type: Union[str, JobOutputType]
        mode: Union[str, OutputDeliveryMode]
        uri: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                mode: Optional[Union[str, OutputDeliveryMode]] = ..., 
                uri: Optional[str] = ..., 
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


    class azure.mgmt.machinelearningservices.models.MLTableData(DataVersionBaseProperties):
        data_type: Union[str, DataType]
        data_uri: str
        description: str
        is_anonymous: bool
        is_archived: bool
        properties: dict[str, str]
        referenced_uris: list[str]
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                data_uri: str, 
                description: Optional[str] = ..., 
                is_anonymous: bool = False, 
                is_archived: bool = False, 
                properties: Optional[Dict[str, str]] = ..., 
                referenced_uris: Optional[List[str]] = ..., 
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


    class azure.mgmt.machinelearningservices.models.MLTableJobInput(AssetJobInput, JobInput):
        description: str
        job_input_type: Union[str, JobInputType]
        mode: Union[str, InputDeliveryMode]
        uri: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                mode: Optional[Union[str, InputDeliveryMode]] = ..., 
                uri: str, 
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


    class azure.mgmt.machinelearningservices.models.MLTableJobOutput(AssetJobOutput, JobOutput):
        description: str
        job_output_type: Union[str, JobOutputType]
        mode: Union[str, OutputDeliveryMode]
        uri: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                mode: Optional[Union[str, OutputDeliveryMode]] = ..., 
                uri: Optional[str] = ..., 
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


    class azure.mgmt.machinelearningservices.models.ManagedIdentity(IdentityConfiguration):
        client_id: str
        identity_type: Union[str, IdentityConfigurationType]
        object_id: str
        resource_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                client_id: Optional[str] = ..., 
                object_id: Optional[str] = ..., 
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


    class azure.mgmt.machinelearningservices.models.ManagedIdentityAuthTypeWorkspaceConnectionProperties(WorkspaceConnectionPropertiesV2):
        auth_type: Union[str, ConnectionAuthType]
        category: Union[str, ConnectionCategory]
        credentials: WorkspaceConnectionManagedIdentity
        target: str
        value: str
        value_format: Union[str, ValueFormat]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                category: Optional[Union[str, ConnectionCategory]] = ..., 
                credentials: Optional[WorkspaceConnectionManagedIdentity] = ..., 
                target: Optional[str] = ..., 
                value: Optional[str] = ..., 
                value_format: Optional[Union[str, ValueFormat]] = ..., 
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


    class azure.mgmt.machinelearningservices.models.ManagedOnlineDeployment(OnlineDeploymentProperties):
        app_insights_enabled: bool
        code_configuration: CodeConfiguration
        description: str
        egress_public_network_access: Union[str, EgressPublicNetworkAccessType]
        endpoint_compute_type: Union[str, EndpointComputeType]
        environment_id: str
        environment_variables: dict[str, str]
        instance_type: str
        liveness_probe: ProbeSettings
        model: str
        model_mount_path: str
        properties: dict[str, str]
        provisioning_state: Union[str, DeploymentProvisioningState]
        readiness_probe: ProbeSettings
        request_settings: OnlineRequestSettings
        scale_settings: OnlineScaleSettings

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                app_insights_enabled: bool = False, 
                code_configuration: Optional[CodeConfiguration] = ..., 
                description: Optional[str] = ..., 
                egress_public_network_access: Optional[Union[str, EgressPublicNetworkAccessType]] = ..., 
                environment_id: Optional[str] = ..., 
                environment_variables: Optional[Dict[str, str]] = ..., 
                instance_type: Optional[str] = ..., 
                liveness_probe: Optional[ProbeSettings] = ..., 
                model: Optional[str] = ..., 
                model_mount_path: Optional[str] = ..., 
                properties: Optional[Dict[str, str]] = ..., 
                readiness_probe: Optional[ProbeSettings] = ..., 
                request_settings: Optional[OnlineRequestSettings] = ..., 
                scale_settings: Optional[OnlineScaleSettings] = ..., 
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


    class azure.mgmt.machinelearningservices.models.ManagedServiceIdentity(Model):
        principal_id: str
        tenant_id: str
        type: Union[str, ManagedServiceIdentityType]
        user_assigned_identities: dict[str, UserAssignedIdentity]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                type: Union[str, ManagedServiceIdentityType], 
                user_assigned_identities: Optional[Dict[str, UserAssignedIdentity]] = ..., 
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


    class azure.mgmt.machinelearningservices.models.ManagedServiceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        SYSTEM_ASSIGNED_USER_ASSIGNED = "SystemAssigned,UserAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.machinelearningservices.models.MedianStoppingPolicy(EarlyTerminationPolicy):
        delay_evaluation: int
        evaluation_interval: int
        policy_type: Union[str, EarlyTerminationPolicyType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                delay_evaluation: int = 0, 
                evaluation_interval: int = 0, 
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


    class azure.mgmt.machinelearningservices.models.ModelContainer(Resource):
        id: str
        name: str
        properties: ModelContainerProperties
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: ModelContainerProperties, 
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


    class azure.mgmt.machinelearningservices.models.ModelContainerProperties(AssetContainer):
        description: str
        is_archived: bool
        latest_version: str
        next_version: str
        properties: dict[str, str]
        provisioning_state: Union[str, AssetProvisioningState]
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                is_archived: bool = False, 
                properties: Optional[Dict[str, str]] = ..., 
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


    class azure.mgmt.machinelearningservices.models.ModelContainerResourceArmPaginatedResult(Model):
        next_link: str
        value: list[ModelContainer]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[ModelContainer]] = ..., 
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


    class azure.mgmt.machinelearningservices.models.ModelSize(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EXTRA_LARGE = "ExtraLarge"
        LARGE = "Large"
        MEDIUM = "Medium"
        NONE = "None"
        SMALL = "Small"


    class azure.mgmt.machinelearningservices.models.ModelVersion(Resource):
        id: str
        name: str
        properties: ModelVersionProperties
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: ModelVersionProperties, 
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


    class azure.mgmt.machinelearningservices.models.ModelVersionProperties(AssetBase):
        description: str
        flavors: dict[str, FlavorData]
        is_anonymous: bool
        is_archived: bool
        job_name: str
        model_type: str
        model_uri: str
        properties: dict[str, str]
        provisioning_state: Union[str, AssetProvisioningState]
        stage: str
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                flavors: Optional[Dict[str, FlavorData]] = ..., 
                is_anonymous: bool = False, 
                is_archived: bool = False, 
                job_name: Optional[str] = ..., 
                model_type: Optional[str] = ..., 
                model_uri: Optional[str] = ..., 
                properties: Optional[Dict[str, str]] = ..., 
                stage: Optional[str] = ..., 
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


    class azure.mgmt.machinelearningservices.models.ModelVersionResourceArmPaginatedResult(Model):
        next_link: str
        value: list[ModelVersion]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[ModelVersion]] = ..., 
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


    class azure.mgmt.machinelearningservices.models.MountAction(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MOUNT = "Mount"
        UNMOUNT = "Unmount"


    class azure.mgmt.machinelearningservices.models.MountState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MOUNTED = "Mounted"
        MOUNT_FAILED = "MountFailed"
        MOUNT_REQUESTED = "MountRequested"
        UNMOUNTED = "Unmounted"
        UNMOUNT_FAILED = "UnmountFailed"
        UNMOUNT_REQUESTED = "UnmountRequested"


    class azure.mgmt.machinelearningservices.models.Mpi(DistributionConfiguration):
        distribution_type: Union[str, DistributionType]
        process_count_per_instance: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                process_count_per_instance: Optional[int] = ..., 
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


    class azure.mgmt.machinelearningservices.models.NCrossValidations(Model):
        mode: Union[str, NCrossValidationsMode]

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


    class azure.mgmt.machinelearningservices.models.NCrossValidationsMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTO = "Auto"
        CUSTOM = "Custom"


    class azure.mgmt.machinelearningservices.models.Network(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BRIDGE = "Bridge"
        HOST = "Host"


    class azure.mgmt.machinelearningservices.models.NlpVertical(Model):
        featurization_settings: NlpVerticalFeaturizationSettings
        limit_settings: NlpVerticalLimitSettings
        validation_data: MLTableJobInput

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                featurization_settings: Optional[NlpVerticalFeaturizationSettings] = ..., 
                limit_settings: Optional[NlpVerticalLimitSettings] = ..., 
                validation_data: Optional[MLTableJobInput] = ..., 
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


    class azure.mgmt.machinelearningservices.models.NlpVerticalFeaturizationSettings(FeaturizationSettings):
        dataset_language: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                dataset_language: Optional[str] = ..., 
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


    class azure.mgmt.machinelearningservices.models.NlpVerticalLimitSettings(Model):
        max_concurrent_trials: int
        max_trials: int
        timeout: timedelta

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                max_concurrent_trials: int = 1, 
                max_trials: int = 1, 
                timeout: timedelta = "P7D", 
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


    class azure.mgmt.machinelearningservices.models.NodeState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        IDLE = "idle"
        LEAVING = "leaving"
        PREEMPTED = "preempted"
        PREPARING = "preparing"
        RUNNING = "running"
        UNUSABLE = "unusable"


    class azure.mgmt.machinelearningservices.models.NodeStateCounts(Model):
        idle_node_count: int
        leaving_node_count: int
        preempted_node_count: int
        preparing_node_count: int
        running_node_count: int
        unusable_node_count: int

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


    class azure.mgmt.machinelearningservices.models.Nodes(Model):
        nodes_value_type: Union[str, NodesValueType]

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


    class azure.mgmt.machinelearningservices.models.NodesValueType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALL = "All"


    class azure.mgmt.machinelearningservices.models.NoneAuthTypeWorkspaceConnectionProperties(WorkspaceConnectionPropertiesV2):
        auth_type: Union[str, ConnectionAuthType]
        category: Union[str, ConnectionCategory]
        target: str
        value: str
        value_format: Union[str, ValueFormat]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                category: Optional[Union[str, ConnectionCategory]] = ..., 
                target: Optional[str] = ..., 
                value: Optional[str] = ..., 
                value_format: Optional[Union[str, ValueFormat]] = ..., 
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


    class azure.mgmt.machinelearningservices.models.NoneDatastoreCredentials(DatastoreCredentials):
        credentials_type: Union[str, CredentialsType]

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


    class azure.mgmt.machinelearningservices.models.NotebookAccessTokenResult(Model):
        access_token: str
        expires_in: int
        host_name: str
        notebook_resource_id: str
        public_dns: str
        refresh_token: str
        scope: str
        token_type: str

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


    class azure.mgmt.machinelearningservices.models.NotebookPreparationError(Model):
        error_message: str
        status_code: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                error_message: Optional[str] = ..., 
                status_code: Optional[int] = ..., 
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


    class azure.mgmt.machinelearningservices.models.NotebookResourceInfo(Model):
        fqdn: str
        notebook_preparation_error: NotebookPreparationError
        resource_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                fqdn: Optional[str] = ..., 
                notebook_preparation_error: Optional[NotebookPreparationError] = ..., 
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


    class azure.mgmt.machinelearningservices.models.ObjectDetectionPrimaryMetrics(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MEAN_AVERAGE_PRECISION = "MeanAveragePrecision"


    class azure.mgmt.machinelearningservices.models.Objective(Model):
        goal: Union[str, Goal]
        primary_metric: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                goal: Union[str, Goal], 
                primary_metric: str, 
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


    class azure.mgmt.machinelearningservices.models.OnlineDeployment(TrackedResource):
        id: str
        identity: ManagedServiceIdentity
        kind: str
        location: str
        name: str
        properties: OnlineDeploymentProperties
        sku: Sku
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                kind: Optional[str] = ..., 
                location: str, 
                properties: OnlineDeploymentProperties, 
                sku: Optional[Sku] = ..., 
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


    class azure.mgmt.machinelearningservices.models.OnlineDeploymentProperties(EndpointDeploymentPropertiesBase):
        app_insights_enabled: bool
        code_configuration: CodeConfiguration
        description: str
        egress_public_network_access: Union[str, EgressPublicNetworkAccessType]
        endpoint_compute_type: Union[str, EndpointComputeType]
        environment_id: str
        environment_variables: dict[str, str]
        instance_type: str
        liveness_probe: ProbeSettings
        model: str
        model_mount_path: str
        properties: dict[str, str]
        provisioning_state: Union[str, DeploymentProvisioningState]
        readiness_probe: ProbeSettings
        request_settings: OnlineRequestSettings
        scale_settings: OnlineScaleSettings

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                app_insights_enabled: bool = False, 
                code_configuration: Optional[CodeConfiguration] = ..., 
                description: Optional[str] = ..., 
                egress_public_network_access: Optional[Union[str, EgressPublicNetworkAccessType]] = ..., 
                environment_id: Optional[str] = ..., 
                environment_variables: Optional[Dict[str, str]] = ..., 
                instance_type: Optional[str] = ..., 
                liveness_probe: Optional[ProbeSettings] = ..., 
                model: Optional[str] = ..., 
                model_mount_path: Optional[str] = ..., 
                properties: Optional[Dict[str, str]] = ..., 
                readiness_probe: Optional[ProbeSettings] = ..., 
                request_settings: Optional[OnlineRequestSettings] = ..., 
                scale_settings: Optional[OnlineScaleSettings] = ..., 
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


    class azure.mgmt.machinelearningservices.models.OnlineDeploymentTrackedResourceArmPaginatedResult(Model):
        next_link: str
        value: list[OnlineDeployment]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[OnlineDeployment]] = ..., 
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


    class azure.mgmt.machinelearningservices.models.OnlineEndpoint(TrackedResource):
        id: str
        identity: ManagedServiceIdentity
        kind: str
        location: str
        name: str
        properties: OnlineEndpointProperties
        sku: Sku
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                kind: Optional[str] = ..., 
                location: str, 
                properties: OnlineEndpointProperties, 
                sku: Optional[Sku] = ..., 
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


    class azure.mgmt.machinelearningservices.models.OnlineEndpointProperties(EndpointPropertiesBase):
        auth_mode: Union[str, EndpointAuthMode]
        compute: str
        description: str
        keys: EndpointAuthKeys
        mirror_traffic: dict[str, int]
        properties: dict[str, str]
        provisioning_state: Union[str, EndpointProvisioningState]
        public_network_access: Union[str, PublicNetworkAccessType]
        scoring_uri: str
        swagger_uri: str
        traffic: dict[str, int]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                auth_mode: Union[str, EndpointAuthMode], 
                compute: Optional[str] = ..., 
                description: Optional[str] = ..., 
                keys: Optional[EndpointAuthKeys] = ..., 
                mirror_traffic: Optional[Dict[str, int]] = ..., 
                properties: Optional[Dict[str, str]] = ..., 
                public_network_access: Optional[Union[str, PublicNetworkAccessType]] = ..., 
                traffic: Optional[Dict[str, int]] = ..., 
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


    class azure.mgmt.machinelearningservices.models.OnlineEndpointTrackedResourceArmPaginatedResult(Model):
        next_link: str
        value: list[OnlineEndpoint]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[OnlineEndpoint]] = ..., 
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


    class azure.mgmt.machinelearningservices.models.OnlineRequestSettings(Model):
        max_concurrent_requests_per_instance: int
        max_queue_wait: timedelta
        request_timeout: timedelta

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                max_concurrent_requests_per_instance: int = 1, 
                max_queue_wait: timedelta = "PT0.5S", 
                request_timeout: timedelta = "PT5S", 
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


    class azure.mgmt.machinelearningservices.models.OnlineScaleSettings(Model):
        scale_type: Union[str, ScaleType]

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


    class azure.mgmt.machinelearningservices.models.OperatingSystemType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LINUX = "Linux"
        WINDOWS = "Windows"


    class azure.mgmt.machinelearningservices.models.OperationName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREATE = "Create"
        DELETE = "Delete"
        REIMAGE = "Reimage"
        RESTART = "Restart"
        START = "Start"
        STOP = "Stop"


    class azure.mgmt.machinelearningservices.models.OperationStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREATE_FAILED = "CreateFailed"
        DELETE_FAILED = "DeleteFailed"
        IN_PROGRESS = "InProgress"
        REIMAGE_FAILED = "ReimageFailed"
        RESTART_FAILED = "RestartFailed"
        START_FAILED = "StartFailed"
        STOP_FAILED = "StopFailed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.machinelearningservices.models.OperationTrigger(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        IDLE_SHUTDOWN = "IdleShutdown"
        SCHEDULE = "Schedule"
        USER = "User"


    class azure.mgmt.machinelearningservices.models.OrderString(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREATED_AT_ASC = "CreatedAtAsc"
        CREATED_AT_DESC = "CreatedAtDesc"
        UPDATED_AT_ASC = "UpdatedAtAsc"
        UPDATED_AT_DESC = "UpdatedAtDesc"


    class azure.mgmt.machinelearningservices.models.OsType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LINUX = "Linux"
        WINDOWS = "Windows"


    class azure.mgmt.machinelearningservices.models.OutputDeliveryMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        READ_WRITE_MOUNT = "ReadWriteMount"
        UPLOAD = "Upload"


    class azure.mgmt.machinelearningservices.models.OutputPathAssetReference(AssetReferenceBase):
        job_id: str
        path: str
        reference_type: Union[str, ReferenceType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                job_id: Optional[str] = ..., 
                path: Optional[str] = ..., 
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


    class azure.mgmt.machinelearningservices.models.PATAuthTypeWorkspaceConnectionProperties(WorkspaceConnectionPropertiesV2):
        auth_type: Union[str, ConnectionAuthType]
        category: Union[str, ConnectionCategory]
        credentials: WorkspaceConnectionPersonalAccessToken
        target: str
        value: str
        value_format: Union[str, ValueFormat]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                category: Optional[Union[str, ConnectionCategory]] = ..., 
                credentials: Optional[WorkspaceConnectionPersonalAccessToken] = ..., 
                target: Optional[str] = ..., 
                value: Optional[str] = ..., 
                value_format: Optional[Union[str, ValueFormat]] = ..., 
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


    class azure.mgmt.machinelearningservices.models.PaginatedComputeResourcesList(Model):
        next_link: str
        value: list[ComputeResource]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[ComputeResource]] = ..., 
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


    class azure.mgmt.machinelearningservices.models.PartialBatchDeployment(Model):
        description: str

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


    class azure.mgmt.machinelearningservices.models.PartialBatchDeploymentPartialMinimalTrackedResourceWithProperties(Model):
        properties: PartialBatchDeployment
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[PartialBatchDeployment] = ..., 
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


    class azure.mgmt.machinelearningservices.models.PartialManagedServiceIdentity(Model):
        type: Union[str, ManagedServiceIdentityType]
        user_assigned_identities: dict[str, JSON]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                type: Optional[Union[str, ManagedServiceIdentityType]] = ..., 
                user_assigned_identities: Optional[Dict[str, JSON]] = ..., 
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


    class azure.mgmt.machinelearningservices.models.PartialMinimalTrackedResource(Model):
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


    class azure.mgmt.machinelearningservices.models.PartialMinimalTrackedResourceWithIdentity(PartialMinimalTrackedResource):
        identity: PartialManagedServiceIdentity
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                identity: Optional[PartialManagedServiceIdentity] = ..., 
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


    class azure.mgmt.machinelearningservices.models.PartialMinimalTrackedResourceWithSku(PartialMinimalTrackedResource):
        sku: PartialSku
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                sku: Optional[PartialSku] = ..., 
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


    class azure.mgmt.machinelearningservices.models.PartialRegistryPartialTrackedResource(Model):
        identity: RegistryPartialManagedServiceIdentity
        sku: PartialSku
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                identity: Optional[RegistryPartialManagedServiceIdentity] = ..., 
                sku: Optional[PartialSku] = ..., 
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


    class azure.mgmt.machinelearningservices.models.PartialSku(Model):
        capacity: int
        family: str
        name: str
        size: str
        tier: Union[str, SkuTier]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                capacity: Optional[int] = ..., 
                family: Optional[str] = ..., 
                name: Optional[str] = ..., 
                size: Optional[str] = ..., 
                tier: Optional[Union[str, SkuTier]] = ..., 
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


    class azure.mgmt.machinelearningservices.models.Password(Model):
        name: str
        value: str

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


    class azure.mgmt.machinelearningservices.models.PendingUploadCredentialDto(Model):
        credential_type: Union[str, PendingUploadCredentialType]

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


    class azure.mgmt.machinelearningservices.models.PendingUploadCredentialType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SAS = "SAS"


    class azure.mgmt.machinelearningservices.models.PendingUploadRequestDto(Model):
        pending_upload_id: str
        pending_upload_type: Union[str, PendingUploadType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                pending_upload_id: Optional[str] = ..., 
                pending_upload_type: Optional[Union[str, PendingUploadType]] = ..., 
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


    class azure.mgmt.machinelearningservices.models.PendingUploadResponseDto(Model):
        blob_reference_for_consumption: BlobReferenceForConsumptionDto
        pending_upload_id: str
        pending_upload_type: Union[str, PendingUploadType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                blob_reference_for_consumption: Optional[BlobReferenceForConsumptionDto] = ..., 
                pending_upload_id: Optional[str] = ..., 
                pending_upload_type: Optional[Union[str, PendingUploadType]] = ..., 
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


    class azure.mgmt.machinelearningservices.models.PendingUploadType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        TEMPORARY_BLOB_REFERENCE = "TemporaryBlobReference"


    class azure.mgmt.machinelearningservices.models.PersonalComputeInstanceSettings(Model):
        assigned_user: AssignedUser

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                assigned_user: Optional[AssignedUser] = ..., 
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


    class azure.mgmt.machinelearningservices.models.PipelineJob(JobBaseProperties):
        component_id: str
        compute_id: str
        description: str
        display_name: str
        experiment_name: str
        identity: IdentityConfiguration
        inputs: dict[str, JobInput]
        is_archived: bool
        job_type: Union[str, JobType]
        jobs: dict[str, JSON]
        outputs: dict[str, JobOutput]
        properties: dict[str, str]
        services: dict[str, JobService]
        settings: JSON
        source_job_id: str
        status: Union[str, JobStatus]
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                component_id: Optional[str] = ..., 
                compute_id: Optional[str] = ..., 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                experiment_name: str = "Default", 
                identity: Optional[IdentityConfiguration] = ..., 
                inputs: Optional[Dict[str, JobInput]] = ..., 
                is_archived: bool = False, 
                jobs: Optional[Dict[str, JSON]] = ..., 
                outputs: Optional[Dict[str, JobOutput]] = ..., 
                properties: Optional[Dict[str, str]] = ..., 
                services: Optional[Dict[str, JobService]] = ..., 
                settings: Optional[JSON] = ..., 
                source_job_id: Optional[str] = ..., 
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


    class azure.mgmt.machinelearningservices.models.PrivateEndpoint(Model):
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


    class azure.mgmt.machinelearningservices.models.PrivateEndpointConnection(Resource):
        id: str
        identity: ManagedServiceIdentity
        location: str
        name: str
        private_endpoint: PrivateEndpoint
        private_link_service_connection_state: PrivateLinkServiceConnectionState
        provisioning_state: Union[str, PrivateEndpointConnectionProvisioningState]
        sku: Sku
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                location: Optional[str] = ..., 
                private_endpoint: Optional[PrivateEndpoint] = ..., 
                private_link_service_connection_state: Optional[PrivateLinkServiceConnectionState] = ..., 
                sku: Optional[Sku] = ..., 
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


    class azure.mgmt.machinelearningservices.models.PrivateEndpointConnectionListResult(Model):
        value: list[PrivateEndpointConnection]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[PrivateEndpointConnection]] = ..., 
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


    class azure.mgmt.machinelearningservices.models.PrivateEndpointConnectionProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.machinelearningservices.models.PrivateEndpointResource(PrivateEndpoint):
        id: str
        subnet_arm_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                subnet_arm_id: Optional[str] = ..., 
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


    class azure.mgmt.machinelearningservices.models.PrivateEndpointServiceConnectionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPROVED = "Approved"
        DISCONNECTED = "Disconnected"
        PENDING = "Pending"
        REJECTED = "Rejected"
        TIMEOUT = "Timeout"


    class azure.mgmt.machinelearningservices.models.PrivateLinkResource(Resource):
        group_id: str
        id: str
        identity: ManagedServiceIdentity
        location: str
        name: str
        required_members: list[str]
        required_zone_names: list[str]
        sku: Sku
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                location: Optional[str] = ..., 
                required_zone_names: Optional[List[str]] = ..., 
                sku: Optional[Sku] = ..., 
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


    class azure.mgmt.machinelearningservices.models.PrivateLinkResourceListResult(Model):
        value: list[PrivateLinkResource]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[PrivateLinkResource]] = ..., 
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


    class azure.mgmt.machinelearningservices.models.PrivateLinkServiceConnectionState(Model):
        actions_required: str
        description: str
        status: Union[str, PrivateEndpointServiceConnectionStatus]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                actions_required: Optional[str] = ..., 
                description: Optional[str] = ..., 
                status: Optional[Union[str, PrivateEndpointServiceConnectionStatus]] = ..., 
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


    class azure.mgmt.machinelearningservices.models.ProbeSettings(Model):
        failure_threshold: int
        initial_delay: timedelta
        period: timedelta
        success_threshold: int
        timeout: timedelta

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                failure_threshold: int = 30, 
                initial_delay: Optional[timedelta] = ..., 
                period: timedelta = "PT10S", 
                success_threshold: int = 1, 
                timeout: timedelta = "PT2S", 
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


    class azure.mgmt.machinelearningservices.models.Protocol(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HTTP = "http"
        TCP = "tcp"
        UDP = "udp"


    class azure.mgmt.machinelearningservices.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UNKNOWN = "Unknown"
        UPDATING = "Updating"


    class azure.mgmt.machinelearningservices.models.ProvisioningStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLETED = "Completed"
        FAILED = "Failed"
        PROVISIONING = "Provisioning"


    class azure.mgmt.machinelearningservices.models.PublicNetworkAccess(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.machinelearningservices.models.PublicNetworkAccessType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.machinelearningservices.models.PyTorch(DistributionConfiguration):
        distribution_type: Union[str, DistributionType]
        process_count_per_instance: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                process_count_per_instance: Optional[int] = ..., 
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


    class azure.mgmt.machinelearningservices.models.QuotaBaseProperties(Model):
        id: str
        limit: int
        type: str
        unit: Union[str, QuotaUnit]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                limit: Optional[int] = ..., 
                type: Optional[str] = ..., 
                unit: Optional[Union[str, QuotaUnit]] = ..., 
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


    class azure.mgmt.machinelearningservices.models.QuotaUnit(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COUNT = "Count"


    class azure.mgmt.machinelearningservices.models.QuotaUpdateParameters(Model):
        location: str
        value: list[QuotaBaseProperties]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                value: Optional[List[QuotaBaseProperties]] = ..., 
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


    class azure.mgmt.machinelearningservices.models.RandomSamplingAlgorithm(SamplingAlgorithm):
        rule: Union[str, RandomSamplingAlgorithmRule]
        sampling_algorithm_type: Union[str, SamplingAlgorithmType]
        seed: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                rule: Optional[Union[str, RandomSamplingAlgorithmRule]] = ..., 
                seed: Optional[int] = ..., 
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


    class azure.mgmt.machinelearningservices.models.RandomSamplingAlgorithmRule(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        RANDOM = "Random"
        SOBOL = "Sobol"


    class azure.mgmt.machinelearningservices.models.Recurrence(Model):
        frequency: Union[str, RecurrenceFrequency]
        interval: int
        schedule: RecurrenceSchedule
        start_time: str
        time_zone: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                frequency: Optional[Union[str, RecurrenceFrequency]] = ..., 
                interval: Optional[int] = ..., 
                schedule: Optional[RecurrenceSchedule] = ..., 
                start_time: Optional[str] = ..., 
                time_zone: str = "UTC", 
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


    class azure.mgmt.machinelearningservices.models.RecurrenceFrequency(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DAY = "Day"
        HOUR = "Hour"
        MINUTE = "Minute"
        MONTH = "Month"
        WEEK = "Week"


    class azure.mgmt.machinelearningservices.models.RecurrenceSchedule(Model):
        hours: list[int]
        minutes: list[int]
        month_days: list[int]
        week_days: Union[list[str, WeekDay]]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                hours: List[int], 
                minutes: List[int], 
                month_days: Optional[List[int]] = ..., 
                week_days: Optional[List[Union[str, WeekDay]]] = ..., 
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


    class azure.mgmt.machinelearningservices.models.RecurrenceTrigger(TriggerBase):
        end_time: str
        frequency: Union[str, RecurrenceFrequency]
        interval: int
        schedule: RecurrenceSchedule
        start_time: str
        time_zone: str
        trigger_type: Union[str, TriggerType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                end_time: Optional[str] = ..., 
                frequency: Union[str, RecurrenceFrequency], 
                interval: int, 
                schedule: Optional[RecurrenceSchedule] = ..., 
                start_time: Optional[str] = ..., 
                time_zone: str = "UTC", 
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


    class azure.mgmt.machinelearningservices.models.ReferenceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DATA_PATH = "DataPath"
        ID = "Id"
        OUTPUT_PATH = "OutputPath"


    class azure.mgmt.machinelearningservices.models.RegenerateEndpointKeysRequest(Model):
        key_type: Union[str, KeyType]
        key_value: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                key_type: Union[str, KeyType], 
                key_value: Optional[str] = ..., 
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


    class azure.mgmt.machinelearningservices.models.Registry(TrackedResource):
        discovery_url: str
        id: str
        identity: ManagedServiceIdentity
        intellectual_property_publisher: str
        kind: str
        location: str
        managed_resource_group: ArmResourceId
        ml_flow_registry_uri: str
        name: str
        public_network_access: str
        region_details: list[RegistryRegionArmDetails]
        registry_private_endpoint_connections: list[RegistryPrivateEndpointConnection]
        sku: Sku
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                discovery_url: Optional[str] = ..., 
                identity: Optional[ManagedServiceIdentity] = ..., 
                intellectual_property_publisher: Optional[str] = ..., 
                kind: Optional[str] = ..., 
                location: str, 
                managed_resource_group: Optional[ArmResourceId] = ..., 
                ml_flow_registry_uri: Optional[str] = ..., 
                public_network_access: Optional[str] = ..., 
                region_details: Optional[List[RegistryRegionArmDetails]] = ..., 
                registry_private_endpoint_connections: Optional[List[RegistryPrivateEndpointConnection]] = ..., 
                sku: Optional[Sku] = ..., 
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


    class azure.mgmt.machinelearningservices.models.RegistryListCredentialsResult(Model):
        location: str
        passwords: list[Password]
        username: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                passwords: Optional[List[Password]] = ..., 
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


    class azure.mgmt.machinelearningservices.models.RegistryPartialManagedServiceIdentity(ManagedServiceIdentity):
        principal_id: str
        tenant_id: str
        type: Union[str, ManagedServiceIdentityType]
        user_assigned_identities: dict[str, UserAssignedIdentity]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                type: Union[str, ManagedServiceIdentityType], 
                user_assigned_identities: Optional[Dict[str, UserAssignedIdentity]] = ..., 
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


    class azure.mgmt.machinelearningservices.models.RegistryPrivateEndpointConnection(Model):
        group_ids: list[str]
        id: str
        location: str
        private_endpoint: PrivateEndpointResource
        provisioning_state: str
        registry_private_link_service_connection_state: RegistryPrivateLinkServiceConnectionState

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                group_ids: Optional[List[str]] = ..., 
                id: Optional[str] = ..., 
                location: Optional[str] = ..., 
                private_endpoint: Optional[PrivateEndpointResource] = ..., 
                provisioning_state: Optional[str] = ..., 
                registry_private_link_service_connection_state: Optional[RegistryPrivateLinkServiceConnectionState] = ..., 
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


    class azure.mgmt.machinelearningservices.models.RegistryPrivateLinkServiceConnectionState(Model):
        actions_required: str
        description: str
        status: Union[str, EndpointServiceConnectionStatus]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                actions_required: Optional[str] = ..., 
                description: Optional[str] = ..., 
                status: Optional[Union[str, EndpointServiceConnectionStatus]] = ..., 
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


    class azure.mgmt.machinelearningservices.models.RegistryRegionArmDetails(Model):
        acr_details: list[AcrDetails]
        location: str
        storage_account_details: list[StorageAccountDetails]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                acr_details: Optional[List[AcrDetails]] = ..., 
                location: Optional[str] = ..., 
                storage_account_details: Optional[List[StorageAccountDetails]] = ..., 
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


    class azure.mgmt.machinelearningservices.models.RegistryTrackedResourceArmPaginatedResult(Model):
        next_link: str
        value: list[Registry]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[Registry]] = ..., 
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


    class azure.mgmt.machinelearningservices.models.Regression(TableVertical, AutoMLVertical):
        cv_split_column_names: list[str]
        featurization_settings: TableVerticalFeaturizationSettings
        limit_settings: TableVerticalLimitSettings
        log_verbosity: Union[str, LogVerbosity]
        n_cross_validations: NCrossValidations
        primary_metric: Union[str, RegressionPrimaryMetrics]
        target_column_name: str
        task_type: Union[str, TaskType]
        test_data: MLTableJobInput
        test_data_size: float
        training_data: MLTableJobInput
        training_settings: RegressionTrainingSettings
        validation_data: MLTableJobInput
        validation_data_size: float
        weight_column_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                cv_split_column_names: Optional[List[str]] = ..., 
                featurization_settings: Optional[TableVerticalFeaturizationSettings] = ..., 
                limit_settings: Optional[TableVerticalLimitSettings] = ..., 
                log_verbosity: Optional[Union[str, LogVerbosity]] = ..., 
                n_cross_validations: Optional[NCrossValidations] = ..., 
                primary_metric: Optional[Union[str, RegressionPrimaryMetrics]] = ..., 
                target_column_name: Optional[str] = ..., 
                test_data: Optional[MLTableJobInput] = ..., 
                test_data_size: Optional[float] = ..., 
                training_data: MLTableJobInput, 
                training_settings: Optional[RegressionTrainingSettings] = ..., 
                validation_data: Optional[MLTableJobInput] = ..., 
                validation_data_size: Optional[float] = ..., 
                weight_column_name: Optional[str] = ..., 
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


    class azure.mgmt.machinelearningservices.models.RegressionModels(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DECISION_TREE = "DecisionTree"
        ELASTIC_NET = "ElasticNet"
        EXTREME_RANDOM_TREES = "ExtremeRandomTrees"
        GRADIENT_BOOSTING = "GradientBoosting"
        KNN = "KNN"
        LASSO_LARS = "LassoLars"
        LIGHT_GBM = "LightGBM"
        RANDOM_FOREST = "RandomForest"
        SGD = "SGD"
        XG_BOOST_REGRESSOR = "XGBoostRegressor"


    class azure.mgmt.machinelearningservices.models.RegressionPrimaryMetrics(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NORMALIZED_MEAN_ABSOLUTE_ERROR = "NormalizedMeanAbsoluteError"
        NORMALIZED_ROOT_MEAN_SQUARED_ERROR = "NormalizedRootMeanSquaredError"
        R2_SCORE = "R2Score"
        SPEARMAN_CORRELATION = "SpearmanCorrelation"


    class azure.mgmt.machinelearningservices.models.RegressionTrainingSettings(TrainingSettings):
        allowed_training_algorithms: Union[list[str, RegressionModels]]
        blocked_training_algorithms: Union[list[str, RegressionModels]]
        enable_dnn_training: bool
        enable_model_explainability: bool
        enable_onnx_compatible_models: bool
        enable_stack_ensemble: bool
        enable_vote_ensemble: bool
        ensemble_model_download_timeout: timedelta
        stack_ensemble_settings: StackEnsembleSettings

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                allowed_training_algorithms: Optional[List[Union[str, RegressionModels]]] = ..., 
                blocked_training_algorithms: Optional[List[Union[str, RegressionModels]]] = ..., 
                enable_dnn_training: bool = False, 
                enable_model_explainability: bool = True, 
                enable_onnx_compatible_models: bool = False, 
                enable_stack_ensemble: bool = True, 
                enable_vote_ensemble: bool = True, 
                ensemble_model_download_timeout: timedelta = "PT5M", 
                stack_ensemble_settings: Optional[StackEnsembleSettings] = ..., 
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


    class azure.mgmt.machinelearningservices.models.RemoteLoginPortPublicAccess(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"
        NOT_SPECIFIED = "NotSpecified"


    class azure.mgmt.machinelearningservices.models.Resource(Model):
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
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.machinelearningservices.models.ResourceBase(Model):
        description: str
        properties: dict[str, str]
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                properties: Optional[Dict[str, str]] = ..., 
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


    class azure.mgmt.machinelearningservices.models.ResourceConfiguration(Model):
        instance_count: int
        instance_type: str
        properties: dict[str, JSON]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                instance_count: int = 1, 
                instance_type: Optional[str] = ..., 
                properties: Optional[Dict[str, JSON]] = ..., 
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


    class azure.mgmt.machinelearningservices.models.ResourceId(Model):
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


    class azure.mgmt.machinelearningservices.models.ResourceName(Model):
        localized_value: str
        value: str

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


    class azure.mgmt.machinelearningservices.models.ResourceQuota(Model):
        aml_workspace_location: str
        id: str
        limit: int
        name: ResourceName
        type: str
        unit: Union[str, QuotaUnit]

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


    class azure.mgmt.machinelearningservices.models.Route(Model):
        path: str
        port: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                path: str, 
                port: int, 
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


    class azure.mgmt.machinelearningservices.models.SASAuthTypeWorkspaceConnectionProperties(WorkspaceConnectionPropertiesV2):
        auth_type: Union[str, ConnectionAuthType]
        category: Union[str, ConnectionCategory]
        credentials: WorkspaceConnectionSharedAccessSignature
        target: str
        value: str
        value_format: Union[str, ValueFormat]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                category: Optional[Union[str, ConnectionCategory]] = ..., 
                credentials: Optional[WorkspaceConnectionSharedAccessSignature] = ..., 
                target: Optional[str] = ..., 
                value: Optional[str] = ..., 
                value_format: Optional[Union[str, ValueFormat]] = ..., 
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


    class azure.mgmt.machinelearningservices.models.SASCredentialDto(PendingUploadCredentialDto):
        credential_type: Union[str, PendingUploadCredentialType]
        sas_uri: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                sas_uri: Optional[str] = ..., 
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


    class azure.mgmt.machinelearningservices.models.SamplingAlgorithm(Model):
        sampling_algorithm_type: Union[str, SamplingAlgorithmType]

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


    class azure.mgmt.machinelearningservices.models.SamplingAlgorithmType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BAYESIAN = "Bayesian"
        GRID = "Grid"
        RANDOM = "Random"


    class azure.mgmt.machinelearningservices.models.SasDatastoreCredentials(DatastoreCredentials):
        credentials_type: Union[str, CredentialsType]
        secrets: SasDatastoreSecrets

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                secrets: SasDatastoreSecrets, 
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


    class azure.mgmt.machinelearningservices.models.SasDatastoreSecrets(DatastoreSecrets):
        sas_token: str
        secrets_type: Union[str, SecretsType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                sas_token: Optional[str] = ..., 
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


    class azure.mgmt.machinelearningservices.models.ScaleSettings(Model):
        max_node_count: int
        min_node_count: int
        node_idle_time_before_scale_down: timedelta

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                max_node_count: int, 
                min_node_count: int = 0, 
                node_idle_time_before_scale_down: Optional[timedelta] = ..., 
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


    class azure.mgmt.machinelearningservices.models.ScaleSettingsInformation(Model):
        scale_settings: ScaleSettings

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                scale_settings: Optional[ScaleSettings] = ..., 
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


    class azure.mgmt.machinelearningservices.models.ScaleType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEFAULT = "Default"
        TARGET_UTILIZATION = "TargetUtilization"


    class azure.mgmt.machinelearningservices.models.Schedule(Resource):
        id: str
        name: str
        properties: ScheduleProperties
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: ScheduleProperties, 
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


    class azure.mgmt.machinelearningservices.models.ScheduleActionBase(Model):
        action_type: Union[str, ScheduleActionType]

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


    class azure.mgmt.machinelearningservices.models.ScheduleActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREATE_JOB = "CreateJob"
        INVOKE_BATCH_ENDPOINT = "InvokeBatchEndpoint"


    class azure.mgmt.machinelearningservices.models.ScheduleBase(Model):
        id: str
        provisioning_status: Union[str, ScheduleProvisioningState]
        status: Union[str, ScheduleStatus]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                provisioning_status: Optional[Union[str, ScheduleProvisioningState]] = ..., 
                status: Optional[Union[str, ScheduleStatus]] = ..., 
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


    class azure.mgmt.machinelearningservices.models.ScheduleListViewType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALL = "All"
        DISABLED_ONLY = "DisabledOnly"
        ENABLED_ONLY = "EnabledOnly"


    class azure.mgmt.machinelearningservices.models.ScheduleProperties(ResourceBase):
        action: ScheduleActionBase
        description: str
        display_name: str
        is_enabled: bool
        properties: dict[str, str]
        provisioning_state: Union[str, ScheduleProvisioningStatus]
        tags: dict[str, str]
        trigger: TriggerBase

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                action: ScheduleActionBase, 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                is_enabled: bool = True, 
                properties: Optional[Dict[str, str]] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                trigger: TriggerBase, 
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


    class azure.mgmt.machinelearningservices.models.ScheduleProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLETED = "Completed"
        FAILED = "Failed"
        PROVISIONING = "Provisioning"


    class azure.mgmt.machinelearningservices.models.ScheduleProvisioningStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.machinelearningservices.models.ScheduleResourceArmPaginatedResult(Model):
        next_link: str
        value: list[Schedule]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[Schedule]] = ..., 
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


    class azure.mgmt.machinelearningservices.models.ScheduleStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.machinelearningservices.models.ScriptReference(Model):
        script_arguments: str
        script_data: str
        script_source: str
        timeout: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                script_arguments: Optional[str] = ..., 
                script_data: Optional[str] = ..., 
                script_source: Optional[str] = ..., 
                timeout: Optional[str] = ..., 
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


    class azure.mgmt.machinelearningservices.models.ScriptsToExecute(Model):
        creation_script: ScriptReference
        startup_script: ScriptReference

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                creation_script: Optional[ScriptReference] = ..., 
                startup_script: Optional[ScriptReference] = ..., 
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


    class azure.mgmt.machinelearningservices.models.Seasonality(Model):
        mode: Union[str, SeasonalityMode]

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


    class azure.mgmt.machinelearningservices.models.SeasonalityMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTO = "Auto"
        CUSTOM = "Custom"


    class azure.mgmt.machinelearningservices.models.SecretsType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCOUNT_KEY = "AccountKey"
        CERTIFICATE = "Certificate"
        SAS = "Sas"
        SERVICE_PRINCIPAL = "ServicePrincipal"


    class azure.mgmt.machinelearningservices.models.ServiceDataAccessAuthIdentity(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        WORKSPACE_SYSTEM_ASSIGNED_IDENTITY = "WorkspaceSystemAssignedIdentity"
        WORKSPACE_USER_ASSIGNED_IDENTITY = "WorkspaceUserAssignedIdentity"


    class azure.mgmt.machinelearningservices.models.ServiceManagedResourcesSettings(Model):
        cosmos_db: CosmosDbSettings

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                cosmos_db: Optional[CosmosDbSettings] = ..., 
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


    class azure.mgmt.machinelearningservices.models.ServicePrincipalDatastoreCredentials(DatastoreCredentials):
        authority_url: str
        client_id: str
        credentials_type: Union[str, CredentialsType]
        resource_url: str
        secrets: ServicePrincipalDatastoreSecrets
        tenant_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                authority_url: Optional[str] = ..., 
                client_id: str, 
                resource_url: Optional[str] = ..., 
                secrets: ServicePrincipalDatastoreSecrets, 
                tenant_id: str, 
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


    class azure.mgmt.machinelearningservices.models.ServicePrincipalDatastoreSecrets(DatastoreSecrets):
        client_secret: str
        secrets_type: Union[str, SecretsType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                client_secret: Optional[str] = ..., 
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


    class azure.mgmt.machinelearningservices.models.SetupScripts(Model):
        scripts: ScriptsToExecute

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                scripts: Optional[ScriptsToExecute] = ..., 
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


    class azure.mgmt.machinelearningservices.models.SharedPrivateLinkResource(Model):
        group_id: str
        name: str
        private_link_resource_id: str
        request_message: str
        status: Union[str, PrivateEndpointServiceConnectionStatus]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                group_id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                private_link_resource_id: Optional[str] = ..., 
                request_message: Optional[str] = ..., 
                status: Optional[Union[str, PrivateEndpointServiceConnectionStatus]] = ..., 
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


    class azure.mgmt.machinelearningservices.models.ShortSeriesHandlingConfiguration(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTO = "Auto"
        DROP = "Drop"
        NONE = "None"
        PAD = "Pad"


    class azure.mgmt.machinelearningservices.models.Sku(Model):
        capacity: int
        family: str
        name: str
        size: str
        tier: Union[str, SkuTier]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                capacity: Optional[int] = ..., 
                family: Optional[str] = ..., 
                name: str, 
                size: Optional[str] = ..., 
                tier: Optional[Union[str, SkuTier]] = ..., 
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


    class azure.mgmt.machinelearningservices.models.SkuCapacity(Model):
        default: int
        maximum: int
        minimum: int
        scale_type: Union[str, SkuScaleType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                default: int = 0, 
                maximum: int = 0, 
                minimum: int = 0, 
                scale_type: Optional[Union[str, SkuScaleType]] = ..., 
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


    class azure.mgmt.machinelearningservices.models.SkuResource(Model):
        capacity: SkuCapacity
        resource_type: str
        sku: SkuSetting

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                capacity: Optional[SkuCapacity] = ..., 
                sku: Optional[SkuSetting] = ..., 
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


    class azure.mgmt.machinelearningservices.models.SkuResourceArmPaginatedResult(Model):
        next_link: str
        value: list[SkuResource]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[SkuResource]] = ..., 
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


    class azure.mgmt.machinelearningservices.models.SkuScaleType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTOMATIC = "Automatic"
        MANUAL = "Manual"
        NONE = "None"


    class azure.mgmt.machinelearningservices.models.SkuSetting(Model):
        name: str
        tier: Union[str, SkuTier]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                name: str, 
                tier: Optional[Union[str, SkuTier]] = ..., 
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


    class azure.mgmt.machinelearningservices.models.SkuTier(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BASIC = "Basic"
        FREE = "Free"
        PREMIUM = "Premium"
        STANDARD = "Standard"


    class azure.mgmt.machinelearningservices.models.SourceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DATASET = "Dataset"
        DATASTORE = "Datastore"
        URI = "URI"


    class azure.mgmt.machinelearningservices.models.SshPublicAccess(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.machinelearningservices.models.SslConfigStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTO = "Auto"
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.machinelearningservices.models.SslConfiguration(Model):
        cert: str
        cname: str
        key: str
        leaf_domain_label: str
        overwrite_existing_domain: bool
        status: Union[str, SslConfigStatus]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                cert: Optional[str] = ..., 
                cname: Optional[str] = ..., 
                key: Optional[str] = ..., 
                leaf_domain_label: Optional[str] = ..., 
                overwrite_existing_domain: Optional[bool] = ..., 
                status: Optional[Union[str, SslConfigStatus]] = ..., 
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


    class azure.mgmt.machinelearningservices.models.StackEnsembleSettings(Model):
        stack_meta_learner_k_wargs: JSON
        stack_meta_learner_train_percentage: float
        stack_meta_learner_type: Union[str, StackMetaLearnerType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                stack_meta_learner_k_wargs: Optional[JSON] = ..., 
                stack_meta_learner_train_percentage: float = 0.2, 
                stack_meta_learner_type: Optional[Union[str, StackMetaLearnerType]] = ..., 
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


    class azure.mgmt.machinelearningservices.models.StackMetaLearnerType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ELASTIC_NET = "ElasticNet"
        ELASTIC_NET_CV = "ElasticNetCV"
        LIGHT_GBM_CLASSIFIER = "LightGBMClassifier"
        LIGHT_GBM_REGRESSOR = "LightGBMRegressor"
        LINEAR_REGRESSION = "LinearRegression"
        LOGISTIC_REGRESSION = "LogisticRegression"
        LOGISTIC_REGRESSION_CV = "LogisticRegressionCV"
        NONE = "None"


    class azure.mgmt.machinelearningservices.models.Status(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAILURE = "Failure"
        INVALID_QUOTA_BELOW_CLUSTER_MINIMUM = "InvalidQuotaBelowClusterMinimum"
        INVALID_QUOTA_EXCEEDS_SUBSCRIPTION_LIMIT = "InvalidQuotaExceedsSubscriptionLimit"
        INVALID_VM_FAMILY_NAME = "InvalidVMFamilyName"
        OPERATION_NOT_ENABLED_FOR_REGION = "OperationNotEnabledForRegion"
        OPERATION_NOT_SUPPORTED_FOR_SKU = "OperationNotSupportedForSku"
        SUCCESS = "Success"
        UNDEFINED = "Undefined"


    class azure.mgmt.machinelearningservices.models.StochasticOptimizer(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ADAM = "Adam"
        ADAMW = "Adamw"
        NONE = "None"
        SGD = "Sgd"


    class azure.mgmt.machinelearningservices.models.StorageAccountDetails(Model):
        system_created_storage_account: SystemCreatedStorageAccount
        user_created_storage_account: UserCreatedStorageAccount

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                system_created_storage_account: Optional[SystemCreatedStorageAccount] = ..., 
                user_created_storage_account: Optional[UserCreatedStorageAccount] = ..., 
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


    class azure.mgmt.machinelearningservices.models.StorageAccountType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PREMIUM_LRS = "Premium_LRS"
        STANDARD_LRS = "Standard_LRS"


    class azure.mgmt.machinelearningservices.models.SweepJob(JobBaseProperties):
        component_id: str
        compute_id: str
        description: str
        display_name: str
        early_termination: EarlyTerminationPolicy
        experiment_name: str
        identity: IdentityConfiguration
        inputs: dict[str, JobInput]
        is_archived: bool
        job_type: Union[str, JobType]
        limits: SweepJobLimits
        objective: Objective
        outputs: dict[str, JobOutput]
        properties: dict[str, str]
        sampling_algorithm: SamplingAlgorithm
        search_space: JSON
        services: dict[str, JobService]
        status: Union[str, JobStatus]
        tags: dict[str, str]
        trial: TrialComponent

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                component_id: Optional[str] = ..., 
                compute_id: Optional[str] = ..., 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                early_termination: Optional[EarlyTerminationPolicy] = ..., 
                experiment_name: str = "Default", 
                identity: Optional[IdentityConfiguration] = ..., 
                inputs: Optional[Dict[str, JobInput]] = ..., 
                is_archived: bool = False, 
                limits: Optional[SweepJobLimits] = ..., 
                objective: Objective, 
                outputs: Optional[Dict[str, JobOutput]] = ..., 
                properties: Optional[Dict[str, str]] = ..., 
                sampling_algorithm: SamplingAlgorithm, 
                search_space: JSON, 
                services: Optional[Dict[str, JobService]] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                trial: TrialComponent, 
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


    class azure.mgmt.machinelearningservices.models.SweepJobLimits(JobLimits):
        job_limits_type: Union[str, JobLimitsType]
        max_concurrent_trials: int
        max_total_trials: int
        timeout: timedelta
        trial_timeout: timedelta

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                max_concurrent_trials: Optional[int] = ..., 
                max_total_trials: Optional[int] = ..., 
                timeout: Optional[timedelta] = ..., 
                trial_timeout: Optional[timedelta] = ..., 
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


    class azure.mgmt.machinelearningservices.models.SynapseSpark(Compute):
        compute_location: str
        compute_type: Union[str, ComputeType]
        created_on: datetime
        description: str
        disable_local_auth: bool
        is_attached_compute: bool
        modified_on: datetime
        properties: SynapseSparkProperties
        provisioning_errors: list[ErrorResponse]
        provisioning_state: Union[str, ProvisioningState]
        resource_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                compute_location: Optional[str] = ..., 
                description: Optional[str] = ..., 
                disable_local_auth: Optional[bool] = ..., 
                properties: Optional[SynapseSparkProperties] = ..., 
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


    class azure.mgmt.machinelearningservices.models.SynapseSparkProperties(Model):
        auto_pause_properties: AutoPauseProperties
        auto_scale_properties: AutoScaleProperties
        node_count: int
        node_size: str
        node_size_family: str
        pool_name: str
        resource_group: str
        spark_version: str
        subscription_id: str
        workspace_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                auto_pause_properties: Optional[AutoPauseProperties] = ..., 
                auto_scale_properties: Optional[AutoScaleProperties] = ..., 
                node_count: Optional[int] = ..., 
                node_size: Optional[str] = ..., 
                node_size_family: Optional[str] = ..., 
                pool_name: Optional[str] = ..., 
                resource_group: Optional[str] = ..., 
                spark_version: Optional[str] = ..., 
                subscription_id: Optional[str] = ..., 
                workspace_name: Optional[str] = ..., 
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


    class azure.mgmt.machinelearningservices.models.SystemCreatedAcrAccount(Model):
        acr_account_name: str
        acr_account_sku: str
        arm_resource_id: ArmResourceId

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                acr_account_name: Optional[str] = ..., 
                acr_account_sku: Optional[str] = ..., 
                arm_resource_id: Optional[ArmResourceId] = ..., 
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


    class azure.mgmt.machinelearningservices.models.SystemCreatedStorageAccount(Model):
        allow_blob_public_access: bool
        arm_resource_id: ArmResourceId
        storage_account_hns_enabled: bool
        storage_account_name: str
        storage_account_type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                allow_blob_public_access: Optional[bool] = ..., 
                arm_resource_id: Optional[ArmResourceId] = ..., 
                storage_account_hns_enabled: Optional[bool] = ..., 
                storage_account_name: Optional[str] = ..., 
                storage_account_type: Optional[str] = ..., 
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


    class azure.mgmt.machinelearningservices.models.SystemData(Model):
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


    class azure.mgmt.machinelearningservices.models.SystemService(Model):
        public_ip_address: str
        system_service_type: str
        version: str

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


    class azure.mgmt.machinelearningservices.models.TableVertical(Model):
        cv_split_column_names: list[str]
        featurization_settings: TableVerticalFeaturizationSettings
        limit_settings: TableVerticalLimitSettings
        n_cross_validations: NCrossValidations
        test_data: MLTableJobInput
        test_data_size: float
        validation_data: MLTableJobInput
        validation_data_size: float
        weight_column_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                cv_split_column_names: Optional[List[str]] = ..., 
                featurization_settings: Optional[TableVerticalFeaturizationSettings] = ..., 
                limit_settings: Optional[TableVerticalLimitSettings] = ..., 
                n_cross_validations: Optional[NCrossValidations] = ..., 
                test_data: Optional[MLTableJobInput] = ..., 
                test_data_size: Optional[float] = ..., 
                validation_data: Optional[MLTableJobInput] = ..., 
                validation_data_size: Optional[float] = ..., 
                weight_column_name: Optional[str] = ..., 
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


    class azure.mgmt.machinelearningservices.models.TableVerticalFeaturizationSettings(FeaturizationSettings):
        blocked_transformers: Union[list[str, BlockedTransformers]]
        column_name_and_types: dict[str, str]
        dataset_language: str
        enable_dnn_featurization: bool
        mode: Union[str, FeaturizationMode]
        transformer_params: dict[str, list[ColumnTransformer]]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                blocked_transformers: Optional[List[Union[str, BlockedTransformers]]] = ..., 
                column_name_and_types: Optional[Dict[str, str]] = ..., 
                dataset_language: Optional[str] = ..., 
                enable_dnn_featurization: bool = False, 
                mode: Optional[Union[str, FeaturizationMode]] = ..., 
                transformer_params: Optional[Dict[str, List[ColumnTransformer]]] = ..., 
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


    class azure.mgmt.machinelearningservices.models.TableVerticalLimitSettings(Model):
        enable_early_termination: bool
        exit_score: float
        max_concurrent_trials: int
        max_cores_per_trial: int
        max_trials: int
        timeout: timedelta
        trial_timeout: timedelta

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                enable_early_termination: bool = True, 
                exit_score: Optional[float] = ..., 
                max_concurrent_trials: int = 1, 
                max_cores_per_trial: int = -1, 
                max_trials: int = 1000, 
                timeout: timedelta = "PT6H", 
                trial_timeout: timedelta = "PT30M", 
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


    class azure.mgmt.machinelearningservices.models.TargetAggregationFunction(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MAX = "Max"
        MEAN = "Mean"
        MIN = "Min"
        NONE = "None"
        SUM = "Sum"


    class azure.mgmt.machinelearningservices.models.TargetLags(Model):
        mode: Union[str, TargetLagsMode]

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


    class azure.mgmt.machinelearningservices.models.TargetLagsMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTO = "Auto"
        CUSTOM = "Custom"


    class azure.mgmt.machinelearningservices.models.TargetRollingWindowSize(Model):
        mode: Union[str, TargetRollingWindowSizeMode]

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


    class azure.mgmt.machinelearningservices.models.TargetRollingWindowSizeMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTO = "Auto"
        CUSTOM = "Custom"


    class azure.mgmt.machinelearningservices.models.TargetUtilizationScaleSettings(OnlineScaleSettings):
        max_instances: int
        min_instances: int
        polling_interval: timedelta
        scale_type: Union[str, ScaleType]
        target_utilization_percentage: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                max_instances: int = 1, 
                min_instances: int = 1, 
                polling_interval: timedelta = "PT1S", 
                target_utilization_percentage: int = 70, 
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


    class azure.mgmt.machinelearningservices.models.TaskType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CLASSIFICATION = "Classification"
        FORECASTING = "Forecasting"
        IMAGE_CLASSIFICATION = "ImageClassification"
        IMAGE_CLASSIFICATION_MULTILABEL = "ImageClassificationMultilabel"
        IMAGE_INSTANCE_SEGMENTATION = "ImageInstanceSegmentation"
        IMAGE_OBJECT_DETECTION = "ImageObjectDetection"
        REGRESSION = "Regression"
        TEXT_CLASSIFICATION = "TextClassification"
        TEXT_CLASSIFICATION_MULTILABEL = "TextClassificationMultilabel"
        TEXT_NER = "TextNER"


    class azure.mgmt.machinelearningservices.models.TensorFlow(DistributionConfiguration):
        distribution_type: Union[str, DistributionType]
        parameter_server_count: int
        worker_count: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                parameter_server_count: int = 0, 
                worker_count: Optional[int] = ..., 
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


    class azure.mgmt.machinelearningservices.models.TextClassification(NlpVertical, AutoMLVertical):
        featurization_settings: NlpVerticalFeaturizationSettings
        limit_settings: NlpVerticalLimitSettings
        log_verbosity: Union[str, LogVerbosity]
        primary_metric: Union[str, ClassificationPrimaryMetrics]
        target_column_name: str
        task_type: Union[str, TaskType]
        training_data: MLTableJobInput
        validation_data: MLTableJobInput

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                featurization_settings: Optional[NlpVerticalFeaturizationSettings] = ..., 
                limit_settings: Optional[NlpVerticalLimitSettings] = ..., 
                log_verbosity: Optional[Union[str, LogVerbosity]] = ..., 
                primary_metric: Optional[Union[str, ClassificationPrimaryMetrics]] = ..., 
                target_column_name: Optional[str] = ..., 
                training_data: MLTableJobInput, 
                validation_data: Optional[MLTableJobInput] = ..., 
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


    class azure.mgmt.machinelearningservices.models.TextClassificationMultilabel(NlpVertical, AutoMLVertical):
        featurization_settings: NlpVerticalFeaturizationSettings
        limit_settings: NlpVerticalLimitSettings
        log_verbosity: Union[str, LogVerbosity]
        primary_metric: Union[str, ClassificationMultilabelPrimaryMetrics]
        target_column_name: str
        task_type: Union[str, TaskType]
        training_data: MLTableJobInput
        validation_data: MLTableJobInput

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                featurization_settings: Optional[NlpVerticalFeaturizationSettings] = ..., 
                limit_settings: Optional[NlpVerticalLimitSettings] = ..., 
                log_verbosity: Optional[Union[str, LogVerbosity]] = ..., 
                target_column_name: Optional[str] = ..., 
                training_data: MLTableJobInput, 
                validation_data: Optional[MLTableJobInput] = ..., 
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


    class azure.mgmt.machinelearningservices.models.TextNer(NlpVertical, AutoMLVertical):
        featurization_settings: NlpVerticalFeaturizationSettings
        limit_settings: NlpVerticalLimitSettings
        log_verbosity: Union[str, LogVerbosity]
        primary_metric: Union[str, ClassificationPrimaryMetrics]
        target_column_name: str
        task_type: Union[str, TaskType]
        training_data: MLTableJobInput
        validation_data: MLTableJobInput

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                featurization_settings: Optional[NlpVerticalFeaturizationSettings] = ..., 
                limit_settings: Optional[NlpVerticalLimitSettings] = ..., 
                log_verbosity: Optional[Union[str, LogVerbosity]] = ..., 
                target_column_name: Optional[str] = ..., 
                training_data: MLTableJobInput, 
                validation_data: Optional[MLTableJobInput] = ..., 
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


    class azure.mgmt.machinelearningservices.models.TmpfsOptions(Model):
        size: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                size: Optional[int] = ..., 
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


    class azure.mgmt.machinelearningservices.models.TrackedResource(Resource):
        id: str
        location: str
        name: str
        system_data: SystemData
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


    class azure.mgmt.machinelearningservices.models.TrainingSettings(Model):
        enable_dnn_training: bool
        enable_model_explainability: bool
        enable_onnx_compatible_models: bool
        enable_stack_ensemble: bool
        enable_vote_ensemble: bool
        ensemble_model_download_timeout: timedelta
        stack_ensemble_settings: StackEnsembleSettings

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                enable_dnn_training: bool = False, 
                enable_model_explainability: bool = True, 
                enable_onnx_compatible_models: bool = False, 
                enable_stack_ensemble: bool = True, 
                enable_vote_ensemble: bool = True, 
                ensemble_model_download_timeout: timedelta = "PT5M", 
                stack_ensemble_settings: Optional[StackEnsembleSettings] = ..., 
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


    class azure.mgmt.machinelearningservices.models.TrialComponent(Model):
        code_id: str
        command: str
        distribution: DistributionConfiguration
        environment_id: str
        environment_variables: dict[str, str]
        resources: JobResourceConfiguration

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                code_id: Optional[str] = ..., 
                command: str, 
                distribution: Optional[DistributionConfiguration] = ..., 
                environment_id: str, 
                environment_variables: Optional[Dict[str, str]] = ..., 
                resources: Optional[JobResourceConfiguration] = ..., 
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


    class azure.mgmt.machinelearningservices.models.TriggerBase(Model):
        end_time: str
        start_time: str
        time_zone: str
        trigger_type: Union[str, TriggerType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                end_time: Optional[str] = ..., 
                start_time: Optional[str] = ..., 
                time_zone: str = "UTC", 
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


    class azure.mgmt.machinelearningservices.models.TriggerType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CRON = "Cron"
        RECURRENCE = "Recurrence"


    class azure.mgmt.machinelearningservices.models.TritonModelJobInput(AssetJobInput, JobInput):
        description: str
        job_input_type: Union[str, JobInputType]
        mode: Union[str, InputDeliveryMode]
        uri: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                mode: Optional[Union[str, InputDeliveryMode]] = ..., 
                uri: str, 
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


    class azure.mgmt.machinelearningservices.models.TritonModelJobOutput(AssetJobOutput, JobOutput):
        description: str
        job_output_type: Union[str, JobOutputType]
        mode: Union[str, OutputDeliveryMode]
        uri: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                mode: Optional[Union[str, OutputDeliveryMode]] = ..., 
                uri: Optional[str] = ..., 
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


    class azure.mgmt.machinelearningservices.models.TruncationSelectionPolicy(EarlyTerminationPolicy):
        delay_evaluation: int
        evaluation_interval: int
        policy_type: Union[str, EarlyTerminationPolicyType]
        truncation_percentage: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                delay_evaluation: int = 0, 
                evaluation_interval: int = 0, 
                truncation_percentage: int = 0, 
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


    class azure.mgmt.machinelearningservices.models.UnderlyingResourceAction(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DELETE = "Delete"
        DETACH = "Detach"


    class azure.mgmt.machinelearningservices.models.UnitOfMeasure(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ONE_HOUR = "OneHour"


    class azure.mgmt.machinelearningservices.models.UpdateWorkspaceQuotas(Model):
        id: str
        limit: int
        status: Union[str, Status]
        type: str
        unit: Union[str, QuotaUnit]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                limit: Optional[int] = ..., 
                status: Optional[Union[str, Status]] = ..., 
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


    class azure.mgmt.machinelearningservices.models.UpdateWorkspaceQuotasResult(Model):
        next_link: str
        value: list[UpdateWorkspaceQuotas]

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


    class azure.mgmt.machinelearningservices.models.UriFileDataVersion(DataVersionBaseProperties):
        data_type: Union[str, DataType]
        data_uri: str
        description: str
        is_anonymous: bool
        is_archived: bool
        properties: dict[str, str]
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                data_uri: str, 
                description: Optional[str] = ..., 
                is_anonymous: bool = False, 
                is_archived: bool = False, 
                properties: Optional[Dict[str, str]] = ..., 
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


    class azure.mgmt.machinelearningservices.models.UriFileJobInput(AssetJobInput, JobInput):
        description: str
        job_input_type: Union[str, JobInputType]
        mode: Union[str, InputDeliveryMode]
        uri: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                mode: Optional[Union[str, InputDeliveryMode]] = ..., 
                uri: str, 
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


    class azure.mgmt.machinelearningservices.models.UriFileJobOutput(AssetJobOutput, JobOutput):
        description: str
        job_output_type: Union[str, JobOutputType]
        mode: Union[str, OutputDeliveryMode]
        uri: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                mode: Optional[Union[str, OutputDeliveryMode]] = ..., 
                uri: Optional[str] = ..., 
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


    class azure.mgmt.machinelearningservices.models.UriFolderDataVersion(DataVersionBaseProperties):
        data_type: Union[str, DataType]
        data_uri: str
        description: str
        is_anonymous: bool
        is_archived: bool
        properties: dict[str, str]
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                data_uri: str, 
                description: Optional[str] = ..., 
                is_anonymous: bool = False, 
                is_archived: bool = False, 
                properties: Optional[Dict[str, str]] = ..., 
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


    class azure.mgmt.machinelearningservices.models.UriFolderJobInput(AssetJobInput, JobInput):
        description: str
        job_input_type: Union[str, JobInputType]
        mode: Union[str, InputDeliveryMode]
        uri: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                mode: Optional[Union[str, InputDeliveryMode]] = ..., 
                uri: str, 
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


    class azure.mgmt.machinelearningservices.models.UriFolderJobOutput(AssetJobOutput, JobOutput):
        description: str
        job_output_type: Union[str, JobOutputType]
        mode: Union[str, OutputDeliveryMode]
        uri: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                mode: Optional[Union[str, OutputDeliveryMode]] = ..., 
                uri: Optional[str] = ..., 
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


    class azure.mgmt.machinelearningservices.models.Usage(Model):
        aml_workspace_location: str
        current_value: int
        id: str
        limit: int
        name: UsageName
        type: str
        unit: Union[str, UsageUnit]

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


    class azure.mgmt.machinelearningservices.models.UsageName(Model):
        localized_value: str
        value: str

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


    class azure.mgmt.machinelearningservices.models.UsageUnit(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COUNT = "Count"


    class azure.mgmt.machinelearningservices.models.UseStl(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SEASON = "Season"
        SEASON_TREND = "SeasonTrend"


    class azure.mgmt.machinelearningservices.models.UserAccountCredentials(Model):
        admin_user_name: str
        admin_user_password: str
        admin_user_ssh_public_key: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                admin_user_name: str, 
                admin_user_password: Optional[str] = ..., 
                admin_user_ssh_public_key: Optional[str] = ..., 
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


    class azure.mgmt.machinelearningservices.models.UserAssignedIdentity(Model):
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


    class azure.mgmt.machinelearningservices.models.UserCreatedAcrAccount(Model):
        arm_resource_id: ArmResourceId

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                arm_resource_id: Optional[ArmResourceId] = ..., 
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


    class azure.mgmt.machinelearningservices.models.UserCreatedStorageAccount(Model):
        arm_resource_id: ArmResourceId

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                arm_resource_id: Optional[ArmResourceId] = ..., 
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


    class azure.mgmt.machinelearningservices.models.UserIdentity(IdentityConfiguration):
        identity_type: Union[str, IdentityConfigurationType]

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


    class azure.mgmt.machinelearningservices.models.UsernamePasswordAuthTypeWorkspaceConnectionProperties(WorkspaceConnectionPropertiesV2):
        auth_type: Union[str, ConnectionAuthType]
        category: Union[str, ConnectionCategory]
        credentials: WorkspaceConnectionUsernamePassword
        target: str
        value: str
        value_format: Union[str, ValueFormat]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                category: Optional[Union[str, ConnectionCategory]] = ..., 
                credentials: Optional[WorkspaceConnectionUsernamePassword] = ..., 
                target: Optional[str] = ..., 
                value: Optional[str] = ..., 
                value_format: Optional[Union[str, ValueFormat]] = ..., 
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


    class azure.mgmt.machinelearningservices.models.VMPriceOSType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LINUX = "Linux"
        WINDOWS = "Windows"


    class azure.mgmt.machinelearningservices.models.VMTier(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LOW_PRIORITY = "LowPriority"
        SPOT = "Spot"
        STANDARD = "Standard"


    class azure.mgmt.machinelearningservices.models.ValidationMetricType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COCO = "Coco"
        COCO_VOC = "CocoVoc"
        NONE = "None"
        VOC = "Voc"


    class azure.mgmt.machinelearningservices.models.ValueFormat(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        JSON = "JSON"


    class azure.mgmt.machinelearningservices.models.VirtualMachine(Compute, VirtualMachineSchema):
        compute_location: str
        compute_type: Union[str, ComputeType]
        created_on: datetime
        description: str
        disable_local_auth: bool
        is_attached_compute: bool
        modified_on: datetime
        properties: VirtualMachineSchemaProperties
        provisioning_errors: list[ErrorResponse]
        provisioning_state: Union[str, ProvisioningState]
        resource_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                compute_location: Optional[str] = ..., 
                description: Optional[str] = ..., 
                disable_local_auth: Optional[bool] = ..., 
                properties: Optional[VirtualMachineSchemaProperties] = ..., 
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


    class azure.mgmt.machinelearningservices.models.VirtualMachineImage(Model):
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


    class azure.mgmt.machinelearningservices.models.VirtualMachineSchema(Model):
        properties: VirtualMachineSchemaProperties

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[VirtualMachineSchemaProperties] = ..., 
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


    class azure.mgmt.machinelearningservices.models.VirtualMachineSchemaProperties(Model):
        address: str
        administrator_account: VirtualMachineSshCredentials
        is_notebook_instance_compute: bool
        notebook_server_port: int
        ssh_port: int
        virtual_machine_size: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                address: Optional[str] = ..., 
                administrator_account: Optional[VirtualMachineSshCredentials] = ..., 
                is_notebook_instance_compute: Optional[bool] = ..., 
                notebook_server_port: Optional[int] = ..., 
                ssh_port: Optional[int] = ..., 
                virtual_machine_size: Optional[str] = ..., 
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


    class azure.mgmt.machinelearningservices.models.VirtualMachineSecrets(ComputeSecrets, VirtualMachineSecretsSchema):
        administrator_account: VirtualMachineSshCredentials
        compute_type: Union[str, ComputeType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                administrator_account: Optional[VirtualMachineSshCredentials] = ..., 
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


    class azure.mgmt.machinelearningservices.models.VirtualMachineSecretsSchema(Model):
        administrator_account: VirtualMachineSshCredentials

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                administrator_account: Optional[VirtualMachineSshCredentials] = ..., 
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


    class azure.mgmt.machinelearningservices.models.VirtualMachineSize(Model):
        estimated_vm_prices: EstimatedVMPrices
        family: str
        gpus: int
        low_priority_capable: bool
        max_resource_volume_mb: int
        memory_gb: float
        name: str
        os_vhd_size_mb: int
        premium_io: bool
        supported_compute_types: list[str]
        v_cp_us: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                estimated_vm_prices: Optional[EstimatedVMPrices] = ..., 
                supported_compute_types: Optional[List[str]] = ..., 
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


    class azure.mgmt.machinelearningservices.models.VirtualMachineSizeListResult(Model):
        value: list[VirtualMachineSize]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[VirtualMachineSize]] = ..., 
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


    class azure.mgmt.machinelearningservices.models.VirtualMachineSshCredentials(Model):
        password: str
        private_key_data: str
        public_key_data: str
        username: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                password: Optional[str] = ..., 
                private_key_data: Optional[str] = ..., 
                public_key_data: Optional[str] = ..., 
                username: Optional[str] = ..., 
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


    class azure.mgmt.machinelearningservices.models.VmPriority(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEDICATED = "Dedicated"
        LOW_PRIORITY = "LowPriority"


    class azure.mgmt.machinelearningservices.models.VolumeDefinition(Model):
        bind: BindOptions
        consistency: str
        read_only: bool
        source: str
        target: str
        tmpfs: TmpfsOptions
        type: Union[str, VolumeDefinitionType]
        volume: VolumeOptions

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                bind: Optional[BindOptions] = ..., 
                consistency: Optional[str] = ..., 
                read_only: Optional[bool] = ..., 
                source: Optional[str] = ..., 
                target: Optional[str] = ..., 
                tmpfs: Optional[TmpfsOptions] = ..., 
                type: Union[str, VolumeDefinitionType] = "bind", 
                volume: Optional[VolumeOptions] = ..., 
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


    class azure.mgmt.machinelearningservices.models.VolumeDefinitionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BIND = "bind"
        NPIPE = "npipe"
        TMPFS = "tmpfs"
        VOLUME = "volume"


    class azure.mgmt.machinelearningservices.models.VolumeOptions(Model):
        nocopy: bool

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                nocopy: Optional[bool] = ..., 
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


    class azure.mgmt.machinelearningservices.models.WeekDay(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FRIDAY = "Friday"
        MONDAY = "Monday"
        SATURDAY = "Saturday"
        SUNDAY = "Sunday"
        THURSDAY = "Thursday"
        TUESDAY = "Tuesday"
        WEDNESDAY = "Wednesday"


    class azure.mgmt.machinelearningservices.models.Workspace(Resource):
        allow_public_access_when_behind_vnet: bool
        application_insights: str
        container_registry: str
        description: str
        discovery_url: str
        encryption: EncryptionProperty
        friendly_name: str
        hbi_workspace: bool
        id: str
        identity: ManagedServiceIdentity
        image_build_compute: str
        key_vault: str
        location: str
        ml_flow_tracking_uri: str
        name: str
        notebook_info: NotebookResourceInfo
        primary_user_assigned_identity: str
        private_endpoint_connections: list[PrivateEndpointConnection]
        private_link_count: int
        provisioning_state: Union[str, ProvisioningState]
        public_network_access: Union[str, PublicNetworkAccess]
        service_managed_resources_settings: ServiceManagedResourcesSettings
        service_provisioned_resource_group: str
        shared_private_link_resources: list[SharedPrivateLinkResource]
        sku: Sku
        storage_account: str
        storage_hns_enabled: bool
        system_data: SystemData
        tags: dict[str, str]
        tenant_id: str
        type: str
        v1_legacy_mode: bool
        workspace_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                allow_public_access_when_behind_vnet: bool = False, 
                application_insights: Optional[str] = ..., 
                container_registry: Optional[str] = ..., 
                description: Optional[str] = ..., 
                discovery_url: Optional[str] = ..., 
                encryption: Optional[EncryptionProperty] = ..., 
                friendly_name: Optional[str] = ..., 
                hbi_workspace: bool = False, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                image_build_compute: Optional[str] = ..., 
                key_vault: Optional[str] = ..., 
                location: Optional[str] = ..., 
                primary_user_assigned_identity: Optional[str] = ..., 
                public_network_access: Optional[Union[str, PublicNetworkAccess]] = ..., 
                service_managed_resources_settings: Optional[ServiceManagedResourcesSettings] = ..., 
                shared_private_link_resources: Optional[List[SharedPrivateLinkResource]] = ..., 
                sku: Optional[Sku] = ..., 
                storage_account: Optional[str] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                v1_legacy_mode: bool = False, 
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


    class azure.mgmt.machinelearningservices.models.WorkspaceConnectionManagedIdentity(Model):
        client_id: str
        resource_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                client_id: Optional[str] = ..., 
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


    class azure.mgmt.machinelearningservices.models.WorkspaceConnectionPersonalAccessToken(Model):
        pat: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                pat: Optional[str] = ..., 
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


    class azure.mgmt.machinelearningservices.models.WorkspaceConnectionPropertiesV2(Model):
        auth_type: Union[str, ConnectionAuthType]
        category: Union[str, ConnectionCategory]
        target: str
        value: str
        value_format: Union[str, ValueFormat]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                category: Optional[Union[str, ConnectionCategory]] = ..., 
                target: Optional[str] = ..., 
                value: Optional[str] = ..., 
                value_format: Optional[Union[str, ValueFormat]] = ..., 
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


    class azure.mgmt.machinelearningservices.models.WorkspaceConnectionPropertiesV2BasicResource(Resource):
        id: str
        name: str
        properties: WorkspaceConnectionPropertiesV2
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: WorkspaceConnectionPropertiesV2, 
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


    class azure.mgmt.machinelearningservices.models.WorkspaceConnectionPropertiesV2BasicResourceArmPaginatedResult(Model):
        next_link: str
        value: list[WorkspaceConnectionPropertiesV2BasicResource]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[WorkspaceConnectionPropertiesV2BasicResource]] = ..., 
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


    class azure.mgmt.machinelearningservices.models.WorkspaceConnectionSharedAccessSignature(Model):
        sas: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                sas: Optional[str] = ..., 
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


    class azure.mgmt.machinelearningservices.models.WorkspaceConnectionUsernamePassword(Model):
        password: str
        username: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                password: Optional[str] = ..., 
                username: Optional[str] = ..., 
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


    class azure.mgmt.machinelearningservices.models.WorkspaceListResult(Model):
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


    class azure.mgmt.machinelearningservices.models.WorkspaceUpdateParameters(Model):
        application_insights: str
        container_registry: str
        description: str
        friendly_name: str
        identity: ManagedServiceIdentity
        image_build_compute: str
        primary_user_assigned_identity: str
        public_network_access: Union[str, PublicNetworkAccess]
        service_managed_resources_settings: ServiceManagedResourcesSettings
        sku: Sku
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                application_insights: Optional[str] = ..., 
                container_registry: Optional[str] = ..., 
                description: Optional[str] = ..., 
                friendly_name: Optional[str] = ..., 
                identity: Optional[ManagedServiceIdentity] = ..., 
                image_build_compute: Optional[str] = ..., 
                primary_user_assigned_identity: Optional[str] = ..., 
                public_network_access: Optional[Union[str, PublicNetworkAccess]] = ..., 
                service_managed_resources_settings: Optional[ServiceManagedResourcesSettings] = ..., 
                sku: Optional[Sku] = ..., 
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


namespace azure.mgmt.machinelearningservices.operations

    class azure.mgmt.machinelearningservices.operations.BatchDeploymentsOperations:

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
                endpoint_name: str, 
                deployment_name: str, 
                body: BatchDeployment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BatchDeployment]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                endpoint_name: str, 
                deployment_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BatchDeployment]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                endpoint_name: str, 
                deployment_name: str, 
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
                endpoint_name: str, 
                deployment_name: str, 
                body: PartialBatchDeploymentPartialMinimalTrackedResourceWithProperties, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BatchDeployment]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                endpoint_name: str, 
                deployment_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BatchDeployment]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                endpoint_name: str, 
                deployment_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> BatchDeployment: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                endpoint_name: str, 
                order_by: Optional[str] = None, 
                top: Optional[int] = None, 
                skip: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[BatchDeployment]: ...


    class azure.mgmt.machinelearningservices.operations.BatchEndpointsOperations:

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
                endpoint_name: str, 
                body: BatchEndpoint, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BatchEndpoint]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                endpoint_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BatchEndpoint]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                endpoint_name: str, 
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
                endpoint_name: str, 
                body: PartialMinimalTrackedResourceWithIdentity, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BatchEndpoint]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                endpoint_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BatchEndpoint]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                endpoint_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> BatchEndpoint: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                count: Optional[int] = None, 
                skip: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[BatchEndpoint]: ...

        @distributed_trace
        def list_keys(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                endpoint_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> EndpointAuthKeys: ...


    class azure.mgmt.machinelearningservices.operations.CodeContainersOperations:

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
                name: str, 
                body: CodeContainer, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CodeContainer: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CodeContainer: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> CodeContainer: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                skip: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[CodeContainer]: ...


    class azure.mgmt.machinelearningservices.operations.CodeVersionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create_or_get_start_pending_upload(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                name: str, 
                version: str, 
                body: PendingUploadRequestDto, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PendingUploadResponseDto: ...

        @overload
        def create_or_get_start_pending_upload(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                name: str, 
                version: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PendingUploadResponseDto: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                name: str, 
                version: str, 
                body: CodeVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CodeVersion: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                name: str, 
                version: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CodeVersion: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                name: str, 
                version: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                name: str, 
                version: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> CodeVersion: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                name: str, 
                order_by: Optional[str] = None, 
                top: Optional[int] = None, 
                skip: Optional[str] = None, 
                hash: Optional[str] = None, 
                hash_version: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[CodeVersion]: ...


    class azure.mgmt.machinelearningservices.operations.ComponentContainersOperations:

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
                name: str, 
                body: ComponentContainer, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ComponentContainer: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ComponentContainer: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ComponentContainer: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                skip: Optional[str] = None, 
                list_view_type: Optional[Union[str, ListViewType]] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[ComponentContainer]: ...


    class azure.mgmt.machinelearningservices.operations.ComponentVersionsOperations:

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
                name: str, 
                version: str, 
                body: ComponentVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ComponentVersion: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                name: str, 
                version: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ComponentVersion: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                name: str, 
                version: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                name: str, 
                version: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ComponentVersion: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                name: str, 
                order_by: Optional[str] = None, 
                top: Optional[int] = None, 
                skip: Optional[str] = None, 
                list_view_type: Optional[Union[str, ListViewType]] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[ComponentVersion]: ...


    class azure.mgmt.machinelearningservices.operations.ComputeOperations:

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
                compute_name: str, 
                parameters: ComputeResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ComputeResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                compute_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ComputeResource]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                compute_name: str, 
                underlying_resource_action: Union[str, UnderlyingResourceAction], 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_restart(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                compute_name: str, 
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
                compute_name: str, 
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
                resource_group_name: str, 
                workspace_name: str, 
                compute_name: str, 
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
                compute_name: str, 
                parameters: ClusterUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ComputeResource]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                compute_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ComputeResource]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                compute_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ComputeResource: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                skip: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[ComputeResource]: ...

        @distributed_trace
        def list_keys(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                compute_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ComputeSecrets: ...

        @distributed_trace
        def list_nodes(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                compute_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[AmlComputeNodeInformation]: ...


    class azure.mgmt.machinelearningservices.operations.DataContainersOperations:

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
                name: str, 
                body: DataContainer, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DataContainer: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DataContainer: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> DataContainer: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                skip: Optional[str] = None, 
                list_view_type: Optional[Union[str, ListViewType]] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[DataContainer]: ...


    class azure.mgmt.machinelearningservices.operations.DataVersionsOperations:

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
                name: str, 
                version: str, 
                body: DataVersionBase, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DataVersionBase: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                name: str, 
                version: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DataVersionBase: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                name: str, 
                version: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                name: str, 
                version: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> DataVersionBase: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                name: str, 
                order_by: Optional[str] = None, 
                top: Optional[int] = None, 
                skip: Optional[str] = None, 
                tags: Optional[str] = None, 
                list_view_type: Optional[Union[str, ListViewType]] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[DataVersionBase]: ...


    class azure.mgmt.machinelearningservices.operations.DatastoresOperations:

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
                name: str, 
                body: Datastore, 
                skip_validation: bool = False, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Datastore: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                name: str, 
                body: IO, 
                skip_validation: bool = False, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Datastore: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Datastore: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                skip: Optional[str] = None, 
                count: int = 30, 
                is_default: Optional[bool] = None, 
                names: Optional[List[str]] = None, 
                search_text: Optional[str] = None, 
                order_by: Optional[str] = None, 
                order_by_asc: bool = False, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[Datastore]: ...

        @distributed_trace
        def list_secrets(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> DatastoreSecrets: ...


    class azure.mgmt.machinelearningservices.operations.EnvironmentContainersOperations:

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
                name: str, 
                body: EnvironmentContainer, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EnvironmentContainer: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EnvironmentContainer: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> EnvironmentContainer: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                skip: Optional[str] = None, 
                list_view_type: Optional[Union[str, ListViewType]] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[EnvironmentContainer]: ...


    class azure.mgmt.machinelearningservices.operations.EnvironmentVersionsOperations:

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
                name: str, 
                version: str, 
                body: EnvironmentVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EnvironmentVersion: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                name: str, 
                version: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EnvironmentVersion: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                name: str, 
                version: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                name: str, 
                version: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> EnvironmentVersion: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                name: str, 
                order_by: Optional[str] = None, 
                top: Optional[int] = None, 
                skip: Optional[str] = None, 
                list_view_type: Optional[Union[str, ListViewType]] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[EnvironmentVersion]: ...


    class azure.mgmt.machinelearningservices.operations.JobsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def begin_cancel(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                id: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                id: str, 
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
                workspace_name: str, 
                id: str, 
                body: JobBase, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JobBase: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                id: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JobBase: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> JobBase: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                skip: Optional[str] = None, 
                job_type: Optional[str] = None, 
                tag: Optional[str] = None, 
                list_view_type: Optional[Union[str, ListViewType]] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[JobBase]: ...


    class azure.mgmt.machinelearningservices.operations.ModelContainersOperations:

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
                name: str, 
                body: ModelContainer, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ModelContainer: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ModelContainer: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ModelContainer: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                skip: Optional[str] = None, 
                count: Optional[int] = None, 
                list_view_type: Optional[Union[str, ListViewType]] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[ModelContainer]: ...


    class azure.mgmt.machinelearningservices.operations.ModelVersionsOperations:

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
                name: str, 
                version: str, 
                body: ModelVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ModelVersion: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                name: str, 
                version: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ModelVersion: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                name: str, 
                version: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                name: str, 
                version: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ModelVersion: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                name: str, 
                skip: Optional[str] = None, 
                order_by: Optional[str] = None, 
                top: Optional[int] = None, 
                version: Optional[str] = None, 
                description: Optional[str] = None, 
                offset: Optional[int] = None, 
                tags: Optional[str] = None, 
                properties: Optional[str] = None, 
                feed: Optional[str] = None, 
                list_view_type: Optional[Union[str, ListViewType]] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[ModelVersion]: ...


    class azure.mgmt.machinelearningservices.operations.OnlineDeploymentsOperations:

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
                endpoint_name: str, 
                deployment_name: str, 
                body: OnlineDeployment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OnlineDeployment]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                endpoint_name: str, 
                deployment_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OnlineDeployment]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                endpoint_name: str, 
                deployment_name: str, 
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
                endpoint_name: str, 
                deployment_name: str, 
                body: PartialMinimalTrackedResourceWithSku, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OnlineDeployment]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                endpoint_name: str, 
                deployment_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OnlineDeployment]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                endpoint_name: str, 
                deployment_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> OnlineDeployment: ...

        @overload
        def get_logs(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                endpoint_name: str, 
                deployment_name: str, 
                body: DeploymentLogsRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DeploymentLogs: ...

        @overload
        def get_logs(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                endpoint_name: str, 
                deployment_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DeploymentLogs: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                endpoint_name: str, 
                order_by: Optional[str] = None, 
                top: Optional[int] = None, 
                skip: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[OnlineDeployment]: ...

        @distributed_trace
        def list_skus(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                endpoint_name: str, 
                deployment_name: str, 
                count: Optional[int] = None, 
                skip: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[SkuResource]: ...


    class azure.mgmt.machinelearningservices.operations.OnlineEndpointsOperations:

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
                endpoint_name: str, 
                body: OnlineEndpoint, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OnlineEndpoint]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                endpoint_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OnlineEndpoint]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                endpoint_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_regenerate_keys(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                endpoint_name: str, 
                body: RegenerateEndpointKeysRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_regenerate_keys(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                endpoint_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                endpoint_name: str, 
                body: PartialMinimalTrackedResourceWithIdentity, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OnlineEndpoint]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                endpoint_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OnlineEndpoint]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                endpoint_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> OnlineEndpoint: ...

        @distributed_trace
        def get_token(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                endpoint_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> EndpointAuthToken: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                name: Optional[str] = None, 
                count: Optional[int] = None, 
                compute_type: Optional[Union[str, EndpointComputeType]] = None, 
                skip: Optional[str] = None, 
                tags: Optional[str] = None, 
                properties: Optional[str] = None, 
                order_by: Optional[Union[str, OrderString]] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[OnlineEndpoint]: ...

        @distributed_trace
        def list_keys(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                endpoint_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> EndpointAuthKeys: ...


    class azure.mgmt.machinelearningservices.operations.Operations:

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
            ) -> Iterable[AmlOperation]: ...


    class azure.mgmt.machinelearningservices.operations.PrivateEndpointConnectionsOperations:

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
                private_endpoint_connection_name: str, 
                properties: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                private_endpoint_connection_name: str, 
                properties: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                private_endpoint_connection_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

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


    class azure.mgmt.machinelearningservices.operations.PrivateLinkResourcesOperations:

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
            ) -> PrivateLinkResourceListResult: ...


    class azure.mgmt.machinelearningservices.operations.QuotasOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def list(
                self, 
                location: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[ResourceQuota]: ...

        @overload
        def update(
                self, 
                location: str, 
                parameters: QuotaUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> UpdateWorkspaceQuotasResult: ...

        @overload
        def update(
                self, 
                location: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> UpdateWorkspaceQuotasResult: ...


    class azure.mgmt.machinelearningservices.operations.RegistriesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                body: Registry, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Registry]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Registry]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_remove_regions(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                body: Registry, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Registry]: ...

        @overload
        def begin_remove_regions(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Registry]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Registry: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[Registry]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[Registry]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                body: PartialRegistryPartialTrackedResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Registry: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Registry: ...


    class azure.mgmt.machinelearningservices.operations.RegistryCodeContainersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                code_name: str, 
                body: CodeContainer, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CodeContainer]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                code_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CodeContainer]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                code_name: str, 
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
                registry_name: str, 
                code_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> CodeContainer: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                skip: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[CodeContainer]: ...


    class azure.mgmt.machinelearningservices.operations.RegistryCodeVersionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                code_name: str, 
                version: str, 
                body: CodeVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CodeVersion]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                code_name: str, 
                version: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CodeVersion]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                code_name: str, 
                version: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def create_or_get_start_pending_upload(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                code_name: str, 
                version: str, 
                body: PendingUploadRequestDto, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PendingUploadResponseDto: ...

        @overload
        def create_or_get_start_pending_upload(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                code_name: str, 
                version: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PendingUploadResponseDto: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                code_name: str, 
                version: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> CodeVersion: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                code_name: str, 
                order_by: Optional[str] = None, 
                top: Optional[int] = None, 
                skip: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[CodeVersion]: ...


    class azure.mgmt.machinelearningservices.operations.RegistryComponentContainersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                component_name: str, 
                body: ComponentContainer, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ComponentContainer]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                component_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ComponentContainer]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                component_name: str, 
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
                registry_name: str, 
                component_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ComponentContainer: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                skip: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[ComponentContainer]: ...


    class azure.mgmt.machinelearningservices.operations.RegistryComponentVersionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                component_name: str, 
                version: str, 
                body: ComponentVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ComponentVersion]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                component_name: str, 
                version: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ComponentVersion]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                component_name: str, 
                version: str, 
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
                registry_name: str, 
                component_name: str, 
                version: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ComponentVersion: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                component_name: str, 
                order_by: Optional[str] = None, 
                top: Optional[int] = None, 
                skip: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[ComponentVersion]: ...


    class azure.mgmt.machinelearningservices.operations.RegistryDataContainersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                name: str, 
                body: DataContainer, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DataContainer]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DataContainer]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                name: str, 
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
                registry_name: str, 
                name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> DataContainer: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                skip: Optional[str] = None, 
                list_view_type: Optional[Union[str, ListViewType]] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[DataContainer]: ...


    class azure.mgmt.machinelearningservices.operations.RegistryDataVersionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                name: str, 
                version: str, 
                body: DataVersionBase, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DataVersionBase]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                name: str, 
                version: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DataVersionBase]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                name: str, 
                version: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def create_or_get_start_pending_upload(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                name: str, 
                version: str, 
                body: PendingUploadRequestDto, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PendingUploadResponseDto: ...

        @overload
        def create_or_get_start_pending_upload(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                name: str, 
                version: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PendingUploadResponseDto: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                name: str, 
                version: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> DataVersionBase: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                name: str, 
                order_by: Optional[str] = None, 
                top: Optional[int] = None, 
                skip: Optional[str] = None, 
                tags: Optional[str] = None, 
                list_view_type: Optional[Union[str, ListViewType]] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[DataVersionBase]: ...


    class azure.mgmt.machinelearningservices.operations.RegistryEnvironmentContainersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                environment_name: str, 
                body: EnvironmentContainer, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EnvironmentContainer]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                environment_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EnvironmentContainer]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                environment_name: str, 
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
                registry_name: str, 
                environment_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> EnvironmentContainer: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                skip: Optional[str] = None, 
                list_view_type: Optional[Union[str, ListViewType]] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[EnvironmentContainer]: ...


    class azure.mgmt.machinelearningservices.operations.RegistryEnvironmentVersionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                environment_name: str, 
                version: str, 
                body: EnvironmentVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EnvironmentVersion]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                environment_name: str, 
                version: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EnvironmentVersion]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                environment_name: str, 
                version: str, 
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
                registry_name: str, 
                environment_name: str, 
                version: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> EnvironmentVersion: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                environment_name: str, 
                order_by: Optional[str] = None, 
                top: Optional[int] = None, 
                skip: Optional[str] = None, 
                list_view_type: Optional[Union[str, ListViewType]] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[EnvironmentVersion]: ...


    class azure.mgmt.machinelearningservices.operations.RegistryModelContainersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                model_name: str, 
                body: ModelContainer, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ModelContainer]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                model_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ModelContainer]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                model_name: str, 
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
                registry_name: str, 
                model_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ModelContainer: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                skip: Optional[str] = None, 
                list_view_type: Optional[Union[str, ListViewType]] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[ModelContainer]: ...


    class azure.mgmt.machinelearningservices.operations.RegistryModelVersionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                model_name: str, 
                version: str, 
                body: ModelVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ModelVersion]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                model_name: str, 
                version: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ModelVersion]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                model_name: str, 
                version: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def create_or_get_start_pending_upload(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                model_name: str, 
                version: str, 
                body: PendingUploadRequestDto, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PendingUploadResponseDto: ...

        @overload
        def create_or_get_start_pending_upload(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                model_name: str, 
                version: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PendingUploadResponseDto: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                model_name: str, 
                version: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ModelVersion: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                model_name: str, 
                skip: Optional[str] = None, 
                order_by: Optional[str] = None, 
                top: Optional[int] = None, 
                version: Optional[str] = None, 
                description: Optional[str] = None, 
                tags: Optional[str] = None, 
                properties: Optional[str] = None, 
                list_view_type: Optional[Union[str, ListViewType]] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[ModelVersion]: ...


    class azure.mgmt.machinelearningservices.operations.SchedulesOperations:

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
                name: str, 
                body: Schedule, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Schedule]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Schedule]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                name: str, 
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
                name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Schedule: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                skip: Optional[str] = None, 
                list_view_type: Optional[Union[str, ScheduleListViewType]] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[Schedule]: ...


    class azure.mgmt.machinelearningservices.operations.UsagesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def list(
                self, 
                location: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[Usage]: ...


    class azure.mgmt.machinelearningservices.operations.VirtualMachineSizesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def list(
                self, 
                location: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> VirtualMachineSizeListResult: ...


    class azure.mgmt.machinelearningservices.operations.WorkspaceConnectionsOperations:

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
                connection_name: str, 
                parameters: WorkspaceConnectionPropertiesV2BasicResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> WorkspaceConnectionPropertiesV2BasicResource: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                connection_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> WorkspaceConnectionPropertiesV2BasicResource: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                connection_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                connection_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> WorkspaceConnectionPropertiesV2BasicResource: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                target: Optional[str] = None, 
                category: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[WorkspaceConnectionPropertiesV2BasicResource]: ...


    class azure.mgmt.machinelearningservices.operations.WorkspaceFeaturesOperations:

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
            ) -> Iterable[AmlUserFeature]: ...


    class azure.mgmt.machinelearningservices.operations.WorkspacesOperations:

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
                parameters: Workspace, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Workspace]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                parameters: IO, 
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
            ) -> LROPoller[None]: ...

        @overload
        def begin_diagnose(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                parameters: Optional[DiagnoseWorkspaceParameters] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DiagnoseResponseResult]: ...

        @overload
        def begin_diagnose(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                parameters: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DiagnoseResponseResult]: ...

        @distributed_trace
        def begin_prepare_notebook(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[NotebookResourceInfo]: ...

        @distributed_trace
        def begin_resync_keys(
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

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                parameters: WorkspaceUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Workspace]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                parameters: IO, 
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
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                skip: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[Workspace]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                skip: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[Workspace]: ...

        @distributed_trace
        def list_keys(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ListWorkspaceKeysResult: ...

        @distributed_trace
        def list_notebook_access_token(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> NotebookAccessTokenResult: ...

        @distributed_trace
        def list_notebook_keys(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ListNotebookKeysResult: ...

        @distributed_trace
        def list_outbound_network_dependencies_endpoints(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ExternalFQDNResponse: ...

        @distributed_trace
        def list_storage_account_keys(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ListStorageAccountKeysResult: ...


```