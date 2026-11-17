```py
namespace azure.mgmt.resourcegraph

    class azure.mgmt.resourcegraph.ResourceGraphClient(_ResourceGraphClientOperationsMixin): implements ContextManager 
        graph_query: GraphQueryOperations
        operations: Operations

        def __init__(
                self, 
                credential: TokenCredential, 
                subscription_id: str, 
                base_url: Optional[str] = None, 
                *, 
                cloud_setting: Optional[AzureClouds] = ..., 
                **kwargs: Any
            ) -> None: ...

        def close(self) -> None: ...

        @overload
        def resource_change_details(
                self, 
                parameters: ResourceChangeDetailsRequestParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> List[ResourceChangeData]: ...

        @overload
        def resource_change_details(
                self, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> List[ResourceChangeData]: ...

        @overload
        def resource_change_details(
                self, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> List[ResourceChangeData]: ...

        @overload
        def resource_changes(
                self, 
                parameters: ResourceChangesRequestParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ResourceChangeList: ...

        @overload
        def resource_changes(
                self, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ResourceChangeList: ...

        @overload
        def resource_changes(
                self, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ResourceChangeList: ...

        @overload
        def resources(
                self, 
                query: QueryRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> QueryResponse: ...

        @overload
        def resources(
                self, 
                query: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> QueryResponse: ...

        @overload
        def resources(
                self, 
                query: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> QueryResponse: ...

        @overload
        def resources_history(
                self, 
                request: ResourcesHistoryRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Any: ...

        @overload
        def resources_history(
                self, 
                request: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Any: ...

        @overload
        def resources_history(
                self, 
                request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Any: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> HttpResponse: ...


namespace azure.mgmt.resourcegraph.aio

    class azure.mgmt.resourcegraph.aio.ResourceGraphClient(_ResourceGraphClientOperationsMixin): implements AsyncContextManager 
        graph_query: GraphQueryOperations
        operations: Operations

        def __init__(
                self, 
                credential: AsyncTokenCredential, 
                subscription_id: str, 
                base_url: Optional[str] = None, 
                *, 
                cloud_setting: Optional[AzureClouds] = ..., 
                **kwargs: Any
            ) -> None: ...

        async def close(self) -> None: ...

        @overload
        async def resource_change_details(
                self, 
                parameters: ResourceChangeDetailsRequestParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> List[ResourceChangeData]: ...

        @overload
        async def resource_change_details(
                self, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> List[ResourceChangeData]: ...

        @overload
        async def resource_change_details(
                self, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> List[ResourceChangeData]: ...

        @overload
        async def resource_changes(
                self, 
                parameters: ResourceChangesRequestParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ResourceChangeList: ...

        @overload
        async def resource_changes(
                self, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ResourceChangeList: ...

        @overload
        async def resource_changes(
                self, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ResourceChangeList: ...

        @overload
        async def resources(
                self, 
                query: QueryRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> QueryResponse: ...

        @overload
        async def resources(
                self, 
                query: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> QueryResponse: ...

        @overload
        async def resources(
                self, 
                query: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> QueryResponse: ...

        @overload
        async def resources_history(
                self, 
                request: ResourcesHistoryRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Any: ...

        @overload
        async def resources_history(
                self, 
                request: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Any: ...

        @overload
        async def resources_history(
                self, 
                request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Any: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> Awaitable[AsyncHttpResponse]: ...


namespace azure.mgmt.resourcegraph.aio.operations

    class azure.mgmt.resourcegraph.aio.operations.GraphQueryOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                properties: GraphQueryResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GraphQueryResource: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GraphQueryResource: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GraphQueryResource: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> GraphQueryResource: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[GraphQueryResource]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[GraphQueryResource]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                body: GraphQueryUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GraphQueryResource: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GraphQueryResource: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GraphQueryResource: ...


    class azure.mgmt.resourcegraph.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


namespace azure.mgmt.resourcegraph.models

    class azure.mgmt.resourcegraph.models.AuthorizationScopeFilter(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AT_SCOPE_ABOVE_AND_BELOW = "AtScopeAboveAndBelow"
        AT_SCOPE_AND_ABOVE = "AtScopeAndAbove"
        AT_SCOPE_AND_BELOW = "AtScopeAndBelow"
        AT_SCOPE_EXACT = "AtScopeExact"


    class azure.mgmt.resourcegraph.models.ChangeCategory(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "System"
        USER = "User"


    class azure.mgmt.resourcegraph.models.ChangeType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREATE = "Create"
        DELETE = "Delete"
        UPDATE = "Update"


    class azure.mgmt.resourcegraph.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.resourcegraph.models.DateTimeInterval(_Model):
        end: datetime
        start: datetime

        @overload
        def __init__(
                self, 
                *, 
                end: datetime, 
                start: datetime
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resourcegraph.models.Error(_Model):
        code: str
        details: Optional[list[ErrorDetails]]
        message: str

        @overload
        def __init__(
                self, 
                *, 
                code: str, 
                details: Optional[list[ErrorDetails]] = ..., 
                message: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resourcegraph.models.ErrorDetails(_Model):
        code: str
        message: str

        @overload
        def __init__(
                self, 
                *, 
                code: str, 
                message: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resourcegraph.models.ErrorFieldContract(_Model):
        code: Optional[str]
        message: Optional[str]
        target: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                message: Optional[str] = ..., 
                target: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resourcegraph.models.ErrorResponse(_Model):
        error: Error

        @overload
        def __init__(
                self, 
                *, 
                error: Error
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resourcegraph.models.Facet(_Model):
        expression: str
        result_type: str

        @overload
        def __init__(
                self, 
                *, 
                expression: str, 
                result_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resourcegraph.models.FacetError(Facet, discriminator='FacetError'):
        errors: list[ErrorDetails]
        expression: str
        result_type: Literal["FacetError"]

        @overload
        def __init__(
                self, 
                *, 
                errors: list[ErrorDetails], 
                expression: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resourcegraph.models.FacetRequest(_Model):
        expression: str
        options: Optional[FacetRequestOptions]

        @overload
        def __init__(
                self, 
                *, 
                expression: str, 
                options: Optional[FacetRequestOptions] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resourcegraph.models.FacetRequestOptions(_Model):
        filter: Optional[str]
        sort_by: Optional[str]
        sort_order: Optional[Union[str, FacetSortOrder]]
        top: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                filter: Optional[str] = ..., 
                sort_by: Optional[str] = ..., 
                sort_order: Optional[Union[str, FacetSortOrder]] = ..., 
                top: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resourcegraph.models.FacetResult(Facet, discriminator='FacetResult'):
        count: int
        data: Any
        expression: str
        result_type: Literal["FacetResult"]
        total_records: int

        @overload
        def __init__(
                self, 
                *, 
                count: int, 
                data: Any, 
                expression: str, 
                total_records: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resourcegraph.models.FacetSortOrder(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ASC = "asc"
        DESC = "desc"


    class azure.mgmt.resourcegraph.models.GraphQueryError(_Model):
        error: Optional[GraphQueryErrorError]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[GraphQueryErrorError] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resourcegraph.models.GraphQueryErrorError(_Model):
        code: Optional[str]
        details: Optional[list[ErrorFieldContract]]
        message: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                details: Optional[list[ErrorFieldContract]] = ..., 
                message: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resourcegraph.models.GraphQueryProperties(_Model):
        description: Optional[str]
        query: str
        result_kind: Optional[Union[str, ResultKind]]
        time_modified: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                query: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resourcegraph.models.GraphQueryPropertiesUpdateParameters(_Model):
        description: Optional[str]
        query: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                query: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resourcegraph.models.GraphQueryResource(ProxyResource):
        etag: Optional[str]
        id: str
        location: Optional[str]
        name: str
        properties: Optional[GraphQueryProperties]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                location: Optional[str] = ..., 
                properties: Optional[GraphQueryProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.resourcegraph.models.GraphQueryUpdateParameters(_Model):
        etag: Optional[str]
        properties: Optional[GraphQueryPropertiesUpdateParameters]
        tags: Optional[dict[str, str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                properties: Optional[GraphQueryPropertiesUpdateParameters] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.resourcegraph.models.Operation(_Model):
        display: Optional[OperationDisplay]
        name: Optional[str]
        origin: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                display: Optional[OperationDisplay] = ..., 
                name: Optional[str] = ..., 
                origin: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resourcegraph.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                operation: Optional[str] = ..., 
                provider: Optional[str] = ..., 
                resource: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resourcegraph.models.PropertyChangeType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INSERT = "Insert"
        REMOVE = "Remove"
        UPDATE = "Update"


    class azure.mgmt.resourcegraph.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.resourcegraph.models.QueryRequest(_Model):
        facets: Optional[list[FacetRequest]]
        management_groups: Optional[list[str]]
        options: Optional[QueryRequestOptions]
        query: str
        subscriptions: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                facets: Optional[list[FacetRequest]] = ..., 
                management_groups: Optional[list[str]] = ..., 
                options: Optional[QueryRequestOptions] = ..., 
                query: str, 
                subscriptions: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resourcegraph.models.QueryRequestOptions(_Model):
        allow_partial_scopes: Optional[bool]
        authorization_scope_filter: Optional[Union[str, AuthorizationScopeFilter]]
        result_format: Optional[Union[str, ResultFormat]]
        skip: Optional[int]
        skip_token: Optional[str]
        top: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                allow_partial_scopes: Optional[bool] = ..., 
                authorization_scope_filter: Optional[Union[str, AuthorizationScopeFilter]] = ..., 
                result_format: Optional[Union[str, ResultFormat]] = ..., 
                skip: Optional[int] = ..., 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resourcegraph.models.QueryResponse(_Model):
        count: int
        data: Any
        facets: Optional[list[Facet]]
        result_truncated: Union[str, ResultTruncated]
        skip_token: Optional[str]
        total_records: int

        @overload
        def __init__(
                self, 
                *, 
                count: int, 
                data: Any, 
                facets: Optional[list[Facet]] = ..., 
                result_truncated: Union[str, ResultTruncated], 
                skip_token: Optional[str] = ..., 
                total_records: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resourcegraph.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.resourcegraph.models.ResourceChangeData(_Model):
        after_snapshot: ResourceChangeDataAfterSnapshot
        before_snapshot: ResourceChangeDataBeforeSnapshot
        change_id: str
        change_type: Optional[Union[str, ChangeType]]
        property_changes: Optional[list[ResourcePropertyChange]]
        resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                after_snapshot: ResourceChangeDataAfterSnapshot, 
                before_snapshot: ResourceChangeDataBeforeSnapshot, 
                change_id: str, 
                change_type: Optional[Union[str, ChangeType]] = ..., 
                property_changes: Optional[list[ResourcePropertyChange]] = ..., 
                resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resourcegraph.models.ResourceChangeDataAfterSnapshot(ResourceSnapshotData):
        content: any
        snapshot_id: str
        timestamp: datetime

        @overload
        def __init__(
                self, 
                *, 
                content: Optional[Any] = ..., 
                snapshot_id: Optional[str] = ..., 
                timestamp: datetime
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resourcegraph.models.ResourceChangeDataBeforeSnapshot(ResourceSnapshotData):
        content: any
        snapshot_id: str
        timestamp: datetime

        @overload
        def __init__(
                self, 
                *, 
                content: Optional[Any] = ..., 
                snapshot_id: Optional[str] = ..., 
                timestamp: datetime
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resourcegraph.models.ResourceChangeDetailsRequestParameters(_Model):
        change_ids: list[str]
        resource_ids: list[str]

        @overload
        def __init__(
                self, 
                *, 
                change_ids: list[str], 
                resource_ids: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resourcegraph.models.ResourceChangeList(_Model):
        changes: Optional[list[ResourceChangeData]]
        skip_token: Optional[Any]

        @overload
        def __init__(
                self, 
                *, 
                changes: Optional[list[ResourceChangeData]] = ..., 
                skip_token: Optional[Any] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resourcegraph.models.ResourceChangesRequestParameters(_Model):
        fetch_property_changes: Optional[bool]
        fetch_snapshots: Optional[bool]
        interval: ResourceChangesRequestParametersInterval
        resource_ids: Optional[list[str]]
        skip_token: Optional[str]
        subscription_id: Optional[str]
        table: Optional[str]
        top: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                fetch_property_changes: Optional[bool] = ..., 
                fetch_snapshots: Optional[bool] = ..., 
                interval: ResourceChangesRequestParametersInterval, 
                resource_ids: Optional[list[str]] = ..., 
                skip_token: Optional[str] = ..., 
                subscription_id: Optional[str] = ..., 
                table: Optional[str] = ..., 
                top: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resourcegraph.models.ResourceChangesRequestParametersInterval(DateTimeInterval):
        end: datetime
        start: datetime

        @overload
        def __init__(
                self, 
                *, 
                end: datetime, 
                start: datetime
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resourcegraph.models.ResourcePropertyChange(_Model):
        after_value: Optional[str]
        before_value: Optional[str]
        change_category: Union[str, ChangeCategory]
        property_change_type: Union[str, PropertyChangeType]
        property_name: str

        @overload
        def __init__(
                self, 
                *, 
                after_value: Optional[str] = ..., 
                before_value: Optional[str] = ..., 
                change_category: Union[str, ChangeCategory], 
                property_change_type: Union[str, PropertyChangeType], 
                property_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resourcegraph.models.ResourceSnapshotData(_Model):
        content: Optional[Any]
        snapshot_id: Optional[str]
        timestamp: datetime

        @overload
        def __init__(
                self, 
                *, 
                content: Optional[Any] = ..., 
                snapshot_id: Optional[str] = ..., 
                timestamp: datetime
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resourcegraph.models.ResourcesHistoryRequest(_Model):
        management_groups: Optional[list[str]]
        options: Optional[ResourcesHistoryRequestOptions]
        query: Optional[str]
        subscriptions: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                management_groups: Optional[list[str]] = ..., 
                options: Optional[ResourcesHistoryRequestOptions] = ..., 
                query: Optional[str] = ..., 
                subscriptions: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resourcegraph.models.ResourcesHistoryRequestOptions(_Model):
        interval: Optional[DateTimeInterval]
        result_format: Optional[Union[str, ResultFormat]]
        skip: Optional[int]
        skip_token: Optional[str]
        top: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                interval: Optional[DateTimeInterval] = ..., 
                result_format: Optional[Union[str, ResultFormat]] = ..., 
                skip: Optional[int] = ..., 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resourcegraph.models.ResultFormat(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        OBJECT_ARRAY = "objectArray"
        TABLE = "table"


    class azure.mgmt.resourcegraph.models.ResultKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BASIC = "basic"


    class azure.mgmt.resourcegraph.models.ResultTruncated(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FALSE = "false"
        TRUE = "true"


    class azure.mgmt.resourcegraph.models.SystemData(_Model):
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


namespace azure.mgmt.resourcegraph.operations

    class azure.mgmt.resourcegraph.operations.GraphQueryOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                properties: GraphQueryResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GraphQueryResource: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GraphQueryResource: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GraphQueryResource: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> GraphQueryResource: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[GraphQueryResource]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[GraphQueryResource]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                body: GraphQueryUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GraphQueryResource: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GraphQueryResource: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GraphQueryResource: ...


    class azure.mgmt.resourcegraph.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


```