```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.edgezones

    class azure.mgmt.edgezones.EdgeZonesMgmtClient: implements ContextManager 
        extended_zones: ExtendedZonesOperations
        operations: Operations

        def __init__(
                self, 
                credential: TokenCredential, 
                subscription_id: str, 
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


namespace azure.mgmt.edgezones.aio

    class azure.mgmt.edgezones.aio.EdgeZonesMgmtClient: implements AsyncContextManager 
        extended_zones: ExtendedZonesOperations
        operations: Operations

        def __init__(
                self, 
                credential: AsyncTokenCredential, 
                subscription_id: str, 
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


namespace azure.mgmt.edgezones.aio.operations

    class azure.mgmt.edgezones.aio.operations.ExtendedZonesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                extended_zone_name: str, 
                **kwargs: Any
            ) -> ExtendedZone: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncIterable[ExtendedZone]: ...

        @distributed_trace_async
        async def register(
                self, 
                extended_zone_name: str, 
                **kwargs: Any
            ) -> ExtendedZone: ...

        @distributed_trace_async
        async def unregister(
                self, 
                extended_zone_name: str, 
                **kwargs: Any
            ) -> ExtendedZone: ...


    class azure.mgmt.edgezones.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncIterable[Operation]: ...


namespace azure.mgmt.edgezones.models

    class azure.mgmt.edgezones.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.edgezones.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.edgezones.models.ErrorAdditionalInfo(Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.edgezones.models.ErrorDetail(Model):
        additional_info: Optional[List[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[List[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.edgezones.models.ErrorResponse(Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.edgezones.models.ExtendedZone(ProxyResource):
        id: str
        name: str
        properties: Optional[ExtendedZoneProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ExtendedZoneProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.edgezones.models.ExtendedZoneProperties(Model):
        display_name: str
        geography: str
        geography_group: str
        home_location: str
        latitude: str
        longitude: str
        provisioning_state: Optional[Union[str, ProvisioningState]]
        region_category: str
        region_type: str
        regional_display_name: str
        registration_state: Optional[Union[str, RegistrationState]]


    class azure.mgmt.edgezones.models.Operation(Model):
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


    class azure.mgmt.edgezones.models.OperationDisplay(Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.edgezones.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.edgezones.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CANCELED = "Canceled"
        DELETING = "Deleting"
        FAILED = "Failed"
        PROVISIONING = "Provisioning"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.edgezones.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.edgezones.models.RegistrationState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NOT_REGISTERED = "NotRegistered"
        PENDING_REGISTER = "PendingRegister"
        PENDING_UNREGISTER = "PendingUnregister"
        REGISTERED = "Registered"


    class azure.mgmt.edgezones.models.Resource(Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.edgezones.models.SystemData(Model):
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


namespace azure.mgmt.edgezones.operations

    class azure.mgmt.edgezones.operations.ExtendedZonesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                extended_zone_name: str, 
                **kwargs: Any
            ) -> ExtendedZone: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> Iterable[ExtendedZone]: ...

        @distributed_trace
        def register(
                self, 
                extended_zone_name: str, 
                **kwargs: Any
            ) -> ExtendedZone: ...

        @distributed_trace
        def unregister(
                self, 
                extended_zone_name: str, 
                **kwargs: Any
            ) -> ExtendedZone: ...


    class azure.mgmt.edgezones.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def list(self, **kwargs: Any) -> Iterable[Operation]: ...


```