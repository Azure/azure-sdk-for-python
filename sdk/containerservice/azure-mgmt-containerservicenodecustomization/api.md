```py
namespace azure.mgmt.containerservicenodecustomization

    class azure.mgmt.containerservicenodecustomization.ContainerServiceClient: implements ContextManager 
        node_customizations: NodeCustomizationsOperations
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


namespace azure.mgmt.containerservicenodecustomization.aio

    class azure.mgmt.containerservicenodecustomization.aio.ContainerServiceClient: implements AsyncContextManager 
        node_customizations: NodeCustomizationsOperations
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


namespace azure.mgmt.containerservicenodecustomization.aio.operations

    class azure.mgmt.containerservicenodecustomization.aio.operations.NodeCustomizationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                node_customization_name: str, 
                resource: NodeCustomization, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[NodeCustomization]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                node_customization_name: str, 
                resource: NodeCustomization, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[NodeCustomization]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                node_customization_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[NodeCustomization]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                node_customization_name: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_delete_version(
                self, 
                resource_group_name: str, 
                node_customization_name: str, 
                version: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                node_customization_name: str, 
                properties: NodeCustomizationUpdate, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[NodeCustomization]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                node_customization_name: str, 
                properties: NodeCustomizationUpdate, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[NodeCustomization]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                node_customization_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[NodeCustomization]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                node_customization_name: str, 
                **kwargs: Any
            ) -> NodeCustomization: ...

        @distributed_trace_async
        async def get_version(
                self, 
                resource_group_name: str, 
                node_customization_name: str, 
                version: str, 
                **kwargs: Any
            ) -> NodeCustomizationVersion: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[NodeCustomization]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[NodeCustomization]: ...

        @distributed_trace
        def list_versions(
                self, 
                resource_group_name: str, 
                node_customization_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[NodeCustomizationVersion]: ...


    class azure.mgmt.containerservicenodecustomization.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


namespace azure.mgmt.containerservicenodecustomization.models

    class azure.mgmt.containerservicenodecustomization.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.containerservicenodecustomization.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.containerservicenodecustomization.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.containerservicenodecustomization.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.containerservicenodecustomization.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservicenodecustomization.models.ExecutionPoint(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NODE_IMAGE_BUILD_TIME = "NodeImageBuildTime"
        NODE_PROVISION_TIME = "NodeProvisionTime"


    class azure.mgmt.containerservicenodecustomization.models.NodeCustomization(TrackedResource):
        e_tag: Optional[str]
        id: str
        location: str
        name: str
        properties: Optional[NodeCustomizationProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[NodeCustomizationProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservicenodecustomization.models.NodeCustomizationProperties(_Model):
        container_images: Optional[list[str]]
        customization_scripts: Optional[list[NodeCustomizationScript]]
        identity_profile: Optional[UserAssignedIdentity]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                container_images: Optional[list[str]] = ..., 
                customization_scripts: Optional[list[NodeCustomizationScript]] = ..., 
                identity_profile: Optional[UserAssignedIdentity] = ..., 
                version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservicenodecustomization.models.NodeCustomizationScript(_Model):
        execution_point: Union[str, ExecutionPoint]
        name: str
        reboot_after: Optional[bool]
        script: Optional[str]
        script_type: Union[str, ScriptType]

        @overload
        def __init__(
                self, 
                *, 
                execution_point: Union[str, ExecutionPoint], 
                name: str, 
                reboot_after: Optional[bool] = ..., 
                script: Optional[str] = ..., 
                script_type: Union[str, ScriptType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservicenodecustomization.models.NodeCustomizationUpdate(_Model):
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservicenodecustomization.models.NodeCustomizationVersion(ProxyResource):
        id: str
        name: str
        properties: Optional[NodeCustomizationProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[NodeCustomizationProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservicenodecustomization.models.Operation(_Model):
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


    class azure.mgmt.containerservicenodecustomization.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.containerservicenodecustomization.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.containerservicenodecustomization.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CANCELED = "Canceled"
        DELETING = "Deleting"
        FAILED = "Failed"
        PROVISIONING = "Provisioning"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.containerservicenodecustomization.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.containerservicenodecustomization.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.containerservicenodecustomization.models.ScriptType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BASH = "Bash"
        POWER_SHELL = "PowerShell"


    class azure.mgmt.containerservicenodecustomization.models.SystemData(_Model):
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


    class azure.mgmt.containerservicenodecustomization.models.TrackedResource(Resource):
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


    class azure.mgmt.containerservicenodecustomization.models.UserAssignedIdentity(_Model):
        client_id: Optional[str]
        principal_id: Optional[str]


namespace azure.mgmt.containerservicenodecustomization.operations

    class azure.mgmt.containerservicenodecustomization.operations.NodeCustomizationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                node_customization_name: str, 
                resource: NodeCustomization, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[NodeCustomization]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                node_customization_name: str, 
                resource: NodeCustomization, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[NodeCustomization]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                node_customization_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[NodeCustomization]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                node_customization_name: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_delete_version(
                self, 
                resource_group_name: str, 
                node_customization_name: str, 
                version: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                node_customization_name: str, 
                properties: NodeCustomizationUpdate, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[NodeCustomization]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                node_customization_name: str, 
                properties: NodeCustomizationUpdate, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[NodeCustomization]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                node_customization_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[NodeCustomization]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                node_customization_name: str, 
                **kwargs: Any
            ) -> NodeCustomization: ...

        @distributed_trace
        def get_version(
                self, 
                resource_group_name: str, 
                node_customization_name: str, 
                version: str, 
                **kwargs: Any
            ) -> NodeCustomizationVersion: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[NodeCustomization]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[NodeCustomization]: ...

        @distributed_trace
        def list_versions(
                self, 
                resource_group_name: str, 
                node_customization_name: str, 
                **kwargs: Any
            ) -> ItemPaged[NodeCustomizationVersion]: ...


    class azure.mgmt.containerservicenodecustomization.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


namespace azure.mgmt.containerservicenodecustomization.types

    class azure.mgmt.containerservicenodecustomization.types.NodeCustomization(TrackedResource):
        key "eTag": str
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('NodeCustomizationProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        eTag: str
        id: str
        location: str
        name: str
        properties: NodeCustomizationProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.containerservicenodecustomization.types.NodeCustomizationProperties(TypedDict, total=False):
        key "identityProfile": ForwardRef('UserAssignedIdentity', module='types')
        key "provisioningState": Union[str, ProvisioningState]
        key "version": str
        containerImages: list[str]
        customizationScripts: list[NodeCustomizationScript]
        identityProfile: UserAssignedIdentity
        provisioningState: Union[str, ProvisioningState]
        version: str


    class azure.mgmt.containerservicenodecustomization.types.NodeCustomizationScript(TypedDict, total=False):
        key "executionPoint": Required[Union[str, ExecutionPoint]]
        key "name": Required[str]
        key "rebootAfter": bool
        key "script": str
        key "scriptType": Required[Union[str, ScriptType]]
        executionPoint: Union[str, ExecutionPoint]
        name: str
        rebootAfter: bool
        script: str
        scriptType: Union[str, ScriptType]


    class azure.mgmt.containerservicenodecustomization.types.NodeCustomizationUpdate(TypedDict, total=False):
        tags: dict[str, str]


    class azure.mgmt.containerservicenodecustomization.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        systemData: SystemData
        type: str


    class azure.mgmt.containerservicenodecustomization.types.SystemData(TypedDict, total=False):
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


    class azure.mgmt.containerservicenodecustomization.types.TrackedResource(Resource):
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


    class azure.mgmt.containerservicenodecustomization.types.UserAssignedIdentity(TypedDict, total=False):
        key "clientId": str
        key "principalId": str
        clientId: str
        principalId: str


```