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


    @overload
    def azure.ai.agentserver.core.experimental(wrapped: type[T]) -> type[T]: ...


    @overload
    def azure.ai.agentserver.core.experimental(wrapped: Callable[P, T]) -> Callable[P, T]: ...


    def azure.ai.agentserver.core.flush_spans(timeout_millis: int = 5000) -> None: ...


    def azure.ai.agentserver.core.get_request_context() -> FoundryAgentRequestContext: ...


    def azure.ai.agentserver.core.read_request_id(scope: Mapping[str, Any]) -> str | None: ...


    def azure.ai.agentserver.core.record_error(span: Any, exc: BaseException) -> None: ...


    def azure.ai.agentserver.core.reset_request_context(token: Token[FoundryAgentRequestContext]) -> None: ...


    def azure.ai.agentserver.core.resolve_state_subdir(name: str) -> Path: ...


    def azure.ai.agentserver.core.set_current_span(span: Any) -> Any: ...


    def azure.ai.agentserver.core.set_request_context(context: FoundryAgentRequestContext) -> Token[FoundryAgentRequestContext]: ...


    async def azure.ai.agentserver.core.trace_stream:async(iterator: AsyncIterable[StreamContent], span: Any) -> AsyncIterator[StreamContent]: ...


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

        def add_middleware(
                self, 
                middleware_class: MiddlewareFactory[P], 
                *args: args, 
                **kwargs: kwargs
            ) -> None: ...

        def register_pre_shutdown_callback(self, fn: Callable[[], None]) -> None: ...

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


    @experimental
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
                call_id: str | None = ...,
                tags: Mapping[str, str] | None = ...
            ) -> StateStoreItemRef: ...

        async def delete(self) -> DeletedStateStore: ...

        async def delete_item(
                self,
                key: str,
                *,
                call_id: str | None = ...,
                if_match: str | None = ...
            ) -> DeletedStateStoreItem: ...

        async def get(self) -> StateStore: ...

        async def get_item(
                self,
                key: str,
                *,
                call_id: str | None = ...
            ) -> StateStoreItem | None: ...

        async def list_keys(
                self, 
                *, 
                after: str | None = ..., 
                before: str | None = ..., 
                call_id: str | None = ...,
                limit: int | None = ..., 
                order: Order = "desc", 
                tags: Mapping[str, str] | None = ...
            ) -> StateStoreItemKeyPage: ...

        async def set_item(
                self, 
                key: str, 
                value: JSONObject, 
                *, 
                call_id: str | None = ...,
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


    @experimental
    class azure.ai.agentserver.core.storage.FoundryStorageApiError(FoundryStorageError):

        def __init__(
                self, 
                message: str, 
                *, 
                response_body: dict[str, Any] | None = ..., 
                status_code: int | None = ...
            ) -> None: ...


    @experimental
    class azure.ai.agentserver.core.storage.FoundryStorageBadRequestError(FoundryStorageError):

        def __init__(
                self, 
                message: str, 
                *, 
                param: str | None = ..., 
                response_body: dict[str, Any] | None = ..., 
                status_code: int | None = ...
            ) -> None: ...


    @experimental
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


    @experimental
    class azure.ai.agentserver.core.storage.FoundryStorageConflictError(FoundryStorageBadRequestError):

        def __init__(
                self, 
                message: str, 
                *, 
                param: str | None = ..., 
                response_body: dict[str, Any] | None = ..., 
                status_code: int | None = ...
            ) -> None: ...


    @experimental
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


    @experimental
    class azure.ai.agentserver.core.storage.FoundryStorageError(Exception):

        def __init__(
                self, 
                message: str, 
                *, 
                response_body: dict[str, Any] | None = ..., 
                status_code: int | None = ...
            ) -> None: ...


    @experimental
    class azure.ai.agentserver.core.storage.FoundryStorageNotFoundError(FoundryStorageError):

        def __init__(
                self, 
                message: str, 
                *, 
                response_body: dict[str, Any] | None = ..., 
                status_code: int | None = ...
            ) -> None: ...


    @experimental
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


namespace azure.ai.agentserver.core.streaming

    @runtime_checkable
    class azure.ai.agentserver.core.streaming.EventStream(Protocol):

        async def close(self) -> None: ...

        async def emit(
                self, 
                payload: Any, 
                *, 
                close: bool = False
            ) -> None: ...

        async def last_cursor(self) -> Optional[int]: ...

        def subscribe(
                self, 
                *, 
                after: Optional[int] = ...
            ) -> AsyncIterator[Any]: ...


    class azure.ai.agentserver.core.streaming.EventStreamClosedError(EventStreamError):


    class azure.ai.agentserver.core.streaming.EventStreamError(Exception):


    class azure.ai.agentserver.core.streaming.EventStreamNotFoundError(EventStreamError):


namespace azure.ai.agentserver.core.tasks

    @overload
    def azure.ai.agentserver.core.tasks.multi_turn_task(
            fn: Callable[[TaskContext[Input]], Awaitable[Output]], 
            *, 
            name: str, 
            retry: RetryPolicy | None = Ellipsis, 
            steerable: bool = Ellipsis, 
            timeout: timedelta | None = Ellipsis, 
            title: str | None = Ellipsis
        ) -> MultiTurnTask[Input, Output]: ...


    @overload
    def azure.ai.agentserver.core.tasks.multi_turn_task(
            *, 
            name: str, 
            retry: RetryPolicy | None = Ellipsis, 
            steerable: bool = Ellipsis, 
            timeout: timedelta | None = Ellipsis, 
            title: str | None = Ellipsis
        ) -> Callable[[Callable[[TaskContext[Input]], Awaitable[Output]]], MultiTurnTask[Input, Output]]: ...


    @experimental
    def azure.ai.agentserver.core.tasks.resilient_tasks_enabled() -> bool: ...


    @experimental
    def azure.ai.agentserver.core.tasks.set_resilient_tasks_enabled(value: bool = True) -> None: ...


    @overload
    def azure.ai.agentserver.core.tasks.task(
            fn: Callable[[TaskContext[Input]], Awaitable[Output]], 
            *, 
            name: str, 
            retry: RetryPolicy | None = Ellipsis, 
            timeout: timedelta | None = Ellipsis, 
            title: str | None = Ellipsis
        ) -> Task[Input, Output]: ...


    @overload
    def azure.ai.agentserver.core.tasks.task(
            *, 
            name: str, 
            retry: RetryPolicy | None = Ellipsis, 
            timeout: timedelta | None = Ellipsis, 
            title: str | None = Ellipsis
        ) -> Callable[[Callable[[TaskContext[Input]], Awaitable[Output]]], Task[Input, Output]]: ...


    @experimental
    class azure.ai.agentserver.core.tasks.InputTooLarge(ValueError):

        def __init__(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...


    @experimental
    class azure.ai.agentserver.core.tasks.LastInputIdPreconditionFailed(TaskPreconditionFailed):

        def __init__(
                self, 
                *args: Any, 
                *, 
                actual_last_input_id: str | None = ..., 
                expected_last_input_id: str | None = ..., 
                task_id: str | None = ..., 
            ) -> None: ...


    @experimental
    class azure.ai.agentserver.core.tasks.MultiTurnTask(Generic[Input, Output]):
        property name: str    # Read-only

        def __init__(
                self, 
                fn: Callable[, Any], 
                opts: TaskOptions, 
                input_type: type | None = None, 
                output_type: type | None = None
            ) -> None: ...

        async def delete(self, task_id: str) -> None: ...

        async def get_active_run(
                self, 
                task_id: str, 
                input_id: str
            ) -> TaskRun[Output] | None: ...

        async def run(
                self, 
                *, 
                if_last_input_id: str | None = ..., 
                input: Any, 
                input_id: str | None = ..., 
                task_id: str
            ) -> Output: ...

        async def start(
                self, 
                *, 
                if_last_input_id: str | None = ..., 
                input: Any, 
                input_id: str | None = ..., 
                task_id: str
            ) -> TaskRun[Output]: ...


    @experimental
    class azure.ai.agentserver.core.tasks.RetryPolicy:

        def __eq__(self, other: object) -> bool: ...

        def __init__(
                self, 
                *, 
                _linear: bool = False, 
                backoff_coefficient: float = 2.0, 
                initial_delay: timedelta | float = timedelta(seconds=1), 
                jitter: bool | float = True, 
                max_attempts: int = 3, 
                max_delay: timedelta | float = timedelta(seconds=60), 
                retry_on: type[Exception] | tuple[type[Exception], ] | None = ...
            ) -> None: ...

        def __repr__(self) -> str: ...

        @classmethod
        def exponential_backoff(
                cls, 
                *, 
                backoff_coefficient: float = 2.0, 
                initial_delay: timedelta = timedelta(seconds=1), 
                jitter: bool = True, 
                max_attempts: int = 3, 
                max_delay: timedelta = timedelta(seconds=60)
            ) -> RetryPolicy: ...

        @classmethod
        def fixed_delay(
                cls, 
                *, 
                delay: timedelta = timedelta(seconds=5), 
                max_attempts: int = 3
            ) -> RetryPolicy: ...

        @classmethod
        def linear_backoff(
                cls, 
                *, 
                initial_delay: timedelta = timedelta(seconds=1), 
                max_attempts: int = 5, 
                max_delay: timedelta = timedelta(seconds=60)
            ) -> RetryPolicy: ...

        @classmethod
        def no_retry(cls) -> RetryPolicy: ...

        def compute_delay(self, attempt: int) -> float: ...

        def should_retry(
                self, 
                attempt: int, 
                error: Exception
            ) -> bool: ...


    @experimental
    class azure.ai.agentserver.core.tasks.SteeringQueueFull(RuntimeError):

        def __init__(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...


    @experimental
    class azure.ai.agentserver.core.tasks.Task(Generic[Input, Output]):

        def __init__(
                self, 
                fn: Callable[[TaskContext[Input]], Awaitable[Output]], 
                opts: TaskOptions, 
                input_type: type[Input], 
                output_type: type[Output]
            ) -> None: ...

        async def get_active_run(self, task_id: str) -> TaskRun[Output] | None: ...

        async def run(
                self, 
                *, 
                if_last_input_id: str | None = ..., 
                input: Input, 
                input_id: str | None = ..., 
                task_id: str | None = ...
            ) -> Output: ...

        async def start(
                self, 
                *, 
                if_last_input_id: str | None = ..., 
                input: Input, 
                input_id: str | None = ..., 
                task_id: str | None = ...
            ) -> TaskRun[Output]: ...


    @experimental
    class azure.ai.agentserver.core.tasks.TaskCancelled(Exception):

        def __init__(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...

        def __str__(self) -> str: ...


    @experimental
    class azure.ai.agentserver.core.tasks.TaskConflictError(RuntimeError):

        def __init__(
                self, 
                *args: Any, 
                *, 
                current_status: str | None = ..., 
            ) -> None: ...


    @experimental
    class azure.ai.agentserver.core.tasks.TaskContext(Generic[Input]):
        property pending_input_count: int    # Read-only

        def __init__(
                self, 
                *, 
                cancel: Event | None = ..., 
                entry_mode: EntryMode = "fresh", 
                input: Input, 
                input_id: str | None = ..., 
                is_steered_turn: bool = False, 
                pending_count_provider: Callable[[], int] | None = ..., 
                recovery_count: int = 0, 
                retry_attempt: int = 0, 
                session_id: str, 
                shutdown: Event | None = ..., 
                task_id: str
            ) -> None: ...

        async def exit_for_recovery(self) -> Any: ...


    @experimental
    class azure.ai.agentserver.core.tasks.TaskDeferred(Exception):

        def __init__(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.agentserver.core.tasks.TaskErrorDict(TypedDict):
        key "message": str
        key "traceback": str
        key "type": str


    class azure.ai.agentserver.core.tasks.TaskExhaustedRetriesErrorDict(TypedDict):
        key "attempts": int
        key "last_error": str
        key "last_error_type": str
        key "traceback": str
        key "type": Literal["exhausted_retries"]


    @experimental
    class azure.ai.agentserver.core.tasks.TaskFailed(Exception):
        error: Union[TaskErrorDict, TaskExhaustedRetriesErrorDict]

        def __init__(
                self, 
                *args: Any, 
                *, 
                error: dict[str, Any] | None = ..., 
            ) -> None: ...


    @experimental
    class azure.ai.agentserver.core.tasks.TaskManagerNotInitialized(RuntimeError):


    @experimental
    class azure.ai.agentserver.core.tasks.TaskRun(Generic[Output]): implements Awaitable 
        property is_queued: bool    # Read-only

        def __init__(
                self, 
                task_id: str, 
                *, 
                cancel_ctx_ref: Any = ..., 
                cancel_event: Event | None = ..., 
                execution_task: Task[Any] | None = ..., 
                input_id: str | None = ..., 
                lease_expiry_count: int = 0, 
                provider: Any = ..., 
                queued_cancel_callback: Any = ..., 
                result_future: Future[Any], 
                status: Any = ..., 
                terminate_event: Event | None = ..., 
                terminate_reason_ref: list[str | None] | None = ...
            ) -> None: ...

        async def cancel(self) -> None: ...

        async def result(self) -> Output: ...


```