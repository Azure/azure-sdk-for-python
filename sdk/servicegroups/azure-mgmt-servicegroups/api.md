```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.servicegroups

    class azure.mgmt.servicegroups.ServiceGroupsMgmtClient(_ServiceGroupsMgmtClientOperationsMixin): implements ContextManager 
        service_groups: ServiceGroupsOperations

        def __init__(
                self, 
                credential: TokenCredential, 
                base_url: Optional[str] = None, 
                *, 
                api_version: str = ..., 
                cloud_setting: Optional[AzureClouds] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @overload
        def begin_create_or_update_service_group(
                self, 
                service_group_name: str, 
                create_service_group_request: ServiceGroup, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ServiceGroup]: ...

        @overload
        def begin_create_or_update_service_group(
                self, 
                service_group_name: str, 
                create_service_group_request: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ServiceGroup]: ...

        @overload
        def begin_create_or_update_service_group(
                self, 
                service_group_name: str, 
                create_service_group_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ServiceGroup]: ...

        @distributed_trace
        def begin_delete_service_group(
                self, 
                service_group_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update_service_group(
                self, 
                service_group_name: str, 
                update_service_group_request: ServiceGroup, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ServiceGroup]: ...

        @overload
        def begin_update_service_group(
                self, 
                service_group_name: str, 
                update_service_group_request: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ServiceGroup]: ...

        @overload
        def begin_update_service_group(
                self, 
                service_group_name: str, 
                update_service_group_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ServiceGroup]: ...

        def close(self) -> None: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> HttpResponse: ...


namespace azure.mgmt.servicegroups.aio

    class azure.mgmt.servicegroups.aio.ServiceGroupsMgmtClient(_ServiceGroupsMgmtClientOperationsMixin): implements AsyncContextManager 
        service_groups: ServiceGroupsOperations

        def __init__(
                self, 
                credential: AsyncTokenCredential, 
                base_url: Optional[str] = None, 
                *, 
                api_version: str = ..., 
                cloud_setting: Optional[AzureClouds] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def begin_create_or_update_service_group(
                self, 
                service_group_name: str, 
                create_service_group_request: ServiceGroup, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ServiceGroup]: ...

        @overload
        async def begin_create_or_update_service_group(
                self, 
                service_group_name: str, 
                create_service_group_request: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ServiceGroup]: ...

        @overload
        async def begin_create_or_update_service_group(
                self, 
                service_group_name: str, 
                create_service_group_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ServiceGroup]: ...

        @distributed_trace_async
        async def begin_delete_service_group(
                self, 
                service_group_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update_service_group(
                self, 
                service_group_name: str, 
                update_service_group_request: ServiceGroup, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ServiceGroup]: ...

        @overload
        async def begin_update_service_group(
                self, 
                service_group_name: str, 
                update_service_group_request: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ServiceGroup]: ...

        @overload
        async def begin_update_service_group(
                self, 
                service_group_name: str, 
                update_service_group_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ServiceGroup]: ...

        async def close(self) -> None: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> Awaitable[AsyncHttpResponse]: ...


namespace azure.mgmt.servicegroups.aio.operations

    class azure.mgmt.servicegroups.aio.operations.ServiceGroupsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                service_group_name: str, 
                **kwargs: Any
            ) -> ServiceGroup: ...

        @distributed_trace_async
        async def list_ancestors(
                self, 
                service_group_name: str, 
                **kwargs: Any
            ) -> ServiceGroupCollectionResponse: ...


namespace azure.mgmt.servicegroups.models

    class azure.mgmt.servicegroups.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.servicegroups.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.servicegroups.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.servicegroups.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicegroups.models.ParentServiceGroupProperties(_Model):
        resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicegroups.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        FAILED = "Failed"
        NOT_STARTED = "NotStarted"
        RUNNING = "Running"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.servicegroups.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.servicegroups.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.servicegroups.models.ServiceGroup(ProxyResource):
        id: str
        kind: Optional[str]
        name: str
        properties: Optional[ServiceGroupProperties]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                kind: Optional[str] = ..., 
                properties: Optional[ServiceGroupProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicegroups.models.ServiceGroupCollectionResponse(_Model):
        next_link: Optional[str]
        value: list[ServiceGroup]

        @overload
        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: list[ServiceGroup]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicegroups.models.ServiceGroupProperties(_Model):
        display_name: Optional[str]
        parent: Optional[ParentServiceGroupProperties]
        provisioning_state: Optional[Union[str, ProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ..., 
                parent: Optional[ParentServiceGroupProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicegroups.models.SystemData(_Model):
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


namespace azure.mgmt.servicegroups.operations

    class azure.mgmt.servicegroups.operations.ServiceGroupsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                service_group_name: str, 
                **kwargs: Any
            ) -> ServiceGroup: ...

        @distributed_trace
        def list_ancestors(
                self, 
                service_group_name: str, 
                **kwargs: Any
            ) -> ServiceGroupCollectionResponse: ...


```