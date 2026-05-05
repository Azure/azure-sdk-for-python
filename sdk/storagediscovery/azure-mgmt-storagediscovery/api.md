```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.storagediscovery

    class azure.mgmt.storagediscovery.StorageDiscoveryMgmtClient: implements ContextManager 
        operations: Operations
        storage_discovery_workspaces: StorageDiscoveryWorkspacesOperations

        def __init__(
                self, 
                credential: TokenCredential, 
                subscription_id: str, 
                base_url: Optional[str] = None, 
                *, 
                api_version: str = ..., 
                cloud_setting: Optional[AzureClouds] = ..., 
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


namespace azure.mgmt.storagediscovery.aio

    class azure.mgmt.storagediscovery.aio.StorageDiscoveryMgmtClient: implements AsyncContextManager 
        operations: Operations
        storage_discovery_workspaces: StorageDiscoveryWorkspacesOperations

        def __init__(
                self, 
                credential: AsyncTokenCredential, 
                subscription_id: str, 
                base_url: Optional[str] = None, 
                *, 
                api_version: str = ..., 
                cloud_setting: Optional[AzureClouds] = ..., 
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


namespace azure.mgmt.storagediscovery.aio.operations

    class azure.mgmt.storagediscovery.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


    class azure.mgmt.storagediscovery.aio.operations.StorageDiscoveryWorkspacesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                storage_discovery_workspace_name: str, 
                resource: StorageDiscoveryWorkspace, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StorageDiscoveryWorkspace: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                storage_discovery_workspace_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StorageDiscoveryWorkspace: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                storage_discovery_workspace_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StorageDiscoveryWorkspace: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                storage_discovery_workspace_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                storage_discovery_workspace_name: str, 
                **kwargs: Any
            ) -> StorageDiscoveryWorkspace: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[StorageDiscoveryWorkspace]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[StorageDiscoveryWorkspace]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                storage_discovery_workspace_name: str, 
                properties: StorageDiscoveryWorkspaceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StorageDiscoveryWorkspace: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                storage_discovery_workspace_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StorageDiscoveryWorkspace: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                storage_discovery_workspace_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StorageDiscoveryWorkspace: ...


namespace azure.mgmt.storagediscovery.models

    class azure.mgmt.storagediscovery.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.storagediscovery.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.storagediscovery.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.storagediscovery.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.storagediscovery.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagediscovery.models.Operation(_Model):
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


    class azure.mgmt.storagediscovery.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.storagediscovery.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.storagediscovery.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.storagediscovery.models.ResourceProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.storagediscovery.models.StorageDiscoveryResourceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        STORAGE_ACCOUNTS = "Microsoft.Storage/storageAccounts"


    class azure.mgmt.storagediscovery.models.StorageDiscoveryScope(_Model):
        display_name: str
        resource_types: list[Union[str, StorageDiscoveryResourceType]]
        tag_keys_only: Optional[list[str]]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                display_name: str, 
                resource_types: list[Union[str, StorageDiscoveryResourceType]], 
                tag_keys_only: Optional[list[str]] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagediscovery.models.StorageDiscoverySku(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FREE = "Free"
        STANDARD = "Standard"


    class azure.mgmt.storagediscovery.models.StorageDiscoveryWorkspace(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[StorageDiscoveryWorkspaceProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[StorageDiscoveryWorkspaceProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagediscovery.models.StorageDiscoveryWorkspaceProperties(_Model):
        description: Optional[str]
        provisioning_state: Optional[Union[str, ResourceProvisioningState]]
        scopes: list[StorageDiscoveryScope]
        sku: Optional[Union[str, StorageDiscoverySku]]
        workspace_roots: list[str]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                scopes: list[StorageDiscoveryScope], 
                sku: Optional[Union[str, StorageDiscoverySku]] = ..., 
                workspace_roots: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagediscovery.models.StorageDiscoveryWorkspacePropertiesUpdate(_Model):
        description: Optional[str]
        scopes: Optional[list[StorageDiscoveryScope]]
        sku: Optional[Union[str, StorageDiscoverySku]]
        workspace_roots: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                scopes: Optional[list[StorageDiscoveryScope]] = ..., 
                sku: Optional[Union[str, StorageDiscoverySku]] = ..., 
                workspace_roots: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagediscovery.models.StorageDiscoveryWorkspaceUpdate(_Model):
        properties: Optional[StorageDiscoveryWorkspacePropertiesUpdate]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[StorageDiscoveryWorkspacePropertiesUpdate] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagediscovery.models.SystemData(_Model):
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


    class azure.mgmt.storagediscovery.models.TrackedResource(Resource):
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


namespace azure.mgmt.storagediscovery.operations

    class azure.mgmt.storagediscovery.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


    class azure.mgmt.storagediscovery.operations.StorageDiscoveryWorkspacesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                storage_discovery_workspace_name: str, 
                resource: StorageDiscoveryWorkspace, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StorageDiscoveryWorkspace: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                storage_discovery_workspace_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StorageDiscoveryWorkspace: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                storage_discovery_workspace_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StorageDiscoveryWorkspace: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                storage_discovery_workspace_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                storage_discovery_workspace_name: str, 
                **kwargs: Any
            ) -> StorageDiscoveryWorkspace: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[StorageDiscoveryWorkspace]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[StorageDiscoveryWorkspace]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                storage_discovery_workspace_name: str, 
                properties: StorageDiscoveryWorkspaceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StorageDiscoveryWorkspace: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                storage_discovery_workspace_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StorageDiscoveryWorkspace: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                storage_discovery_workspace_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StorageDiscoveryWorkspace: ...


```