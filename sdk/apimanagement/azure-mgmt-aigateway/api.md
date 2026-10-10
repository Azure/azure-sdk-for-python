```py
namespace azure.mgmt.aigateway

    class azure.mgmt.aigateway.ApiManagementClient: implements ContextManager 
        ai_gateway_resources: AiGatewayResourcesOperations
        operations: Operations

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


namespace azure.mgmt.aigateway.aio

    class azure.mgmt.aigateway.aio.ApiManagementClient: implements AsyncContextManager 
        ai_gateway_resources: AiGatewayResourcesOperations
        operations: Operations

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


namespace azure.mgmt.aigateway.aio.operations

    class azure.mgmt.aigateway.aio.operations.AiGatewayResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                resource: AiGatewayResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AiGatewayResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                resource: AiGatewayResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AiGatewayResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AiGatewayResource]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                *, 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                properties: AiGatewayUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> AsyncLROPoller[AiGatewayResource]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                properties: AiGatewayUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> AsyncLROPoller[AiGatewayResource]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> AsyncLROPoller[AiGatewayResource]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                **kwargs: Any
            ) -> AiGatewayResource: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[AiGatewayResource]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[AiGatewayResource]: ...


    class azure.mgmt.aigateway.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


namespace azure.mgmt.aigateway.models

    class azure.mgmt.aigateway.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.aigateway.models.AiGatewayBackend(_Model):
        subnet: Optional[AiGatewaySubnet]

        @overload
        def __init__(
                self, 
                *, 
                subnet: Optional[AiGatewaySubnet] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewayFrontend(_Model):
        default_hostname: Optional[str]


    class azure.mgmt.aigateway.models.AiGatewayProperties(_Model):
        backend: Optional[AiGatewayBackend]
        frontend: Optional[AiGatewayFrontend]
        provisioning_state: Optional[Union[str, AiGatewayProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                backend: Optional[AiGatewayBackend] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewayProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.aigateway.models.AiGatewayResource(TrackedResource):
        e_tag: Optional[str]
        id: str
        identity: Optional[ManagedServiceIdentity]
        location: str
        name: str
        properties: AiGatewayProperties
        sku: Optional[Sku]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                location: str, 
                properties: AiGatewayProperties, 
                sku: Optional[Sku] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewaySkuUpdate(_Model):
        capacity: Optional[int]
        family: Optional[str]
        name: Optional[str]
        size: Optional[str]
        tier: Optional[Union[str, SkuTier]]

        @overload
        def __init__(
                self, 
                *, 
                capacity: Optional[int] = ..., 
                family: Optional[str] = ..., 
                name: Optional[str] = ..., 
                size: Optional[str] = ..., 
                tier: Optional[Union[str, SkuTier]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewaySubnet(_Model):
        id: str

        @overload
        def __init__(
                self, 
                *, 
                id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewayUpdateParameters(_Model):
        identity: Optional[ManagedServiceIdentity]
        sku: Optional[AiGatewaySkuUpdate]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                sku: Optional[AiGatewaySkuUpdate] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.aigateway.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.aigateway.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.aigateway.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.ManagedServiceIdentity(_Model):
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


    class azure.mgmt.aigateway.models.ManagedServiceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        SYSTEM_ASSIGNED_USER_ASSIGNED = "SystemAssigned,UserAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.aigateway.models.Operation(_Model):
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


    class azure.mgmt.aigateway.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.aigateway.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.aigateway.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.aigateway.models.Sku(_Model):
        capacity: Optional[int]
        family: Optional[str]
        name: str
        size: Optional[str]
        tier: Optional[Union[str, SkuTier]]

        @overload
        def __init__(
                self, 
                *, 
                capacity: Optional[int] = ..., 
                family: Optional[str] = ..., 
                name: str, 
                size: Optional[str] = ..., 
                tier: Optional[Union[str, SkuTier]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.SkuTier(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BASIC = "Basic"
        FREE = "Free"
        PREMIUM = "Premium"
        STANDARD = "Standard"


    class azure.mgmt.aigateway.models.SystemData(_Model):
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


    class azure.mgmt.aigateway.models.TrackedResource(Resource):
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


    class azure.mgmt.aigateway.models.UserAssignedIdentity(_Model):
        client_id: Optional[str]
        principal_id: Optional[str]


namespace azure.mgmt.aigateway.operations

    class azure.mgmt.aigateway.operations.AiGatewayResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                resource: AiGatewayResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AiGatewayResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                resource: AiGatewayResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AiGatewayResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AiGatewayResource]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                *, 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                properties: AiGatewayUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> LROPoller[AiGatewayResource]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                properties: AiGatewayUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> LROPoller[AiGatewayResource]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> LROPoller[AiGatewayResource]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                **kwargs: Any
            ) -> AiGatewayResource: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[AiGatewayResource]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[AiGatewayResource]: ...


    class azure.mgmt.aigateway.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


namespace azure.mgmt.aigateway.types

    class azure.mgmt.aigateway.types.AiGatewayBackend(TypedDict, total=False):
        key "subnet": ForwardRef('AiGatewaySubnet', module='types')
        subnet: AiGatewaySubnet


    class azure.mgmt.aigateway.types.AiGatewayFrontend(TypedDict, total=False):
        key "defaultHostname": str
        defaultHostname: str


    class azure.mgmt.aigateway.types.AiGatewayProperties(TypedDict, total=False):
        key "backend": ForwardRef('AiGatewayBackend', module='types')
        key "frontend": ForwardRef('AiGatewayFrontend', module='types')
        key "provisioningState": Union[str, AiGatewayProvisioningState]
        backend: AiGatewayBackend
        frontend: AiGatewayFrontend
        provisioningState: Union[str, AiGatewayProvisioningState]


    class azure.mgmt.aigateway.types.AiGatewayResource(TrackedResource):
        key "eTag": str
        key "id": str
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "location": Required[str]
        key "name": str
        key "properties": Required[AiGatewayProperties]
        key "sku": ForwardRef('Sku', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        eTag: str
        id: str
        identity: ManagedServiceIdentity
        location: str
        name: str
        properties: AiGatewayProperties
        sku: Sku
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.aigateway.types.AiGatewaySkuUpdate(TypedDict, total=False):
        key "capacity": int
        key "family": str
        key "name": str
        key "size": str
        key "tier": Union[str, SkuTier]
        capacity: int
        family: str
        name: str
        size: str
        tier: Union[str, SkuTier]


    class azure.mgmt.aigateway.types.AiGatewaySubnet(TypedDict, total=False):
        key "id": Required[str]
        id: str


    class azure.mgmt.aigateway.types.AiGatewayUpdateParameters(TypedDict, total=False):
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "sku": ForwardRef('AiGatewaySkuUpdate', module='types')
        identity: ManagedServiceIdentity
        sku: AiGatewaySkuUpdate
        tags: dict[str, str]


    class azure.mgmt.aigateway.types.ManagedServiceIdentity(TypedDict, total=False):
        key "principalId": str
        key "tenantId": str
        key "type": Required[Union[str, ManagedServiceIdentityType]]
        principalId: str
        tenantId: str
        type: Union[str, ManagedServiceIdentityType]
        userAssignedIdentities: dict[str, UserAssignedIdentity]


    class azure.mgmt.aigateway.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        systemData: SystemData
        type: str


    class azure.mgmt.aigateway.types.Sku(TypedDict, total=False):
        key "capacity": int
        key "family": str
        key "name": Required[str]
        key "size": str
        key "tier": Union[str, SkuTier]
        capacity: int
        family: str
        name: str
        size: str
        tier: Union[str, SkuTier]


    class azure.mgmt.aigateway.types.SystemData(TypedDict, total=False):
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


    class azure.mgmt.aigateway.types.TrackedResource(Resource):
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


    class azure.mgmt.aigateway.types.UserAssignedIdentity(TypedDict, total=False):
        key "clientId": str
        key "principalId": str
        clientId: str
        principalId: str


```