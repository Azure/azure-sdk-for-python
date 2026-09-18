```py
namespace azure.mgmt.resource.resources

    class azure.mgmt.resource.resources.ResourceManagementClient: implements ContextManager 
        operations: Operations
        provider_resource_types: ProviderResourceTypesOperations
        providers: ProvidersOperations
        resource_groups: ResourceGroupsOperations
        resources: ResourcesOperations
        tags: TagsOperations

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


namespace azure.mgmt.resource.resources.aio

    class azure.mgmt.resource.resources.aio.ResourceManagementClient: implements AsyncContextManager 
        operations: Operations
        provider_resource_types: ProviderResourceTypesOperations
        providers: ProvidersOperations
        resource_groups: ResourceGroupsOperations
        resources: ResourcesOperations
        tags: TagsOperations

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


namespace azure.mgmt.resource.resources.aio.operations

    class azure.mgmt.resource.resources.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


    class azure.mgmt.resource.resources.aio.operations.ProviderResourceTypesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def list(
                self, 
                resource_provider_namespace: str, 
                *, 
                expand: Optional[str] = ..., 
                **kwargs: Any
            ) -> ProviderResourceTypeListResult: ...


    class azure.mgmt.resource.resources.aio.operations.ProvidersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_provider_namespace: str, 
                *, 
                expand: Optional[str] = ..., 
                **kwargs: Any
            ) -> Provider: ...

        @distributed_trace_async
        async def get_at_tenant_scope(
                self, 
                resource_provider_namespace: str, 
                *, 
                expand: Optional[str] = ..., 
                **kwargs: Any
            ) -> Provider: ...

        @distributed_trace
        def list(
                self, 
                *, 
                expand: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Provider]: ...

        @distributed_trace
        def list_at_tenant_scope(
                self, 
                *, 
                expand: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Provider]: ...

        @distributed_trace_async
        async def provider_permissions(
                self, 
                resource_provider_namespace: str, 
                **kwargs: Any
            ) -> ProviderPermissionListResult: ...

        @overload
        async def register(
                self, 
                resource_provider_namespace: str, 
                properties: Optional[ProviderRegistrationRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Provider: ...

        @overload
        async def register(
                self, 
                resource_provider_namespace: str, 
                properties: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Provider: ...

        @overload
        async def register(
                self, 
                resource_provider_namespace: str, 
                properties: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Provider: ...

        @distributed_trace_async
        async def register_at_management_group_scope(
                self, 
                resource_provider_namespace: str, 
                group_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def unregister(
                self, 
                resource_provider_namespace: str, 
                **kwargs: Any
            ) -> Provider: ...


    class azure.mgmt.resource.resources.aio.operations.ResourceGroupsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                *, 
                force_deletion_types: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_export_template(
                self, 
                resource_group_name: str, 
                parameters: ExportTemplateRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ResourceGroupExportResult]: ...

        @overload
        async def begin_export_template(
                self, 
                resource_group_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ResourceGroupExportResult]: ...

        @overload
        async def begin_export_template(
                self, 
                resource_group_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ResourceGroupExportResult]: ...

        @distributed_trace_async
        async def check_existence(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> bool: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                parameters: ResourceGroup, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ResourceGroup: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ResourceGroup: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ResourceGroup: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ResourceGroup: ...

        @distributed_trace
        def list(
                self, 
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[ResourceGroup]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                parameters: ResourceGroupPatchable, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ResourceGroup: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ResourceGroup: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ResourceGroup: ...


    class azure.mgmt.resource.resources.aio.operations.ResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_provider_namespace: str, 
                parent_resource_path: str, 
                resource_type: str, 
                resource_name: str, 
                parameters: GenericResource, 
                *, 
                api_version: str, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GenericResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_provider_namespace: str, 
                parent_resource_path: str, 
                resource_type: str, 
                resource_name: str, 
                parameters: JSON, 
                *, 
                api_version: str, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GenericResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_provider_namespace: str, 
                parent_resource_path: str, 
                resource_type: str, 
                resource_name: str, 
                parameters: IO[bytes], 
                *, 
                api_version: str, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GenericResource]: ...

        @overload
        async def begin_create_or_update_by_id(
                self, 
                resource_id: str, 
                parameters: GenericResource, 
                *, 
                api_version: str, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GenericResource]: ...

        @overload
        async def begin_create_or_update_by_id(
                self, 
                resource_id: str, 
                parameters: JSON, 
                *, 
                api_version: str, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GenericResource]: ...

        @overload
        async def begin_create_or_update_by_id(
                self, 
                resource_id: str, 
                parameters: IO[bytes], 
                *, 
                api_version: str, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GenericResource]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                resource_provider_namespace: str, 
                parent_resource_path: str, 
                resource_type: str, 
                resource_name: str, 
                *, 
                api_version: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_delete_by_id(
                self, 
                resource_id: str, 
                *, 
                api_version: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_move_resources(
                self, 
                source_resource_group_name: str, 
                parameters: ResourcesMoveInfo, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_move_resources(
                self, 
                source_resource_group_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_move_resources(
                self, 
                source_resource_group_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                resource_provider_namespace: str, 
                parent_resource_path: str, 
                resource_type: str, 
                resource_name: str, 
                parameters: GenericResource, 
                *, 
                api_version: str, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GenericResource]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                resource_provider_namespace: str, 
                parent_resource_path: str, 
                resource_type: str, 
                resource_name: str, 
                parameters: JSON, 
                *, 
                api_version: str, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GenericResource]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                resource_provider_namespace: str, 
                parent_resource_path: str, 
                resource_type: str, 
                resource_name: str, 
                parameters: IO[bytes], 
                *, 
                api_version: str, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GenericResource]: ...

        @overload
        async def begin_update_by_id(
                self, 
                resource_id: str, 
                parameters: GenericResource, 
                *, 
                api_version: str, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GenericResource]: ...

        @overload
        async def begin_update_by_id(
                self, 
                resource_id: str, 
                parameters: JSON, 
                *, 
                api_version: str, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GenericResource]: ...

        @overload
        async def begin_update_by_id(
                self, 
                resource_id: str, 
                parameters: IO[bytes], 
                *, 
                api_version: str, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GenericResource]: ...

        @overload
        async def begin_validate_move_resources(
                self, 
                source_resource_group_name: str, 
                parameters: ResourcesMoveInfo, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_validate_move_resources(
                self, 
                source_resource_group_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_validate_move_resources(
                self, 
                source_resource_group_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def check_existence(
                self, 
                resource_group_name: str, 
                resource_provider_namespace: str, 
                parent_resource_path: str, 
                resource_type: str, 
                resource_name: str, 
                *, 
                api_version: str, 
                **kwargs: Any
            ) -> bool: ...

        @distributed_trace_async
        async def check_existence_by_id(
                self, 
                resource_id: str, 
                *, 
                api_version: str, 
                **kwargs: Any
            ) -> bool: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                resource_provider_namespace: str, 
                parent_resource_path: str, 
                resource_type: str, 
                resource_name: str, 
                *, 
                api_version: str, 
                **kwargs: Any
            ) -> GenericResource: ...

        @distributed_trace_async
        async def get_by_id(
                self, 
                resource_id: str, 
                *, 
                api_version: str, 
                **kwargs: Any
            ) -> GenericResource: ...

        @distributed_trace
        def list(
                self, 
                *, 
                expand: Optional[str] = ..., 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[GenericResourceExpanded]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                expand: Optional[str] = ..., 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[GenericResourceExpanded]: ...


    class azure.mgmt.resource.resources.aio.operations.TagsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update_at_scope(
                self, 
                scope: str, 
                parameters: TagsResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[TagsResource]: ...

        @overload
        async def begin_create_or_update_at_scope(
                self, 
                scope: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[TagsResource]: ...

        @overload
        async def begin_create_or_update_at_scope(
                self, 
                scope: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[TagsResource]: ...

        @distributed_trace_async
        async def begin_delete_at_scope(
                self, 
                scope: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update_at_scope(
                self, 
                scope: str, 
                parameters: TagsPatchResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[TagsResource]: ...

        @overload
        async def begin_update_at_scope(
                self, 
                scope: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[TagsResource]: ...

        @overload
        async def begin_update_at_scope(
                self, 
                scope: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[TagsResource]: ...

        @distributed_trace_async
        async def create_or_update(
                self, 
                tag_name: str, 
                **kwargs: Any
            ) -> TagDetails: ...

        @distributed_trace_async
        async def create_or_update_value(
                self, 
                tag_name: str, 
                tag_value: str, 
                **kwargs: Any
            ) -> TagValue: ...

        @distributed_trace_async
        async def delete(
                self, 
                tag_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def delete_value(
                self, 
                tag_name: str, 
                tag_value: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get_at_scope(
                self, 
                scope: str, 
                **kwargs: Any
            ) -> TagsResource: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[TagDetails]: ...


namespace azure.mgmt.resource.resources.models

    class azure.mgmt.resource.resources.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.resource.resources.models.Alias(_Model):
        default_metadata: Optional[AliasPathMetadata]
        default_path: Optional[str]
        default_pattern: Optional[AliasPattern]
        name: Optional[str]
        paths: Optional[list[AliasPath]]
        type: Optional[Union[str, AliasType]]

        @overload
        def __init__(
                self, 
                *, 
                default_path: Optional[str] = ..., 
                default_pattern: Optional[AliasPattern] = ..., 
                name: Optional[str] = ..., 
                paths: Optional[list[AliasPath]] = ..., 
                type: Optional[Union[str, AliasType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.resources.models.AliasPath(_Model):
        api_versions: Optional[list[str]]
        metadata: Optional[AliasPathMetadata]
        path: Optional[str]
        pattern: Optional[AliasPattern]

        @overload
        def __init__(
                self, 
                *, 
                api_versions: Optional[list[str]] = ..., 
                path: Optional[str] = ..., 
                pattern: Optional[AliasPattern] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.resources.models.AliasPathAttributes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MODIFIABLE = "Modifiable"
        NONE = "None"


    class azure.mgmt.resource.resources.models.AliasPathMetadata(_Model):
        attributes: Optional[Union[str, AliasPathAttributes]]
        type: Optional[Union[str, AliasPathTokenType]]


    class azure.mgmt.resource.resources.models.AliasPathTokenType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ANY = "Any"
        ARRAY = "Array"
        BOOLEAN = "Boolean"
        INTEGER = "Integer"
        NOT_SPECIFIED = "NotSpecified"
        NUMBER = "Number"
        OBJECT = "Object"
        STRING = "String"


    class azure.mgmt.resource.resources.models.AliasPattern(_Model):
        phrase: Optional[str]
        type: Optional[Union[str, AliasPatternType]]
        variable: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                phrase: Optional[str] = ..., 
                type: Optional[Union[str, AliasPatternType]] = ..., 
                variable: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.resources.models.AliasPatternType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EXTRACT = "Extract"
        NOT_SPECIFIED = "NotSpecified"


    class azure.mgmt.resource.resources.models.AliasType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MASK = "Mask"
        NOT_SPECIFIED = "NotSpecified"
        PLAIN_TEXT = "PlainText"


    class azure.mgmt.resource.resources.models.ApiProfile(_Model):
        api_version: Optional[str]
        profile_version: Optional[str]


    class azure.mgmt.resource.resources.models.CloudError(_Model):
        error: Optional[ErrorResponse]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorResponse] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.resources.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.resource.resources.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.resource.resources.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.resource.resources.models.ErrorResponse(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorResponse]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.resource.resources.models.ExportTemplateOutputFormat(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BICEP = "Bicep"
        JSON = "Json"


    class azure.mgmt.resource.resources.models.ExportTemplateRequest(_Model):
        options: Optional[str]
        output_format: Optional[Union[str, ExportTemplateOutputFormat]]
        resources: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                options: Optional[str] = ..., 
                output_format: Optional[Union[str, ExportTemplateOutputFormat]] = ..., 
                resources: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.resources.models.ExtendedLocation(_Model):
        name: Optional[str]
        type: Optional[Union[str, ExtendedLocationType]]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                type: Optional[Union[str, ExtendedLocationType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.resources.models.ExtendedLocationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EDGE_ZONE = "EdgeZone"


    class azure.mgmt.resource.resources.models.ExtensionResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.resource.resources.models.GenericResource(Resource):
        extended_location: Optional[ExtendedLocation]
        id: str
        identity: Optional[Identity]
        kind: Optional[str]
        location: Optional[str]
        managed_by: Optional[str]
        name: str
        plan: Optional[Plan]
        properties: Optional[Any]
        sku: Optional[Sku]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                extended_location: Optional[ExtendedLocation] = ..., 
                identity: Optional[Identity] = ..., 
                kind: Optional[str] = ..., 
                location: Optional[str] = ..., 
                managed_by: Optional[str] = ..., 
                plan: Optional[Plan] = ..., 
                properties: Optional[Any] = ..., 
                sku: Optional[Sku] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.resources.models.GenericResourceExpanded(GenericResource):
        changed_time: Optional[datetime]
        created_time: Optional[datetime]
        extended_location: ExtendedLocation
        id: str
        identity: Identity
        kind: str
        location: str
        managed_by: str
        name: str
        plan: Plan
        properties: any
        provisioning_state: Optional[str]
        sku: Sku
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                extended_location: Optional[ExtendedLocation] = ..., 
                identity: Optional[Identity] = ..., 
                kind: Optional[str] = ..., 
                location: Optional[str] = ..., 
                managed_by: Optional[str] = ..., 
                plan: Optional[Plan] = ..., 
                properties: Optional[Any] = ..., 
                sku: Optional[Sku] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.resources.models.Identity(_Model):
        principal_id: Optional[str]
        tenant_id: Optional[str]
        type: Optional[Union[str, ResourceIdentityType]]
        user_assigned_identities: Optional[dict[str, IdentityUserAssignedIdentitiesValue]]

        @overload
        def __init__(
                self, 
                *, 
                type: Optional[Union[str, ResourceIdentityType]] = ..., 
                user_assigned_identities: Optional[dict[str, IdentityUserAssignedIdentitiesValue]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.resources.models.IdentityUserAssignedIdentitiesValue(_Model):
        client_id: Optional[str]
        principal_id: Optional[str]


    class azure.mgmt.resource.resources.models.Operation(_Model):
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


    class azure.mgmt.resource.resources.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.resource.resources.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.resource.resources.models.Permission(_Model):
        actions: Optional[list[str]]
        data_actions: Optional[list[str]]
        not_actions: Optional[list[str]]
        not_data_actions: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                actions: Optional[list[str]] = ..., 
                data_actions: Optional[list[str]] = ..., 
                not_actions: Optional[list[str]] = ..., 
                not_data_actions: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.resources.models.Plan(_Model):
        name: Optional[str]
        product: Optional[str]
        promotion_code: Optional[str]
        publisher: Optional[str]
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                product: Optional[str] = ..., 
                promotion_code: Optional[str] = ..., 
                publisher: Optional[str] = ..., 
                version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.resources.models.Provider(_Model):
        id: Optional[str]
        namespace: Optional[str]
        provider_authorization_consent_state: Optional[Union[str, ProviderAuthorizationConsentState]]
        registration_policy: Optional[str]
        registration_state: Optional[str]
        resource_types: Optional[list[ProviderResourceType]]

        @overload
        def __init__(
                self, 
                *, 
                namespace: Optional[str] = ..., 
                provider_authorization_consent_state: Optional[Union[str, ProviderAuthorizationConsentState]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.resources.models.ProviderAuthorizationConsentState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONSENTED = "Consented"
        NOT_REQUIRED = "NotRequired"
        NOT_SPECIFIED = "NotSpecified"
        REQUIRED = "Required"


    class azure.mgmt.resource.resources.models.ProviderConsentDefinition(_Model):
        consent_to_authorization: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                consent_to_authorization: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.resources.models.ProviderExtendedLocation(_Model):
        extended_locations: Optional[list[str]]
        location: Optional[str]
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                extended_locations: Optional[list[str]] = ..., 
                location: Optional[str] = ..., 
                type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.resources.models.ProviderPermission(_Model):
        application_id: Optional[str]
        managed_by_role_definition: Optional[RoleDefinition]
        provider_authorization_consent_state: Optional[Union[str, ProviderAuthorizationConsentState]]
        role_definition: Optional[RoleDefinition]

        @overload
        def __init__(
                self, 
                *, 
                application_id: Optional[str] = ..., 
                managed_by_role_definition: Optional[RoleDefinition] = ..., 
                provider_authorization_consent_state: Optional[Union[str, ProviderAuthorizationConsentState]] = ..., 
                role_definition: Optional[RoleDefinition] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.resources.models.ProviderPermissionListResult(_Model):
        next_link: Optional[str]
        value: list[ProviderPermission]

        @overload
        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: list[ProviderPermission]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.resources.models.ProviderRegistrationRequest(_Model):
        third_party_provider_consent: Optional[ProviderConsentDefinition]

        @overload
        def __init__(
                self, 
                *, 
                third_party_provider_consent: Optional[ProviderConsentDefinition] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.resources.models.ProviderResourceType(_Model):
        aliases: Optional[list[Alias]]
        api_profiles: Optional[list[ApiProfile]]
        api_versions: Optional[list[str]]
        capabilities: Optional[str]
        default_api_version: Optional[str]
        location_mappings: Optional[list[ProviderExtendedLocation]]
        locations: Optional[list[str]]
        properties: Optional[dict[str, str]]
        resource_type: Optional[str]
        zone_mappings: Optional[list[ZoneMapping]]

        @overload
        def __init__(
                self, 
                *, 
                aliases: Optional[list[Alias]] = ..., 
                api_versions: Optional[list[str]] = ..., 
                capabilities: Optional[str] = ..., 
                location_mappings: Optional[list[ProviderExtendedLocation]] = ..., 
                locations: Optional[list[str]] = ..., 
                properties: Optional[dict[str, str]] = ..., 
                resource_type: Optional[str] = ..., 
                zone_mappings: Optional[list[ZoneMapping]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.resources.models.ProviderResourceTypeListResult(_Model):
        next_link: Optional[str]
        value: list[ProviderResourceType]

        @overload
        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: list[ProviderResourceType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.resources.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.resource.resources.models.ResourceGroup(TrackedResource):
        id: str
        location: str
        managed_by: Optional[str]
        name: str
        properties: Optional[ResourceGroupProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                managed_by: Optional[str] = ..., 
                properties: Optional[ResourceGroupProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.resources.models.ResourceGroupExportResult(_Model):
        error: Optional[ErrorDetail]
        output: Optional[str]
        template: Optional[Any]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ..., 
                output: Optional[str] = ..., 
                template: Optional[Any] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.resources.models.ResourceGroupPatchable(_Model):
        managed_by: Optional[str]
        name: Optional[str]
        properties: Optional[ResourceGroupProperties]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                managed_by: Optional[str] = ..., 
                name: Optional[str] = ..., 
                properties: Optional[ResourceGroupProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.resources.models.ResourceGroupProperties(_Model):
        provisioning_state: Optional[str]


    class azure.mgmt.resource.resources.models.ResourceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        SYSTEM_ASSIGNED_USER_ASSIGNED = "SystemAssigned, UserAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.resource.resources.models.ResourcesMoveInfo(_Model):
        resources: Optional[list[str]]
        target_resource_group: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                resources: Optional[list[str]] = ..., 
                target_resource_group: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.resources.models.RoleDefinition(_Model):
        id: Optional[str]
        is_service_role: Optional[bool]
        name: Optional[str]
        permissions: Optional[list[Permission]]
        scopes: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                is_service_role: Optional[bool] = ..., 
                name: Optional[str] = ..., 
                permissions: Optional[list[Permission]] = ..., 
                scopes: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.resources.models.Sku(_Model):
        capacity: Optional[int]
        family: Optional[str]
        model: Optional[str]
        name: Optional[str]
        size: Optional[str]
        tier: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                capacity: Optional[int] = ..., 
                family: Optional[str] = ..., 
                model: Optional[str] = ..., 
                name: Optional[str] = ..., 
                size: Optional[str] = ..., 
                tier: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.resources.models.SystemData(_Model):
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


    class azure.mgmt.resource.resources.models.TagCount(_Model):
        type: Optional[str]
        value: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                type: Optional[str] = ..., 
                value: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.resources.models.TagDetails(_Model):
        count: Optional[TagCount]
        id: Optional[str]
        tag_name: Optional[str]
        values_property: Optional[list[TagValue]]

        @overload
        def __init__(
                self, 
                *, 
                count: Optional[TagCount] = ..., 
                tag_name: Optional[str] = ..., 
                values_property: Optional[list[TagValue]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.resources.models.TagValue(_Model):
        count: Optional[TagCount]
        id: Optional[str]
        tag_value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                count: Optional[TagCount] = ..., 
                tag_value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.resources.models.Tags(_Model):
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.resources.models.TagsPatchOperation(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DELETE = "Delete"
        MERGE = "Merge"
        REPLACE = "Replace"


    class azure.mgmt.resource.resources.models.TagsPatchResource(_Model):
        operation: Optional[Union[str, TagsPatchOperation]]
        properties: Optional[Tags]

        @overload
        def __init__(
                self, 
                *, 
                operation: Optional[Union[str, TagsPatchOperation]] = ..., 
                properties: Optional[Tags] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.resources.models.TagsResource(ExtensionResource):
        id: str
        name: str
        properties: Tags
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Tags
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.resources.models.TrackedResource(Resource):
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


    class azure.mgmt.resource.resources.models.ZoneMapping(_Model):
        location: Optional[str]
        zones: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                zones: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


namespace azure.mgmt.resource.resources.operations

    class azure.mgmt.resource.resources.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


    class azure.mgmt.resource.resources.operations.ProviderResourceTypesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                resource_provider_namespace: str, 
                *, 
                expand: Optional[str] = ..., 
                **kwargs: Any
            ) -> ProviderResourceTypeListResult: ...


    class azure.mgmt.resource.resources.operations.ProvidersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_provider_namespace: str, 
                *, 
                expand: Optional[str] = ..., 
                **kwargs: Any
            ) -> Provider: ...

        @distributed_trace
        def get_at_tenant_scope(
                self, 
                resource_provider_namespace: str, 
                *, 
                expand: Optional[str] = ..., 
                **kwargs: Any
            ) -> Provider: ...

        @distributed_trace
        def list(
                self, 
                *, 
                expand: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Provider]: ...

        @distributed_trace
        def list_at_tenant_scope(
                self, 
                *, 
                expand: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Provider]: ...

        @distributed_trace
        def provider_permissions(
                self, 
                resource_provider_namespace: str, 
                **kwargs: Any
            ) -> ProviderPermissionListResult: ...

        @overload
        def register(
                self, 
                resource_provider_namespace: str, 
                properties: Optional[ProviderRegistrationRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Provider: ...

        @overload
        def register(
                self, 
                resource_provider_namespace: str, 
                properties: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Provider: ...

        @overload
        def register(
                self, 
                resource_provider_namespace: str, 
                properties: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Provider: ...

        @distributed_trace
        def register_at_management_group_scope(
                self, 
                resource_provider_namespace: str, 
                group_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def unregister(
                self, 
                resource_provider_namespace: str, 
                **kwargs: Any
            ) -> Provider: ...


    class azure.mgmt.resource.resources.operations.ResourceGroupsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                *, 
                force_deletion_types: Optional[str] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_export_template(
                self, 
                resource_group_name: str, 
                parameters: ExportTemplateRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ResourceGroupExportResult]: ...

        @overload
        def begin_export_template(
                self, 
                resource_group_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ResourceGroupExportResult]: ...

        @overload
        def begin_export_template(
                self, 
                resource_group_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ResourceGroupExportResult]: ...

        @distributed_trace
        def check_existence(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> bool: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                parameters: ResourceGroup, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ResourceGroup: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ResourceGroup: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ResourceGroup: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ResourceGroup: ...

        @distributed_trace
        def list(
                self, 
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[ResourceGroup]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                parameters: ResourceGroupPatchable, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ResourceGroup: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ResourceGroup: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ResourceGroup: ...


    class azure.mgmt.resource.resources.operations.ResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_provider_namespace: str, 
                parent_resource_path: str, 
                resource_type: str, 
                resource_name: str, 
                parameters: GenericResource, 
                *, 
                api_version: str, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GenericResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_provider_namespace: str, 
                parent_resource_path: str, 
                resource_type: str, 
                resource_name: str, 
                parameters: JSON, 
                *, 
                api_version: str, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GenericResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_provider_namespace: str, 
                parent_resource_path: str, 
                resource_type: str, 
                resource_name: str, 
                parameters: IO[bytes], 
                *, 
                api_version: str, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GenericResource]: ...

        @overload
        def begin_create_or_update_by_id(
                self, 
                resource_id: str, 
                parameters: GenericResource, 
                *, 
                api_version: str, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GenericResource]: ...

        @overload
        def begin_create_or_update_by_id(
                self, 
                resource_id: str, 
                parameters: JSON, 
                *, 
                api_version: str, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GenericResource]: ...

        @overload
        def begin_create_or_update_by_id(
                self, 
                resource_id: str, 
                parameters: IO[bytes], 
                *, 
                api_version: str, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GenericResource]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                resource_provider_namespace: str, 
                parent_resource_path: str, 
                resource_type: str, 
                resource_name: str, 
                *, 
                api_version: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_delete_by_id(
                self, 
                resource_id: str, 
                *, 
                api_version: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_move_resources(
                self, 
                source_resource_group_name: str, 
                parameters: ResourcesMoveInfo, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_move_resources(
                self, 
                source_resource_group_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_move_resources(
                self, 
                source_resource_group_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                resource_provider_namespace: str, 
                parent_resource_path: str, 
                resource_type: str, 
                resource_name: str, 
                parameters: GenericResource, 
                *, 
                api_version: str, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GenericResource]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                resource_provider_namespace: str, 
                parent_resource_path: str, 
                resource_type: str, 
                resource_name: str, 
                parameters: JSON, 
                *, 
                api_version: str, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GenericResource]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                resource_provider_namespace: str, 
                parent_resource_path: str, 
                resource_type: str, 
                resource_name: str, 
                parameters: IO[bytes], 
                *, 
                api_version: str, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GenericResource]: ...

        @overload
        def begin_update_by_id(
                self, 
                resource_id: str, 
                parameters: GenericResource, 
                *, 
                api_version: str, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GenericResource]: ...

        @overload
        def begin_update_by_id(
                self, 
                resource_id: str, 
                parameters: JSON, 
                *, 
                api_version: str, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GenericResource]: ...

        @overload
        def begin_update_by_id(
                self, 
                resource_id: str, 
                parameters: IO[bytes], 
                *, 
                api_version: str, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GenericResource]: ...

        @overload
        def begin_validate_move_resources(
                self, 
                source_resource_group_name: str, 
                parameters: ResourcesMoveInfo, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_validate_move_resources(
                self, 
                source_resource_group_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_validate_move_resources(
                self, 
                source_resource_group_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def check_existence(
                self, 
                resource_group_name: str, 
                resource_provider_namespace: str, 
                parent_resource_path: str, 
                resource_type: str, 
                resource_name: str, 
                *, 
                api_version: str, 
                **kwargs: Any
            ) -> bool: ...

        @distributed_trace
        def check_existence_by_id(
                self, 
                resource_id: str, 
                *, 
                api_version: str, 
                **kwargs: Any
            ) -> bool: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                resource_provider_namespace: str, 
                parent_resource_path: str, 
                resource_type: str, 
                resource_name: str, 
                *, 
                api_version: str, 
                **kwargs: Any
            ) -> GenericResource: ...

        @distributed_trace
        def get_by_id(
                self, 
                resource_id: str, 
                *, 
                api_version: str, 
                **kwargs: Any
            ) -> GenericResource: ...

        @distributed_trace
        def list(
                self, 
                *, 
                expand: Optional[str] = ..., 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[GenericResourceExpanded]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                expand: Optional[str] = ..., 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[GenericResourceExpanded]: ...


    class azure.mgmt.resource.resources.operations.TagsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update_at_scope(
                self, 
                scope: str, 
                parameters: TagsResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[TagsResource]: ...

        @overload
        def begin_create_or_update_at_scope(
                self, 
                scope: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[TagsResource]: ...

        @overload
        def begin_create_or_update_at_scope(
                self, 
                scope: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[TagsResource]: ...

        @distributed_trace
        def begin_delete_at_scope(
                self, 
                scope: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update_at_scope(
                self, 
                scope: str, 
                parameters: TagsPatchResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[TagsResource]: ...

        @overload
        def begin_update_at_scope(
                self, 
                scope: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[TagsResource]: ...

        @overload
        def begin_update_at_scope(
                self, 
                scope: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[TagsResource]: ...

        @distributed_trace
        def create_or_update(
                self, 
                tag_name: str, 
                **kwargs: Any
            ) -> TagDetails: ...

        @distributed_trace
        def create_or_update_value(
                self, 
                tag_name: str, 
                tag_value: str, 
                **kwargs: Any
            ) -> TagValue: ...

        @distributed_trace
        def delete(
                self, 
                tag_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete_value(
                self, 
                tag_name: str, 
                tag_value: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get_at_scope(
                self, 
                scope: str, 
                **kwargs: Any
            ) -> TagsResource: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[TagDetails]: ...


```