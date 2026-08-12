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

    @experimental
    def azure.ai.agentserver.invocations.voice.new_item_id() -> str: ...


    @experimental
    def azure.ai.agentserver.invocations.voice.new_message_id() -> str: ...


    @experimental
    def azure.ai.agentserver.invocations.voice.new_response_id() -> str: ...


    @experimental
    @dataclass(frozen=True, kw_only=True, repr=False)
    class azure.ai.agentserver.invocations.voice.AgentError(_OutboundMessage):
        code: str
        id: str
        item_id: Optional[str]
        message: str
        response_id: Optional[str]
        ts: str
        type: ClassVar[str] = error

        def __delattr__() -> None: ...

        def __eq__() -> None: ...

        def __hash__() -> None: ...

        def __init__(
                id: str, 
                ts: str, 
                code: str, 
                message: str, 
                response_id: str | None, 
                item_id: str | None
            ) -> None: ...

        def __setattr__() -> None: ...

        def _voice_model_repr(self: Any) -> str: ...


    @experimental
    @dataclass(frozen=True, kw_only=True, repr=False)
    class azure.ai.agentserver.invocations.voice.BargeIn(_InboundMessage):
        heard_text: str
        id: str
        item_id: Optional[str]
        response_id: str
        ts: str
        type: ClassVar[str] = barge_in

        def __delattr__() -> None: ...

        def __eq__() -> None: ...

        def __hash__() -> None: ...

        def __init__(
                id: str, 
                ts: str, 
                response_id: str, 
                heard_text: str, 
                item_id: str | None
            ) -> None: ...

        def __setattr__() -> None: ...

        def _voice_model_repr(self: Any) -> str: ...


    @experimental
    @dataclass(frozen=True, kw_only=True, repr=False)
    class azure.ai.agentserver.invocations.voice.EndCall(_OutboundMessage):
        id: str
        mode: EndCallMode = EndCallMode.DRAIN
        reason: str
        ts: str
        type: ClassVar[str] = end_call

        def __delattr__() -> None: ...

        def __eq__() -> None: ...

        def __hash__() -> None: ...

        def __init__(
                id: str, 
                ts: str, 
                reason: str, 
                mode: EndCallMode
            ) -> None: ...

        def __setattr__() -> None: ...

        def _voice_model_repr(self: Any) -> str: ...


    @experimental
    class azure.ai.agentserver.invocations.voice.EndCallMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DRAIN = "drain"
        IMMEDIATE = "immediate"


    @experimental
    @dataclass(frozen=True, kw_only=True, repr=False)
    class azure.ai.agentserver.invocations.voice.InputTextPart:
        text: str
        type: Literal["input_text"] = input_text

        def __delattr__() -> None: ...

        def __eq__() -> None: ...

        def __hash__() -> None: ...

        def __init__(text: str) -> None: ...

        def __setattr__() -> None: ...

        def _voice_model_repr(self: Any) -> str: ...


    @experimental
    @dataclass(frozen=True, kw_only=True, repr=False)
    class azure.ai.agentserver.invocations.voice.ResponseAccepted(_InboundMessage):
        id: str
        response_id: str
        ts: str
        type: ClassVar[str] = response.accepted

        def __delattr__() -> None: ...

        def __eq__() -> None: ...

        def __hash__() -> None: ...

        def __init__(
                id: str, 
                ts: str, 
                response_id: str
            ) -> None: ...

        def __setattr__() -> None: ...

        def _voice_model_repr(self: Any) -> str: ...


    @experimental
    @dataclass(frozen=True, kw_only=True, repr=False)
    class azure.ai.agentserver.invocations.voice.ResponseCancel(_OutboundMessage):
        id: str
        reason: Optional[str]
        response_id: str
        ts: str
        type: ClassVar[str] = response.cancel

        def __delattr__() -> None: ...

        def __eq__() -> None: ...

        def __hash__() -> None: ...

        def __init__(
                id: str, 
                ts: str, 
                response_id: str, 
                reason: str | None
            ) -> None: ...

        def __setattr__() -> None: ...

        def _voice_model_repr(self: Any) -> str: ...


    @experimental
    @dataclass(frozen=True, kw_only=True, repr=False)
    class azure.ai.agentserver.invocations.voice.ResponseCancelled(_InboundMessage):
        heard_text: str
        id: str
        item_id: Optional[str]
        response_id: str
        ts: str
        type: ClassVar[str] = response.cancelled

        def __delattr__() -> None: ...

        def __eq__() -> None: ...

        def __hash__() -> None: ...

        def __init__(
                id: str, 
                ts: str, 
                response_id: str, 
                heard_text: str, 
                item_id: str | None
            ) -> None: ...

        def __setattr__() -> None: ...

        def _voice_model_repr(self: Any) -> str: ...


    @experimental
    @dataclass(frozen=True, kw_only=True, repr=False)
    class azure.ai.agentserver.invocations.voice.ResponseCreated(_OutboundMessage):
        admission_timeout_ms: Optional[int]
        id: str
        in_reply_to: Optional[tuple[str, Ellipsis]]
        response_id: str
        supersede_key: Optional[str]
        ts: str
        type: ClassVar[str] = response.created

        def __delattr__() -> None: ...

        def __eq__() -> None: ...

        def __hash__() -> None: ...

        def __init__(
                id: str, 
                ts: str, 
                response_id: str, 
                in_reply_to: tuple, 
                admission_timeout_ms: int | None, 
                supersede_key: str | None
            ) -> None: ...

        def __setattr__() -> None: ...

        def _voice_model_repr(self: Any) -> str: ...


    @experimental
    @dataclass(frozen=True, kw_only=True, repr=False)
    class azure.ai.agentserver.invocations.voice.ResponseDone(_OutboundMessage):
        id: str
        response_id: str
        ts: str
        type: ClassVar[str] = response.done

        def __delattr__() -> None: ...

        def __eq__() -> None: ...

        def __hash__() -> None: ...

        def __init__(
                id: str, 
                ts: str, 
                response_id: str
            ) -> None: ...

        def __setattr__() -> None: ...

        def _voice_model_repr(self: Any) -> str: ...


    @experimental
    @dataclass(frozen=True, kw_only=True, repr=False)
    class azure.ai.agentserver.invocations.voice.ResponseDropped(_InboundMessage):
        id: str
        reason: str
        response_id: str
        ts: str
        type: ClassVar[str] = response.dropped

        def __delattr__() -> None: ...

        def __eq__() -> None: ...

        def __hash__() -> None: ...

        def __init__(
                id: str, 
                ts: str, 
                response_id: str, 
                reason: str
            ) -> None: ...

        def __setattr__() -> None: ...

        def _voice_model_repr(self: Any) -> str: ...


    @experimental
    @dataclass(frozen=True, kw_only=True, repr=False)
    class azure.ai.agentserver.invocations.voice.ResponseNone(_OutboundMessage):
        id: str
        in_reply_to: tuple[str, Ellipsis]
        reason: Optional[str]
        ts: str
        type: ClassVar[str] = response.none

        def __delattr__() -> None: ...

        def __eq__() -> None: ...

        def __hash__() -> None: ...

        def __init__(
                id: str, 
                ts: str, 
                in_reply_to: tuple, 
                reason: str | None
            ) -> None: ...

        def __setattr__() -> None: ...

        def _voice_model_repr(self: Any) -> str: ...


    @experimental
    @dataclass(frozen=True, kw_only=True, repr=False)
    class azure.ai.agentserver.invocations.voice.ResponseOutputTextDelta(_OutboundMessage):
        delta: str
        id: str
        item_id: str
        response_id: str
        ts: str
        type: ClassVar[str] = response.output_text.delta
        voice: Optional[Mapping[str, Any]]

        def __delattr__() -> None: ...

        def __eq__() -> None: ...

        def __hash__() -> None: ...

        def __init__(
                id: str, 
                ts: str, 
                response_id: str, 
                item_id: str, 
                delta: str, 
                voice: Mapping
            ) -> None: ...

        def __post_init__(self) -> None: ...

        def __setattr__() -> None: ...

        def _voice_model_repr(self: Any) -> str: ...


    @experimental
    @dataclass(frozen=True, kw_only=True, repr=False)
    class azure.ai.agentserver.invocations.voice.ResponseOutputTextDone(_OutboundMessage):
        id: str
        item_id: str
        response_id: str
        text: str
        ts: str
        type: ClassVar[str] = response.output_text.done
        voice: Optional[Mapping[str, Any]]

        def __delattr__() -> None: ...

        def __eq__() -> None: ...

        def __hash__() -> None: ...

        def __init__(
                id: str, 
                ts: str, 
                response_id: str, 
                item_id: str, 
                text: str, 
                voice: Mapping
            ) -> None: ...

        def __post_init__(self) -> None: ...

        def __setattr__() -> None: ...

        def _voice_model_repr(self: Any) -> str: ...


    @experimental
    @dataclass(frozen=True, kw_only=True, repr=False)
    class azure.ai.agentserver.invocations.voice.ResponseTimeout(_InboundMessage):
        id: str
        item_ids: Optional[tuple[str, Ellipsis]]
        response_id: Optional[str]
        stage: str
        ts: str
        type: ClassVar[str] = response.timeout

        def __delattr__() -> None: ...

        def __eq__() -> None: ...

        def __hash__() -> None: ...

        def __init__(
                id: str, 
                ts: str, 
                stage: str, 
                response_id: str | None, 
                item_ids: tuple
            ) -> None: ...

        def __setattr__() -> None: ...

        def _voice_model_repr(self: Any) -> str: ...


    @experimental
    @dataclass(frozen=True, kw_only=True, repr=False)
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

        def __setattr__() -> None: ...

        def _voice_model_repr(self: Any) -> str: ...


    @experimental
    class azure.ai.agentserver.invocations.voice.Session:

        def __init__(self) -> None: ...

        async def send(self, message: OutboundVoiceMessage) -> None: ...


    @experimental
    @dataclass(frozen=True, kw_only=True, repr=False)
    class azure.ai.agentserver.invocations.voice.SessionDisconnected:
        code: int
        reason: Optional[str]

        def __delattr__() -> None: ...

        def __eq__() -> None: ...

        def __hash__() -> None: ...

        def __init__(code: int, reason: str | None) -> None: ...

        def __setattr__() -> None: ...

        def _voice_model_repr(self: Any) -> str: ...


    @experimental
    @dataclass(frozen=True, kw_only=True, repr=False)
    class azure.ai.agentserver.invocations.voice.SessionEnd(_InboundMessage):
        id: str
        reason: str
        ts: str
        type: ClassVar[str] = session.end

        def __delattr__() -> None: ...

        def __eq__() -> None: ...

        def __hash__() -> None: ...

        def __init__(
                id: str, 
                ts: str, 
                reason: str
            ) -> None: ...

        def __setattr__() -> None: ...

        def _voice_model_repr(self: Any) -> str: ...


    @experimental
    @dataclass(frozen=True, kw_only=True, repr=False)
    class azure.ai.agentserver.invocations.voice.SessionReady(_OutboundMessage):
        id: str
        ts: str
        type: ClassVar[str] = session.ready

        def __delattr__() -> None: ...

        def __eq__() -> None: ...

        def __hash__() -> None: ...

        def __init__(id: str, ts: str) -> None: ...

        def __setattr__() -> None: ...

        def _voice_model_repr(self: Any) -> str: ...


    @experimental
    @dataclass(frozen=True, kw_only=True, repr=False)
    class azure.ai.agentserver.invocations.voice.SessionRejected(_OutboundMessage):
        code: str
        id: str
        message: Optional[str]
        retriable: bool
        ts: str
        type: ClassVar[str] = session.rejected

        def __delattr__() -> None: ...

        def __eq__() -> None: ...

        def __hash__() -> None: ...

        def __init__(
                id: str, 
                ts: str, 
                code: str, 
                retriable: bool = False, 
                message: str | None
            ) -> None: ...

        def __setattr__() -> None: ...

        def _voice_model_repr(self: Any) -> str: ...


    @experimental
    @dataclass(frozen=True, kw_only=True, repr=False)
    class azure.ai.agentserver.invocations.voice.SessionStart(_InboundMessage):
        caller: Optional[Mapping[str, Any]]
        greeting: Optional[str]
        id: str
        no_input_timeout_ms: Optional[int]
        protocol_version: str
        reconnect: bool
        response_timeouts: ResponseTimeouts
        ts: str
        type: ClassVar[str] = session.start

        def __delattr__() -> None: ...

        def __eq__() -> None: ...

        def __hash__() -> None: ...

        def __init__(
                id: str, 
                ts: str, 
                protocol_version: str, 
                reconnect: bool = False, 
                response_timeouts: ResponseTimeouts, 
                greeting: str | None, 
                no_input_timeout_ms: int | None, 
                caller: Mapping
            ) -> None: ...

        def __setattr__() -> None: ...

        def _voice_model_repr(self: Any) -> str: ...


    @experimental
    @dataclass(frozen=True, kw_only=True, repr=False)
    class azure.ai.agentserver.invocations.voice.UserMessage(_InboundMessage):
        content: tuple[InputTextPart, Ellipsis]
        id: str
        item_id: str
        ts: str
        type: ClassVar[str] = user.message

        def __delattr__() -> None: ...

        def __eq__() -> None: ...

        def __hash__() -> None: ...

        def __init__(
                id: str, 
                ts: str, 
                item_id: str, 
                content: tuple
            ) -> None: ...

        def __setattr__() -> None: ...

        def _voice_model_repr(self: Any) -> str: ...


    @experimental
    @dataclass(frozen=True, kw_only=True, repr=False)
    class azure.ai.agentserver.invocations.voice.UserNoInput(_InboundMessage):
        count: int
        id: str
        item_id: str
        ts: str
        type: ClassVar[str] = user.no_input

        def __delattr__() -> None: ...

        def __eq__() -> None: ...

        def __hash__() -> None: ...

        def __init__(
                id: str, 
                ts: str, 
                item_id: str, 
                count: int
            ) -> None: ...

        def __setattr__() -> None: ...

        def _voice_model_repr(self: Any) -> str: ...


    @experimental
    @dataclass(frozen=True, kw_only=True, repr=False)
    class azure.ai.agentserver.invocations.voice.UserSpeechStarted(_InboundMessage):
        id: str
        ts: str
        type: ClassVar[str] = user.speech_started

        def __delattr__() -> None: ...

        def __eq__() -> None: ...

        def __hash__() -> None: ...

        def __init__(id: str, ts: str) -> None: ...

        def __setattr__() -> None: ...

        def _voice_model_repr(self: Any) -> str: ...


    @experimental
    class azure.ai.agentserver.invocations.voice.VoiceAgentServerHost(InvocationAgentServerHost):
        property routes: list[BaseRoute]    # Read-only
        property ws_ping_interval: float    # Read-only

        def __init__(
                self, 
                *, 
                asyncapi_spec_json: dict[str, Any] | None = ..., 
                asyncapi_spec_yaml: str | None = ..., 
                openapi_spec: dict[str, Any] | None = ..., 
                **kwargs: Any
            ) -> None: ...

        def cancel_invocation_handler(self, fn: Callable[[Request], Awaitable[Response]]) -> Callable[[Request], Awaitable[Response]]: ...

        def get_asyncapi_spec_json(self) -> Optional[dict[str, Any]]: ...

        def get_asyncapi_spec_yaml(self) -> Optional[str]: ...

        def get_invocation_handler(self, fn: Callable[[Request], Awaitable[Response]]) -> Callable[[Request], Awaitable[Response]]: ...

        def get_openapi_spec(self) -> Optional[dict[str, Any]]: ...

        def invoke_handler(self, fn: Callable[[Request], Awaitable[Response]]) -> Callable[[Request], Awaitable[Response]]: ...

        def on_barge_in(self, callback: BargeInCallback) -> BargeInCallback: ...

        def on_disconnect(self, callback: DisconnectCallback) -> DisconnectCallback: ...

        def on_response_accepted(self, callback: ResponseAcceptedCallback) -> ResponseAcceptedCallback: ...

        def on_response_cancelled(self, callback: ResponseCancelledCallback) -> ResponseCancelledCallback: ...

        def on_response_dropped(self, callback: ResponseDroppedCallback) -> ResponseDroppedCallback: ...

        def on_response_timeout(self, callback: ResponseTimeoutCallback) -> ResponseTimeoutCallback: ...

        def on_session_end(self, callback: SessionEndCallback) -> SessionEndCallback: ...

        def on_session_start(self, callback: SessionStartCallback) -> SessionStartCallback: ...

        def on_user_message(self, callback: UserMessageCallback) -> UserMessageCallback: ...

        def on_user_no_input(self, callback: UserNoInputCallback) -> UserNoInputCallback: ...

        def on_user_speech_started(self, callback: UserSpeechStartedCallback) -> UserSpeechStartedCallback: ...

        def ws_handler(self, fn: Any) -> NoReturn: ...


```