```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.computerecommender

    class azure.mgmt.computerecommender.RecommenderMgmtClient: implements ContextManager 
        operations: Operations
        spot_placement_scores: SpotPlacementScoresOperations

        def __init__(
                self, 
                credential: TokenCredential, 
                subscription_id: str, 
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


namespace azure.mgmt.computerecommender.aio

    class azure.mgmt.computerecommender.aio.RecommenderMgmtClient: implements AsyncContextManager 
        operations: Operations
        spot_placement_scores: SpotPlacementScoresOperations

        def __init__(
                self, 
                credential: AsyncTokenCredential, 
                subscription_id: str, 
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


namespace azure.mgmt.computerecommender.aio.operations

    class azure.mgmt.computerecommender.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


    class azure.mgmt.computerecommender.aio.operations.SpotPlacementScoresOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                location: str, 
                **kwargs: Any
            ) -> ComputeDiagnosticBase: ...

        @overload
        async def post(
                self, 
                location: str, 
                spot_placement_scores_input: SpotPlacementScoresInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SpotPlacementScoresResponse: ...

        @overload
        async def post(
                self, 
                location: str, 
                spot_placement_scores_input: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SpotPlacementScoresResponse: ...

        @overload
        async def post(
                self, 
                location: str, 
                spot_placement_scores_input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SpotPlacementScoresResponse: ...


namespace azure.mgmt.computerecommender.models

    class azure.mgmt.computerecommender.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.computerecommender.models.ComputeDiagnosticBase(ProxyResource):
        id: str
        name: str
        properties: Optional[DiagnosticProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[DiagnosticProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computerecommender.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.computerecommender.models.DiagnosticProperties(_Model):
        supported_resource_types: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                supported_resource_types: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computerecommender.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.computerecommender.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.computerecommender.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computerecommender.models.Operation(_Model):
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


    class azure.mgmt.computerecommender.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.computerecommender.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.computerecommender.models.PlacementScore(_Model):
        availability_zone: Optional[str]
        is_quota_available: Optional[bool]
        region: Optional[str]
        score: Optional[str]
        sku: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                availability_zone: Optional[str] = ..., 
                is_quota_available: Optional[bool] = ..., 
                region: Optional[str] = ..., 
                score: Optional[str] = ..., 
                sku: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computerecommender.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.computerecommender.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.computerecommender.models.ResourceSize(_Model):
        sku: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                sku: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computerecommender.models.SpotPlacementScoresInput(_Model):
        availability_zones: Optional[bool]
        desired_count: Optional[int]
        desired_locations: Optional[list[str]]
        desired_sizes: Optional[list[ResourceSize]]

        @overload
        def __init__(
                self, 
                *, 
                availability_zones: Optional[bool] = ..., 
                desired_count: Optional[int] = ..., 
                desired_locations: Optional[list[str]] = ..., 
                desired_sizes: Optional[list[ResourceSize]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computerecommender.models.SpotPlacementScoresResponse(_Model):
        availability_zones: Optional[bool]
        desired_count: Optional[int]
        desired_locations: Optional[list[str]]
        desired_sizes: Optional[list[ResourceSize]]
        placement_scores: Optional[list[PlacementScore]]

        @overload
        def __init__(
                self, 
                *, 
                availability_zones: Optional[bool] = ..., 
                desired_count: Optional[int] = ..., 
                desired_locations: Optional[list[str]] = ..., 
                desired_sizes: Optional[list[ResourceSize]] = ..., 
                placement_scores: Optional[list[PlacementScore]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computerecommender.models.SystemData(_Model):
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


namespace azure.mgmt.computerecommender.operations

    class azure.mgmt.computerecommender.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


    class azure.mgmt.computerecommender.operations.SpotPlacementScoresOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                location: str, 
                **kwargs: Any
            ) -> ComputeDiagnosticBase: ...

        @overload
        def post(
                self, 
                location: str, 
                spot_placement_scores_input: SpotPlacementScoresInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SpotPlacementScoresResponse: ...

        @overload
        def post(
                self, 
                location: str, 
                spot_placement_scores_input: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SpotPlacementScoresResponse: ...

        @overload
        def post(
                self, 
                location: str, 
                spot_placement_scores_input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SpotPlacementScoresResponse: ...


```