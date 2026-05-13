```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.portalservicescopilot

    class azure.mgmt.portalservicescopilot.PortalServicesCopilotMgmtClient: implements ContextManager 
        copilot_settings: CopilotSettingsOperations
        operations: Operations

        def __init__(
                self, 
                credential: TokenCredential, 
                base_url: str = "https://management.azure.com", 
                *, 
                api_version: str = ..., 
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


namespace azure.mgmt.portalservicescopilot.aio

    class azure.mgmt.portalservicescopilot.aio.PortalServicesCopilotMgmtClient: implements AsyncContextManager 
        copilot_settings: CopilotSettingsOperations
        operations: Operations

        def __init__(
                self, 
                credential: AsyncTokenCredential, 
                base_url: str = "https://management.azure.com", 
                *, 
                api_version: str = ..., 
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


namespace azure.mgmt.portalservicescopilot.aio.operations

    class azure.mgmt.portalservicescopilot.aio.operations.CopilotSettingsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource: CopilotSettingsResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CopilotSettingsResource: ...

        @overload
        async def create_or_update(
                self, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CopilotSettingsResource: ...

        @overload
        async def create_or_update(
                self, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CopilotSettingsResource: ...

        @distributed_trace_async
        async def delete(self, **kwargs: Any) -> None: ...

        @distributed_trace_async
        async def get(self, **kwargs: Any) -> CopilotSettingsResource: ...

        @overload
        async def update(
                self, 
                properties: CopilotSettingsResourceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CopilotSettingsResource: ...

        @overload
        async def update(
                self, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CopilotSettingsResource: ...

        @overload
        async def update(
                self, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CopilotSettingsResource: ...


    class azure.mgmt.portalservicescopilot.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncIterable[Operation]: ...


namespace azure.mgmt.portalservicescopilot.models

    class azure.mgmt.portalservicescopilot.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.portalservicescopilot.models.CopilotSettingsProperties(Model):
        access_control_enabled: bool
        provisioning_state: Optional[Union[str, ResourceProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                access_control_enabled: bool
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.portalservicescopilot.models.CopilotSettingsResource(ProxyResource):
        id: str
        name: str
        properties: Optional[CopilotSettingsProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[CopilotSettingsProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.portalservicescopilot.models.CopilotSettingsResourceUpdate(Model):
        properties: Optional[CopilotSettingsResourceUpdateProperties]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[CopilotSettingsResourceUpdateProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.portalservicescopilot.models.CopilotSettingsResourceUpdateProperties(Model):
        access_control_enabled: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                access_control_enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.portalservicescopilot.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.portalservicescopilot.models.ErrorAdditionalInfo(Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.portalservicescopilot.models.ErrorDetail(Model):
        additional_info: Optional[List[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[List[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.portalservicescopilot.models.ErrorResponse(Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.portalservicescopilot.models.Operation(Model):
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


    class azure.mgmt.portalservicescopilot.models.OperationDisplay(Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.portalservicescopilot.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.portalservicescopilot.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.portalservicescopilot.models.Resource(Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.portalservicescopilot.models.ResourceProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.portalservicescopilot.models.SystemData(Model):
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


namespace azure.mgmt.portalservicescopilot.operations

    class azure.mgmt.portalservicescopilot.operations.CopilotSettingsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create_or_update(
                self, 
                resource: CopilotSettingsResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CopilotSettingsResource: ...

        @overload
        def create_or_update(
                self, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CopilotSettingsResource: ...

        @overload
        def create_or_update(
                self, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CopilotSettingsResource: ...

        @distributed_trace
        def delete(self, **kwargs: Any) -> None: ...

        @distributed_trace
        def get(self, **kwargs: Any) -> CopilotSettingsResource: ...

        @overload
        def update(
                self, 
                properties: CopilotSettingsResourceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CopilotSettingsResource: ...

        @overload
        def update(
                self, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CopilotSettingsResource: ...

        @overload
        def update(
                self, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CopilotSettingsResource: ...


    class azure.mgmt.portalservicescopilot.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def list(self, **kwargs: Any) -> Iterable[Operation]: ...


```