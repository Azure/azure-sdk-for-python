```py
namespace azure.mgmt.storagemover

    class azure.mgmt.storagemover.StorageMoverMgmtClient: implements ContextManager 
        agents: AgentsOperations
        connections: ConnectionsOperations
        endpoints: EndpointsOperations
        job_definitions: JobDefinitionsOperations
        job_runs: JobRunsOperations
        operations: Operations
        projects: ProjectsOperations
        storage_movers: StorageMoversOperations

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


namespace azure.mgmt.storagemover.aio

    class azure.mgmt.storagemover.aio.StorageMoverMgmtClient: implements AsyncContextManager 
        agents: AgentsOperations
        connections: ConnectionsOperations
        endpoints: EndpointsOperations
        job_definitions: JobDefinitionsOperations
        job_runs: JobRunsOperations
        operations: Operations
        projects: ProjectsOperations
        storage_movers: StorageMoversOperations

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


namespace azure.mgmt.storagemover.aio.operations

    class azure.mgmt.storagemover.aio.operations.AgentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                storage_mover_name: str, 
                agent_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                storage_mover_name: str, 
                agent_name: str, 
                agent: Agent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Agent: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                storage_mover_name: str, 
                agent_name: str, 
                agent: Agent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Agent: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                storage_mover_name: str, 
                agent_name: str, 
                agent: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Agent: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                storage_mover_name: str, 
                agent_name: str, 
                **kwargs: Any
            ) -> Agent: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                storage_mover_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Agent]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                storage_mover_name: str, 
                agent_name: str, 
                agent: AgentUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Agent: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                storage_mover_name: str, 
                agent_name: str, 
                agent: AgentUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Agent: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                storage_mover_name: str, 
                agent_name: str, 
                agent: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Agent: ...


    class azure.mgmt.storagemover.aio.operations.ConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-08-01', params_added_on={'2025-08-01': ['api_version', 'subscription_id', 'resource_group_name', 'storage_mover_name', 'connection_name']}, api_versions_list=['2025-08-01', '2025-12-01', '2026-05-01'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                storage_mover_name: str, 
                connection_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                storage_mover_name: str, 
                connection_name: str, 
                connection: Connection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Connection: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                storage_mover_name: str, 
                connection_name: str, 
                connection: Connection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Connection: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                storage_mover_name: str, 
                connection_name: str, 
                connection: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Connection: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-08-01', params_added_on={'2025-08-01': ['api_version', 'subscription_id', 'resource_group_name', 'storage_mover_name', 'connection_name', 'accept']}, api_versions_list=['2025-08-01', '2025-12-01', '2026-05-01'])
        async def get(
                self, 
                resource_group_name: str, 
                storage_mover_name: str, 
                connection_name: str, 
                **kwargs: Any
            ) -> Connection: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-08-01', params_added_on={'2025-08-01': ['api_version', 'subscription_id', 'resource_group_name', 'storage_mover_name', 'accept']}, api_versions_list=['2025-08-01', '2025-12-01', '2026-05-01'])
        def list(
                self, 
                resource_group_name: str, 
                storage_mover_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Connection]: ...


    class azure.mgmt.storagemover.aio.operations.EndpointsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                storage_mover_name: str, 
                endpoint_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                storage_mover_name: str, 
                endpoint_name: str, 
                endpoint: Endpoint, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Endpoint: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                storage_mover_name: str, 
                endpoint_name: str, 
                endpoint: Endpoint, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Endpoint: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                storage_mover_name: str, 
                endpoint_name: str, 
                endpoint: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Endpoint: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                storage_mover_name: str, 
                endpoint_name: str, 
                **kwargs: Any
            ) -> Endpoint: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                storage_mover_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Endpoint]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                storage_mover_name: str, 
                endpoint_name: str, 
                endpoint: EndpointBaseUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Endpoint: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                storage_mover_name: str, 
                endpoint_name: str, 
                endpoint: EndpointBaseUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Endpoint: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                storage_mover_name: str, 
                endpoint_name: str, 
                endpoint: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Endpoint: ...


    class azure.mgmt.storagemover.aio.operations.JobDefinitionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                storage_mover_name: str, 
                project_name: str, 
                job_definition_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                storage_mover_name: str, 
                project_name: str, 
                job_definition_name: str, 
                job_definition: JobDefinition, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JobDefinition: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                storage_mover_name: str, 
                project_name: str, 
                job_definition_name: str, 
                job_definition: JobDefinition, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JobDefinition: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                storage_mover_name: str, 
                project_name: str, 
                job_definition_name: str, 
                job_definition: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JobDefinition: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                storage_mover_name: str, 
                project_name: str, 
                job_definition_name: str, 
                **kwargs: Any
            ) -> JobDefinition: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                storage_mover_name: str, 
                project_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[JobDefinition]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-05-01', params_added_on={'2026-05-01': ['api_version', 'subscription_id', 'resource_group_name', 'storage_mover_name', 'project_name', 'job_definition_name', 'accept']}, api_versions_list=['2026-05-01'])
        async def reconcile_job(
                self, 
                resource_group_name: str, 
                storage_mover_name: str, 
                project_name: str, 
                job_definition_name: str, 
                **kwargs: Any
            ) -> JobRunResourceId: ...

        @distributed_trace_async
        async def start_job(
                self, 
                resource_group_name: str, 
                storage_mover_name: str, 
                project_name: str, 
                job_definition_name: str, 
                **kwargs: Any
            ) -> JobRunResourceId: ...

        @distributed_trace_async
        async def stop_job(
                self, 
                resource_group_name: str, 
                storage_mover_name: str, 
                project_name: str, 
                job_definition_name: str, 
                **kwargs: Any
            ) -> JobRunResourceId: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                storage_mover_name: str, 
                project_name: str, 
                job_definition_name: str, 
                job_definition: JobDefinitionUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JobDefinition: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                storage_mover_name: str, 
                project_name: str, 
                job_definition_name: str, 
                job_definition: JobDefinitionUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JobDefinition: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                storage_mover_name: str, 
                project_name: str, 
                job_definition_name: str, 
                job_definition: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JobDefinition: ...


    class azure.mgmt.storagemover.aio.operations.JobRunsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                storage_mover_name: str, 
                project_name: str, 
                job_definition_name: str, 
                job_run_name: str, 
                **kwargs: Any
            ) -> JobRun: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                storage_mover_name: str, 
                project_name: str, 
                job_definition_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[JobRun]: ...


    class azure.mgmt.storagemover.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


    class azure.mgmt.storagemover.aio.operations.ProjectsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                storage_mover_name: str, 
                project_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                storage_mover_name: str, 
                project_name: str, 
                project: Project, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Project: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                storage_mover_name: str, 
                project_name: str, 
                project: Project, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Project: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                storage_mover_name: str, 
                project_name: str, 
                project: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Project: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                storage_mover_name: str, 
                project_name: str, 
                **kwargs: Any
            ) -> Project: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                storage_mover_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Project]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                storage_mover_name: str, 
                project_name: str, 
                project: ProjectUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Project: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                storage_mover_name: str, 
                project_name: str, 
                project: ProjectUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Project: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                storage_mover_name: str, 
                project_name: str, 
                project: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Project: ...


    class azure.mgmt.storagemover.aio.operations.StorageMoversOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                storage_mover_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                storage_mover_name: str, 
                storage_mover: StorageMover, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StorageMover: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                storage_mover_name: str, 
                storage_mover: StorageMover, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StorageMover: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                storage_mover_name: str, 
                storage_mover: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StorageMover: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                storage_mover_name: str, 
                **kwargs: Any
            ) -> StorageMover: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[StorageMover]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[StorageMover]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                storage_mover_name: str, 
                storage_mover: StorageMoverUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StorageMover: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                storage_mover_name: str, 
                storage_mover: StorageMoverUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StorageMover: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                storage_mover_name: str, 
                storage_mover: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StorageMover: ...


namespace azure.mgmt.storagemover.models

    class azure.mgmt.storagemover.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.storagemover.models.Agent(ProxyResource):
        id: str
        name: str
        properties: AgentProperties
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: AgentProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.storagemover.models.AgentProperties(_Model):
        agent_status: Optional[Union[str, AgentStatus]]
        agent_version: Optional[str]
        arc_resource_id: str
        arc_vm_uuid: str
        description: Optional[str]
        error_details: Optional[AgentPropertiesErrorDetails]
        last_status_update: Optional[datetime]
        local_ip_address: Optional[str]
        memory_in_mb: Optional[int]
        number_of_cores: Optional[int]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        time_zone: Optional[str]
        upload_limit_schedule: Optional[UploadLimitSchedule]
        uptime_in_seconds: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                arc_resource_id: str, 
                arc_vm_uuid: str, 
                description: Optional[str] = ..., 
                upload_limit_schedule: Optional[UploadLimitSchedule] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagemover.models.AgentPropertiesErrorDetails(_Model):
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


    class azure.mgmt.storagemover.models.AgentStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EXECUTING = "Executing"
        OFFLINE = "Offline"
        ONLINE = "Online"
        REGISTERING = "Registering"
        REQUIRES_ATTENTION = "RequiresAttention"
        UNREGISTERING = "Unregistering"


    class azure.mgmt.storagemover.models.AgentUpdateParameters(_Model):
        properties: Optional[AgentUpdateProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AgentUpdateProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.storagemover.models.AgentUpdateProperties(_Model):
        description: Optional[str]
        upload_limit_schedule: Optional[UploadLimitSchedule]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                upload_limit_schedule: Optional[UploadLimitSchedule] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagemover.models.AzureKeyVaultS3WithHmacCredentials(Credentials, discriminator='AzureKeyVaultS3WithHMAC'):
        access_key_uri: Optional[str]
        secret_key_uri: Optional[str]
        type: Literal[CredentialType.AZURE_KEY_VAULT_S3_WITH_HMAC]

        @overload
        def __init__(
                self, 
                *, 
                access_key_uri: Optional[str] = ..., 
                secret_key_uri: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagemover.models.AzureKeyVaultSmbCredentials(Credentials, discriminator='AzureKeyVaultSmb'):
        password_uri: Optional[str]
        type: Literal[CredentialType.AZURE_KEY_VAULT_SMB]
        username_uri: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                password_uri: Optional[str] = ..., 
                username_uri: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagemover.models.AzureMultiCloudConnectorEndpointProperties(EndpointBaseProperties, discriminator='AzureMultiCloudConnector'):
        aws_s3_bucket_id: str
        description: str
        endpoint_kind: Union[str, EndpointKind]
        endpoint_type: Literal[EndpointType.AZURE_MULTI_CLOUD_CONNECTOR]
        multi_cloud_connector_id: str
        provisioning_state: Union[str, ProvisioningState]

        @overload
        def __init__(
                self, 
                *, 
                aws_s3_bucket_id: str, 
                description: Optional[str] = ..., 
                endpoint_kind: Optional[Union[str, EndpointKind]] = ..., 
                multi_cloud_connector_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagemover.models.AzureMultiCloudConnectorEndpointUpdateProperties(EndpointBaseUpdateProperties, discriminator='AzureMultiCloudConnector'):
        description: str
        endpoint_type: Literal[EndpointType.AZURE_MULTI_CLOUD_CONNECTOR]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagemover.models.AzureStorageBlobContainerEndpointProperties(EndpointBaseProperties, discriminator='AzureStorageBlobContainer'):
        allowed_storage_accounts: Optional[list[str]]
        blob_container_name: str
        description: str
        enable_cross_tenant_transfer: Optional[bool]
        endpoint_kind: Union[str, EndpointKind]
        endpoint_type: Literal[EndpointType.AZURE_STORAGE_BLOB_CONTAINER]
        provisioning_state: Union[str, ProvisioningState]
        storage_account_resource_id: str

        @overload
        def __init__(
                self, 
                *, 
                allowed_storage_accounts: Optional[list[str]] = ..., 
                blob_container_name: str, 
                description: Optional[str] = ..., 
                enable_cross_tenant_transfer: Optional[bool] = ..., 
                endpoint_kind: Optional[Union[str, EndpointKind]] = ..., 
                storage_account_resource_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagemover.models.AzureStorageBlobContainerEndpointUpdateProperties(EndpointBaseUpdateProperties, discriminator='AzureStorageBlobContainer'):
        allowed_storage_accounts: Optional[list[str]]
        description: str
        enable_cross_tenant_transfer: Optional[bool]
        endpoint_type: Literal[EndpointType.AZURE_STORAGE_BLOB_CONTAINER]

        @overload
        def __init__(
                self, 
                *, 
                allowed_storage_accounts: Optional[list[str]] = ..., 
                description: Optional[str] = ..., 
                enable_cross_tenant_transfer: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagemover.models.AzureStorageNfsFileShareEndpointProperties(EndpointBaseProperties, discriminator='AzureStorageNfsFileShare'):
        description: str
        endpoint_kind: Union[str, EndpointKind]
        endpoint_type: Literal[EndpointType.AZURE_STORAGE_NFS_FILE_SHARE]
        file_share_name: str
        provisioning_state: Union[str, ProvisioningState]
        storage_account_resource_id: str

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                endpoint_kind: Optional[Union[str, EndpointKind]] = ..., 
                file_share_name: str, 
                storage_account_resource_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagemover.models.AzureStorageNfsFileShareEndpointUpdateProperties(EndpointBaseUpdateProperties, discriminator='AzureStorageNfsFileShare'):
        description: str
        endpoint_type: Literal[EndpointType.AZURE_STORAGE_NFS_FILE_SHARE]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagemover.models.AzureStorageSmbFileShareEndpointProperties(EndpointBaseProperties, discriminator='AzureStorageSmbFileShare'):
        allowed_storage_accounts: Optional[list[str]]
        description: str
        enable_cross_tenant_transfer: Optional[bool]
        endpoint_kind: Union[str, EndpointKind]
        endpoint_type: Literal[EndpointType.AZURE_STORAGE_SMB_FILE_SHARE]
        file_share_name: str
        provisioning_state: Union[str, ProvisioningState]
        storage_account_resource_id: str

        @overload
        def __init__(
                self, 
                *, 
                allowed_storage_accounts: Optional[list[str]] = ..., 
                description: Optional[str] = ..., 
                enable_cross_tenant_transfer: Optional[bool] = ..., 
                endpoint_kind: Optional[Union[str, EndpointKind]] = ..., 
                file_share_name: str, 
                storage_account_resource_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagemover.models.AzureStorageSmbFileShareEndpointUpdateProperties(EndpointBaseUpdateProperties, discriminator='AzureStorageSmbFileShare'):
        allowed_storage_accounts: Optional[list[str]]
        description: str
        enable_cross_tenant_transfer: Optional[bool]
        endpoint_type: Literal[EndpointType.AZURE_STORAGE_SMB_FILE_SHARE]

        @overload
        def __init__(
                self, 
                *, 
                allowed_storage_accounts: Optional[list[str]] = ..., 
                description: Optional[str] = ..., 
                enable_cross_tenant_transfer: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagemover.models.Connection(ProxyResource):
        id: str
        name: str
        properties: ConnectionProperties
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: ConnectionProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagemover.models.ConnectionProperties(_Model):
        connection_status: Optional[Union[str, ConnectionStatus]]
        description: Optional[str]
        job_list: Optional[list[str]]
        private_endpoint_name: Optional[str]
        private_endpoint_resource_id: Optional[str]
        private_link_service_id: str
        provisioning_state: Optional[Union[str, ProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                job_list: Optional[list[str]] = ..., 
                private_link_service_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagemover.models.ConnectionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPROVED = "Approved"
        DISCONNECTED = "Disconnected"
        PENDING = "Pending"
        REJECTED = "Rejected"
        STALE = "Stale"


    class azure.mgmt.storagemover.models.CopyMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ADDITIVE = "Additive"
        MIRROR = "Mirror"


    class azure.mgmt.storagemover.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.storagemover.models.CredentialType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_KEY_VAULT_S3_WITH_HMAC = "AzureKeyVaultS3WithHMAC"
        AZURE_KEY_VAULT_SMB = "AzureKeyVaultSmb"


    class azure.mgmt.storagemover.models.Credentials(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagemover.models.DataIntegrityValidation(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SAVE_FILE_MD5 = "SaveFileMD5"
        SAVE_VERIFY_FILE_MD5 = "SaveVerifyFileMD5"


    class azure.mgmt.storagemover.models.DayOfWeek(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FRIDAY = "Friday"
        MONDAY = "Monday"
        SATURDAY = "Saturday"
        SUNDAY = "Sunday"
        THURSDAY = "Thursday"
        TUESDAY = "Tuesday"
        WEDNESDAY = "Wednesday"


    class azure.mgmt.storagemover.models.Endpoint(ProxyResource):
        id: str
        identity: Optional[ManagedServiceIdentity]
        name: str
        properties: EndpointBaseProperties
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                properties: EndpointBaseProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagemover.models.EndpointBaseProperties(_Model):
        description: Optional[str]
        endpoint_kind: Optional[Union[str, EndpointKind]]
        endpoint_type: str
        provisioning_state: Optional[Union[str, ProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                endpoint_kind: Optional[Union[str, EndpointKind]] = ..., 
                endpoint_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagemover.models.EndpointBaseUpdateParameters(_Model):
        identity: Optional[ManagedServiceIdentity]
        properties: Optional[EndpointBaseUpdateProperties]

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                properties: Optional[EndpointBaseUpdateProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagemover.models.EndpointBaseUpdateProperties(_Model):
        description: Optional[str]
        endpoint_type: str

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                endpoint_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagemover.models.EndpointKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SOURCE = "Source"
        TARGET = "Target"


    class azure.mgmt.storagemover.models.EndpointType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_MULTI_CLOUD_CONNECTOR = "AzureMultiCloudConnector"
        AZURE_STORAGE_BLOB_CONTAINER = "AzureStorageBlobContainer"
        AZURE_STORAGE_NFS_FILE_SHARE = "AzureStorageNfsFileShare"
        AZURE_STORAGE_SMB_FILE_SHARE = "AzureStorageSmbFileShare"
        NFS_MOUNT = "NfsMount"
        S3_WITH_HMAC = "S3WithHMAC"
        SMB_MOUNT = "SmbMount"


    class azure.mgmt.storagemover.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.storagemover.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.storagemover.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagemover.models.Frequency(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DAILY = "Daily"
        HOURLY = "Hourly"
        MONTHLY = "Monthly"
        NONE = "None"
        ONETIME = "Onetime"
        WEEKLY = "Weekly"


    class azure.mgmt.storagemover.models.JobDefinition(ProxyResource):
        id: str
        name: str
        properties: JobDefinitionProperties
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: JobDefinitionProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.storagemover.models.JobDefinitionProperties(_Model):
        agent_name: Optional[str]
        agent_resource_id: Optional[str]
        connections: Optional[list[str]]
        copy_mode: Union[str, CopyMode]
        cross_tenant_endpoint_resource_id: Optional[str]
        cross_tenant_endpoint_tenant_id: Optional[str]
        data_integrity_validation: Optional[Union[str, DataIntegrityValidation]]
        description: Optional[str]
        is_cross_tenant_job: Optional[bool]
        job_type: Optional[Union[str, JobType]]
        latest_job_run_name: Optional[str]
        latest_job_run_resource_id: Optional[str]
        latest_job_run_status: Optional[Union[str, JobRunStatus]]
        mover_synced_until: Optional[datetime]
        preserve_permissions: Optional[bool]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        schedule: Optional[ScheduleInfo]
        source_name: str
        source_resource_id: Optional[str]
        source_subpath: Optional[str]
        source_target_map: Optional[JobDefinitionPropertiesSourceTargetMap]
        sync_mode: Optional[str]
        target_name: str
        target_resource_id: Optional[str]
        target_subpath: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                agent_name: Optional[str] = ..., 
                connections: Optional[list[str]] = ..., 
                copy_mode: Union[str, CopyMode], 
                cross_tenant_endpoint_resource_id: Optional[str] = ..., 
                cross_tenant_endpoint_tenant_id: Optional[str] = ..., 
                data_integrity_validation: Optional[Union[str, DataIntegrityValidation]] = ..., 
                description: Optional[str] = ..., 
                is_cross_tenant_job: Optional[bool] = ..., 
                job_type: Optional[Union[str, JobType]] = ..., 
                mover_synced_until: Optional[datetime] = ..., 
                preserve_permissions: Optional[bool] = ..., 
                schedule: Optional[ScheduleInfo] = ..., 
                source_name: str, 
                source_subpath: Optional[str] = ..., 
                source_target_map: Optional[JobDefinitionPropertiesSourceTargetMap] = ..., 
                sync_mode: Optional[str] = ..., 
                target_name: str, 
                target_subpath: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagemover.models.JobDefinitionPropertiesSourceTargetMap(_Model):
        value: Optional[list[SourceTargetMap]]


    class azure.mgmt.storagemover.models.JobDefinitionUpdateParameters(_Model):
        properties: Optional[JobDefinitionUpdateProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[JobDefinitionUpdateProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.storagemover.models.JobDefinitionUpdateProperties(_Model):
        agent_name: Optional[str]
        connections: Optional[list[str]]
        copy_mode: Optional[Union[str, CopyMode]]
        data_integrity_validation: Optional[Union[str, DataIntegrityValidation]]
        description: Optional[str]
        mover_synced_until: Optional[datetime]
        schedule: Optional[ScheduleInfo]
        sync_mode: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                agent_name: Optional[str] = ..., 
                connections: Optional[list[str]] = ..., 
                copy_mode: Optional[Union[str, CopyMode]] = ..., 
                data_integrity_validation: Optional[Union[str, DataIntegrityValidation]] = ..., 
                description: Optional[str] = ..., 
                mover_synced_until: Optional[datetime] = ..., 
                schedule: Optional[ScheduleInfo] = ..., 
                sync_mode: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagemover.models.JobRun(ProxyResource):
        id: str
        name: str
        properties: Optional[JobRunProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[JobRunProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.storagemover.models.JobRunError(_Model):
        code: Optional[str]
        message: Optional[str]
        target: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                message: Optional[str] = ..., 
                target: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagemover.models.JobRunProperties(_Model):
        agent_name: Optional[str]
        agent_resource_id: Optional[str]
        bytes_excluded: Optional[int]
        bytes_failed: Optional[int]
        bytes_no_transfer_needed: Optional[int]
        bytes_scanned: Optional[int]
        bytes_transferred: Optional[int]
        bytes_unsupported: Optional[int]
        error: Optional[JobRunError]
        execution_end_time: Optional[datetime]
        execution_start_time: Optional[datetime]
        items_excluded: Optional[int]
        items_failed: Optional[int]
        items_no_transfer_needed: Optional[int]
        items_scanned: Optional[int]
        items_transferred: Optional[int]
        items_unsupported: Optional[int]
        job_definition_properties: Optional[Any]
        last_status_update: Optional[datetime]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        scan_status: Optional[Union[str, JobRunScanStatus]]
        scheduled_execution_time: Optional[datetime]
        source_name: Optional[str]
        source_properties: Optional[Any]
        source_resource_id: Optional[str]
        status: Optional[Union[str, JobRunStatus]]
        target_name: Optional[str]
        target_properties: Optional[Any]
        target_resource_id: Optional[str]
        trigger_type: Optional[Union[str, TriggerType]]
        warnings: Optional[list[JobRunWarning]]


    class azure.mgmt.storagemover.models.JobRunResourceId(_Model):
        job_run_resource_id: Optional[str]


    class azure.mgmt.storagemover.models.JobRunScanStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLETED = "Completed"
        NOT_STARTED = "NotStarted"
        SCANNING = "Scanning"


    class azure.mgmt.storagemover.models.JobRunStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CANCELING = "Canceling"
        CANCEL_REQUESTED = "CancelRequested"
        FAILED = "Failed"
        PAUSED_BY_BANDWIDTH_MANAGEMENT = "PausedByBandwidthManagement"
        QUEUED = "Queued"
        RUNNING = "Running"
        STARTED = "Started"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.storagemover.models.JobRunWarning(_Model):
        code: Optional[str]
        message: Optional[str]
        target: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                message: Optional[str] = ..., 
                target: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagemover.models.JobType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CLOUD_TO_CLOUD = "CloudToCloud"
        ON_PREM_TO_CLOUD = "OnPremToCloud"
        ON_PREM_TO_CLOUD_AGENT_LESS = "OnPremToCloudAgentLess"


    class azure.mgmt.storagemover.models.ManagedServiceIdentity(_Model):
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


    class azure.mgmt.storagemover.models.ManagedServiceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        SYSTEM_ASSIGNED_USER_ASSIGNED = "SystemAssigned,UserAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.storagemover.models.Minute(int, Enum, metaclass=CaseInsensitiveEnumMeta):
        THIRTY = 30
        ZERO = 0


    class azure.mgmt.storagemover.models.NfsMountEndpointProperties(EndpointBaseProperties, discriminator='NfsMount'):
        description: str
        endpoint_kind: Union[str, EndpointKind]
        endpoint_type: Literal[EndpointType.NFS_MOUNT]
        export: str
        host: str
        nfs_version: Optional[Union[str, NfsVersion]]
        provisioning_state: Union[str, ProvisioningState]
        source_type: Optional[Union[str, NfsMountSourceType]]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                endpoint_kind: Optional[Union[str, EndpointKind]] = ..., 
                export: str, 
                host: str, 
                nfs_version: Optional[Union[str, NfsVersion]] = ..., 
                source_type: Optional[Union[str, NfsMountSourceType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagemover.models.NfsMountEndpointUpdateProperties(EndpointBaseUpdateProperties, discriminator='NfsMount'):
        description: str
        endpoint_type: Literal[EndpointType.NFS_MOUNT]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagemover.models.NfsMountSourceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FSXEFS = "FSX-EFS"
        NFS_MOUNT = "NfsMount"


    class azure.mgmt.storagemover.models.NfsVersion(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NF_SAUTO = "NFSauto"
        NF_SV3 = "NFSv3"
        NF_SV4 = "NFSv4"
        NF_SV4_1 = "NFSv4_1"


    class azure.mgmt.storagemover.models.Operation(_Model):
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


    class azure.mgmt.storagemover.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.storagemover.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.storagemover.models.Project(ProxyResource):
        id: str
        name: str
        properties: Optional[ProjectProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ProjectProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.storagemover.models.ProjectProperties(_Model):
        description: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagemover.models.ProjectUpdateParameters(_Model):
        properties: Optional[ProjectUpdateProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ProjectUpdateProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.storagemover.models.ProjectUpdateProperties(_Model):
        description: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagemover.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.storagemover.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.storagemover.models.Recurrence(_Model):
        end_time: Time
        start_time: Time

        @overload
        def __init__(
                self, 
                *, 
                end_time: Time, 
                start_time: Time
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagemover.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.storagemover.models.S3WithHmacEndpointProperties(EndpointBaseProperties, discriminator='S3WithHMAC'):
        credentials: Optional[AzureKeyVaultS3WithHmacCredentials]
        description: str
        endpoint_kind: Union[str, EndpointKind]
        endpoint_type: Literal[EndpointType.S3_WITH_HMAC]
        other_source_type_description: Optional[str]
        provisioning_state: Union[str, ProvisioningState]
        source_type: Optional[Union[str, S3WithHmacSourceType]]
        source_uri: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                credentials: Optional[AzureKeyVaultS3WithHmacCredentials] = ..., 
                description: Optional[str] = ..., 
                endpoint_kind: Optional[Union[str, EndpointKind]] = ..., 
                other_source_type_description: Optional[str] = ..., 
                source_type: Optional[Union[str, S3WithHmacSourceType]] = ..., 
                source_uri: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagemover.models.S3WithHmacEndpointUpdateProperties(EndpointBaseUpdateProperties, discriminator='S3WithHMAC'):
        credentials: Optional[AzureKeyVaultS3WithHmacCredentials]
        description: str
        endpoint_type: Literal[EndpointType.S3_WITH_HMAC]

        @overload
        def __init__(
                self, 
                *, 
                credentials: Optional[AzureKeyVaultS3WithHmacCredentials] = ..., 
                description: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagemover.models.S3WithHmacSourceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALIBABA = "ALIBABA"
        DELL_EMC = "DELL_EMC"
        GCS = "GCS"
        IBM = "IBM"
        MINIO = "MINIO"
        OTHER = "OTHER"


    class azure.mgmt.storagemover.models.ScheduleInfo(_Model):
        cron_expression: Optional[str]
        days_of_month: Optional[list[int]]
        days_of_week: Optional[list[str]]
        end_date: Optional[datetime]
        execution_time: Optional[SchedulerTime]
        frequency: Optional[Union[str, Frequency]]
        is_active: Optional[bool]
        repeat_interval: Optional[str]
        start_date: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                cron_expression: Optional[str] = ..., 
                days_of_month: Optional[list[int]] = ..., 
                days_of_week: Optional[list[str]] = ..., 
                end_date: Optional[datetime] = ..., 
                execution_time: Optional[SchedulerTime] = ..., 
                frequency: Optional[Union[str, Frequency]] = ..., 
                is_active: Optional[bool] = ..., 
                repeat_interval: Optional[str] = ..., 
                start_date: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagemover.models.SchedulerTime(_Model):
        hour: Optional[int]
        minute: Optional[Union[int, Minute]]

        @overload
        def __init__(
                self, 
                *, 
                hour: Optional[int] = ..., 
                minute: Optional[Union[int, Minute]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagemover.models.SmbMountEndpointProperties(EndpointBaseProperties, discriminator='SmbMount'):
        credentials: Optional[AzureKeyVaultSmbCredentials]
        description: str
        endpoint_kind: Union[str, EndpointKind]
        endpoint_type: Literal[EndpointType.SMB_MOUNT]
        host: str
        provisioning_state: Union[str, ProvisioningState]
        share_name: str
        source_type: Optional[Union[str, SmbMountSourceType]]

        @overload
        def __init__(
                self, 
                *, 
                credentials: Optional[AzureKeyVaultSmbCredentials] = ..., 
                description: Optional[str] = ..., 
                endpoint_kind: Optional[Union[str, EndpointKind]] = ..., 
                host: str, 
                share_name: str, 
                source_type: Optional[Union[str, SmbMountSourceType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagemover.models.SmbMountEndpointUpdateProperties(EndpointBaseUpdateProperties, discriminator='SmbMount'):
        credentials: Optional[AzureKeyVaultSmbCredentials]
        description: str
        endpoint_type: Literal[EndpointType.SMB_MOUNT]

        @overload
        def __init__(
                self, 
                *, 
                credentials: Optional[AzureKeyVaultSmbCredentials] = ..., 
                description: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagemover.models.SmbMountSourceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FSXSMB = "FSX-SMB"
        SMB_MOUNT = "SmbMount"


    class azure.mgmt.storagemover.models.SourceEndpoint(_Model):
        properties: Optional[SourceEndpointProperties]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SourceEndpointProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagemover.models.SourceEndpointProperties(_Model):
        aws_s3_bucket_id: Optional[str]
        name: Optional[str]
        source_endpoint_resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                aws_s3_bucket_id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                source_endpoint_resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagemover.models.SourceTargetMap(_Model):
        source_endpoint: SourceEndpoint
        target_endpoint: TargetEndpoint

        @overload
        def __init__(
                self, 
                *, 
                source_endpoint: SourceEndpoint, 
                target_endpoint: TargetEndpoint
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagemover.models.StorageMover(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[StorageMoverProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[StorageMoverProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.storagemover.models.StorageMoverProperties(_Model):
        description: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagemover.models.StorageMoverUpdateParameters(_Model):
        properties: Optional[StorageMoverUpdateProperties]
        tags: Optional[dict[str, str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[StorageMoverUpdateProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.storagemover.models.StorageMoverUpdateProperties(_Model):
        description: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagemover.models.SystemData(_Model):
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


    class azure.mgmt.storagemover.models.TargetEndpoint(_Model):
        properties: Optional[TargetEndpointProperties]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[TargetEndpointProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagemover.models.TargetEndpointProperties(_Model):
        azure_storage_account_resource_id: Optional[str]
        azure_storage_blob_container_name: Optional[str]
        name: Optional[str]
        target_endpoint_resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                azure_storage_account_resource_id: Optional[str] = ..., 
                azure_storage_blob_container_name: Optional[str] = ..., 
                name: Optional[str] = ..., 
                target_endpoint_resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagemover.models.Time(_Model):
        hour: int
        minute: Optional[Union[int, Minute]]

        @overload
        def __init__(
                self, 
                *, 
                hour: int, 
                minute: Optional[Union[int, Minute]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagemover.models.TrackedResource(Resource):
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


    class azure.mgmt.storagemover.models.TriggerType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MANUAL = "Manual"
        SCHEDULED = "Scheduled"


    class azure.mgmt.storagemover.models.UploadLimitSchedule(_Model):
        weekly_recurrences: Optional[list[UploadLimitWeeklyRecurrence]]

        @overload
        def __init__(
                self, 
                *, 
                weekly_recurrences: Optional[list[UploadLimitWeeklyRecurrence]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagemover.models.UploadLimitWeeklyRecurrence(WeeklyRecurrence):
        days: Union[list[str, DayOfWeek]]
        end_time: Time
        limit_in_mbps: int
        start_time: Time

        @overload
        def __init__(
                self, 
                *, 
                days: list[Union[str, DayOfWeek]], 
                end_time: Time, 
                limit_in_mbps: int, 
                start_time: Time
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagemover.models.UserAssignedIdentity(_Model):
        client_id: Optional[str]
        principal_id: Optional[str]


    class azure.mgmt.storagemover.models.WeeklyRecurrence(Recurrence):
        days: list[Union[str, DayOfWeek]]
        end_time: Time
        start_time: Time

        @overload
        def __init__(
                self, 
                *, 
                days: list[Union[str, DayOfWeek]], 
                end_time: Time, 
                start_time: Time
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


namespace azure.mgmt.storagemover.operations

    class azure.mgmt.storagemover.operations.AgentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                storage_mover_name: str, 
                agent_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                storage_mover_name: str, 
                agent_name: str, 
                agent: Agent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Agent: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                storage_mover_name: str, 
                agent_name: str, 
                agent: Agent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Agent: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                storage_mover_name: str, 
                agent_name: str, 
                agent: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Agent: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                storage_mover_name: str, 
                agent_name: str, 
                **kwargs: Any
            ) -> Agent: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                storage_mover_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Agent]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                storage_mover_name: str, 
                agent_name: str, 
                agent: AgentUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Agent: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                storage_mover_name: str, 
                agent_name: str, 
                agent: AgentUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Agent: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                storage_mover_name: str, 
                agent_name: str, 
                agent: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Agent: ...


    class azure.mgmt.storagemover.operations.ConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-08-01', params_added_on={'2025-08-01': ['api_version', 'subscription_id', 'resource_group_name', 'storage_mover_name', 'connection_name']}, api_versions_list=['2025-08-01', '2025-12-01', '2026-05-01'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                storage_mover_name: str, 
                connection_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                storage_mover_name: str, 
                connection_name: str, 
                connection: Connection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Connection: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                storage_mover_name: str, 
                connection_name: str, 
                connection: Connection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Connection: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                storage_mover_name: str, 
                connection_name: str, 
                connection: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Connection: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-08-01', params_added_on={'2025-08-01': ['api_version', 'subscription_id', 'resource_group_name', 'storage_mover_name', 'connection_name', 'accept']}, api_versions_list=['2025-08-01', '2025-12-01', '2026-05-01'])
        def get(
                self, 
                resource_group_name: str, 
                storage_mover_name: str, 
                connection_name: str, 
                **kwargs: Any
            ) -> Connection: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-08-01', params_added_on={'2025-08-01': ['api_version', 'subscription_id', 'resource_group_name', 'storage_mover_name', 'accept']}, api_versions_list=['2025-08-01', '2025-12-01', '2026-05-01'])
        def list(
                self, 
                resource_group_name: str, 
                storage_mover_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Connection]: ...


    class azure.mgmt.storagemover.operations.EndpointsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                storage_mover_name: str, 
                endpoint_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                storage_mover_name: str, 
                endpoint_name: str, 
                endpoint: Endpoint, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Endpoint: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                storage_mover_name: str, 
                endpoint_name: str, 
                endpoint: Endpoint, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Endpoint: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                storage_mover_name: str, 
                endpoint_name: str, 
                endpoint: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Endpoint: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                storage_mover_name: str, 
                endpoint_name: str, 
                **kwargs: Any
            ) -> Endpoint: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                storage_mover_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Endpoint]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                storage_mover_name: str, 
                endpoint_name: str, 
                endpoint: EndpointBaseUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Endpoint: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                storage_mover_name: str, 
                endpoint_name: str, 
                endpoint: EndpointBaseUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Endpoint: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                storage_mover_name: str, 
                endpoint_name: str, 
                endpoint: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Endpoint: ...


    class azure.mgmt.storagemover.operations.JobDefinitionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                storage_mover_name: str, 
                project_name: str, 
                job_definition_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                storage_mover_name: str, 
                project_name: str, 
                job_definition_name: str, 
                job_definition: JobDefinition, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JobDefinition: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                storage_mover_name: str, 
                project_name: str, 
                job_definition_name: str, 
                job_definition: JobDefinition, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JobDefinition: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                storage_mover_name: str, 
                project_name: str, 
                job_definition_name: str, 
                job_definition: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JobDefinition: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                storage_mover_name: str, 
                project_name: str, 
                job_definition_name: str, 
                **kwargs: Any
            ) -> JobDefinition: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                storage_mover_name: str, 
                project_name: str, 
                **kwargs: Any
            ) -> ItemPaged[JobDefinition]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01', params_added_on={'2026-05-01': ['api_version', 'subscription_id', 'resource_group_name', 'storage_mover_name', 'project_name', 'job_definition_name', 'accept']}, api_versions_list=['2026-05-01'])
        def reconcile_job(
                self, 
                resource_group_name: str, 
                storage_mover_name: str, 
                project_name: str, 
                job_definition_name: str, 
                **kwargs: Any
            ) -> JobRunResourceId: ...

        @distributed_trace
        def start_job(
                self, 
                resource_group_name: str, 
                storage_mover_name: str, 
                project_name: str, 
                job_definition_name: str, 
                **kwargs: Any
            ) -> JobRunResourceId: ...

        @distributed_trace
        def stop_job(
                self, 
                resource_group_name: str, 
                storage_mover_name: str, 
                project_name: str, 
                job_definition_name: str, 
                **kwargs: Any
            ) -> JobRunResourceId: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                storage_mover_name: str, 
                project_name: str, 
                job_definition_name: str, 
                job_definition: JobDefinitionUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JobDefinition: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                storage_mover_name: str, 
                project_name: str, 
                job_definition_name: str, 
                job_definition: JobDefinitionUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JobDefinition: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                storage_mover_name: str, 
                project_name: str, 
                job_definition_name: str, 
                job_definition: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JobDefinition: ...


    class azure.mgmt.storagemover.operations.JobRunsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                storage_mover_name: str, 
                project_name: str, 
                job_definition_name: str, 
                job_run_name: str, 
                **kwargs: Any
            ) -> JobRun: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                storage_mover_name: str, 
                project_name: str, 
                job_definition_name: str, 
                **kwargs: Any
            ) -> ItemPaged[JobRun]: ...


    class azure.mgmt.storagemover.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


    class azure.mgmt.storagemover.operations.ProjectsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                storage_mover_name: str, 
                project_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                storage_mover_name: str, 
                project_name: str, 
                project: Project, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Project: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                storage_mover_name: str, 
                project_name: str, 
                project: Project, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Project: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                storage_mover_name: str, 
                project_name: str, 
                project: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Project: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                storage_mover_name: str, 
                project_name: str, 
                **kwargs: Any
            ) -> Project: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                storage_mover_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Project]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                storage_mover_name: str, 
                project_name: str, 
                project: ProjectUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Project: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                storage_mover_name: str, 
                project_name: str, 
                project: ProjectUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Project: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                storage_mover_name: str, 
                project_name: str, 
                project: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Project: ...


    class azure.mgmt.storagemover.operations.StorageMoversOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                storage_mover_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                storage_mover_name: str, 
                storage_mover: StorageMover, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StorageMover: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                storage_mover_name: str, 
                storage_mover: StorageMover, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StorageMover: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                storage_mover_name: str, 
                storage_mover: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StorageMover: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                storage_mover_name: str, 
                **kwargs: Any
            ) -> StorageMover: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[StorageMover]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[StorageMover]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                storage_mover_name: str, 
                storage_mover: StorageMoverUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StorageMover: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                storage_mover_name: str, 
                storage_mover: StorageMoverUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StorageMover: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                storage_mover_name: str, 
                storage_mover: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StorageMover: ...


namespace azure.mgmt.storagemover.types

    class azure.mgmt.storagemover.types.Agent(ProxyResource):
        key "id": str
        key "name": str
        key "properties": Required[AgentProperties]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: AgentProperties
        system_data: SystemData
        type: str


    class azure.mgmt.storagemover.types.AgentProperties(TypedDict, total=False):
        key "agentStatus": Union[str, AgentStatus]
        key "agentVersion": str
        key "arcResourceId": Required[str]
        key "arcVmUuid": Required[str]
        key "description": str
        key "errorDetails": ForwardRef('AgentPropertiesErrorDetails', module='types')
        key "lastStatusUpdate": str
        key "localIPAddress": str
        key "memoryInMB": int
        key "numberOfCores": int
        key "provisioningState": Union[str, ProvisioningState]
        key "timeZone": str
        key "uploadLimitSchedule": ForwardRef('UploadLimitSchedule', module='types')
        key "uptimeInSeconds": int
        agent_status: Union[str, AgentStatus]
        agent_version: str
        arc_resource_id: str
        arc_vm_uuid: str
        description: str
        error_details: AgentPropertiesErrorDetails
        last_status_update: str
        local_ip_address: str
        memory_in_mb: int
        number_of_cores: int
        provisioning_state: Union[str, ProvisioningState]
        time_zone: str
        upload_limit_schedule: UploadLimitSchedule
        uptime_in_seconds: int


    class azure.mgmt.storagemover.types.AgentPropertiesErrorDetails(TypedDict, total=False):
        key "code": str
        key "message": str
        code: str
        message: str


    class azure.mgmt.storagemover.types.AgentUpdateParameters(TypedDict, total=False):
        key "properties": ForwardRef('AgentUpdateProperties', module='types')
        properties: AgentUpdateProperties


    class azure.mgmt.storagemover.types.AgentUpdateProperties(TypedDict, total=False):
        key "description": str
        key "uploadLimitSchedule": ForwardRef('UploadLimitSchedule', module='types')
        description: str
        upload_limit_schedule: UploadLimitSchedule


    class azure.mgmt.storagemover.types.AzureKeyVaultS3WithHmacCredentials(TypedDict, total=False):
        key "accessKeyUri": str
        key "secretKeyUri": str
        key "type": Required[Literal[CredentialType.AZURE_KEY_VAULT_S3_WITH_HMAC]]
        access_key_uri: str
        secret_key_uri: str
        type: Literal[CredentialType.AZURE_KEY_VAULT_S3_WITH_HMAC]


    class azure.mgmt.storagemover.types.AzureKeyVaultSmbCredentials(TypedDict, total=False):
        key "passwordUri": str
        key "type": Required[Literal[CredentialType.AZURE_KEY_VAULT_SMB]]
        key "usernameUri": str
        password_uri: str
        type: Literal[CredentialType.AZURE_KEY_VAULT_SMB]
        username_uri: str


    class azure.mgmt.storagemover.types.AzureMultiCloudConnectorEndpointProperties(TypedDict, total=False):
        key "awsS3BucketId": Required[str]
        key "description": str
        key "endpointKind": Union[str, EndpointKind]
        key "endpointType": Required[Literal[EndpointType.AZURE_MULTI_CLOUD_CONNECTOR]]
        key "multiCloudConnectorId": Required[str]
        key "provisioningState": Union[str, ProvisioningState]
        aws_s3_bucket_id: str
        description: str
        endpoint_kind: Union[str, EndpointKind]
        endpoint_type: Literal[EndpointType.AZURE_MULTI_CLOUD_CONNECTOR]
        multi_cloud_connector_id: str
        provisioning_state: Union[str, ProvisioningState]


    class azure.mgmt.storagemover.types.AzureMultiCloudConnectorEndpointUpdateProperties(TypedDict, total=False):
        key "description": str
        key "endpointType": Required[Literal[EndpointType.AZURE_MULTI_CLOUD_CONNECTOR]]
        description: str
        endpoint_type: Literal[EndpointType.AZURE_MULTI_CLOUD_CONNECTOR]


    class azure.mgmt.storagemover.types.AzureStorageBlobContainerEndpointProperties(TypedDict, total=False):
        key "blobContainerName": Required[str]
        key "description": str
        key "enableCrossTenantTransfer": bool
        key "endpointKind": Union[str, EndpointKind]
        key "endpointType": Required[Literal[EndpointType.AZURE_STORAGE_BLOB_CONTAINER]]
        key "provisioningState": Union[str, ProvisioningState]
        key "storageAccountResourceId": Required[str]
        allowedStorageAccounts: list[str]
        allowed_storage_accounts: list[str]
        blob_container_name: str
        description: str
        enable_cross_tenant_transfer: bool
        endpoint_kind: Union[str, EndpointKind]
        endpoint_type: Literal[EndpointType.AZURE_STORAGE_BLOB_CONTAINER]
        provisioning_state: Union[str, ProvisioningState]
        storage_account_resource_id: str


    class azure.mgmt.storagemover.types.AzureStorageBlobContainerEndpointUpdateProperties(TypedDict, total=False):
        key "description": str
        key "enableCrossTenantTransfer": bool
        key "endpointType": Required[Literal[EndpointType.AZURE_STORAGE_BLOB_CONTAINER]]
        allowedStorageAccounts: list[str]
        allowed_storage_accounts: list[str]
        description: str
        enable_cross_tenant_transfer: bool
        endpoint_type: Literal[EndpointType.AZURE_STORAGE_BLOB_CONTAINER]


    class azure.mgmt.storagemover.types.AzureStorageNfsFileShareEndpointProperties(TypedDict, total=False):
        key "description": str
        key "endpointKind": Union[str, EndpointKind]
        key "endpointType": Required[Literal[EndpointType.AZURE_STORAGE_NFS_FILE_SHARE]]
        key "fileShareName": Required[str]
        key "provisioningState": Union[str, ProvisioningState]
        key "storageAccountResourceId": Required[str]
        description: str
        endpoint_kind: Union[str, EndpointKind]
        endpoint_type: Literal[EndpointType.AZURE_STORAGE_NFS_FILE_SHARE]
        file_share_name: str
        provisioning_state: Union[str, ProvisioningState]
        storage_account_resource_id: str


    class azure.mgmt.storagemover.types.AzureStorageNfsFileShareEndpointUpdateProperties(TypedDict, total=False):
        key "description": str
        key "endpointType": Required[Literal[EndpointType.AZURE_STORAGE_NFS_FILE_SHARE]]
        description: str
        endpoint_type: Literal[EndpointType.AZURE_STORAGE_NFS_FILE_SHARE]


    class azure.mgmt.storagemover.types.AzureStorageSmbFileShareEndpointProperties(TypedDict, total=False):
        key "description": str
        key "enableCrossTenantTransfer": bool
        key "endpointKind": Union[str, EndpointKind]
        key "endpointType": Required[Literal[EndpointType.AZURE_STORAGE_SMB_FILE_SHARE]]
        key "fileShareName": Required[str]
        key "provisioningState": Union[str, ProvisioningState]
        key "storageAccountResourceId": Required[str]
        allowedStorageAccounts: list[str]
        allowed_storage_accounts: list[str]
        description: str
        enable_cross_tenant_transfer: bool
        endpoint_kind: Union[str, EndpointKind]
        endpoint_type: Literal[EndpointType.AZURE_STORAGE_SMB_FILE_SHARE]
        file_share_name: str
        provisioning_state: Union[str, ProvisioningState]
        storage_account_resource_id: str


    class azure.mgmt.storagemover.types.AzureStorageSmbFileShareEndpointUpdateProperties(TypedDict, total=False):
        key "description": str
        key "enableCrossTenantTransfer": bool
        key "endpointType": Required[Literal[EndpointType.AZURE_STORAGE_SMB_FILE_SHARE]]
        allowedStorageAccounts: list[str]
        allowed_storage_accounts: list[str]
        description: str
        enable_cross_tenant_transfer: bool
        endpoint_type: Literal[EndpointType.AZURE_STORAGE_SMB_FILE_SHARE]


    class azure.mgmt.storagemover.types.Connection(ProxyResource):
        key "id": str
        key "name": str
        key "properties": Required[ConnectionProperties]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: ConnectionProperties
        system_data: SystemData
        type: str


    class azure.mgmt.storagemover.types.ConnectionProperties(TypedDict, total=False):
        key "connectionStatus": Union[str, ConnectionStatus]
        key "description": str
        key "privateEndpointName": str
        key "privateEndpointResourceId": str
        key "privateLinkServiceId": Required[str]
        key "provisioningState": Union[str, ProvisioningState]
        connection_status: Union[str, ConnectionStatus]
        description: str
        jobList: list[str]
        job_list: list[str]
        private_endpoint_name: str
        private_endpoint_resource_id: str
        private_link_service_id: str
        provisioning_state: Union[str, ProvisioningState]


    class azure.mgmt.storagemover.types.CredentialType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_KEY_VAULT_S3_WITH_HMAC = "AzureKeyVaultS3WithHMAC"
        AZURE_KEY_VAULT_SMB = "AzureKeyVaultSmb"


    class azure.mgmt.storagemover.types.Endpoint(ProxyResource):
        key "id": str
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "name": str
        key "properties": Required[EndpointBaseProperties]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        identity: ManagedServiceIdentity
        name: str
        properties: EndpointBaseProperties
        system_data: SystemData
        type: str


    class azure.mgmt.storagemover.types.EndpointBaseUpdateParameters(TypedDict, total=False):
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "properties": ForwardRef('EndpointBaseUpdateProperties', module='types')
        identity: ManagedServiceIdentity
        properties: EndpointBaseUpdateProperties


    class azure.mgmt.storagemover.types.EndpointType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_MULTI_CLOUD_CONNECTOR = "AzureMultiCloudConnector"
        AZURE_STORAGE_BLOB_CONTAINER = "AzureStorageBlobContainer"
        AZURE_STORAGE_NFS_FILE_SHARE = "AzureStorageNfsFileShare"
        AZURE_STORAGE_SMB_FILE_SHARE = "AzureStorageSmbFileShare"
        NFS_MOUNT = "NfsMount"
        S3_WITH_HMAC = "S3WithHMAC"
        SMB_MOUNT = "SmbMount"


    class azure.mgmt.storagemover.types.JobDefinition(ProxyResource):
        key "id": str
        key "name": str
        key "properties": Required[JobDefinitionProperties]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: JobDefinitionProperties
        system_data: SystemData
        type: str


    class azure.mgmt.storagemover.types.JobDefinitionProperties(TypedDict, total=False):
        key "agentName": str
        key "agentResourceId": str
        key "copyMode": Required[Union[str, CopyMode]]
        key "crossTenantEndpointResourceId": str
        key "crossTenantEndpointTenantId": str
        key "dataIntegrityValidation": Union[str, DataIntegrityValidation]
        key "description": str
        key "isCrossTenantJob": bool
        key "jobType": Union[str, JobType]
        key "latestJobRunName": str
        key "latestJobRunResourceId": str
        key "latestJobRunStatus": Union[str, JobRunStatus]
        key "moverSyncedUntil": str
        key "preservePermissions": bool
        key "provisioningState": Union[str, ProvisioningState]
        key "schedule": ForwardRef('ScheduleInfo', module='types')
        key "sourceName": Required[str]
        key "sourceResourceId": str
        key "sourceSubpath": str
        key "sourceTargetMap": ForwardRef('JobDefinitionPropertiesSourceTargetMap', module='types')
        key "syncMode": str
        key "targetName": Required[str]
        key "targetResourceId": str
        key "targetSubpath": str
        agent_name: str
        agent_resource_id: str
        connections: list[str]
        copy_mode: Union[str, CopyMode]
        cross_tenant_endpoint_resource_id: str
        cross_tenant_endpoint_tenant_id: str
        data_integrity_validation: Union[str, DataIntegrityValidation]
        description: str
        is_cross_tenant_job: bool
        job_type: Union[str, JobType]
        latest_job_run_name: str
        latest_job_run_resource_id: str
        latest_job_run_status: Union[str, JobRunStatus]
        mover_synced_until: str
        preserve_permissions: bool
        provisioning_state: Union[str, ProvisioningState]
        schedule: ScheduleInfo
        source_name: str
        source_resource_id: str
        source_subpath: str
        source_target_map: JobDefinitionPropertiesSourceTargetMap
        sync_mode: str
        target_name: str
        target_resource_id: str
        target_subpath: str


    class azure.mgmt.storagemover.types.JobDefinitionPropertiesSourceTargetMap(TypedDict, total=False):
        value: list[SourceTargetMap]


    class azure.mgmt.storagemover.types.JobDefinitionUpdateParameters(TypedDict, total=False):
        key "properties": ForwardRef('JobDefinitionUpdateProperties', module='types')
        properties: JobDefinitionUpdateProperties


    class azure.mgmt.storagemover.types.JobDefinitionUpdateProperties(TypedDict, total=False):
        key "agentName": str
        key "copyMode": Union[str, CopyMode]
        key "dataIntegrityValidation": Union[str, DataIntegrityValidation]
        key "description": str
        key "moverSyncedUntil": str
        key "schedule": ForwardRef('ScheduleInfo', module='types')
        key "syncMode": str
        agent_name: str
        connections: list[str]
        copy_mode: Union[str, CopyMode]
        data_integrity_validation: Union[str, DataIntegrityValidation]
        description: str
        mover_synced_until: str
        schedule: ScheduleInfo
        sync_mode: str


    class azure.mgmt.storagemover.types.ManagedServiceIdentity(TypedDict, total=False):
        key "principalId": str
        key "tenantId": str
        key "type": Required[Union[str, ManagedServiceIdentityType]]
        principal_id: str
        tenant_id: str
        type: Union[str, ManagedServiceIdentityType]
        userAssignedIdentities: dict[str, UserAssignedIdentity]
        user_assigned_identities: dict[str, UserAssignedIdentity]


    class azure.mgmt.storagemover.types.NfsMountEndpointProperties(TypedDict, total=False):
        key "description": str
        key "endpointKind": Union[str, EndpointKind]
        key "endpointType": Required[Literal[EndpointType.NFS_MOUNT]]
        key "export": Required[str]
        key "host": Required[str]
        key "nfsVersion": Union[str, NfsVersion]
        key "provisioningState": Union[str, ProvisioningState]
        key "sourceType": Union[str, NfsMountSourceType]
        description: str
        endpoint_kind: Union[str, EndpointKind]
        endpoint_type: Literal[EndpointType.NFS_MOUNT]
        export: str
        host: str
        nfs_version: Union[str, NfsVersion]
        provisioning_state: Union[str, ProvisioningState]
        source_type: Union[str, NfsMountSourceType]


    class azure.mgmt.storagemover.types.NfsMountEndpointUpdateProperties(TypedDict, total=False):
        key "description": str
        key "endpointType": Required[Literal[EndpointType.NFS_MOUNT]]
        description: str
        endpoint_type: Literal[EndpointType.NFS_MOUNT]


    class azure.mgmt.storagemover.types.Project(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('ProjectProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: ProjectProperties
        system_data: SystemData
        type: str


    class azure.mgmt.storagemover.types.ProjectProperties(TypedDict, total=False):
        key "description": str
        key "provisioningState": Union[str, ProvisioningState]
        description: str
        provisioning_state: Union[str, ProvisioningState]


    class azure.mgmt.storagemover.types.ProjectUpdateParameters(TypedDict, total=False):
        key "properties": ForwardRef('ProjectUpdateProperties', module='types')
        properties: ProjectUpdateProperties


    class azure.mgmt.storagemover.types.ProjectUpdateProperties(TypedDict, total=False):
        key "description": str
        description: str


    class azure.mgmt.storagemover.types.ProxyResource(Resource):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.storagemover.types.Recurrence(TypedDict, total=False):
        key "endTime": Required[Time]
        key "startTime": Required[Time]
        end_time: Time
        start_time: Time


    class azure.mgmt.storagemover.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.storagemover.types.S3WithHmacEndpointProperties(TypedDict, total=False):
        key "credentials": ForwardRef('AzureKeyVaultS3WithHmacCredentials', module='types')
        key "description": str
        key "endpointKind": Union[str, EndpointKind]
        key "endpointType": Required[Literal[EndpointType.S3_WITH_HMAC]]
        key "otherSourceTypeDescription": str
        key "provisioningState": Union[str, ProvisioningState]
        key "sourceType": Union[str, S3WithHmacSourceType]
        key "sourceUri": str
        credentials: AzureKeyVaultS3WithHmacCredentials
        description: str
        endpoint_kind: Union[str, EndpointKind]
        endpoint_type: Literal[EndpointType.S3_WITH_HMAC]
        other_source_type_description: str
        provisioning_state: Union[str, ProvisioningState]
        source_type: Union[str, S3WithHmacSourceType]
        source_uri: str


    class azure.mgmt.storagemover.types.S3WithHmacEndpointUpdateProperties(TypedDict, total=False):
        key "credentials": ForwardRef('AzureKeyVaultS3WithHmacCredentials', module='types')
        key "description": str
        key "endpointType": Required[Literal[EndpointType.S3_WITH_HMAC]]
        credentials: AzureKeyVaultS3WithHmacCredentials
        description: str
        endpoint_type: Literal[EndpointType.S3_WITH_HMAC]


    class azure.mgmt.storagemover.types.ScheduleInfo(TypedDict, total=False):
        key "cronExpression": str
        key "endDate": str
        key "executionTime": ForwardRef('SchedulerTime', module='types')
        key "frequency": Union[str, Frequency]
        key "isActive": bool
        key "repeatInterval": str
        key "startDate": str
        cron_expression: str
        daysOfMonth: list[int]
        daysOfWeek: list[str]
        days_of_month: list[int]
        days_of_week: list[str]
        end_date: str
        execution_time: SchedulerTime
        frequency: Union[str, Frequency]
        is_active: bool
        repeat_interval: str
        start_date: str


    class azure.mgmt.storagemover.types.SchedulerTime(TypedDict, total=False):
        key "hour": int
        key "minute": Union[int, Minute]
        hour: int
        minute: Union[int, Minute]


    class azure.mgmt.storagemover.types.SmbMountEndpointProperties(TypedDict, total=False):
        key "credentials": ForwardRef('AzureKeyVaultSmbCredentials', module='types')
        key "description": str
        key "endpointKind": Union[str, EndpointKind]
        key "endpointType": Required[Literal[EndpointType.SMB_MOUNT]]
        key "host": Required[str]
        key "provisioningState": Union[str, ProvisioningState]
        key "shareName": Required[str]
        key "sourceType": Union[str, SmbMountSourceType]
        credentials: AzureKeyVaultSmbCredentials
        description: str
        endpoint_kind: Union[str, EndpointKind]
        endpoint_type: Literal[EndpointType.SMB_MOUNT]
        host: str
        provisioning_state: Union[str, ProvisioningState]
        share_name: str
        source_type: Union[str, SmbMountSourceType]


    class azure.mgmt.storagemover.types.SmbMountEndpointUpdateProperties(TypedDict, total=False):
        key "credentials": ForwardRef('AzureKeyVaultSmbCredentials', module='types')
        key "description": str
        key "endpointType": Required[Literal[EndpointType.SMB_MOUNT]]
        credentials: AzureKeyVaultSmbCredentials
        description: str
        endpoint_type: Literal[EndpointType.SMB_MOUNT]


    class azure.mgmt.storagemover.types.SourceEndpoint(TypedDict, total=False):
        key "properties": ForwardRef('SourceEndpointProperties', module='types')
        properties: SourceEndpointProperties


    class azure.mgmt.storagemover.types.SourceEndpointProperties(TypedDict, total=False):
        key "awsS3BucketId": str
        key "name": str
        key "sourceEndpointResourceId": str
        aws_s3_bucket_id: str
        name: str
        source_endpoint_resource_id: str


    class azure.mgmt.storagemover.types.SourceTargetMap(TypedDict, total=False):
        key "sourceEndpoint": Required[SourceEndpoint]
        key "targetEndpoint": Required[TargetEndpoint]
        source_endpoint: SourceEndpoint
        target_endpoint: TargetEndpoint


    class azure.mgmt.storagemover.types.StorageMover(TrackedResource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('StorageMoverProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: StorageMoverProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.storagemover.types.StorageMoverProperties(TypedDict, total=False):
        key "description": str
        key "provisioningState": Union[str, ProvisioningState]
        description: str
        provisioning_state: Union[str, ProvisioningState]


    class azure.mgmt.storagemover.types.StorageMoverUpdateParameters(TypedDict, total=False):
        key "properties": ForwardRef('StorageMoverUpdateProperties', module='types')
        properties: StorageMoverUpdateProperties
        tags: dict[str, str]


    class azure.mgmt.storagemover.types.StorageMoverUpdateProperties(TypedDict, total=False):
        key "description": str
        description: str


    class azure.mgmt.storagemover.types.SystemData(TypedDict, total=False):
        key "createdAt": str
        key "createdBy": str
        key "createdByType": Union[str, CreatedByType]
        key "lastModifiedAt": str
        key "lastModifiedBy": str
        key "lastModifiedByType": Union[str, CreatedByType]
        created_at: str
        created_by: str
        created_by_type: Union[str, CreatedByType]
        last_modified_at: str
        last_modified_by: str
        last_modified_by_type: Union[str, CreatedByType]


    class azure.mgmt.storagemover.types.TargetEndpoint(TypedDict, total=False):
        key "properties": ForwardRef('TargetEndpointProperties', module='types')
        properties: TargetEndpointProperties


    class azure.mgmt.storagemover.types.TargetEndpointProperties(TypedDict, total=False):
        key "azureStorageAccountResourceId": str
        key "azureStorageBlobContainerName": str
        key "name": str
        key "targetEndpointResourceId": str
        azure_storage_account_resource_id: str
        azure_storage_blob_container_name: str
        name: str
        target_endpoint_resource_id: str


    class azure.mgmt.storagemover.types.Time(TypedDict, total=False):
        key "hour": Required[int]
        key "minute": Union[int, Minute]
        hour: int
        minute: Union[int, Minute]


    class azure.mgmt.storagemover.types.TrackedResource(Resource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.storagemover.types.UploadLimitSchedule(TypedDict, total=False):
        weeklyRecurrences: list[UploadLimitWeeklyRecurrence]
        weekly_recurrences: list[UploadLimitWeeklyRecurrence]


    class azure.mgmt.storagemover.types.UploadLimitWeeklyRecurrence(WeeklyRecurrence):
        key "days": Required[list[Union[str, DayOfWeek]]]
        key "endTime": Required[Time]
        key "limitInMbps": Required[int]
        key "startTime": Required[Time]
        days: list[Union[str, DayOfWeek]]
        end_time: Time
        limit_in_mbps: int
        start_time: Time


    class azure.mgmt.storagemover.types.UserAssignedIdentity(TypedDict, total=False):
        key "clientId": str
        key "principalId": str
        client_id: str
        principal_id: str


    class azure.mgmt.storagemover.types.WeeklyRecurrence(Recurrence):
        key "days": Required[list[Union[str, DayOfWeek]]]
        key "endTime": Required[Time]
        key "startTime": Required[Time]
        days: list[Union[str, DayOfWeek]]
        end_time: Time
        start_time: Time


```