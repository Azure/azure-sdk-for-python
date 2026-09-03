```py
namespace azure.mgmt.monitoragents

    class azure.mgmt.monitoragents.MonitorClient: implements ContextManager 
        observability_agents: ObservabilityAgentsOperations
        operations: Operations

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


namespace azure.mgmt.monitoragents.aio

    class azure.mgmt.monitoragents.aio.MonitorClient: implements AsyncContextManager 
        observability_agents: ObservabilityAgentsOperations
        operations: Operations

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


namespace azure.mgmt.monitoragents.aio.operations

    class azure.mgmt.monitoragents.aio.operations.ObservabilityAgentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                observability_agent_name: str, 
                resource: ObservabilityAgentResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ObservabilityAgentResource: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                observability_agent_name: str, 
                resource: ObservabilityAgentResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ObservabilityAgentResource: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                observability_agent_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ObservabilityAgentResource: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                observability_agent_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                observability_agent_name: str, 
                **kwargs: Any
            ) -> ObservabilityAgentResource: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ObservabilityAgentResource]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[ObservabilityAgentResource]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                observability_agent_name: str, 
                properties: ObservabilityAgentPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ObservabilityAgentResource: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                observability_agent_name: str, 
                properties: ObservabilityAgentPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ObservabilityAgentResource: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                observability_agent_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ObservabilityAgentResource: ...


    class azure.mgmt.monitoragents.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


namespace azure.mgmt.monitoragents.models

    class azure.mgmt.monitoragents.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.monitoragents.models.ArmOrigin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.monitoragents.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.monitoragents.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.monitoragents.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.monitoragents.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitoragents.models.ManagedServiceIdentity(_Model):
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


    class azure.mgmt.monitoragents.models.ManagedServiceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        SYSTEM_ASSIGNED_USER_ASSIGNED = "SystemAssigned,UserAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.monitoragents.models.ObservabilityAgentPatch(_Model):
        identity: Optional[ManagedServiceIdentity]
        properties: Optional[ObservabilityAgentPropertiesUpdate]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                properties: Optional[ObservabilityAgentPropertiesUpdate] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitoragents.models.ObservabilityAgentProperties(_Model):
        enabled: Optional[bool]
        monitoring_account_id: str
        operations: Optional[list[OperationEntry]]
        provisioning_state: Optional[Union[str, ResourceProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ..., 
                monitoring_account_id: str, 
                operations: Optional[list[OperationEntry]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitoragents.models.ObservabilityAgentPropertiesUpdate(_Model):
        enabled: Optional[bool]
        monitoring_account_id: Optional[str]
        operations: Optional[list[OperationEntry]]

        @overload
        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ..., 
                monitoring_account_id: Optional[str] = ..., 
                operations: Optional[list[OperationEntry]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitoragents.models.ObservabilityAgentResource(TrackedResource):
        id: str
        identity: Optional[ManagedServiceIdentity]
        location: str
        name: str
        properties: Optional[ObservabilityAgentProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                location: str, 
                properties: Optional[ObservabilityAgentProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitoragents.models.Operation(_Model):
        action_type: Optional[Union[str, ActionType]]
        display: Optional[OperationDisplay]
        is_data_action: Optional[bool]
        name: Optional[str]
        origin: Optional[Union[str, ArmOrigin]]

        @overload
        def __init__(
                self, 
                *, 
                display: Optional[OperationDisplay] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitoragents.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.monitoragents.models.OperationEntry(_Model):
        instructions: Optional[str]
        mode: Optional[Union[str, OperationMode]]
        type: Union[str, OperationType]

        @overload
        def __init__(
                self, 
                *, 
                instructions: Optional[str] = ..., 
                mode: Optional[Union[str, OperationMode]] = ..., 
                type: Union[str, OperationType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitoragents.models.OperationMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTO = "Auto"
        MANUAL = "Manual"


    class azure.mgmt.monitoragents.models.OperationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INVESTIGATION = "Investigation"
        ISSUE_CREATION = "IssueCreation"


    class azure.mgmt.monitoragents.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.monitoragents.models.ResourceProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.monitoragents.models.SystemData(_Model):
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


    class azure.mgmt.monitoragents.models.TrackedResource(Resource):
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


    class azure.mgmt.monitoragents.models.UserAssignedIdentity(_Model):
        client_id: Optional[str]
        principal_id: Optional[str]


namespace azure.mgmt.monitoragents.operations

    class azure.mgmt.monitoragents.operations.ObservabilityAgentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                observability_agent_name: str, 
                resource: ObservabilityAgentResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ObservabilityAgentResource: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                observability_agent_name: str, 
                resource: ObservabilityAgentResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ObservabilityAgentResource: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                observability_agent_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ObservabilityAgentResource: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                observability_agent_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                observability_agent_name: str, 
                **kwargs: Any
            ) -> ObservabilityAgentResource: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ObservabilityAgentResource]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[ObservabilityAgentResource]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                observability_agent_name: str, 
                properties: ObservabilityAgentPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ObservabilityAgentResource: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                observability_agent_name: str, 
                properties: ObservabilityAgentPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ObservabilityAgentResource: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                observability_agent_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ObservabilityAgentResource: ...


    class azure.mgmt.monitoragents.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


namespace azure.mgmt.monitoragents.types

    class azure.mgmt.monitoragents.types.ManagedServiceIdentity(TypedDict, total=False):
        key "principalId": str
        key "tenantId": str
        key "type": Required[Union[str, ManagedServiceIdentityType]]
        principalId: str
        tenantId: str
        type: Union[str, ManagedServiceIdentityType]
        userAssignedIdentities: dict[str, UserAssignedIdentity]


    class azure.mgmt.monitoragents.types.ObservabilityAgentPatch(TypedDict, total=False):
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "properties": ForwardRef('ObservabilityAgentPropertiesUpdate', module='types')
        identity: ManagedServiceIdentity
        properties: ObservabilityAgentPropertiesUpdate
        tags: dict[str, str]


    class azure.mgmt.monitoragents.types.ObservabilityAgentProperties(TypedDict, total=False):
        key "enabled": bool
        key "monitoringAccountId": Required[str]
        key "provisioningState": Union[str, ResourceProvisioningState]
        enabled: bool
        monitoringAccountId: str
        operations: list[OperationEntry]
        provisioningState: Union[str, ResourceProvisioningState]


    class azure.mgmt.monitoragents.types.ObservabilityAgentPropertiesUpdate(TypedDict, total=False):
        key "enabled": bool
        key "monitoringAccountId": str
        enabled: bool
        monitoringAccountId: str
        operations: list[OperationEntry]


    class azure.mgmt.monitoragents.types.ObservabilityAgentResource(TrackedResource):
        key "id": str
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('ObservabilityAgentProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        identity: ManagedServiceIdentity
        location: str
        name: str
        properties: ObservabilityAgentProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.monitoragents.types.OperationEntry(TypedDict, total=False):
        key "instructions": str
        key "mode": Union[str, OperationMode]
        key "type": Required[Union[str, OperationType]]
        instructions: str
        mode: Union[str, OperationMode]
        type: Union[str, OperationType]


    class azure.mgmt.monitoragents.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        systemData: SystemData
        type: str


    class azure.mgmt.monitoragents.types.SystemData(TypedDict, total=False):
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


    class azure.mgmt.monitoragents.types.TrackedResource(Resource):
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


    class azure.mgmt.monitoragents.types.UserAssignedIdentity(TypedDict, total=False):
        key "clientId": str
        key "principalId": str
        clientId: str
        principalId: str


```