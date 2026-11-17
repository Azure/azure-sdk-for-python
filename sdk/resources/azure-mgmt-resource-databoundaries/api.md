```py
namespace azure.mgmt.resource.databoundaries

    class azure.mgmt.resource.databoundaries.DataBoundaryMgmtClient: implements ContextManager 
        data_boundaries: DataBoundariesOperations
        operations: Operations

        def __init__(
                self, 
                credential: TokenCredential, 
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


namespace azure.mgmt.resource.databoundaries.aio

    class azure.mgmt.resource.databoundaries.aio.DataBoundaryMgmtClient: implements AsyncContextManager 
        data_boundaries: DataBoundariesOperations
        operations: Operations

        def __init__(
                self, 
                credential: AsyncTokenCredential, 
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


namespace azure.mgmt.resource.databoundaries.aio.operations

    class azure.mgmt.resource.databoundaries.aio.operations.DataBoundariesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get_scope(
                self, 
                scope: str, 
                default: Union[str, DefaultName], 
                **kwargs: Any
            ) -> DataBoundaryDefinition: ...

        @distributed_trace_async
        async def get_tenant(
                self, 
                default: Union[str, DefaultName], 
                **kwargs: Any
            ) -> DataBoundaryDefinition: ...

        @overload
        async def put(
                self, 
                default: Union[str, DefaultName], 
                data_boundary_definition: DataBoundaryDefinition, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DataBoundaryDefinition: ...

        @overload
        async def put(
                self, 
                default: Union[str, DefaultName], 
                data_boundary_definition: DataBoundaryDefinition, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DataBoundaryDefinition: ...

        @overload
        async def put(
                self, 
                default: Union[str, DefaultName], 
                data_boundary_definition: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DataBoundaryDefinition: ...


    class azure.mgmt.resource.databoundaries.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


namespace azure.mgmt.resource.databoundaries.models

    class azure.mgmt.resource.databoundaries.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.resource.databoundaries.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.resource.databoundaries.models.DataBoundary(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EU = "EU"
        GLOBAL = "Global"
        NOT_DEFINED = "NotDefined"


    class azure.mgmt.resource.databoundaries.models.DataBoundaryDefinition(ProxyResource):
        id: str
        name: str
        properties: Optional[DataBoundaryProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[DataBoundaryProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.databoundaries.models.DataBoundaryProperties(_Model):
        data_boundary: Optional[Union[str, DataBoundary]]
        provisioning_state: Optional[Union[str, ProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                data_boundary: Optional[Union[str, DataBoundary]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.databoundaries.models.DefaultName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEFAULT = "default"


    class azure.mgmt.resource.databoundaries.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.resource.databoundaries.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.resource.databoundaries.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.databoundaries.models.Operation(_Model):
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


    class azure.mgmt.resource.databoundaries.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.resource.databoundaries.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.resource.databoundaries.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CANCELED = "Canceled"
        CREATING = "Creating"
        FAILED = "Failed"
        RUNNING = "Running"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.resource.databoundaries.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.resource.databoundaries.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.resource.databoundaries.models.SystemData(_Model):
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


namespace azure.mgmt.resource.databoundaries.operations

    class azure.mgmt.resource.databoundaries.operations.DataBoundariesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get_scope(
                self, 
                scope: str, 
                default: Union[str, DefaultName], 
                **kwargs: Any
            ) -> DataBoundaryDefinition: ...

        @distributed_trace
        def get_tenant(
                self, 
                default: Union[str, DefaultName], 
                **kwargs: Any
            ) -> DataBoundaryDefinition: ...

        @overload
        def put(
                self, 
                default: Union[str, DefaultName], 
                data_boundary_definition: DataBoundaryDefinition, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DataBoundaryDefinition: ...

        @overload
        def put(
                self, 
                default: Union[str, DefaultName], 
                data_boundary_definition: DataBoundaryDefinition, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DataBoundaryDefinition: ...

        @overload
        def put(
                self, 
                default: Union[str, DefaultName], 
                data_boundary_definition: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DataBoundaryDefinition: ...


    class azure.mgmt.resource.databoundaries.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


namespace azure.mgmt.resource.databoundaries.types

    class azure.mgmt.resource.databoundaries.types.DataBoundaryDefinition(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('DataBoundaryProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: DataBoundaryProperties
        system_data: SystemData
        type: str


    class azure.mgmt.resource.databoundaries.types.DataBoundaryProperties(TypedDict, total=False):
        key "dataBoundary": Union[str, DataBoundary]
        key "provisioningState": Union[str, ProvisioningState]
        data_boundary: Union[str, DataBoundary]
        provisioning_state: Union[str, ProvisioningState]


    class azure.mgmt.resource.databoundaries.types.ProxyResource(Resource):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.resource.databoundaries.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.resource.databoundaries.types.SystemData(TypedDict, total=False):
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


```