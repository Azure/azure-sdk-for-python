```py
namespace azure.mgmt.digitalassets

    class azure.mgmt.digitalassets.DigitalAssetsMgmtClient: implements ContextManager 
        operations: Operations
        partitions: PartitionsOperations
        zkp_rollups: ZkpRollupsOperations

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


namespace azure.mgmt.digitalassets.aio

    class azure.mgmt.digitalassets.aio.DigitalAssetsMgmtClient: implements AsyncContextManager 
        operations: Operations
        partitions: PartitionsOperations
        zkp_rollups: ZkpRollupsOperations

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


namespace azure.mgmt.digitalassets.aio.operations

    class azure.mgmt.digitalassets.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


    class azure.mgmt.digitalassets.aio.operations.PartitionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                zkp_rollup_name: str, 
                partition_name: str, 
                resource: Partition, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Partition]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                zkp_rollup_name: str, 
                partition_name: str, 
                resource: Partition, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Partition]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                zkp_rollup_name: str, 
                partition_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Partition]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                zkp_rollup_name: str, 
                partition_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                zkp_rollup_name: str, 
                partition_name: str, 
                **kwargs: Any
            ) -> Partition: ...

        @distributed_trace
        def list_by_parent(
                self, 
                resource_group_name: str, 
                zkp_rollup_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Partition]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                zkp_rollup_name: str, 
                partition_name: str, 
                properties: PartitionTagsUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Partition: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                zkp_rollup_name: str, 
                partition_name: str, 
                properties: PartitionTagsUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Partition: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                zkp_rollup_name: str, 
                partition_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Partition: ...


    class azure.mgmt.digitalassets.aio.operations.ZkpRollupsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                zkp_rollup_name: str, 
                resource: ZkpRollup, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ZkpRollup]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                zkp_rollup_name: str, 
                resource: ZkpRollup, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ZkpRollup]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                zkp_rollup_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ZkpRollup]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                zkp_rollup_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                zkp_rollup_name: str, 
                properties: ZkpRollupUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ZkpRollup]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                zkp_rollup_name: str, 
                properties: ZkpRollupUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ZkpRollup]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                zkp_rollup_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ZkpRollup]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                zkp_rollup_name: str, 
                **kwargs: Any
            ) -> ZkpRollup: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ZkpRollup]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[ZkpRollup]: ...


namespace azure.mgmt.digitalassets.models

    class azure.mgmt.digitalassets.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.digitalassets.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.digitalassets.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.digitalassets.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.digitalassets.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.digitalassets.models.ManagedServiceIdentity(_Model):
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


    class azure.mgmt.digitalassets.models.ManagedServiceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        SYSTEM_ASSIGNED_USER_ASSIGNED = "SystemAssigned,UserAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.digitalassets.models.Operation(_Model):
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


    class azure.mgmt.digitalassets.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.digitalassets.models.OperationalStatus(_Model):
        evaluated_at: datetime
        status: str
        valid_until: datetime

        @overload
        def __init__(
                self, 
                *, 
                evaluated_at: datetime, 
                status: str, 
                valid_until: datetime
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.digitalassets.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.digitalassets.models.Partition(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[PartitionProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[PartitionProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.digitalassets.models.PartitionProperties(_Model):
        operational_status: Optional[OperationalStatus]
        provisioning_state: Optional[Union[str, ProvisioningState]]


    class azure.mgmt.digitalassets.models.PartitionTagsUpdate(_Model):
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.digitalassets.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CANCELED = "Canceled"
        DELETING = "Deleting"
        FAILED = "Failed"
        PROVISIONING = "Provisioning"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.digitalassets.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.digitalassets.models.SystemData(_Model):
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


    class azure.mgmt.digitalassets.models.TrackedResource(Resource):
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


    class azure.mgmt.digitalassets.models.UserAssignedIdentity(_Model):
        client_id: Optional[str]
        principal_id: Optional[str]


    class azure.mgmt.digitalassets.models.ZkpRollup(TrackedResource):
        id: str
        identity: Optional[ManagedServiceIdentity]
        location: str
        name: str
        properties: Optional[ZkpRollupProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                location: str, 
                properties: Optional[ZkpRollupProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.digitalassets.models.ZkpRollupIdentityUpdate(_Model):
        type: Optional[Union[str, ManagedServiceIdentityType]]
        user_assigned_identities: Optional[dict[str, UserAssignedIdentity]]

        @overload
        def __init__(
                self, 
                *, 
                type: Optional[Union[str, ManagedServiceIdentityType]] = ..., 
                user_assigned_identities: Optional[dict[str, UserAssignedIdentity]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.digitalassets.models.ZkpRollupPatchProperties(_Model):
        boot_node_id: Optional[str]
        boot_node_ip: Optional[str]
        boot_node_p2_p_port: Optional[int]
        boot_node_rpc_port: Optional[int]
        token_owner_accounts: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                boot_node_id: Optional[str] = ..., 
                boot_node_ip: Optional[str] = ..., 
                boot_node_p2_p_port: Optional[int] = ..., 
                boot_node_rpc_port: Optional[int] = ..., 
                token_owner_accounts: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.digitalassets.models.ZkpRollupProperties(_Model):
        blocks_per_proof: Optional[int]
        boot_node_id: str
        boot_node_ip: str
        boot_node_p2_p_port: int
        boot_node_rpc_port: int
        customer_on_prem_address_prefixes: Optional[list[str]]
        customer_vpn_public_ip: Optional[str]
        key_vault_id: str
        key_vault_user_assigned_identity_resource_id: str
        operational_status: Optional[OperationalStatus]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        service_bus_endpoint: str
        service_bus_queue_name: str
        service_vpn_address_space: Optional[str]
        service_vpn_public_ip: Optional[str]
        token_owner_accounts: list[str]

        @overload
        def __init__(
                self, 
                *, 
                blocks_per_proof: Optional[int] = ..., 
                boot_node_id: str, 
                boot_node_ip: str, 
                boot_node_p2_p_port: int, 
                boot_node_rpc_port: int, 
                customer_on_prem_address_prefixes: Optional[list[str]] = ..., 
                customer_vpn_public_ip: Optional[str] = ..., 
                key_vault_id: str, 
                key_vault_user_assigned_identity_resource_id: str, 
                service_bus_endpoint: str, 
                service_bus_queue_name: str, 
                token_owner_accounts: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.digitalassets.models.ZkpRollupUpdate(_Model):
        identity: Optional[ZkpRollupIdentityUpdate]
        properties: Optional[ZkpRollupPatchProperties]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ZkpRollupIdentityUpdate] = ..., 
                properties: Optional[ZkpRollupPatchProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


namespace azure.mgmt.digitalassets.operations

    class azure.mgmt.digitalassets.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


    class azure.mgmt.digitalassets.operations.PartitionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                zkp_rollup_name: str, 
                partition_name: str, 
                resource: Partition, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Partition]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                zkp_rollup_name: str, 
                partition_name: str, 
                resource: Partition, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Partition]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                zkp_rollup_name: str, 
                partition_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Partition]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                zkp_rollup_name: str, 
                partition_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                zkp_rollup_name: str, 
                partition_name: str, 
                **kwargs: Any
            ) -> Partition: ...

        @distributed_trace
        def list_by_parent(
                self, 
                resource_group_name: str, 
                zkp_rollup_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Partition]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                zkp_rollup_name: str, 
                partition_name: str, 
                properties: PartitionTagsUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Partition: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                zkp_rollup_name: str, 
                partition_name: str, 
                properties: PartitionTagsUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Partition: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                zkp_rollup_name: str, 
                partition_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Partition: ...


    class azure.mgmt.digitalassets.operations.ZkpRollupsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                zkp_rollup_name: str, 
                resource: ZkpRollup, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ZkpRollup]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                zkp_rollup_name: str, 
                resource: ZkpRollup, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ZkpRollup]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                zkp_rollup_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ZkpRollup]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                zkp_rollup_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                zkp_rollup_name: str, 
                properties: ZkpRollupUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ZkpRollup]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                zkp_rollup_name: str, 
                properties: ZkpRollupUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ZkpRollup]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                zkp_rollup_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ZkpRollup]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                zkp_rollup_name: str, 
                **kwargs: Any
            ) -> ZkpRollup: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ZkpRollup]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[ZkpRollup]: ...


namespace azure.mgmt.digitalassets.types

    class azure.mgmt.digitalassets.types.ManagedServiceIdentity(TypedDict, total=False):
        key "principalId": str
        key "tenantId": str
        key "type": Required[Union[str, ManagedServiceIdentityType]]
        principalId: str
        tenantId: str
        type: Union[str, ManagedServiceIdentityType]
        userAssignedIdentities: dict[str, UserAssignedIdentity]


    class azure.mgmt.digitalassets.types.OperationalStatus(TypedDict, total=False):
        key "evaluatedAt": Required[str]
        key "status": Required[str]
        key "validUntil": Required[str]
        evaluatedAt: str
        status: str
        validUntil: str


    class azure.mgmt.digitalassets.types.Partition(TrackedResource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('PartitionProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: PartitionProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.digitalassets.types.PartitionProperties(TypedDict, total=False):
        key "operationalStatus": ForwardRef('OperationalStatus', module='types')
        key "provisioningState": Union[str, ProvisioningState]
        operationalStatus: OperationalStatus
        provisioningState: Union[str, ProvisioningState]


    class azure.mgmt.digitalassets.types.PartitionTagsUpdate(TypedDict, total=False):
        tags: dict[str, str]


    class azure.mgmt.digitalassets.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        systemData: SystemData
        type: str


    class azure.mgmt.digitalassets.types.SystemData(TypedDict, total=False):
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


    class azure.mgmt.digitalassets.types.TrackedResource(Resource):
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


    class azure.mgmt.digitalassets.types.UserAssignedIdentity(TypedDict, total=False):
        key "clientId": str
        key "principalId": str
        clientId: str
        principalId: str


    class azure.mgmt.digitalassets.types.ZkpRollup(TrackedResource):
        key "id": str
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('ZkpRollupProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        identity: ManagedServiceIdentity
        location: str
        name: str
        properties: ZkpRollupProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.digitalassets.types.ZkpRollupIdentityUpdate(TypedDict, total=False):
        key "type": Union[str, ManagedServiceIdentityType]
        type: Union[str, ManagedServiceIdentityType]
        userAssignedIdentities: dict[str, UserAssignedIdentity]


    class azure.mgmt.digitalassets.types.ZkpRollupPatchProperties(TypedDict, total=False):
        key "bootNodeId": str
        key "bootNodeIp": str
        key "bootNodeP2pPort": int
        key "bootNodeRpcPort": int
        bootNodeId: str
        bootNodeIp: str
        bootNodeP2pPort: int
        bootNodeRpcPort: int
        tokenOwnerAccounts: list[str]


    class azure.mgmt.digitalassets.types.ZkpRollupProperties(TypedDict, total=False):
        key "blocksPerProof": int
        key "bootNodeId": Required[str]
        key "bootNodeIp": Required[str]
        key "bootNodeP2pPort": Required[int]
        key "bootNodeRpcPort": Required[int]
        key "customerVpnPublicIp": str
        key "keyVaultId": Required[str]
        key "keyVaultUserAssignedIdentityResourceId": Required[str]
        key "operationalStatus": ForwardRef('OperationalStatus', module='types')
        key "provisioningState": Union[str, ProvisioningState]
        key "serviceBusEndpoint": Required[str]
        key "serviceBusQueueName": Required[str]
        key "serviceVpnAddressSpace": str
        key "serviceVpnPublicIp": str
        key "tokenOwnerAccounts": Required[list[str]]
        blocksPerProof: int
        bootNodeId: str
        bootNodeIp: str
        bootNodeP2pPort: int
        bootNodeRpcPort: int
        customerOnPremAddressPrefixes: list[str]
        customerVpnPublicIp: str
        keyVaultId: str
        keyVaultUserAssignedIdentityResourceId: str
        operationalStatus: OperationalStatus
        provisioningState: Union[str, ProvisioningState]
        serviceBusEndpoint: str
        serviceBusQueueName: str
        serviceVpnAddressSpace: str
        serviceVpnPublicIp: str
        tokenOwnerAccounts: list[str]


    class azure.mgmt.digitalassets.types.ZkpRollupUpdate(TypedDict, total=False):
        key "identity": ForwardRef('ZkpRollupIdentityUpdate', module='types')
        key "properties": ForwardRef('ZkpRollupPatchProperties', module='types')
        identity: ZkpRollupIdentityUpdate
        properties: ZkpRollupPatchProperties
        tags: dict[str, str]


```