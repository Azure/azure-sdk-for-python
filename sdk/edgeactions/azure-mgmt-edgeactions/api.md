```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.edgeactions

    class azure.mgmt.edgeactions.EdgeActionsMgmtClient: implements ContextManager 
        edge_action_execution_filters: EdgeActionExecutionFiltersOperations
        edge_action_versions: EdgeActionVersionsOperations
        edge_actions: EdgeActionsOperations

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


namespace azure.mgmt.edgeactions.aio

    class azure.mgmt.edgeactions.aio.EdgeActionsMgmtClient: implements AsyncContextManager 
        edge_action_execution_filters: EdgeActionExecutionFiltersOperations
        edge_action_versions: EdgeActionVersionsOperations
        edge_actions: EdgeActionsOperations

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


namespace azure.mgmt.edgeactions.aio.operations

    class azure.mgmt.edgeactions.aio.operations.EdgeActionExecutionFiltersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                edge_action_name: str, 
                execution_filter: str, 
                resource: EdgeActionExecutionFilter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EdgeActionExecutionFilter]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                edge_action_name: str, 
                execution_filter: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EdgeActionExecutionFilter]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                edge_action_name: str, 
                execution_filter: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EdgeActionExecutionFilter]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                edge_action_name: str, 
                execution_filter: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                edge_action_name: str, 
                execution_filter: str, 
                properties: EdgeActionExecutionFilterUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EdgeActionExecutionFilter]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                edge_action_name: str, 
                execution_filter: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EdgeActionExecutionFilter]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                edge_action_name: str, 
                execution_filter: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EdgeActionExecutionFilter]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                edge_action_name: str, 
                execution_filter: str, 
                **kwargs: Any
            ) -> EdgeActionExecutionFilter: ...

        @distributed_trace
        def list_by_edge_action(
                self, 
                resource_group_name: str, 
                edge_action_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[EdgeActionExecutionFilter]: ...


    class azure.mgmt.edgeactions.aio.operations.EdgeActionVersionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                edge_action_name: str, 
                version: str, 
                resource: EdgeActionVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EdgeActionVersion]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                edge_action_name: str, 
                version: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EdgeActionVersion]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                edge_action_name: str, 
                version: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EdgeActionVersion]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                edge_action_name: str, 
                version: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_deploy_version_code(
                self, 
                resource_group_name: str, 
                edge_action_name: str, 
                version: str, 
                body: VersionCode, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EdgeActionVersionProperties]: ...

        @overload
        async def begin_deploy_version_code(
                self, 
                resource_group_name: str, 
                edge_action_name: str, 
                version: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EdgeActionVersionProperties]: ...

        @overload
        async def begin_deploy_version_code(
                self, 
                resource_group_name: str, 
                edge_action_name: str, 
                version: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EdgeActionVersionProperties]: ...

        @distributed_trace_async
        async def begin_get_version_code(
                self, 
                resource_group_name: str, 
                edge_action_name: str, 
                version: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[VersionCode]: ...

        @distributed_trace_async
        async def begin_swap_default(
                self, 
                resource_group_name: str, 
                edge_action_name: str, 
                version: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                edge_action_name: str, 
                version: str, 
                properties: EdgeActionVersionUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EdgeActionVersion]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                edge_action_name: str, 
                version: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EdgeActionVersion]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                edge_action_name: str, 
                version: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EdgeActionVersion]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                edge_action_name: str, 
                version: str, 
                **kwargs: Any
            ) -> EdgeActionVersion: ...

        @distributed_trace
        def list_by_edge_action(
                self, 
                resource_group_name: str, 
                edge_action_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[EdgeActionVersion]: ...


    class azure.mgmt.edgeactions.aio.operations.EdgeActionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                edge_action_name: str, 
                resource: EdgeAction, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EdgeAction]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                edge_action_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EdgeAction]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                edge_action_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EdgeAction]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                edge_action_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                edge_action_name: str, 
                properties: EdgeActionUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EdgeAction]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                edge_action_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EdgeAction]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                edge_action_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EdgeAction]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                edge_action_name: str, 
                **kwargs: Any
            ) -> EdgeAction: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[EdgeAction]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[EdgeAction]: ...


namespace azure.mgmt.edgeactions.models

    class azure.mgmt.edgeactions.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.edgeactions.models.EdgeAction(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[EdgeActionProperties]
        sku: SkuType
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[EdgeActionProperties] = ..., 
                sku: SkuType, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.edgeactions.models.EdgeActionAttachment(_Model):
        attached_resource_id: str
        id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                attached_resource_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.edgeactions.models.EdgeActionExecutionFilter(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[EdgeActionExecutionFilterProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[EdgeActionExecutionFilterProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.edgeactions.models.EdgeActionExecutionFilterProperties(_Model):
        execution_filter_identifier_header_name: str
        execution_filter_identifier_header_value: str
        last_update_time: Optional[datetime]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        version_id: str

        @overload
        def __init__(
                self, 
                *, 
                execution_filter_identifier_header_name: str, 
                execution_filter_identifier_header_value: str, 
                version_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.edgeactions.models.EdgeActionExecutionFilterUpdate(_Model):
        properties: Optional[EdgeActionExecutionFilterUpdateProperties]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[EdgeActionExecutionFilterUpdateProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.edgeactions.models.EdgeActionExecutionFilterUpdateProperties(_Model):
        execution_filter_identifier_header_name: Optional[str]
        execution_filter_identifier_header_value: Optional[str]
        version_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                execution_filter_identifier_header_name: Optional[str] = ..., 
                execution_filter_identifier_header_value: Optional[str] = ..., 
                version_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.edgeactions.models.EdgeActionIsDefaultVersion(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FALSE = "False"
        TRUE = "True"


    class azure.mgmt.edgeactions.models.EdgeActionProperties(_Model):
        attachments: list[EdgeActionAttachment]
        provisioning_state: Optional[Union[str, ProvisioningState]]


    class azure.mgmt.edgeactions.models.EdgeActionPropertiesUpdate(_Model):


    class azure.mgmt.edgeactions.models.EdgeActionUpdate(_Model):
        properties: Optional[EdgeActionPropertiesUpdate]
        sku: Optional[SkuTypeUpdate]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[EdgeActionPropertiesUpdate] = ..., 
                sku: Optional[SkuTypeUpdate] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.edgeactions.models.EdgeActionVersion(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[EdgeActionVersionProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[EdgeActionVersionProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.edgeactions.models.EdgeActionVersionDeploymentType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FILE = "file"
        OTHERS = "others"
        ZIP = "zip"


    class azure.mgmt.edgeactions.models.EdgeActionVersionProperties(_Model):
        deployment_type: Union[str, EdgeActionVersionDeploymentType]
        is_default_version: Union[str, EdgeActionIsDefaultVersion]
        last_package_update_time: Optional[datetime]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        validation_status: Optional[Union[str, EdgeActionVersionValidationStatus]]

        @overload
        def __init__(
                self, 
                *, 
                deployment_type: Union[str, EdgeActionVersionDeploymentType], 
                is_default_version: Union[str, EdgeActionIsDefaultVersion]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.edgeactions.models.EdgeActionVersionUpdate(_Model):
        properties: Optional[EdgeActionVersionUpdateProperties]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[EdgeActionVersionUpdateProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.edgeactions.models.EdgeActionVersionUpdateProperties(_Model):
        deployment_type: Optional[Union[str, EdgeActionVersionDeploymentType]]
        is_default_version: Optional[Union[str, EdgeActionIsDefaultVersion]]

        @overload
        def __init__(
                self, 
                *, 
                deployment_type: Optional[Union[str, EdgeActionVersionDeploymentType]] = ..., 
                is_default_version: Optional[Union[str, EdgeActionIsDefaultVersion]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.edgeactions.models.EdgeActionVersionValidationStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.edgeactions.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.edgeactions.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.edgeactions.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.edgeactions.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        FAILED = "Failed"
        PROVISIONING = "Provisioning"
        SUCCEEDED = "Succeeded"
        UPGRADING = "Upgrading"


    class azure.mgmt.edgeactions.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.edgeactions.models.SkuType(_Model):
        name: str
        tier: str

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                tier: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.edgeactions.models.SkuTypeUpdate(_Model):
        name: Optional[str]
        tier: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                tier: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.edgeactions.models.SystemData(_Model):
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


    class azure.mgmt.edgeactions.models.TrackedResource(Resource):
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


    class azure.mgmt.edgeactions.models.VersionCode(_Model):
        content: str
        name: str

        @overload
        def __init__(
                self, 
                *, 
                content: str, 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


namespace azure.mgmt.edgeactions.operations

    class azure.mgmt.edgeactions.operations.EdgeActionExecutionFiltersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                edge_action_name: str, 
                execution_filter: str, 
                resource: EdgeActionExecutionFilter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EdgeActionExecutionFilter]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                edge_action_name: str, 
                execution_filter: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EdgeActionExecutionFilter]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                edge_action_name: str, 
                execution_filter: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EdgeActionExecutionFilter]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                edge_action_name: str, 
                execution_filter: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                edge_action_name: str, 
                execution_filter: str, 
                properties: EdgeActionExecutionFilterUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EdgeActionExecutionFilter]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                edge_action_name: str, 
                execution_filter: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EdgeActionExecutionFilter]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                edge_action_name: str, 
                execution_filter: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EdgeActionExecutionFilter]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                edge_action_name: str, 
                execution_filter: str, 
                **kwargs: Any
            ) -> EdgeActionExecutionFilter: ...

        @distributed_trace
        def list_by_edge_action(
                self, 
                resource_group_name: str, 
                edge_action_name: str, 
                **kwargs: Any
            ) -> ItemPaged[EdgeActionExecutionFilter]: ...


    class azure.mgmt.edgeactions.operations.EdgeActionVersionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                edge_action_name: str, 
                version: str, 
                resource: EdgeActionVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EdgeActionVersion]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                edge_action_name: str, 
                version: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EdgeActionVersion]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                edge_action_name: str, 
                version: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EdgeActionVersion]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                edge_action_name: str, 
                version: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_deploy_version_code(
                self, 
                resource_group_name: str, 
                edge_action_name: str, 
                version: str, 
                body: VersionCode, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EdgeActionVersionProperties]: ...

        @overload
        def begin_deploy_version_code(
                self, 
                resource_group_name: str, 
                edge_action_name: str, 
                version: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EdgeActionVersionProperties]: ...

        @overload
        def begin_deploy_version_code(
                self, 
                resource_group_name: str, 
                edge_action_name: str, 
                version: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EdgeActionVersionProperties]: ...

        @distributed_trace
        def begin_get_version_code(
                self, 
                resource_group_name: str, 
                edge_action_name: str, 
                version: str, 
                **kwargs: Any
            ) -> LROPoller[VersionCode]: ...

        @distributed_trace
        def begin_swap_default(
                self, 
                resource_group_name: str, 
                edge_action_name: str, 
                version: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                edge_action_name: str, 
                version: str, 
                properties: EdgeActionVersionUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EdgeActionVersion]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                edge_action_name: str, 
                version: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EdgeActionVersion]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                edge_action_name: str, 
                version: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EdgeActionVersion]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                edge_action_name: str, 
                version: str, 
                **kwargs: Any
            ) -> EdgeActionVersion: ...

        @distributed_trace
        def list_by_edge_action(
                self, 
                resource_group_name: str, 
                edge_action_name: str, 
                **kwargs: Any
            ) -> ItemPaged[EdgeActionVersion]: ...


    class azure.mgmt.edgeactions.operations.EdgeActionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                edge_action_name: str, 
                resource: EdgeAction, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EdgeAction]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                edge_action_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EdgeAction]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                edge_action_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EdgeAction]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                edge_action_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                edge_action_name: str, 
                properties: EdgeActionUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EdgeAction]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                edge_action_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EdgeAction]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                edge_action_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EdgeAction]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                edge_action_name: str, 
                **kwargs: Any
            ) -> EdgeAction: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[EdgeAction]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[EdgeAction]: ...


```