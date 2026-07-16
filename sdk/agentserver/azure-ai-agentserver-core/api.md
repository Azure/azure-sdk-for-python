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


    def azure.ai.agentserver.core.read_request_id(scope: Mapping[str, Any]) -> str | None: ...


    def azure.ai.agentserver.core.record_error(span: Any, exc: BaseException) -> None: ...


    def azure.ai.agentserver.core.reset_request_context(token: Token[FoundryAgentRequestContext]) -> None: ...


    def azure.ai.agentserver.core.resolve_state_subdir(name: str) -> Path: ...


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


    class azure.ai.agentserver.core.tasks.InputTooLarge(ValueError):

        def __init__(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.agentserver.core.tasks.LastInputIdPreconditionFailed(TaskPreconditionFailed):

        def __init__(
                self, 
                *args: Any, 
                *, 
                actual_last_input_id: str | None = ..., 
                expected_last_input_id: str | None = ..., 
                task_id: str | None = ..., 
            ) -> None: ...


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
            ) -> Any: ...

        async def start(
                self, 
                *, 
                if_last_input_id: str | None = ..., 
                input: Any, 
                input_id: str | None = ..., 
                task_id: str
            ) -> TaskRun[Output]: ...


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


    class azure.ai.agentserver.core.tasks.SteeringQueueFull(RuntimeError):

        def __init__(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...


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


    class azure.ai.agentserver.core.tasks.TaskCancelled(Exception):

        def __init__(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...

        def __str__(self) -> str: ...


    class azure.ai.agentserver.core.tasks.TaskConflictError(RuntimeError):

        def __init__(
                self, 
                *args: Any, 
                *, 
                current_status: str | None = ..., 
            ) -> None: ...


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
                metadata: TaskMetadata, 
                pending_count_provider: Callable[[], int] | None = ..., 
                recovery_count: int = 0, 
                retry_attempt: int = 0, 
                session_id: str, 
                shutdown: Event | None = ..., 
                task_id: str
            ) -> None: ...

        async def exit_for_recovery(self) -> Any: ...


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


    class azure.ai.agentserver.core.tasks.TaskFailed(Exception):
        error: Union[TaskErrorDict, TaskExhaustedRetriesErrorDict]

        def __init__(
                self, 
                *args: Any, 
                *, 
                error: dict[str, Any] | None = ..., 
            ) -> None: ...


    class azure.ai.agentserver.core.tasks.TaskManagerNotInitialized(RuntimeError):


    class azure.ai.agentserver.core.tasks.TaskMetadata(MutableMapping): implements Collection 

        def __call__(self, name: Optional[str] = None) -> TaskMetadata: ...

        def __delitem__(self, key: str) -> None: ...

        def __getitem__(self, key: str) -> Any: ...

        def __init__(
                self, 
                initial: dict[str, Any] | None = None, 
                *, 
                _namespace_name: Optional[str] = ..., 
                _registry: dict[Optional[str], TaskMetadata] | None = ..., 
                flush_callback: NamespaceFlushCallback | None = ...
            ) -> None: ...

        def __setitem__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...

        @classmethod
        def from_payload(
                cls, 
                payload: dict[str, Any] | None, 
                *, 
                flush_callback: NamespaceFlushCallback | None = ...
            ) -> TaskMetadata: ...

        def append(
                self, 
                key: str, 
                value: Any
            ) -> None: ...

        async def flush(self) -> None: ...

        def get(
                self, 
                key: str, 
                default: Any = None
            ) -> Any: ...

        def increment(
                self, 
                key: str, 
                delta: int = 1
            ) -> None: ...

        def items(self) -> ItemsView[str, Any]: ...

        def keys(self) -> KeysView[str]: ...

        def set(
                self, 
                key: str, 
                value: Any
            ) -> None: ...

        def to_dict(self) -> dict[str, Any]: ...

        def values(self) -> ValuesView[Any]: ...


    class azure.ai.agentserver.core.tasks.TaskRun(Generic[Output]): implements Awaitable 
        property is_queued: bool    # Read-only
        property metadata: TaskMetadata    # Read-only

        def __init__(
                self, 
                task_id: str, 
                *, 
                cancel_ctx_ref: Any = ..., 
                cancel_event: Event | None = ..., 
                execution_task: Task[Any] | None = ..., 
                input_id: str | None = ..., 
                lease_expiry_count: int = 0, 
                metadata: TaskMetadata | None = ..., 
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