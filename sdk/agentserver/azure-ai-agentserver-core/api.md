```py
namespace azure.ai.agentserver.core

    def azure.ai.agentserver.core.build_server_version(sdk_name: str, version: str) -> str: ...


    def azure.ai.agentserver.core.configure_observability(
            *, 
            connection_string: Optional[str] = ..., 
            enable_sensitive_data: bool = False, 
            log_level: Optional[str] = ...
        ) -> None: ...


    def azure.ai.agentserver.core.create_error_response(
            code: str, 
            message: str, 
            *, 
            details: Optional[list[dict[str, Any]]] = ..., 
            error_type: Optional[str] = ..., 
            headers: Optional[dict[str, str]] = ..., 
            status_code: int
        ) -> JSONResponse: ...


    def azure.ai.agentserver.core.detach_context(token: Any) -> None: ...


    def azure.ai.agentserver.core.end_span(span: Any, exc: Optional[BaseException] = None) -> None: ...


    def azure.ai.agentserver.core.flush_spans(timeout_millis: int = 5000) -> None: ...


    def azure.ai.agentserver.core.get_request_context() -> FoundryAgentRequestContext: ...


    def azure.ai.agentserver.core.record_error(span: Any, exc: BaseException) -> None: ...


    def azure.ai.agentserver.core.reset_request_context(token: Token[FoundryAgentRequestContext]) -> None: ...


    def azure.ai.agentserver.core.set_current_span(span: Any) -> Any: ...


    def azure.ai.agentserver.core.set_request_context(context: FoundryAgentRequestContext) -> Token[FoundryAgentRequestContext]: ...


    async def azure.ai.agentserver.core.trace_stream:async(iterator: AsyncIterable[_Content], span: Any) -> AsyncIterator[_Content]: ...


    class azure.ai.agentserver.core.AgentConfig:

        def __init__(
                self, 
                *, 
                agent_guid: str = "", 
                agent_id: str, 
                agent_name: str, 
                agent_version: str, 
                appinsights_connection_string: str, 
                is_hosted: bool, 
                otlp_endpoint: str, 
                port: int, 
                project_endpoint: str, 
                project_id: str, 
                session_id: str, 
                sse_keepalive_interval: int, 
                ws_ping_interval: float = 0.0
            ) -> None: ...

        @classmethod
        def from_env(cls) -> Self: ...


    class azure.ai.agentserver.core.AgentServerHost(Starlette):
        property routes: list[BaseRoute]    # Read-only

        def __init__(
                self, 
                *, 
                access_log: Optional[Logger] = _SENTINEL_ACCESS_LOG, 
                access_log_format: Optional[str] = ..., 
                applicationinsights_connection_string: Optional[str] = ..., 
                configure_observability: Optional[Callable[, None]] = _tracing.configure_observability, 
                graceful_shutdown_timeout: Optional[int] = ..., 
                log_level: Optional[str] = ..., 
                routes: Optional[list[Route]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def register_server_version(self, version_segment: str) -> None: ...

        def run(
                self, 
                host: str = "0.0.0.0", 
                port: Optional[int] = None
            ) -> None: ...

        async def run_async(
                self, 
                host: str = "0.0.0.0", 
                port: Optional[int] = None
            ) -> None: ...

        def shutdown_handler(self, fn: Callable[[], Awaitable[None]]) -> Callable[[], Awaitable[None]]: ...

        @staticmethod
        async def sse_keepalive_stream(iterator: AsyncIterable[_Content], interval: int) -> AsyncIterator[_Content]: ...


    class azure.ai.agentserver.core.FoundryAgentRequestContext:
        call_id: str | None
        session_id: str | None
        user_id: str | None

        def __init__(
                self, 
                *, 
                call_id: str | None = ..., 
                session_id: str | None = ..., 
                user_id: str | None = ...
            ) -> None: ...

        def platform_headers(self) -> dict[str, str]: ...


    class azure.ai.agentserver.core.InboundRequestLoggingMiddleware:

        async def __call__(
                self, 
                scope: Scope, 
                receive: Receive, 
                send: Send
            ) -> None: ...

        def __init__(self, app: ASGIApp) -> None: ...


    class azure.ai.agentserver.core.RequestIdMiddleware:

        async def __call__(
                self, 
                scope: Scope, 
                receive: Receive, 
                send: Send
            ) -> None: ...

        def __init__(self, app: ASGIApp) -> None: ...


namespace azure.ai.agentserver.core.storage

    class azure.ai.agentserver.core.storage.DeletedStateStore(_Model):
        deleted: bool
        id: Optional[str]
        name: str
        object: Literal[StateStoreObjectType.STATE_STORE]

        @overload
        def __init__(
                self, 
                *, 
                deleted: bool, 
                id: Optional[str] = ..., 
                name: str, 
                object: Literal[StateStoreObjectType.STATE_STORE]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.core.storage.DeletedStateStoreItem(_Model):
        deleted: bool
        id: Optional[str]
        key: str
        object: Literal[StateStoreItemObjectType.STATE_STORE_ITEM]

        @overload
        def __init__(
                self, 
                *, 
                deleted: bool, 
                id: Optional[str] = ..., 
                key: str, 
                object: Literal[StateStoreItemObjectType.STATE_STORE_ITEM]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.core.storage.FoundryStateStore(FoundryStorageClient): implements AsyncContextManager 
        property name: str    # Read-only

        def __init__(
                self, 
                name: str, 
                credential: AsyncTokenCredential | None = None, 
                endpoint: FoundryStorageEndpoint | str | None = None, 
                *, 
                api_version: str = "v1", 
                description: str | None = ..., 
                item_ttl_seconds: int = DEFAULT_ITEM_TTL_SECONDS, 
                tags: Mapping[str, str] | None = ..., 
                user_id: str | None = ..., 
                user_isolation: bool = False, 
                **kwargs: Any
            ) -> None: ...

        @classmethod
        async def get_or_create(
                cls, 
                name: str, 
                credential: AsyncTokenCredential | None = None, 
                endpoint: FoundryStorageEndpoint | str | None = None, 
                *, 
                api_version: str = "v1", 
                description: str | None = ..., 
                item_ttl_seconds: int = DEFAULT_ITEM_TTL_SECONDS, 
                tags: Mapping[str, str] | None = ..., 
                user_id: str | None = ..., 
                user_isolation: bool = False, 
                **kwargs: Any
            ) -> FoundryStateStore: ...

        async def aclose(self) -> None: ...

        async def create_item(
                self, 
                key: str, 
                value: JSONObject, 
                *, 
                tags: Mapping[str, str] | None = ...
            ) -> StateStoreItemRef: ...

        async def delete(self) -> DeletedStateStore: ...

        async def delete_item(
                self, 
                key: str, 
                *, 
                if_match: str | None = ...
            ) -> DeletedStateStoreItem: ...

        async def get(self) -> StateStore: ...

        async def get_item(self, key: str) -> StateStoreItem | None: ...

        async def list_keys(
                self, 
                *, 
                after: str | None = ..., 
                before: str | None = ..., 
                limit: int | None = ..., 
                order: Order = "desc", 
                tags: Mapping[str, str] | None = ...
            ) -> StateStoreItemKeyPage: ...

        async def set_item(
                self, 
                key: str, 
                value: JSONObject, 
                *, 
                if_match: str | None = ..., 
                require_exists: bool = False, 
                tags: Mapping[str, str] | None = ...
            ) -> StateStoreItemRef: ...

        async def update(
                self, 
                *, 
                description: str | None | object = _UNSET, 
                tags: Mapping[str, str] | None | object = _UNSET
            ) -> StateStore: ...


    class azure.ai.agentserver.core.storage.FoundryStorageApiError(FoundryStorageError):

        def __init__(
                self, 
                message: str, 
                *, 
                response_body: dict[str, Any] | None = ..., 
                status_code: int | None = ...
            ) -> None: ...


    class azure.ai.agentserver.core.storage.FoundryStorageBadRequestError(FoundryStorageError):

        def __init__(
                self, 
                message: str, 
                *, 
                param: str | None = ..., 
                response_body: dict[str, Any] | None = ..., 
                status_code: int | None = ...
            ) -> None: ...


    class azure.ai.agentserver.core.storage.FoundryStorageClient: implements AsyncContextManager 

        def __init__(
                self, 
                credential: AsyncTokenCredential, 
                endpoint: FoundryStorageEndpoint, 
                *, 
                get_server_version: Callable[[], str] | None = ..., 
                sdk_moniker: str | None = ..., 
                **kwargs: Any
            ) -> None: ...

        async def aclose(self) -> None: ...


    class azure.ai.agentserver.core.storage.FoundryStorageConflictError(FoundryStorageBadRequestError):

        def __init__(
                self, 
                message: str, 
                *, 
                param: str | None = ..., 
                response_body: dict[str, Any] | None = ..., 
                status_code: int | None = ...
            ) -> None: ...


    class azure.ai.agentserver.core.storage.FoundryStorageEndpoint:

        def __init__(
                self, 
                *, 
                api_version: str = _DEFAULT_API_VERSION, 
                storage_base_url: str
            ) -> None: ...

        @classmethod
        def from_endpoint(
                cls, 
                endpoint: str, 
                *, 
                api_version: str = _DEFAULT_API_VERSION
            ) -> FoundryStorageEndpoint: ...

        @classmethod
        def from_env(
                cls, 
                *, 
                api_version: str = _DEFAULT_API_VERSION
            ) -> FoundryStorageEndpoint: ...

        def build_url(
                self, 
                path: str, 
                **extra_params: str
            ) -> str: ...


    class azure.ai.agentserver.core.storage.FoundryStorageError(Exception):

        def __init__(
                self, 
                message: str, 
                *, 
                response_body: dict[str, Any] | None = ..., 
                status_code: int | None = ...
            ) -> None: ...


    class azure.ai.agentserver.core.storage.FoundryStorageNotFoundError(FoundryStorageError):

        def __init__(
                self, 
                message: str, 
                *, 
                response_body: dict[str, Any] | None = ..., 
                status_code: int | None = ...
            ) -> None: ...


    class azure.ai.agentserver.core.storage.FoundryStoragePreconditionError(FoundryStorageError):

        def __init__(
                self, 
                message: str, 
                *, 
                current_etag: str | None = ..., 
                response_body: dict[str, Any] | None = ..., 
                status_code: int | None = ...
            ) -> None: ...


    class azure.ai.agentserver.core.storage.StateStore(_Model):
        created_at: int
        description: Optional[str]
        id: str
        item_ttl_seconds: int
        name: str
        object: Literal[StateStoreObjectType.STATE_STORE]
        tags: Optional[dict[str, str]]
        updated_at: int
        user_isolation: bool

        @overload
        def __init__(
                self, 
                *, 
                created_at: int, 
                description: Optional[str] = ..., 
                id: str, 
                item_ttl_seconds: int, 
                name: str, 
                object: Literal[StateStoreObjectType.STATE_STORE], 
                tags: Optional[dict[str, str]] = ..., 
                updated_at: int, 
                user_isolation: bool
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.core.storage.StateStoreItem(_Model):
        created_at: int
        etag: str
        id: str
        key: str
        object: Literal[StateStoreItemObjectType.STATE_STORE_ITEM]
        tags: Optional[dict[str, str]]
        updated_at: int
        value: dict[str, Any]

        @overload
        def __init__(
                self, 
                *, 
                created_at: int, 
                etag: str, 
                id: str, 
                key: str, 
                object: Literal[StateStoreItemObjectType.STATE_STORE_ITEM], 
                tags: Optional[dict[str, str]] = ..., 
                updated_at: int, 
                value: dict[str, Any]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.core.storage.StateStoreItemKey(_Model):
        created_at: int
        etag: str
        id: str
        key: str
        object: Literal[StateStoreItemObjectType.STATE_STORE_ITEM]
        tags: Optional[dict[str, str]]
        updated_at: int

        @overload
        def __init__(
                self, 
                *, 
                created_at: int, 
                etag: str, 
                id: str, 
                key: str, 
                object: Literal[StateStoreItemObjectType.STATE_STORE_ITEM], 
                tags: Optional[dict[str, str]] = ..., 
                updated_at: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    @dataclass(eq = True, frozen = False, init = True, kw_only = False, match_args = True, order = False, repr = True, slots = False, unsafe_hash = False, weakref_slot = False)
    class azure.ai.agentserver.core.storage.StateStoreItemKeyPage:
        first_id: Optional[str]
        has_more: bool = field(compare = True, default = False, hash = None, init = True, kw_only = False, metadata = {}, name = "has_more", repr = True, type = "bool")
        keys: list[StateStoreItemKey]
        last_id: Optional[str]

        def __eq__() -> None: ...

        def __init__(
                keys: list, 
                first_id: str | None, 
                last_id: str | None, 
                has_more: bool
            ): ...

        def __repr__() -> None: ...


    class azure.ai.agentserver.core.storage.StateStoreItemRef(_Model):
        created_at: int
        etag: str
        id: str
        key: str
        object: Literal[StateStoreItemObjectType.STATE_STORE_ITEM]
        updated_at: int

        @overload
        def __init__(
                self, 
                *, 
                created_at: int, 
                etag: str, 
                id: str, 
                key: str, 
                object: Literal[StateStoreItemObjectType.STATE_STORE_ITEM], 
                updated_at: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


```