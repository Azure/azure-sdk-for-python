```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.durabletask

    class azure.mgmt.durabletask.DurableTaskMgmtClient: implements ContextManager 
        operations: Operations
        retention_policies: RetentionPoliciesOperations
        schedulers: SchedulersOperations
        task_hubs: TaskHubsOperations

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


namespace azure.mgmt.durabletask.aio

    class azure.mgmt.durabletask.aio.DurableTaskMgmtClient: implements AsyncContextManager 
        operations: Operations
        retention_policies: RetentionPoliciesOperations
        schedulers: SchedulersOperations
        task_hubs: TaskHubsOperations

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


namespace azure.mgmt.durabletask.aio.operations

    class azure.mgmt.durabletask.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


    class azure.mgmt.durabletask.aio.operations.RetentionPoliciesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                resource: RetentionPolicy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[RetentionPolicy]: ...

        @overload
        async def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[RetentionPolicy]: ...

        @overload
        async def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[RetentionPolicy]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-04-01-preview', params_added_on={'2025-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'scheduler_name']}, api_versions_list=['2025-04-01-preview', '2025-11-01', '2026-02-01'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                properties: RetentionPolicy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[RetentionPolicy]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[RetentionPolicy]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[RetentionPolicy]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-04-01-preview', params_added_on={'2025-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'scheduler_name', 'accept']}, api_versions_list=['2025-04-01-preview', '2025-11-01', '2026-02-01'])
        async def get(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                **kwargs: Any
            ) -> RetentionPolicy: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-04-01-preview', params_added_on={'2025-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'scheduler_name', 'accept']}, api_versions_list=['2025-04-01-preview', '2025-11-01', '2026-02-01'])
        def list_by_scheduler(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[RetentionPolicy]: ...


    class azure.mgmt.durabletask.aio.operations.SchedulersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                resource: Scheduler, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Scheduler]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Scheduler]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Scheduler]: ...

        @overload
        async def begin_create_or_update_private_endpoint_connection(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                private_endpoint_connection_name: str, 
                resource: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateEndpointConnection]: ...

        @overload
        async def begin_create_or_update_private_endpoint_connection(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                private_endpoint_connection_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateEndpointConnection]: ...

        @overload
        async def begin_create_or_update_private_endpoint_connection(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                private_endpoint_connection_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateEndpointConnection]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-02-01', params_added_on={'2026-02-01': ['api_version', 'subscription_id', 'resource_group_name', 'scheduler_name', 'private_endpoint_connection_name']}, api_versions_list=['2026-02-01'])
        async def begin_delete_private_endpoint_connection(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                properties: SchedulerUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Scheduler]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Scheduler]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Scheduler]: ...

        @overload
        async def begin_update_private_endpoint_connection(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                private_endpoint_connection_name: str, 
                properties: PrivateEndpointConnectionUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateEndpointConnection]: ...

        @overload
        async def begin_update_private_endpoint_connection(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                private_endpoint_connection_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateEndpointConnection]: ...

        @overload
        async def begin_update_private_endpoint_connection(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                private_endpoint_connection_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateEndpointConnection]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                **kwargs: Any
            ) -> Scheduler: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-02-01', params_added_on={'2026-02-01': ['api_version', 'subscription_id', 'resource_group_name', 'scheduler_name', 'private_endpoint_connection_name', 'accept']}, api_versions_list=['2026-02-01'])
        async def get_private_endpoint_connection(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-02-01', params_added_on={'2026-02-01': ['api_version', 'subscription_id', 'resource_group_name', 'scheduler_name', 'private_link_resource_name', 'accept']}, api_versions_list=['2026-02-01'])
        async def get_private_link(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                private_link_resource_name: str, 
                **kwargs: Any
            ) -> SchedulerPrivateLinkResource: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Scheduler]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[Scheduler]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-02-01', params_added_on={'2026-02-01': ['api_version', 'subscription_id', 'resource_group_name', 'scheduler_name', 'accept']}, api_versions_list=['2026-02-01'])
        def list_private_endpoint_connections(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[PrivateEndpointConnection]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-02-01', params_added_on={'2026-02-01': ['api_version', 'subscription_id', 'resource_group_name', 'scheduler_name', 'accept']}, api_versions_list=['2026-02-01'])
        def list_private_links(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[SchedulerPrivateLinkResource]: ...


    class azure.mgmt.durabletask.aio.operations.TaskHubsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                task_hub_name: str, 
                resource: TaskHub, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[TaskHub]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                task_hub_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[TaskHub]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                task_hub_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[TaskHub]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                task_hub_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                task_hub_name: str, 
                **kwargs: Any
            ) -> TaskHub: ...

        @distributed_trace
        def list_by_scheduler(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[TaskHub]: ...


namespace azure.mgmt.durabletask.models

    class azure.mgmt.durabletask.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.durabletask.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.durabletask.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.durabletask.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.durabletask.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.durabletask.models.Operation(_Model):
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


    class azure.mgmt.durabletask.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.durabletask.models.OptionalPropertiesUpdateableProperties(_Model):
        private_endpoint: Optional[PrivateEndpoint]
        private_link_service_connection_state: Optional[PrivateLinkServiceConnectionState]

        @overload
        def __init__(
                self, 
                *, 
                private_endpoint: Optional[PrivateEndpoint] = ..., 
                private_link_service_connection_state: Optional[PrivateLinkServiceConnectionState] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.durabletask.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.durabletask.models.PrivateEndpoint(_Model):
        id: Optional[str]


    class azure.mgmt.durabletask.models.PrivateEndpointConnection(Resource):
        id: str
        name: str
        properties: Optional[PrivateEndpointConnectionProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[PrivateEndpointConnectionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.durabletask.models.PrivateEndpointConnectionProperties(_Model):
        group_ids: Optional[list[str]]
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


    class azure.mgmt.durabletask.models.PrivateEndpointConnectionProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.durabletask.models.PrivateEndpointConnectionUpdate(_Model):
        properties: Optional[OptionalPropertiesUpdateableProperties]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[OptionalPropertiesUpdateableProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.durabletask.models.PrivateEndpointServiceConnectionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPROVED = "Approved"
        PENDING = "Pending"
        REJECTED = "Rejected"


    class azure.mgmt.durabletask.models.PrivateLinkResourceProperties(_Model):
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


    class azure.mgmt.durabletask.models.PrivateLinkServiceConnectionState(_Model):
        actions_required: Optional[str]
        description: Optional[str]
        status: Optional[Union[str, PrivateEndpointServiceConnectionStatus]]

        @overload
        def __init__(
                self, 
                *, 
                actions_required: Optional[str] = ..., 
                description: Optional[str] = ..., 
                status: Optional[Union[str, PrivateEndpointServiceConnectionStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.durabletask.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CANCELED = "Canceled"
        DELETING = "Deleting"
        FAILED = "Failed"
        PROVISIONING = "Provisioning"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.durabletask.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.durabletask.models.PublicNetworkAccess(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.durabletask.models.PurgeableOrchestrationState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        COMPLETED = "Completed"
        FAILED = "Failed"
        TERMINATED = "Terminated"


    class azure.mgmt.durabletask.models.RedundancyState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        ZONE = "Zone"


    class azure.mgmt.durabletask.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.durabletask.models.RetentionPolicy(ProxyResource):
        id: str
        name: str
        properties: Optional[RetentionPolicyProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[RetentionPolicyProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.durabletask.models.RetentionPolicyDetails(_Model):
        orchestration_state: Optional[Union[str, PurgeableOrchestrationState]]
        retention_period_in_days: int

        @overload
        def __init__(
                self, 
                *, 
                orchestration_state: Optional[Union[str, PurgeableOrchestrationState]] = ..., 
                retention_period_in_days: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.durabletask.models.RetentionPolicyProperties(_Model):
        provisioning_state: Optional[Union[str, ProvisioningState]]
        retention_policies: Optional[list[RetentionPolicyDetails]]

        @overload
        def __init__(
                self, 
                *, 
                retention_policies: Optional[list[RetentionPolicyDetails]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.durabletask.models.Scheduler(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[SchedulerProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[SchedulerProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.durabletask.models.SchedulerPrivateLinkResource(Resource):
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


    class azure.mgmt.durabletask.models.SchedulerProperties(_Model):
        endpoint: Optional[str]
        ip_allowlist: list[str]
        private_endpoint_connections: Optional[list[PrivateEndpointConnection]]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        public_network_access: Optional[Union[str, PublicNetworkAccess]]
        sku: SchedulerSku

        @overload
        def __init__(
                self, 
                *, 
                ip_allowlist: list[str], 
                public_network_access: Optional[Union[str, PublicNetworkAccess]] = ..., 
                sku: SchedulerSku
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.durabletask.models.SchedulerPropertiesUpdate(_Model):
        endpoint: Optional[str]
        ip_allowlist: Optional[list[str]]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        public_network_access: Optional[Union[str, PublicNetworkAccess]]
        sku: Optional[SchedulerSkuUpdate]

        @overload
        def __init__(
                self, 
                *, 
                ip_allowlist: Optional[list[str]] = ..., 
                public_network_access: Optional[Union[str, PublicNetworkAccess]] = ..., 
                sku: Optional[SchedulerSkuUpdate] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.durabletask.models.SchedulerSku(_Model):
        capacity: Optional[int]
        name: Union[str, SchedulerSkuName]
        redundancy_state: Optional[Union[str, RedundancyState]]

        @overload
        def __init__(
                self, 
                *, 
                capacity: Optional[int] = ..., 
                name: Union[str, SchedulerSkuName]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.durabletask.models.SchedulerSkuName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONSUMPTION = "Consumption"
        DEDICATED = "Dedicated"


    class azure.mgmt.durabletask.models.SchedulerSkuUpdate(_Model):
        capacity: Optional[int]
        name: Optional[Union[str, SchedulerSkuName]]
        redundancy_state: Optional[Union[str, RedundancyState]]

        @overload
        def __init__(
                self, 
                *, 
                capacity: Optional[int] = ..., 
                name: Optional[Union[str, SchedulerSkuName]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.durabletask.models.SchedulerUpdate(_Model):
        properties: Optional[SchedulerPropertiesUpdate]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SchedulerPropertiesUpdate] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.durabletask.models.SystemData(_Model):
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


    class azure.mgmt.durabletask.models.TaskHub(ProxyResource):
        id: str
        name: str
        properties: Optional[TaskHubProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[TaskHubProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.durabletask.models.TaskHubProperties(_Model):
        dashboard_url: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]


    class azure.mgmt.durabletask.models.TrackedResource(Resource):
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


namespace azure.mgmt.durabletask.operations

    class azure.mgmt.durabletask.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


    class azure.mgmt.durabletask.operations.RetentionPoliciesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                resource: RetentionPolicy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[RetentionPolicy]: ...

        @overload
        def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[RetentionPolicy]: ...

        @overload
        def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[RetentionPolicy]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-04-01-preview', params_added_on={'2025-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'scheduler_name']}, api_versions_list=['2025-04-01-preview', '2025-11-01', '2026-02-01'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                properties: RetentionPolicy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[RetentionPolicy]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[RetentionPolicy]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[RetentionPolicy]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-04-01-preview', params_added_on={'2025-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'scheduler_name', 'accept']}, api_versions_list=['2025-04-01-preview', '2025-11-01', '2026-02-01'])
        def get(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                **kwargs: Any
            ) -> RetentionPolicy: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-04-01-preview', params_added_on={'2025-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'scheduler_name', 'accept']}, api_versions_list=['2025-04-01-preview', '2025-11-01', '2026-02-01'])
        def list_by_scheduler(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                **kwargs: Any
            ) -> ItemPaged[RetentionPolicy]: ...


    class azure.mgmt.durabletask.operations.SchedulersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                resource: Scheduler, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Scheduler]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Scheduler]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Scheduler]: ...

        @overload
        def begin_create_or_update_private_endpoint_connection(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                private_endpoint_connection_name: str, 
                resource: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateEndpointConnection]: ...

        @overload
        def begin_create_or_update_private_endpoint_connection(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                private_endpoint_connection_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateEndpointConnection]: ...

        @overload
        def begin_create_or_update_private_endpoint_connection(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                private_endpoint_connection_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateEndpointConnection]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-02-01', params_added_on={'2026-02-01': ['api_version', 'subscription_id', 'resource_group_name', 'scheduler_name', 'private_endpoint_connection_name']}, api_versions_list=['2026-02-01'])
        def begin_delete_private_endpoint_connection(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                properties: SchedulerUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Scheduler]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Scheduler]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Scheduler]: ...

        @overload
        def begin_update_private_endpoint_connection(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                private_endpoint_connection_name: str, 
                properties: PrivateEndpointConnectionUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateEndpointConnection]: ...

        @overload
        def begin_update_private_endpoint_connection(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                private_endpoint_connection_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateEndpointConnection]: ...

        @overload
        def begin_update_private_endpoint_connection(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                private_endpoint_connection_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateEndpointConnection]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                **kwargs: Any
            ) -> Scheduler: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-02-01', params_added_on={'2026-02-01': ['api_version', 'subscription_id', 'resource_group_name', 'scheduler_name', 'private_endpoint_connection_name', 'accept']}, api_versions_list=['2026-02-01'])
        def get_private_endpoint_connection(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-02-01', params_added_on={'2026-02-01': ['api_version', 'subscription_id', 'resource_group_name', 'scheduler_name', 'private_link_resource_name', 'accept']}, api_versions_list=['2026-02-01'])
        def get_private_link(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                private_link_resource_name: str, 
                **kwargs: Any
            ) -> SchedulerPrivateLinkResource: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Scheduler]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[Scheduler]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-02-01', params_added_on={'2026-02-01': ['api_version', 'subscription_id', 'resource_group_name', 'scheduler_name', 'accept']}, api_versions_list=['2026-02-01'])
        def list_private_endpoint_connections(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                **kwargs: Any
            ) -> ItemPaged[PrivateEndpointConnection]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-02-01', params_added_on={'2026-02-01': ['api_version', 'subscription_id', 'resource_group_name', 'scheduler_name', 'accept']}, api_versions_list=['2026-02-01'])
        def list_private_links(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                **kwargs: Any
            ) -> ItemPaged[SchedulerPrivateLinkResource]: ...


    class azure.mgmt.durabletask.operations.TaskHubsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                task_hub_name: str, 
                resource: TaskHub, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[TaskHub]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                task_hub_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[TaskHub]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                task_hub_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[TaskHub]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                task_hub_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                task_hub_name: str, 
                **kwargs: Any
            ) -> TaskHub: ...

        @distributed_trace
        def list_by_scheduler(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                **kwargs: Any
            ) -> ItemPaged[TaskHub]: ...


```