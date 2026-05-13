```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.healthdataaiservices

    class azure.mgmt.healthdataaiservices.HealthDataAIServicesMgmtClient: implements ContextManager 
        deid_services: DeidServicesOperations
        operations: Operations
        private_endpoint_connections: PrivateEndpointConnectionsOperations
        private_links: PrivateLinksOperations

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

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> HttpResponse: ...


namespace azure.mgmt.healthdataaiservices.aio

    class azure.mgmt.healthdataaiservices.aio.HealthDataAIServicesMgmtClient: implements AsyncContextManager 
        deid_services: DeidServicesOperations
        operations: Operations
        private_endpoint_connections: PrivateEndpointConnectionsOperations
        private_links: PrivateLinksOperations

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

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> Awaitable[AsyncHttpResponse]: ...


namespace azure.mgmt.healthdataaiservices.aio.operations

    class azure.mgmt.healthdataaiservices.aio.operations.DeidServicesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                deid_service_name: str, 
                resource: DeidService, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DeidService]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                deid_service_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DeidService]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                deid_service_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DeidService]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                deid_service_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                deid_service_name: str, 
                properties: DeidUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DeidService]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                deid_service_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DeidService]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                deid_service_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DeidService]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                deid_service_name: str, 
                **kwargs: Any
            ) -> DeidService: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[DeidService]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncIterable[DeidService]: ...


    class azure.mgmt.healthdataaiservices.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncIterable[Operation]: ...


    class azure.mgmt.healthdataaiservices.aio.operations.PrivateEndpointConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                deid_service_name: str, 
                private_endpoint_connection_name: str, 
                resource: PrivateEndpointConnectionResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateEndpointConnectionResource]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                deid_service_name: str, 
                private_endpoint_connection_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateEndpointConnectionResource]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                deid_service_name: str, 
                private_endpoint_connection_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateEndpointConnectionResource]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                deid_service_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                deid_service_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> PrivateEndpointConnectionResource: ...

        @distributed_trace
        def list_by_deid_service(
                self, 
                resource_group_name: str, 
                deid_service_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[PrivateEndpointConnectionResource]: ...


    class azure.mgmt.healthdataaiservices.aio.operations.PrivateLinksOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_by_deid_service(
                self, 
                resource_group_name: str, 
                deid_service_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[PrivateLinkResource]: ...


namespace azure.mgmt.healthdataaiservices.models

    class azure.mgmt.healthdataaiservices.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.healthdataaiservices.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.healthdataaiservices.models.DeidPropertiesUpdate(Model):
        public_network_access: Optional[Union[str, PublicNetworkAccess]]

        @overload
        def __init__(
                self, 
                *, 
                public_network_access: Optional[Union[str, PublicNetworkAccess]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.healthdataaiservices.models.DeidService(TrackedResource):
        id: str
        identity: Optional[ManagedServiceIdentity]
        location: str
        name: str
        properties: Optional[DeidServiceProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                location: str, 
                properties: Optional[DeidServiceProperties] = ..., 
                tags: Optional[Dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.healthdataaiservices.models.DeidServiceProperties(Model):
        private_endpoint_connections: Optional[List[PrivateEndpointConnection]]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        public_network_access: Optional[Union[str, PublicNetworkAccess]]
        service_url: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                public_network_access: Optional[Union[str, PublicNetworkAccess]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.healthdataaiservices.models.DeidUpdate(Model):
        identity: Optional[ManagedServiceIdentityUpdate]
        properties: Optional[DeidPropertiesUpdate]
        tags: Optional[Dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentityUpdate] = ..., 
                properties: Optional[DeidPropertiesUpdate] = ..., 
                tags: Optional[Dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.healthdataaiservices.models.ErrorAdditionalInfo(Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.healthdataaiservices.models.ErrorDetail(Model):
        additional_info: Optional[List[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[List[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.healthdataaiservices.models.ErrorResponse(Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.healthdataaiservices.models.ManagedServiceIdentity(Model):
        principal_id: Optional[str]
        tenant_id: Optional[str]
        type: Union[str, ManagedServiceIdentityType]
        user_assigned_identities: Optional[Dict[str, UserAssignedIdentity]]

        @overload
        def __init__(
                self, 
                *, 
                type: Union[str, ManagedServiceIdentityType], 
                user_assigned_identities: Optional[Dict[str, UserAssignedIdentity]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.healthdataaiservices.models.ManagedServiceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        SYSTEM_ASSIGNED_USER_ASSIGNED = "SystemAssigned,UserAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.healthdataaiservices.models.ManagedServiceIdentityUpdate(Model):
        type: Optional[Union[str, ManagedServiceIdentityType]]
        user_assigned_identities: Optional[Dict[str, UserAssignedIdentity]]

        @overload
        def __init__(
                self, 
                *, 
                type: Optional[Union[str, ManagedServiceIdentityType]] = ..., 
                user_assigned_identities: Optional[Dict[str, UserAssignedIdentity]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.healthdataaiservices.models.Operation(Model):
        action_type: Optional[Union[str, ActionType]]
        display: Optional[OperationDisplay]
        is_data_action: Optional[bool]
        name: Optional[str]
        origin: Optional[Union[str, Origin]]

        @overload
        def __init__(
                self, 
                *, 
                action_type: Optional[Union[str, ActionType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.healthdataaiservices.models.OperationDisplay(Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.healthdataaiservices.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.healthdataaiservices.models.PrivateEndpoint(Model):
        id: Optional[str]


    class azure.mgmt.healthdataaiservices.models.PrivateEndpointConnection(Resource):
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


    class azure.mgmt.healthdataaiservices.models.PrivateEndpointConnectionProperties(Model):
        group_ids: Optional[List[str]]
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


    class azure.mgmt.healthdataaiservices.models.PrivateEndpointConnectionProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.healthdataaiservices.models.PrivateEndpointConnectionResource(ProxyResource):
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


    class azure.mgmt.healthdataaiservices.models.PrivateEndpointServiceConnectionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPROVED = "Approved"
        PENDING = "Pending"
        REJECTED = "Rejected"


    class azure.mgmt.healthdataaiservices.models.PrivateLinkResource(ProxyResource):
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


    class azure.mgmt.healthdataaiservices.models.PrivateLinkResourceProperties(Model):
        group_id: Optional[str]
        required_members: Optional[List[str]]
        required_zone_names: Optional[List[str]]

        @overload
        def __init__(
                self, 
                *, 
                required_zone_names: Optional[List[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.healthdataaiservices.models.PrivateLinkServiceConnectionState(Model):
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


    class azure.mgmt.healthdataaiservices.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CANCELED = "Canceled"
        DELETING = "Deleting"
        FAILED = "Failed"
        PROVISIONING = "Provisioning"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.healthdataaiservices.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.healthdataaiservices.models.PublicNetworkAccess(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.healthdataaiservices.models.Resource(Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.healthdataaiservices.models.SystemData(Model):
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


    class azure.mgmt.healthdataaiservices.models.TrackedResource(Resource):
        id: str
        location: str
        name: str
        system_data: SystemData
        tags: Optional[Dict[str, str]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                tags: Optional[Dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.healthdataaiservices.models.UserAssignedIdentity(Model):
        client_id: Optional[str]
        principal_id: Optional[str]


namespace azure.mgmt.healthdataaiservices.operations

    class azure.mgmt.healthdataaiservices.operations.DeidServicesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                deid_service_name: str, 
                resource: DeidService, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DeidService]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                deid_service_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DeidService]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                deid_service_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DeidService]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                deid_service_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                deid_service_name: str, 
                properties: DeidUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DeidService]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                deid_service_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DeidService]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                deid_service_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DeidService]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                deid_service_name: str, 
                **kwargs: Any
            ) -> DeidService: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> Iterable[DeidService]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> Iterable[DeidService]: ...


    class azure.mgmt.healthdataaiservices.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def list(self, **kwargs: Any) -> Iterable[Operation]: ...


    class azure.mgmt.healthdataaiservices.operations.PrivateEndpointConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                deid_service_name: str, 
                private_endpoint_connection_name: str, 
                resource: PrivateEndpointConnectionResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateEndpointConnectionResource]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                deid_service_name: str, 
                private_endpoint_connection_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateEndpointConnectionResource]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                deid_service_name: str, 
                private_endpoint_connection_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateEndpointConnectionResource]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                deid_service_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                deid_service_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> PrivateEndpointConnectionResource: ...

        @distributed_trace
        def list_by_deid_service(
                self, 
                resource_group_name: str, 
                deid_service_name: str, 
                **kwargs: Any
            ) -> Iterable[PrivateEndpointConnectionResource]: ...


    class azure.mgmt.healthdataaiservices.operations.PrivateLinksOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def list_by_deid_service(
                self, 
                resource_group_name: str, 
                deid_service_name: str, 
                **kwargs: Any
            ) -> Iterable[PrivateLinkResource]: ...


```