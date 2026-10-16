```py
namespace azure.mgmt.deviceregistrysoftwareupdate

    class azure.mgmt.deviceregistrysoftwareupdate.DeviceRegistrySoftwareUpdateMgmtClient: implements ContextManager 
        operations: Operations
        update_instances: UpdateInstancesOperations

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


namespace azure.mgmt.deviceregistrysoftwareupdate.aio

    class azure.mgmt.deviceregistrysoftwareupdate.aio.DeviceRegistrySoftwareUpdateMgmtClient: implements AsyncContextManager 
        operations: Operations
        update_instances: UpdateInstancesOperations

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


namespace azure.mgmt.deviceregistrysoftwareupdate.aio.operations

    class azure.mgmt.deviceregistrysoftwareupdate.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


    class azure.mgmt.deviceregistrysoftwareupdate.aio.operations.UpdateInstancesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                update_instance_name: str, 
                resource: UpdateInstance, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[UpdateInstance]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                update_instance_name: str, 
                resource: UpdateInstance, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[UpdateInstance]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                update_instance_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[UpdateInstance]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                update_instance_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                update_instance_name: str, 
                properties: UpdateInstanceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[UpdateInstance]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                update_instance_name: str, 
                properties: UpdateInstanceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[UpdateInstance]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                update_instance_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[UpdateInstance]: ...

        @overload
        async def check_name_availability(
                self, 
                body: CheckNameAvailabilityRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResult: ...

        @overload
        async def check_name_availability(
                self, 
                body: CheckNameAvailabilityRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResult: ...

        @overload
        async def check_name_availability(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResult: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                update_instance_name: str, 
                **kwargs: Any
            ) -> UpdateInstance: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[UpdateInstance]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[UpdateInstance]: ...


namespace azure.mgmt.deviceregistrysoftwareupdate.models

    class azure.mgmt.deviceregistrysoftwareupdate.models.AccountLinking(_Model):
        linking_state: Union[str, AccountLinkingState]
        namespace_resource_id: str

        @overload
        def __init__(
                self, 
                *, 
                linking_state: Union[str, AccountLinkingState], 
                namespace_resource_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistrysoftwareupdate.models.AccountLinkingState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        IN_PROGRESS = "InProgress"
        ORPHANED = "Orphaned"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.deviceregistrysoftwareupdate.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.deviceregistrysoftwareupdate.models.CheckNameAvailabilityReason(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALREADY_EXISTS = "AlreadyExists"
        INVALID = "Invalid"


    class azure.mgmt.deviceregistrysoftwareupdate.models.CheckNameAvailabilityRequest(_Model):
        name: Optional[str]
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistrysoftwareupdate.models.CheckNameAvailabilityResult(_Model):
        message: Optional[str]
        name_available: Optional[bool]
        reason: Optional[Union[str, CheckNameAvailabilityReason]]

        @overload
        def __init__(
                self, 
                *, 
                message: Optional[str] = ..., 
                name_available: Optional[bool] = ..., 
                reason: Optional[Union[str, CheckNameAvailabilityReason]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistrysoftwareupdate.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.deviceregistrysoftwareupdate.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.deviceregistrysoftwareupdate.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.deviceregistrysoftwareupdate.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistrysoftwareupdate.models.ManagedServiceIdentity(_Model):
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


    class azure.mgmt.deviceregistrysoftwareupdate.models.ManagedServiceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        SYSTEM_ASSIGNED_USER_ASSIGNED = "SystemAssigned,UserAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.deviceregistrysoftwareupdate.models.Operation(_Model):
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


    class azure.mgmt.deviceregistrysoftwareupdate.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.deviceregistrysoftwareupdate.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.deviceregistrysoftwareupdate.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.deviceregistrysoftwareupdate.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.deviceregistrysoftwareupdate.models.SystemData(_Model):
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


    class azure.mgmt.deviceregistrysoftwareupdate.models.TrackedResource(Resource):
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


    class azure.mgmt.deviceregistrysoftwareupdate.models.UpdateInstance(TrackedResource):
        id: str
        identity: Optional[ManagedServiceIdentity]
        location: str
        name: str
        properties: Optional[UpdateInstanceProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                location: str, 
                properties: Optional[UpdateInstanceProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistrysoftwareupdate.models.UpdateInstanceProperties(_Model):
        linking: Optional[AccountLinking]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        service_address: Optional[str]


    class azure.mgmt.deviceregistrysoftwareupdate.models.UpdateInstanceUpdate(_Model):
        identity: Optional[ManagedServiceIdentity]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistrysoftwareupdate.models.UserAssignedIdentity(_Model):
        client_id: Optional[str]
        principal_id: Optional[str]


namespace azure.mgmt.deviceregistrysoftwareupdate.operations

    class azure.mgmt.deviceregistrysoftwareupdate.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


    class azure.mgmt.deviceregistrysoftwareupdate.operations.UpdateInstancesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                update_instance_name: str, 
                resource: UpdateInstance, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[UpdateInstance]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                update_instance_name: str, 
                resource: UpdateInstance, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[UpdateInstance]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                update_instance_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[UpdateInstance]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                update_instance_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                update_instance_name: str, 
                properties: UpdateInstanceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[UpdateInstance]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                update_instance_name: str, 
                properties: UpdateInstanceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[UpdateInstance]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                update_instance_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[UpdateInstance]: ...

        @overload
        def check_name_availability(
                self, 
                body: CheckNameAvailabilityRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResult: ...

        @overload
        def check_name_availability(
                self, 
                body: CheckNameAvailabilityRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResult: ...

        @overload
        def check_name_availability(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResult: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                update_instance_name: str, 
                **kwargs: Any
            ) -> UpdateInstance: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[UpdateInstance]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[UpdateInstance]: ...


namespace azure.mgmt.deviceregistrysoftwareupdate.types

    class azure.mgmt.deviceregistrysoftwareupdate.types.AccountLinking(TypedDict, total=False):
        key "linkingState": Required[Union[str, AccountLinkingState]]
        key "namespaceResourceId": Required[str]
        linkingState: Union[str, AccountLinkingState]
        namespaceResourceId: str


    class azure.mgmt.deviceregistrysoftwareupdate.types.CheckNameAvailabilityRequest(TypedDict, total=False):
        key "name": str
        key "type": str
        name: str
        type: str


    class azure.mgmt.deviceregistrysoftwareupdate.types.InboundCallerIdentity(TypedDict, total=False):
        key "type": Required[Union[str, ManagedServiceIdentityType]]
        key "userAssignedIdentity": str
        type: Union[str, ManagedServiceIdentityType]
        userAssignedIdentity: str


    class azure.mgmt.deviceregistrysoftwareupdate.types.LinkInitiateRequest(TypedDict, total=False):
        key "dataAddress": Required[str]
        key "inboundCallerIdentity": Required[InboundCallerIdentity]
        key "namespaceResourceId": Required[str]
        key "namespaceUuid": Required[str]
        dataAddress: str
        inboundCallerIdentity: InboundCallerIdentity
        namespaceResourceId: str
        namespaceUuid: str


    class azure.mgmt.deviceregistrysoftwareupdate.types.LinkNotifyRequest(TypedDict, total=False):
        key "action": Required[Union[str, LinkNotifyAction]]
        key "errorCode": str
        key "reason": str
        action: Union[str, LinkNotifyAction]
        errorCode: str
        reason: str


    class azure.mgmt.deviceregistrysoftwareupdate.types.LinkPreflightRequest(TypedDict, total=False):
        key "inboundCallerIdentity": Required[InboundCallerIdentity]
        key "namespaceResourceId": Required[str]
        key "namespaceUuid": Required[str]
        inboundCallerIdentity: InboundCallerIdentity
        namespaceResourceId: str
        namespaceUuid: str


    class azure.mgmt.deviceregistrysoftwareupdate.types.LinkUpdateRequest(TypedDict, total=False):
        key "dataAddress": str
        key "inboundCallerIdentity": ForwardRef('InboundCallerIdentity', module='types')
        key "namespaceResourceId": str
        key "namespaceUuid": str
        dataAddress: str
        inboundCallerIdentity: InboundCallerIdentity
        namespaceResourceId: str
        namespaceUuid: str


    class azure.mgmt.deviceregistrysoftwareupdate.types.ManagedServiceIdentity(TypedDict, total=False):
        key "principalId": str
        key "tenantId": str
        key "type": Required[Union[str, ManagedServiceIdentityType]]
        principalId: str
        tenantId: str
        type: Union[str, ManagedServiceIdentityType]
        userAssignedIdentities: dict[str, UserAssignedIdentity]


    class azure.mgmt.deviceregistrysoftwareupdate.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        systemData: SystemData
        type: str


    class azure.mgmt.deviceregistrysoftwareupdate.types.SystemData(TypedDict, total=False):
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


    class azure.mgmt.deviceregistrysoftwareupdate.types.TrackedResource(Resource):
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


    class azure.mgmt.deviceregistrysoftwareupdate.types.UpdateInstance(TrackedResource):
        key "id": str
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('UpdateInstanceProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        identity: ManagedServiceIdentity
        location: str
        name: str
        properties: UpdateInstanceProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.deviceregistrysoftwareupdate.types.UpdateInstanceProperties(TypedDict, total=False):
        key "linking": ForwardRef('AccountLinking', module='types')
        key "provisioningState": Union[str, ProvisioningState]
        key "serviceAddress": str
        linking: AccountLinking
        provisioningState: Union[str, ProvisioningState]
        serviceAddress: str


    class azure.mgmt.deviceregistrysoftwareupdate.types.UpdateInstanceUpdate(TypedDict, total=False):
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        identity: ManagedServiceIdentity
        tags: dict[str, str]


    class azure.mgmt.deviceregistrysoftwareupdate.types.UserAssignedIdentity(TypedDict, total=False):
        key "clientId": str
        key "principalId": str
        clientId: str
        principalId: str


```