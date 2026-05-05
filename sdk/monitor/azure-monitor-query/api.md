```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.monitor.query

    class azure.monitor.query.LogsBatchQuery:

        def __init__(
                self, 
                workspace_id: str, 
                query: str, 
                *, 
                additional_workspaces: Optional[list[str]] = ..., 
                include_statistics: Optional[bool] = ..., 
                include_visualization: Optional[bool] = ..., 
                server_timeout: Optional[int] = ..., 
                timespan: Optional[Union[timedelta, Tuple[datetime, timedelta], Tuple[datetime, datetime]]], 
                **kwargs: Any
            ) -> None: ...


    class azure.monitor.query.LogsQueryClient(GeneratedClient): implements ContextManager 

        def __init__(
                self, 
                credential: TokenCredential, 
                *, 
                api_version: str = ..., 
                audience: str = ..., 
                endpoint: str = ..., 
                **kwargs: Any
            ) -> None: ...

        def close(self) -> None: ...

        @distributed_trace
        def query_batch(
                self, 
                queries: Union[Sequence[Dict], Sequence[LogsBatchQuery]], 
                **kwargs: Any
            ) -> List[Union[LogsQueryResult, LogsQueryError, LogsQueryPartialResult]]: ...

        @distributed_trace
        def query_resource(
                self, 
                resource_id: str, 
                query: str, 
                *, 
                additional_workspaces: Optional[Sequence[str]] = ..., 
                include_statistics: bool = False, 
                include_visualization: bool = False, 
                server_timeout: Optional[int] = ..., 
                timespan: Optional[Union[timedelta, Tuple[datetime, timedelta], Tuple[datetime, datetime]]], 
                **kwargs: Any
            ) -> Union[LogsQueryResult, LogsQueryPartialResult]: ...

        @distributed_trace
        def query_workspace(
                self, 
                workspace_id: str, 
                query: str, 
                *, 
                additional_workspaces: Optional[Sequence[str]] = ..., 
                include_statistics: bool = False, 
                include_visualization: bool = False, 
                server_timeout: Optional[int] = ..., 
                timespan: Optional[Union[timedelta, Tuple[datetime, timedelta], Tuple[datetime, datetime]]], 
                **kwargs: Any
            ) -> Union[LogsQueryResult, LogsQueryPartialResult]: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> HttpResponse: ...


    class azure.monitor.query.LogsQueryError:
        code: str
        details: Optional[List[Mapping[str, Any]]]
        message: str
        status: Literal[LogsQueryStatus.FAILURE]

        def __init__(self, **kwargs: Any) -> None: ...

        def __str__(self) -> str: ...


    class azure.monitor.query.LogsQueryPartialResult:
        partial_data: List[LogsTable]
        partial_error: Optional[LogsQueryError]
        statistics: Optional[Mapping[str, Any]]
        status: Literal[LogsQueryStatus.PARTIAL]
        visualization: Optional[Mapping[str, Any]]

        def __init__(self, **kwargs: Any) -> None: ...

        def __iter__(self) -> Iterator[LogsTable]: ...


    class azure.monitor.query.LogsQueryResult:
        statistics: Optional[Mapping[str, Any]]
        status: Literal[LogsQueryStatus.SUCCESS]
        tables: List[LogsTable]
        visualization: Optional[Mapping[str, Any]]

        def __init__(self, **kwargs: Any) -> None: ...

        def __iter__(self) -> Iterator[LogsTable]: ...


    class azure.monitor.query.LogsQueryStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAILURE = "Failure"
        PARTIAL = "PartialError"
        SUCCESS = "Success"


    class azure.monitor.query.LogsTable:
        columns: List[str]
        columns_types: List[str]
        name: str
        rows: List[LogsTableRow]

        def __init__(self, **kwargs: Any) -> None: ...


    class azure.monitor.query.LogsTableRow:
        index: int

        def __getitem__(self, column: Union[str, int]) -> Any: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __iter__(self) -> Iterator[Any]: ...

        def __len__(self) -> int: ...

        def __repr__(self) -> str: ...


    class azure.monitor.query.MonitorQueryLogsClient(_MonitorQueryLogsClientOperationsMixin): implements ContextManager 

        def __init__(
                self, 
                credential: TokenCredential, 
                *, 
                api_version: Union[str, Versions] = ..., 
                endpoint: str = "https://api.loganalytics.io", 
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


namespace azure.monitor.query.aio

    class azure.monitor.query.aio.LogsQueryClient(GeneratedClient): implements AsyncContextManager 

        def __init__(
                self, 
                credential: AsyncTokenCredential, 
                *, 
                api_version: str = ..., 
                audience: str = ..., 
                endpoint: str = ..., 
                **kwargs: Any
            ) -> None: ...

        async def close(self) -> None: ...

        @distributed_trace_async
        async def query_batch(
                self, 
                queries: Union[Sequence[Dict], Sequence[LogsBatchQuery]], 
                **kwargs: Any
            ) -> List[Union[LogsQueryResult, LogsQueryError, LogsQueryPartialResult]]: ...

        @distributed_trace_async
        async def query_resource(
                self, 
                resource_id: str, 
                query: str, 
                *, 
                additional_workspaces: Optional[Sequence[str]] = ..., 
                include_statistics: bool = False, 
                include_visualization: bool = False, 
                server_timeout: Optional[int] = ..., 
                timespan: Optional[Union[timedelta, Tuple[datetime, timedelta], Tuple[datetime, datetime]]], 
                **kwargs: Any
            ) -> Union[LogsQueryResult, LogsQueryPartialResult]: ...

        @distributed_trace_async
        async def query_workspace(
                self, 
                workspace_id: str, 
                query: str, 
                *, 
                additional_workspaces: Optional[Sequence[str]] = ..., 
                include_statistics: bool = False, 
                include_visualization: bool = False, 
                server_timeout: Optional[int] = ..., 
                timespan: Optional[Union[timedelta, Tuple[datetime, timedelta], Tuple[datetime, datetime]]], 
                **kwargs: Any
            ) -> Union[LogsQueryResult, LogsQueryPartialResult]: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> Awaitable[AsyncHttpResponse]: ...


    class azure.monitor.query.aio.MonitorQueryLogsClient(_MonitorQueryLogsClientOperationsMixin): implements AsyncContextManager 

        def __init__(
                self, 
                credential: AsyncTokenCredential, 
                *, 
                api_version: Union[str, Versions] = ..., 
                endpoint: str = "https://api.loganalytics.io", 
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


```