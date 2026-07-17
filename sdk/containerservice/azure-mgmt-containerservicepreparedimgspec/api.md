```py
namespace azure.mgmt.containerservicepreparedimgspec

    class azure.mgmt.containerservicepreparedimgspec.ContainerServiceClient: implements ContextManager 
        operations: Operations
        prepared_image_specifications: PreparedImageSpecificationsOperations

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


namespace azure.mgmt.containerservicepreparedimgspec.aio

    class azure.mgmt.containerservicepreparedimgspec.aio.ContainerServiceClient: implements AsyncContextManager 
        operations: Operations
        prepared_image_specifications: PreparedImageSpecificationsOperations

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


namespace azure.mgmt.containerservicepreparedimgspec.aio.operations

    class azure.mgmt.containerservicepreparedimgspec.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


    class azure.mgmt.containerservicepreparedimgspec.aio.operations.PreparedImageSpecificationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                prepared_image_specification_name: str, 
                resource: PreparedImageSpecification, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[PreparedImageSpecification]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                prepared_image_specification_name: str, 
                resource: PreparedImageSpecification, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[PreparedImageSpecification]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                prepared_image_specification_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[PreparedImageSpecification]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                prepared_image_specification_name: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_delete_version(
                self, 
                resource_group_name: str, 
                prepared_image_specification_name: str, 
                version: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                prepared_image_specification_name: str, 
                **kwargs: Any
            ) -> PreparedImageSpecification: ...

        @distributed_trace_async
        async def get_version(
                self, 
                resource_group_name: str, 
                prepared_image_specification_name: str, 
                version: str, 
                **kwargs: Any
            ) -> PreparedImageSpecificationVersion: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[PreparedImageSpecification]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[PreparedImageSpecification]: ...

        @distributed_trace
        def list_versions(
                self, 
                resource_group_name: str, 
                prepared_image_specification_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[PreparedImageSpecificationVersion]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                prepared_image_specification_name: str, 
                properties: PreparedImageSpecificationPatch, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> PreparedImageSpecification: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                prepared_image_specification_name: str, 
                properties: PreparedImageSpecificationPatch, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> PreparedImageSpecification: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                prepared_image_specification_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> PreparedImageSpecification: ...


namespace azure.mgmt.containerservicepreparedimgspec.models

    class azure.mgmt.containerservicepreparedimgspec.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.containerservicepreparedimgspec.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.containerservicepreparedimgspec.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.containerservicepreparedimgspec.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.containerservicepreparedimgspec.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservicepreparedimgspec.models.ExecutionPoint(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NODE_IMAGE_BUILD_TIME = "NodeImageBuildTime"
        NODE_PROVISION_TIME = "NodeProvisionTime"


    class azure.mgmt.containerservicepreparedimgspec.models.Operation(_Model):
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


    class azure.mgmt.containerservicepreparedimgspec.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.containerservicepreparedimgspec.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.containerservicepreparedimgspec.models.PostScriptAction(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        REBOOT_AFTER = "RebootAfter"


    class azure.mgmt.containerservicepreparedimgspec.models.PreparedImageSpecification(TrackedResource):
        e_tag: Optional[str]
        id: str
        location: str
        name: str
        properties: Optional[PreparedImageSpecificationProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[PreparedImageSpecificationProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservicepreparedimgspec.models.PreparedImageSpecificationManagedIdentityProfile(_Model):
        client_id: Optional[str]
        object_id: Optional[str]
        resource_id: str

        @overload
        def __init__(
                self, 
                *, 
                resource_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservicepreparedimgspec.models.PreparedImageSpecificationPatch(_Model):
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservicepreparedimgspec.models.PreparedImageSpecificationProperties(_Model):
        container_images: Optional[list[str]]
        customization_scripts: Optional[list[PreparedImageSpecificationScript]]
        identity_profile: Optional[PreparedImageSpecificationManagedIdentityProfile]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                container_images: Optional[list[str]] = ..., 
                customization_scripts: Optional[list[PreparedImageSpecificationScript]] = ..., 
                identity_profile: Optional[PreparedImageSpecificationManagedIdentityProfile] = ..., 
                version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservicepreparedimgspec.models.PreparedImageSpecificationScript(_Model):
        execution_point: Union[str, ExecutionPoint]
        name: str
        post_script_action: Optional[Union[str, PostScriptAction]]
        script: Optional[str]
        script_type: Union[str, ScriptType]

        @overload
        def __init__(
                self, 
                *, 
                execution_point: Union[str, ExecutionPoint], 
                name: str, 
                post_script_action: Optional[Union[str, PostScriptAction]] = ..., 
                script: Optional[str] = ..., 
                script_type: Union[str, ScriptType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservicepreparedimgspec.models.PreparedImageSpecificationVersion(ProxyResource):
        id: str
        name: str
        properties: Optional[PreparedImageSpecificationProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[PreparedImageSpecificationProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservicepreparedimgspec.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CANCELED = "Canceled"
        DELETING = "Deleting"
        FAILED = "Failed"
        PROVISIONING = "Provisioning"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.containerservicepreparedimgspec.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.containerservicepreparedimgspec.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.containerservicepreparedimgspec.models.ScriptType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BASH = "Bash"
        POWER_SHELL = "PowerShell"


    class azure.mgmt.containerservicepreparedimgspec.models.SystemData(_Model):
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


    class azure.mgmt.containerservicepreparedimgspec.models.TrackedResource(Resource):
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


namespace azure.mgmt.containerservicepreparedimgspec.operations

    class azure.mgmt.containerservicepreparedimgspec.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


    class azure.mgmt.containerservicepreparedimgspec.operations.PreparedImageSpecificationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                prepared_image_specification_name: str, 
                resource: PreparedImageSpecification, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[PreparedImageSpecification]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                prepared_image_specification_name: str, 
                resource: PreparedImageSpecification, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[PreparedImageSpecification]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                prepared_image_specification_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[PreparedImageSpecification]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                prepared_image_specification_name: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_delete_version(
                self, 
                resource_group_name: str, 
                prepared_image_specification_name: str, 
                version: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                prepared_image_specification_name: str, 
                **kwargs: Any
            ) -> PreparedImageSpecification: ...

        @distributed_trace
        def get_version(
                self, 
                resource_group_name: str, 
                prepared_image_specification_name: str, 
                version: str, 
                **kwargs: Any
            ) -> PreparedImageSpecificationVersion: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[PreparedImageSpecification]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[PreparedImageSpecification]: ...

        @distributed_trace
        def list_versions(
                self, 
                resource_group_name: str, 
                prepared_image_specification_name: str, 
                **kwargs: Any
            ) -> ItemPaged[PreparedImageSpecificationVersion]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                prepared_image_specification_name: str, 
                properties: PreparedImageSpecificationPatch, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> PreparedImageSpecification: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                prepared_image_specification_name: str, 
                properties: PreparedImageSpecificationPatch, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> PreparedImageSpecification: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                prepared_image_specification_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> PreparedImageSpecification: ...


namespace azure.mgmt.containerservicepreparedimgspec.types

    class azure.mgmt.containerservicepreparedimgspec.types.PreparedImageSpecification(TrackedResource):
        key "eTag": str
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('PreparedImageSpecificationProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        e_tag: str
        id: str
        location: str
        name: str
        properties: PreparedImageSpecificationProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.containerservicepreparedimgspec.types.PreparedImageSpecificationManagedIdentityProfile(TypedDict, total=False):
        key "clientId": str
        key "objectId": str
        key "resourceId": Required[str]
        client_id: str
        object_id: str
        resource_id: str


    class azure.mgmt.containerservicepreparedimgspec.types.PreparedImageSpecificationPatch(TypedDict, total=False):
        tags: dict[str, str]


    class azure.mgmt.containerservicepreparedimgspec.types.PreparedImageSpecificationProperties(TypedDict, total=False):
        key "identityProfile": ForwardRef('PreparedImageSpecificationManagedIdentityProfile', module='types')
        key "provisioningState": Union[str, ProvisioningState]
        key "version": str
        containerImages: list[str]
        container_images: list[str]
        customizationScripts: list[PreparedImageSpecificationScript]
        customization_scripts: list[PreparedImageSpecificationScript]
        identity_profile: PreparedImageSpecificationManagedIdentityProfile
        provisioning_state: Union[str, ProvisioningState]
        version: str


    class azure.mgmt.containerservicepreparedimgspec.types.PreparedImageSpecificationScript(TypedDict, total=False):
        key "executionPoint": Required[Union[str, ExecutionPoint]]
        key "name": Required[str]
        key "postScriptAction": Union[str, PostScriptAction]
        key "script": str
        key "scriptType": Required[Union[str, ScriptType]]
        execution_point: Union[str, ExecutionPoint]
        name: str
        post_script_action: Union[str, PostScriptAction]
        script: str
        script_type: Union[str, ScriptType]


    class azure.mgmt.containerservicepreparedimgspec.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.containerservicepreparedimgspec.types.SystemData(TypedDict, total=False):
        key "createdAt": str
        key "createdBy": str
        key "createdByType": Union[str, CreatedByType]
        key "lastModifiedAt": str
        key "lastModifiedBy": str
        key "lastModifiedByType": Union[str, CreatedByType]
        created_at: str
        created_by: str
        created_by_type: Union[str, CreatedByType]
        last_modified_at: str
        last_modified_by: str
        last_modified_by_type: Union[str, CreatedByType]


    class azure.mgmt.containerservicepreparedimgspec.types.TrackedResource(Resource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        system_data: SystemData
        tags: dict[str, str]
        type: str


```