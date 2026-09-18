```py
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
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StorageDiscoveryWorkspace: ...


namespace azure.mgmt.storagediscovery.models

    class azure.mgmt.storagediscovery.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.storagediscovery.models.AzureBlobStorageCapability(_Model):
        capacity_details: CapacityDetails
        prefix_definitions: Optional[list[PrefixDefinition]]

        @overload
        def __init__(
                self, 
                *, 
                capacity_details: CapacityDetails, 
                prefix_definitions: Optional[list[PrefixDefinition]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagediscovery.models.AzureBlobStorageCapabilityUpdate(_Model):
        capacity_details: Optional[CapacityDetailsUpdate]
        prefix_definitions: Optional[list[PrefixDefinitionUpdate]]

        @overload
        def __init__(
                self, 
                *, 
                capacity_details: Optional[CapacityDetailsUpdate] = ..., 
                prefix_definitions: Optional[list[PrefixDefinitionUpdate]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagediscovery.models.CapabilityStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.storagediscovery.models.CapacityDetails(_Model):
        status: Union[str, CapabilityStatus]

        @overload
        def __init__(
                self, 
                *, 
                status: Union[str, CapabilityStatus]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagediscovery.models.CapacityDetailsUpdate(_Model):
        status: Optional[Union[str, CapabilityStatus]]

        @overload
        def __init__(
                self, 
                *, 
                status: Optional[Union[str, CapabilityStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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


    class azure.mgmt.storagediscovery.models.PrefixDefinition(_Model):
        container_name: str
        prefix: Optional[str]
        storage_account_name: str

        @overload
        def __init__(
                self, 
                *, 
                container_name: str, 
                prefix: Optional[str] = ..., 
                storage_account_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagediscovery.models.PrefixDefinitionUpdate(_Model):
        container_name: Optional[str]
        prefix: Optional[str]
        storage_account_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                container_name: Optional[str] = ..., 
                prefix: Optional[str] = ..., 
                storage_account_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagediscovery.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.storagediscovery.models.ResourceProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.storagediscovery.models.StorageDiscoveryCapabilities(_Model):
        azure_blob_storage: AzureBlobStorageCapability

        @overload
        def __init__(
                self, 
                *, 
                azure_blob_storage: AzureBlobStorageCapability
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagediscovery.models.StorageDiscoveryCapabilitiesUpdate(_Model):
        azure_blob_storage: Optional[AzureBlobStorageCapabilityUpdate]

        @overload
        def __init__(
                self, 
                *, 
                azure_blob_storage: Optional[AzureBlobStorageCapabilityUpdate] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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
        capabilities: Optional[StorageDiscoveryCapabilities]
        description: Optional[str]
        provisioning_state: Optional[Union[str, ResourceProvisioningState]]
        scopes: list[StorageDiscoveryScope]
        sku: Optional[Union[str, StorageDiscoverySku]]
        workspace_roots: list[str]

        @overload
        def __init__(
                self, 
                *, 
                capabilities: Optional[StorageDiscoveryCapabilities] = ..., 
                description: Optional[str] = ..., 
                scopes: list[StorageDiscoveryScope], 
                sku: Optional[Union[str, StorageDiscoverySku]] = ..., 
                workspace_roots: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagediscovery.models.StorageDiscoveryWorkspacePropertiesUpdate(_Model):
        capabilities: Optional[StorageDiscoveryCapabilitiesUpdate]
        description: Optional[str]
        scopes: Optional[list[StorageDiscoveryScope]]
        sku: Optional[Union[str, StorageDiscoverySku]]
        workspace_roots: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                capabilities: Optional[StorageDiscoveryCapabilitiesUpdate] = ..., 
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
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StorageDiscoveryWorkspace: ...


namespace azure.mgmt.storagediscovery.types

    class azure.mgmt.storagediscovery.types.AzureBlobStorageCapability(TypedDict, total=False):
        key "capacityDetails": Required[CapacityDetails]
        capacityDetails: CapacityDetails
        prefixDefinitions: list[PrefixDefinition]


    class azure.mgmt.storagediscovery.types.AzureBlobStorageCapabilityUpdate(TypedDict, total=False):
        key "capacityDetails": ForwardRef('CapacityDetailsUpdate', module='types')
        capacityDetails: CapacityDetailsUpdate
        prefixDefinitions: list[PrefixDefinitionUpdate]


    class azure.mgmt.storagediscovery.types.CapacityDetails(TypedDict, total=False):
        key "status": Required[Union[str, CapabilityStatus]]
        status: Union[str, CapabilityStatus]


    class azure.mgmt.storagediscovery.types.CapacityDetailsUpdate(TypedDict, total=False):
        key "status": Union[str, CapabilityStatus]
        status: Union[str, CapabilityStatus]


    class azure.mgmt.storagediscovery.types.PrefixDefinition(TypedDict, total=False):
        key "containerName": Required[str]
        key "prefix": str
        key "storageAccountName": Required[str]
        containerName: str
        prefix: str
        storageAccountName: str


    class azure.mgmt.storagediscovery.types.PrefixDefinitionUpdate(TypedDict, total=False):
        key "containerName": str
        key "prefix": str
        key "storageAccountName": str
        containerName: str
        prefix: str
        storageAccountName: str


    class azure.mgmt.storagediscovery.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        systemData: SystemData
        type: str


    class azure.mgmt.storagediscovery.types.StorageDiscoveryCapabilities(TypedDict, total=False):
        key "azureBlobStorage": Required[AzureBlobStorageCapability]
        azureBlobStorage: AzureBlobStorageCapability


    class azure.mgmt.storagediscovery.types.StorageDiscoveryCapabilitiesUpdate(TypedDict, total=False):
        key "azureBlobStorage": ForwardRef('AzureBlobStorageCapabilityUpdate', module='types')
        azureBlobStorage: AzureBlobStorageCapabilityUpdate


    class azure.mgmt.storagediscovery.types.StorageDiscoveryScope(TypedDict, total=False):
        key "displayName": Required[str]
        key "resourceTypes": Required[list[Union[str, StorageDiscoveryResourceType]]]
        displayName: str
        resourceTypes: list[Union[str, StorageDiscoveryResourceType]]
        tagKeysOnly: list[str]
        tags: dict[str, str]


    class azure.mgmt.storagediscovery.types.StorageDiscoveryWorkspace(TrackedResource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('StorageDiscoveryWorkspaceProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: StorageDiscoveryWorkspaceProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.storagediscovery.types.StorageDiscoveryWorkspaceProperties(TypedDict, total=False):
        key "capabilities": ForwardRef('StorageDiscoveryCapabilities', module='types')
        key "description": str
        key "provisioningState": Union[str, ResourceProvisioningState]
        key "scopes": Required[list[StorageDiscoveryScope]]
        key "sku": Union[str, StorageDiscoverySku]
        key "workspaceRoots": Required[list[str]]
        capabilities: StorageDiscoveryCapabilities
        description: str
        provisioningState: Union[str, ResourceProvisioningState]
        scopes: list[StorageDiscoveryScope]
        sku: Union[str, StorageDiscoverySku]
        workspaceRoots: list[str]


    class azure.mgmt.storagediscovery.types.StorageDiscoveryWorkspacePropertiesUpdate(TypedDict, total=False):
        key "capabilities": ForwardRef('StorageDiscoveryCapabilitiesUpdate', module='types')
        key "description": str
        key "sku": Union[str, StorageDiscoverySku]
        capabilities: StorageDiscoveryCapabilitiesUpdate
        description: str
        scopes: list[StorageDiscoveryScope]
        sku: Union[str, StorageDiscoverySku]
        workspaceRoots: list[str]


    class azure.mgmt.storagediscovery.types.StorageDiscoveryWorkspaceUpdate(TypedDict, total=False):
        key "properties": ForwardRef('StorageDiscoveryWorkspacePropertiesUpdate', module='types')
        properties: StorageDiscoveryWorkspacePropertiesUpdate
        tags: dict[str, str]


    class azure.mgmt.storagediscovery.types.SystemData(TypedDict, total=False):
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


    class azure.mgmt.storagediscovery.types.TrackedResource(Resource):
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


```