```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.kubernetesconfiguration.privatelinkscopes

    class azure.mgmt.kubernetesconfiguration.privatelinkscopes.KubernetesConfigurationPrivateLinkScopesMgmtClient: implements ContextManager 
        private_endpoint_connections: PrivateEndpointConnectionsOperations
        private_link_resources: PrivateLinkResourcesOperations
        private_link_scopes: PrivateLinkScopesOperations

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


namespace azure.mgmt.kubernetesconfiguration.privatelinkscopes.aio

    class azure.mgmt.kubernetesconfiguration.privatelinkscopes.aio.KubernetesConfigurationPrivateLinkScopesMgmtClient: implements AsyncContextManager 
        private_endpoint_connections: PrivateEndpointConnectionsOperations
        private_link_resources: PrivateLinkResourcesOperations
        private_link_scopes: PrivateLinkScopesOperations

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


namespace azure.mgmt.kubernetesconfiguration.privatelinkscopes.aio.operations

    class azure.mgmt.kubernetesconfiguration.privatelinkscopes.aio.operations.PrivateEndpointConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                scope_name: str, 
                private_endpoint_connection_name: str, 
                properties: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateEndpointConnection]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                scope_name: str, 
                private_endpoint_connection_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateEndpointConnection]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                scope_name: str, 
                private_endpoint_connection_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateEndpointConnection]: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                scope_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                scope_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @distributed_trace_async
        async def list_by_private_link_scope(
                self, 
                resource_group_name: str, 
                scope_name: str, 
                **kwargs: Any
            ) -> PrivateEndpointConnectionListResult: ...


    class azure.mgmt.kubernetesconfiguration.privatelinkscopes.aio.operations.PrivateLinkResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                scope_name: str, 
                group_name: str, 
                **kwargs: Any
            ) -> PrivateLinkResource: ...

        @distributed_trace_async
        async def list_by_private_link_scope(
                self, 
                resource_group_name: str, 
                scope_name: str, 
                **kwargs: Any
            ) -> PrivateLinkResourceListResult: ...


    class azure.mgmt.kubernetesconfiguration.privatelinkscopes.aio.operations.PrivateLinkScopesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                scope_name: str, 
                parameters: KubernetesConfigurationPrivateLinkScope, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> KubernetesConfigurationPrivateLinkScope: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                scope_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> KubernetesConfigurationPrivateLinkScope: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                scope_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> KubernetesConfigurationPrivateLinkScope: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                scope_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                scope_name: str, 
                **kwargs: Any
            ) -> KubernetesConfigurationPrivateLinkScope: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[KubernetesConfigurationPrivateLinkScope]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[KubernetesConfigurationPrivateLinkScope]: ...

        @overload
        async def update_tags(
                self, 
                resource_group_name: str, 
                scope_name: str, 
                private_link_scope_tags: TagsResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> KubernetesConfigurationPrivateLinkScope: ...

        @overload
        async def update_tags(
                self, 
                resource_group_name: str, 
                scope_name: str, 
                private_link_scope_tags: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> KubernetesConfigurationPrivateLinkScope: ...

        @overload
        async def update_tags(
                self, 
                resource_group_name: str, 
                scope_name: str, 
                private_link_scope_tags: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> KubernetesConfigurationPrivateLinkScope: ...


namespace azure.mgmt.kubernetesconfiguration.privatelinkscopes.models

    class azure.mgmt.kubernetesconfiguration.privatelinkscopes.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.kubernetesconfiguration.privatelinkscopes.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.kubernetesconfiguration.privatelinkscopes.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.kubernetesconfiguration.privatelinkscopes.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.kubernetesconfiguration.privatelinkscopes.models.KubernetesConfigurationPrivateLinkScope(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[KubernetesConfigurationPrivateLinkScopeProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[KubernetesConfigurationPrivateLinkScopeProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.kubernetesconfiguration.privatelinkscopes.models.KubernetesConfigurationPrivateLinkScopeProperties(_Model):
        cluster_resource_id: str
        private_endpoint_connections: Optional[list[PrivateEndpointConnection]]
        private_link_scope_id: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        public_network_access: Optional[Union[str, PublicNetworkAccessType]]

        @overload
        def __init__(
                self, 
                *, 
                cluster_resource_id: str, 
                public_network_access: Optional[Union[str, PublicNetworkAccessType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.kubernetesconfiguration.privatelinkscopes.models.PrivateEndpoint(_Model):
        id: Optional[str]


    class azure.mgmt.kubernetesconfiguration.privatelinkscopes.models.PrivateEndpointConnection(Resource):
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


    class azure.mgmt.kubernetesconfiguration.privatelinkscopes.models.PrivateEndpointConnectionListResult(_Model):
        next_link: Optional[str]
        value: list[PrivateEndpointConnection]

        @overload
        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: list[PrivateEndpointConnection]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.kubernetesconfiguration.privatelinkscopes.models.PrivateEndpointConnectionProperties(_Model):
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


    class azure.mgmt.kubernetesconfiguration.privatelinkscopes.models.PrivateEndpointConnectionProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.kubernetesconfiguration.privatelinkscopes.models.PrivateEndpointServiceConnectionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPROVED = "Approved"
        PENDING = "Pending"
        REJECTED = "Rejected"


    class azure.mgmt.kubernetesconfiguration.privatelinkscopes.models.PrivateLinkResource(ProxyResource):
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


    class azure.mgmt.kubernetesconfiguration.privatelinkscopes.models.PrivateLinkResourceListResult(_Model):
        next_link: Optional[str]
        value: list[PrivateLinkResource]

        @overload
        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: list[PrivateLinkResource]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.kubernetesconfiguration.privatelinkscopes.models.PrivateLinkResourceProperties(_Model):
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


    class azure.mgmt.kubernetesconfiguration.privatelinkscopes.models.PrivateLinkServiceConnectionState(_Model):
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


    class azure.mgmt.kubernetesconfiguration.privatelinkscopes.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.kubernetesconfiguration.privatelinkscopes.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.kubernetesconfiguration.privatelinkscopes.models.PublicNetworkAccessType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.kubernetesconfiguration.privatelinkscopes.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.kubernetesconfiguration.privatelinkscopes.models.SystemData(_Model):
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


    class azure.mgmt.kubernetesconfiguration.privatelinkscopes.models.TagsResource(_Model):
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.kubernetesconfiguration.privatelinkscopes.models.TrackedResource(Resource):
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


namespace azure.mgmt.kubernetesconfiguration.privatelinkscopes.operations

    class azure.mgmt.kubernetesconfiguration.privatelinkscopes.operations.PrivateEndpointConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                scope_name: str, 
                private_endpoint_connection_name: str, 
                properties: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateEndpointConnection]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                scope_name: str, 
                private_endpoint_connection_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateEndpointConnection]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                scope_name: str, 
                private_endpoint_connection_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateEndpointConnection]: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                scope_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                scope_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @distributed_trace
        def list_by_private_link_scope(
                self, 
                resource_group_name: str, 
                scope_name: str, 
                **kwargs: Any
            ) -> PrivateEndpointConnectionListResult: ...


    class azure.mgmt.kubernetesconfiguration.privatelinkscopes.operations.PrivateLinkResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                scope_name: str, 
                group_name: str, 
                **kwargs: Any
            ) -> PrivateLinkResource: ...

        @distributed_trace
        def list_by_private_link_scope(
                self, 
                resource_group_name: str, 
                scope_name: str, 
                **kwargs: Any
            ) -> PrivateLinkResourceListResult: ...


    class azure.mgmt.kubernetesconfiguration.privatelinkscopes.operations.PrivateLinkScopesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                scope_name: str, 
                parameters: KubernetesConfigurationPrivateLinkScope, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> KubernetesConfigurationPrivateLinkScope: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                scope_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> KubernetesConfigurationPrivateLinkScope: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                scope_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> KubernetesConfigurationPrivateLinkScope: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                scope_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                scope_name: str, 
                **kwargs: Any
            ) -> KubernetesConfigurationPrivateLinkScope: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[KubernetesConfigurationPrivateLinkScope]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[KubernetesConfigurationPrivateLinkScope]: ...

        @overload
        def update_tags(
                self, 
                resource_group_name: str, 
                scope_name: str, 
                private_link_scope_tags: TagsResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> KubernetesConfigurationPrivateLinkScope: ...

        @overload
        def update_tags(
                self, 
                resource_group_name: str, 
                scope_name: str, 
                private_link_scope_tags: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> KubernetesConfigurationPrivateLinkScope: ...

        @overload
        def update_tags(
                self, 
                resource_group_name: str, 
                scope_name: str, 
                private_link_scope_tags: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> KubernetesConfigurationPrivateLinkScope: ...


```