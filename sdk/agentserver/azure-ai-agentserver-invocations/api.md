```py
namespace azure.ai.agentserver.invocations

    class azure.ai.agentserver.invocations.InvocationAgentServerHost(_WSHandlerMixin, AgentServerHost):
        property routes: list[BaseRoute]    # Read-only
        property ws_ping_interval: float    # Read-only

        def __init__(
                self, 
                *, 
                asyncapi_spec_json: Optional[dict[str, Any]] = ..., 
                asyncapi_spec_yaml: Optional[str] = ..., 
                openapi_spec: Optional[dict[str, Any]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def cancel_invocation_handler(self, fn: Callable[[Request], Awaitable[Response]]) -> Callable[[Request], Awaitable[Response]]: ...

        def get_asyncapi_spec_json(self) -> Optional[dict[str, Any]]: ...

        def get_asyncapi_spec_yaml(self) -> Optional[str]: ...

        def get_invocation_handler(self, fn: Callable[[Request], Awaitable[Response]]) -> Callable[[Request], Awaitable[Response]]: ...

        def get_openapi_spec(self) -> Optional[dict[str, Any]]: ...

        def invoke_handler(self, fn: Callable[[Request], Awaitable[Response]]) -> Callable[[Request], Awaitable[Response]]: ...

        def ws_handler(self, fn: WSHandler) -> WSHandler: ...


namespace azure.ai.agentserver.invocations.voice

    @dataclass(frozen=True)
    class azure.ai.agentserver.invocations.voice.BargeInEvent:
        heard_text: str
        item_id: Optional[str]
        response_id: str

        def __delattr__() -> None: ...

        def __eq__() -> None: ...

        def __hash__() -> None: ...

        def __init__(
                response_id: str, 
                heard_text: str, 
                item_id: str | None
            ) -> None: ...

        def __repr__() -> None: ...

        def __setattr__() -> None: ...


    @dataclass(frozen=True)
    class azure.ai.agentserver.invocations.voice.ConversationHistoryItem:
        content: tuple[Union[InputTextPart, InputImagePart], Ellipsis]
        item_id: str
        role: Literal["user"] = user

        def __delattr__() -> None: ...

        def __eq__() -> None: ...

        def __hash__() -> None: ...

        def __init__(item_id: str, content: tuple) -> None: ...

        def __repr__() -> None: ...

        def __setattr__() -> None: ...


    @dataclass(frozen=True)
    class azure.ai.agentserver.invocations.voice.ConversationItemCreateEvent:
        item: ConversationHistoryItem
        previous_item_id: Optional[str]
        request_id: str

        def __delattr__() -> None: ...

        def __eq__() -> None: ...

        def __hash__() -> None: ...

        def __init__(
                request_id: str, 
                item: ConversationHistoryItem, 
                previous_item_id: str | None
            ) -> None: ...

        def __repr__() -> None: ...

        def __setattr__() -> None: ...


    @dataclass(frozen=True)
    class azure.ai.agentserver.invocations.voice.ConversationItemDeleteEvent:
        item_id: str
        request_id: str

        def __delattr__() -> None: ...

        def __eq__() -> None: ...

        def __hash__() -> None: ...

        def __init__(request_id: str, item_id: str) -> None: ...

        def __repr__() -> None: ...

        def __setattr__() -> None: ...


    @dataclass(frozen=True)
    class azure.ai.agentserver.invocations.voice.DtmfCollectedEvent:
        collection_id: str
        completion_reason: str
        digits: str
        item_id: str

        def __delattr__() -> None: ...

        def __eq__() -> None: ...

        def __hash__() -> None: ...

        def __init__(
                item_id: str, 
                collection_id: str, 
                digits: str, 
                completion_reason: str
            ) -> None: ...

        def __repr__() -> None: ...

        def __setattr__() -> None: ...


    @dataclass(frozen=True)
    class azure.ai.agentserver.invocations.voice.DtmfCollectionCancelledEvent:
        collection_id: str
        reason: str

        def __delattr__() -> None: ...

        def __eq__() -> None: ...

        def __hash__() -> None: ...

        def __init__(collection_id: str, reason: str) -> None: ...

        def __repr__() -> None: ...

        def __setattr__() -> None: ...


    @dataclass(frozen=True)
    class azure.ai.agentserver.invocations.voice.DtmfCollectionRejectedEvent:
        collection_id: str
        reason: str

        def __delattr__() -> None: ...

        def __eq__() -> None: ...

        def __hash__() -> None: ...

        def __init__(collection_id: str, reason: str) -> None: ...

        def __repr__() -> None: ...

        def __setattr__() -> None: ...


    @dataclass(frozen=True)
    class azure.ai.agentserver.invocations.voice.DtmfKeyEvent:
        digit: str

        def __delattr__() -> None: ...

        def __eq__() -> None: ...

        def __hash__() -> None: ...

        def __init__(digit: str) -> None: ...

        def __repr__() -> None: ...

        def __setattr__() -> None: ...


    @dataclass(frozen=True)
    class azure.ai.agentserver.invocations.voice.HandoffFailedEvent:
        code: str
        item_id: str
        message: Optional[str]
        target: str

        def __delattr__() -> None: ...

        def __eq__() -> None: ...

        def __hash__() -> None: ...

        def __init__(
                item_id: str, 
                target: str, 
                code: str, 
                message: str | None
            ) -> None: ...

        def __repr__() -> None: ...

        def __setattr__() -> None: ...


    @dataclass(frozen=True)
    class azure.ai.agentserver.invocations.voice.InputImagePart:
        alt: Optional[str]
        image_ref: str
        mime_type: str
        type: Literal["input_image"] = input_image

        def __delattr__() -> None: ...

        def __eq__() -> None: ...

        def __hash__() -> None: ...

        def __init__(
                image_ref: str, 
                mime_type: str, 
                alt: str | None
            ) -> None: ...

        def __repr__() -> None: ...

        def __setattr__() -> None: ...


    @dataclass(frozen=True)
    class azure.ai.agentserver.invocations.voice.InputTextPart:
        text: str
        type: Literal["input_text"] = input_text

        def __delattr__() -> None: ...

        def __eq__() -> None: ...

        def __hash__() -> None: ...

        def __init__(text: str) -> None: ...

        def __repr__() -> None: ...

        def __setattr__() -> None: ...


    @dataclass(frozen=True)
    class azure.ai.agentserver.invocations.voice.ResponseCancellationOutcome:
        heard_text: str
        item_id: Optional[str]
        kind: Literal["cancelled", "barge_in"]
        response_id: str

        def __delattr__() -> None: ...

        def __eq__() -> None: ...

        def __hash__() -> None: ...

        def __init__(
                response_id: str, 
                kind: Literal, 
                heard_text: str, 
                item_id: str | None
            ) -> None: ...

        def __repr__() -> None: ...

        def __setattr__() -> None: ...


    @dataclass(frozen=True)
    class azure.ai.agentserver.invocations.voice.ResponseTimeoutEvent:
        item_ids: Optional[tuple[str, Ellipsis]]
        response_id: Optional[str]
        stage: str

        def __delattr__() -> None: ...

        def __eq__() -> None: ...

        def __hash__() -> None: ...

        def __init__(
                stage: str, 
                response_id: str | None, 
                item_ids: tuple
            ) -> None: ...

        def __repr__() -> None: ...

        def __setattr__() -> None: ...


    @dataclass(frozen=True)
    class azure.ai.agentserver.invocations.voice.ResponseTimeouts:
        first_output_ms: int
        idle_ms: int
        max_duration_ms: int

        def __delattr__() -> None: ...

        def __eq__() -> None: ...

        def __hash__() -> None: ...

        def __init__(
                first_output_ms: int, 
                idle_ms: int, 
                max_duration_ms: int
            ) -> None: ...

        def __repr__() -> None: ...

        def __setattr__() -> None: ...


    @dataclass(frozen=True)
    class azure.ai.agentserver.invocations.voice.SessionEndEvent:
        reason: str

        def __delattr__() -> None: ...

        def __eq__() -> None: ...

        def __hash__() -> None: ...

        def __init__(reason: str) -> None: ...

        def __repr__() -> None: ...

        def __setattr__() -> None: ...


    @dataclass(frozen=True)
    class azure.ai.agentserver.invocations.voice.SessionStartEvent:
        caller: Optional[Mapping[str, Any]]
        greeting: Optional[str]
        no_input_timeout_ms: Optional[int]
        protocol_version: str
        reconnect: bool
        response_timeouts: ResponseTimeouts

        def __delattr__() -> None: ...

        def __eq__() -> None: ...

        def __hash__() -> None: ...

        def __init__(
                protocol_version: str, 
                reconnect: bool, 
                response_timeouts: ResponseTimeouts, 
                greeting: str | None, 
                no_input_timeout_ms: int | None, 
                caller: Mapping
            ) -> None: ...

        def __repr__() -> None: ...

        def __setattr__() -> None: ...


    @dataclass(frozen=True)
    class azure.ai.agentserver.invocations.voice.UserMessageEvent:
        property text: str    # Read-only
        content: tuple[Union[InputTextPart, InputImagePart], Ellipsis]
        item_id: str

        def __delattr__() -> None: ...

        def __eq__() -> None: ...

        def __hash__() -> None: ...

        def __init__(item_id: str, content: tuple) -> None: ...

        def __repr__() -> None: ...

        def __setattr__() -> None: ...


    @dataclass(frozen=True)
    class azure.ai.agentserver.invocations.voice.UserNoInputEvent:
        count: int
        item_id: str

        def __delattr__() -> None: ...

        def __eq__() -> None: ...

        def __hash__() -> None: ...

        def __init__(item_id: str, count: int) -> None: ...

        def __repr__() -> None: ...

        def __setattr__() -> None: ...


    @dataclass(frozen=True)
    class azure.ai.agentserver.invocations.voice.UserSpeechStartedEvent:

        def __delattr__() -> None: ...

        def __eq__() -> None: ...

        def __hash__() -> None: ...

        def __init__() -> None: ...

        def __repr__() -> None: ...

        def __setattr__() -> None: ...


    class azure.ai.agentserver.invocations.voice.VoiceAgentServerHost(InvocationAgentServerHost):
        property routes: list[BaseRoute]    # Read-only
        property ws_ping_interval: float    # Read-only

        def __init__(self, **kwargs: Any) -> None: ...

        def cancel_invocation_handler(self, fn: Callable[[Request], Awaitable[Response]]) -> Callable[[Request], Awaitable[Response]]: ...

        def get_asyncapi_spec_json(self) -> Optional[dict[str, Any]]: ...

        def get_asyncapi_spec_yaml(self) -> Optional[str]: ...

        def get_invocation_handler(self, fn: Callable[[Request], Awaitable[Response]]) -> Callable[[Request], Awaitable[Response]]: ...

        def get_openapi_spec(self) -> Optional[dict[str, Any]]: ...

        def invoke_handler(self, fn: Callable[[Request], Awaitable[Response]]) -> Callable[[Request], Awaitable[Response]]: ...

        def on_barge_in(self, fn: BargeInCallback) -> BargeInCallback: ...

        def on_conversation_item_create(self, fn: ConversationItemCreateCallback) -> ConversationItemCreateCallback: ...

        def on_conversation_item_delete(self, fn: ConversationItemDeleteCallback) -> ConversationItemDeleteCallback: ...

        def on_dtmf_collected(self, fn: DtmfCollectedCallback) -> DtmfCollectedCallback: ...

        def on_dtmf_collection_cancelled(self, fn: DtmfCollectionCancelledCallback) -> DtmfCollectionCancelledCallback: ...

        def on_dtmf_collection_rejected(self, fn: DtmfCollectionRejectedCallback) -> DtmfCollectionRejectedCallback: ...

        def on_dtmf_key(self, fn: DtmfKeyCallback) -> DtmfKeyCallback: ...

        def on_handoff_failed(self, fn: HandoffFailedCallback) -> HandoffFailedCallback: ...

        def on_response_timeout(self, fn: ResponseTimeoutCallback) -> ResponseTimeoutCallback: ...

        def on_session_end(self, fn: SessionEndCallback) -> SessionEndCallback: ...

        def on_session_start(self, fn: SessionStartCallback) -> SessionStartCallback: ...

        def on_user_message(self, fn: UserMessageCallback) -> UserMessageCallback: ...

        def on_user_no_input(self, fn: UserNoInputCallback) -> UserNoInputCallback: ...

        def on_user_speech_started(self, fn: UserSpeechStartedCallback) -> UserSpeechStartedCallback: ...

        def ws_handler(self, fn: Any) -> Any: ...


    class azure.ai.agentserver.invocations.voice.VoiceBridgeConnectionClosedError(RuntimeError):


    class azure.ai.agentserver.invocations.voice.VoiceBridgeProtocolError(ValueError):

        def __init__(
                self, 
                message: str, 
                *, 
                close_code: int = 1002
            ) -> None: ...


    class azure.ai.agentserver.invocations.voice.VoiceCancellationToken:
        property is_cancelled: bool    # Read-only

        def __init__(self) -> None: ...

        async def wait(self) -> None: ...


    class azure.ai.agentserver.invocations.voice.VoiceProactiveResponseDroppedError(RuntimeError):

        def __init__(
                self, 
                response_id: str, 
                reason: str
            ) -> None: ...


    class azure.ai.agentserver.invocations.voice.VoiceResponse:
        property cancellation: VoiceCancellationToken    # Read-only
        property in_reply_to: tuple[str, ] | None    # Read-only
        property is_cancel_pending: bool    # Read-only
        property is_terminal: bool    # Read-only
        property is_wire_opened: bool    # Read-only
        property response_id: str    # Read-only

        def __init__(self) -> None: ...

        async def cancel(
                self, 
                *, 
                reason: str | None = ...
            ) -> ResponseCancellationOutcome: ...

        async def collect_dtmf(
                self, 
                *, 
                initial_timeout_ms: int, 
                inter_digit_timeout_ms: int, 
                max_digits: int, 
                terminator: str | None = ...
            ) -> str: ...

        async def decline(
                self, 
                *, 
                reason: str | None = ...
            ) -> None: ...

        async def done(self) -> None: ...

        async def fail(
                self, 
                *, 
                code: str, 
                message: str
            ) -> None: ...

        async def handoff(
                self, 
                *, 
                message: str | None = ..., 
                target: str
            ) -> None: ...

        def new_text_item(self) -> VoiceTextItem: ...

        async def send_text(
                self, 
                text: str, 
                *, 
                voice: Mapping[str, Any] | None = ...
            ) -> None: ...

        async def send_text_delta(
                self, 
                delta: str, 
                *, 
                voice: Mapping[str, Any] | None = ...
            ) -> None: ...

        async def send_text_done(
                self, 
                *, 
                voice: Mapping[str, Any] | None = ...
            ) -> None: ...


    class azure.ai.agentserver.invocations.voice.VoiceSession:
        property caller: Mapping[str, Any] | None    # Read-only
        property greeting: str | None    # Read-only
        property no_input_timeout_ms: int | None    # Read-only
        property reconnect: bool    # Read-only
        property response_timeouts: ResponseTimeouts    # Read-only

        def __init__(self) -> None: ...

        async def cancel_dtmf_collection(self, collection_id: str) -> None: ...

        async def end_call(
                self, 
                *, 
                mode: Literal["drain", "immediate"] = "drain", 
                reason: str
            ) -> None: ...

        async def report_error(
                self, 
                *, 
                code: str, 
                message: str
            ) -> None: ...

        async def start_proactive_response(
                self, 
                *, 
                admission_timeout_ms: int = 60000, 
                supersede_key: str | None = ...
            ) -> VoiceResponse: ...


    class azure.ai.agentserver.invocations.voice.VoiceTextItem:
        property item_id: str    # Read-only

        def __init__(self) -> None: ...

        async def send_text(
                self, 
                text: str, 
                *, 
                voice: Mapping[str, Any] | None = ...
            ) -> None: ...

        async def send_text_delta(
                self, 
                delta: str, 
                *, 
                voice: Mapping[str, Any] | None = ...
            ) -> None: ...

        async def send_text_done(
                self, 
                *, 
                voice: Mapping[str, Any] | None = ...
            ) -> None: ...


```